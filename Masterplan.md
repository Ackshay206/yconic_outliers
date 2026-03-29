# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

*Seven AI agents. One mission. See the kill chain before it kills your startup.*

---

## The problem

Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

A lead engineer quietly disengages. Nobody notices for three weeks. The payments service she owns stops getting deployed. A critical feature deadline slips. The contract with your biggest client — 42% of revenue — has a delivery clause tied to that feature. The contract lapses. Revenue craters overnight. Your runway drops below three months. The down-round clause in your investor agreement triggers. The company is effectively dead.

Every signal was visible. The GitHub commits were declining. The deployment frequency was dropping. The contract deadline was approaching. The revenue concentration was documented. The investor terms were signed. But no tool, no dashboard, no human connected these dots across domains until the post-mortem.

This is the problem DEADPOOL solves.

**Who experiences it:** Every seed-to-Series B founder running a SaaS company. These are companies with 5–50 employees where no single person has full operational visibility across engineering, finance, legal, and product simultaneously. The failure modes are identical across the category. The signals are always present. The cross-domain synthesis never happens.

---

## The vision

DEADPOOL is a multi-agent startup immune system built on LangGraph's stateful graph orchestration framework. Six specialist agents continuously monitor every operational layer of a company — people, finance, infrastructure, product, legal, and codebase — connected by a LangGraph `StateGraph` where a Head Supervisor node orchestrates them all: dynamically routing cross-validation tasks between specialists via conditional edges, accumulating corroborated evidence in a shared typed state object, and tracing exactly how a single anomaly cascades into downstream failures.

The system is **model-agnostic by design** — five specialist agents and the Head Supervisor run on **Google Gemini** (gemini-2.5-flash), while the Finance Agent runs on **OpenAI GPT-4o-mini**. This multi-provider architecture is intentional: it demonstrates that the orchestration layer (LangGraph) is the intelligence, not any single model. It also provides a natural cross-validation benefit — when a Gemini-powered agent and a GPT-4o-mini-powered agent independently corroborate the same anomaly, the finding is robust across model families, not just consistent within one model's biases.

We don't show you isolated metrics. We show you the domino chain. And we show you which domino to catch.

---

## Architecture

### The 7-node LangGraph

DEADPOOL runs as a **LangGraph `StateGraph`**. Six specialist nodes are domain experts — pure functions that read from `DEADPOOLState` and write their anomaly outputs back. The Head Supervisor node is the graph's central router — it reads all specialist outputs, reasons over them using Gemini, and uses **conditional edges** to dynamically delegate corroboration tasks back to specific specialists before routing to the cascade mapper and briefing nodes.

**Model assignment strategy:**

| Node | Model | Why |
|------|-------|-----|
| Head Supervisor | **Gemini 2.5 Flash** | Longest context window needed for cross-domain synthesis. Reads all six domain reports + corroboration history + cascade state simultaneously. Gemini's 1M token context handles the full state without truncation. |
| People Agent | **Gemini 2.5 Flash** | Analyzes developer activity patterns across 12-week time series. Benefits from Gemini's strong pattern recognition on tabular/temporal data. |
| Finance Agent | **GPT-4o-mini** | The only node running on OpenAI. Deliberate choice: Finance is the most structured agent — CSV parsing, arithmetic (burn rate, runway, revenue concentration), and investor clause threshold checks. GPT-4o-mini excels at structured data extraction and precise numerical reasoning at very low latency. It also creates a **cross-provider corroboration signal**: when the GPT-4o-mini Finance Agent and Gemini-powered Legal Agent independently flag the same contract risk from different data sources, the finding is model-family-independent. |
| Infra Agent | **Gemini 2.5 Flash** | Monitors deployment pipelines and service health. Benefits from Gemini's ability to reason about system metrics and correlate degradation patterns. |
| Product Agent | **Gemini 2.5 Flash** | Analyzes user engagement, churn, NPS, and support ticket sentiment. Gemini's strong language understanding handles sentiment analysis well. |
| Legal Agent | **Gemini 2.5 Flash** | Parses contract clauses, checks compliance deadlines, and cross-references regulatory obligations. Benefits from Gemini's document comprehension. |
| Code Audit Agent | **Gemini 2.5 Flash** | Scans dependency trees, calculates bus factor, checks CVE databases, analyzes PR review patterns. Benefits from Gemini's code understanding. |
| Cascade Mapper | *deterministic* | No LLM — pure graph traversal with probability multiplication. NetworkX BFS. |
| Briefing Node | **Gemini 2.5 Flash** | Generates the founder-facing briefing. Uses Gemini for natural, clear language synthesis. |

**Why multi-provider matters for the demo:** When the Head Supervisor (Gemini) cross-validates an anomaly between the Finance Agent (GPT-4o-mini) and the Legal Agent (Gemini), and both independently corroborate the same risk — that's a stronger signal than two calls to the same model. Different model families have different failure modes and biases. Agreement across providers is evidence of genuine signal, not model echo.

```
                      ┌─────────────────────────────┐
                      │       DEADPOOLState          │
                      │  TypedDict — shared across   │
                      │  all nodes in the graph      │
                      │                              │
                      │  anomalies: list[Anomaly]    │
                      │  domain_reports: dict        │
                      │  corroboration_queue: list   │
                      │  cascade_chains: list        │
                      │  risk_score: float           │
                      │  briefing: str               │
                      │  iteration: int              │
                      └──────────────┬──────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │       HEAD SUPERVISOR NODE       │
                    │       (Gemini 2.5 Flash)         │
                    │                                  │
                    │  Reads all domain_reports        │
                    │  Reasons over anomalies          │
                    │  Emits conditional routing       │
                    │  decision via add_conditional_   │
                    │  edges → corroboration targets   │
                    └─────────┬───────────────────────┘
          ┌──────────────────┬┼──────────────────┐
          │                  ││                  │
  ┌───────▼──────┐  ┌────────▼┴──────┐  ┌───────▼──────────┐
  │ People Node  │  │ Finance Node   │  │   Infra Node     │
  │ (Gemini)     │  │ (GPT-4o-mini)  │  │   (Gemini)       │
  │              │  │                │  │                  │
  │ Team health  │  │ Cash flow      │  │ System uptime    │
  │ Key-person   │  │ Runway         │  │ Deploy velocity  │
  │ Engagement   │  │ Revenue        │  │ CI/CD health     │
  └──────────────┘  └────────────────┘  └──────────────────┘
          │                  │                  │
  ┌───────▼──────┐  ┌────────▼───────┐  ┌───────▼──────────┐
  │ Product Node │  │  Legal Node    │  │ Code Audit Node  │
  │ (Gemini)     │  │  (Gemini)      │  │ (Gemini)         │
  │              │  │                │  │                  │
  │ User engage. │  │ Contracts      │  │ CVEs & vulns     │
  │ Churn signals│  │ Compliance     │  │ Tech debt        │
  │ NPS & support│  │ Deadlines      │  │ Bus factor       │
  └──────────────┘  └────────────────┘  └──────────────────┘
          │                  │                  │
          └──────────────────▼──────────────────┘
                    ┌─────────────────────┐
                    │   Cascade Mapper    │
                    │   (deterministic)   │
                    │                    │
                    │ Traces anomalies   │
                    │ through cross-     │
                    │ domain dependency  │
                    │ graph              │
                    └──────────┬─────────┘
                               │
                    ┌──────────▼─────────┐
                    │   Briefing Node    │
                    │   (Gemini)         │
                    │                   │
                    │ Risk score 0–100  │
                    │ Top 3 cascades    │
                    │ Founder briefing  │
                    │ What-If mode      │
                    └───────────────────┘
```

