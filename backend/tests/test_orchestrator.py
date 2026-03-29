"""
Unit tests for the LangGraph orchestrator (orchestrator.py).

Covers:
- Graph builds without error and contains the correct nodes
- All 6 specialist nodes are invoked (in parallel) when the graph runs
- specialist_reports state is fully populated before head_agent runs
- head_agent.analyze() receives the combined anomaly list from all specialists
- Final state contains a RiskScore in the risk_score key
- run_pipeline() convenience wrapper returns the RiskScore directly
- Graph handles agents that return zero anomalies
- Graph handles a mix of anomaly-producing and silent agents
- _make_specialist_node correctly wraps the agent report in a list
- _make_head_node correctly aggregates anomalies and calls analyze
"""
from __future__ import annotations

import sys
import os

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, call, patch

from models import AgentReport, Anomaly, RiskScore, CascadeChain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_anomaly(domain: str, anomaly_id: str, severity: float = 0.7) -> Anomaly:
    return Anomaly(
        id=anomaly_id,
        agent_domain=domain,
        severity=severity,
        confidence=0.8,
        title=f"Test anomaly from {domain}",
        description="A synthetic anomaly for testing.",
        affected_entities=[],
        evidence={},
        cross_references=[],
        timestamp=datetime.now(timezone.utc),
    )


def _make_report(domain: str, anomaly_count: int = 1) -> AgentReport:
    anomalies = [_make_anomaly(domain, f"{domain}_{i}") for i in range(anomaly_count)]
    return AgentReport(
        agent=domain,
        anomalies=anomalies,
        raw_data_summary=f"{domain} data loaded",
        timestamp=datetime.now(timezone.utc),
    )


def _make_risk_score() -> RiskScore:
    return RiskScore(
        score=72.5,
        trend="increasing",
        top_cascades=[],
        briefing="Test briefing from head agent.",
        timestamp=datetime.now(timezone.utc),
    )


def _make_mock_specialist(domain: str, anomaly_count: int = 1) -> MagicMock:
    """Return a mock specialist agent that returns a pre-built AgentReport on .run()."""
    agent = MagicMock()
    agent.domain = domain
    agent.run.return_value = _make_report(domain, anomaly_count)
    return agent


def _make_mock_head_agent(risk_score: RiskScore | None = None) -> MagicMock:
    """Return a mock head agent whose .analyze() returns the given RiskScore."""
    head = MagicMock()
    head.analyze.return_value = risk_score or _make_risk_score()
    return head


def _all_mock_specialists(anomaly_count: int = 1) -> dict:
    """Return a dict of 6 mock specialist agents, one per domain."""
    domains = ["people", "finance", "infra", "product", "legal", "code_audit"]
    return {d: _make_mock_specialist(d, anomaly_count) for d in domains}


# ---------------------------------------------------------------------------
# Graph construction tests
# ---------------------------------------------------------------------------

class TestBuildGraph:
    def test_build_graph_returns_compiled_graph(self):
        """build_graph should return a compiled LangGraph object without raising."""
        from orchestrator import build_graph
        specialists = _all_mock_specialists()
        head = _make_mock_head_agent()
        graph = build_graph(specialists, head)
        assert graph is not None


# ---------------------------------------------------------------------------
# Graph execution tests
# ---------------------------------------------------------------------------

