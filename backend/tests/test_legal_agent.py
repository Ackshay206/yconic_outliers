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
from unittest.mock import patch

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
