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
import pytest
from unittest.mock import patch, mock_open

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
        legal_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "legal"

    def test_run_populates_anomalies(self, legal_agent, mock_signal_bus):
        legal_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "legal"

    def test_run_publishes_to_signal_bus(self, legal_agent, mock_signal_bus):
        two = [LEGAL_ANOMALY, {**LEGAL_ANOMALY, "id": "legal_002"}]
        legal_agent.client.messages.create.return_value = make_claude_response(
            json.dumps(two)
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            legal_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, legal_agent, mock_signal_bus):
        legal_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([LEGAL_ANOMALY])
        )
        with patch.object(legal_agent, "load_data", return_value=SAMPLE_CONTRACTS_DATA):
            report = legal_agent.run()

        assert legal_agent.last_report is report

    def test_run_no_anomalies(self, legal_agent, mock_signal_bus):
        legal_agent.client.messages.create.return_value = make_claude_response("[]")
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
    def test_load_data_reads_json_file(self, legal_agent):
        fake_data = {"contracts": []}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = legal_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, legal_agent):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                legal_agent.load_data()
