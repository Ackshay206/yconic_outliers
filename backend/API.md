# DEADPOOL API Documentation

Base URL: `http://localhost:8000`
Interactive docs (Swagger): `http://localhost:8000/docs`

---

## Authentication

No authentication required. CORS is open for all origins.

---

## Endpoints

### System

#### `GET /health`

Returns service health and list of initialized agents.

**Response**
```json
{
  "status": "ok",
  "timestamp": "2026-03-29T12:00:00+00:00",
  "agents": ["people", "finance", "infra", "product", "legal", "code_audit"]
}
```

---

### Agents

#### `GET /api/agents/{agent_name}/run`

Run a single specialist agent and return its anomaly report.

**Path parameters**

| Parameter    | Type   | Description                                                                      |
|-------------|--------|----------------------------------------------------------------------------------|
| `agent_name` | string | One of: `people`, `finance`, `infra`, `product`, `legal`, `code_audit`          |

**Response** — `AgentReport`
```json
{
  "agent": "people",
  "anomalies": [
    {
      "id": "people_a1b2c3d4",
      "agent_domain": "people",
      "severity": 0.85,
      "confidence": 0.9,
      "title": "Key engineer commit drop",
      "description": "Sarah Chen's weekly commits dropped 94% over 5 weeks.",
      "affected_entities": ["sarah_chen", "payments-service"],
      "evidence": { "commits_last_week": 1, "average": 18 },
      "cross_references": ["code_audit", "infra"],
      "timestamp": "2026-03-29T12:00:00"
    }
  ],
  "raw_data_summary": "Loaded: slack_data.json, commit_history.json",
  "timestamp": "2026-03-29T12:00:00"
}
```

**Error responses**

| Status | Condition |
|--------|-----------|
| 404    | `agent_name` not in valid set |
| 503    | Agent not yet initialized |
| 500    | Agent execution failed |

---

#### `GET /api/agents/all/run`

Run all 6 specialist agents concurrently and return a map of their reports.

**Response**
```json
{
  "people": { "agent": "people", "anomalies": [...], "raw_data_summary": "...", "timestamp": "..." },
  "finance": { "agent": "finance", "anomalies": [...], "raw_data_summary": "...", "timestamp": "..." },
  "infra": { ... },
  "product": { ... },
  "legal": { ... },
  "code_audit": { ... }
}
```

On per-agent failure:
```json
{
  "people": { "error": "..." }
}
```

**Error responses**

| Status | Condition |
|--------|-----------|
| 503    | Agent registry not yet initialized |

---

#### `GET /api/agents/{agent_name}/report`

Return the cached report from the last run of a specific agent. If no report is cached, runs the agent first.

**Path parameters**

| Parameter    | Type   | Description                                                             |
|-------------|--------|-------------------------------------------------------------------------|
| `agent_name` | string | One of: `people`, `finance`, `infra`, `product`, `legal`, `code_audit` |

**Response** — same shape as `AgentReport` above.

**Error responses**

| Status | Condition |
|--------|-----------|
| 404    | `agent_name` not in valid set |
| 503    | Agent not initialized |
| 500    | Agent execution failed (only if no cache and fresh run fails) |

---

### Head Agent

#### `POST /api/head-agent/analyze`

Run the full LangGraph pipeline:

1. All 6 specialist agents run in parallel
2. Head Agent cross-validates anomalies, computes risk score (0–100), generates `FounderBriefing`
3. Cascade expander traces multi-domain failure chains (up to depth 5)
4. Response is assembled with graph nodes/edges for the React Flow dashboard

This is the primary endpoint. The frontend calls this after opening the SSE stream.

**Request body** — none

**Response**
```json
{
  "riskScore": 78,
  "trend": "increasing",
  "activeCascades": 2,
  "nodes": [
    {
      "id": "node_abc123",
      "agent_domain": "people",
      "title": "Key engineer disengagement",
      "severity": 0.85,
      "conditional_probability": 1.0,
      "cumulative_probability": 1.0,
      "evidence": "Commit velocity dropped 94%"
    }
  ],
  "edges": [
    { "source": "node_abc123", "target": "node_def456" }
  ],
  "activeChains": [
    {
      "id": "chain_001",
      "trigger_anomaly_id": "people_a1b2c3d4",
      "nodes": [...],
      "overall_probability": 0.72,
      "time_to_impact_days": 50,
      "financial_impact": 1200000,
      "urgency_score": 0.91
    }
  ],
  "severityLevel": "high",
  "briefing": {
    "summary": "Sarah Chen's disengagement creates a critical ownership gap in payments-service...",
    "timeline": "50 days to financial impact",
    "recommended_action": "Schedule a 1-on-1 with Sarah Chen this week to surface blockers."
  },
  "timestamp": "2026-03-29T12:00:00+00:00"
}
```

