"""
Unit tests for ProductAgent.

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
def product_agent(mock_anthropic_client, mock_signal_bus):
    from agents.product_agent import ProductAgent
    agent = ProductAgent()
    agent.client = mock_anthropic_client
    return agent


SAMPLE_PRODUCT_DATA = {
    "weekly_active_users": [34000, 32000, 29000, 25000],
    "nps_score": 18,
    "monthly_churn_rate": 0.07,
    "features": [
        {
            "name": "payments",
            "adoption_last_4_weeks": [0.82, 0.75, 0.61, 0.48],
            "error_rate_percent": 2.1,
        }
    ],
    "support_tickets": {
        "volume_last_week": 430,
        "sentiment": "negative",
    },
}

PRODUCT_ANOMALY = {**VALID_ANOMALY, "agent_domain": "product", "id": "prod_001"}


class TestProductAgentRun:
    def test_run_returns_agent_report(self, product_agent, mock_signal_bus):
        product_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "product"

    def test_run_populates_anomalies(self, product_agent, mock_signal_bus):
        product_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "product"

    def test_run_publishes_to_signal_bus(self, product_agent, mock_signal_bus):
        two = [PRODUCT_ANOMALY, {**PRODUCT_ANOMALY, "id": "prod_002"}]
        product_agent.client.messages.create.return_value = make_claude_response(
            json.dumps(two)
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            product_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, product_agent, mock_signal_bus):
        product_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        assert product_agent.last_report is report

    def test_run_no_anomalies(self, product_agent, mock_signal_bus):
        product_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()


class TestProductAgentParseAnomalies:
    def test_parse_plain_json(self, product_agent):
        result = product_agent._parse_anomalies(json.dumps([PRODUCT_ANOMALY]))
        assert len(result) == 1

    def test_parse_markdown_fenced(self, product_agent):
        fenced = f"```json\n{json.dumps([PRODUCT_ANOMALY])}\n```"
        result = product_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, product_agent):
        assert product_agent._parse_anomalies("[]") == []

    def test_parse_malformed_json(self, product_agent):
        assert product_agent._parse_anomalies("no anomalies found") == []

    def test_parse_assigns_domain(self, product_agent):
        anomaly = {**PRODUCT_ANOMALY, "agent_domain": "infra"}
        result = product_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "product"

    def test_parse_auto_assigns_id(self, product_agent):
        anomaly = {k: v for k, v in PRODUCT_ANOMALY.items() if k != "id"}
        result = product_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].id.startswith("product_")

    def test_parse_confidence_range_validated(self, product_agent):
        """Anomaly with confidence < 0 should be skipped by Pydantic validation."""
        anomaly = {**PRODUCT_ANOMALY, "confidence": -0.1}
        result = product_agent._parse_anomalies(json.dumps([anomaly]))
        assert result == []

    def test_parse_evidence_preserved(self, product_agent):
        """Evidence dict should be passed through unchanged."""
        anomaly = {**PRODUCT_ANOMALY, "evidence": {"churn": "7%", "nps": 18}}
        result = product_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].evidence == {"churn": "7%", "nps": 18}


class TestProductAgentLoadData:
    def test_load_data_reads_json_file(self, product_agent):
        fake_data = {"nps_score": 42}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = product_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, product_agent):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                product_agent.load_data()
