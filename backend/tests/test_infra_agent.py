"""
Unit tests for InfraAgent.

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
        infra_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([INFRA_ANOMALY])
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "infra"

    def test_run_populates_anomalies(self, infra_agent, mock_signal_bus):
        infra_agent.client.models.generate_content.return_value = make_claude_response(
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
        infra_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps(three)
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            infra_agent.run()

        assert mock_signal_bus.publish.call_count == 3

    def test_run_caches_last_report(self, infra_agent, mock_signal_bus):
        infra_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([INFRA_ANOMALY])
        )
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert infra_agent.last_report is report

    def test_run_no_anomalies(self, infra_agent, mock_signal_bus):
        infra_agent.client.models.generate_content.return_value = make_claude_response("[]")
        with patch.object(infra_agent, "load_data", return_value=SAMPLE_INFRA_DATA):
            report = infra_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()

    def test_run_raw_data_summary_present(self, infra_agent, mock_signal_bus):
        """AgentReport must include a non-empty raw_data_summary."""
        infra_agent.client.models.generate_content.return_value = make_claude_response("[]")
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
    def test_load_data_returns_dict(self, infra_agent):
        """load_data() always returns a dict."""
        data = infra_agent.load_data()
        assert isinstance(data, dict)

    def test_load_data_has_data_sources_key(self, infra_agent):
        """load_data() always includes a data_sources list."""
        data = infra_agent.load_data()
        assert "data_sources" in data

    def test_load_data_delegates_to_load_infrastructure_json(self, infra_agent):
        """load_data() calls _load_infrastructure_json() as its primary data source."""
        fake = {"cloud_instances": [], "data_sources": ["test"]}
        with patch.object(infra_agent, "_load_infrastructure_json", return_value=fake) as mock_fn:
            data = infra_agent.load_data()
        mock_fn.assert_called_once()
        assert data["cloud_instances"] == []

    def test_load_data_no_github_token_skips_actions(self, infra_agent):
        """Without GITHUB_TOKEN, GitHub Actions fetch is skipped."""
        with patch.dict("os.environ", {}, clear=True):
            data = infra_agent.load_data()
        assert "github_actions_error" not in data or "github_actions" not in data


class TestInfraAgentDataFile:
    """Validate the real infrastructure.json file on disk."""

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/infrastructure.json")

    @pytest.fixture(scope="class")
    def data(self):
        with open(self.DATA_PATH, "r") as f:
            return json.load(f)

    def test_data_file_exists(self):
        assert os.path.exists(self.DATA_PATH), "infrastructure.json not found"

    def test_data_file_is_valid_json(self):
        with open(self.DATA_PATH, "r") as f:
            parsed = json.load(f)
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, data):
        required = {"metadata", "cloud_instances", "databases", "ci_cd", "monitoring"}
        for key in required:
            assert key in data, f"Missing top-level key: {key}"

    def test_cloud_instances_is_non_empty_list(self, data):
        assert isinstance(data["cloud_instances"], list)
        assert len(data["cloud_instances"]) > 0

    def test_cloud_instance_entries_have_required_fields(self, data):
        required = {"id", "name", "role", "status"}
        for instance in data["cloud_instances"]:
            missing = required - instance.keys()
            assert not missing, f"Instance {instance.get('name', '?')} missing: {missing}"

    def test_databases_is_non_empty_list(self, data):
        assert isinstance(data["databases"], list)
        assert len(data["databases"]) > 0

    def test_database_has_backup_enabled(self, data):
        for db in data["databases"]:
            assert "backup_enabled" in db

    def test_ci_cd_has_pipeline_info(self, data):
        ci = data["ci_cd"]
        assert "provider" in ci
        assert "stages" in ci
        assert isinstance(ci["stages"], list)
        assert len(ci["stages"]) > 0

    def test_ci_cd_has_weekly_pipeline_runs(self, data):
        assert "weekly_pipeline_runs" in data["ci_cd"]

    def test_monitoring_has_dashboards(self, data):
        mon = data["monitoring"]
        assert "dashboards" in mon
        assert isinstance(mon["dashboards"], list)

    def test_metadata_has_cloud_provider(self, data):
        assert "cloud_provider" in data["metadata"]

    @pytest.mark.usefixtures("mock_anthropic_client", "mock_signal_bus")
    def test_load_data_reads_real_file(self):
        """InfraAgent.load_data() must successfully parse infrastructure.json."""
        from agents.infra_agent import InfraAgent
        agent = InfraAgent()
        data = agent.load_data()
        assert "cloud_instances" in data
        assert isinstance(data["cloud_instances"], list)
        assert len(data["cloud_instances"]) > 0
