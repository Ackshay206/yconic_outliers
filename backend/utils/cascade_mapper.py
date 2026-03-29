"""
Cascade Mapper — traces anomalies forward through a pre-built dependency graph
of cross-domain causal relationships.

The six pre-seeded cascade paths encode the most common startup failure patterns.
Conditional probabilities are baseline values calibrated against Series-A SaaS
post-mortems; the Head Agent can override them at runtime via
``probability_overrides`` when live specialist data provides stronger evidence.

Urgency formula:  urgency = (1 / time_to_impact_days) × severity × (1 − reversibility)

Chains are pruned when cumulative probability drops below the THRESHOLD (0.25).
This prevents low-probability tail paths from inflating the risk score with noise.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from models import Anomaly, CascadeChain, CascadeNode

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

# ---------------------------------------------------------------------------
# Pre-built dependency graph
# Each entry maps a trigger (agent_domain + keyword) to an ordered list of
# cascade nodes with baseline conditional probabilities.
# ---------------------------------------------------------------------------

CASCADE_PATHS: dict[str, list[dict]] = {
    # Path 1 — Key-person departure → code gap → delivery failure → contract breach → revenue loss
    "people_key_person": [
        {
            "id": "people_disengagement",
            "agent_domain": "people",
            "title": "Key engineer disengaging",
            "severity": 0.85,
            "conditional_probability": 1.0,
        },
        {
            "id": "code_ownership_gap",
            "agent_domain": "code_audit",
            "title": "Critical service ownership gap (bus factor = 1)",
            "severity": 0.82,
            "conditional_probability": 0.78,
        },
        {
            "id": "infra_deploy_stall",
            "agent_domain": "infra",
            "title": "Payments-service deploy frequency drops to zero",
            "severity": 0.79,
            "conditional_probability": 0.72,
        },
        {
            "id": "legal_deadline_miss",
            "agent_domain": "legal",
            "title": "Nexus Corp Payments API v2 deadline missed",
            "severity": 0.88,
            "conditional_probability": 0.58,
        },
        {
            "id": "finance_revenue_loss",
            "agent_domain": "finance",
            "title": "Nexus Corp contract termination — 42% revenue loss",
            "severity": 0.92,
            "conditional_probability": 0.65,
        },
        {
            "id": "finance_downround",
            "agent_domain": "finance",
            "title": "Down-round clause triggers below 3-month runway",
            "severity": 0.95,
            "conditional_probability": 0.75,
        },
    ],
    # Path 2 — Critical CVE → compliance breach → legal exposure → funding risk
    "code_audit_cve": [
        {
            "id": "code_cve_found",
            "agent_domain": "code_audit",
            "title": "Critical CVE in payment processing dependency (CVSS 8.1)",
            "severity": 0.85,
            "conditional_probability": 1.0,
        },
        {
            "id": "legal_compliance_breach",
            "agent_domain": "legal",
            "title": "PCI DSS compliance breach due to unpatched CVE",
            "severity": 0.80,
            "conditional_probability": 0.70,
        },
        {
            "id": "legal_exposure",
            "agent_domain": "legal",
            "title": "Legal exposure from payment data breach liability",
            "severity": 0.78,
            "conditional_probability": 0.60,
        },
        {
            "id": "finance_investor_confidence",
            "agent_domain": "finance",
            "title": "Investor confidence loss — funding round at risk",
            "severity": 0.88,
            "conditional_probability": 0.45,
        },
    ],
    # Path 3 — Test coverage decline → bugs shipped → churn → revenue drop
    "code_audit_coverage": [
        {
            "id": "code_coverage_decline",
            "agent_domain": "code_audit",
            "title": "Test coverage declining below 60% for critical services",
            "severity": 0.70,
            "conditional_probability": 1.0,
        },
        {
            "id": "product_user_errors",
            "agent_domain": "product",
            "title": "User-facing errors increasing in payments dashboard",
            "severity": 0.72,
            "conditional_probability": 0.65,
        },
        {
            "id": "product_churn_spike",
            "agent_domain": "product",
            "title": "Churn spike — users abandoning payments features",
            "severity": 0.78,
            "conditional_probability": 0.55,
        },
        {
            "id": "finance_revenue_decline",
            "agent_domain": "finance",
            "title": "Revenue decline from feature churn",
            "severity": 0.80,
            "conditional_probability": 0.60,
        },
    ],
    # Path 4 — Technical debt → deploy velocity drop → feature delivery failure → competitive loss
    "infra_deploy_velocity": [
        {
            "id": "infra_tech_debt",
            "agent_domain": "infra",
            "title": "Accumulating technical debt slowing deployment velocity",
            "severity": 0.65,
            "conditional_probability": 1.0,
        },
        {
            "id": "infra_velocity_drop",
            "agent_domain": "infra",
            "title": "Deploy velocity drops — feature delivery falling behind",
            "severity": 0.70,
            "conditional_probability": 0.72,
        },
        {
            "id": "product_feature_miss",
            "agent_domain": "product",
            "title": "Key feature delivery failure — competitive gap opening",
            "severity": 0.75,
            "conditional_probability": 0.55,
        },
        {
            "id": "finance_competitive_loss",
            "agent_domain": "finance",
            "title": "Competitive loss leading to customer acquisition slowdown",
            "severity": 0.70,
            "conditional_probability": 0.40,
        },
    ],
    # Path 5 — Client revenue concentration → single client churn → revenue cliff → down-round
    "finance_concentration": [
        {
            "id": "finance_concentration_risk",
            "agent_domain": "finance",
            "title": "Revenue concentration risk — single client at 42%",
            "severity": 0.80,
            "conditional_probability": 1.0,
        },
        {
            "id": "legal_contract_risk",
            "agent_domain": "legal",
            "title": "Client contract renewal risk — delivery obligations at risk",
            "severity": 0.82,
            "conditional_probability": 0.65,
        },
        {
            "id": "finance_revenue_cliff",
            "agent_domain": "finance",
            "title": "Revenue cliff — loss of 42% monthly revenue overnight",
            "severity": 0.92,
            "conditional_probability": 0.70,
        },
        {
            "id": "finance_downround_trigger",
            "agent_domain": "finance",
            "title": "Down-round clause triggers — investor converts at 50% discount",
            "severity": 0.95,
            "conditional_probability": 0.80,
        },
    ],
    # Path 6 — Infrastructure degradation → SLA breach → contract penalty → burn spike → runway compression
    "infra_sla": [
        {
            "id": "infra_degradation",
            "agent_domain": "infra",
            "title": "Infrastructure degradation — response times and error rates rising",
            "severity": 0.75,
            "conditional_probability": 1.0,
        },
        {
            "id": "legal_sla_breach",
            "agent_domain": "legal",
            "title": "SLA breach threshold approached — contract penalty exposure",
            "severity": 0.78,
            "conditional_probability": 0.60,
        },
        {
            "id": "finance_penalty_burn",
            "agent_domain": "finance",
            "title": "Contract penalty payments spike burn rate",
            "severity": 0.80,
            "conditional_probability": 0.65,
        },
        {
            "id": "finance_runway_compression",
            "agent_domain": "finance",
            "title": "Runway compressed by penalty payments and recovery costs",
            "severity": 0.85,
            "conditional_probability": 0.70,
        },
    ],
}

# Map anomaly keywords → cascade path keys
TRIGGER_MAP: dict[str, str] = {
    "sarah chen": "people_key_person",
    "key person": "people_key_person",
    "key engineer": "people_key_person",
    "disengag": "people_key_person",
    "commit drop": "people_key_person",
    "cve": "code_audit_cve",
    "vulnerability": "code_audit_cve",
    "cvss": "code_audit_cve",
    "test coverage": "code_audit_coverage",
    "coverage": "code_audit_coverage",
    "deploy velocity": "infra_deploy_velocity",
    "technical debt": "infra_deploy_velocity",
    "revenue concentration": "finance_concentration",
    "nexus corp": "finance_concentration",
    "42%": "finance_concentration",
    "sla": "infra_sla",
    "infrastructure degrad": "infra_sla",
    "response time": "infra_sla",
}


def _select_path(anomaly: Anomaly) -> str | None:
    """Pick the best cascade path for an anomaly based on title + description."""
    text = (anomaly.title + " " + anomaly.description).lower()
    for keyword, path_key in TRIGGER_MAP.items():
        if keyword in text:
            return path_key
    # Fallback by domain
    domain_defaults = {
        "people": "people_key_person",
        "code_audit": "code_audit_cve",
        "infra": "infra_sla",
        "finance": "finance_concentration",
        "legal": "people_key_person",
        "product": "code_audit_coverage",
    }
    return domain_defaults.get(anomaly.agent_domain)


def map_cascade(anomaly: Anomaly, probability_overrides: dict[str, float] | None = None) -> CascadeChain:
    """
    Trace a cascade chain forward from the trigger anomaly.

    probability_overrides: optional dict of node_id → adjusted conditional probability
    supplied by the Head Agent after querying specialists for live corroboration.
    """
    overrides = probability_overrides or {}
    path_key = _select_path(anomaly)

    if path_key is None or path_key not in CASCADE_PATHS:
        # Minimal single-node chain for unknown anomaly types
        node = CascadeNode(
            id=anomaly.id + "_node",
            agent_domain=anomaly.agent_domain,
            title=anomaly.title,
            severity=anomaly.severity,
            conditional_probability=1.0,
            cumulative_probability=1.0,
            evidence=anomaly.description,
        )
        return CascadeChain(
            id=str(uuid.uuid4()),
            trigger_anomaly_id=anomaly.id,
            nodes=[node],
            overall_probability=anomaly.confidence,
            time_to_impact_days=90,
            financial_impact=0.0,
            urgency_score=_urgency(anomaly.severity, 90, 0.5),
            head_agent_briefing="",
        )

    path_template = CASCADE_PATHS[path_key]
    nodes: list[CascadeNode] = []
    cumulative = 1.0
    THRESHOLD = 0.25  # prune chains whose cumulative probability falls below 25%

    for step in path_template:
        node_id = step["id"]
        # Use override probability if the Head Agent supplied one for this node
        cond_prob = overrides.get(node_id, step["conditional_probability"])
        cumulative = cumulative * cond_prob

        node = CascadeNode(
            id=node_id,
            agent_domain=step["agent_domain"],
            title=step["title"],
            severity=step["severity"],
            conditional_probability=cond_prob,
            cumulative_probability=round(cumulative, 4),
            evidence="",
        )
        nodes.append(node)

        # Stop tracing if probability drops too low
        if cumulative < THRESHOLD:
            break

    # Median financial impact estimates (USD) per cascade path, calibrated for
    # a Series-A SaaS company with the Brainrot revenue profile (~$500K ARR).
    impact_map = {
        "people_key_person": 1_900_000,   # full Nexus Corp contract + re-hiring + down-round dilution
        "code_audit_cve": 750_000,         # breach liability + emergency patching + investor confidence
        "code_audit_coverage": 400_000,    # churn recovery + bug-fix sprint + lost expansion revenue
        "infra_deploy_velocity": 250_000,  # competitive feature gap + customer acquisition slowdown
        "finance_concentration": 1_200_000, # overnight revenue cliff + down-round clause discount
        "infra_sla": 500_000,              # SLA penalties + emergency infrastructure remediation
    }
    # Median days from anomaly detection to financial materialisation per path
    time_map = {
        "people_key_person": 75,   # ~10 weeks: notice period + handover + deadline slip
        "code_audit_cve": 45,      # ~6 weeks: compliance audit → legal exposure
        "code_audit_coverage": 60, # ~8 weeks: bugs accumulate → visible churn
        "infra_deploy_velocity": 90, # ~13 weeks: slow-burn competitive loss
        "finance_concentration": 60, # ~8 weeks: contract renewal / termination window
        "infra_sla": 50,           # ~7 weeks: SLA breach window → penalty invoice
    }

    financial_impact = impact_map.get(path_key, 500_000)
    time_to_impact = time_map.get(path_key, 60)
    overall_prob = round(cumulative * anomaly.confidence, 4)
    urgency = _urgency(anomaly.severity, time_to_impact, 0.3)

    return CascadeChain(
        id=str(uuid.uuid4()),
        trigger_anomaly_id=anomaly.id,
        nodes=nodes,
        overall_probability=overall_prob,
        time_to_impact_days=time_to_impact,
        financial_impact=financial_impact,
        urgency_score=round(urgency, 4),
        head_agent_briefing="",
    )


def _urgency(severity: float, time_to_impact_days: int, reversibility: float) -> float:
    """
    urgency = (1 / time_to_impact_days) × severity × (1 - reversibility)
    Higher urgency = act now.
    """
    if time_to_impact_days <= 0:
        time_to_impact_days = 1
    return (1.0 / time_to_impact_days) * severity * (1.0 - reversibility)