**Error responses**

| Status | Condition |
|--------|-----------|
| 503    | Head agent not initialized |
| 500    | Pipeline execution failed |

---

### Risk

#### `GET /api/dashboard`

Alias for `POST /api/head-agent/analyze`. Returns identical response. Provided for convenience.

---

#### `GET /api/risk-score`

Return the most recently cached `RiskScore`. If no analysis has been run yet, triggers a fresh pipeline run first.

**Response** — `RiskScore`
```json
{
  "score": 78.0,
  "severity_level": "high",
  "trend": "increasing",
  "top_cascades": [...],
  "briefing": {
    "summary": "...",
    "timeline": "50 days to financial impact",
    "recommended_action": "..."
  },
  "timestamp": "2026-03-29T12:00:00"
}
```

**`severity_level` values**

| Value      | Score range |
|------------|-------------|
| `low`      | 0 – 24      |
| `medium`   | 25 – 49     |
| `high`     | 50 – 74     |
| `critical` | 75 – 100    |

**Error responses**

| Status | Condition |
|--------|-----------|
| 503    | Head agent not initialized |

---

#### `GET /api/cascades`

List all active cascade chains from the last analysis.

**Response** — `CascadeChain[]`
```json
[
  {
    "id": "chain_001",
    "trigger_anomaly_id": "people_a1b2c3d4",
    "nodes": [
      {
        "id": "node_abc123",
        "agent_domain": "people",
        "title": "Key engineer disengagement",
        "severity": 0.85,
        "conditional_probability": 1.0,
        "cumulative_probability": 1.0,
        "evidence": "Commit velocity dropped 94%"
      }
    ],
    "overall_probability": 0.72,
    "time_to_impact_days": 50,
    "financial_impact": 1200000.0,
    "urgency_score": 0.91,
    "head_agent_briefing": null
  }
]
```

**Error responses**

| Status | Condition |
|--------|-----------|
| 503    | Head agent not initialized |

---

### Simulation

#### `POST /api/whatif`

Simulate a what-if scenario by boosting relevant anomaly severities, re-running the cascade pipeline, and returning a comparison briefing.

**Request body** — `WhatIfScenario`
```json
{
  "scenario_type": "engineer_leaves",
  "parameters": {
    "severity_multiplier": 1.5
  }
}
```

**`scenario_type` values**

| Value               | Domain affected | Description                                     |
|--------------------|-----------------|--------------------------------------------------|
| `engineer_leaves`   | `people`        | Boosts severity of People domain anomalies       |
| `client_churns`     | `finance`       | Boosts Finance anomalies referencing Nexus Corp  |
| `cve_discovered`    | `code_audit`    | Boosts Code Audit domain anomalies               |
| `cloud_costs_double`| `infra`         | Boosts Infra domain anomalies                    |

**Response** — `WhatIfScenario` (input fields + populated output fields)
```json
{
  "scenario_type": "engineer_leaves",
  "parameters": { "severity_multiplier": 1.5 },
  "modified_cascades": [...],
  "new_risk_score": 91.0,
  "comparison_briefing": "Under this scenario, risk rises from 78 to 91..."
}
```

**Error responses**

| Status | Condition |
|--------|-----------|
| 503    | Head agent not initialized |
| 500    | Simulation failed |

---

### Real-time

#### `GET /api/sse/updates`

Server-Sent Events stream. The frontend opens this connection before triggering analysis to receive anomaly events incrementally as agents complete.

**Response** — `text/event-stream`

On connect, the server immediately sends:
1. The current `risk_score` (if a prior analysis exists)
2. The 10 most recent `anomaly` events from the in-memory ring buffer

Then streams new events as they arrive.

**Event types**

| Event       | Payload | Description |
|-------------|---------|-------------|
| `anomaly`   | `Anomaly` (JSON) | New risk signal detected by a specialist agent |
| `risk_score`| `RiskScore` (JSON) | Sent once on connect with the last cached score |
| `heartbeat` | `{ "ts": "<iso>" }` | Keep-alive ping every 15 seconds |

**Example stream**
```
event: risk_score
data: {"score": 78.0, "severity_level": "high", ...}

event: anomaly
data: {"id": "people_a1b2c3d4", "agent_domain": "people", "severity": 0.85, ...}

event: heartbeat
data: {"ts": "2026-03-29T12:00:15+00:00"}
```

