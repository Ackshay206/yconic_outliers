"""
Head Agent — orchestrates all specialist agents, cross-validates anomalies,
maps cascades, and generates plain-language founder briefings.

Model: Gemini 2.5 Pro (Google) — largest context window for cross-domain synthesis.
Requires GOOGLE_API_KEY environment variable.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

import google.genai as genai
from google.genai import types as genai_types

from models import Anomaly, AgentReport, CascadeChain, FounderBriefing, RiskScore

MODEL = "gemini-2.5-pro"

# Which domains should corroborate a given trigger domain
CORROBORATION_MAP: dict[str, list[str]] = {
    "people": ["code_audit", "infra"],
    "code_audit": ["legal", "infra"],
    "finance": ["legal"],
    "infra": ["code_audit", "people"],
    "product": ["infra", "code_audit"],
    "legal": ["infra", "finance"],
}

SYSTEM_PROMPT = """You are the Head Agent for DEADPOOL — a startup risk monitoring system.

Your role is to:
1. Cross-validate anomalies from specialist agents
2. Trace cascade chains through cross-domain dependencies
3. Rank cascades by urgency: urgency = (1 / time_to_impact_days) × severity × (1 - reversibility)
4. Generate plain-language founder briefings (3-5 sentences, no jargon)

CRITICAL PRIORITY — KEY ENGINEER DEPARTURE:
A key engineer leaving is the single most dangerous event for an early-stage startup.
Unlike financial or infra issues, it cannot be quickly reversed — there is no replacement pipeline,
no knowledge transfer (KT), and institutional knowledge walks out permanently.
If ANY anomaly signals an engineer resignation, burnout leading to departure, treat it as MAXIMUM severity regardless
of other scores. Surface it as the #1 risk in the briefing and recommend immediate founder action.


When given a list of anomalies from multiple domains, you must:
- Identify which anomalies are corroborated across domains (raise severity)
- Identify conflicts and resolve them with explicit reasoning
- Produce a risk score from 0 to 100
- Name the top 3 most urgent cascades
- Write a briefing that names the risk, states the timeline, and recommends ONE specific action

