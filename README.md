# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

> *Seven AI agents. Two model providers. One mission: see the kill chain before it kills your startup.*

Built at the **yconic New England Inter-Collegiate AI Hackathon** — March 28–29, 2026  
Track: AI Innovation Hack · Powered by: **Google Gemini 2.5 Flash** + **OpenAI GPT-4o-mini** + **LangGraph**

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
- [Cascade Paths](#cascade-paths)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

---

## What Is DEADPOOL?

Startups don't die from one thing — they die from a **chain reaction** nobody mapped until it was too late. A lead engineer quietly disengages → the service she owns stops getting deployed → a critical feature deadline slips → the contract with your biggest client lapses → revenue craters → the down-round clause triggers → the company is dead.

**DEADPOOL is a multi-agent startup immune system.** Six specialist AI agents continuously monitor every operational layer of a company — **People, Finance, Infrastructure, Product, Legal, and Code Audit** — orchestrated by a **Head Supervisor** that cross-validates findings, traces cascade chains through dependency graphs, and produces plain-language founder briefings.

The system is **multi-model by design**: five specialist agents and the Head Supervisor run on **Google Gemini 2.5 Flash**, while the Finance Agent runs on **OpenAI GPT-4o-mini**. When agents on different model families independently corroborate the same risk, the signal is model-independent — not just one model agreeing with itself.

---

## Architecture Overview

```
                      ┌─────────────────────────────┐
                      │       DEADPOOLState          │
                      │  Shared typed state across   │
                      │  all nodes in the graph      │
                      └──────────────┬──────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │   HEAD SUPERVISOR (Gemini Flash) │
                    │  Cross-validates all reports     │
                    │  Conditional edge routing        │
                    └─────────┬──────────────────────┘
          ┌──────────────────┬┼──────────────────┐
          │                  ││                  │
  ┌───────▼──────┐  ┌───────▼┴───────┐  ┌──────▼──────────┐
  │ People       │  │ Finance        │  │ Infra           │
  │ (Gemini)     │  │ (GPT-4o-mini)  │  │ (Gemini)        │
  └──────────────┘  └────────────────┘  └─────────────────┘
  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐
  │ Product      │  │ Legal          │  │ Code Audit      │
  │ (Gemini)     │  │ (Gemini)       │  │ (Gemini)        │
  └──────────────┘  └────────────────┘  └─────────────────┘
          │                  │                  │
          └──────────────────▼──────────────────┘
                    ┌─────────────────────┐
                    │ Cascade Mapper      │
                    │ (deterministic)     │
                    └──────────┬──────────┘
                    ┌──────────▼──────────┐
                    │ Briefing (Gemini)   │
                    └─────────────────────┘
```

**Execution flow:**

1. All 6 specialist agents run **concurrently** via LangGraph parallel fan-out — each loads its domain data, calls its AI model, and returns structured anomalies.
2. The **Head Supervisor** reads all 6 domain reports, identifies cross-domain anomalies, and routes corroboration queries to targeted agents via conditional edges.
3. Cross-validation boosts severity for corroborated signals (+15%), dampens uncorroborated low-severity noise (−15%). Cross-provider corroborations (Gemini ↔ GPT-4o-mini) carry extra confidence weight.
4. High-severity anomalies (≥0.5) are fed to the **Cascade Mapper** — a deterministic engine (no LLM) that traces dependencies forward through 6 pre-built failure paths, multiplying conditional probabilities at each step and pruning chains below a 0.25 threshold.
5. The Head Supervisor generates a **founder briefing** via Gemini — a 3–5 sentence plain-language summary naming the risk, the timeline, and one specific action to take.
6. Results stream to the **React + D3.js dashboard** in real-time via **Server-Sent Events (SSE)**.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | **LangGraph** `StateGraph` | Typed state, conditional edges, parallel fan-out, `MemorySaver` checkpointing |
| AI (Primary) | **Gemini 2.5 Flash** via `google-genai` SDK | 5 specialist agents + briefing generation |
| AI (Head Agent) | **Gemini 2.5 Pro** via `google-genai` SDK | Head Agent — largest context window for cross-domain synthesis |
| AI (Finance) | **GPT-4o-mini** via `openai` SDK | Finance agent — fast structured CSV extraction, precise arithmetic |
| Backend | **Python 3.11+ / FastAPI** | Async API server, SSE streaming, Pydantic v2 data validation |
| Frontend | **React 19 + Vite 6 + D3.js** | Dashboard with data ingestion, cascade graph visualization, real-time SSE client |
| Real-time | **sse-starlette** | Server → browser push for live anomaly & risk score updates |
| Data | **Pandas** | CSV parsing for Finance Agent |
| Integrations | **slack-sdk**, **PyGithub** | Slack team monitoring and GitHub commit history |

---

## Project Structure

```
yconic_outliers/
├── .env                        # API keys (see Environment Variables)
├── .env.example                # Template for all required environment variables
├── Masterplan.md               # Full product vision & architecture document
├── Productrequirement.md       # Product requirements document
├── data_plan.md                # Data architecture planning document
├── taskplan.md                 # Execution task breakdown
├── README.md                   # ← You are here
│
├── backend/                    # ── Python FastAPI Backend ──
│   ├── main.py                 # 🚀 Entry point — routes, CORS, SSE, agent lifecycle
│   ├── models.py               # 📐 Pydantic v2 schemas (Anomaly, CascadeChain, RiskScore, FounderBriefing, etc.)
│   ├── orchestrator.py         # 🔀 LangGraph StateGraph builder — fan-out/fan-in pipeline
│   ├── signal_bus.py           # 📡 In-memory pub/sub event bus for SSE anomaly streaming
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── utils/
│   │   ├── cascade_mapper.py   # 🔗 Deterministic cascade engine — 6 pre-seeded failure paths
│   │   ├── slack_client.py     # 💬 Slack API integration client
│   │   └── reddit_scraper.py   # 🌐 Reddit public JSON API scraper (r/BrainrotGenz)
│   │
│   ├── agents/                 # 🤖 AI Agent Modules
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Abstract base — Gemini client, prompt template, JSON parsing
│   │   ├── head_agent.py       # Orchestrator — cross-validation, cascade mapping, briefing
│   │   ├── people_agent.py     # Team health & key-person risk         (Gemini Flash)
│   │   ├── finance_agent.py    # Cash flow, runway, revenue            (GPT-4o-mini)
│   │   ├── infra_agent.py      # System reliability & deploy ops      (Gemini Flash)
│   │   ├── product_agent.py    # User engagement & retention          (Gemini Flash)
│   │   ├── legal_agent.py      # Contracts & compliance               (Gemini Flash)
│   │   └── code_audit_agent.py # Codebase health, CVEs, bus factor    (Gemini Flash)
│   │
│   └── data/                   # 📁 Synthetic Data (engineered cascade signals)
│       ├── team_activity.json         # → People Agent
│       ├── infrastructure.json        # → Infra Agent
│       ├── product_metrics.json       # → Product Agent
│       ├── contracts.json             # → Legal Agent
│       ├── codebase_audit.json        # → Code Audit Agent
│       ├── financials.json            # → Finance Agent (JSON financials)
│       └── csv/
│           ├── deadpool_finance_data.csv       # → Finance Agent: transaction ledger
│           ├── deadpool_revenue_pipeline.csv   # → Finance Agent: revenue + pipeline deals
│           ├── deadpool_funding_runway.csv     # → Finance Agent: investor terms + runway
│           └── product_data.csv               # → Product Agent: CSV variant
│
└── frontend/                   # ── React + Vite + D3.js Dashboard ──
    ├── index.html              # HTML entry point
    ├── package.json            # Dependencies: React 19, Vite 6, D3.js
    ├── vite.config.js          # Vite build configuration
    ├── App.jsx                 # 🏠 Root — tab navigation (Ingest ↔ Cascade), SSE connection
    │
    ├── src/
    │   └── main.jsx            # React DOM mount point
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Header.jsx          # Top bar — DEADPOOL branding + live risk score
    │   │   └── TabBar.jsx          # Tab navigation
    │   │
    │   ├── ingest/                 # Data ingestion & agent monitoring tab
    │   │   ├── IngestTab.jsx       # Main ingest view — file upload + agent status
    │   │   ├── FileUploadPanel.jsx # Drag-and-drop file upload for each data slot
    │   │   ├── FileSlot.jsx        # Individual upload slot
    │   │   ├── AgentStatusPanel.jsx # Real-time agent status grid
    │   │   ├── AgentStatusCard.jsx  # Single agent status (idle/running/done/error)
    │   │   ├── AgentTabBar.jsx     # Agent output sub-tabs
    │   │   ├── AgentOutputPanel.jsx # Agent report display
    │   │   └── AnomalyCard.jsx     # Anomaly card with severity badge
    │   │
    │   ├── cascade/                # Cascade visualization tab
    │   │   ├── CascadeTab.jsx      # Main cascade analysis view
    │   │   ├── CascadeGraph.jsx    # D3.js directed graph — cascade chains with animation
    │   │   ├── CascadeNode.jsx     # Domain-colored node with glow & pulse effects
    │   │   ├── CascadeEdge.jsx     # Edge with probability label & thickness encoding
    │   │   ├── CascadeChainList.jsx # List view of cascade chains with details
    │   │   ├── RiskMetricsBar.jsx  # Risk score + key financial metrics
    │   │   └── GraphLegend.jsx     # Domain color legend
    │   │
    │   └── shared/
    │       └── StatusBadge.jsx     # Reusable status indicator
    │
    ├── hooks/
    │   ├── useAgentProcessor.js    # Agent lifecycle — file management + backend API orchestration
    │   └── useCascaseAnimation.js  # Cascade graph pulse animation controller
    │
    ├── utils/
    │   ├── formatter.js            # Number/date formatting
    │   └── riskColor.js            # Risk level → color mapping
    │
    └── constants/
        ├── agents.js           # Agent metadata (names, domains, colors, descriptions)
        ├── cascade.js          # Cascade path definitions
        ├── fileSlots.js        # File upload slot configurations
        └── mockOutputs.js      # Mock agent outputs for offline development
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Google API Key** (Gemini 2.5 Flash access)
- **OpenAI API Key** (GPT-4o-mini access)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/yconic_outliers.git
cd yconic_outliers
```

### 2. Set up environment variables

Create a `.env` file in the **project root**:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=your_slack_bot_token      # Optional — for Slack integration
```

### 3. Start the backend

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run the server
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive Swagger docs at `http://localhost:8000/docs`.

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

The dashboard will be available at `http://localhost:5173`.

---

## Understanding the Code

### Backend Deep Dive

#### Entry Point: `backend/main.py`

On startup, the `lifespan` context manager:
1. Creates instances of all 6 specialist agents (`PeopleAgent`, `FinanceAgent`, `InfraAgent`, `ProductAgent`, `LegalAgent`, `CodeAuditAgent`)
2. Creates the `HeadAgent` and passes it the specialist dict
3. Stores everything in a global `agent_registry`

All agents run via `asyncio.to_thread()` to avoid blocking the async event loop.

**Key routes:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/health` | GET | System health + active agent list |
| `/api/agents/{name}/run` | GET | Run a single specialist agent |
| `/api/agents/all/run` | GET | Run all 6 specialists concurrently |
| `/api/head-agent/analyze` | POST | Full pipeline: all agents → cross-validation → cascades → briefing |
| `/api/risk-score` | GET | Latest risk score (triggers analysis if none cached) |
| `/api/cascades` | GET | List all active cascade chains |
| `/api/agents/{name}/report` | GET | Most recent report for a specific agent |
| `/api/whatif` | POST | What-If simulation |
| `/api/sse/updates` | GET | SSE stream — real-time anomaly & risk updates |
| `/api/slack/status` | GET | Slack integration health |

#### Data Models: `backend/models.py`

All data flowing through the system is typed with **Pydantic v2** schemas:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Anomaly` | A single detected risk signal | `severity` (0–1), `confidence` (0–1), `affected_entities`, `evidence`, `cross_references` |
| `CascadeNode` | One step in a cascade chain | `conditional_probability`, `cumulative_probability` |
| `CascadeChain` | Full failure chain trigger → end-state | `overall_probability`, `time_to_impact_days`, `financial_impact`, `urgency_score` |
| `FounderBriefing` | Structured plain-language briefing | `summary`, `timeline`, `recommended_action` |
| `RiskScore` | Overall system output | `score` (0–100), `severity_level`, `trend`, `top_cascades` (top 3), `briefing: FounderBriefing` |
| `AgentReport` | Specialist agent output | `anomalies` list, `raw_data_summary` |
| `WhatIfScenario` | Simulation input/output | `scenario_type`, `parameters`, `modified_cascades`, `new_risk_score` |

#### Agent System: `backend/agents/`

**`base_agent.py` — Gemini-Powered Base Class**

All agents except Finance inherit from `BaseAgent`:
- Initializes a `google.genai.Client` with `GOOGLE_API_KEY`
- `run()` method: calls `load_data()` → builds a structured prompt → calls Gemini 2.5 Flash → parses JSON response → strips markdown fences → validates into `Anomaly` objects → publishes each to the signal bus → returns `AgentReport`
- If the model returns malformed JSON, gracefully returns an empty anomaly list (never crashes the graph)

Subclasses only need to implement `load_data()` to return their domain data dict.

**`finance_agent.py` — GPT-4o-mini (Standalone)**

Does **not** extend `BaseAgent`. Uses the OpenAI SDK directly:
- Loads 3 CSV files via Pandas: `deadpool_finance_data.csv`, `deadpool_revenue_pipeline.csv`, `deadpool_funding_runway.csv`
- Calls `gpt-4o-mini` with `response_format={"type": "json_object"}` and `temperature=0.1` for deterministic, structured output
- Handles GPT's tendency to wrap arrays in keys like `{"anomalies": [...]}` — unwraps automatically
- Creates **cross-provider corroboration**: when Finance (GPT-4o-mini) and Legal (Gemini) independently flag the same contract risk, the signal is model-family-independent

**`head_agent.py` — The Orchestrator**

The Head Agent doesn't monitor a domain. It orchestrates:

1. **`_cross_validate(anomalies)`**: Uses a `CORROBORATION_MAP` (e.g., `people → [code_audit, infra]`). If 2+ corroborating domains have signals, anomaly severity is boosted by 15%. Uncorroborated low-severity anomalies are dampened by 15%.

2. **Cascade mapping**: Feeds validated anomalies (severity ≥ 0.5) to `cascade_mapper.map_cascade()`. Sorts chains by urgency, keeps top 3.

3. **`_compute_risk_score()`**: Weighted formula:
   - Cascade urgency scores (capped at 40 points)
   - High-severity anomaly count (capped at 40 points)
   - Average severity baseline (up to 20 points)
   - Total: 0–100 scale

4. **`_generate_briefing()`**: Calls Gemini with anomaly + cascade summaries, requesting a 3–5 sentence founder briefing — names the risk, states the timeline, recommends one action.

5. **`simulate_whatif(scenario)`**: Modifies anomaly severities based on scenario type (e.g., `engineer_leaves` → 1.5× People severity), re-runs the full pipeline, generates a comparison briefing.

#### Cascade Mapper: `backend/cascade_mapper.py`

A **deterministic** engine (no LLM) that traces failures forward through pre-built dependency graphs:

- **`CASCADE_PATHS`**: 6 hardcoded failure chains, each with ordered nodes and baseline conditional probabilities
- **`TRIGGER_MAP`**: Maps keywords in anomaly text to cascade path keys (e.g., `"sarah chen"` → `people_key_person`, `"cve"` → `code_audit_cve`)
- **`map_cascade(anomaly)`**: Walks the matched path, multiplying conditional probabilities at each step. Prunes when cumulative probability drops below **0.25**.
- **Urgency formula**: `urgency = (1 / time_to_impact_days) × severity × (1 − reversibility)`

#### Signal Bus: `backend/signal_bus.py`

An in-memory **publish/subscribe** system:
- Agents call `bus.publish(anomaly)` after each detection
- SSE endpoint (`/api/sse/updates`) subscribes and streams events to the dashboard
- Ring buffer retains the last 500 events
- Supports multiple concurrent subscribers

### Frontend Deep Dive

The frontend is a **React 19 + Vite 6 + D3.js** dashboard with two main tabs:

#### Ingest Tab (`components/ingest/`)

Handles data ingestion and agent monitoring:

- **`FileUploadPanel`** + **`FileSlot`**: Drag-and-drop upload slots mapped to specific agent domains via `fileSlots.js`. Each slot accepts the data file for its corresponding agent.
- **`AgentStatusPanel`** + **`AgentStatusCard`**: Real-time status grid showing each agent transitioning through states: idle → processing → healthy/warning/critical.
- **`AgentOutputPanel`** + **`AnomalyCard`**: Displays formatted agent findings after analysis, with color-coded severity badges.
- **`useAgentProcessor` hook**: Manages the full lifecycle — tracks uploaded files, triggers backend API calls, monitors agent run states, and exposes `handleFile()` and `runAnalysis()` methods.

#### Cascade Tab (`components/cascade/`)

Visualizes detected cascade chains from the backend:

- **`CascadeGraph`**: D3.js-powered directed graph with domain-colored nodes, probability-labeled edges with thickness encoding, radial gradient glow effects, and animated pulse propagation along active cascade paths.
- **`CascadeNode`**: Individual node rendered with domain-specific color, severity indicator, and hover details showing evidence.
- **`CascadeEdge`**: SVG edge with probability label and arrow marker. Active edges are highlighted during cascade animation.
- **`CascadeChainList`**: Expandable list of all detected cascades with step-by-step node details, probabilities, financial impact, and time-to-impact.
- **`RiskMetricsBar`**: Displays the 0–100 risk score with trend direction and key financial metrics.
- **`GraphLegend`**: Color legend mapping each domain (People, Finance, Product, Infra, Legal, Code Audit) to its node color.
- **`useCascadeAnimation` hook**: Controls pulse animation timing, progressively highlighting cascade edges.

#### SSE Integration

The frontend maintains a persistent SSE connection to `/api/sse/updates`, receiving three event types:
- `anomaly` — New anomaly detected by a specialist agent
- `risk_score` — Updated overall risk score with cascades and briefing
- `heartbeat` — Keep-alive ping every 15 seconds

#### Utilities & Constants

- **`formatter.js`** — Number and date formatting helpers
- **`riskColor.js`** — Maps risk levels (0–100) to color codes for consistent visual encoding
- **`agents.js`** — Agent metadata: domain names, display labels, colors, icons, descriptions
- **`cascade.js`** — Cascade path definitions and default visualization configs
- **`fileSlots.js`** — Maps file upload slots to their target agent domains
- **`mockOutputs.js`** — Mock agent outputs for offline/development mode

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
Returns `RiskScore` with top 3 cascades and founder briefing.

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

All data files are in `backend/data/` and contain **carefully engineered signals** with consistent entity linking keys (`sarah_chen`, `payments-service`, `nexus_corp`, `payments_api_v2`) that enable cross-domain cascade tracing:

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

---

## Cascade Paths

Six pre-seeded failure patterns in `cascade_mapper.py`:

| # | Trigger → End State | Impact | Days |
|---|---------------------|--------|------|
| 1 | **Key-person departure** → code gap → delivery delay → contract breach → revenue loss → down-round | $1.9M | 75 |
| 2 | **Critical CVE** → compliance breach → legal exposure → investor confidence loss | $750K | 45 |
| 3 | **Test coverage decline** → bugs shipped → churn → revenue drop | $400K | 60 |
| 4 | **Tech debt** → deploy velocity drop → feature failure → competitive loss | $250K | 90 |
| 5 | **Revenue concentration** → client churn → revenue cliff → down-round trigger | $1.2M | 60 |
| 6 | **Infra degradation** → SLA breach → contract penalty → burn spike → runway compression | $500K | 50 |

Each path prunes at a **cumulative probability threshold of 0.25** — low-probability chains are cut to prevent noise.

---

## Environment Variables

| Variable | Required | Used By | Notes |
|----------|----------|---------|-------|
| `GOOGLE_API_KEY` | ✅ Yes | All Gemini agents + Head Agent | Required for startup |
| `OPENAI_API_KEY` | ✅ Yes | Finance Agent (GPT-4o-mini) | Required for startup |
| `GITHUB_TOKEN` | ⚠️ Recommended | Code Audit Agent, Infra Agent | Falls back to JSON if missing |
| `GITHUB_REPO` | ⚠️ Recommended | Code Audit Agent, Infra Agent | Format: `owner/repo` |
| `SLACK_BOT_TOKEN` | ❌ Optional | `utils/slack_client.py` | Only for Slack integration; gracefully skipped if missing |

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
  Built by Team Outliers
</p>
