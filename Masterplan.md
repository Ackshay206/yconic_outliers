# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

*Seven AI agents. One mission. See the kill chain before it kills your startup.*

---

## The problem

Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

A lead engineer quietly disengages. Nobody notices for three weeks. The payments service she owns stops getting deployed. A critical feature deadline slips. The contract with your biggest client — 42% of revenue — has a delivery clause tied to that feature. The contract lapses. Revenue craters overnight. Your runway drops below three months. The down-round clause in your investor agreement triggers. The company is effectively dead.

Every signal was visible. The GitHub commits were declining. The deployment frequency was dropping. The contract deadline was approaching. The revenue concentration was documented. The investor terms were signed. But no tool, no dashboard, no human connected these dots across domains until the post-mortem.

This is the problem DEADPOOL solves.

**Who experiences it:** Every seed-to-Series B founder running a technology company with 5–50 employees — where no single person has full operational visibility across engineering, finance, legal, and product simultaneously. The failure modes are identical across the category: isolated signals in separate tools, no cross-domain synthesis, and chain reactions that become visible only in retrospect. While we launch focused on SaaS startups (the densest ICP with the most standardized tooling), the cascade detection concept applies to any small organization where operational domains are siloed — hardware startups, agencies, funded non-profits. SaaS is the wedge; cross-domain risk intelligence is the category.

**What we've heard from founders:** In conversations with 8 seed-stage founders during the hackathon prep period, the most common reaction was: *"I literally had this happen — our lead engineer left, and it took us three weeks to realize the client deadline was at risk."* Every founder we spoke to could name at least one chain reaction they'd experienced. None had a tool that connected the signals across domains. The demand signal is unambiguous.

---

## The vision

DEADPOOL is a multi-agent startup immune system built on LangGraph's stateful graph orchestration framework. Six specialist agents continuously monitor every operational layer of a company — people, finance, infrastructure, product, legal, and codebase — connected by a LangGraph `StateGraph` where a Head Supervisor node orchestrates them all: dynamically routing cross-validation tasks between specialists via conditional edges, accumulating corroborated evidence in a shared typed state object, and tracing exactly how a single anomaly cascades into downstream failures.

The system is **model-agnostic by design** — five specialist agents and the Head Supervisor run on **Google Gemini 2.5 Flash**, while the Finance Agent runs on **OpenAI GPT-4o-mini**. This multi-provider architecture is intentional: it demonstrates that the orchestration layer (LangGraph) is the intelligence, not any single model. When a Gemini-powered agent and a GPT-4o-mini-powered agent independently corroborate the same anomaly, the finding is robust across model families — not just consistent within one model's biases.

### What ships at this hackathon vs. what comes later

| | Hackathon (ships Sunday 2:30 PM) | Post-hackathon (weeks/months) |
|---|---|---|
| **Data** | Synthetic JSON/CSV files — carefully engineered to contain discoverable cascade chains | Real API integrations (GitHub, Slack, Stripe, PostHog) via OAuth + webhook connectors |
| **Agents** | 7 LangGraph nodes, each making 1 LLM call per cycle with structured output | Agents with multi-step tool-use loops, retry logic, and rate limit handling |
| **Orchestration** | Full LangGraph StateGraph with conditional routing, parallel fan-out, and MemorySaver checkpointing | PostgresSaver, multi-tenant thread_id isolation, horizontal node scaling |
| **Dashboard** | React + D3.js: cascade graph visualization, risk score, founder briefing, activity log | Animated cascade pulses, What-If simulation mode, alert system, mobile responsive |
| **Traction** | Landing page with signup form | Waitlist → beta invites → paid pilot with 5 founders |

This distinction matters because **code is evaluated against the master plan** — not against an aspirational vision. Everything in the "Hackathon" column is what we commit to building and what the code will be measured against. The "Post-hackathon" column is documented to show scalability thinking, but we do not claim to build it this weekend.

### The team — 5 people, clear ownership

| Member | Role | Owns | Skills |
|--------|------|------|--------|
| **Dev 1** | Agent Engineer (People, Finance, Product) | 3 specialist nodes, all prompts + structured output schemas, synthetic data files | Python, LLM APIs, data modeling |
| **Dev 2** | Agent Engineer (Infra, Legal, Code Audit) | 3 specialist nodes, CVE matching, contract parsing, deploy analysis | Python, security, systems |
| **Dev 3** | Orchestration Lead | Head Supervisor node, LangGraph StateGraph, conditional routing, cascade mapper, corroboration loop | Python, LangGraph, graph algorithms |
| **Dev 4** | Frontend Lead | React dashboard, D3 cascade graph, risk score panel, activity log, SSE client, landing page | React, D3.js, CSS, UI/UX |
| **Dev 5** | Integration & Infra | FastAPI backend, SSE streaming, deployment (Vercel + Railway), API wiring between frontend/backend, demo environment, traction | Python, DevOps, marketing |

Five people is the right size for this architecture: two devs building six specialist agents in parallel, one dedicated to the hardest engineering problem (LangGraph orchestration + cascade mapper), one owning the entire frontend, and one making sure everything connects and deploys. No single person is a bottleneck for more than one Tier 1 feature.

### Current progress (as of Saturday evening)

We are not starting from zero. Here's what's done and what remains:

| Component | Status | What's left |
|-----------|--------|-------------|
| **FastAPI backend scaffold** | ✅ Done | — |
| **React frontend scaffold** | ✅ Done | — |
| **All 6 specialist agent nodes** | ✅ Done | Prompt tuning, edge case handling |
| **Pydantic schemas** (Anomaly, AgentReport, CascadeChain) | ✅ Done | — |
| **Synthetic data files** (all 8 JSON/CSV) | ✅ Done | — |
| **Gemini + OpenAI SDK integration** | ✅ Done | — |
| **Deployment pipeline** (Vercel + Railway) | ✅ Done | — |
| **Head Supervisor node** | 🔄 In progress | Conditional routing logic, corroboration loop |
| **LangGraph StateGraph compilation** | 🔄 In progress | Wiring conditional edges, Send API fan-out |
| **Cascade mapper** (NetworkX BFS) | 🔄 In progress | Probability multiplication, chain pruning |
| **Agent collaboration protocol** | 🔄 In progress | Corroboration re-queries, entity-scoped context passing |
| **Dashboard: cascade graph (D3)** | 🔜 Next | Color-coded nodes, edge thickness, click-to-expand |
| **Dashboard: risk score + briefing** | 🔜 Next | Wire to SSE stream from backend |
| **Dashboard: activity log** | 🔜 Next | Read Head Supervisor decisions from state |
| **SSE streaming** | 🔜 Next | FastAPI → React push |
| **Landing page** | 🔜 Next | Signup form, "What's your DEADPOOL score?" |
| **What-If simulation** (Tier 2) | 🔜 Stretch | Only if Tier 1 is solid |

The critical path right now is **agent collaboration and cascade detection** — getting the Head Supervisor's conditional routing to work correctly so that the primary cascade (People → Code Audit → Infra → Legal → Finance) fires end-to-end. Once that works, the remaining items are frontend wiring and polish.

---

## Architecture

### The 7-node LangGraph

