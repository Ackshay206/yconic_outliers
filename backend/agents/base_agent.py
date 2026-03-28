"""
Base agent — shared foundation for all six DEADPOOL specialist agents.

Requires ANTHROPIC_API_KEY environment variable.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime

import anthropic

from models import Anomaly, AgentReport


class BaseAgent:
    """Abstract base class for specialist agents."""

    def __init__(self, domain: str, system_prompt: str):
        self.domain = domain
        self.system_prompt = system_prompt
        # Requires ANTHROPIC_API_KEY to be set in the environment
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.last_report: AgentReport | None = None

    # ------------------------------------------------------------------
    # Subclasses must override this
    # ------------------------------------------------------------------

    def load_data(self) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__} must implement load_data()")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> AgentReport:
        """
        Main entry point: load domain data, call Claude, parse anomalies,
        publish to the signal bus, and return an AgentReport.
        """
        data = self.load_data()
        data_json = json.dumps(data, indent=2)

        user_message = (
            f"Analyze the following {self.domain} data and return a JSON array of anomalies.\n\n"
            f"```json\n{data_json}\n```\n\n"
            "Return ONLY a valid JSON array. Each element must match this schema:\n"
            "{\n"
            '  "id": "<unique string>",\n'
            '  "agent_domain": "<domain>",\n'
            '  "severity": <0.0-1.0>,\n'
            '  "confidence": <0.0-1.0>,\n'
            '  "title": "<short title>",\n'
            '  "description": "<1-2 sentence description>",\n'
            '  "affected_entities": ["<name>", ...],\n'
            '  "evidence": {"key": "value"},\n'
            '  "cross_references": ["<domain>", ...]\n'
            "}\n"
            "Return an empty array [] if no anomalies are detected."
        )

        raw_response = self._call_claude(user_message)
        anomalies = self._parse_anomalies(raw_response)

        summary = self._summarize_data(data)
        report = AgentReport(
            agent=self.domain,
            anomalies=anomalies,
            raw_data_summary=summary,
            timestamp=datetime.utcnow(),
        )
        self.last_report = report

        # Publish to signal bus
        from signal_bus import bus
        for anomaly in anomalies:
            bus.publish(anomaly)

        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_claude(self, user_message: str) -> str:
        """Send user_message to Claude with the agent's system prompt and return the text."""
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text

    def _parse_anomalies(self, raw: str) -> list[Anomaly]:
        """
        Extract a JSON array from Claude's response and deserialize into Anomaly objects.
        Handles markdown code fences and extraneous text.
        """
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()

        # Find the first [ ... ] block
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            return []

        array_str = text[start : end + 1]
        try:
            raw_list = json.loads(array_str)
        except json.JSONDecodeError:
            return []

        anomalies: list[Anomaly] = []
        for item in raw_list:
            # Guarantee an id and agent_domain
            if "id" not in item or not item["id"]:
                item["id"] = f"{self.domain}_{uuid.uuid4().hex[:8]}"
            item["agent_domain"] = self.domain
            try:
                anomalies.append(Anomaly(**item))
            except Exception:
                pass

        return anomalies

    def _summarize_data(self, data: dict) -> str:
        """Produce a one-line summary of the raw data for the AgentReport."""
        keys = list(data.keys())
        total_items = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
        return f"{self.domain} data loaded — top-level keys: {keys}, ~{total_items} data points"
