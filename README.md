# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

> *Seven AI agents. Two model providers. One mission: see the kill chain before it kills your startup.*

Built at the **yconic New England Inter-Collegiate AI Hackathon** — March 28–29, 2026
Track: AI Innovation Hack · Powered by: **Google Gemini 2.5 Pro** + **OpenAI GPT-4o-mini** + **LangGraph**

**Live deployment:**
- Frontend: https://outstanding-essence-production.up.railway.app/
- Backend API: https://perfect-learning-production-814f.up.railway.app/
- Swagger docs: https://perfect-learning-production-814f.up.railway.app/docs

---

## Table of Contents

- [What Is DEADPOOL?](#what-is-deadpool)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Understanding the Code](#understanding-the-code)
  - [Backend Deep Dive](#backend-deep-dive)
  - [Frontend Deep Dive](#frontend-deep-dive)
- [API Reference](#api-reference)
- [Synthetic Data](#synthetic-data)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

---

## What Is DEADPOOL?

Startups don't die from one thing — they die from a **chain reaction** nobody mapped until it was too late. A lead engineer quietly disengages → the service she owns stops getting deployed → a critical feature deadline slips → the contract with your biggest client lapses → revenue craters → the down-round clause triggers → the company is dead.

**DEADPOOL is a multi-agent startup immune system.** Six specialist AI agents continuously monitor every operational layer of a company — **People, Finance, Infrastructure, Product, Legal, and Code Audit** — orchestrated by a **LangGraph pipeline** that cross-validates findings, traces cascade chains using LLM-driven consequence expansion, and produces plain-language founder briefings.

The system is **multi-model by design**: five specialist agents run on **Google Gemini 2.5 Flash**, the Head Agent and cascade expander run on **Gemini 2.5 Pro**, and the Finance Agent runs on **OpenAI GPT-4o-mini**. When agents on different model families independently corroborate the same risk, the signal is model-independent — not just one model agreeing with itself.

---

## Architecture Overview

```
  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐
  │ People       │  │ Finance        │  │ Infra           │
  │ (Gemini Flash│  │ (GPT-4o-mini)  │  │ (Gemini Flash)  │
  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘
  ┌──────┴───────┐  ┌───────┴────────┐  ┌────────┴────────┐
  │ Product      │  │ Legal          │  │ Code Audit      │
  │ (Gemini Flash│  │ (Gemini Flash) │  │ (Gemini Flash)  │
  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘
         └──────────────────▼──────────────────────┘
                   ┌───────────────────────────────────┐
                   │  HEAD AGENT (Gemini 2.5 Pro)      │
                   │  Cross-validate anomalies          │
                   │  Compute risk score 0–100          │
                   │  Generate FounderBriefing          │
                   │  Seed cascade threads (sev ≥ 0.5) │
                   └─────────────┬─────────────────────┘
                                 │ conditional
                       ┌─────────▼──────────┐
                       │  CASCADE EXPANDER  │◄──┐
                       │  (Gemini 2.5 Pro)  │   │ loop (max 5)
                       │  LLM next-step     │───┘
                       │  _apply_rules boost│
                       │  prune < 40%       │
                       └─────────┬──────────┘
                                 │ conditional
                       ┌─────────▼──────────┐
                       │  FORMAT OUTPUT     │
                       │  nodes/edges/chains│
                       └────────────────────┘
```

**Execution flow:**

1. All 6 specialist agents run **concurrently** via LangGraph parallel fan-out — each loads its domain data, calls its AI model, and returns structured `Anomaly` objects.
2. The **Head Agent** reads all 6 reports, cross-validates signals using a `CORROBORATION_MAP`, boosts severity for multi-domain corroborations (+15%), dampens uncorroborated weak signals (−15%), computes a 0–100 risk score, and calls Gemini to generate a structured `FounderBriefing`.
3. Anomalies with severity ≥ 0.5 become root threads fed into the **Cascade Expander loop**.
4. The Cascade Expander calls Gemini iteratively: *"given all active causal threads, what happens next?"* — collecting all threads together so cross-cause acceleration is captured. Branches below 40% probability are pruned. Loop runs up to 5 depths.
5. The **Format Output** node assembles `nodes`, `edges`, and `activeChains` for the React Flow dashboard.
6. Anomalies stream to the dashboard in real-time via **Server-Sent Events (SSE)** from `signal_bus.py` while the pipeline runs. The authoritative final result arrives via the POST response.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | **LangGraph** `StateGraph` | Typed state, conditional edges, parallel fan-out, cascade expander loop |
| AI (Specialists) | **Gemini 2.5 Flash** via `google-genai` SDK | 5 specialist agents (people, infra, product, legal, code_audit) |
| AI (Orchestration) | **Gemini 2.5 Pro** via `google-genai` SDK | Head Agent + cascade expansion |
| AI (Finance) | **GPT-4o-mini** via `openai` SDK | Finance agent — fast structured CSV extraction, precise arithmetic |
| Backend | **Python 3.11+ / FastAPI** | Async API server, SSE streaming, Pydantic v2 data validation |
| Frontend | **React 19 + Vite 6 + React Flow** | Two-page dashboard: Overview + Cascade Chains (`@xyflow/react`) |
| Real-time | **sse-starlette** | Server → browser push for live anomaly updates |
| Data | **Pandas** | CSV parsing for Finance Agent |
| Integrations | **slack-sdk**, **PyGithub** | Slack team monitoring and GitHub commit history |
| Deployment | **Caddy** + **Railway** | Single Railway service; Caddy serves built frontend + proxies `/api` |

---

## Project Structure

```
yconic_outliers/
├── .env                        # API keys (see Environment Variables)
├── .env.example                # Template for all required environment variables
├── Masterplan.md               # Full product vision & architecture document
├── README.md                   # ← You are here
│
├── backend/                    # ── Python FastAPI Backend ──
│   ├── main.py                 # 🚀 Entry point — routes, CORS, SSE, agent lifecycle
│   ├── models.py               # 📐 Pydantic v2 schemas (Anomaly, CascadeChain, RiskScore, FounderBriefing, etc.)
│   ├── orchestrator.py         # 🔀 LangGraph StateGraph — fan-out → head_agent → cascade_expander loop → format_output
│   ├── cascade_mapper.py       # 🔗 _llm_next_step (Gemini) + _apply_rules (probability boosts for domain combos)
│   ├── signal_bus.py           # 📡 In-memory pub/sub ring buffer for SSE anomaly streaming
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── agents/                 # 🤖 AI Agent Modules
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Abstract base — Gemini client, prompt template, JSON parsing
│   │   ├── head_agent.py       # Cross-validate + risk score + FounderBriefing + What-If simulation
│   │   ├── people_agent.py     # Team health & key-person risk         (Gemini 2.5 Flash)
│   │   ├── finance_agent.py    # Cash flow, runway, revenue            (GPT-4o-mini)
│   │   ├── infra_agent.py      # System reliability & deploy ops       (Gemini 2.5 Flash)
│   │   ├── product_agent.py    # User engagement & retention           (Gemini 2.5 Flash)
│   │   ├── legal_agent.py      # Contracts & compliance                (Gemini 2.5 Flash)
│   │   └── code_audit_agent.py # Codebase health, CVEs, bus factor     (Gemini 2.5 Flash)
│   │
│   ├── utils/
│   │   ├── dashboard_formatter.py  # Dashboard response formatting helpers
│   │   ├── slack_client.py         # 💬 Slack API integration client
│   │   ├── get_commit_history.py   # GitHub commit history fetcher
│   │   └── reddit_scraper.py       # Public Reddit JSON API scraper
│   │
│   └── data/                   # 📁 Synthetic Data (engineered cascade signals)
│       ├── team_activity.json         # → People Agent
│       ├── infrastructure.json        # → Infra Agent
│       ├── product_metrics.json       # → Product Agent
│       ├── contracts.json             # → Legal Agent
│       ├── codebase_audit.json        # → Code Audit Agent
│       └── csv/
│           ├── deadpool_finance_data.csv       # → Finance Agent: transaction ledger
│           ├── deadpool_revenue_pipeline.csv   # → Finance Agent: revenue + pipeline deals
│           └── deadpool_funding_runway.csv     # → Finance Agent: investor terms + runway
│
└── frontend/                   # ── React + Vite + React Flow Dashboard ──
    ├── index.html              # HTML entry point
    ├── package.json            # Dependencies: React 19, Vite 6, @xyflow/react
    ├── vite.config.js          # Vite build configuration
    ├── App.jsx                 # 🏠 Root — two-page app (Overview ↔ Cascade Chains)
    │
    ├── src/
    │   └── main.jsx            # React DOM mount point
    │
    ├── components/
    │   ├── layout/
    │   │   └── Header.jsx          # Top bar — DEADPOOL branding + Run Analysis button + page nav
    │   │
    │   ├── AgentsPanel.jsx         # 2×3 grid of agent status cards (idle/processing/healthy/warning/critical)
    │   ├── BriefingPanel.jsx       # FounderBriefing (summary, timeline, recommended_action)
    │   ├── FlawsPanel.jsx          # Scrollable liabilities list sorted by severity
    │   ├── RiskIndex.jsx           # 0–100 risk score with severity level + trend
    │   ├── CascadeChainPanel.jsx   # React Flow directed graph — cascade chains
    │   ├── ErrorBoundary.jsx       # React error boundary wrapper
    │   │
    │   ├── shared/
    │   │   └── StatusBadge.jsx     # Reusable status indicator
    │   │
    │   └── ingest/                 # Unused in production App.jsx (preserved for reference)
    │       ├── IngestTab.jsx
    │       ├── FileUploadPanel.jsx
    │       ├── FileSlot.jsx
    │       ├── AgentStatusPanel.jsx
    │       ├── AgentStatusCard.jsx
    │       ├── AgentTabBar.jsx
    │       ├── AgentOutputPanel.jsx
    │       └── AnomalyCard.jsx
    │
    ├── hooks/
    │   ├── useDeadpool.js          # Main hook — SSE + POST /api/head-agent/analyze + all state
    │   └── useCascaseAnimation.js  # Cascade animation controller (unused in production)
    │
    ├── utils/
    │   ├── formatter.js            # Number/date formatting
    │   └── riskColor.js            # Risk level → color mapping
    │
    └── constants/
        ├── agents.js           # Agent metadata, DOMAIN_COLORS
        ├── cascade.js          # Cascade definitions
        ├── fileSlots.js        # File slot configurations
        └── mockOutputs.js      # Mock agent outputs for offline development
```

---

## Getting Started

> **Just want to try it?** The live deployment is already running — open https://outstanding-essence-production.up.railway.app/ and click **Run Analysis**.

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Google API Key** (Gemini 2.5 Pro access)
- **OpenAI API Key** (GPT-4o-mini access)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/yconic_outliers.git
cd yconic_outliers
```

### 2. Set up environment variables

Create a `.env` file in the `backend/` directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_pat        # Optional — for Code Audit + Infra live data
GITHUB_REPO=owner/repo              # Optional — e.g. "acme/payments-service"
SLACK_BOT_TOKEN=your_slack_token    # Optional — for People Agent Slack integration
```

### 3. Start the backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

On startup you should see:
```
[DEADPOOL] All agents initialized. Ready.
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

Click **Run Analysis** in the header to trigger the full pipeline.

---

## Understanding the Code

### Backend Deep Dive

#### Entry Point: `backend/main.py`

On startup, the `lifespan` context manager:
1. Creates instances of all 6 specialist agents
2. Creates `HeadAgent` and passes it the specialist dict
3. Stores everything in a global `agent_registry`

The full pipeline runs via `asyncio.to_thread(run_pipeline, agent_registry, head_agent_instance)` — wrapping the synchronous LangGraph `graph.invoke()` call to avoid blocking the async event loop. After the pipeline returns, `main.py` merges `severityLevel`, `briefing`, and `timestamp` from `HeadAgent.last_risk_score` into the dashboard response.

**Key routes:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/health` | GET | System health + active agent list |
| `/api/agents/{name}/run` | GET | Run a single specialist agent |
| `/api/agents/all/run` | GET | Run all 6 specialists concurrently |
| `/api/head-agent/analyze` | POST | Full LangGraph pipeline — returns dashboard dict |
| `/api/dashboard` | GET | Alias for `/api/head-agent/analyze` |
| `/api/risk-score` | GET | Latest `RiskScore` (triggers fresh analysis if none cached) |
| `/api/cascades` | GET | List active cascade chains from last analysis |
| `/api/agents/{name}/report` | GET | Most recent report for a specific agent |
| `/api/whatif` | POST | What-If scenario simulation |
| `/api/sse/updates` | GET | SSE stream — real-time anomaly & risk updates |
| `/api/slack/status` | GET | Slack integration health |

#### LangGraph Orchestrator: `backend/orchestrator.py`

The core execution engine — a `StateGraph` with `OrchestratorState`:

```python
class OrchestratorState(TypedDict):
    specialist_reports: Annotated[list[AgentReport], operator.add]  # merged across parallel branches
    risk_score:      Optional[RiskScore]
    root_causes:     list[str]
    domains_present: list[str]
    active_threads:  list[dict]                          # current depth threads (replaced each iter)
    cascade_nodes:   Annotated[list[dict], operator.add] # accumulated across iterations
    cascade_edges:   Annotated[list[dict], operator.add]
    visited_causes:  Annotated[list[str],  operator.add]
    depth:           int
    dashboard:       Optional[dict]
```

Graph nodes: 6 specialist nodes (parallel) → `head_agent` → `cascade_expander` (loop, max 5) → `format_output`.

The `format_output` node assembles the final dashboard dict: `{ riskScore, trend, activeCascades, nodes, edges, activeChains }`.

#### Data Models: `backend/models.py`

All data is typed with **Pydantic v2** schemas:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Anomaly` | A single detected risk signal | `severity` (0–1), `confidence` (0–1), `affected_entities`, `evidence`, `cross_references` |
| `CascadeNode` | One step in a cascade chain | `conditional_probability`, `cumulative_probability` |
| `CascadeChain` | Full failure chain trigger → end-state | `overall_probability`, `time_to_impact_days`, `financial_impact`, `urgency_score` |
| `FounderBriefing` | Structured plain-language briefing | `summary`, `timeline`, `recommended_action` |
| `RiskScore` | Overall system output | `score` (0–100), `severity_level`, `trend`, `top_cascades` (top 3), `briefing: FounderBriefing` |
| `AgentReport` | Specialist agent output | `anomalies` list, `raw_data_summary` |
| `WhatIfScenario` | Simulation input/output | `scenario_type`, `parameters`, `modified_cascades`, `new_risk_score`, `comparison_briefing` |

#### Agent System: `backend/agents/`

**`base_agent.py` — Gemini-Powered Base Class**

All agents except Finance inherit from `BaseAgent`:
- Initializes a `google.genai.Client` with `GOOGLE_API_KEY`
- `run()` method: calls `load_data()` → builds a structured prompt → calls Gemini 2.5 Flash → parses JSON response → strips markdown fences → validates into `Anomaly` objects → publishes each to the signal bus → returns `AgentReport`
- If the model returns malformed JSON, gracefully returns an empty anomaly list

Subclasses only need to implement `load_data()` to return their domain data dict.

**`finance_agent.py` — GPT-4o-mini (Standalone)**

Does **not** extend `BaseAgent`. Uses the OpenAI SDK directly:
- Loads 3 CSV files via Pandas
- Calls `gpt-4o-mini` with `response_format={"type": "json_object"}` and `temperature=0.1`
- Creates **cross-provider corroboration**: when Finance (GPT-4o-mini) and Legal (Gemini) independently flag the same contract risk from different data, the signal is model-family-independent

**`head_agent.py` — The Orchestrator**

The Head Agent doesn't monitor a domain — it synthesizes and scores:

1. **`_cross_validate(anomalies)`**: Uses `CORROBORATION_MAP` (e.g., `people → [code_audit, infra]`). If 2+ corroborating domains have signals: severity +15%, confidence +10%. Uncorroborated low-severity signals: severity −15%.

2. **`_compute_risk_score()`**: Three additive components, each capped:
   - Cascade urgency: `Σ min(urgency × 500, 40)` for top 3 — up to 40 pts
   - High-severity count: `count(severity ≥ 0.75) × 8` — up to 40 pts
   - Baseline: `avg(severities) × 20` — up to 20 pts

3. **`_generate_briefing()`**: Calls Gemini 2.5 Pro with anomaly + cascade summaries, requesting a structured `FounderBriefing` JSON.

4. **`simulate_whatif(scenario)`**: Modifies anomaly severities by scenario type, re-runs the full `analyze()` pipeline, generates a Gemini comparison briefing.

#### Cascade Logic: `backend/cascade_mapper.py`

Contains two functions used by the LangGraph orchestrator's cascade expander node:

- **`_llm_next_step(client, active_threads, depth)`**: Sends all currently active causal threads to Gemini 2.5 Pro and asks: *"given these threads, what are the next consequences?"*. Returns a JSON array with `cause`, `probability` (0–100), `contributing_causes`, and `is_terminal`. Passing all threads together enables Gemini to detect cross-cause acceleration.

- **`_apply_rules(domains_present, base_prob)`**: Additive probability boosts for dangerous domain combos:
  - `finance+people`: +25 — cash + workforce crisis
  - `legal+finance`: +20 — compliance meets burn pressure
  - `infra+product`: +15 — infra failures manifest in product
  - Caps at 99 to keep LLM output meaningful.

The `CascadeMapperAgent` class and `_build_cascade` function also exist in this file but are not used in the main pipeline.

#### Signal Bus: `backend/signal_bus.py`

In-memory **publish/subscribe** system:
- Agents call `bus.publish(anomaly)` after each detection
- SSE endpoint subscribes and streams events to the dashboard
- Ring buffer retains the last 500 events
- Supports multiple concurrent subscribers

### Frontend Deep Dive

React 19 + Vite 6 single-page dashboard. No file upload — agents load their own data from `backend/data/`. Analysis is triggered by clicking **Run Analysis** in the header.

#### Main Hook: `hooks/useDeadpool.js`

Manages the entire analysis lifecycle:

1. Opens `EventSource` to `/api/sse/updates` — streams anomaly events incrementally, updating liabilities and agent statuses in real time while the pipeline runs.
2. POSTs to `/api/head-agent/analyze` — the authoritative final response. On completion, overwrites all SSE-accumulated state with the definitive values.
3. Closes SSE after POST resolves.

Exposes: `agentStatuses`, `liabilities`, `cascadeChains`, `cascadeNodes`, `cascadeEdges`, `riskScore`, `severityLevel`, `trend`, `briefing`, `running`, `done`, `error`, `runAnalysis`.

#### Page: Overview (default)

Two-column layout:
- **Left (3fr)** — `AgentsPanel`: 2×3 grid of agent cards with animated status and rotating processing messages during analysis.
- **Right (7fr)**:
  - `BriefingPanel` — renders `FounderBriefing.summary`, `.timeline`, `.recommended_action`
  - `FlawsPanel` — scrollable severity-sorted list of detected liabilities
  - `RiskIndex` — 0–100 score with severity level and trend

#### Page: Cascade Chains (unlocks after analysis)

Full-width `CascadeChainPanel` using **React Flow** (`@xyflow/react`):
- Multi-node chains: one horizontal row per chain, nodes connected left→right with animated edges
- Single-node chains: packed into a single horizontal row, connected sequentially
- Domain-colored nodes with probability bars; MiniMap, Controls, domain legend in header
- `fitView` called on load and on data change

#### SSE Integration

The `useDeadpool` hook opens an `EventSource` receiving three event types:
- `anomaly` — new anomaly detected; incrementally adds to liabilities list and updates agent status
- `risk_score` — updates risk score display
- `heartbeat` — keep-alive ping every 15 seconds (no action taken)

#### Utilities & Constants

- **`formatter.js`** — Number and date formatting helpers
- **`riskColor.js`** — Maps risk levels to color codes
- **`agents.js`** — Agent metadata, `DOMAIN_COLORS` (used by React Flow nodes and legend)
- **`cascade.js`** — Cascade definitions
- **`fileSlots.js`** — File slot configurations (for reference)
- **`mockOutputs.js`** — Mock agent outputs for offline development

---

## API Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Run a Single Agent
```bash
# Options: people, finance, infra, product, legal, code_audit
curl http://localhost:8000/api/agents/people/run
```

### Run All Agents Concurrently
```bash
curl http://localhost:8000/api/agents/all/run
```

### Full Orchestrated Analysis
```bash
curl -X POST http://localhost:8000/api/head-agent/analyze
```
Returns dashboard dict: `{ riskScore, severityLevel, trend, briefing, nodes, edges, activeChains, activeCascades }`.

### Get Latest Risk Score
```bash
curl http://localhost:8000/api/risk-score
```

### List Active Cascades
```bash
curl http://localhost:8000/api/cascades
```

### What-If Simulation
```bash
curl -X POST http://localhost:8000/api/whatif \
  -H "Content-Type: application/json" \
  -d '{"scenario_type": "engineer_leaves", "parameters": {"severity_multiplier": 1.5}}'
```
**Scenario types:** `engineer_leaves`, `client_churns`, `cve_discovered`, `cloud_costs_double`

### Get Agent's Last Report
```bash
curl http://localhost:8000/api/agents/finance/report
```

### SSE Stream (Real-time)
```bash
curl -N http://localhost:8000/api/sse/updates
```
Event types: `anomaly`, `risk_score`, `heartbeat` (every 15s)

### Slack Integration Status
```bash
curl http://localhost:8000/api/slack/status
```

---

## Synthetic Data

All data files are in `backend/data/` with **carefully engineered signals** and consistent entity linking keys (`sarah_chen`, `payments-service`, `nexus_corp`, `payments_api_v2`) that enable cross-domain cascade tracing:

| File | Agent | Key Signals |
|------|-------|-------------|
| `team_activity.json` | People | Sarah Chen: 94% commit drop over 5 weeks. 11 others: normal with noise. |
| `csv/deadpool_finance_data.csv` | Finance | $900K raised, $73K/mo burn, $493K cash, $1.2K/mo revenue. |
| `csv/deadpool_revenue_pipeline.csv` | Finance | Nexus Corp $423K/yr deal at risk (prob 0.85→0.35). Greenleaf $9K overdue (noise). |
| `csv/deadpool_funding_runway.csv` | Finance | Down-round clause at runway <3mo. Base runway: 6.7mo. Worst case: 3.6mo. |
| `infrastructure.json` | Infra | `payments-service`: 0 deploys in 2 weeks, API v2 at 34% completion. |
| `product_metrics.json` | Product | Payments dashboard errors 0.2%→12%. Other features stable. |
| `contracts.json` | Legal | Nexus Corp Section 4.2: API v2 by April 15 or termination. PCI DSS obligation. |
| `codebase_audit.json` | Code Audit | `payments-service`: bus factor=1, CVE-2026-4821 (CVSS 8.1), coverage 82%→61%. |

**Primary demo cascade:**
> Sarah Chen disengages → `payments-service` code ownership gap → deploy stall → Nexus Corp API v2 deadline missed → contract termination → 42% revenue cliff → runway drops to 2.5 months → down-round clause triggers

---

## Environment Variables

| Variable | Required | Used By | Notes |
|----------|----------|---------|-------|
| `GOOGLE_API_KEY` | ✅ Yes | All Gemini agents + Head Agent + cascade expander | Required for startup |
| `OPENAI_API_KEY` | ✅ Yes | Finance Agent (GPT-4o-mini) | Required for startup |
| `GITHUB_TOKEN` | ⚠️ Recommended | Code Audit Agent, Infra Agent | Falls back to JSON data if missing |
| `GITHUB_REPO` | ⚠️ Recommended | Code Audit Agent, Infra Agent | Format: `owner/repo` |
| `SLACK_BOT_TOKEN` | ❌ Optional | `utils/slack_client.py` | Gracefully skipped if missing |

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  <strong>DEADPOOL</strong> — <em>Dependency Evaluation And Downstream Prediction Of Operational Liabilities</em><br/>
  Built by Team Outliers · yconic New England Inter-Collegiate AI Hackathon, March 2026
</p>

<p align="center">
  Built with ❤️ by Reghu, Pavi, Ackshay, Yashas and Srini
</p>
