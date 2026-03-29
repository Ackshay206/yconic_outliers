"""
DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities
FastAPI backend entry point.

Requires: ANTHROPIC_API_KEY environment variable
Run with: uvicorn main:app --reload
"""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from models import AgentReport, CascadeChain, RiskScore, WhatIfScenario

# Load .env if present (ANTHROPIC_API_KEY must be set in environment)
load_dotenv()

# ---------------------------------------------------------------------------
# Agent registry — populated during lifespan startup
# ---------------------------------------------------------------------------
agent_registry: dict[str, Any] = {}
head_agent_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all agents on startup."""
    global head_agent_instance

    # Import here to avoid circular imports at module load time
    from agents.people_agent import PeopleAgent
    from agents.finance_agent import FinanceAgent
    from agents.infra_agent import InfraAgent
    from agents.product_agent import ProductAgent
    from agents.legal_agent import LegalAgent
    from agents.code_audit_agent import CodeAuditAgent
    from agents.head_agent import HeadAgent

    specialists = {
        "people": PeopleAgent(),
        "finance": FinanceAgent(),
        "infra": InfraAgent(),
        "product": ProductAgent(),
        "legal": LegalAgent(),
        "code_audit": CodeAuditAgent(),
    }
    agent_registry.update(specialists)

    head_agent_instance = HeadAgent(specialist_agents=specialists)

    print("[DEADPOOL] All agents initialized. Ready.")
    yield
    print("[DEADPOOL] Shutting down.")


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="DEADPOOL",
    description="Dependency Evaluation And Downstream Prediction Of Operational Liabilities",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — open for hackathon demo (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": list(agent_registry.keys()),
    }


# ---------------------------------------------------------------------------
# Slack integration status
# ---------------------------------------------------------------------------
@app.get("/api/slack/status", tags=["Integrations"])
async def slack_status():
    """Check whether the Slack API integration is connected and healthy."""
    from slack_client import slack
    return slack.status()


# ---------------------------------------------------------------------------
# Individual agent run
# ---------------------------------------------------------------------------
VALID_AGENTS = {"people", "finance", "infra", "product", "legal", "code_audit"}


@app.get("/api/agents/{agent_name}/run", response_model=AgentReport, tags=["Agents"])
async def run_agent(agent_name: str):
    """Run a single specialist agent and return its anomaly report."""
    if agent_name not in VALID_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Valid: {sorted(VALID_AGENTS)}",
        )
    agent = agent_registry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized yet.")

    try:
        report = await asyncio.to_thread(agent.run)
        return report
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Run all specialist agents
# ---------------------------------------------------------------------------
@app.get("/api/agents/all/run", tags=["Agents"])
async def run_all_agents():
    """Run all 6 specialist agents concurrently and return their reports."""
    if not agent_registry:
        raise HTTPException(status_code=503, detail="Agents not initialized yet.")

    async def _run(name: str, agent):
        try:
            report = await asyncio.to_thread(agent.run)
            return name, report, None
        except Exception as exc:
            return name, None, str(exc)

    tasks = [_run(name, agent) for name, agent in agent_registry.items()]
    results = await asyncio.gather(*tasks)

    output = {}
    for name, report, error in results:
        if error:
            output[name] = {"error": error}
        else:
            output[name] = report.model_dump()

    return output


# ---------------------------------------------------------------------------
# Head Agent analysis
# ---------------------------------------------------------------------------
@app.post("/api/head-agent/analyze", response_model=RiskScore, tags=["Head Agent"])
async def head_agent_analyze():
    """
    Run all specialist agents, then have the Head Agent cross-validate
    anomalies, map cascade chains, and produce a founder briefing.
    """
    if not head_agent_instance:
        raise HTTPException(status_code=503, detail="Head agent not initialized.")

    # Collect anomalies from all specialists
    all_anomalies = []
    for agent in agent_registry.values():
        try:
            report = await asyncio.to_thread(agent.run)
            all_anomalies.extend(report.anomalies)
        except Exception as exc:
            print(f"[DEADPOOL] Agent {agent.domain} failed: {exc}")

    try:
        risk_score = await asyncio.to_thread(head_agent_instance.analyze, all_anomalies)
        return risk_score
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Risk score
# ---------------------------------------------------------------------------
@app.get("/api/risk-score", response_model=RiskScore, tags=["Risk"])
async def get_risk_score():
    """Return the most recent computed risk score with top 3 cascades."""
    if not head_agent_instance:
        raise HTTPException(status_code=503, detail="Head agent not initialized.")

    if head_agent_instance.last_risk_score:
        return head_agent_instance.last_risk_score

    # No cached score — trigger a fresh analysis
    return await head_agent_analyze()


# ---------------------------------------------------------------------------
# Active cascades
# ---------------------------------------------------------------------------
@app.get("/api/cascades", response_model=list[CascadeChain], tags=["Risk"])
async def get_cascades():
    """List all active cascade chains detected in the last analysis."""
    if not head_agent_instance:
        raise HTTPException(status_code=503, detail="Head agent not initialized.")
    return head_agent_instance.active_cascades


# ---------------------------------------------------------------------------
# Agent last report
# ---------------------------------------------------------------------------
@app.get("/api/agents/{agent_name}/report", response_model=AgentReport, tags=["Agents"])
async def get_agent_report(agent_name: str):
    """Return the most recent report for a specific agent."""
    if agent_name not in VALID_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found.",
        )
    agent = agent_registry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized.")

    if not agent.last_report:
        # Run the agent now to get a fresh report
        try:
            report = await asyncio.to_thread(agent.run)
            return report
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    return agent.last_report


# ---------------------------------------------------------------------------
# What-If simulation
# ---------------------------------------------------------------------------
@app.post("/api/whatif", response_model=WhatIfScenario, tags=["Simulation"])
async def whatif_simulation(scenario: WhatIfScenario):
    """
    Simulate a what-if scenario and return modified cascade chains
    with a new risk score and comparison briefing.

    Scenario types:
    - engineer_leaves
    - client_churns
    - cve_discovered
    - cloud_costs_double
    """
    if not head_agent_instance:
        raise HTTPException(status_code=503, detail="Head agent not initialized.")

    try:
        result = await asyncio.to_thread(head_agent_instance.simulate_whatif, scenario)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# SSE — real-time dashboard updates
# ---------------------------------------------------------------------------
@app.get("/api/sse/updates", tags=["Real-time"])
async def sse_updates():
    """
    Server-Sent Events endpoint. Streams real-time anomaly events and
    risk score updates to the dashboard.

    Event types:
    - anomaly: new anomaly detected by a specialist agent
    - risk_score: updated overall risk score
    - heartbeat: keep-alive ping every 15 seconds
    """
    from signal_bus import bus

    queue = bus.subscribe()

    async def event_generator():
        # Send current risk score on connect
        if head_agent_instance and head_agent_instance.last_risk_score:
            score_data = head_agent_instance.last_risk_score.model_dump()
            score_data["timestamp"] = score_data["timestamp"].isoformat()
            yield {
                "event": "risk_score",
                "data": json.dumps(score_data, default=str),
            }

        # Send recent anomalies from bus on connect
        for anomaly in bus.get_recent(10):
            payload = anomaly.model_dump()
            payload["timestamp"] = payload["timestamp"].isoformat()
            yield {
                "event": "anomaly",
                "data": json.dumps(payload, default=str),
            }

        # Stream new events
        while True:
            try:
                # Wait up to 15 seconds for a new event, then send heartbeat
                anomaly = await asyncio.wait_for(queue.get(), timeout=15.0)
                payload = anomaly.model_dump()
                payload["timestamp"] = payload["timestamp"].isoformat()
                yield {
                    "event": "anomaly",
                    "data": json.dumps(payload, default=str),
                }
            except asyncio.TimeoutError:
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({"ts": datetime.utcnow().isoformat()}),
                }
            except asyncio.CancelledError:
                break

        bus.unsubscribe(queue)

    return EventSourceResponse(event_generator())