DEADPOOL runs as a **LangGraph `StateGraph`**. Six specialist nodes are domain experts. The Head Supervisor node is the graph's central router. Each node is a pure function: read from `DEADPOOLState`, call its model (Gemini or GPT-4o-mini), write structured output back.

**Model assignment:**

| Node | Model | Rationale |
|------|-------|-----------|
| Head Supervisor | Gemini 2.5 Flash | Needs the longest context to read all six domain reports + corroboration history simultaneously |
| People Agent | Gemini 2.5 Flash | Pattern recognition on 12-week developer activity time series |
| Finance Agent | **GPT-4o-mini** | Most structured workload — CSV parsing, arithmetic, threshold checks. GPT-4o-mini excels at structured extraction at low latency. Creates cross-provider corroboration signal. |
| Infra Agent | Gemini 2.5 Flash | System metrics correlation and degradation pattern detection |
| Product Agent | Gemini 2.5 Flash | Sentiment analysis on support tickets and engagement trends |
| Legal Agent | Gemini 2.5 Flash | Contract clause comprehension and compliance deadline tracking |
| Code Audit Agent | Gemini 2.5 Flash | Dependency tree analysis, CVE matching, bus factor calculation |
| Cascade Mapper | Deterministic | No LLM — pure NetworkX BFS with probability multiplication |
| Briefing Node | Gemini 2.5 Flash | Natural language synthesis for founder-facing output |

```
                      ┌─────────────────────────────┐
                      │       DEADPOOLState          │
                      │  TypedDict — shared across   │
                      │  all nodes in the graph      │
                      └──────────────┬──────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     HEAD SUPERVISOR (Gemini)     │
                    │  Reads all domain_reports        │
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

### DEADPOOLState — the shared typed state

```python
class DEADPOOLState(TypedDict):
    anomalies: Annotated[list[Anomaly], operator.add]  # list-append reducer
    domain_reports: dict[str, AgentReport]
    corroboration_queue: list[str]
    corroboration_results: dict
    cascade_chains: list[CascadeChain]
    risk_score: float
    briefing: str
    iteration: int              # guards against infinite loops (max 2)
    whatif_params: dict | None  # None = live mode, dict = simulation
```

State is model-agnostic — it doesn't care whether the writing node used Gemini or GPT-4o-mini. The Pydantic schemas for anomalies and reports are identical regardless of provider. LangGraph's `operator.add` reducer handles parallel merge of anomaly lists without conflict.

### Graph execution flow

```
START → [Parallel Fan-Out: 6 specialists via Send API]
         5 call Gemini, 1 calls GPT-4o-mini, all concurrent
      → [Head Supervisor reads all 6 reports]
         Identifies cross-domain anomalies
         Writes corroboration_queue (e.g. ["code_audit", "legal"])
      → [Conditional edge → targeted corroboration re-queries]
         Entity-scoped, not full re-scan
      → [Head Supervisor second pass]
         Cross-validates, raises/lowers severity
         Cross-provider agreement gets confidence boost
         iteration < 2? → more corroboration or → cascade_mapper
      → [Cascade Mapper: deterministic graph traversal]
         BFS through dependency graph, multiply probabilities
         Prune chains below 0.25 threshold
      → [Briefing Node: Gemini generates founder brief]
         Top 3 cascades, plain language, one action
      → END
```

### Conditional routing — the intelligence layer

The Head Supervisor uses `add_conditional_edges` with a routing function. LangGraph fans out to all targets in parallel — each uses its own model provider. The routing function is not hardcoded; it's Gemini reasoning over accumulated evidence to decide which specialist to query next.

```python
def supervisor_router(state: DEADPOOLState) -> list[str]:
    if state["iteration"] >= 2 or not state["corroboration_queue"]:
        return ["cascade_mapper"]
    return state["corroboration_queue"]
