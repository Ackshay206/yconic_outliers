"""
LangGraph orchestrator for DEADPOOL.

Graph topology:

    START ──► people ──────┐
          ──► finance ─────┤
          ──► infra ───────┼──► head_agent ──►[conditional]──► cascade_expander ◄─┐
          ──► product ─────┤                         │                              │ loop
          ──► legal ───────┤                         │             [conditional] ───┘
          ──► code_audit ──┘                         │
                                                     └──────────► format_output ──► END

Conditional edges make this a true LangGraph graph:
  - head_agent     → cascade_expander  (if root causes exist)
                   → format_output     (if no anomalies to expand)
  - cascade_expander → cascade_expander (loop while active threads remain and depth < MAX)
                     → format_output    (when expansion is complete)
"""
from __future__ import annotations

import operator
import os
import re
from typing import TYPE_CHECKING, Annotated, Optional

import google.genai as genai

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from models import AgentReport, Anomaly, RiskScore
from cascade_mapper import PROB_THRESHOLD, _llm_next_step, _apply_rules

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_CASCADE_DEPTH = 5    # run cascade expander up to 5 times (depth budget)

DOMAIN_AGENT_NAMES: dict[str, str] = {
    "people":     "People Agent",
    "finance":    "Finance Agent",
    "infra":      "Infra Agent",
    "product":    "Product Agent",
    "legal":      "Legal Agent",
    "code_audit": "Code Audit Agent",
}

