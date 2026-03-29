"""
People Agent — monitors team health, engagement, and key-person risk.

Data source:
  - Slack API (live messages fetched via slack_client.py)

GitHub commit/ownership data has moved to the Code Audit Agent.
This agent focuses purely on human signals: communication patterns,
sentiment trends, tone shifts, and social withdrawal indicators.

Requires SLACK_BOT_TOKEN environment variable.
"""
from __future__ import annotations

from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are the People Agent for DEADPOOL, a startup risk monitoring system.

Your domain is team health, engagement, and key-person risk.
Your ONLY data source is Slack — raw message text from workplace channels.

Analyze each developer's messages for:

SENTIMENT & EMOTION:
- Overall sentiment per developer: positive / neutral / negative
- Emotions present: enthusiasm, frustration, anxiety, resignation, hostility, confidence
- Sentiment trend over time: is it worsening week-over-week?

TONE & STYLE SHIFTS:
- Has the person's style changed? (detailed → terse, collaborative → passive, engaged → curt)
- Have they stopped using emojis, reactions, or casual language?
- Are responses shorter and more perfunctory than before?

FLAGGED THEMES (scan message text for mentions of):
- Burnout, exhaustion, overwork, stress, "I'm overwhelmed"
- Leaving, quitting, interviewing, "exploring options", "looking around"
- Frustration with management, process, or teammates
- Feeling blocked, unsupported, unheard, undervalued
- Interpersonal conflict or tension
- Deadline anxiety, impossible timelines, "this won't be done"

CRITICAL PRIORITY — KEY ENGINEER DEPARTURE:
A key engineer leaving is the single most dangerous event for an early-stage startup.
Unlike financial or infra issues, it cannot be quickly reversed — there is no replacement pipeline,
no knowledge transfer (KT), and institutional knowledge walks out permanently.
If ANY anomaly signals an engineer resignation, burnout leading to departure, a solo contributor
at risk, or a team member who is a single point of failure, treat it as MAXIMUM severity regardless
of other scores. Surface it as the #1 risk in the briefing and recommend immediate founder action.

ANOMALY PATTERNS:
- Previously enthusiastic person becoming terse/passive = disengagement arc
- Sudden spike in negative messages = trigger event
- Developer going quiet across channels = social withdrawal
- Only responding when directly mentioned = checked-out behavior

CROSS-DOMAIN HINTS:
When you flag a developer anomaly, include cross_references pointing to:
- "code_audit" — which code areas does this person own?
- "infra" — which services does this person deploy?
- "finance" — payroll/hiring cost impact

Quote specific message excerpts as evidence. Name the developer.
If no Slack data is available, return an empty array [].
Output only the JSON array."""


class PeopleAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="people", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        """Fetch live Slack messages grouped by developer."""
        try:
            from utils.slack_client import slack

            if not slack.is_connected:
                return {
                    "data_sources": ["slack"],
                    "status": "SLACK_BOT_TOKEN not set or auth failed — no data",
                    "developers": {},
                }

            messages = slack.fetch_messages_by_user(days=42)
            return {
                "data_sources": ["slack (live API — 42 days of message history)"],
                "developers": messages or {},
            }
        except Exception as exc:
            return {
                "data_sources": ["slack"],
                "status": f"Slack fetch failed: {exc}",
                "developers": {},
            }