```

### Cross-domain linking via entity keys

| Key | Connects |
|-----|----------|
| `developer_name` | People ↔ Code Audit ↔ Infra |
| `service_name` | Infra ↔ Code Audit ↔ Legal ↔ Product |
| `client_name` | Finance ↔ Legal |
| `feature_name` | Infra ↔ Legal ↔ Product |

These keys are embedded in every corroboration query so receiving nodes narrow their analysis to the specific cross-domain intersection.

---

## The six specialist agents

### People Agent *(Gemini)*
**Domain:** Team health, engagement, key-person risk.
**Data:** `team_activity.json` — 12 developers × 12 weeks of commit, PR, and response time data.
**Detects:** Commit drops >50% WoW, prolonged silence from key contributors, bus factor concentration, PR review bottlenecks.
**Cross-references:** Code Audit (affected code areas), Infra (owned services), Finance (payroll impact).

### Finance Agent *(GPT-4o-mini)*
**Domain:** Cash flow, runway, revenue pipeline, funding terms.
**Data:** Three CSV files — `deadpool_finance_data.csv` (transaction ledger), `deadpool_revenue_pipeline.csv` (revenue + pipeline deals), `deadpool_funding_runway.csv` (investor terms + runway scenarios).
**Why GPT-4o-mini:** Most structured workload in the system. CSV parsing, arithmetic (burn = expenses − revenue, runway = cash / net burn), threshold checks (runway < 6mo? concentration > 40%?). GPT-4o-mini is fast, precise at structured extraction, and produces consistent JSON. Cross-provider corroboration: when Finance (GPT-4o-mini) and Legal (Gemini) independently flag the same contract risk from different data sources, the finding is model-family-independent.
**Detects:** Runway <6 months, revenue concentration >40%, burn acceleration, investor clause proximity, pipeline deals at risk from feature dependencies.
**Cross-references:** Legal (contract deadlines), People (headcount costs), Product (churn impact on revenue).

### Infra Agent *(Gemini)*
**Domain:** System reliability, deployment operations, performance.
**Data:** `infrastructure.json` — 6 microservices × 12 weeks of deploy counts, uptime, response times, error rates, cloud costs.
**Detects:** Deploy frequency drops, CI failure spikes, response time degradation, SLA breach risk, cloud cost anomalies.
**Cross-references:** Code Audit (code quality → runtime failures?), People (who owns the degrading service?), Legal (SLA obligations at risk).

### Product Agent *(Gemini)*
**Domain:** User engagement, retention, satisfaction.
**Data:** `product_metrics.json` — WAU, feature engagement, support tickets, NPS, churn rates.
**Detects:** Feature adoption decline, churn increases, NPS drops, support ticket spikes, sentiment deterioration.
**Cross-references:** Infra (performance → UX decline?), Code Audit (bugs → user errors?), Finance (revenue impact of churn).

### Legal Agent *(Gemini)*
**Domain:** Contracts, compliance, regulatory exposure.
**Data:** `contracts.json` — client contracts with parsed clauses, investor agreements, compliance obligations.
**Detects:** Contract deadlines approaching with delivery at risk, conflicting terms, regulatory changes, compliance gaps (PCI DSS, SOC 2).
**Cross-references:** Finance (breach liability), Infra (feature delivery status), Code Audit (compliance mapped to code state).

### Code Audit Agent *(Gemini)*
**Domain:** Codebase health, security posture, technical debt.
**Data:** `codebase_audit.json` — file change frequency, code ownership maps, CVE scan results, test coverage, PR review patterns.
**Detects:** CVEs with CVSS ≥7.0, test coverage <60% for critical services, bus factor = 1, unreviewed PRs in critical paths, outdated dependencies (2+ major versions behind).
**Cross-references:** People (who owns the code?), Infra (which services run on it?), Legal (compliance implications), Product (user-facing features built on degraded code).

---

## The Head Supervisor Node *(Gemini)*

The Head Supervisor orchestrates, arbitrates, and synthesizes through LangGraph's graph execution model.

**Cross-validation:** Reads all six domain reports (five from Gemini, one from GPT-4o-mini), identifies high-severity anomalies, routes corroboration queries via conditional edges. Cross-provider corroborations (Gemini ↔ GPT-4o-mini) carry extra confidence weight.

**Conflict resolution:** Does not average or discard contradictory signals. Models the scenario forward. Example: GPT-4o-mini Finance reports healthy runway (9.4 months). Gemini Legal flags contract breach risk. The supervisor reasons: *"Finance computed runway without the conditional revenue loss. Legal's breach is upstream — recalculate Finance under Legal's scenario."* Routes to GPT-4o-mini Finance with breach parameters. New output: runway = 2.5 months. Legal dominates. Resolution documented in state.

**Cascade ranking:**
```
urgency = (1 / time_to_impact_days) × severity × (1 - reversibility)
```
Top 3 cascades surfaced. Information overload is itself a risk.

**LangGraph checkpointing:** `MemorySaver` persists every execution by `thread_id`. Across cycles, the supervisor reads prior state to adjust baseline probabilities based on which signals proved predictive.

---

## The Cascade Mapper *(deterministic)*

No LLM. Pure NetworkX BFS with probability multiplication. This is intentional — the cascade mapper should be deterministic, fast, and free of model variance.

1. Reads validated anomalies from state
2. Matches each to pre-built cascade paths via `TRIGGER_MAP`
3. Multiplies conditional probabilities edge-by-edge
4. Prunes chains where cumulative probability < 0.25
5. Writes `CascadeChain` objects to state

**Six pre-seeded cascade paths:**
1. Key-person departure → code gap → quality drop → delivery delay → contract breach → revenue loss → runway crisis *(primary demo cascade)*
2. CVE in dependency → compliance breach → legal exposure → investor confidence loss
3. Test coverage decline → bugs shipped → user errors → churn spike → revenue drop
4. Tech debt → deploy velocity drop → feature failure → competitive loss
5. Revenue concentration → single client churn → revenue cliff → down-round trigger
6. Infra degradation → SLA breach → contract penalty → burn spike → runway compression

---

## Features: what ships vs. what's stretch

**The scoring rubric evaluates code against the master plan.** Overcommitting kills the completeness score. We define three tiers:

### Tier 1 — Must ship (core product, code deadline: Day 1 midnight)

| Feature | Owner | Description | Status |
|---------|-------|-------------|--------|
| **7-node LangGraph graph** | Dev 3 | All 6 specialists + Head Supervisor compiled and executing. Parallel fan-out, conditional routing, corroboration loop, cascade mapper, briefing node. | 🔄 Agent nodes done, orchestration in progress |
| **Cascade detection** | Dev 3 + Dev 1/2 | Primary cascade (People → Code Audit → Infra → Legal → Finance) detected from synthetic data with correct probability chain. | 🔄 In progress |
| **Dashboard: cascade graph** | Dev 4 | React + D3.js directed graph showing cascade chains with color-coded nodes and edge thickness encoding probability. Clickable nodes expanding to show evidence. | 🔜 Next |
| **Dashboard: risk score + briefing** | Dev 4 | Single number 0–100, color indicator, trend arrow, and 2–3 sentence Head Supervisor briefing displayed below. | 🔜 Next |
| **Dashboard: activity log** | Dev 4 | Scrollable log showing Head Supervisor routing decisions, corroboration results, and severity adjustments. | 🔜 Next |
| **SSE streaming** | Dev 5 | FastAPI → React real-time push for cascade updates and briefings. | 🔜 Next |
| **Landing page** | Dev 5 | Signup form with "What's your DEADPOOL score?" framing. | 🔜 Next |

### Tier 2 — Should ship (high-value, code deadline: Day 2 10:30 AM)

| Feature | Owner | Description | Complexity |
|---------|-------|-------------|------------|
| **What-If simulation** | Dev 3 | Sliders modify `whatif_params` in state, re-invoke graph, display side-by-side comparison. | Medium |
| **Cross-provider highlighting** | Dev 4 | Activity log marks corroborations that cross the Gemini/GPT-4o-mini boundary. | Low |
| **Cascade animation** | Dev 4 | Pulse animation traveling along active cascade chains from trigger to end-state. | Medium |

### Tier 3 — Stretch (demo polish, only if Tiers 1-2 are solid)

| Feature | Owner | Description | Complexity |
|---------|-------|-------------|------------|
| **Alert toasts** | Dev 4 | Toast notifications when cascade probability crosses severity threshold. | Low |
| **LangGraph trace visualization** | Dev 5 | Show which nodes are active and which edges fired during graph execution. | Medium |
| **Multiple simultaneous cascades** | Dev 3 | Dashboard rendering 2+ cascade chains simultaneously. | Medium |

### Feasibility analysis — why this ships in time

**Why we're confident (not naive):**

1. **Backend agents are already done.** All six specialist nodes produce structured `AgentReport` outputs from synthetic data. Gemini and GPT-4o-mini integrations are tested. This is the part most hackathon teams are still building at midnight — we finished it Saturday afternoon.

2. **The critical remaining work is well-scoped.** The Head Supervisor's conditional routing is a known LangGraph pattern (`add_conditional_edges` + `supervisor_router`). The cascade mapper is deterministic NetworkX BFS — no LLM variance, no prompt debugging. These are engineering problems with clear solutions, not open-ended research.

3. **Five people eliminates the frontend bottleneck.** The most common hackathon failure mode is "backend works but dashboard isn't ready." With a dedicated frontend dev (Dev 4) and an integration dev (Dev 5) who handles SSE + deployment, the frontend track runs in parallel with zero dependency on the orchestration track.

4. **We have a working fallback at every layer.** D3 graph too complex? → Table view in 30 minutes. What-If not ready? → Demo script has an if/else that skips to traction. SSE breaks? → Pre-cached last result in frontend state. The demo never breaks; it just degrades gracefully.

5. **We've already validated the hardest integration point.** Gemini and GPT-4o-mini both produce outputs that parse into the same Pydantic `AgentReport` schema. The cross-provider schema mismatch risk — the scariest feasibility question — is already resolved.

**Honest risks that remain:**

- The Head Supervisor's corroboration routing is the single hardest remaining piece. If it takes longer than expected, we simplify: supervisor does one pass (no corroboration loop), reads all six reports, and routes directly to cascade mapper. Corroboration becomes a Tier 2 feature.
- D3 cascade graph visualization could eat more time than allocated. Dev 4 builds the table fallback *first* and only upgrades to D3 if time permits.
- End-to-end integration (backend → SSE → frontend) always has surprises. Dev 5's entire role is handling these surprises.

**Dashboard contingency:** If D3 animated graph visualization runs over time, we fall back to a structured table view of cascade chains (node → node → node with probabilities) rendered in plain React. The cascade data is the same — only the visualization changes. The table fallback can be built in 30 minutes. The D3 graph is a better demo, but the table is a better plan.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | **LangGraph** `StateGraph` | Typed state, conditional edges, parallel fan-out via `Send`, `MemorySaver` checkpointing. The right primitive for graph-structured agent orchestration. |
| AI (primary) | **Gemini 2.5 Flash** via `google-genai` SDK | 5 specialist nodes + supervisor + briefing. JSON mode for structured output. |
| AI (finance) | **GPT-4o-mini** via `openai` SDK | Finance node only. `response_format={"type": "json_object"}`, `temperature=0.1`. |
| Backend | **Python + FastAPI** | Async-native, Pydantic v2 for type-safe I/O, SSE via `sse-starlette`. |
| Frontend | **React + D3.js** | D3 for cascade graph. React for dashboard state and panels. |
| Deployment | **Vercel** (frontend) + **Railway** (backend) | Free tiers, <5 minute deploy. |

---

## Agent implementation

### LangGraph graph construction

```python
import google.genai as genai
from openai import OpenAI

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

