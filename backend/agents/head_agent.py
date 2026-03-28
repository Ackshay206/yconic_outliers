"""
Head Agent — orchestrates all specialist agents, cross-validates anomalies,
maps cascades, and generates plain-language founder briefings.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime

import anthropic

from models import Anomaly, AgentReport, CascadeChain, RiskScore, WhatIfScenario
from cascade_mapper import map_cascade, _urgency

# Requires ANTHROPIC_API_KEY environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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

When given a list of anomalies from multiple domains, you must:
- Identify which anomalies are corroborated across domains (raise severity)
- Identify conflicts and resolve them with explicit reasoning
- Produce a risk score from 0 to 100
- Name the top 3 most urgent cascades
- Write a briefing that names the risk, states the timeline, and recommends ONE specific action

Respond in valid JSON only."""


class HeadAgent:
    def __init__(self, specialist_agents: dict):
        """
        specialist_agents: dict mapping domain name → specialist agent instance
        e.g. {"people": PeopleAgent(), "finance": FinanceAgent(), ...}
        """
        self.specialists = specialist_agents
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.active_cascades: list[CascadeChain] = []
        self.last_risk_score: RiskScore | None = None

    # ------------------------------------------------------------------
    # Main orchestration cycle
    # ------------------------------------------------------------------

    def analyze(self, all_anomalies: list[Anomaly]) -> RiskScore:
        """
        Full analysis cycle:
        1. Cross-validate anomalies with corroborating specialists
        2. Map cascade chains
        3. Rank by urgency
        4. Generate founder briefing
        5. Return RiskScore
        """
        if not all_anomalies:
            return self._empty_risk_score()

        # Step 1: Cross-validate
        validated = self._cross_validate(all_anomalies)

        # Step 2: Map cascades (deduplicate by trigger anomaly)
        seen_triggers: set[str] = set()
        chains: list[CascadeChain] = []
        for anomaly in validated:
            if anomaly.id not in seen_triggers and anomaly.severity >= 0.5:
                chain = map_cascade(anomaly)
                chains.append(chain)
                seen_triggers.add(anomaly.id)

        # Step 3: Rank by urgency, keep top 3
        chains.sort(key=lambda c: c.urgency_score, reverse=True)
        top_cascades = chains[:3]

        # Step 4: Compute composite risk score (0-100)
        risk_score = self._compute_risk_score(validated, top_cascades)

        # Step 5: Generate briefing
        briefing = self._generate_briefing(validated, top_cascades, risk_score)

        # Attach briefing to each chain
        for chain in top_cascades:
            chain.head_agent_briefing = briefing

        self.active_cascades = chains
        result = RiskScore(
            score=risk_score,
            trend="increasing" if risk_score > 60 else "stable",
            top_cascades=top_cascades,
            briefing=briefing,
            timestamp=datetime.utcnow(),
        )
        self.last_risk_score = result
        return result

    # ------------------------------------------------------------------
    # What-If simulation
    # ------------------------------------------------------------------

    def simulate_whatif(self, scenario: WhatIfScenario) -> WhatIfScenario:
        """
        Re-run analysis with modified parameters for a what-if scenario.
        """
        # Collect current anomalies from specialist last reports
        base_anomalies: list[Anomaly] = []
        for agent in self.specialists.values():
            if agent.last_report:
                base_anomalies.extend(agent.last_report.anomalies)

        # Apply scenario modifiers to anomaly severities
        modified = list(base_anomalies)
        params = scenario.parameters

        if scenario.scenario_type == "engineer_leaves":
            for a in modified:
                if a.agent_domain == "people":
                    a.severity = min(1.0, a.severity * params.get("severity_multiplier", 1.5))
        elif scenario.scenario_type == "client_churns":
            for a in modified:
                if a.agent_domain == "finance" and "nexus" in a.description.lower():
                    a.severity = min(1.0, a.severity * params.get("severity_multiplier", 1.8))
        elif scenario.scenario_type == "cve_discovered":
            for a in modified:
                if a.agent_domain == "code_audit":
                    a.severity = min(1.0, a.severity * params.get("severity_multiplier", 1.4))
        elif scenario.scenario_type == "cloud_costs_double":
            for a in modified:
                if a.agent_domain == "infra":
                    a.severity = min(1.0, a.severity * params.get("severity_multiplier", 1.3))

        simulated_result = self.analyze(modified)

        # Build comparison briefing
        current_score = self.last_risk_score.score if self.last_risk_score else 0.0
        comparison = self._call_claude(
            f"Compare these two risk states and write a 2-sentence comparison:\n"
            f"CURRENT risk score: {current_score}\n"
            f"SIMULATED risk score ({scenario.scenario_type}): {simulated_result.score}\n"
            f"Current briefing: {self.last_risk_score.briefing if self.last_risk_score else 'N/A'}\n"
            f"Simulated briefing: {simulated_result.briefing}\n"
            "Respond with plain text only."
        )

        scenario.modified_cascades = simulated_result.top_cascades
        scenario.new_risk_score = simulated_result.score
        scenario.comparison_briefing = comparison
        return scenario

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cross_validate(self, anomalies: list[Anomaly]) -> list[Anomaly]:
        """
        For each anomaly, check if corroborating agents have flagged related issues.
        Raise severity for corroborated anomalies, reduce for isolated ones.
        """
        # Build a lookup of domain → anomaly titles for quick cross-reference
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
        Composite risk score 0–100 based on:
        - Top cascade urgency scores
        - Average anomaly severity
        - Number of high-severity anomalies
        """
        if not anomalies and not cascades:
            return 0.0

        cascade_score = sum(min(c.urgency_score * 500, 40) for c in cascades[:3])
        high_severity = [a for a in anomalies if a.severity >= 0.75]
        anomaly_score = min(len(high_severity) * 8, 40)
        avg_severity = sum(a.severity for a in anomalies) / len(anomalies) if anomalies else 0
        base_score = avg_severity * 20

        return min(100.0, round(cascade_score + anomaly_score + base_score, 1))

    def _generate_briefing(
        self,
        anomalies: list[Anomaly],
        cascades: list[CascadeChain],
        risk_score: float,
    ) -> str:
        """Ask Claude to generate a plain-language founder briefing."""
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
            "Write a 3-5 sentence plain-language briefing for the founder. "
            "Name the risk, state the timeline, and recommend ONE specific action. "
            "No jargon. No bullet points. Just clear prose."
        )

        return self._call_claude(prompt)

    def _call_claude(self, prompt: str) -> str:
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _empty_risk_score(self) -> RiskScore:
        return RiskScore(
            score=0.0,
            trend="stable",
            top_cascades=[],
            briefing="No anomalies detected. All systems operating within normal parameters.",
            timestamp=datetime.utcnow(),
        )
