"""
Unit tests for PeopleAgent.

Covers:
- Successful run() returning a valid AgentReport
- Anomalies are published to the signal bus
- Parse handles markdown-fenced JSON from Claude
- Parse handles an empty array (no anomalies)
- Parse handles malformed JSON gracefully
- load_data() reads the correct JSON file
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open

from conftest import VALID_ANOMALY, make_claude_response


# ---------------------------------------------------------------------------
# Fixture: a PeopleAgent with mocked Anthropic client
# ---------------------------------------------------------------------------
@pytest.fixture
def people_agent(mock_anthropic_client, mock_signal_bus):
    from agents.people_agent import PeopleAgent
    agent = PeopleAgent()
    agent.client = mock_anthropic_client
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
        people_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "people"

    def test_run_populates_anomalies(self, people_agent, mock_signal_bus):
        """run() should parse Claude's JSON response into Anomaly objects."""
        people_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "people"
        assert report.anomalies[0].severity == PEOPLE_ANOMALY["severity"]

    def test_run_publishes_to_signal_bus(self, people_agent, mock_signal_bus):
        """Each detected anomaly must be published to the signal bus."""
        people_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY, {**PEOPLE_ANOMALY, "id": "test_002"}])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            people_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, people_agent, mock_signal_bus):
        """run() should store the report in last_report for later retrieval."""
        people_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([PEOPLE_ANOMALY])
        )
        with patch.object(people_agent, "load_data", return_value=SAMPLE_TEAM_DATA):
            report = people_agent.run()

        assert people_agent.last_report is report

    def test_run_no_anomalies(self, people_agent, mock_signal_bus):
        """run() with an empty anomaly array should return a report with no anomalies."""
        people_agent.client.messages.create.return_value = make_claude_response("[]")
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
    def test_load_data_reads_json_file(self, people_agent):
        """load_data() should open and parse the team_activity.json file."""
        fake_data = {"team": []}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = people_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, people_agent):
        """load_data() should propagate FileNotFoundError when data file is missing."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                people_agent.load_data()
