"""
Pydantic v2 models for DEADPOOL — the startup risk monitoring system.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Anomaly(BaseModel):
    id: str
    agent_domain: str  # people | finance | infra | product | legal | code_audit
    severity: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    title: str
    description: str
    affected_entities: list[str] = []
    evidence: dict[str, Any] = {}
    cross_references: list[str] = []  # domains that should corroborate this
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CascadeNode(BaseModel):
    id: str
    agent_domain: str
    title: str
    severity: float = Field(ge=0.0, le=1.0)
    conditional_probability: float = Field(ge=0.0, le=1.0)
    cumulative_probability: float = Field(ge=0.0, le=1.0)
    evidence: str = ""


class CascadeChain(BaseModel):
    id: str
    trigger_anomaly_id: str
    nodes: list[CascadeNode]
    overall_probability: float = Field(ge=0.0, le=1.0)
    time_to_impact_days: int
    financial_impact: float  # USD
    urgency_score: float
    head_agent_briefing: str | None = None  # deprecated — use RiskScore.briefing


class FounderBriefing(BaseModel):
    summary: str            # 2-3 sentences on the highest-priority risk
    timeline: str           # e.g. "50 days to financial impact"
    recommended_action: str # ONE specific action the founder should take now


class RiskScore(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    severity_level: Literal["low", "medium", "high", "critical"]
    trend: Literal["increasing", "stable", "decreasing"]
    top_cascades: list[CascadeChain]
    briefing: FounderBriefing
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentReport(BaseModel):
    agent: str
    anomalies: list[Anomaly]
    raw_data_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WhatIfScenario(BaseModel):
    scenario_type: str  # "engineer_leaves" | "client_churns" | "cve_discovered" | "cloud_costs_double"
    parameters: dict[str, Any] = {}
    modified_cascades: list[CascadeChain] = []
    new_risk_score: float | None = None
    comparison_briefing: str = ""
