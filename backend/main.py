"""
DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities
FastAPI backend entry point.

Required environment variables:
  GOOGLE_API_KEY  — Gemini API key (used by all specialist agents + Head Agent)
  OPENAI_API_KEY  — OpenAI API key (used by Finance Agent / GPT-4o-mini)

Optional:
  GITHUB_TOKEN    — GitHub personal access token (Code Audit + Infra agents)
  GITHUB_REPO     — Target repository in "owner/repo" format
  SLACK_BOT_TOKEN — Slack bot token (People Agent; gracefully skipped if absent)

Run with: uvicorn main:app --reload
"""
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from models import AgentReport

# Load .env if present (ANTHROPIC_API_KEY must be set in environment)
load_dotenv()

# ---------------------------------------------------------------------------
# Agent registry — populated during lifespan startup
# ---------------------------------------------------------------------------
agent_registry: dict[str, Any] = {}
head_agent_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager — runs startup logic before the first
    request and teardown logic after the last.

    On startup:
    - Instantiates all 6 specialist agents and the HeadAgent.
    - Populates the module-level ``agent_registry`` and ``head_agent_instance``
      globals used by every route handler.

    Agents are created once and reused across requests; each agent caches its
    last report in ``agent.last_report`` for cheap GET /report responses.
    """
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": list(agent_registry.keys()),
    }


# ---------------------------------------------------------------------------
# Slack integration status
# ---------------------------------------------------------------------------
@app.get("/api/slack/status", tags=["Integrations"])
async def slack_status():
    """Check whether the Slack API integration is connected and healthy."""
    from utils.slack_client import slack
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
async def _run_full_pipeline() -> dict:
    """Shared logic: run full LangGraph pipeline and merge RiskScore + dashboard."""
    from orchestrator import run_pipeline

    dashboard = await asyncio.to_thread(run_pipeline, agent_registry, head_agent_instance)

    # Merge RiskScore fields (briefing, severity_level, timestamp) into dashboard
    rs = head_agent_instance.last_risk_score
    if rs:
        dashboard["severityLevel"] = rs.severity_level
        dashboard["briefing"] = rs.briefing.model_dump()
        dashboard["timestamp"] = rs.timestamp.isoformat()

    return dashboard


@app.post("/api/head-agent/analyze", tags=["Head Agent"])
async def head_agent_analyze():
    """
    Run the full LangGraph pipeline (specialists → head agent → cascade expander × 3 → format)
    and return a merged response with RiskScore fields and frontend dashboard graph data.
    """
    if not head_agent_instance:
        raise HTTPException(status_code=503, detail="Head agent not initialized.")

    try:
        return await _run_full_pipeline()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



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
        try:
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
                        "data": json.dumps({"ts": datetime.now(timezone.utc).isoformat()}),
                    }
                except asyncio.CancelledError:
                    break
        finally:
            bus.unsubscribe(queue)

    return EventSourceResponse(event_generator())