workflow = StateGraph(DEADPOOLState)

# Each node owns its model client
workflow.add_node("people", people_node)          # Gemini
workflow.add_node("finance", finance_node)        # GPT-4o-mini
workflow.add_node("infra", infra_node)            # Gemini
workflow.add_node("product", product_node)        # Gemini
workflow.add_node("legal", legal_node)            # Gemini
workflow.add_node("code_audit", code_audit_node)  # Gemini
workflow.add_node("head_supervisor", head_supervisor_node)  # Gemini
workflow.add_node("cascade_mapper", cascade_mapper_node)    # deterministic
workflow.add_node("briefing", briefing_node)      # Gemini

workflow.add_conditional_edges(START, initial_fanout)
for s in ["people","finance","infra","product","legal","code_audit"]:
    workflow.add_edge(s, "head_supervisor")
workflow.add_conditional_edges("head_supervisor", supervisor_router)
workflow.add_edge("cascade_mapper", "briefing")
workflow.add_edge("briefing", END)

app = workflow.compile(checkpointer=MemorySaver())
```

### Specialist node pattern (Gemini)

```python
def people_node(state: DEADPOOLState) -> dict:
    data = load_json("team_activity.json")
    entity_context = get_entity_context(state, "people")
    prompt = build_people_prompt(data, entity_context)

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AgentReport
        )
    )
    report = AgentReport.model_validate_json(response.text)
    return {"anomalies": report.anomalies, "domain_reports": {"people": report}}
```

### Finance node (GPT-4o-mini)

```python
def finance_node(state: DEADPOOLState) -> dict:
    transactions = load_csv("deadpool_finance_data.csv")
    pipeline = load_csv("deadpool_revenue_pipeline.csv")
    funding = load_csv("deadpool_funding_runway.csv")
    entity_context = get_entity_context(state, "finance")
    whatif = state.get("whatif_params")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": FINANCE_SYSTEM_PROMPT},
            {"role": "user", "content": build_finance_prompt(
                transactions, pipeline, funding, entity_context, whatif)}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    report = AgentReport.model_validate_json(response.choices[0].message.content)
    report.model_provider = "openai/gpt-4o-mini"
    return {"anomalies": report.anomalies, "domain_reports": {"finance": report}}
```

### Agent interaction flow

The full flow (parallel fan-out → supervisor reads → conditional corroboration → cascade mapping → briefing) is detailed in the Architecture section above. The key implementation detail: steps [3]–[6] in that flow are the Head Supervisor's conditional routing — each step is a LangGraph edge, not a function call. The graph structure *is* the control flow.

---

## Data architecture

### Synthetic data (hackathon)

Seven files, engineered with discoverable cascade chains and noise signals that agents should correctly ignore:

| File | Agent | Key signals |
|------|-------|-------------|
| `team_activity.json` | People | Sarah Chen: 94% commit drop over 5 weeks. 11 others: normal with noise. |
| `deadpool_finance_data.csv` | Finance | $900K raised, $73K/mo burn, $493K cash, $1.2K/mo revenue. |
| `deadpool_revenue_pipeline.csv` | Finance | Nexus Corp $423K/yr deal at_risk (prob 0.85→0.35). Greenleaf $9K overdue (noise). |
| `deadpool_funding_runway.csv` | Finance | Down-round clause at runway <3mo. Base runway: 6.7mo. Worst case: 3.6mo to trigger. |
| `infrastructure.json` | Infra | payments-service: 0 deploys in 2 weeks, API v2 at 34% completion. Others stable. |
| `product_metrics.json` | Product | Payments dashboard errors 0.2%→12%. Other features stable. |
| `contracts.json` | Legal | Nexus Corp Section 4.2: API v2 by April 15 or termination. PCI DSS obligation. |
| `codebase_audit.json` | Code Audit | payments-service: bus factor=1, CVE-2026-4821 (CVSS 8.1), coverage 82%→61%. |

Entity linking keys (`sarah_chen`, `payments-service`, `nexus_corp`, `payments_api_v2`) are identical across all files.

### Transition to real data (post-hackathon)

The synthetic data architecture is designed so each file maps to a specific real API integration. The transition path per agent:

| Agent | Hackathon data | Production data source | Integration method | Entity resolution |
|-------|---------------|----------------------|-------------------|-------------------|
| People | `team_activity.json` | GitHub REST API + Slack API | OAuth app → webhook on push/PR events → normalize to `DeveloperActivity` schema | GitHub username → Slack display name mapping table |
| Finance | 3 CSV files | Stripe API + QuickBooks/Xero API + manual CSV upload | OAuth for Stripe/accounting; CSV upload remains as fallback for cap table data | Stripe customer_id → contract client_name mapping |
| Infra | `infrastructure.json` | GitHub Actions API + BetterStack/UptimeRobot API + AWS Cost Explorer | OAuth + API keys → periodic polling → normalize to `ServiceHealth` schema | GitHub repo → service_name mapping in config |
| Product | `product_metrics.json` | PostHog/Plausible API + Intercom/Zendesk API | OAuth → periodic polling → normalize to `ProductMetrics` schema | Feature names defined in onboarding config |
| Legal | `contracts.json` | PDF upload → Claude/Gemini extraction of key clauses | Upload UI → LLM extracts structured clause data → human reviews/confirms | Client names matched to Finance `client_name` |
| Code Audit | `codebase_audit.json` | GitHub API (git blame, PRs) + `pip-audit`/`npm audit` output | GitHub OAuth → periodic scan → normalize to `CodebaseHealth` schema | GitHub username → developer_name; repo → service_name |

**The critical engineering challenge** at the integration layer is entity resolution — ensuring that "sarah-chen" in GitHub, "Sarah Chen" in Slack, and "Sarah Chen" in the HR system all resolve to the same `developer_name` entity key. Post-hackathon, this requires a configurable entity mapping layer (JSON config uploaded during onboarding) that normalizes identifiers across sources. The hackathon version sidesteps this by using pre-normalized synthetic data — but the schema design accommodates the mapping layer.

---

## Cascade demonstration

### Primary demo cascade (5 agents, 2 providers, 6 nodes)

```
Step 1 │ PEOPLE NODE (Gemini)
       │ Sarah Chen commits dropped 94% over 5 weeks
       │ Severity: 0.85 → validated to 0.91
       ▼ P(link fires): 0.78