DOMAIN_SUBTITLES: dict[str, str] = {
    "people":     "Team & personnel risk",
    "finance":    "Financial & runway risk",
    "infra":      "Infrastructure & deployment",
    "product":    "Product & user risk",
    "legal":      "Compliance & contract risk",
    "code_audit": "Code quality & security",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_domain(cause: str) -> str:
    text = cause.lower()
    if any(k in text for k in ["engineer", "team", "attrition", "hire", "burnout", "quit", "people", "employee", "talent", "departure", "morale"]):
        return "people"
    if any(k in text for k in ["revenue", "cash", "finance", "investor", "runway", "burn", "mrr", "arr", "funding", "money", "profit"]):
        return "finance"
    if any(k in text for k in ["deploy", "infra", "server", "ci", "pipeline", "uptime", "latency", "outage", "cloud", "devops"]):
        return "infra"
    if any(k in text for k in ["legal", "compliance", "contract", "sla", "gdpr", "lawsuit", "regulatory", "penalty"]):
        return "legal"
    if any(k in text for k in ["product", "feature", "user", "churn", "ux", "bug", "adoption", "nps", "customer"]):
        return "product"
    if any(k in text for k in ["cve", "vulnerability", "security", "code", "test", "coverage", "dependency", "audit"]):
        return "code_audit"
    return "unknown"


def _prob_to_status(probability: float) -> str:
    if probability >= 80:
        return "OCCURRED"
    if probability >= 50:
        return "LIKELY"
    return "POSSIBLE"


def _edge_severity(probability: float) -> str:
    if probability >= 70:
        return "high"
    if probability >= 50:
        return "medium"
    return "low"


def _node_id(cause: str, depth: int, idx: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", cause[:25].lower()).strip("_")
    return f"{slug}_{depth}_{idx}"


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------

class OrchestratorState(TypedDict):
    # Specialist outputs — operator.add merges parallel branches
    specialist_reports: Annotated[list[AgentReport], operator.add]

    # Head agent output
    risk_score:      Optional[RiskScore]
    root_causes:     list[str]
    domains_present: list[str]

    # Cascade loop state
    active_threads:  list[dict]                          # current depth threads (replaced each iter)
    cascade_nodes:   Annotated[list[dict], operator.add] # dashboard nodes — accumulated across iterations
    cascade_edges:   Annotated[list[dict], operator.add] # dashboard edges — accumulated across iterations
    visited_causes:  Annotated[list[str],  operator.add] # dedup across iterations
    depth:           int                                  # loop counter (replaced each iter)

    # Final output
    dashboard: Optional[dict]


# ---------------------------------------------------------------------------
# Specialist nodes
# ---------------------------------------------------------------------------

def _make_specialist_node(agent):
    def node(_state: OrchestratorState) -> dict:
        report: AgentReport = agent.run()
        return {"specialist_reports": [report]}
    node.__name__ = f"run_{agent.domain}"
    return node


# ---------------------------------------------------------------------------
# Head agent node — cross-validates anomalies and seeds the cascade
# ---------------------------------------------------------------------------

def _make_head_node(head_agent):
    def node(state: OrchestratorState) -> dict:
        all_anomalies:   list[Anomaly] = []
        domains_present: list[str]     = []

        for report in state["specialist_reports"]:
            all_anomalies.extend(report.anomalies)
            if report.anomalies:
                domains_present.append(report.agent)

        risk_score: RiskScore = head_agent.analyze(all_anomalies)

        # Seed the cascade with high-severity anomalies as root nodes
        trigger_anomalies = [a for a in all_anomalies if a.severity >= 0.5]

        cascade_nodes: list[dict] = []
        active_threads: list[dict] = []
        visited_causes: list[str]  = []

        for idx, anomaly in enumerate(trigger_anomalies):
            nid    = _node_id(anomaly.title, 0, idx)
            domain = anomaly.agent_domain
            evidence_str = (
                " ".join(f"{k}: {v}" for k, v in anomaly.evidence.items())
                if anomaly.evidence else ""
            )
            cascade_nodes.append({
                "id":                 nid,
                "domain":             domain,
                "status":             "OCCURRED",
                "title":              anomaly.title,
                "subtitle":           DOMAIN_SUBTITLES.get(domain, ""),
                "description":        anomaly.description,
                "agentName":          DOMAIN_AGENT_NAMES.get(domain, "Agent"),
                "evidence":           evidence_str,
                "cascadeProbability": round(min(anomaly.severity, 1.0), 4),
                "position":           {"x": 0, "y": idx * 200 + 100},
            })
            active_threads.append({
                "id":          nid,
                "cause":       anomaly.title,
                "probability": round(anomaly.severity * 100, 2),
            })
            visited_causes.append(anomaly.title)

        return {
            "risk_score":      risk_score,
            "root_causes":     [a.title for a in trigger_anomalies],
            "domains_present": list(set(domains_present)),
            "active_threads":  active_threads,
            "cascade_nodes":   cascade_nodes,
            "cascade_edges":   [],
            "visited_causes":  visited_causes,
            "depth":           0,
        }
    node.__name__ = "run_head_agent"
    return node


# ---------------------------------------------------------------------------
# Cascade expander node — one iteration of the cascade loop
# ---------------------------------------------------------------------------

def _make_cascade_expander_node():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def node(state: OrchestratorState) -> dict:
        active_threads  = state["active_threads"]
        depth           = state["depth"]
        domains_present = state["domains_present"]
        visited         = set(state["visited_causes"])

        consequences = _llm_next_step(client, active_threads, depth)

        new_nodes:   list[dict] = []
        new_edges:   list[dict] = []
        new_visited: list[str]  = []
        new_threads: list[dict] = []

        added_idx = 0
        for c in consequences:
            cause = (c.get("cause") or "").strip()
            if not cause or cause in visited:
                continue

            prob = float(c.get("probability", 0))
            prob = _apply_rules(domains_present, prob)

            # If the next-step cascading probability is below the threshold,
            # stop expanding this branch.
            if prob < PROB_THRESHOLD:
                continue

            nid    = _node_id(cause, depth + 1, added_idx)
            domain = _infer_domain(cause)

            visited.add(cause)
            new_visited.append(cause)

            new_nodes.append({
                "id":                 nid,
                "domain":             domain,
                "status":             _prob_to_status(prob),
                "title":              cause,
                "subtitle":           DOMAIN_SUBTITLES.get(domain, ""),
                "description":        cause,
                "agentName":          DOMAIN_AGENT_NAMES.get(domain, "Agent"),
                "evidence":           "",
                "cascadeProbability": round(prob / 100.0, 4),
                "position":           {"x": (depth + 1) * 300, "y": added_idx * 200 + 100},
            })

            # Build edges — prefer matching contributing_causes, fallback to all parents
            contributing   = set(c.get("contributing_causes", []))
            matched        = [t for t in active_threads if t["cause"] in contributing]
            parents_to_link = matched if matched else active_threads

            for parent in parents_to_link:
                new_edges.append({
                    "source":   parent["id"],
                    "target":   nid,
                    "severity": _edge_severity(prob),
                })

            is_terminal = c.get("is_terminal", False)
            if not is_terminal:
                new_threads.append({
                    "id":          nid,
                    "cause":       cause,
                    "probability": prob,
                })

            added_idx += 1

        return {
            "active_threads": new_threads,
            "cascade_nodes":  new_nodes,
            "cascade_edges":  new_edges,
            "visited_causes": new_visited,
            "depth":          depth + 1,
        }
    node.__name__ = "cascade_expander"
    return node


# ---------------------------------------------------------------------------
# Bounty scoring — inline, no extra LLM calls
# ---------------------------------------------------------------------------

# How reversible each domain is (0 = permanent, 1 = fully reversible)
_DOMAIN_REVERSIBILITY: dict[str, float] = {
    "people":     0.10,
    "finance":    0.45,
    "legal":      0.30,
    "infra":      0.70,
    "product":    0.55,
    "code_audit": 0.60,
}

# Rough fix-cost baseline per domain (USD) — used when no better estimate exists
_DOMAIN_FIX_COST: dict[str, float] = {
    "people":     15000,
    "finance":     5000,
    "legal":      20000,
    "infra":       8000,
    "product":     6000,
    "code_audit":  4000,
}

def _compute_bounty(nodes: list[dict]) -> list[dict]:
    """
    Enrich each node with bountyValue (0-100), costToFix, and costOfIgnoring.
    Uses only data already present on the node — no extra LLM calls.
    """
    scores: list[float] = []
    for node in nodes:
        prob        = float(node.get("cascadeProbability", 0))   # 0-1
        domain      = node.get("domain", "unknown")
        reversibility = _DOMAIN_REVERSIBILITY.get(domain, 0.5)
        cost_to_fix   = _DOMAIN_FIX_COST.get(domain, 10000)
        # Expected loss: assume $500k baseline financial impact scaled by probability
        cost_of_ignoring = prob * 500_000

        raw = (
            (cost_of_ignoring)
            * (prob ** 1.5)                          # non-linear severity weight
            * (1 + (1 - reversibility))              # irreversibility multiplier
            / (cost_to_fix + 1)                      # ROI denominator
        )
        node["costToFix"]      = cost_to_fix
        node["costOfIgnoring"] = round(cost_of_ignoring, 2)
        scores.append(raw)

    # Normalise to 0-100
    min_s, max_s = min(scores, default=0), max(scores, default=1)
    span = max_s - min_s or 1
    for node, raw in zip(nodes, scores):
        node["bountyValue"] = round((raw - min_s) / span * 100, 1)

    return nodes


# ---------------------------------------------------------------------------
# Format output node — assembles the final dashboard JSON
# ---------------------------------------------------------------------------

def _format_output_node(state: OrchestratorState) -> dict:
    risk_score    = state["risk_score"]
    cascade_nodes = state["cascade_nodes"]
    cascade_edges = state["cascade_edges"]

    # Number edges
    for i, edge in enumerate(cascade_edges):
        edge["id"] = f"e{i + 1}"

    # Build adjacency maps
    outgoing: dict[str, list[str]] = {}
    incoming: set[str]             = set()
    for edge in cascade_edges:
        outgoing.setdefault(edge["source"], []).append(edge["target"])
        incoming.add(edge["target"])

    node_by_id = {n["id"]: n for n in cascade_nodes}
    root_ids   = [n["id"] for n in cascade_nodes if n["id"] not in incoming]

    # DFS to trace the main (first-child) path from each root → active chain
    def _dfs_chain(nid: str, path: list[str]) -> list[str]:
        children = outgoing.get(nid, [])
        return _dfs_chain(children[0], path + [children[0]]) if children else path

    active_chains: list[dict] = []
    for i, root_id in enumerate(root_ids[:8]):
        path_ids = _dfs_chain(root_id, [root_id])
        titles   = [node_by_id[n]["title"]  for n in path_ids if n in node_by_id]
        domains  = [node_by_id[n]["domain"] for n in path_ids if n in node_by_id]

        unique_labels: list[str] = []
        for d in domains:
            label = d.replace("_", " ").title()
            if not unique_labels or unique_labels[-1] != label:
                unique_labels.append(label)

        prob = node_by_id[path_ids[-1]]["cascadeProbability"] if path_ids and path_ids[-1] in node_by_id else 0.0

        label_sep = " \u2192 "
        active_chains.append({
            "label":   f"Cascade #{i + 1} \u2014 {label_sep.join(unique_labels)}",
            "chain":   titles,
            "domains": domains,
            "prob":    prob,
        })

    # Enrich nodes with bounty fields
    cascade_nodes = _compute_bounty(cascade_nodes)

    # Build prioritised action queue sorted by bountyValue descending
    bounty_ranking = sorted(
        [{"nodeId": n["id"], "title": n["title"], "domain": n["domain"],
          "bountyValue": n["bountyValue"], "costToFix": n["costToFix"],
          "costOfIgnoring": n["costOfIgnoring"]}
         for n in cascade_nodes],
        key=lambda x: x["bountyValue"],
        reverse=True,
    )[:10]

    dashboard = {
        "riskScore":      risk_score.score if risk_score else 0,
        "trend":          risk_score.trend if risk_score else "stable",
        "activeCascades": len(root_ids),
        "nodes":          cascade_nodes,
        "edges":          cascade_edges,
        "activeChains":   active_chains,
        "bountyRanking":  bounty_ranking,
    }

    return {"dashboard": dashboard}


# ---------------------------------------------------------------------------
# Conditional edge routers
# ---------------------------------------------------------------------------

def _after_head_agent(state: OrchestratorState) -> str:
    """Start cascade expansion if there are seeded threads; else skip to format."""
    return "cascade_expander" if state.get("active_threads") else "format_output"


def _after_cascade_expander(state: OrchestratorState) -> str:
    """Keep expanding while we still have expandable threads and depth budget."""
    if state.get("depth", 0) < MAX_CASCADE_DEPTH and state.get("active_threads"):
        return "cascade_expander"
    return "format_output"


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

SPECIALIST_DOMAINS = ["people", "finance", "infra", "product", "legal", "code_audit"]


def build_graph(specialists: dict, head_agent) -> "CompiledStateGraph":
    builder = StateGraph(OrchestratorState)

    for domain, agent in specialists.items():
        builder.add_node(domain, _make_specialist_node(agent))

    builder.add_node("head_agent",       _make_head_node(head_agent))
    builder.add_node("cascade_expander", _make_cascade_expander_node())
    builder.add_node("format_output",    _format_output_node)

    # Fan-out: START → all specialists (parallel)
    for domain in specialists:
        builder.add_edge(START, domain)

    # Fan-in: all specialists → head_agent (barrier join)
    for domain in specialists:
        builder.add_edge(domain, "head_agent")

    # Conditional: head_agent → cascade_expander OR format_output
    builder.add_conditional_edges(
        "head_agent",
        _after_head_agent,
        {"cascade_expander": "cascade_expander", "format_output": "format_output"},
    )

    # Conditional loop: cascade_expander → cascade_expander OR format_output
    builder.add_conditional_edges(
        "cascade_expander",
        _after_cascade_expander,
        {"cascade_expander": "cascade_expander", "format_output": "format_output"},
    )

    builder.add_edge("format_output", END)

    return builder.compile()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_pipeline(specialists: dict, head_agent) -> dict:
    """
    Run the full DEADPOOL LangGraph pipeline.
    Returns the dashboard dict in the frontend format.
    """
    graph = build_graph(specialists, head_agent)
    initial_state: OrchestratorState = {
        "specialist_reports": [],
        "risk_score":         None,
        "root_causes":        [],
        "domains_present":    [],
        "active_threads":     [],
        "cascade_nodes":      [],
        "cascade_edges":      [],
        "visited_causes":     [],
        "depth":              0,
        "dashboard":          None,
    }
    final_state = graph.invoke(initial_state)
    return final_state["dashboard"]
