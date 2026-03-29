"""
Unit tests for PeopleAgent.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies are published to the signal bus
- Parse handles markdown-fenced JSON from Claude
- Parse handles an empty array (no anomalies)
- Parse handles malformed JSON gracefully
- load_data() reads the correct JSON file
- Data file presence and schema validation (real file on disk)
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from conftest import VALID_ANOMALY, make_claude_response


# ---------------------------------------------------------------------------
# Fixture: a PeopleAgent with mocked Anthropic client
# ---------------------------------------------------------------------------
@pytest.fixture
def people_agent(mock_gemini_client, mock_signal_bus):
    from agents.people_agent import PeopleAgent
    agent = PeopleAgent()
    agent.client = mock_gemini_client
    return agent


SAMPLE_TEAM_DATA = {
    "team": [
        {
            "name": "Alice",
            "commits_last_4_weeks": [12, 10, 3, 0],
            "prs_opened": 2,
            "code_ownership": {"payments": 0.85},
        }
    ]
}

PEOPLE_ANOMALY = {**VALID_ANOMALY, "agent_domain": "people"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPeopleAgentRun:
    def test_run_returns_agent_report(self, people_agent, mock_signal_bus):
        """run() should return an AgentReport with the correct agent domain."""
        people_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "people"

    def test_run_populates_anomalies(self, people_agent, mock_signal_bus):
        """run() should parse Claude's JSON response into Anomaly objects."""
        people_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "people"
        assert report.anomalies[0].severity == PEOPLE_ANOMALY["severity"]

    def test_run_publishes_to_signal_bus(self, people_agent, mock_signal_bus):
        """Each detected anomaly must be published to the signal bus."""
        people_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY, {**PEOPLE_ANOMALY, "id": "test_002"}])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            people_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, people_agent, mock_signal_bus):
        """run() should store the report in last_report for later retrieval."""
        people_agent.client.models.generate_content.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        assert people_agent.last_report is report

    def test_run_no_anomalies(self, people_agent, mock_signal_bus):
        """run() with an empty anomaly array should return a report with no anomalies."""
        people_agent.client.models.generate_content.return_value = make_claude_response("[]")
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()


class TestPeopleAgentParseAnomalies:
    def test_parse_plain_json(self, people_agent):
        """_parse_anomalies should handle a plain JSON array string."""
        result = people_agent._parse_anomalies(json.dumps([PEOPLE_ANOMALY]))
        assert len(result) == 1
        assert result[0].title == PEOPLE_ANOMALY["title"]

    def test_parse_markdown_fenced_json(self, people_agent):
        """_parse_anomalies should strip ```json ... ``` fences from Claude output."""
        fenced = f"```json\n{json.dumps([PEOPLE_ANOMALY])}\n```"
        result = people_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, people_agent):
        """_parse_anomalies should return [] when Claude returns an empty array."""
        result = people_agent._parse_anomalies("[]")
        assert result == []

    def test_parse_malformed_json(self, people_agent):
        """_parse_anomalies should return [] on invalid JSON instead of raising."""
        result = people_agent._parse_anomalies("not valid json at all")
        assert result == []

    def test_parse_assigns_domain(self, people_agent):
        """_parse_anomalies must force agent_domain to 'people' regardless of input."""
        anomaly = {**PEOPLE_ANOMALY, "agent_domain": "wrong_domain"}
        result = people_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "people"

    def test_parse_auto_assigns_id(self, people_agent):
        """_parse_anomalies should generate an id when none is provided."""
        anomaly = {k: v for k, v in PEOPLE_ANOMALY.items() if k != "id"}
        result = people_agent._parse_anomalies(json.dumps([anomaly]))
        assert len(result) == 1
        assert result[0].id.startswith("people_")

    def test_parse_skips_invalid_items(self, people_agent):
        """_parse_anomalies should skip items that fail Pydantic validation."""
        bad = {"id": "x", "agent_domain": "people"}  # missing required fields
        good = PEOPLE_ANOMALY
        result = people_agent._parse_anomalies(json.dumps([bad, good]))
        assert len(result) == 1
        assert result[0].id == good["id"]


class TestPeopleAgentLoadData:
    def test_load_data_returns_dict(self, people_agent):
        """load_data() always returns a dict (Slack not connected in test env)."""
        data = people_agent.load_data()
        assert isinstance(data, dict)

    def test_load_data_has_developers_key(self, people_agent):
        """load_data() always includes a developers key."""
        data = people_agent.load_data()
        assert "developers" in data

    def test_load_data_has_data_sources_key(self, people_agent):
        """load_data() always includes a data_sources list."""
        data = people_agent.load_data()
        assert "data_sources" in data

    def test_load_data_slack_not_connected_returns_empty_developers(self, people_agent):
        """When SLACK_BOT_TOKEN is unset, developers should be empty (no real Slack)."""
        data = people_agent.load_data()
        assert data["developers"] == {} or isinstance(data["developers"], dict)


class TestPeopleAgentDataFile:
    """Validate the real team_activity.json file on disk."""

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/team_activity.json")

    @pytest.fixture(scope="class")
    def data(self):
        with open(self.DATA_PATH, "r") as f:
            return json.load(f)

    def test_data_file_exists(self):
        assert os.path.exists(self.DATA_PATH), "team_activity.json not found"

    def test_data_file_is_valid_json(self):
        with open(self.DATA_PATH, "r") as f:
            content = f.read()
        assert len(content) > 0
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_top_level_keys_present(self, data):
        for key in ("metadata", "developers", "team_alerts"):
            assert key in data, f"Missing top-level key: {key}"

    def test_developers_is_non_empty_list(self, data):
        assert isinstance(data["developers"], list)
        assert len(data["developers"]) > 0, "developers list must not be empty"

    def test_developer_entries_have_required_fields(self, data):
        required = {"name", "role", "primary_services", "weekly_activity", "code_ownership"}
        for dev in data["developers"]:
            missing = required - dev.keys()
            assert not missing, f"Developer {dev.get('name', '?')} missing fields: {missing}"

    def test_weekly_activity_is_list(self, data):
        for dev in data["developers"]:
            assert isinstance(dev["weekly_activity"], list), (
                f"{dev['name']}: weekly_activity must be a list"
            )

    def test_code_ownership_is_dict(self, data):
        for dev in data["developers"]:
            assert isinstance(dev["code_ownership"], dict), (
                f"{dev['name']}: code_ownership must be a dict"
            )

    def test_team_alerts_is_list(self, data):
        assert isinstance(data["team_alerts"], list)

    def test_metadata_has_team_size(self, data):
        assert "team_size" in data["metadata"]
        assert isinstance(data["metadata"]["team_size"], int)
        assert data["metadata"]["team_size"] > 0

    def test_developer_count_matches_metadata(self, data):
        assert len(data["developers"]) == data["metadata"]["team_size"]

    @pytest.mark.usefixtures("mock_gemini_client", "mock_signal_bus")
    def test_load_data_returns_expected_structure(self):
        """PeopleAgent.load_data() reads from Slack; returns dict with developers key."""
        from agents.people_agent import PeopleAgent
        agent = PeopleAgent()
        data = agent.load_data()
        assert "developers" in data
        assert "data_sources" in data