Step 2 │ CODE AUDIT NODE (Gemini)
       │ payments-service: bus factor=1, coverage 61%, CVE-2026-4821 (CVSS 8.1)
       │ Severity: 0.82
       ▼ P(link fires): 0.72

Step 3 │ INFRA NODE (Gemini)
       │ payments-service: 0 deploys in 2 weeks. API v2 at 34%, deadline 18 days.
       │ Severity: 0.79
       ▼ P(link fires): 0.58

Step 4 │ LEGAL NODE (Gemini)
       │ Nexus Corp Section 4.2: API v2 by April 15. Breach = termination.
       │ Refund liability: $211,680
       │ Severity: 0.88
       ▼ P(link fires): 0.65

Step 5 │ FINANCE NODE (GPT-4o-mini ← cross-provider)
       │ Nexus = 42% revenue. Post-loss burn: $80K/mo net negative.
       │ After refund: cash ~$200K. Runway: 2.5 months.
       │ *** Cross-provider corroboration: Gemini Legal + GPT-4o-mini Finance
       │ *** independently flag same risk. Model-independent signal.
       │ Severity: 0.92
       ▼ P(link fires): 0.75

Step 6 │ FINANCE NODE (GPT-4o-mini)
       │ Down-round clause triggers below 3-month runway.
       │ Investor converts at 50% discount, 2x liquidation preference.
       │ Founder diluted below control. END STATE: Company lost.
       │
       │ Cascade probability: 0.19 | Time to impact: 75 days | Impact: $1.9M+
```

**Head Supervisor briefing:**

> "Your lead backend engineer has been disengaging for five weeks, and she's the only person who can ship the payments feature that Nexus Corp's contract requires by April 15. The Code Audit node found an unpatched critical vulnerability in the same service. If the deadline is missed, Nexus Corp can walk — taking 42% of your revenue. That drops your runway below three months and triggers the down-round clause. Talk to Sarah Chen today. Start knowledge transfer this week. Contact Nexus Corp about a deadline extension before April 1."

---

## Quantified user impact

### Total addressable market

Approximately **34,000 venture-backed startups** between seed and Series B in the US (PitchBook 2025), ~80,000 globally. At $500/month (below a fractional COO at $5K–$10K/mo, above commodity dashboards), the US SAM is **$204M annually**.

### Cost of a missed cascade

| Cascade type | Avg financial impact | Time from signal to crisis | Early detection window |
|-------------|---------------------|---------------------------|----------------------|
| Key-person → delivery failure → contract breach | $1.2M–$2.4M | 60–120 days | 2–4 weeks after first commit drop |
| CVE → compliance breach → client termination | $400K–$900K | 30–90 days | Immediately on CVE publication |
| Revenue concentration → client churn → runway cliff | $800K–$3M | 45–90 days | Continuous monitoring at 40% threshold |
| Tech debt → deploy collapse → competitive loss | $500K–$1.5M | 90–180 days | Weeks before velocity hits critical |

**Average missed cascade cost: $1.4M.** DEADPOOL at $500/mo ($6K/year) delivers **230x ROI** on catching one.

### Time-to-insight comparison

| Method | Latency | Cross-domain coverage |
|--------|---------|----------------------|
| Founder intuition | Weeks to never | Partial — depends on which dashboards they check |
| Weekly standups | 7+ days | Filtered by what team members choose to escalate |
| Board meetings | 30–90 days | High-level only. Won't see a commit drop in one engineer. |
| **DEADPOOL** | **< 60 seconds** | All six domains. Cross-domain links traced automatically. |

For a company burning $50K–$100K/month, every week of earlier detection preserves $12K–$25K in runway.

---

## Market awareness and competitive landscape

### Competitive landscape — who's adjacent and why they can't do this

| Tool | What it does | Gap | Could they add cross-domain? |
|------|-------------|-----|------------------------------|
| **LinearB / GitHub Insights** | Engineering metrics (cycle time, PR throughput) | Finance + legal blind spots | No. Would need to ingest financial data, parse contracts, and build a causal reasoning layer. Completely outside their data model and product thesis. |
| **ChartMogul / Baremetrics** | Revenue dashboards, MRR/churn analytics | No causal link to engineering triggers | No. They don't have access to GitHub, infrastructure metrics, or codebase analysis. Revenue is the *end* of the cascade — they can't see the *beginning*. |
| **Notion / Linear** | Project and task tracking | Passive; human must connect dots | Theoretically possible — they have some cross-domain data. But their AI investment is in task automation and summarization, not causal chain reasoning. The LangGraph orchestration layer alone is 6+ months of engineering. |
| **Looker / Metabase** | BI reporting and dashboards | Descriptive, not predictive; no agent reasoning | No. BI tools visualize data you query — they don't autonomously detect anomalies across domains or reason about causal chains. Adding multi-agent orchestration would be a complete product pivot. |
| **Runway (financial planning)** | Financial modeling and scenario planning | Engineering, legal, and product blind spots | Closest potential competitor in the finance domain. But their product is manual scenario modeling — a human builds the model. DEADPOOL's Finance Agent *discovers* the scenarios autonomously by cross-referencing with engineering and legal signals. |
| **Snyk / Dependabot** | Dependency vulnerability scanning | Only code domain; no business context | They can tell you there's a CVE. They can't tell you that the CVE is in a service owned by an engineer who just went on leave, blocking a feature that a $423K contract depends on. The business context is DEADPOOL's entire value. |

**DEADPOOL's position:** No current tool performs cross-domain causal reasoning across people + finance + infra + product + legal + code simultaneously. The category does not exist yet.

**Why incumbents won't build this fast:** The core challenge isn't AI — it's the cross-domain data model. LinearB would need to integrate with Stripe, parse legal contracts, and build entity resolution across GitHub users → financial records → contract clauses. ChartMogul would need to ingest GitHub data, infrastructure metrics, and codebase analysis. Each of these is a 6–12 month integration project *before* building the orchestration layer. By then, DEADPOOL has 12+ months of checkpoint memory for each customer — a data moat that a late entrant cannot shortcut.

### Competitive moat — three layers of defensibility

1. **Orchestration complexity moat (technical):** A 7-node LangGraph with conditional cross-domain routing, multi-provider orchestration, and typed state contracts is an order of magnitude harder to build than a single-domain AI dashboard. The architecture *is* the product.

2. **Compounding data moat (time-based):** Every monitoring cycle, DEADPOOL's checkpoint memory learns which cross-domain signal correlations are predictive for *this specific company*. After 6 months, a company's DEADPOOL instance has a unique risk model that a competitor starting fresh cannot replicate. The switching cost is losing your accumulated operational intelligence. This moat deepens every day automatically.

3. **Cross-domain entity graph moat (configuration-based):** The entity resolution layer (developer_name ↔ service_name ↔ client_name ↔ feature_name) is configured per company during onboarding. This mapping — who owns what, what depends on what, which contracts matter — is proprietary organizational knowledge. It's the company's operational DNA encoded as graph edges. Once configured, it's deeply sticky — migrating to a competitor means re-mapping your entire organizational structure.

### Go-to-market — phased approach

| Phase | Timeline | Strategy | Success metric |
|-------|----------|----------|----------------|
| **Hackathon** | This weekend | Landing page + LinkedIn post with cascade demo GIF + hackathon Slack sharing + in-person demos to attendees | 50+ signups |
| **Founder validation** | Month 1–2 | Personal outreach to 8 founders who validated the problem. Free DEADPOOL score using their real GitHub + financial data. Iterate on the product based on real feedback. | 5 companies running DEADPOOL on real data |
| **Closed beta** | Month 3–6 | Waitlist → beta with 15–20 companies. Focus on seed-stage SaaS with 8–25 employees (sweetest ICP — small enough for one founder to use DEADPOOL as their entire ops layer, large enough to have real cross-domain complexity). | 15 active companies, 3+ using it weekly |
| **Self-serve launch** | Month 6+ | OAuth connectors for GitHub, Slack, Stripe. CSV upload for everything else. Pricing: $500/mo for up to 30 employees. | 50 paying customers, $25K MRR |
| **Expansion** | Year 2+ | Expand beyond SaaS: hardware startups, agencies, funded non-profits. Investor dashboard product (aggregate DEADPOOL scores across portfolio). | $100K MRR, enterprise pilot |

### Pricing logic

$500/month positions DEADPOOL in the "essential infrastructure" price band — below a fractional COO ($5K–$10K/month) or a risk consultant ($200–$400/hour), but above commodity dashboards ($50–$100/month). At this price point, a founder who catches one cascade per year gets a 230x ROI. The price is low enough to be a no-brainer expense for any funded startup, high enough to signal serious value.

---

## Ecosystem and extensibility

DEADPOOL is designed as an **open platform**, not a closed dashboard. Every layer — data ingestion, agent logic, cascade paths, and output — is extensible through well-defined interfaces.

### Customer data integration model

| Integration tier | Method | Availability | Data flow |
|-----------------|--------|-------------|-----------|
| **Tier 1: CSV/JSON upload** | Manual file upload via dashboard. Finance CSVs, contract JSONs, team activity exports. | Hackathon (ships Sunday) | User uploads → backend parses → agent reads from disk |
| **Tier 2: OAuth connectors** | One-click connect for GitHub, Slack, Stripe, PostHog, Intercom. Periodic polling (every 5 min). | Post-hackathon Month 1–2 | OAuth flow → token stored → background worker polls API → normalizes to agent schema → writes to data store |
| **Tier 3: Webhooks** | Real-time push from customer systems. GitHub push/PR webhooks, Stripe invoice events, Slack message events. | Post-hackathon Month 3+ | Webhook endpoint → validate signature → normalize event → trigger agent re-analysis on affected domain |
| **Tier 4: Custom adapters** | Python adapter interface for proprietary data sources. Customers write a `DataAdapter` class that returns normalized schema. | Post-hackathon Month 6+ | Customer implements `DataAdapter.fetch() → NormalizedData` → DEADPOOL polls adapter on schedule |

**Normalization layer:** All integration tiers feed through a normalization layer that converts source-specific data into DEADPOOL's internal schemas (`DeveloperActivity`, `FinancialRecord`, `ServiceHealth`, `ProductMetric`, `ContractClause`, `CodebaseState`). Agents never see raw API responses — they see normalized domain objects. Adding a new data source (e.g., switching from GitHub to GitLab) only requires a new normalizer, not changes to agent logic. The normalizer interface is a simple Python ABC: `DataAdapter.fetch(entity_keys) → NormalizedData`.

### Custom cascade paths

The six pre-seeded cascade paths cover common startup failure modes. But companies have unique risk topologies. Post-hackathon, customers can define custom cascade paths through a JSON configuration:

```json
{
  "name": "Customer onboarding failure → support overload → churn → revenue loss",
  "nodes": [
    {"domain": "product", "trigger": "onboarding_completion_rate < 0.4"},
    {"domain": "product", "trigger": "support_ticket_volume > 2x_baseline"},
    {"domain": "product", "trigger": "churn_rate > 0.05"},
    {"domain": "finance", "trigger": "monthly_revenue_decline > 0.1"}
  ],
  "baseline_probabilities": [0.6, 0.7, 0.5]
}
```

The cascade mapper's BFS engine is path-agnostic — it traverses whatever edges exist in the dependency graph. Custom paths are just new edges added to the NetworkX graph. This means DEADPOOL's intelligence grows with the customer's domain knowledge: the more cascade paths they define, the more failure modes the system can detect.

**Cascade path marketplace (future vision):** Companies in similar industries share failure modes. Post-hackathon, we envision a community library of anonymized cascade path templates — "SaaS Revenue Concentration Pack," "Compliance-Heavy Fintech Pack." This creates a network effect: every contributed cascade path makes the platform better for all customers.

### DEADPOOL Score API (post-hackathon)

Third-party consumption of DEADPOOL scores via REST API:

```
GET  /api/v1/score
→ { "risk_score": 73, "trend": "increasing", "top_cascade": "...", "briefing": "..." }

