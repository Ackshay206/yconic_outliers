"""
Unit tests for FinanceAgent.

FinanceAgent uses OpenAI (chat.completions.create) and reads CSV files,
NOT google.genai and NOT financials.json.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies published to signal bus
- Parse handles plain JSON / dict-wrapped JSON from GPT json_object mode
- Parse handles empty / malformed responses
- load_data() returns the expected keys from CSV sources
- Data file presence and schema validation (financials.json still exists on disk)
"""
import json
import os
import pytest
from unittest.mock import patch, MagicMock

from conftest import VALID_ANOMALY, make_openai_response


@pytest.fixture
def finance_agent(mock_openai_client, mock_signal_bus):
    from agents.finance_agent import FinanceAgent
    agent = FinanceAgent()
    agent.client = mock_openai_client
    return agent


FINANCE_ANOMALY = {**VALID_ANOMALY, "agent_domain": "finance", "id": "fin_001"}


class TestFinanceAgentRun:
    def test_run_returns_agent_report(self, finance_agent, mock_signal_bus):
        finance_agent.client.chat.completions.create.return_value = make_openai_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value={"transactions": [], "data_sources": []}):
            report = finance_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "finance"

    def test_run_populates_anomalies(self, finance_agent, mock_signal_bus):
        finance_agent.client.chat.completions.create.return_value = make_openai_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value={"transactions": [], "data_sources": []}):
            report = finance_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "finance"

    def test_run_publishes_to_signal_bus(self, finance_agent, mock_signal_bus):
        two = [FINANCE_ANOMALY, {**FINANCE_ANOMALY, "id": "fin_002"}]
        finance_agent.client.chat.completions.create.return_value = make_openai_response(
            json.dumps(two)
        )
        with patch.object(finance_agent, "load_data", return_value={"transactions": [], "data_sources": []}):
            finance_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, finance_agent, mock_signal_bus):
        finance_agent.client.chat.completions.create.return_value = make_openai_response(
            json.dumps([FINANCE_ANOMALY])
        )
        with patch.object(finance_agent, "load_data", return_value={"transactions": [], "data_sources": []}):
            report = finance_agent.run()

        assert finance_agent.last_report is report

    def test_run_no_anomalies(self, finance_agent, mock_signal_bus):
        finance_agent.client.chat.completions.create.return_value = make_openai_response("[]")
        with patch.object(finance_agent, "load_data", return_value={"transactions": [], "data_sources": []}):
            report = finance_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()


class TestFinanceAgentParseAnomalies:
    def test_parse_plain_json(self, finance_agent):
        result = finance_agent._parse_anomalies(json.dumps([FINANCE_ANOMALY]))
        assert len(result) == 1

    def test_parse_dict_wrapped_anomalies_key(self, finance_agent):
        """GPT json_object mode may wrap array: {"anomalies": [...]}"""
        wrapped = {"anomalies": [FINANCE_ANOMALY]}
        result = finance_agent._parse_anomalies(json.dumps(wrapped))
        assert len(result) == 1

    def test_parse_dict_wrapped_results_key(self, finance_agent):
        wrapped = {"results": [FINANCE_ANOMALY]}
        result = finance_agent._parse_anomalies(json.dumps(wrapped))
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
    def test_load_data_returns_dict(self, finance_agent):
        """load_data() always returns a dict regardless of CSV availability."""
        data = finance_agent.load_data()
        assert isinstance(data, dict)

    def test_load_data_has_data_sources_key(self, finance_agent):
        """load_data() always includes a data_sources list."""
        data = finance_agent.load_data()
        assert "data_sources" in data

    def test_load_data_has_transaction_keys(self, finance_agent):
        """load_data() must include all three CSV-backed keys."""
        data = finance_agent.load_data()
        for key in ("transactions", "revenue_pipeline", "funding_runway"):
            assert key in data, f"Missing key: {key}"

    def test_load_data_returns_lists_for_csv_keys(self, finance_agent):
        """All three CSV keys should map to lists."""
        data = finance_agent.load_data()
        for key in ("transactions", "revenue_pipeline", "funding_runway"):
            assert isinstance(data[key], list), f"{key} must be a list"


class TestFinanceAgentDataFile:
    """Validate the financials.json file on disk (legacy reference file)."""

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/financials.json")

    @pytest.fixture(scope="class")
    def data(self):
        with open(self.DATA_PATH, "r") as f:
            return json.load(f)

    def test_data_file_exists(self):
        assert os.path.exists(self.DATA_PATH), "financials.json not found"

    def test_data_file_is_valid_json(self):
        with open(self.DATA_PATH, "r") as f:
            parsed = json.load(f)
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, data):
        required = {
            "metadata", "monthly_revenue", "revenue_concentration",
            "monthly_expenses", "cash_position", "investor_agreement", "burn_rate_trend",
        }
        for key in required:
            assert key in data, f"Missing top-level key: {key}"

    def test_monthly_revenue_is_non_empty_list(self, data):
        assert isinstance(data["monthly_revenue"], list)
        assert len(data["monthly_revenue"]) > 0

    def test_monthly_revenue_entries_have_required_fields(self, data):
        for entry in data["monthly_revenue"]:
            assert "month" in entry
            assert "total" in entry
            assert isinstance(entry["total"], (int, float))

    def test_revenue_concentration_has_nexus_percentage(self, data):
        rc = data["revenue_concentration"]
        assert "nexus_corp_percentage" in rc
        assert isinstance(rc["nexus_corp_percentage"], (int, float))

    def test_cash_position_has_runway(self, data):
        cp = data["cash_position"]
        assert "current_runway_months" in cp
        assert isinstance(cp["current_runway_months"], (int, float))

    def test_cash_position_has_current_balance(self, data):
        assert "current_balance" in data["cash_position"]
        assert isinstance(data["cash_position"]["current_balance"], (int, float))

    def test_investor_agreement_has_clauses(self, data):
        ia = data["investor_agreement"]
        assert "clauses" in ia
        assert isinstance(ia["clauses"], list)
        assert len(ia["clauses"]) > 0

    def test_burn_rate_trend_has_acceleration_flag(self, data):
        brt = data["burn_rate_trend"]
        assert "acceleration" in brt
        assert "flag" in brt

    def test_monthly_expenses_is_non_empty_list(self, data):
        assert isinstance(data["monthly_expenses"], list)
        assert len(data["monthly_expenses"]) > 0

    @pytest.mark.usefixtures("mock_openai_client", "mock_signal_bus")
    def test_load_data_reads_csv_files(self):
        """FinanceAgent.load_data() reads CSV files; data_sources reflects which were found."""
        from agents.finance_agent import FinanceAgent
        agent = FinanceAgent()
        data = agent.load_data()
        assert "data_sources" in data
        assert "transactions" in data