---

### Integrations

#### `GET /api/slack/status`

Check whether the Slack API integration is connected and authenticated.

**Response**
```json
{ "connected": true, "workspace": "acme-corp" }
```
or
```json
{ "connected": false, "reason": "SLACK_BOT_TOKEN not set" }
```

---

## Data Models

### `Anomaly`

| Field               | Type              | Description                                                  |
|--------------------|-------------------|--------------------------------------------------------------|
| `id`               | string            | Unique identifier, e.g. `people_a1b2c3d4`                   |
| `agent_domain`     | string            | Source domain: `people` \| `finance` \| `infra` \| `product` \| `legal` \| `code_audit` |
| `severity`         | float [0–1]       | How severe the risk is if it materialises                    |
| `confidence`       | float [0–1]       | How certain the agent is the signal is real                  |
| `title`            | string            | Short label for the anomaly                                  |
| `description`      | string            | Full explanation of the detected signal                      |
| `affected_entities`| string[]          | Named entities involved (people, services, clients)          |
| `evidence`         | object            | Raw data points supporting the signal                        |
| `cross_references` | string[]          | Domains that should corroborate this anomaly                 |
| `timestamp`        | ISO 8601 datetime | When the anomaly was detected                                |

### `CascadeNode`

| Field                    | Type        | Description                                                    |
|--------------------------|-------------|----------------------------------------------------------------|
| `id`                     | string      | Node identifier                                                |
| `agent_domain`           | string      | Domain this step belongs to                                    |
| `title`                  | string      | Short description of this failure step                         |
| `severity`               | float [0–1] | Severity of this step                                          |
| `conditional_probability`| float [0–1] | Probability this step occurs given the previous step occurred  |
| `cumulative_probability` | float [0–1] | Product of all conditional probabilities from trigger to here  |
| `evidence`               | string      | Supporting rationale from the LLM                              |

### `CascadeChain`

| Field                  | Type        | Description                                                        |
|------------------------|-------------|---------------------------------------------------------------------|
| `id`                   | string      | Chain identifier                                                    |
| `trigger_anomaly_id`   | string      | ID of the root anomaly that started this chain                      |
| `nodes`                | CascadeNode[]| Ordered steps in the failure path                                  |
| `overall_probability`  | float [0–1] | Probability the full chain materialises                             |
| `time_to_impact_days`  | integer     | Days until the chain reaches a terminal state                       |
| `financial_impact`     | float       | Estimated USD impact                                                |
| `urgency_score`        | float       | `(1 / time_to_impact_days) × severity × (1 − reversibility)`       |

### `RiskScore`

| Field           | Type                                          | Description                              |
|----------------|-----------------------------------------------|------------------------------------------|
| `score`         | float [0–100]                                 | Composite risk score for this cycle      |
| `severity_level`| `low` \| `medium` \| `high` \| `critical`    | Human-readable bucket of the score       |
| `trend`         | `increasing` \| `stable` \| `decreasing`     | Trend vs. previous analysis              |
| `top_cascades`  | CascadeChain[]                                | Top 3 chains ranked by urgency           |
| `briefing`      | FounderBriefing                               | Plain-language founder summary           |
| `timestamp`     | ISO 8601 datetime                             | When this score was computed             |

### `FounderBriefing`

| Field                | Type   | Description                                      |
|---------------------|--------|--------------------------------------------------|
| `summary`            | string | 2–3 sentences on the highest-priority risk       |
| `timeline`           | string | e.g. `"50 days to financial impact"`             |
| `recommended_action` | string | One specific action the founder should take now  |

### `AgentReport`

| Field              | Type      | Description                                      |
|-------------------|-----------|--------------------------------------------------|
| `agent`            | string    | Agent domain name                                |
| `anomalies`        | Anomaly[] | All risk signals detected this cycle             |
| `raw_data_summary` | string    | Description of data sources loaded               |
| `timestamp`        | ISO 8601  | When the report was generated                    |

### `WhatIfScenario`

| Field                | Type          | Description                                         |
|---------------------|---------------|-----------------------------------------------------|
| `scenario_type`      | string        | One of the four supported scenario types            |
| `parameters`         | object        | Optional overrides, e.g. `{ "severity_multiplier": 1.5 }` |
| `modified_cascades`  | CascadeChain[]| Recalculated chains under the scenario              |
| `new_risk_score`     | float \| null | Risk score under the scenario                       |
| `comparison_briefing`| string        | Narrative comparing baseline vs. scenario           |