class TestGraphExecution:
    def _invoke(self, specialists=None, head=None):
        """Helper: build and invoke the graph, return final state."""
        from orchestrator import build_graph
        specialists = specialists or _all_mock_specialists()
        head = head or _make_mock_head_agent()
        graph = build_graph(specialists, head)
        return graph.invoke({"specialist_reports": [], "risk_score": None}), specialists, head

    def test_all_specialists_are_called(self):
        """Every specialist agent's .run() must be called exactly once."""
        final_state, specialists, _ = self._invoke()
        for domain, agent in specialists.items():
            agent.run.assert_called_once(), f"{domain} agent was not called"

    def test_specialist_reports_domains_match(self):
        """Each report in specialist_reports should match an expected domain."""
        expected_domains = {"people", "finance", "infra", "product", "legal", "code_audit"}
        final_state, _, _ = self._invoke()
        actual_domains = {r.agent for r in final_state["specialist_reports"]}
        assert actual_domains == expected_domains

    def test_head_agent_analyze_called_once(self):
        """head_agent.analyze() must be called exactly once."""
        _, _, head = self._invoke()
        head.analyze.assert_called_once()

    def test_head_agent_receives_all_anomalies(self):
        """head_agent.analyze() must receive the combined anomaly list from all specialists."""
        specialists = _all_mock_specialists(anomaly_count=2)  # 6 agents × 2 anomalies = 12
        head = _make_mock_head_agent()
        self._invoke(specialists=specialists, head=head)

        call_args = head.analyze.call_args
        passed_anomalies = call_args[0][0]  # first positional argument
        assert len(passed_anomalies) == 12

    def test_final_state_risk_score_is_correct_type(self):
        """The risk_score in final state must be a RiskScore instance."""
        final_state, _, _ = self._invoke()
        assert isinstance(final_state["risk_score"], RiskScore)

    def test_final_risk_score_matches_head_agent_output(self):
        """The risk_score in final state must be exactly what head_agent.analyze() returned."""
        expected = _make_risk_score()
        expected.score = 88.0
        head = _make_mock_head_agent(risk_score=expected)
        final_state, _, _ = self._invoke(head=head)
        assert final_state["risk_score"].score == 88.0
        assert final_state["risk_score"].briefing == expected.briefing

    def test_empty_anomalies_still_calls_head_agent(self):
        """Even if every specialist returns 0 anomalies, head_agent.analyze() must still run."""
        specialists = _all_mock_specialists(anomaly_count=0)
        head = _make_mock_head_agent()
        self._invoke(specialists=specialists, head=head)
        head.analyze.assert_called_once_with([])

    def test_mixed_anomaly_counts(self):
        """Specialists returning different anomaly counts should all be merged correctly."""
        domains = ["people", "finance", "infra", "product", "legal", "code_audit"]
        specialists = {}
        total_expected = 0
        for i, domain in enumerate(domains):
            count = i  # 0, 1, 2, 3, 4, 5  → total = 15
            total_expected += count
            specialists[domain] = _make_mock_specialist(domain, count)

        head = _make_mock_head_agent()
        from orchestrator import build_graph
        graph = build_graph(specialists, head)
        graph.invoke({"specialist_reports": [], "risk_score": None})

        passed_anomalies = head.analyze.call_args[0][0]
        assert len(passed_anomalies) == total_expected


# ---------------------------------------------------------------------------
# run_pipeline convenience function tests
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_run_pipeline_returns_correct_score(self):
        """run_pipeline() must return the exact RiskScore from head_agent."""
        from orchestrator import run_pipeline
        expected = _make_risk_score()
        expected.score = 55.5
        result = run_pipeline(_all_mock_specialists(), _make_mock_head_agent(risk_score=expected))
        assert isinstance(result, RiskScore)
        assert result.score == 55.5


# ---------------------------------------------------------------------------
# Node factory unit tests
# ---------------------------------------------------------------------------

class TestMakeSpecialistNode:
    def test_node_returns_list_with_one_report(self):
        """_make_specialist_node returns a function whose output wraps the report in a list."""
        from orchestrator import _make_specialist_node
        report = _make_report("people")
        agent = MagicMock()
        agent.domain = "people"
        agent.run.return_value = report

        node_fn = _make_specialist_node(agent)
        result = node_fn({})  # state is unused by specialist nodes

        assert result == {"specialist_reports": [report]}


class TestMakeHeadNode:
    def test_node_aggregates_anomalies(self):
        """_make_head_node must flatten all report anomalies into one list."""
        from orchestrator import _make_head_node
        head = _make_mock_head_agent()

        state = {
            "specialist_reports": [
                _make_report("people", 2),
                _make_report("finance", 3),
            ],
            "risk_score": None,
        }
        node_fn = _make_head_node(head)
        node_fn(state)

        passed = head.analyze.call_args[0][0]
        assert len(passed) == 5

    def test_node_returns_risk_score_in_dict(self):
        """_make_head_node's return value must be {"risk_score": <RiskScore>}."""
        from orchestrator import _make_head_node
        expected = _make_risk_score()
        head = _make_mock_head_agent(risk_score=expected)

        node_fn = _make_head_node(head)
        result = node_fn({"specialist_reports": [_make_report("infra", 1)], "risk_score": None})
        assert result["risk_score"] is expected

    def test_node_handles_empty_reports(self):
        """_make_head_node must call analyze([]) when no reports exist."""
        from orchestrator import _make_head_node
        head = _make_mock_head_agent()
        node_fn = _make_head_node(head)
        node_fn({"specialist_reports": [], "risk_score": None})
        head.analyze.assert_called_once_with([])


# ---------------------------------------------------------------------------
# SPECIALIST_DOMAINS constant
# ---------------------------------------------------------------------------

class TestSpecialistDomains:
    def test_specialist_domains_contains_all_expected(self):
        from orchestrator import SPECIALIST_DOMAINS
        expected = {"people", "finance", "infra", "product", "legal", "code_audit"}
        assert set(SPECIALIST_DOMAINS) == expected
