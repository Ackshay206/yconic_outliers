"""
Unit tests for FinanceAgent.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies are published to the signal bus
- Parse handles markdown-fenced JSON from Claude
- Parse handles an empty array (no anomalies)
- Parse handles malformed JSON gracefully
- load_data() reads the correct JSON file
"""
import json
import pytest
from unittest.mock import patch, mock_open

from conftest import VALID_ANOMALY, make_claude_response


@pytest.fixture
def finance_agent(mock_anthropic_client, mock_signal_bus):
    from agents.finance_agent import FinanceAgent
    agent = FinanceAgent()
    agent.client = mock_anthropic_client
    return agent


SAMPLE_FINANCIALS_DATA = {
    "monthly_revenue": [120000, 118000, 115000, 110000],
    "monthly_burn": [95000, 97000, 100000, 105000],
    "cash_on_hand": 420000,
    "clients": [
        {"name": "Nexus Corp", "arr": 516000, "percent_of_revenue": 0.42}
    ],
}

FINANCE_ANOMALY = {**VALID_ANOMALY, "agent_domain": "finance", "id": "fin_001"}


class TestFinanceAgentRun:
    def test_run_returns_agent_report(self, finance_agent, mock_signal_bus):
        finance_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value=SAMPLE_FINANCIALS_DATA):
            report = finance_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "finance"

    def test_run_populates_anomalies(self, finance_agent, mock_signal_bus):
        finance_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value=SAMPLE_FINANCIALS_DATA):
            report = finance_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "finance"

    def test_run_publishes_to_signal_bus(self, finance_agent, mock_signal_bus):
        two_anomalies = [FINANCE_ANOMALY, {**FINANCE_ANOMALY, "id": "fin_002"}]
        finance_agent.client.messages.create.return_value = make_claude_response(
            json.dumps(two_anomalies)
        )
        with patch.object(finance_agent, "load_data", return_value=SAMPLE_FINANCIALS_DATA):
            finance_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, finance_agent, mock_signal_bus):
        finance_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value=SAMPLE_FINANCIALS_DATA):
            report = finance_agent.run()

        assert finance_agent.last_report is report

    def test_run_no_anomalies(self, finance_agent, mock_signal_bus):
        finance_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(finance_agent, "load_data", return_value=SAMPLE_FINANCIALS_DATA):
            report = finance_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()


class TestFinanceAgentParseAnomalies:
    def test_parse_plain_json(self, finance_agent):
        result = finance_agent._parse_anomalies(json.dumps([FINANCE_ANOMALY]))
        assert len(result) == 1

    def test_parse_markdown_fenced(self, finance_agent):
        fenced = f"```json\n{json.dumps([FINANCE_ANOMALY])}\n```"
        result = finance_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, finance_agent):
        assert finance_agent._parse_anomalies("[]") == []

    def test_parse_malformed_json(self, finance_agent):
        assert finance_agent._parse_anomalies("{broken}") == []

    def test_parse_assigns_domain(self, finance_agent):
        anomaly = {**FINANCE_ANOMALY, "agent_domain": "people"}
        result = finance_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "finance"

    def test_parse_auto_assigns_id(self, finance_agent):
        anomaly = {k: v for k, v in FINANCE_ANOMALY.items() if k != "id"}
        result = finance_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].id.startswith("finance_")

    def test_severity_range_validated(self, finance_agent):
        """Anomaly with severity out of range [0.0, 1.0] should be skipped."""
        anomaly = {**FINANCE_ANOMALY, "severity": 1.5}
        result = finance_agent._parse_anomalies(json.dumps([anomaly]))
        assert result == []


class TestFinanceAgentLoadData:
    def test_load_data_reads_json_file(self, finance_agent):
        fake_data = {"cash_on_hand": 500000}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = finance_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, finance_agent):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                finance_agent.load_data()