GET  /api/v1/cascades
→ [{ "name": "...", "probability": 0.19, "time_to_impact_days": 75, "chain": [...] }]

POST /api/v1/simulate
← { "whatif": {"key_engineer_leaves": true} }
→ { "new_score": 89, "new_cascades": [...], "delta": "+16" }

GET  /api/v1/agents/{domain}/report
→ { "domain": "finance", "anomalies": [...], "model_provider": "openai/gpt-4o-mini" }
```

**Use cases:** Investor dashboards that aggregate DEADPOOL scores across portfolio companies (a VC with 30 portfolio companies gets a single view of which ones are at risk), board reporting integrations (monthly board deck auto-populates with DEADPOOL risk trends), Slack bots that post daily briefings, CI/CD pipeline gates that block deploys if DEADPOOL risk score exceeds a threshold.

### Interoperability with existing tools

DEADPOOL doesn't replace existing tools — it connects them. A company keeps using GitHub, Slack, Stripe, and Linear exactly as before. DEADPOOL reads from those tools (via OAuth/webhooks) and adds the cross-domain reasoning layer on top. Zero workflow change required: install, connect, receive cascade briefings.

---

## Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Infinite corroboration loop** | Medium | High — system hangs | `iteration` counter in state; max 2 passes before routing to cascade mapper |
| **Gemini returns malformed JSON** | Medium | Medium — node fails | Pydantic parsing with fallback to empty anomaly list; node never crashes the graph |
| **GPT-4o-mini Finance node timeout** | Low | High — breaks demo | 10s timeout; fallback: inject last-known Finance report from checkpoint state |
| **Schema mismatch across providers** | Low | High — state corruption | All nodes output identical Pydantic `Anomaly` schema; validated before state write |
| **D3 graph visualization overruns time budget** | Medium | Medium — demo quality | **Fallback: structured table view** of cascade chains in plain React. Same data, simpler render. Buildable in 30 minutes. |
| **Synthetic data triggers no anomalies** | Low | High — empty demo | Data engineered with known cascade signals; fallback: severity floor of 0.5 for demo mode |
| **Full integration sprint fails (Day 1 5–7 PM)** | Low | Critical — nothing works | Each specialist node is independently testable. If full graph doesn't compile, demo individual agent outputs + manually narrate the cascade chain. Ugly but functional. |
| **WiFi drops during live demo** | Medium | Medium — demo pauses | Pre-cache last graph execution result in frontend local state. Demo runs from cached state if backend is unreachable. Briefing and cascade chain display from cache. |
| **Projector/display issues** | Low | Low | Backup: screen-share from laptop. Secondary backup: screenshots in slide deck. |
| **Audience doesn't understand cascade in 60 seconds** | Medium | High — judges confused | Demo script opens with the *story* (engineer leaves → contract breaks → company dies) before showing the graph. Narrative first, visualization second. Rehearsed 3x. |

**Contingency priority:** The riskiest item is the D3 visualization eating too much time. We commit to having the table fallback working by Day 1 midnight. D3 animated graph is a Day 2 upgrade — attempted only if Tiers 1 are solid.

---

## Scalability design

### PostgresSaver — production checkpointer

One-line swap from hackathon to production:

```python
# Hackathon
app = workflow.compile(checkpointer=MemorySaver())

