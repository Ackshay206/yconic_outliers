"""
Unit tests for InfraAgent.

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
def infra_agent(mock_anthropic_client, mock_signal_bus):
    from agents.infra_agent import InfraAgent
    agent = InfraAgent()
    agent.client = mock_anthropic_client
    return agent


SAMPLE_INFRA_DATA = {
    "services": [
        {
            "name": "payments-service",
            "uptime_percent": 99.1,
            "deploys_last_14_days": 0,
            "p99_response_ms": 4200,
            "error_rate_percent": 1.8,
        }
    ],
    "ci_cd": {
        "failure_rate_percent": 25,
    },
}

INFRA_ANOMALY = {**VALID_ANOMALY, "agent_domain": "infra", "id": "infra_001"}


class TestInfraAgentRun:
    def test_run_returns_agent_report(self, infra_agent, mock_signal_bus):
        infra_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([INFRA_ANOMALY])
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "infra"

    def test_run_populates_anomalies(self, infra_agent, mock_signal_bus):
        infra_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([INFRA_ANOMALY])
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "infra"

    def test_run_publishes_each_anomaly(self, infra_agent, mock_signal_bus):
        three = [
            {**INFRA_ANOMALY, "id": f"infra_00{i}"} for i in range(1, 4)
        ]
        infra_agent.client.messages.create.return_value = make_claude_response(
            json.dumps(three)
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            infra_agent.run()

        assert mock_signal_bus.publish.call_count == 3

    def test_run_caches_last_report(self, infra_agent, mock_signal_bus):
        infra_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([INFRA_ANOMALY])
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert infra_agent.last_report is report

    def test_run_no_anomalies(self, infra_agent, mock_signal_bus):
        infra_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()

    def test_run_raw_data_summary_present(self, infra_agent, mock_signal_bus):
        """AgentReport must include a non-empty raw_data_summary."""
        infra_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert report.raw_data_summary != ""
        assert "infra" in report.raw_data_summary


class TestInfraAgentParseAnomalies:
    def test_parse_plain_json(self, infra_agent):
        result = infra_agent._parse_anomalies(json.dumps([INFRA_ANOMALY]))
        assert len(result) == 1

    def test_parse_markdown_fenced(self, infra_agent):
        fenced = f"```json\n{json.dumps([INFRA_ANOMALY])}\n```"
        result = infra_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, infra_agent):
        assert infra_agent._parse_anomalies("[]") == []

    def test_parse_malformed_json(self, infra_agent):
        assert infra_agent._parse_anomalies("I found no issues today.") == []

    def test_parse_assigns_domain(self, infra_agent):
        anomaly = {**INFRA_ANOMALY, "agent_domain": "finance"}
        result = infra_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "infra"

    def test_parse_auto_assigns_id(self, infra_agent):
        anomaly = {k: v for k, v in INFRA_ANOMALY.items() if k != "id"}
        result = infra_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].id.startswith("infra_")

    def test_parse_multiple_anomalies(self, infra_agent):
        anomalies = [{**INFRA_ANOMALY, "id": f"infra_00{i}"} for i in range(1, 4)]
        result = infra_agent._parse_anomalies(json.dumps(anomalies))
        assert len(result) == 3


class TestInfraAgentLoadData:
    def test_load_data_reads_json_file(self, infra_agent):
        fake_data = {"services": []}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = infra_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, infra_agent):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                infra_agent.load_data()
