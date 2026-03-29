"""
Unit tests for CodeAuditAgent.

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
def code_audit_agent(mock_anthropic_client, mock_signal_bus):
    from agents.code_audit_agent import CodeAuditAgent
    agent = CodeAuditAgent()
    agent.client = mock_anthropic_client
    return agent


SAMPLE_CODEBASE_DATA = {
    "services": [
        {
            "name": "payments-service",
            "bus_factor": 1,
            "primary_owner": "Sarah Chen",
            "owner_commit_percent": 84,
            "test_coverage_percent": 52,
            "prs_merged_without_review_last_month": 3,
        }
    ],
    "cves": [
        {
            "id": "CVE-2024-1234",
            "cvss_score": 8.1,
            "affected_package": "stripe-python",
            "service": "payments-service",
            "patched": False,
        }
    ],
    "dependencies": [
        {
            "package": "django",
            "current_version": "3.2",
            "latest_major": "5.0",
            "versions_behind": 2,
        }
    ],
}

CODE_AUDIT_ANOMALY = {
    **VALID_ANOMALY,
    "agent_domain": "code_audit",
    "id": "ca_001",
}


class TestCodeAuditAgentRun:
    def test_run_returns_agent_report(self, code_audit_agent, mock_signal_bus):
        code_audit_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([CODE_AUDIT_ANOMALY])
        )
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            report = code_audit_agent.run()

        from models import AgentReport
        assert isinstance(report, AgentReport)
        assert report.agent == "code_audit"

    def test_run_populates_anomalies(self, code_audit_agent, mock_signal_bus):
        code_audit_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([CODE_AUDIT_ANOMALY])
        )
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            report = code_audit_agent.run()

        assert len(report.anomalies) == 1
        assert report.anomalies[0].agent_domain == "code_audit"

    def test_run_publishes_to_signal_bus(self, code_audit_agent, mock_signal_bus):
        two = [CODE_AUDIT_ANOMALY, {**CODE_AUDIT_ANOMALY, "id": "ca_002"}]
        code_audit_agent.client.messages.create.return_value = make_claude_response(
            json.dumps(two)
        )
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            code_audit_agent.run()

        assert mock_signal_bus.publish.call_count == 2

    def test_run_caches_last_report(self, code_audit_agent, mock_signal_bus):
        code_audit_agent.client.messages.create.return_value = make_claude_response(
            json.dumps([CODE_AUDIT_ANOMALY])
        )
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            report = code_audit_agent.run()

        assert code_audit_agent.last_report is report

    def test_run_no_anomalies(self, code_audit_agent, mock_signal_bus):
        code_audit_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            report = code_audit_agent.run()

        assert report.anomalies == []
        mock_signal_bus.publish.assert_not_called()

    def test_run_raw_data_summary_mentions_domain(self, code_audit_agent, mock_signal_bus):
        code_audit_agent.client.messages.create.return_value = make_claude_response("[]")
        with patch.object(code_audit_agent, "load_data", return_value=SAMPLE_CODEBASE_DATA):
            report = code_audit_agent.run()

        assert "code_audit" in report.raw_data_summary


class TestCodeAuditAgentParseAnomalies:
    def test_parse_plain_json(self, code_audit_agent):
        result = code_audit_agent._parse_anomalies(json.dumps([CODE_AUDIT_ANOMALY]))
        assert len(result) == 1

    def test_parse_markdown_fenced(self, code_audit_agent):
        fenced = f"```json\n{json.dumps([CODE_AUDIT_ANOMALY])}\n```"
        result = code_audit_agent._parse_anomalies(fenced)
        assert len(result) == 1

    def test_parse_empty_array(self, code_audit_agent):
        assert code_audit_agent._parse_anomalies("[]") == []

    def test_parse_malformed_json(self, code_audit_agent):
        assert code_audit_agent._parse_anomalies("```\nnot json\n```") == []

    def test_parse_assigns_domain(self, code_audit_agent):
        anomaly = {**CODE_AUDIT_ANOMALY, "agent_domain": "people"}
        result = code_audit_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].agent_domain == "code_audit"

    def test_parse_auto_assigns_id(self, code_audit_agent):
        anomaly = {k: v for k, v in CODE_AUDIT_ANOMALY.items() if k != "id"}
        result = code_audit_agent._parse_anomalies(json.dumps([anomaly]))
        assert result[0].id.startswith("code_audit_")

    def test_parse_multiple_anomalies_mixed_validity(self, code_audit_agent):
        """Valid and invalid anomalies in the same array — only valid ones returned."""
        bad = {"id": "ca_bad", "agent_domain": "code_audit"}   # missing required fields
        good = CODE_AUDIT_ANOMALY
        result = code_audit_agent._parse_anomalies(json.dumps([bad, good]))
        assert len(result) == 1
        assert result[0].id == good["id"]

    def test_parse_handles_text_after_array(self, code_audit_agent):
        """_parse_anomalies uses rfind for ']', so trailing text is handled correctly."""
        raw = json.dumps([CODE_AUDIT_ANOMALY]) + "\n\nLet me know if you need more details."
        result = code_audit_agent._parse_anomalies(raw)
        assert len(result) == 1

    def test_parse_severity_boundary_values(self, code_audit_agent):
        """Severity of exactly 0.0 and 1.0 are both valid boundary values."""
        for sev in [0.0, 1.0]:
            anomaly = {**CODE_AUDIT_ANOMALY, "id": f"ca_sev_{sev}", "severity": sev}
            result = code_audit_agent._parse_anomalies(json.dumps([anomaly]))
            assert len(result) == 1
            assert result[0].severity == sev


class TestCodeAuditAgentLoadData:
    def test_load_data_reads_json_file(self, code_audit_agent):
        fake_data = {"cves": [], "services": []}
        m = mock_open(read_data=json.dumps(fake_data))
        with patch("builtins.open", m):
            data = code_audit_agent.load_data()
        assert data == fake_data

    def test_load_data_file_not_found(self, code_audit_agent):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                code_audit_agent.load_data()