# Production
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
pool = AsyncConnectionPool(conninfo=os.environ["DATABASE_URL"])
app = workflow.compile(checkpointer=AsyncPostgresSaver(pool))
```

Enables durable cross-cycle memory, crash recovery (graph resumes from last checkpoint), and SQL-queryable audit history.

### Multi-tenant isolation

Each company gets a unique `thread_id`. LangGraph's checkpointer scopes all state to that thread. Company A's cascade history never leaks into Company B's. Dependency graphs evolve independently per tenant.

```python
result = await app.ainvoke(state, config={"configurable": {"thread_id": "company-acme-001"}})
```

### Horizontal scaling path

| Phase | Architecture | Scale | What changes |
|-------|-------------|-------|-------------|
| Hackathon | All nodes in-process, `asyncio` concurrency | 1 company | Nothing — this is what ships |
| Early production | Specialist nodes as FastAPI microservices behind load balancer | 10–50 companies | Node function body swaps from direct API call to HTTP client call. Graph structure unchanged. |
| Growth | Kubernetes HPA on request queue depth per service | 100–5,000 companies | Each specialist service autoscales independently. Finance (GPT-4o-mini) and Gemini services scale on different profiles. |
| Enterprise | Dedicated graph instances per enterprise customer, shared specialist service pool | 5,000+ companies | Graph compilation per tenant with customer-specific cascade paths. Specialist services are stateless and shared. |

The LangGraph graph structure doesn't change across any phase. The compiled graph is the same artifact at hackathon scale and enterprise scale — only the infrastructure underneath evolves.

### Transition from synthetic data to real APIs

This is the most significant engineering challenge post-hackathon. The synthetic data files map 1:1 to real API integrations, but the transition requires solving entity resolution, rate limiting, and data freshness:

| Agent | Hackathon source | Production source | Key engineering challenge |
|-------|-----------------|-------------------|--------------------------|
| People | `team_activity.json` | GitHub REST API + Slack API | **Entity resolution:** GitHub `sarah-chen-42` → Slack `Sarah Chen` → HR system `sarah.chen@company.com` must all resolve to the same `developer_name`. Solved with a configurable mapping table uploaded during onboarding. |
| Finance | 3 CSV files | Stripe API + QuickBooks/Xero + CSV upload | **Data freshness:** Stripe webhooks for real-time transaction data. Accounting APIs polled daily. CSV upload remains for cap table and investor terms (too sensitive for API access). |
| Infra | `infrastructure.json` | GitHub Actions API + BetterStack + AWS CloudWatch | **Rate limiting:** GitHub API has 5,000 req/hour. With 50 companies each with 6 services, we need intelligent caching (poll every 5 min, cache results, only re-query on webhook trigger). |
| Product | `product_metrics.json` | PostHog/Plausible + Intercom/Zendesk | **Schema normalization:** PostHog events have different structure than Plausible pageviews. Normalization layer converts both to `ProductMetric` schema before the agent sees them. |
| Legal | `contracts.json` | PDF upload → LLM extraction | **Accuracy:** Contract clause extraction via LLM is ~90% accurate. Requires human review step before clauses are used for cascade detection. False positive contract breach alerts are the highest-stakes failure mode. |
| Code Audit | `codebase_audit.json` | GitHub API (blame, PRs) + `pip-audit`/`npm audit` | **Scale:** `git blame` on large repos is expensive. Pre-compute ownership maps nightly, cache results, update incrementally on push webhooks. |

**The hackathon architecture enables this transition** because every agent reads from a normalized schema (`DeveloperActivity`, `FinancialRecord`, `ServiceHealth`, etc.), not from raw data files. Swapping the data source means swapping the loader function, not the agent logic or the cascade mapper.

### Cost model

| Scale | Companies | Gemini calls/day | GPT-4o-mini calls/day | API cost/day | Revenue/day | Margin |
|-------|-----------|------------------|-----------------------|-------------|-------------|--------|
| Hackathon | 1 | ~100 | ~10 | ~$0.50 | $0 | N/A |
| 50 companies | 50 | 5,000 | 500 | ~$25 | $833 | 97% |
| 500 companies | 500 | 50,000 | 5,000 | ~$200 | $8,333 | 97.6% |
| 5,000 companies | 5,000 | 500,000 | 50,000 | ~$1,800 | $83,333 | 97.8% |

API costs are 2.2% of revenue at scale. GPT-4o-mini Finance node is ~10x cheaper per call than Gemini nodes, which actually makes the cross-provider architecture more cost-efficient than running everything on Gemini.

---

## Execution plan

### Current status: Saturday evening

Backend agent nodes and frontend scaffold are done. We are now in the **agent collaboration and cascade detection** phase — the critical path to a working demo.

### Day 1 — remaining work (Saturday evening – midnight)

**Completed earlier today (for context — not claiming credit for hackathon-time work):**
- ✅ Repo setup, FastAPI + React scaffold, deployment pipeline
- ✅ DEADPOOLState TypedDict, Pydantic schemas, entity key constants
- ✅ All 6 specialist agent nodes (Gemini × 5 + GPT-4o-mini × 1) producing AgentReport outputs
- ✅ Synthetic data files loaded and verified
- ✅ Gemini + OpenAI API integrations tested

**Now – 8:00 PM (agent collaboration sprint):**
- Dev 1 + Dev 2: Tune specialist prompts — ensure cross_reference_hints are populated correctly in anomaly outputs. Test that entity keys match across agents.
- Dev 3: **Head Supervisor node** — build the LangGraph StateGraph, implement `supervisor_router`, wire conditional edges, implement corroboration loop with iteration guard. This is the hardest remaining piece.
- Dev 4: **Dashboard: table-based cascade view** (the guaranteed fallback). Risk score display. Briefing panel. Activity log component shell.
- Dev 5: **SSE streaming** — FastAPI SSE endpoint, React SSE client, wire one dummy event end-to-end.

**8:00 – 10:00 PM (cascade detection sprint):**
- Dev 3: **Cascade mapper** — NetworkX BFS, probability multiplication, `TRIGGER_MAP`, chain pruning at 0.25 threshold. Wire into LangGraph graph after Head Supervisor.
- Dev 1 + Dev 2: **Integration testing** — invoke full graph with `app.invoke()`, verify the primary cascade fires (People → Code Audit → Infra → Legal → Finance). Debug entity key mismatches, schema parsing failures, corroboration routing errors.
- Dev 4: **D3 cascade graph** — start the upgrade from table view. Color-coded nodes, edge thickness, basic click-to-expand.
- Dev 5: Wire SSE to real graph output. Dashboard receives live cascade chains and briefings. Deploy current state to Railway + Vercel.

**10:00 PM – midnight (buffer + polish):**
- All: Fix whatever broke in integration. If primary cascade works end-to-end:
  - Dev 3: Refine corroboration loop — test multi-step routing
  - Dev 4: Continue D3 polish
  - Dev 5: Landing page with signup form
- If primary cascade does NOT work:
  - Dev 3 + Dev 1 + Dev 2: All-hands on cascade detection debugging
  - Dev 4: Ensure table fallback renders whatever data exists
  - Dev 5: Ensure deployment is stable

**Tier 1 must be functional before anyone sleeps.** The definition of "functional": `app.invoke()` produces a CascadeChain, the dashboard renders it (table or D3), and the risk score + briefing display.

### Day 2 — Polish and demo prep (9:00 AM – 2:30 PM)

**9:00 – 10:30 AM:**
- Dev 1: What-If simulation mode (Tier 2) — only if Tier 1 is solid.
- Dev 2: Prompt refinement — ensure noise signals (Greenleaf overdue invoices, normal developer vacation) don't trigger false cascades.
- Dev 3: Cross-provider highlighting in activity log. Second cascade detection (CVE → compliance → legal).
- Dev 4: D3 cascade graph polish (if started last night) or cascade animation (Tier 2).
- Dev 5: Drive signups — LinkedIn post with demo GIF, hackathon Slack sharing, in-person demos to other teams.

**10:30 AM – 12:00 PM:**
- All: Tier 2 features if time permits. Alert toasts (Tier 3) only if everything else is done.
- **Code freeze at 11:30 AM** for Tier 3 items. Only bug fixes after.
- Dev 5: Final deployment. Pre-cache one graph execution result in frontend (WiFi contingency).

**12:00 – 1:30 PM:** Demo rehearsal ×3. All 5 team members watch each run. Practice: story → architecture → live cascade → What-If (if built) → traction. Time each run strictly to 3 minutes. Prepare for technical questions: "Show me the reasoning trace," "What's the false positive rate?", "Why two different models?", "How does the cascade mapper work?"

**1:30 – 2:30 PM:** Final polish. Hard code freeze. Verify deployment is live. Prepare backup screenshots in case of demo-day WiFi issues.

---

## Demo script (3 minutes)

**0:00 – 0:30 | The hook.**
"Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — seven AI agents, two model providers, one mission: see the kill chain before it kills you."

**0:30 – 0:50 | Architecture.**
Show LangGraph graph. "Six specialists monitor every layer of your company. Five on Gemini, one on GPT-4o-mini — because when agents on different model families independently agree, that's a stronger signal than one model agreeing with itself. One Head Supervisor connects them via conditional graph edges."

**0:50 – 1:50 | Live cascade.**
Walk through cascade on dashboard. "People Agent detected a 94% commit drop. Code Audit confirmed the vulnerability. Legal flagged the contract deadline. Then Finance — running on GPT-4o-mini, separate data — independently calculated: 42% revenue vanishes, runway drops to 2.5 months, down-round triggers. Two model families, different data, same conclusion. Click any node — see exactly why each agent flagged it."

**1:50 – 2:15 | [If built] What-If mode / [If not] Traction.**
If What-If ships: toggle simulation, adjust sliders, show cascade probability dropping. If not: skip directly to traction.

**2:15 – 2:45 | Traction.**
Show landing page + signup count. "[X] founders signed up in 20 hours."

**2:45 – 3:00 | Close.**
"Every startup has a DEADPOOL score right now. Most founders don't know theirs. Now they can."

---

## Why this wins

**Graph-native orchestration:** The cascade detection problem is structurally isomorphic to graph traversal. LangGraph's `StateGraph` with conditional edges, parallel fan-out, and typed state is the right primitive — not a pipeline of sequential API calls.

**Multi-provider corroboration:** When Gemini and GPT-4o-mini independently reach the same conclusion from different data, that's model-independent confidence. Single-provider systems cannot replicate this.

**Quantified impact:** $1.4M average cascade cost. 230x ROI. <60 second time-to-insight vs. weeks-to-never. $204M TAM.

**Production-ready architecture:** `MemorySaver` → `PostgresSaver` is one line. Multi-tenant is a `thread_id`. Specialist nodes extract to microservices by swapping the function body. API costs at 2.2% of revenue at 5,000 companies.

**Honest feasibility:** We scope to what ships in 24 hours. Tier 1 features are the commitment. Code will match the plan. We don't scaffold 10 features and ship 3.

**Compounding data moat:** Every monitoring cycle builds company-specific operational intelligence in the checkpoint store. Switching cost = losing your accumulated risk model.

---

## Differentiation strategy

1. **Orchestration complexity as moat:** A 7-node LangGraph with conditional cross-domain routing is an order of magnitude harder to build than a single-domain AI dashboard. Linear can't add this by shipping a feature.

2. **Compounding data moat:** Checkpoint memory learns which signals are predictive *for this specific company*. 6 months of history is irreplaceable.

3. **Cross-domain entity graph as defensibility:** The entity mapping (who owns what, what depends on what) is proprietary organizational knowledge encoded as graph edges. Deeply sticky once configured.

4. **Multi-provider corroboration:** Architectural advantage single-provider systems can't replicate without intentional cross-provider engineering.

5. **DEADPOOL score as viral wedge:** Single number, shareable, creates FOMO. "What's your DEADPOOL score?"

---

## Request for Hacks alignment

**RFH #02 — Agents That Hire Agents:** Head Supervisor dynamically routes to specialists via conditional edges — including across model providers. The `supervisor_router` is the hiring decision.

**RFH #04 — Intent as Code:** The cascade dependency graph is operational intent as configuration. `DEADPOOLState` carries company priorities through every node.

**RFH #05 — The Product That Builds Itself:** `MemorySaver` checkpoints compound across cycles. The supervisor adjusts probabilities based on which signals proved predictive.

**RFH #07 — The One-Person Billion-Dollar Company:** Seven agents, two providers, one unified briefing. A founder's virtual COO.

---

## Success criteria

### Tier 1 (must achieve — code will be measured against these)
- All 7 LangGraph nodes running with structured outputs writing to `DEADPOOLState`
- LangGraph conditional edges driving cross-node routing (visible in activity log)
- Primary cascade detected spanning 4+ domains crossing the Gemini → GPT-4o-mini boundary
- Dashboard displaying: cascade graph (table or D3), risk score, briefing, activity log
- SSE streaming live updates from backend to frontend
- Landing page live with signup form
- 50+ landing page signups

### Tier 2 (should achieve)
- What-If simulation mode with slider-driven graph re-invocation
- Cross-provider corroboration highlighted in activity log
- D3 animated cascade graph (upgrade from table fallback)

### Tier 3 (stretch)
- Alert toast notifications
- Multiple simultaneous cascade rendering
- LangGraph execution trace visualization

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities.*
*Built at the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*
*Powered by: Google Gemini 2.5 Flash + OpenAI GPT-4o-mini + LangGraph*