Respond in valid JSON only when asked for JSON."""

BRIEFING_SYSTEM_PROMPT = """You are the Head Agent for DEADPOOL — a startup risk monitoring system.
Your job is to write clear, plain-language briefings for startup founders.
Be direct. Name the risk, state the timeline, and recommend ONE specific action.
No jargon. No bullet points. No JSON. Just clear prose."""


class HeadAgent:
    """
    Orchestrating agent that synthesises all specialist findings into a single risk picture.

    Responsibilities:
    1. Cross-validate anomalies using the domain corroboration map — boost
       severity for signals that appear across multiple domains, dampen noise
       for unconfirmed low-severity signals.
    2. Map each validated anomaly (severity ≥ 0.5) to a cascade chain via the
       deterministic CascadeMapper.
    3. Compute a 0–100 risk score from cascade urgency, anomaly count, and
       average severity.
    4. Call Gemini 2.5 Pro to generate a structured ``FounderBriefing``.
    5. Cache the last ``RiskScore`` for GET /api/risk-score and What-If simulations.
    """

    def __init__(self, specialist_agents: dict) -> None:
        """
        Args:
            specialist_agents: Mapping of domain name → initialised specialist
                agent instance (people, finance, infra, product, legal, code_audit).
        """
        self.specialists = specialist_agents
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.active_cascades: list[CascadeChain] = []
        self.last_risk_score: RiskScore | None = None

    # ------------------------------------------------------------------
    # Main orchestration cycle
    # ------------------------------------------------------------------

    def analyze(self, all_anomalies: list[Anomaly]) -> RiskScore:
        """
        Run a full analysis cycle over the given anomaly list.

        Steps: cross-validate → map cascades → compute score → generate briefing.
        The result is cached in ``self.last_risk_score`` for subsequent GET requests
        and What-If simulations.

        Args:
            all_anomalies: Flat list of anomalies collected from all specialist agents.

        Returns:
            A fully populated ``RiskScore`` with severity_level, trend, top 3 cascade
            chains, and a structured ``FounderBriefing``.
        """
        if not all_anomalies:
            return self._empty_risk_score()

        validated = self._cross_validate(all_anomalies)

        # Cascade expansion is now handled by the orchestrator's cascade_expander node.
        # analyze() only computes the risk score and briefing from anomalies.
        top_cascades: list[CascadeChain] = []

        risk_score = self._compute_risk_score(validated, top_cascades)
        briefing = self._generate_briefing(validated, top_cascades, risk_score)

        self.active_cascades = top_cascades
        result = RiskScore(
            score=risk_score,
            severity_level=self._score_to_severity(risk_score),
            trend="increasing" if risk_score > 60 else "stable",
            top_cascades=top_cascades,
            briefing=briefing,
            timestamp=datetime.now(timezone.utc),
        )
        self.last_risk_score = result
        return result


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cross_validate(self, anomalies: list[Anomaly]) -> list[Anomaly]:
        """
        Adjust anomaly severities based on cross-domain corroboration.

        For each anomaly, checks how many of its expected corroborating domains
        (from CORROBORATION_MAP) also have active signals in this cycle:
        - 2+ corroborating domains present → severity +15%, confidence +10%
          (multi-domain agreement is strong evidence the risk is real)
        - 0 corroborating domains AND severity < 0.5 → severity −15%
          (unconfirmed weak signal — dampen noise without discarding it)
        - 1 corroborating domain → no adjustment (ambiguous evidence)

        Args:
            anomalies: Raw anomaly list from all specialist agents.

        Returns:
            The same anomaly objects with adjusted severity/confidence values.
        """
        domain_signals: dict[str, list[str]] = {}
        for a in anomalies:
            domain_signals.setdefault(a.agent_domain, []).append(a.title.lower())

        validated: list[Anomaly] = []
        for anomaly in anomalies:
            corroborating_domains = CORROBORATION_MAP.get(anomaly.agent_domain, [])
            corroboration_count = sum(
                1 for d in corroborating_domains if d in domain_signals
            )

            if corroboration_count >= 2:
                anomaly.severity = min(1.0, anomaly.severity * 1.15)
                anomaly.confidence = min(1.0, anomaly.confidence * 1.10)
            elif corroboration_count == 0 and anomaly.severity < 0.5:
                anomaly.severity = anomaly.severity * 0.85

            validated.append(anomaly)

        return validated

    def _compute_risk_score(self, anomalies: list[Anomaly], cascades: list[CascadeChain]) -> float:
        """
        Compute a 0–100 composite risk score from three additive components.

        Each component is independently capped so no single dimension can
        dominate the total:

        | Component            | Formula                              | Cap    |
        |----------------------|--------------------------------------|--------|
        | Cascade urgency      | Σ min(urgency × 500, 40) for top 3   | 40 pts |
        | High-severity count  | count(severity ≥ 0.75) × 8           | 40 pts |
        | Baseline severity    | avg(all severities) × 20              | 20 pts |

        Maximum possible score = 100.
        """
        if not anomalies and not cascades:
            return 0.0

        # Cascade component: urgency × 500 scales the small float into a meaningful
        # point contribution; capped at 40 so cascades alone can't max the score.
        cascade_score = sum(min(c.urgency_score * 500, 40) for c in cascades[:3])

        # Anomaly component: 8 pts per high-severity signal, capped at 40 pts (5 signals)
        high_severity = [a for a in anomalies if a.severity >= 0.75]
        anomaly_score = min(len(high_severity) * 8, 40)

        # Baseline component: average severity across all anomalies, max 20 pts
        avg_severity = sum(a.severity for a in anomalies) / len(anomalies) if anomalies else 0
        base_score = avg_severity * 20

        return min(100.0, round(cascade_score + anomaly_score + base_score, 1))

    def _generate_briefing(
        self,
        anomalies: list[Anomaly],
        cascades: list[CascadeChain],
        risk_score: float,
    ) -> FounderBriefing:
        anomaly_summaries = [
            f"[{a.agent_domain.upper()}] {a.title} (severity={a.severity:.2f})"
            for a in sorted(anomalies, key=lambda x: x.severity, reverse=True)[:10]
        ]
        cascade_summaries = [
            f"Cascade {i+1}: {c.nodes[0].title if c.nodes else 'Unknown'} → ... "
            f"(probability={c.overall_probability:.0%}, "
            f"impact=${c.financial_impact:,.0f}, "
            f"days={c.time_to_impact_days})"
            for i, c in enumerate(cascades[:3])
        ]

        prompt = (
            f"Risk score: {risk_score:.0f}/100\n\n"
            f"Top anomalies:\n" + "\n".join(anomaly_summaries) + "\n\n"
            f"Top cascade chains:\n" + "\n".join(cascade_summaries) + "\n\n"
            "Respond with valid JSON only, using exactly this structure:\n"
            '{"summary": "2-3 sentences describing the top risk and its cause", '
            '"timeline": "specific timeframe e.g. 50 days to financial impact", '
            '"recommended_action": "ONE specific action the founder should take today"}'
        )

        raw = self._call_gemini(prompt, system_prompt=SYSTEM_PROMPT)
        try:
            # Strip markdown code fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            data = json.loads(clean.strip())
            return FounderBriefing(**data)
        except Exception as e:
            logger.warning("Failed to parse briefing JSON (%s), using fallback.", e)
            # Best-effort: return raw text as summary
            return FounderBriefing(
                summary=raw[:500] if raw else "Analysis complete.",
                timeline=f"{cascades[0].time_to_impact_days} days to impact" if cascades else "See cascade chains.",
                recommended_action="Review the top cascade chains above and address the highest urgency item.",
            )

    def _score_to_severity(self, score: float) -> str:
        """
        Map a 0–100 risk score to a human-readable severity level.

        Thresholds: critical ≥ 75 · high ≥ 50 · medium ≥ 25 · low < 25
        """
        if score >= 75:
            return "critical"
        if score >= 50:
            return "high"
        if score >= 25:
            return "medium"
        return "low"

    def _call_gemini(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """
        Call Gemini 2.5 Pro with up to 3 retry attempts.

        Uses a ``thinking_budget`` of 1024 tokens — enough for the model to
        reason internally without exhausting the 8192-token output budget before
        generating the actual response text (a known failure mode for thinking
        models with very low ``max_output_tokens``).

        Returns an empty fallback string after 3 consecutive failures rather than
        raising, so the caller can decide how to handle degraded output.
        """
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=8192,
                        thinking_config=genai_types.ThinkingConfig(
                            thinking_budget=1024,
                        ),
                    ),
                )
                if response.text:
                    return response.text
                logger.warning("Gemini returned empty (attempt %d/3, finish_reason=%s)", attempt + 1, response.candidates[0].finish_reason if response.candidates else "N/A")
            except Exception as e:
                logger.warning("Gemini call failed (attempt %d/3): %s", attempt + 1, e)
            import time
            time.sleep(2)
        return "Unable to generate briefing at this time."

    def _empty_risk_score(self) -> RiskScore:
        """Return a zeroed-out RiskScore for the case where no anomalies were detected."""
        return RiskScore(
            score=0.0,
            severity_level="low",
            trend="stable",
            top_cascades=[],
            briefing=FounderBriefing(
                summary="No anomalies detected. All systems operating within normal parameters.",
                timeline="No imminent risks identified.",
                recommended_action="Continue monitoring. No action required at this time.",
            ),
            timestamp=datetime.now(timezone.utc),
        )