### DEADPOOLState — the shared typed state

The entire graph communicates through a single `TypedDict` state object. This state is model-agnostic — it doesn't care whether the writing node used Gemini or GPT-4o-mini. The Pydantic schemas for anomalies, domain reports, and cascade chains are identical regardless of provider. This is what makes multi-provider orchestration seamless: the LangGraph state is the contract, not the model.

```python
class DEADPOOLState(TypedDict):
    anomalies: list[Anomaly]           # accumulates as nodes run
    domain_reports: dict[str, AgentReport]  # one per specialist
    corroboration_queue: list[str]     # domains to query next
    corroboration_results: dict        # entity-scoped corroboration outputs
    cascade_chains: list[CascadeChain]
    risk_score: float
    briefing: str
    iteration: int                     # guards against infinite corroboration loops
    whatif_params: dict | None         # None = live mode, dict = simulation mode
```

State is **append-only for anomalies** — LangGraph's reducer merges lists across parallel node executions without data loss. Every node reads the state it needs and writes only its own domain output. The Head Supervisor writes to `corroboration_queue` and `cascade_chains`. The Briefing Node writes the final `risk_score` and `briefing`.

### How the graph executes

```
START
  │
  ▼
[Initial Fan-Out via Send API]
  │  Head Supervisor dispatches Send(people_node, state)    → Gemini
  │                               Send(finance_node, state)  → GPT-4o-mini
  │                               Send(infra_node, state)    → Gemini
  │                               Send(product_node, state)  → Gemini
  │                               Send(legal_node, state)    → Gemini
  │                               Send(code_audit_node, state) → Gemini
  │  All six run in parallel threads (mixed-provider)
  │
  ▼
[Head Supervisor — first pass] (Gemini)
  │  Reads all six domain_reports from state
  │  NOTE: Finance report came from GPT-4o-mini, other five from Gemini
  │  Identifies high-severity anomalies and their cross_reference_hints
  │  Uses conditional edges to route to corroboration specialists
  │  Writes corroboration_queue to state
  │
  ▼
[Corroboration Pass — targeted specialist re-queries]
  │  Each corroboration node receives entity-scoped context in state
  │  If finance_node is in the queue → GPT-4o-mini handles it
  │  If any other node is in the queue → Gemini handles it
  │  Returns focused anomaly outputs appended to state.anomalies
  │
  ▼
[Head Supervisor — second pass] (Gemini)
  │  Cross-validates: raises severity for corroborated anomalies
  │  CROSS-PROVIDER SIGNAL: anomalies corroborated across Gemini + GPT-4o-mini
  │    get an additional confidence boost (model-family independence)
  │  Resolves conflicts: models scenarios forward
  │  Decides: iteration < 2 AND new corroboration needed?
  │    YES → conditional edge back to specific specialist nodes
  │    NO  → conditional edge to cascade_mapper_node
  │
  ▼
[Cascade Mapper Node] (deterministic — no LLM)
  │  Traces each validated anomaly through pre-built dependency graph
  │  Calculates conditional probabilities at each edge
  │  Prunes chains where cumulative probability < 0.25 threshold
  │  Writes cascade_chains to state
  │
  ▼
[Briefing Node] (Gemini)
  │  Ranks cascades by urgency formula
  │  Selects top 3
  │  Generates plain-language founder briefing
  │  Writes risk_score (0–100) and briefing to state
  │
  ▼
END
```

### Conditional routing — the intelligence layer

The Head Supervisor uses `add_conditional_edges` with a routing function that reads `state["corroboration_queue"]` and returns a list of target node names. LangGraph fans out to all targets in parallel — each target uses its own model provider. After corroboration, the routing function checks `state["iteration"]` to prevent infinite loops and returns `"cascade_mapper"` when corroboration is complete. This is not hardcoded — the routing function is Gemini reasoning over the accumulated anomaly evidence to decide which specialist to query next.

```python
def supervisor_router(state: DEADPOOLState) -> list[str]:
    if state["iteration"] >= 2 or not state["corroboration_queue"]:
        return ["cascade_mapper"]
    return state["corroboration_queue"]  # e.g. ["code_audit", "legal"]
```

### Cross-domain linking

Agents connect data through shared entity keys consistent across all data sources:

- `developer_name` links People ↔ Code Audit ↔ Infra (who owns what code and which services)
- `service_name` links Infra ↔ Code Audit ↔ Legal ↔ Product (runtime health to code quality to contract obligations to user experience)
- `client_name` links Finance ↔ Legal (revenue concentration to contract terms)
- `feature_name` links Infra ↔ Legal ↔ Product (delivery progress to deadlines to user engagement)

These keys are passed as entity context in the corroboration state so receiving nodes narrow their analysis to the specific cross-domain intersection — not a full domain re-scan. The entity keys work identically regardless of whether the receiving node runs Gemini or GPT-4o-mini.

---

## The six specialist agents

