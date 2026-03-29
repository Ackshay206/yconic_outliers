"""
LangGraph orchestrator for DEADPOOL.

Graph topology (all specialist nodes run in parallel):

    START ──► people ──────┐
          ──► finance ─────┤
          ──► infra ───────┼──► head_agent ──► END
          ──► product ─────┤
          ──► legal ───────┤
          ──► code_audit ──┘

LangGraph's barrier semantics guarantee that head_agent only executes
after every specialist node has written its AgentReport into the state.
The `operator.add` reducer on `specialist_reports` merges the lists
produced by each parallel branch before head_agent reads them.
"""
from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Annotated, Optional

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from models import AgentReport, Anomaly, RiskScore

# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------

class OrchestratorState(TypedDict):
    # Each specialist node appends [AgentReport] to this list.
    # operator.add merges all parallel branches before head_agent runs.
    specialist_reports: Annotated[list[AgentReport], operator.add]
    # Populated by head_agent; None until that node executes.
    risk_score: Optional[RiskScore]


# ---------------------------------------------------------------------------
# Node factories
# ---------------------------------------------------------------------------

def _make_specialist_node(agent):
    """
    Return a sync LangGraph node function that runs a specialist agent
    and appends its AgentReport to the shared state list.
    """
    def node(_state: OrchestratorState) -> dict:
        report: AgentReport = agent.run()
        return {"specialist_reports": [report]}
    node.__name__ = f"run_{agent.domain}"
    return node


def _make_head_node(head_agent):
    """
    Return a sync LangGraph node function that collects all anomalies
    from specialist reports and runs the HeadAgent analysis.
    """
    def node(state: OrchestratorState) -> dict:
        all_anomalies: list[Anomaly] = []
        for report in state["specialist_reports"]:
            all_anomalies.extend(report.anomalies)
        risk_score: RiskScore = head_agent.analyze(all_anomalies)
        return {"risk_score": risk_score}
    node.__name__ = "run_head_agent"
    return node


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

#: Canonical order of specialist domains (used for graph construction and tests)
SPECIALIST_DOMAINS = ["people", "finance", "infra", "product", "legal", "code_audit"]


def build_graph(specialists: dict, head_agent) -> CompiledStateGraph:
    """
    Build and compile the DEADPOOL LangGraph pipeline.

    Parameters
    ----------
    specialists : dict
        Mapping of domain name → specialist agent instance.
        Expected keys: people, finance, infra, product, legal, code_audit.
    head_agent : HeadAgent
        The orchestrating head agent that cross-validates and scores anomalies.

    Returns
    -------
    CompiledStateGraph
        A compiled LangGraph graph ready for .invoke() / .ainvoke().
    """
    builder = StateGraph(OrchestratorState)

    # Register one node per specialist
    for domain, agent in specialists.items():
        builder.add_node(domain, _make_specialist_node(agent))

    # Register the head agent node
    builder.add_node("head_agent", _make_head_node(head_agent))

    # Fan-out: START → all specialist nodes (LangGraph executes them in parallel)
    for domain in specialists:
        builder.add_edge(START, domain)

    # Fan-in: all specialist nodes → head_agent (barrier join)
    for domain in specialists:
        builder.add_edge(domain, "head_agent")

    # head_agent → END
    builder.add_edge("head_agent", END)

    return builder.compile()


# ---------------------------------------------------------------------------
# Convenience entry point
# ---------------------------------------------------------------------------

def run_pipeline(specialists: dict, head_agent) -> RiskScore:
    """
    Build the graph, execute it with the given agents, and return the
    RiskScore produced by the head agent.

    This is a synchronous wrapper suitable for use with asyncio.to_thread()
    when called from an async FastAPI endpoint.
    """
    graph = build_graph(specialists, head_agent)
    initial_state: OrchestratorState = {
        "specialist_reports": [],
        "risk_score": None,
    }
    final_state = graph.invoke(initial_state)
    return final_state["risk_score"]
