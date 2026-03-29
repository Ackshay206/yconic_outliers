"""
Unit tests for ProductAgent.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies published to signal bus
- Parse handles markdown-fenced JSON
- Parse handles empty / malformed responses
- load_data() reads the correct JSON file
- Data file presence and schema validation (real file on disk)
"""
import json
import os
import pytest
from unittest.mock import patch

from conftest import VALID_ANOMALY, make_claude_response


@pytest.fixture
def product_agent(mock_gemini_client, mock_signal_bus):
    from agents.product_agent import ProductAgent
    agent = ProductAgent()
    agent.client = mock_gemini_client
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
        product_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "product"

    def test_run_populates_anomalies(self, product_agent, mock_signal_bus):
        product_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "product"

    def test_run_publishes_to_signal_bus(self, product_agent, mock_signal_bus):
        two = [PRODUCT_ANOMALY, {**PRODUCT_ANOMALY, "id": "prod_002"}]
        product_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps(two)
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            product_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, product_agent, mock_signal_bus):
        product_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PRODUCT_ANOMALY])
        )
        with patch.object(product_agent, "load_data", return_value=SAMPLE_PRODUCT_DATA):
            report = product_agent.run()

        assert product_agent.last_report is report

    def test_run_no_anomalies(self, product_agent, mock_signal_bus):
        product_agent.client.models.generate_content.return_value = make_claude_response("[]")
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
    def test_load_data_returns_dict(self, product_agent):
        """load_data() always returns a dict."""
        data = product_agent.load_data()
        assert isinstance(data, dict)

    def test_load_data_has_data_sources_key(self, product_agent):
        """load_data() always includes a data_sources list."""
        data = product_agent.load_data()
        assert "data_sources" in data

    def test_load_data_no_sources_returns_status(self, product_agent):
        """When both CSV and JSON are absent, returns a status dict."""
        with patch("agents.product_agent.CSV_PATH") as mock_csv, \
             patch("agents.product_agent.FALLBACK_JSON") as mock_json:
            mock_csv.exists.return_value = False
            mock_json.exists.return_value = False
            data = product_agent.load_data()
        assert data.get("status") == "no product data found"


class TestProductAgentDataFile:
    """Validate the real product_metrics.json file on disk."""

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/product_metrics.json")

    @pytest.fixture(scope="class")
    def data(self):
        with open(self.DATA_PATH, "r") as f:
            return json.load(f)

    def test_data_file_exists(self):
        assert os.path.exists(self.DATA_PATH), "product_metrics.json not found"

    def test_data_file_is_valid_json(self):
        with open(self.DATA_PATH, "r") as f:
            parsed = json.load(f)
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, data):
        required = {"metadata", "overall_metrics", "feature_engagement",
                    "support_tickets", "churn_analysis"}
        for key in required:
            assert key in data, f"Missing top-level key: {key}"

    def test_feature_engagement_is_non_empty_list(self, data):
        assert isinstance(data["feature_engagement"], list)
        assert len(data["feature_engagement"]) > 0

    def test_feature_entries_have_required_fields(self, data):
        required = {"feature", "service", "weekly_metrics"}
        for feat in data["feature_engagement"]:
            missing = required - feat.keys()
            assert not missing, f"Feature {feat.get('feature', '?')} missing: {missing}"

    def test_weekly_metrics_is_non_empty_list(self, data):
        for feat in data["feature_engagement"]:
            assert isinstance(feat["weekly_metrics"], list)
            assert len(feat["weekly_metrics"]) > 0, (
                f"{feat['feature']}: weekly_metrics must not be empty"
            )

    def test_overall_metrics_has_wau(self, data):
        om = data["overall_metrics"]
        assert "weekly_active_users" in om

    def test_support_tickets_has_weekly_volume(self, data):
        st = data["support_tickets"]
        assert "weekly_volume" in st
        assert isinstance(st["weekly_volume"], list)
        assert len(st["weekly_volume"]) > 0

    def test_churn_analysis_has_churned_mrr(self, data):
        ca = data["churn_analysis"]
        assert "churned_mrr_last_30_days" in ca
        assert isinstance(ca["churned_mrr_last_30_days"], (int, float))

    def test_churn_analysis_has_acceleration_flag(self, data):
        assert "churn_acceleration_flag" in data["churn_analysis"]

    @pytest.mark.usefixtures("mock_gemini_client", "mock_signal_bus")
    def test_load_data_reads_real_file(self):
        """ProductAgent.load_data() must successfully parse product_data.csv or fallback JSON."""
        from agents.product_agent import ProductAgent
        agent = ProductAgent()
        data = agent.load_data()
        assert isinstance(data, dict)
        assert "data_sources" in data