### People Agent *(Gemini 2.5 Flash)*
**Domain:** Team health, engagement, key-person risk.
**Data sources:** GitHub API (commit frequency, PR activity per developer), Slack API (message frequency, response times).
**Detects:** Commit drops exceeding 50% week-over-week, prolonged silence from key contributors, workload concentration on a single person, PR review bottlenecks.
**Cross-references:** Code Audit (which code areas are affected by the person's decline), Infra (which services the person owns), Finance (payroll cost and hiring pipeline impact).

### Finance Agent *(GPT-4o-mini — OpenAI)*
**Domain:** Cash flow, runway, revenue, funding terms.
**Data sources:** Three CSV files — `deadpool_finance_data.csv` (transaction ledger), `deadpool_revenue_pipeline.csv` (revenue, invoices, pipeline deals), `deadpool_funding_runway.csv` (investor terms, monthly summaries, runway scenarios).
**Why GPT-4o-mini:** The Finance Agent's workload is the most structured of all six agents: parsing CSV rows, computing arithmetic (monthly burn = total expenses − revenue, runway = cash / net burn), checking threshold conditions (runway < 6 months? revenue concentration > 40%?), and extracting specific clause terms from tabular data. GPT-4o-mini is exceptionally fast and accurate at structured data extraction and numerical reasoning — faster than Gemini for this specific workload, at a fraction of the cost. It also produces highly consistent JSON output, reducing parsing failures. Most importantly, having one agent on a different model family creates a **natural cross-validation signal** — when Finance (GPT-4o-mini) and Legal (Gemini) independently flag the same contract risk, the corroboration is model-independent.
**Detects:** Runway dropping below 6 months, revenue concentration exceeding 40% in a single client, burn rate acceleration, approaching investor clause thresholds, payment delays, pipeline deals at risk due to feature dependencies.
**Cross-references:** Legal (contract values and renewal dates), People (headcount cost impact), Product (health of revenue-driving features).

### Infra Agent *(Gemini 2.5 Flash)*
**Domain:** System reliability, deployment operations, performance.
**Data sources:** GitHub Actions API, health endpoint monitoring, UptimeRobot/BetterStack API, cloud cost tracking.
**Detects:** Deploy frequency drops, CI failure rate spikes, response time degradation, uptime approaching SLA breach thresholds, cloud cost anomalies.
**Cross-references:** Code Audit (are code quality issues causing the runtime failures?), People (who owns the degrading service and are they active?), Legal (SLA obligations at risk from the degradation).

### Product Agent *(Gemini 2.5 Flash)*
**Domain:** User engagement, retention, satisfaction.
**Data sources:** Plausible/PostHog API, support ticket data, NPS survey results.
**Detects:** Feature adoption decline, churn rate increases, NPS dropping below threshold, support ticket volume spikes, sentiment deterioration in customer communications.
**Cross-references:** Infra (is system performance driving the UX decline?), Code Audit (are bugs in the code causing the errors users see?), Finance (revenue impact of the churn trend).

### Legal Agent *(Gemini 2.5 Flash)*
**Domain:** Contracts, compliance, intellectual property, regulatory exposure.
**Data sources:** Uploaded contract PDFs parsed for key clauses, Federal Register API, SEC EDGAR.
**Detects:** Contract deadlines approaching with delivery at risk, conflicting terms across multiple agreements, regulatory changes requiring compliance action, IP exposure from open-source license conflicts.
**Cross-references:** Finance (financial impact of contract breach including refund liabilities), Infra (delivery progress on features tied to contractual obligations), Code Audit (compliance requirements like PCI DSS and SOC 2 mapped to actual code state).

### Code Audit Agent *(Gemini 2.5 Flash)*
**Domain:** Codebase health, security posture, architectural integrity, technical debt.
**Data sources:** GitHub API (file change frequency, code ownership via git blame, PR merge patterns), dependency scanning (package.json/requirements.txt parsed against CVE databases), static analysis signals (test coverage, cyclomatic complexity, code duplication ratio).
**Detects:** Critical dependency vulnerabilities with CVSS score 7.0 or above, test coverage dropping below 60% for critical services, bus factor of 1 for any critical service, pull requests merged without review in critical paths, circular dependencies, missing error handling in payment and authentication code paths, dependencies more than 2 major versions behind.
**Cross-references:** People (who wrote and owns the problematic code?), Infra (which running services sit on top of the vulnerable code?), Legal (compliance implications of unpatched vulnerabilities), Product (which user-facing features are built on the degraded code?).

---

## The Head Supervisor Node *(Gemini 2.5 Flash)*

The Head Supervisor is the brain of DEADPOOL. It does not monitor data directly. It orchestrates, arbitrates, and synthesizes — and it does so through LangGraph's graph execution model rather than through imperative control flow.

**Cross-validation via conditional edges:** After the initial parallel fan-out, the Head Supervisor reads all six domain reports from state — five from Gemini nodes, one from the GPT-4o-mini Finance node — identifies high-severity anomalies with `cross_reference_hints`, and uses conditional edges to route back to specific corroboration nodes. An anomaly confirmed by multiple agents gets its severity raised. An anomaly contradicted gets downgraded. When corroboration crosses the Gemini/GPT-4o-mini boundary (e.g., Legal → Finance or Finance → Legal), a successful cross-validation carries extra weight because it's model-family-independent.

**Conflict resolution via forward scenario modeling:** When agents return contradictory signals, the supervisor does not average them or discard one. It models the scenario forward using Gemini to determine which signal dominates. Example: The GPT-4o-mini Finance Agent reports healthy runway (9.4 months). The Gemini Legal Agent flags imminent contract breach risk. The supervisor reasons: *"Finance's runway figure was computed without the conditional revenue loss. Legal's breach is upstream — if the contract terminates, Finance's inputs change. Recalculate Finance under Legal's scenario."* It routes a conditional query to the GPT-4o-mini Finance node with the breach scenario injected into state. The Finance node re-runs its structured calculation with the new assumptions and returns runway = 2.5 months. Legal dominates. The resolution is documented in state.

**Cascade ranking:** When multiple cascade chains are active simultaneously, the Head Supervisor ranks them using the urgency formula:

```
urgency = (1 / time_to_impact_days) × severity × (1 - reversibility)
```

Only the top three cascades are surfaced to the founder. Information overload is itself a risk.

**Founder briefing:** The Head Supervisor produces a 3–5 sentence plain-language briefing that names the risk, states the timeline, and recommends one specific action. No jargon. No dashboards full of numbers. One clear message.

**LangGraph checkpointing:** The compiled graph uses `MemorySaver` as its checkpointer. Every graph execution is persisted by `thread_id`. Across monitoring cycles the supervisor reads prior checkpoint state — which cascade links materialized, which cross-domain signals proved reliable — and uses this history to adjust baseline probabilities in the cascade dependency graph. The system compounds: routing decisions improve as the supervisor builds a model of which signals are predictive for this specific company.

---

## The Cascade Mapper *(deterministic — no LLM)*

The cascade mapper traces anomalies forward through a pre-built dependency graph of cross-domain causal relationships. It runs as a dedicated LangGraph node after the Head Supervisor has completed corroboration. It uses no LLM — it's pure graph traversal (NetworkX BFS with probability multiplication). This is intentional: the cascade mapper should be deterministic and fast, with no model variance.

### How it works

1. The Head Supervisor writes validated anomalies to state and routes to `cascade_mapper_node`.
2. The mapper reads `state["anomalies"]`, selects the cascade path for each anomaly using `TRIGGER_MAP` keyword matching.
3. For each path, it multiplies conditional probabilities edge-by-edge, pruning branches where cumulative probability drops below 0.25.
4. The mapper writes all active `CascadeChain` objects to `state["cascade_chains"]`.
5. The graph continues to `briefing_node`.

### Pre-built cascade paths

The MVP ships with six pre-seeded cascade paths encoding the most common startup failure patterns:

1. **Key-person departure → code ownership gap → code quality degradation → delivery delays → contract breach → revenue loss → runway crisis.** The primary demo cascade. Five agent domains, six nodes, dramatic legible story on stage.

2. **Critical CVE in dependency → compliance breach → legal exposure → investor confidence loss → funding risk.** Starts with Code Audit, shows how a technical vulnerability cascades into an existential business threat.

3. **Test coverage decline → undetected bugs shipped → user-facing errors → churn spike → revenue drop.** Connects Code Audit to Product to Finance.

4. **Technical debt accumulation → deploy velocity drop → feature delivery failure → competitive loss.** Architectural rot slows the entire company.

5. **Client revenue concentration → single client churn → revenue cliff → down-round trigger.** Pure finance-legal cascade every seed-stage founder recognizes immediately.

6. **Infrastructure degradation → SLA breach → contract penalty → burn rate spike → runway compression.** Operational issues compounding into financial damage through contractual mechanisms.

Each path is encoded as nodes and edges with baseline conditional probabilities. The Head Supervisor adjusts these probabilities in real-time based on corroborated specialist outputs written into state.

---

## Features

### Dashboard — cascade map

The primary interface is a full-width directed graph showing all active cascade chains. Nodes are color-coded by agent domain: blue for People, green for Finance, orange for Infra, purple for Product, red for Legal, cyan for Code Audit. **Finance nodes have a subtle OpenAI badge indicating the cross-provider agent.** Edge thickness encodes probability. Active cascades animate with a pulse traveling along the chain from trigger to end-state. Clicking any node expands it to show the specialist agent's raw evidence, the model that generated it (Gemini or GPT-4o-mini), and the Head Supervisor's corroboration notes from the LangGraph state.

### Risk score and founder briefing

A single number from 0 to 100 sits at the top of the dashboard with a color indicator shifting from green through yellow and orange to red. A trend arrow shows whether risk is increasing, stable, or decreasing. Below the score, the Head Supervisor's latest briefing appears as a 2–3 sentence plain-language summary. A "top action" button shows the single most important thing the founder should do right now.

### Head Supervisor activity log

A scrollable log showing every conditional edge decision the Head Supervisor made. Entries show which specialist flagged what, which model provider generated the finding, which other specialists were routed to for corroboration, whether the anomaly was confirmed or contradicted, and how severity was adjusted. **Cross-provider corroborations are highlighted** — when a Gemini agent and the GPT-4o-mini Finance agent independently agree, the log marks this as a "model-independent corroboration." When agents disagree, the log shows the supervisor's reasoning for which signal it trusted — all pulled directly from `DEADPOOLState`.

### "What If" simulation mode

A toggle switches the dashboard into simulation mode. Sliders appear for key scenario variables: "Key engineer leaves," "Biggest client churns," "Critical CVE discovered," "Cloud costs double." As sliders move, the compiled LangGraph is invoked with `whatif_params` set in state, causing the Head Supervisor to modulate anomaly severities before cascade mapping. The graph produces a new briefing and risk score for the simulated state — re-running the GPT-4o-mini Finance node with modified assumptions and the Gemini nodes with modified context. The dashboard shows a side-by-side comparison.

### Alert system

When a new cascade chain is detected or an existing chain's probability crosses a severity threshold, a toast notification appears with the Head Supervisor's summary. The cascade chain highlights and animates on the graph. An alert log stores all historical alerts with timestamps and full chain details, sourced from LangGraph checkpoint history.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React + D3.js | D3 handles the dependency graph rendering with animated edges and interactive nodes. React manages dashboard state, panels, and real-time updates. |
| Backend | Python + FastAPI | Async-native, Pydantic v2 for type-safe agent I/O, minimal boilerplate. Handles the LangGraph execution loop, signal bus event queue, and SSE streaming. |
| AI orchestration | **LangGraph** + **Google Gemini 2.5 Flash** + **OpenAI GPT-4o-mini** | `StateGraph` with typed `DEADPOOLState`, `add_conditional_edges` for dynamic supervisor routing, `Send` API for parallel specialist fan-out (mixed-provider), `MemorySaver` checkpointer for cross-cycle memory. LangGraph's model-agnostic node architecture makes multi-provider orchestration seamless — each node is a function that can call any model. |
| Gemini integration | `google-genai` Python SDK | Used by 5 specialist nodes + Head Supervisor + Briefing Node. Structured output via Gemini's JSON mode ensures Pydantic-compatible responses. |
| OpenAI integration | `openai` Python SDK | Used by Finance Agent only. `response_format={"type": "json_object"}` for structured output. GPT-4o-mini's speed (~300ms for structured extraction) keeps the Finance node from being the bottleneck in parallel fan-out. |
| LangGraph observability | LangSmith (optional) | Traces every node execution, edge routing decision, state transition, and which model provider each node used. |
| Data ingestion | JSON synthetic data files (hackathon), GitHub REST API, CSV upload for financials, pip-audit output for dependency scanning | Covers all six specialist agents with minimal integration overhead. |
| Real-time updates | Server-Sent Events (SSE) via sse-starlette | Pushes cascade updates, Head Supervisor briefings, and risk score changes to the dashboard without client-side polling. |
| Deployment | Vercel (frontend) + Railway (backend) | Free tiers, deploy in under 5 minutes, sufficient for hackathon demo traffic. |

---

## Agent implementation

### LangGraph architecture with multi-provider nodes

DEADPOOL runs as a **compiled LangGraph `StateGraph`**. Every agent is a pure Python function (a LangGraph node) that accepts `DEADPOOLState` and returns a state delta. The key architectural decision: **each node owns its own model client**. The LangGraph framework doesn't care which model a node calls — it only cares about the state delta returned. This makes multi-provider orchestration a configuration choice, not an architectural change.

```python
import google.genai as genai
from openai import OpenAI

# Model clients — initialized once, used by their respective nodes
gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Graph construction
workflow = StateGraph(DEADPOOLState)

# Register nodes — each node knows its own model
workflow.add_node("people", people_node)          # → Gemini
workflow.add_node("finance", finance_node)        # → GPT-4o-mini
workflow.add_node("infra", infra_node)            # → Gemini
workflow.add_node("product", product_node)        # → Gemini
workflow.add_node("legal", legal_node)            # → Gemini
workflow.add_node("code_audit", code_audit_node)  # → Gemini
workflow.add_node("head_supervisor", head_supervisor_node)  # → Gemini
workflow.add_node("cascade_mapper", cascade_mapper_node)    # → deterministic
workflow.add_node("briefing", briefing_node)      # → Gemini

# Initial fan-out via Send API (parallel execution, mixed providers)
workflow.add_conditional_edges(START, initial_fanout)

# Specialist nodes always return to head supervisor
for specialist in ["people", "finance", "infra", "product", "legal", "code_audit"]:
    workflow.add_edge(specialist, "head_supervisor")

# Head supervisor uses conditional routing to corroborate or proceed
workflow.add_conditional_edges("head_supervisor", supervisor_router)
workflow.add_edge("cascade_mapper", "briefing")
workflow.add_edge("briefing", END)

# Compile with memory checkpointing
app = workflow.compile(checkpointer=MemorySaver())
```

### Specialist node structure (Gemini-powered)

Five of six specialist nodes follow this pattern using the Google GenAI SDK:

```python
def people_node(state: DEADPOOLState) -> dict:
    """People Agent — runs on Gemini 2.5 Flash."""
    # Load domain data
    data = load_json("team_activity.json")

    # Check if this is a corroboration re-query (entity-scoped)
    entity_context = get_entity_context(state, "people")

    # Build prompt with domain data + entity context
    prompt = build_people_prompt(data, entity_context)

    # Call Gemini with structured output
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AgentReport  # Pydantic model
        )
    )

    report = AgentReport.model_validate_json(response.text)

    return {
        "anomalies": report.anomalies,  # list-append reducer
        "domain_reports": {"people": report}
    }
```

### Finance node (GPT-4o-mini — the cross-provider agent)

The Finance Agent is the only node running on OpenAI. Its implementation uses the OpenAI SDK with JSON mode:

```python
def finance_node(state: DEADPOOLState) -> dict:
    """Finance Agent — runs on GPT-4o-mini (OpenAI).

    Deliberately on a different model family from the other five agents.
    Creates cross-provider corroboration signal when Finance findings
    are validated by Gemini-powered agents (or vice versa).
    """
    # Load all three CSV files
    transactions = load_csv("deadpool_finance_data.csv")
    pipeline = load_csv("deadpool_revenue_pipeline.csv")
    funding = load_csv("deadpool_funding_runway.csv")

    # Check if this is a corroboration re-query or scenario simulation
    entity_context = get_entity_context(state, "finance")
    whatif = state.get("whatif_params")

    # Build prompt with financial data + context
    prompt = build_finance_prompt(transactions, pipeline, funding,
                                  entity_context, whatif)

    # Call GPT-4o-mini with structured JSON output
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1  # Low temp for numerical precision
    )

    report = AgentReport.model_validate_json(
        response.choices[0].message.content
    )

    # Tag the report with its model provider for cross-validation tracking
    report.model_provider = "openai/gpt-4o-mini"

    return {
        "anomalies": report.anomalies,
        "domain_reports": {"finance": report}
    }
```

### Head Supervisor node structure (Gemini)

```python
def head_supervisor_node(state: DEADPOOLState) -> dict:
    """Head Supervisor — runs on Gemini 2.5 Flash.

    Reads all six domain reports (5 from Gemini, 1 from GPT-4o-mini).
    Reasons about cross-domain implications.
    Produces routing decisions for corroboration.
    """
    all_reports = state["domain_reports"]
    all_anomalies = state["anomalies"]
    iteration = state.get("iteration", 0)

    # Build supervisor prompt with all evidence
    # Explicitly notes which model produced each report
    prompt = build_supervisor_prompt(all_reports, all_anomalies, iteration)

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SupervisorDecision
        )
    )

    decision = SupervisorDecision.model_validate_json(response.text)

    return {
        "corroboration_queue": decision.corroboration_targets,
        "iteration": iteration + 1,
        "anomalies": decision.updated_anomalies  # severity adjustments
    }
```

### Agent interaction and delegation flow

```
[1] START → initial_fanout dispatches Send() to all six specialist nodes
    Five nodes call Gemini 2.5 Flash in parallel
    One node (Finance) calls GPT-4o-mini in parallel
    All six run concurrently

[2] Specialists write domain_reports and anomalies to DEADPOOLState
    Each anomaly carries: severity, confidence, affected_entities,
    cross_reference_hints, model_provider

[3] Head Supervisor (Gemini) reads state, reasons:
    "People node (Gemini) flagged sarah_chen, severity=0.85.
     cross_reference_hints: ['payments-service', 'code_ownership'].
     → corroboration_queue = ['code_audit']
     → corroboration context: {developer_name: 'sarah_chen',
                                service: 'payments-service'}"

[4] Code Audit node (Gemini) receives targeted re-query
    Reads entity context from state, returns focused output:
    CVE confirmed, bus_factor=1, coverage=61%
    cross_reference_hints: ['nexus_corp_contract', 'pci_compliance']

[5] Head Supervisor (Gemini) reads updated state:
    "CVE in payments-service + contract hint.
     → corroboration_queue = ['legal', 'finance']
     → context: {service: 'payments-service', contract: 'nexus_corp'}"

[6] Legal node (Gemini) returns: breach_risk=high, refund=$211,680
    Finance node (GPT-4o-mini) returns: nexus_corp=42% revenue,
      post-loss runway=2.5mo, investor clause triggers

    *** CROSS-PROVIDER CORROBORATION: Legal (Gemini) and Finance (GPT-4o-mini)
    *** independently flag the same contract risk from different data sources
    *** and different model families. Head Supervisor notes this in state.

[7] Head Supervisor (Gemini) reads state:
    iteration=2 → conditional edge routes to cascade_mapper

[8] Cascade Mapper (deterministic) traces:
    People → Code Audit → Legal → Finance → Finance(investor)
    Multiplies probabilities, writes CascadeChain to state

[9] Briefing Node (Gemini) scores urgency, generates founder briefing
    Writes risk_score and briefing to state → END
```

### Conflict resolution between agents (cross-provider)

When two specialists return contradictory signals, the supervisor does not average them or discard one. It models the scenario forward to determine which signal dominates. The most interesting case is when the contradiction crosses the model boundary:

**Example:** The GPT-4o-mini Finance Agent reports healthy runway (9.4 months). The Gemini Legal Agent flags imminent contract breach risk. The Gemini Head Supervisor reasons: *"Finance (GPT-4o-mini) computed runway without the conditional revenue loss that Legal (Gemini) is flagging. These are from different models analyzing different data sources — neither is echoing the other. Legal's breach scenario is conditionally upstream. Recalculate Finance under Legal's breach scenario."* It routes to the GPT-4o-mini Finance node with the breach scenario injected. Finance re-runs and returns runway = 2.5 months. Legal dominates. The cross-provider disagreement-then-resolution is documented in state and visible in the activity log — demonstrating genuine reasoning, not model agreement by default.

### LangGraph memory and persistence

The compiled graph uses `MemorySaver` with a `thread_id` per company. Every execution checkpoint is persisted. The Head Supervisor reads prior checkpoint state at startup — specifically, which cascade links fired in previous cycles and which cross-domain anomaly correlations proved predictive. This is not LLM fine-tuning; it is structured state compounding over time, accumulated in the checkpointer and read into the supervisor's reasoning prompt at each cycle.

---

## Data architecture

### Synthetic data strategy

For the hackathon demo, we use carefully constructed synthetic data representing a realistic seed-stage SaaS startup over 12 weeks. The data is designed so that agents genuinely discover cascade chains from the data — they are not told what to find.

Six JSON data files, one per specialist agent domain, plus three CSV files for the Finance Agent:

- **team_activity.json** — 12 developers with weekly commit, PR, and response time data. One developer (the cascade trigger) shows a gradual five-week disengagement pattern. Eleven developers show normal patterns with realistic noise.

- **deadpool_finance_data.csv** — Transaction-level ledger from Sep 2025 through Mar 2026. Every income event and every expense with running balance. This is the primary input for the GPT-4o-mini Finance Agent.

- **deadpool_revenue_pipeline.csv** — Revenue actuals, accounts receivable, and pipeline deals with probabilities and feature dependencies. The critical Nexus Corp enterprise deal ($423K/year) depends on Payments API v2.

- **deadpool_funding_runway.csv** — Funding round details, investor clause terms (down-round trigger at runway < 3 months), monthly summaries, and runway scenario projections.

- **infrastructure.json** — 6 microservices with weekly deploy counts, uptime percentages, response times, error rates, and cloud costs. The payments service degrades in correlation with the lead engineer's decline.

- **product_metrics.json** — Weekly active users, feature-level engagement data, support ticket volume and sentiment, NPS scores, and churn rates.

- **contracts.json** — 4 client contracts with delivery deadlines and SLA guarantees. One investor agreement with a down-round clause. PCI DSS compliance obligation linked to the payments service.

- **codebase_audit.json** — Repository-level analysis including file change frequency, code ownership maps, dependency vulnerability scan results, test coverage per service, PR review patterns.

All files share consistent entity linking keys: developer names, service names, client names, and feature names are identical across files so the Head Supervisor and cascade mapper can trace connections through `DEADPOOLState`.

### Cross-reference linking keys

| Key | Connects |
|-----|----------|
| `developer_name` | People ↔ Code Audit ↔ Infra |
| `service_name` | Infra ↔ Code Audit ↔ Legal ↔ Product |
| `client_name` | Finance ↔ Legal |
| `feature_name` | Infra ↔ Legal ↔ Product |

---

## Cascade demonstration

### Primary demo cascade (5 agents, 6 nodes, 2 model providers)

This is the cascade we demonstrate on stage. It passes through People → Code Audit → Infra → Legal → Finance → Finance (investor terms). Critically, the final two nodes involve the **GPT-4o-mini Finance Agent** corroborating findings from **Gemini-powered** upstream agents — demonstrating cross-provider cascade tracing.

```
Step 1 │ PEOPLE NODE detects (Gemini)
       │ Sarah Chen commit activity dropped 94% over 5 weeks
       │ Severity: 0.85 → Head Supervisor validates to 0.91
       │ (Code Audit corroboration confirms: 0 code reviews in 14 days)
       │
       ▼ Conditional probability: 0.78
       │
Step 2 │ CODE AUDIT NODE confirms (Gemini)
       │ payments-service: bus factor = 1, test coverage dropped to 61%,
       │ unpatched CVE-2026-4821 (CVSS 8.1) in payment processing dependency
       │ Severity: 0.82
       │
       ▼ Conditional probability: 0.72
       │
Step 3 │ INFRA NODE reports (Gemini)
       │ payments-service deploy frequency: 0 in last 2 weeks
       │ Payments API v2 at 34% completion, deadline in 18 days
       │ Projected miss: 30+ days overdue
       │ Severity: 0.79
       │
       ▼ Conditional probability: 0.58
       │
Step 4 │ LEGAL NODE flags (Gemini)
       │ Nexus Corp contract Section 4.2: delivery of Payments API v2
       │ required by April 15, 2026. Breach = termination without penalty.
       │ Refund liability: $211,680
       │ Severity: 0.88
       │
       ▼ Conditional probability: 0.65
       │
Step 5 │ FINANCE NODE calculates (GPT-4o-mini ← cross-provider!)
       │ Nexus Corp = 42% of revenue ($35,280/month)
       │ Post-loss monthly burn: $80,000 net negative
       │ After refund: cash drops to ~$200,000
       │ Runway: 2.5 months
       │ Severity: 0.92
       │
       │ *** MODEL-INDEPENDENT CORROBORATION: Legal (Gemini) flagged the
       │ *** contract risk. Finance (GPT-4o-mini) independently calculated
       │ *** the revenue impact from separate CSV data. Two model families,
       │ *** two data sources, same conclusion. High-confidence finding.
       │
       ▼ Conditional probability: 0.75
       │
Step 6 │ FINANCE NODE (investor terms) triggers (GPT-4o-mini)
       │ Down-round clause activates below 3-month runway
       │ Investor converts at 50% discount with 2x liquidation preference
       │ Founder diluted below control threshold
       │ END STATE: Company effectively lost
       │
       │ Overall cascade probability: 0.19
       │ Time to impact: 75 days
       │ Financial impact: $1.9M+
```

**Head Supervisor briefing for this cascade:**

> "Your lead backend engineer has been disengaging for five weeks, and she's the only person who can ship the payments feature that Nexus Corp's contract requires by April 15. The Code Audit node found an unpatched critical vulnerability in the same service. If the deadline is missed, Nexus Corp can walk — taking 42% of your revenue with them. That drops your runway below three months and triggers the down-round clause in your investor agreement. Talk to Sarah Chen today. Start a knowledge transfer to a backup engineer this week. Contact Nexus Corp about a deadline extension before April 1."

---

## Market awareness and competitive landscape

| Tool | What it does | Why it's insufficient |
|------|-------------|----------------------|
| GitHub Insights / LinearB | Engineering metrics only | No cross-domain synthesis; finance and legal blind spots |
| ChartMogul / Baremetrics | Revenue dashboards | No causal link to engineering or legal triggers |
| Notion / Linear | Task and project tracking | Passive; requires human to connect the dots |
| Traditional BI (Looker, Metabase) | Aggregated reporting | Descriptive, not predictive; no agent reasoning |

**DEADPOOL's position:** No current tool performs cross-domain causal reasoning across people + finance + infra + product + legal + code simultaneously. The category does not exist yet. DEADPOOL creates it by treating company operations as a graph traversal problem — which is exactly what LangGraph is built for.

---

## Quantified user impact

### Total addressable market

There are approximately **34,000 venture-backed startups** between seed and Series B in the US at any given time (PitchBook 2025). Globally the figure is roughly 80,000. These are companies with 5–50 employees, $500K–$20M raised, and exactly the cross-domain blind spot DEADPOOL addresses. At a projected price point of $500/month (positioning below a fractional COO at $5K–$10K/month but above commodity dashboards at $50–$100/month), the serviceable addressable market is **$204M annually** in the US alone.

### The cost of a missed cascade

Startup post-mortems consistently cite chain reactions — not single events — as the cause of death. We quantified the average cost using data from the CB Insights top 20 failure reasons, Carta's startup mortality data, and our own cascade modeling:

| Cascade type | Avg financial impact | Avg time from first signal to company-ending event | Detection window (if caught early) |
|-------------|---------------------|---------------------------------------------------|------------------------------------|
| Key-person departure → delivery failure → contract breach | **$1.2M–$2.4M** (lost revenue + investor dilution) | 60–120 days | 2–4 weeks after first commit drop |
| CVE in dependency → compliance breach → client termination | **$400K–$900K** (penalties + lost contracts) | 30–90 days | Immediately on CVE publication |
| Revenue concentration → single client churn → runway crisis | **$800K–$3M** (runway collapse + forced down-round) | 45–90 days | Continuous monitoring flags at 40% threshold |
| Tech debt → deploy velocity collapse → competitive loss | **$500K–$1.5M** (opportunity cost + delayed fundraise) | 90–180 days | Weeks before velocity hits critical threshold |

**The average seed-stage startup that dies from a missed cascade loses $1.4M in combined direct financial impact and opportunity cost.** DEADPOOL at $500/month costs $6K/year. The ROI of catching a single cascade is **230x**.

### Time-to-insight comparison

| Method | Time to connect cross-domain signals | Coverage |
|--------|--------------------------------------|----------|
| **Founder intuition** (status quo) | Weeks to never — depends on whether the founder happens to check the right dashboard on the right day | Partial. No human monitors GitHub commits, contract deadlines, and investor clause thresholds simultaneously. |
| **Weekly team standups** | 7 days minimum latency. Information is filtered, summarized, and often deprioritized before reaching the founder. | Depends entirely on what team members choose to escalate. Cross-domain connections are almost never surfaced. |
| **Board meetings** (monthly/quarterly) | 30–90 day latency. Retrospective by definition. | High-level only. A board doesn't see a 60% commit drop in a payments engineer. |
| **DEADPOOL** | **< 60 seconds** from data ingestion to cascade chain with cross-validated probabilities and a plain-language founder briefing. | All six domains monitored simultaneously. Cross-domain links traced automatically through the dependency graph. |

DEADPOOL compresses the time from "signal visible somewhere in the company" to "founder has an actionable briefing with quantified risk" from **weeks-to-never down to under a minute**. For a seed-stage company burning $50K–$100K per month, every week of earlier detection is worth $12K–$25K in runway preserved.

### Hackathon traction targets

| Metric | Target | Why it matters |
|--------|--------|---------------|
| Landing page signups | 50+ | Founders who want their DEADPOOL score — direct demand signal |
| LinkedIn post impressions | 5,000+ | "How your startup dies" framing — category awareness |
| Email list from signups | 30+ .edu or company domains | Filters out curiosity clicks; indicates genuine ICP interest |
| Demo day audience "would use this" hand-raise | 40%+ of room | Live PMF signal |

---

## Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LangGraph conditional routing produces infinite corroboration loops | Medium | High — system hangs | `iteration` counter in state; max 2 corroboration passes |
| Gemini returns malformed JSON from specialist nodes | Medium | Medium — node fails | Pydantic parsing with fallback to empty anomaly list |
| GPT-4o-mini Finance node fails or times out | Low | High — breaks cross-provider narrative | Finance node has 10s timeout; fallback: inject last-known Finance report from checkpoint |
| Gemini and GPT-4o-mini produce incompatible anomaly schemas | Low | High — state corruption | All nodes output to identical Pydantic `Anomaly` schema; validated before state write |
| OpenAI API rate limit hit during demo | Low | Medium | GPT-4o-mini is only called 1-2 times per graph invocation; well within rate limits |
| LangGraph state shape mismatch across providers | Low | High — demo broken | TypedDict with explicit `Annotated[list, operator.add]` reducers; unit-tested |
| Synthetic data triggers no anomalies | Low | High — empty demo | Data engineered to produce anomalies; fallback: inject severity floor of 0.5 for demo |

**Contingency plan:** If GPT-4o-mini has unexpected issues, the Finance node can hot-swap to Gemini with a single environment variable change (`FINANCE_PROVIDER=gemini`). The node function checks this variable and routes to the appropriate client. The multi-provider narrative is a feature, not a hard dependency.

---

## Scalability design

The hackathon demo runs on `MemorySaver` (in-memory checkpointer) with a single `thread_id`. But DEADPOOL's architecture is designed to scale to production multi-tenant deployment with zero structural changes to the LangGraph graph — only the infrastructure layer swaps out.

### PostgresSaver — production checkpointer

LangGraph's checkpointer interface is pluggable. Replacing `MemorySaver` with `PostgresSaver` (from `langgraph-checkpoint-postgres`) requires changing exactly one line:

```python
# Hackathon
app = workflow.compile(checkpointer=MemorySaver())

# Production
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
pool = AsyncConnectionPool(conninfo=os.environ["DATABASE_URL"])
app = workflow.compile(checkpointer=AsyncPostgresSaver(pool))
```

Every graph execution checkpoint — specialist outputs, corroboration results, cascade chains, Head Supervisor reasoning, risk scores — is persisted to PostgreSQL. This gives us durable cross-cycle memory, crash recovery (a graph can resume from its last checkpoint if a node fails mid-execution), and full audit history queryable via SQL.

### Multi-tenant isolation via `thread_id`

Each company that uses DEADPOOL gets a unique `thread_id` passed to every `app.invoke()` call. LangGraph's checkpointer scopes all state to that thread. This means:

- **Company A's cascade history never leaks into Company B's.** The Head Supervisor reads only its own company's prior checkpoints when adjusting baseline probabilities.
- **Each company's dependency graph evolves independently.** When Company A's Head Supervisor proposes a new graph edge (human-approved), it only affects Company A's cascade paths.
- **Concurrent graph executions for different companies are fully isolated.** LangGraph handles this natively through the checkpointer's thread-scoped state.

```python
# Company A's monitoring cycle
result_a = await app.ainvoke(
    initial_state,
    config={"configurable": {"thread_id": "company-acme-001"}}
)

# Company B's monitoring cycle (concurrent, isolated)
result_b = await app.ainvoke(
    initial_state,
    config={"configurable": {"thread_id": "company-nova-002"}}
)
```

In production, `thread_id` maps to a company ID in the application database. The LangGraph graph itself is compiled once and shared across all tenants — only the state and checkpoints are tenant-scoped.

### Horizontal scaling of specialist nodes

The current architecture runs all six specialist nodes in parallel via LangGraph's `Send` API within a single process. For production scale (hundreds of concurrent companies), specialist nodes can be extracted to independent worker processes:

**Phase 1 — Hackathon (current):** All nodes run in-process. `Send` API dispatches to `asyncio` coroutines. Fast, simple, sufficient for demo.

**Phase 2 — Early production (10–50 companies):** Specialist nodes run as **FastAPI microservices** behind a load balancer. The LangGraph node functions become thin HTTP clients that call the specialist service and return the response as a state delta. The graph structure doesn't change — only the node implementation swaps from "call Gemini directly" to "call specialist-service/people endpoint which calls Gemini."

```python
# Hackathon: node calls Gemini directly
def people_node(state: DEADPOOLState) -> dict:
    response = gemini_client.models.generate_content(...)
    return {"anomalies": parse(response), "domain_reports": {"people": report}}

# Production: node calls specialist microservice
async def people_node(state: DEADPOOLState) -> dict:
    response = await httpx.post("https://people-service.internal/analyze",
                                 json=state_to_request(state))
    return response.json()  # Same state delta shape
```

**Phase 3 — Scale (100+ companies):** Specialist services autoscale horizontally (Kubernetes HPA on request queue depth). The Finance service (GPT-4o-mini) and Gemini-powered services scale independently based on their respective API rate limits and latency profiles. The Head Supervisor remains a single logical node per graph execution but can run on dedicated compute.

### Cost modeling at scale

| Scale | Companies | Graph invocations/day | Gemini calls/day | GPT-4o-mini calls/day | Est. daily API cost | PostgreSQL cost |
|-------|-----------|----------------------|------------------|-----------------------|--------------------|-----------------| 
| Hackathon | 1 (demo) | 5–10 | 50–100 | 5–10 | ~$0.50 | $0 (MemorySaver) |
| Early production | 50 | 500 | 5,000 | 500 | ~$25 | $15/mo (managed Postgres) |
| Growth | 500 | 5,000 | 50,000 | 5,000 | ~$200 | $50/mo |
| Scale | 5,000 | 50,000 | 500,000 | 50,000 | ~$1,800 | $200/mo |

At 5,000 companies paying $500/month ($2.5M MRR), daily API cost is ~$1,800 ($54K/month) — a **2.2% cost-of-revenue**, well within SaaS norms. The GPT-4o-mini Finance node is ~10x cheaper per call than the Gemini nodes, so the cross-provider architecture is actually more cost-efficient than running all nodes on a single premium model.

### What this means for the hackathon

We don't build any of this during the hackathon. We build the single-tenant, `MemorySaver`, in-process version that demonstrates the full cascade detection pipeline. But the architecture is designed so that every production scaling step is a configuration change, not a rewrite:

- `MemorySaver` → `PostgresSaver`: one-line swap
- Single-tenant → multi-tenant: add `thread_id` to `invoke()` config
- In-process nodes → microservices: swap node function body from direct API call to HTTP client
- Single instance → horizontal scale: standard container orchestration

The judges should see that this isn't a hackathon toy that needs to be rewritten for production. The LangGraph `StateGraph` compiles identically at demo scale and production scale. The graph is the architecture. The infrastructure is pluggable.

---

## Execution plan

### Day 1 — Build the engine (12:00 PM – midnight)

**12:00 – 1:00 PM:** Repository setup, project scaffold (React + FastAPI), deployment pipeline, `DEADPOOLState` TypedDict definition, shared entity linking key constants. Install both `google-genai` and `openai` SDKs. Verify both API keys work with a test call.

**1:00 – 3:00 PM (parallel tracks):**
- Dev 1: People Node (Gemini) + Finance Node (GPT-4o-mini) — data loaders, prompt engineering for both providers, structured output parsing (Gemini JSON mode + OpenAI JSON mode), state write patterns. Verify both produce identical `AgentReport` Pydantic schemas.
- Dev 2: Infra Node (Gemini) + Code Audit Node (Gemini) — GitHub API integration, dependency scanning, CVE cross-referencing, state reducers.
- Dev 3: Dashboard scaffold — React layout, D3 graph component, Head Supervisor briefing panel, risk score display. Add provider badge to node display.

**3:00 – 5:00 PM (parallel tracks):**
- Dev 1: Product Node (Gemini) + Legal Node (Gemini) — analytics data parsing, contract clause extraction, Pydantic anomaly schema.
- Dev 2: Head Supervisor node (Gemini) — LangGraph `StateGraph` construction, `add_conditional_edges`, `supervisor_router` function, corroboration loop with iteration guard. Cross-provider corroboration detection logic.
- Dev 3: Signal bus + cascade mapper node (deterministic) + LangGraph graph compilation with `MemorySaver`.

**5:00 – 7:00 PM:** Full team integration sprint. Wire all six specialist nodes → Head Supervisor → cascade mapper → briefing node. Compile the graph. First end-to-end `app.invoke()` test. Verify Gemini and GPT-4o-mini outputs both parse correctly into `DEADPOOLState`. Test cross-provider corroboration flow (Legal → Finance).

**7:00 – 8:00 PM:** Dinner.

**8:00 PM – midnight:** Testing, debugging, first live cascade detection. Verify cross-provider corroboration produces the model-independent signal in the activity log. Verify LangGraph checkpoint persists across runs. Fix edge cases. SSE streaming from FastAPI to React.

### Day 2 — Polish and demo hardening (9:00 AM – 2:30 PM)

**9:00 – 10:30 AM:**
- Dev 1: "What If" simulation mode — inject `whatif_params` into state, re-invoke graph (both providers re-run with modified assumptions).
- Dev 2: Head Supervisor activity log UI — visualize conditional edge decisions, cross-provider corroboration highlights, and conflict resolution reasoning.
- Dev 3: Landing page for signups + graph execution visualization showing which model powers each node.

**10:30 AM – 12:00 PM:**
- Dev 1 + Dev 2: Cascade animation polish, alert system, live node execution flow showing Gemini vs GPT-4o-mini processing.
- Dev 3: Drive signups — post on LinkedIn/Twitter with cascade demo GIF.

**12:00 – 1:30 PM:** Demo rehearsal ×3. Practice explaining the cross-provider narrative. Prepare for: "Why not use the same model for everything?" Answer: "Model-independent corroboration. When two different model families analyzing different data sources reach the same conclusion, that's a stronger signal than one model agreeing with itself."

**1:30 – 2:30 PM:** Final polish. Freeze code. Verify both API keys are live. Prepare fallback.

---

## Demo script (3 minutes)

**0:00 – 0:30 | The hook.**
"Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities. Seven AI agents, two model providers, one mission: see the kill chain before it kills you."

**0:30 – 0:50 | Architecture flash.**
Show the LangGraph `StateGraph` on screen. "Six specialist nodes monitor every layer of your company. Five run on Gemini. One — the Finance Agent — runs on GPT-4o-mini. This is intentional: when agents on different model families independently corroborate the same risk, that's a stronger signal than one model agreeing with itself. One Head Supervisor on Gemini connects the dots via conditional graph edges."

**0:50 – 1:50 | Live cascade with cross-provider corroboration.**
Walk through the cascade. "The People node on Gemini detected a 94% commit drop. Code Audit on Gemini confirmed the vulnerability. Legal on Gemini flagged the contract deadline. Then the Finance Agent — running on GPT-4o-mini, analyzing completely separate CSV data — independently calculated: if this contract breaks, 42% of revenue vanishes, runway drops to 2.5 months, and the investor down-round clause triggers. Two model families. Different data sources. Same conclusion. That's not model agreement — that's ground truth."

**1:50 – 2:15 | What If mode.**
Toggle simulation. Adjust sliders. Both Gemini and GPT-4o-mini re-run with modified assumptions. Cascade probability drops. "DEADPOOL doesn't just find the problem — it tells you exactly where to break the chain."

**2:15 – 2:45 | Traction.**
Flash the landing page. Show signup count. "We launched this 20 hours ago. [X] founders signed up."

**2:45 – 3:00 | Close.**
"Every startup has a DEADPOOL score right now. Most founders don't know theirs. Now they can."

---

## Why this wins

**Graph-native orchestration:** DEADPOOL's architecture is not a pipeline of sequential API calls. It is a compiled LangGraph `StateGraph` where the Head Supervisor dynamically routes between specialist nodes via conditional edges based on accumulated evidence in shared typed state. The cascade detection problem is structurally isomorphic to graph traversal. LangGraph is the right primitive.

**Multi-provider as a feature, not a constraint:** Five agents on Gemini. One agent on GPT-4o-mini. The multi-provider architecture creates **model-independent corroboration** — when agents on different model families reach the same conclusion from different data sources, the system has higher confidence than any single-model architecture could provide. This isn't a limitation we're working around. It's a deliberate architectural advantage that single-provider systems cannot replicate.

**State as the product:** `DEADPOOLState` is model-agnostic — it doesn't care whether the writing node used Gemini or GPT-4o-mini. The shared typed state object is the contract between all nodes. Anomalies from both providers merge seamlessly through LangGraph's list-append reducers.

**Memory that compounds:** LangGraph's `MemorySaver` checkpointer persists every state snapshot. The Head Supervisor reads prior state to adjust baseline probabilities — which signals proved predictive, which didn't. This works identically regardless of which model generated the original signal.

**Conditional routing IS the intelligence:** The `supervisor_router` function is where Gemini's reasoning produces observable behavior in the graph topology. When it routes to `["code_audit", "finance"]`, that routing decision sends one query to Gemini and one to GPT-4o-mini. The cross-provider fan-out is automatic.

**Product-market fit:** Every founder has been blindsided by a chain reaction they could have predicted. The Head Supervisor's unified briefing — synthesized from six specialists across two model providers — is the feature that makes people say "I need this yesterday."

**Quantified impact:** The average missed cascade costs a seed-stage startup $1.4M. DEADPOOL costs $6K/year — a 230x ROI on catching a single chain reaction. Time-to-insight compresses from weeks-to-never (founder intuition, board meetings) to under 60 seconds. The TAM is $204M annually across 34,000 US venture-backed startups between seed and Series B.

**Production-ready architecture:** The hackathon demo runs on `MemorySaver` and in-process nodes — but every production scaling step is a configuration change, not a rewrite. `MemorySaver` → `PostgresSaver` is a one-line swap. Multi-tenant isolation is a `thread_id` in the invoke config. Specialist nodes extract to microservices by swapping the function body. At 5,000 companies, API costs are 2.2% of revenue. The LangGraph `StateGraph` compiles identically at demo scale and production scale.

**Traction:** Landing page deployed by Day 1 evening. Target: 50+ signups.

---

## Differentiation strategy

1. **Graph-native cascade tracing:** LangGraph's `StateGraph` with conditional edges mirrors the cascade chain concept architecturally. Competitors would need to rebuild their orchestration layer.

2. **Cross-domain synthesis as core value:** No current tool performs cross-domain causal reasoning across people + finance + infra + product + legal + code simultaneously. The category does not exist yet.

3. **Multi-provider corroboration:** A single-provider system can only tell you that one model thinks there's a risk. DEADPOOL tells you that two independent model families, analyzing different data sources, independently reached the same conclusion. That's a fundamentally different confidence level.

4. **The "DEADPOOL score" as a wedge:** A single number from 0–100 representing company-wide operational risk creates FOMO ("what's your DEADPOOL score?") that is inherently viral among founders.

---

## Request for Hacks alignment

**RFH #02 — Agents That Hire Agents:** The Head Supervisor dynamically routes to specialist nodes via conditional edges — including routing across model providers. The `supervisor_router` function is the "hiring" decision. When it decides to query Finance, it's hiring a GPT-4o-mini agent. When it queries Legal, it's hiring a Gemini agent. Emergent cross-provider orchestration.

**RFH #04 — Intent as Code:** The cascade dependency graph is a company's operational intent encoded as configuration. `DEADPOOLState` carries the company's priorities through every node execution — regardless of which model powers that node. Intent-as-state-schema, model-agnostically.

**RFH #05 — The Product That Builds Itself:** LangGraph's `MemorySaver` persists cascade history across monitoring cycles. The Head Supervisor adjusts baseline probabilities based on which links materialized — including tracking which cross-provider corroborations were most predictive.

**RFH #07 — The One-Person Billion-Dollar Company:** DEADPOOL gives a solo founder the operational awareness of a 50-person leadership team. Seven agents, two model providers, one unified briefing.

---

## Success criteria

- All 7 LangGraph nodes running — five on Gemini, one on GPT-4o-mini, one deterministic — with structured outputs writing to `DEADPOOLState`.
- LangGraph conditional edges demonstrably driving cross-node, cross-provider routing (visible in Head Supervisor activity log).
- At least one detected cascade spanning 4+ node domains where the chain crosses the Gemini → GPT-4o-mini boundary.
- Head Supervisor resolving at least one cross-provider agent conflict on stage with documented reasoning in state.
- Working "What If" simulation mode — graph re-invoked with both providers processing modified assumptions.
- LangGraph `MemorySaver` checkpoint persisting state across monitoring cycles.
- Scalability path articulated: `PostgresSaver` swap, multi-tenant `thread_id` isolation, and horizontal specialist node extraction documented with code examples and cost model.
- Quantified user impact presented: $1.4M average cascade cost, 230x ROI, < 60 second time-to-insight vs weeks-to-never baseline, $204M TAM.
- 50+ landing page signups.
- The audience understands both the cascade chain and the cross-provider corroboration in under 60 seconds.

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities.*
*Built at the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*
*Powered by: Google Gemini 2.5 Flash + OpenAI GPT-4o-mini + LangGraph*