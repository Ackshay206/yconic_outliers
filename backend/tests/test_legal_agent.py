"""
Unit tests for LegalAgent.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies published to signal bus
- Parse handles markdown-fenced JSON
- Parse handles empty / malformed responses
- load_data() reads the correct JSON file
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from conftest import VALID_ANOMALY, make_claude_response


@pytest.fixture
def legal_agent(mock_anthropic_client, mock_signal_bus):
    from agents.legal_agent import LegalAgent
    agent = LegalAgent()
    agent.client = mock_anthropic_client
    return agent


SAMPLE_CONTRACTS_DATA = {
    "contracts": [
        {
            "client": "Nexus Corp",
            "arr": 516000,
            "renewal_date": "2024-04-15",
            "sla_uptime": 99.9,
            "termination_clause": "30_day_notice_no_penalty",
            "compliance_required": ["PCI_DSS", "SOC2"],
        }
    ],
    "investor_terms": {
        "down_round_clause": "triggers_below_3_month_runway",
    },
}

LEGAL_ANOMALY = {**VALID_ANOMALY, "agent_domain": "legal", "id": "legal_001"}


class TestLegalAgentRun:
    def test_run_returns_agent_report(self, legal_agent, mock_signal_bus):
        legal_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "legal"

    def test_run_populates_anomalies(self, legal_agent, mock_signal_bus):
        legal_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "legal"

    def test_run_publishes_to_signal_bus(self, legal_agent, mock_signal_bus):
        two = [LEGAL_ANOMALY, {**LEGAL_ANOMALY, "id": "legal_002"}]
        legal_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps(two)
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            legal_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, legal_agent, mock_signal_bus):
        legal_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        assert legal_agent.last_report is report

    def test_run_no_anomalies(self, legal_agent, mock_signal_bus):
        legal_agent.client.models.generate_content.return_value = make_claude_response("[]")
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()


class TestLegalAgentParseAnomalies:
    def test_parse_plain_json(self, legal_agent):
        result = legal_agent._parse_anomalies(json.dumps([LEGAL_ANOMALY]))
        assert len(result) == 1

    def test_parse_markdown_fenced(self, legal_agent):
        fenced = f"```json\n{json.dumps([LEGAL_ANOMALY])}\n```"
        result = legal_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, legal_agent):
        assert legal_agent._parse_anomalies("[]") == []

    def test_parse_malformed_json(self, legal_agent):
        assert legal_agent._parse_anomalies("{invalid") == []

    def test_parse_assigns_domain(self, legal_agent):
        anomaly = {**LEGAL_ANOMALY, "agent_domain": "code_audit"}
        result = legal_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "legal"

    def test_parse_auto_assigns_id(self, legal_agent):
        anomaly = {k: v for k, v in LEGAL_ANOMALY.items() if k != "id"}
        result = legal_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].id.startswith("legal_")

    def test_parse_cross_references_preserved(self, legal_agent):
        anomaly = {**LEGAL_ANOMALY, "cross_references": ["finance", "infra"]}
        result = legal_agent._parse_anomalies(json.dumps([anomaly]))
        assert set(result[0].cross_references) == {"finance", "infra"}

    def test_parse_affected_entities_preserved(self, legal_agent):
        anomaly = {**LEGAL_ANOMALY, "affected_entities": ["Nexus Corp", "Acme SaaS"]}
        result = legal_agent._parse_anomalies(json.dumps([anomaly]))
        assert "Nexus Corp" in result[0].affected_entities

    def test_parse_response_with_extra_text_before_array(self, legal_agent):
        """_parse_anomalies should find the array even when Claude adds preamble text."""
        preamble = "Here are the anomalies I detected:\n"
        raw = preamble + json.dumps([LEGAL_ANOMALY])
        result = legal_agent._parse_anomalies(raw)
        assert len(result) == 1


class TestLegalAgentLoadData:
    def test_load_data_returns_dict(self, legal_agent):
        """load_data() always returns a dict."""
        with patch.object(legal_agent, "_extract_pdfs", return_value=[]), \
             patch.object(legal_agent, "_web_search_regulatory", return_value=[]):
            data = legal_agent.load_data()
        assert isinstance(data, dict)

    def test_load_data_has_data_sources_key(self, legal_agent):
        """load_data() always includes a data_sources list."""
        with patch.object(legal_agent, "_extract_pdfs", return_value=[]), \
             patch.object(legal_agent, "_web_search_regulatory", return_value=[]):
            data = legal_agent.load_data()
        assert "data_sources" in data

    def test_load_data_calls_extract_pdfs(self, legal_agent):
        """load_data() calls _extract_pdfs() as the primary data source."""
        with patch.object(legal_agent, "_extract_pdfs", return_value=[]) as mock_pdfs, \
             patch.object(legal_agent, "_web_search_regulatory", return_value=[]):
            legal_agent.load_data()
        mock_pdfs.assert_called_once()

    def test_load_data_falls_back_to_json_when_no_pdfs(self, legal_agent):
        """With no PDFs, load_data() loads contracts.json as fallback."""
        with patch.object(legal_agent, "_extract_pdfs", return_value=[]), \
             patch.object(legal_agent, "_web_search_regulatory", return_value=[]):
            data = legal_agent.load_data()
        assert "contracts" in data


class TestLegalAgentWebSearch:
    """Tests for _web_search_regulatory — unit (mocked) and integration (real network)."""

    EXPECTED_QUERIES = [
        "PCI DSS 4.0 compliance requirements 2026",
        "SOC 2 Type II audit requirements SaaS startup",
        "GDPR enforcement actions SaaS 2026",
    ]

    def _make_ddgs_hit(self, title="T", body="B" * 600, href="https://example.com"):
        return {"title": title, "body": body, "href": href}

    def _mock_ddgs(self, hits_per_query=2):
        """Return a context-manager mock for DDGS that yields `hits_per_query` hits per query."""
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            self._make_ddgs_hit(title=f"Result {i}") for i in range(hits_per_query)
        ]
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ctx.__exit__ = MagicMock(return_value=False)
        return mock_ctx, mock_ddgs_instance

    def test_returns_list(self, legal_agent):
        """_web_search_regulatory always returns a list."""
        mock_ctx, _ = self._mock_ddgs()
        with patch("ddgs.DDGS", return_value=mock_ctx):
            result = legal_agent._web_search_regulatory()
        assert isinstance(result, list)

    def test_result_has_required_keys(self, legal_agent):
        """Each result dict must have query, title, snippet, and url."""
        mock_ctx, _ = self._mock_ddgs(hits_per_query=1)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            results = legal_agent._web_search_regulatory()
        assert len(results) > 0
        for r in results:
            assert "query" in r
            assert "title" in r
            assert "snippet" in r
            assert "url" in r

    def test_snippet_truncated_to_500_chars(self, legal_agent):
        """Snippet must be at most 500 characters even when body is longer."""
        mock_ctx, _ = self._mock_ddgs(hits_per_query=1)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            results = legal_agent._web_search_regulatory()
        for r in results:
            assert len(r["snippet"]) <= 500

    def test_searches_all_three_queries(self, legal_agent):
        """All three regulatory queries must be issued to DDGS."""
        mock_ctx, mock_ddgs_instance = self._mock_ddgs(hits_per_query=1)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            legal_agent._web_search_regulatory()
        actual_queries = [call.args[0] for call in mock_ddgs_instance.text.call_args_list]
        assert actual_queries == self.EXPECTED_QUERIES

    def test_at_most_two_results_per_query(self, legal_agent):
        """max_results=2 is passed to DDGS, so no more than 2 hits per query."""
        mock_ctx, mock_ddgs_instance = self._mock_ddgs(hits_per_query=2)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            results = legal_agent._web_search_regulatory()
        # 3 queries × 2 hits = 6 max
        assert len(results) <= len(self.EXPECTED_QUERIES) * 2
        for call in mock_ddgs_instance.text.call_args_list:
            assert call.kwargs.get("max_results", call.args[1] if len(call.args) > 1 else 2) == 2

    def test_query_field_matches_search_term(self, legal_agent):
        """The 'query' field in each result must match the query that produced it."""
        mock_ctx, _ = self._mock_ddgs(hits_per_query=1)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            results = legal_agent._web_search_regulatory()
        returned_queries = {r["query"] for r in results}
        assert returned_queries.issubset(set(self.EXPECTED_QUERIES))

    def test_returns_empty_on_import_error(self, legal_agent):
        """Returns [] gracefully when duckduckgo_search is not installed."""
        with patch.dict("sys.modules", {"ddgs": None}):
            result = legal_agent._web_search_regulatory()
        assert result == []

    def test_returns_empty_on_network_error(self, legal_agent):
        """Returns [] gracefully when DDGS raises a network exception."""
        mock_ctx = MagicMock()
        mock_ctx.__enter__ = MagicMock(side_effect=Exception("network error"))
        mock_ctx.__exit__ = MagicMock(return_value=False)
        with patch("ddgs.DDGS", return_value=mock_ctx):
            result = legal_agent._web_search_regulatory()
        assert result == []

    @pytest.mark.network
    def test_real_web_search_returns_results(self, legal_agent):
        """Integration: actually calls DuckDuckGo and checks result structure."""
        results = legal_agent._web_search_regulatory()
        # Network may return nothing in restricted environments — just validate shape
        assert isinstance(results, list)
        for r in results:
            assert "query" in r and "title" in r and "snippet" in r and "url" in r
            assert r["query"] in self.EXPECTED_QUERIES
            assert len(r["snippet"]) <= 500

    @pytest.mark.network
    def test_real_web_search_covers_all_queries(self, legal_agent):
        """Integration: results should span all three regulatory queries."""
        results = legal_agent._web_search_regulatory()
        if not results:
            pytest.skip("DuckDuckGo returned no results in this environment")
        returned_queries = {r["query"] for r in results}
        assert returned_queries == set(self.EXPECTED_QUERIES)


class TestLegalAgentDataFile:
    """Validate the real contracts.json file on disk."""

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/contracts.json")

    @pytest.fixture(scope="class")
    def data(self):
        with open(self.DATA_PATH, "r") as f:
            return json.load(f)

    def test_data_file_exists(self):
        assert os.path.exists(self.DATA_PATH), "contracts.json not found"

    def test_data_file_is_valid_json(self):
        with open(self.DATA_PATH, "r") as f:
            parsed = json.load(f)
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, data):
        required = {"metadata", "contracts", "compliance_obligations"}
        for key in required:
            assert key in data, f"Missing top-level key: {key}"

    def test_contracts_is_non_empty_list(self, data):
        assert isinstance(data["contracts"], list)
        assert len(data["contracts"]) > 0

    def test_contract_entries_have_required_fields(self, data):
        # id, client, contract_type, status, and clauses are always present
        required = {"id", "client", "contract_type", "status", "clauses"}
        for contract in data["contracts"]:
            missing = required - contract.keys()
            assert not missing, f"Contract {contract.get('id', '?')} missing: {missing}"

    def test_contract_clauses_is_list(self, data):
        for contract in data["contracts"]:
            assert isinstance(contract["clauses"], list), (
                f"{contract['id']}: clauses must be a list"
            )

    def test_contract_annual_value_is_numeric_when_present(self, data):
        for contract in data["contracts"]:
            if "annual_contract_value" in contract:
                assert isinstance(contract["annual_contract_value"], (int, float)), (
                    f"{contract['id']}: annual_contract_value must be numeric"
                )

    def test_compliance_obligations_is_list(self, data):
        assert isinstance(data["compliance_obligations"], list)
        assert len(data["compliance_obligations"]) > 0

    def test_compliance_entries_have_standard_and_status(self, data):
        for obligation in data["compliance_obligations"]:
            assert "standard" in obligation, "Compliance obligation missing 'standard'"
            assert "status" in obligation, "Compliance obligation missing 'status'"

    def test_metadata_has_reporting_date(self, data):
        assert "reporting_date" in data["metadata"]

    @pytest.mark.usefixtures("mock_anthropic_client", "mock_signal_bus")
    def test_load_data_reads_real_file(self):
        """LegalAgent.load_data() falls back to contracts.json when no PDFs are present."""
        from agents.legal_agent import LegalAgent
        agent = LegalAgent()
        with patch.object(agent, "_web_search_regulatory", return_value=[]):
            data = agent.load_data()
        assert isinstance(data, dict)
        assert "data_sources" in data
