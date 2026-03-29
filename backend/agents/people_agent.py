"""
People Agent — monitors team health, engagement, and key-person risk.

Data sources:
  - team_activity.json (GitHub activity: commits, PRs, code ownership)
  - Slack API (raw message text — sentiment/emotion analyzed by Claude in this agent)

When SLACK_BOT_TOKEN is set, live Slack messages are fetched and included.
Claude analyzes both GitHub metrics AND Slack message content in a single call,
extracting sentiment, emotions, tone shifts, and anomaly patterns.
"""
from __future__ import annotations

import json
import os

from agents.base_agent import BaseAgent

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/team_activity.json")

SYSTEM_PROMPT = """You are the People Agent for DEADPOOL, a startup risk monitoring system.

Your domain is team health, engagement, and key-person risk.

You analyze TWO data streams for each developer:

1. **GitHub activity** — commits, PRs opened, PRs reviewed, code review comments, response times
2. **Slack messages** — raw message text from workplace Slack channels (when available)

--- GITHUB SIGNALS ---

- Commit activity dropping >50% week-over-week for any developer
- A developer going quiet for >2 weeks (especially in critical code areas)
- Bus factor risks: a single developer owns >60% of commits in a critical service
- PR review bottlenecks: PRs going unreviewed for >5 days
- Workload imbalance: one developer doing >3x the work of peers

--- SLACK MESSAGE ANALYSIS ---

When Slack messages are provided, READ THE ACTUAL TEXT and analyze for:

Sentiment & Emotion:
- What is the overall sentiment? (positive, neutral, negative)
- What emotions are present? (enthusiasm, frustration, anxiety, resignation, hostility, confidence)
- Is there a sentiment TREND over time? (e.g. messages becoming progressively more negative)

Tone & Style Shifts:
- Has the person's communication style changed? (detailed → terse, collaborative → passive)
- Are they writing shorter, more curt messages over time?
- Have they stopped using emojis, reactions, or casual language?

Flagged Themes (look for mentions of):
- Burnout, exhaustion, overwork, stress
- Leaving, quitting, interviewing, "exploring options"
- Frustration with management, process, teammates
- Feeling blocked, unsupported, unheard
- Interpersonal conflict, disagreements
- Deadline anxiety, impossible timelines

Anomaly Patterns:
- Previously enthusiastic person becoming terse/passive = disengagement arc
- Sudden spike in negative messages after stable period = trigger event
- Dropping out of channels = social withdrawal
- Only responding when directly asked = checked-out behavior

--- CROSS-DOMAIN CORRELATION ---

- GitHub commits drop + Slack messages negative/frustrated → burnout or departure imminent (CRITICAL)
- GitHub commits drop + Slack messages positive → possible reassignment or blocker (MODERATE)
- GitHub stable + Slack messages negative → interpersonal conflict or isolation (HIGH)
- GitHub AND Slack BOTH declining → strongest departure signal (CRITICAL)

When you detect an anomaly, cross-reference with:
- code_audit: which code areas does this person own?
- infra: which services does this person deploy?
- finance: what is the payroll and hiring pipeline impact?

Be precise. Name the developer. Cite specific numbers AND quote specific message excerpts
that reveal sentiment/emotion patterns. Output only the JSON array."""


class PeopleAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="people", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        with open(DATA_PATH, "r") as f:
            base_data = json.load(f)

        slack_data = self._fetch_slack_messages(base_data)
        if slack_data:
            base_data["slack_messages"] = slack_data
            base_data["data_sources"] = [
                "github (team_activity.json)",
                "slack (live API — raw message text for sentiment analysis)",
            ]
        else:
            base_data["data_sources"] = [
                "github (team_activity.json)",
                "slack (not connected — SLACK_BOT_TOKEN not set)",
            ]

        return base_data

    def _fetch_slack_messages(self, base_data: dict) -> dict | None:
        """Try to pull raw Slack messages. Returns None if unavailable."""
        try:
            from slack_client import slack

            if not slack.is_connected:
                return None

            email_map = self._build_email_map(base_data)
            return slack.fetch_messages_by_user(days=42, user_email_map=email_map)
        except Exception:
            return None

    @staticmethod
    def _build_email_map(base_data: dict) -> dict[str, str]:
        """Build {email: developer_name} from team_activity.json if emails are present."""
        mapping: dict[str, str] = {}
        for dev in base_data.get("developers", []):
            email = dev.get("email")
            if email:
                mapping[email] = dev["name"]
        return mapping
