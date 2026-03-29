"""
Shared pytest fixtures and path setup for all agent tests.
"""
import sys
import os

# Ensure the backend directory is on the path so imports work the same
# way they do when the app runs from the backend/ directory.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Minimal valid anomaly dict that satisfies the Anomaly Pydantic schema
# ---------------------------------------------------------------------------
VALID_ANOMALY = {
    "id": "test_001",
    "agent_domain": "people",
    "severity": 0.8,
    "confidence": 0.9,
    "title": "Test anomaly",
    "description": "A test anomaly for unit testing.",
    "affected_entities": ["Alice"],
    "evidence": {"commits_this_week": 0},
    "cross_references": ["code_audit"],
}


def make_claude_response(anomalies_json: str) -> MagicMock:
    """Return a mock that looks like an anthropic Messages response."""
    content_block = MagicMock()
    content_block.text = anomalies_json
    response = MagicMock()
    response.content = [content_block]
    return response


@pytest.fixture
def mock_signal_bus():
    """Patch the signal bus so publish() is a no-op during tests."""
    with patch("agents.base_agent.bus") as mock_bus:
        mock_bus.publish = MagicMock()
        yield mock_bus


@pytest.fixture
def mock_anthropic_client():
    """
    Patch anthropic.Anthropic so no real API calls are made.
    Returns the mock client instance; tests set mock_client.messages.create.return_value
    to control what Claude 'returns'.
    """
    with patch("anthropic.Anthropic") as MockClass:
        mock_instance = MagicMock()
        MockClass.return_value = mock_instance
        yield mock_instance
