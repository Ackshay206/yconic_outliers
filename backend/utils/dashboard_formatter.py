"""
Transforms a backend RiskScore into the frontend dashboard JSON format.

Output shape:
{
  riskScore, trend, activeCascades,
  nodes[],       -- deduplicated across chains
  edges[],       -- derived from consecutive nodes within each chain
  activeChains[] -- one entry per top cascade
}
"""
from __future__ import annotations

from models import RiskScore, CascadeNode

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

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

def _status(node: CascadeNode, is_trigger: bool) -> str:
    if is_trigger and node.severity >= 0.75:
        return "OCCURRED"
    if node.severity >= 0.65 or node.cumulative_probability >= 0.5:
        return "LIKELY"
    return "POSSIBLE"


def _edge_severity(conditional_probability: float) -> str:
    if conditional_probability >= 0.7:
        return "high"
    if conditional_probability >= 0.5:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Main formatter
# ---------------------------------------------------------------------------

def format_dashboard(risk_score: RiskScore) -> dict:
    chains = risk_score.top_cascades

    # Deduplicated node map  node_id → frontend dict
    node_map:        dict[str, dict]      = {}
    node_depth:      dict[str, int]       = {}   # first-seen column depth
    node_chain_rows: dict[str, list[int]] = {}   # chain indices containing this node

    edge_set: set[tuple[str, str]] = set()
    edges:    list[dict]           = []

    for chain_idx, chain in enumerate(chains):
        for depth, node in enumerate(chain.nodes):
            nid = node.id

            if nid not in node_map:
                node_map[nid] = {
                    "id":                 nid,
                    "domain":             node.agent_domain,
                    "status":             _status(node, depth == 0),
                    "title":              node.title,
                    "subtitle":           DOMAIN_SUBTITLES.get(node.agent_domain, ""),
                    "description":        node.evidence if node.evidence else node.title,
                    "agentName":          DOMAIN_AGENT_NAMES.get(
                                              node.agent_domain,
                                              node.agent_domain.replace("_", " ").title() + " Agent",
                                          ),
                    "evidence":           node.evidence if node.evidence else node.title,
                    "cascadeProbability": node.cumulative_probability,
                }
                node_depth[nid]      = depth
                node_chain_rows[nid] = [chain_idx]
            else:
                node_chain_rows[nid].append(chain_idx)

            # Edge from previous node in this chain
            if depth > 0:
                prev_id  = chain.nodes[depth - 1].id
                edge_key = (prev_id, nid)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append({
                        "id":       f"e{len(edges) + 1}",
                        "source":   prev_id,
                        "target":   nid,
                        "severity": _edge_severity(node.conditional_probability),
                    })

    # Assign positions: x = depth column, y = average chain row
    COLUMN_WIDTH = 300
    ROW_HEIGHT   = 200
    Y_OFFSET     = 100

    for nid, node_dict in node_map.items():
        avg_row = sum(node_chain_rows[nid]) / len(node_chain_rows[nid])
        node_dict["position"] = {
            "x": node_depth[nid] * COLUMN_WIDTH,
            "y": int(avg_row * ROW_HEIGHT + Y_OFFSET),
        }

    # Build activeChains
    active_chains: list[dict] = []
    for i, chain in enumerate(chains):
        domains = [n.agent_domain for n in chain.nodes]

        # Unique consecutive domain labels for the cascade label string
        unique: list[str] = []
        for d in domains:
            label = d.replace("_", " ").title()
            if not unique or unique[-1] != label:
                unique.append(label)

        active_chains.append({
            "label":   f"Cascade #{i + 1} \u2014 {' \u2192 '.join(unique)}",
            "chain":   [n.title for n in chain.nodes],
            "domains": domains,
            "prob":    chain.overall_probability,
        })

    return {
        "riskScore":      risk_score.score,
        "trend":          risk_score.trend,
        "activeCascades": len(chains),
        "nodes":          list(node_map.values()),
        "edges":          edges,
        "activeChains":   active_chains,
    }
