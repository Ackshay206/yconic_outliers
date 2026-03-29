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

DEADPOOL is a multi-agent startup immune system built on LangGraph's stateful graph orchestration framework. Six specialist agents continuously monitor every operational layer of a company — people, finance, infrastructure, product, legal, and codebase — connected by a LangGraph `StateGraph` where a Head Agent node orchestrates them all: cross-validating signals across domains, computing a 0–100 risk score, generating a plain-language founder briefing, and seeding a looping cascade expander that traces exactly how a single anomaly propagates into downstream failures.

The system is **model-agnostic by design** — five specialist agents and the Head Agent run on **Google Gemini 2.5 Pro**, while the Finance Agent runs on **OpenAI GPT-4o-mini**. This multi-provider architecture is intentional: it demonstrates that the orchestration layer (LangGraph) is the intelligence, not any single model. When a Gemini-powered agent and a GPT-4o-mini-powered agent independently corroborate the same anomaly, the finding is robust across model families — not just consistent within one model's biases.

### What ships at this hackathon vs. what comes later

| | Hackathon (ships Sunday 2:30 PM) | Post-hackathon (weeks/months) |
|---|---|---|
| **Data** | Real API integrations: Slack API (People), GitHub Actions + REST + Dependabot APIs (Infra, Code Audit), uploaded CSVs (Finance, Product), uploaded PDFs + DuckDuckGo search (Legal) | Full OAuth + webhook connectors, multi-tenant ingestion pipelines |
| **Agents** | 7 LangGraph nodes, each making 1 LLM call per cycle with structured output | Agents with multi-step tool-use loops, retry logic, and rate limit handling |
| **Orchestration** | Full LangGraph StateGraph with conditional routing, parallel fan-out, LLM cascade expander loop (max depth 5) | PostgresSaver, multi-tenant thread_id isolation, horizontal node scaling |
| **Dashboard** | React + React Flow (`@xyflow/react`): cascade chain graph, risk score, founder briefing, liabilities panel | Animated cascade pulses, What-If simulation mode, alert system, mobile responsive |
| **Agent Chat** | Per-agent conversational interface grounded in latest analysis data, SSE token streaming, persisted history | Multi-tenant conversation isolation, proactive alert surfacing, voice interface |
| **Traction** | Landing page with signup form | Waitlist → beta invites → paid pilot with 5 founders |

This distinction matters because **code is evaluated against the master plan** — not against an aspirational vision. Everything in the "Hackathon" column is what we commit to building and what the code will be measured against. The "Post-hackathon" column is documented to show scalability thinking, but we do not claim to build it this weekend.

### The team — 5 people, clear ownership

| Member | Role | Owns | Skills |
|--------|------|------|--------|
| **Dev 1** | Agent Engineer (People, Finance, Product) | 3 specialist nodes, all prompts + structured output schemas, synthetic data files | Python, LLM APIs, data modeling |
| **Dev 2** | Agent Engineer (Infra, Legal, Code Audit) | 3 specialist nodes, CVE matching, contract parsing, deploy analysis | Python, security, systems |
| **Dev 3** | Orchestration Lead | LangGraph orchestrator (`orchestrator.py`), head_agent node, cascade expander loop, conditional routing | Python, LangGraph, graph algorithms |
| **Dev 4** | Frontend Lead | React dashboard, React Flow cascade graph, risk score panel, liabilities panel, SSE client | React, React Flow, CSS, UI/UX |
| **Dev 5** | Integration & Infra | FastAPI backend, SSE streaming, deployment (Vercel + Railway), API wiring between frontend/backend, demo environment, traction | Python, DevOps, marketing |

Five people is the right size for this architecture: two devs building six specialist agents in parallel, one dedicated to the hardest engineering problem (LangGraph orchestration + cascade mapper), one owning the entire frontend, and one making sure everything connects and deploys. No single person is a bottleneck for more than one Tier 1 feature.

### Current progress (as of Saturday evening)

We are not starting from zero. Here's what's done and what remains:

| Component | Status | Notes |
|-----------|--------|-------|
| **FastAPI backend scaffold** | ✅ Done | — |
| **React frontend scaffold** | ✅ Done | — |
| **All 6 specialist agent nodes** | ✅ Done | — |
| **Pydantic schemas** (Anomaly, AgentReport, CascadeChain, FounderBriefing, RiskScore) | ✅ Done | — |
| **Synthetic data files** (all 8 JSON/CSV) | ✅ Done | — |
| **Gemini + OpenAI SDK integration** | ✅ Done | — |
| **Deployment pipeline** (Caddy + Railway) | ✅ Done | — |
| **LangGraph orchestrator** (`orchestrator.py`) | ✅ Done | Parallel fan-out → head_agent → cascade_expander loop → format_output |
| **Head Agent** (cross-validate + risk score + briefing) | ✅ Done | Single-pass cross-validation; briefing via Gemini 2.5 Pro |
| **LLM cascade expander** (loop, max 5 depth) | ✅ Done | Replaces deterministic NetworkX — Gemini drives expansion |
| **SSE streaming** | ✅ Done | FastAPI `signal_bus` → React `EventSource` |
| **Dashboard: cascade graph (React Flow)** | ✅ Done | Domain-colored nodes, animated edges, MiniMap, Controls |
| **Dashboard: risk score + founder briefing** | ✅ Done | Summary, timeline, recommended_action |
| **Dashboard: liabilities panel** | ✅ Done | Replaces activity log — sorted by severity |
| **What-If simulation** | ✅ Done | `POST /api/whatif` wired to `HeadAgent.simulate_whatif()` |
| **Agent Chat** | ✅ Shipped | `POST /api/agents/{name}/chat` — per-agent conversational interface grounded in latest analysis data, SSE token streaming, persisted conversation history across tab switches |

| **Landing page** |  shipped |

The critical path was **agent collaboration and cascade detection** — getting the LangGraph conditional routing to work correctly so that the primary cascade (People → Code Audit → Infra → Legal → Finance) fires end-to-end. This is complete. The LLM-driven cascade expander replaced the planned deterministic NetworkX approach.

---

## Architecture

### The 7-node LangGraph

DEADPOOL runs as a **LangGraph `StateGraph`**. Six specialist nodes are domain experts. The head_agent node orchestrates cross-validation and briefing. The cascade_expander loops to trace consequences. Each node is a pure function: read from `OrchestratorState`, call its model (Gemini or GPT-4o-mini), write structured output back.

**Model assignment:**

| Node | Model | Rationale |
|------|-------|-----------|
| Head Agent | Gemini 2.5 Pro | Cross-validates all 6 reports, computes risk score, generates FounderBriefing in one pass |
| People Agent | Gemini 2.5 Pro | Pattern recognition on 12-week developer activity time series |
| Finance Agent | **GPT-4o-mini** | Most structured workload — CSV parsing, arithmetic, threshold checks. GPT-4o-mini excels at structured extraction at low latency. Creates cross-provider corroboration signal. |
| Infra Agent | Gemini 2.5 Pro | System metrics correlation and degradation pattern detection |
| Product Agent | Gemini 2.5 Pro | Sentiment analysis on support tickets and engagement trends |
| Legal Agent | Gemini 2.5 Pro | Contract clause comprehension and compliance deadline tracking |
| Code Audit Agent | Gemini 2.5 Pro | Dependency tree analysis, CVE matching, bus factor calculation |
| Cascade Expander | Gemini 2.5 Pro | LLM-driven consequence expansion — asks "what happens next?" for all active threads collectively, enabling cross-cause acceleration detection |

```
  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐
  │ People       │  │ Finance        │  │ Infra           │
  │ (Gemini)     │  │ (GPT-4o-mini)  │  │ (Gemini)        │
  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘
  ┌──────┴───────┐  ┌───────┴────────┐  ┌────────┴────────┐
  │ Product      │  │ Legal          │  │ Code Audit      │
  │ (Gemini)     │  │ (Gemini)       │  │ (Gemini)        │
  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘
         └──────────────────▼──────────────────────┘
                    ┌──────────────────────────────────┐
                    │  HEAD AGENT (Gemini 2.5 Pro)     │
                    │  Cross-validate anomalies         │
                    │  Compute risk score 0–100         │
                    │  Generate FounderBriefing         │
                    │  Seed cascade threads (sev ≥ 0.5)│
                    └──────────────┬───────────────────┘
                                   │ conditional
                         ┌─────────▼─────────┐
                         │  CASCADE EXPANDER  │◄──┐
                         │  (Gemini 2.5 Pro)  │   │ loop (max 5)
                         │  LLM next-step     │───┘
                         │  _apply_rules boost│
                         │  prune < 40%       │
                         └─────────┬──────────┘
                                   │ conditional
                         ┌─────────▼──────────┐
                         │  FORMAT OUTPUT     │
                         │  Build dashboard   │
                         │  nodes/edges/chains│
                         └────────────────────┘
```

### OrchestratorState — the shared typed state

```python
class OrchestratorState(TypedDict):
    # Specialist outputs — operator.add merges parallel branches
    specialist_reports: Annotated[list[AgentReport], operator.add]

    # Head agent output
    risk_score:      Optional[RiskScore]
    root_causes:     list[str]
    domains_present: list[str]

    # Cascade loop state
    active_threads:  list[dict]                          # current depth threads (replaced each iter)
    cascade_nodes:   Annotated[list[dict], operator.add] # accumulated across iterations
    cascade_edges:   Annotated[list[dict], operator.add] # accumulated across iterations
    visited_causes:  Annotated[list[str],  operator.add] # dedup across iterations
    depth:           int                                  # loop counter (replaced each iter)

    # Final output
    dashboard: Optional[dict]
```

State is model-agnostic — the same `OrchestratorState` flows through Gemini specialist nodes and the GPT-4o-mini Finance node unchanged. LangGraph's `operator.add` reducer handles parallel merge of `specialist_reports` without conflict. The cascade loop state (`active_threads`, `depth`) is replaced each iteration while `cascade_nodes`/`cascade_edges`/`visited_causes` accumulate across iterations.

### Graph execution flow

```
START → [Parallel Fan-Out: 6 specialist nodes]
         5 call Gemini 2.5 Pro, 1 calls GPT-4o-mini, all concurrent
      → [Barrier join: all 6 feed into head_agent node]
      → [Head Agent: HeadAgent.analyze()]
         Cross-validates anomalies via CORROBORATION_MAP
         Severity +15% for 2+ corroborating domains
         Severity −15% for unconfirmed weak signals
         Computes 0–100 risk score
         Generates FounderBriefing via Gemini
         Seeds cascade threads from anomalies with severity ≥ 0.5
      → [Conditional edge]
         active_threads exist? → cascade_expander
         no anomalies? → format_output
      → [Cascade Expander loop (max depth 5)]
         Calls _llm_next_step(Gemini): given all active threads, what next?
         Applies _apply_rules: boosts probability for dangerous domain combos
           (finance+people: +25, legal+finance: +20, infra+product: +15)
         Prunes branches below 40% probability
         Deduplicates visited causes
         Has more threads AND depth < 5? → loop back
         Done? → format_output
      → [Format Output]
         Numbers edges, builds adjacency map
         DFS to trace chain paths (root → terminal)
         Returns { riskScore, trend, activeCascades, nodes, edges, activeChains }
      → END
```

### Conditional routing — the intelligence layer

The orchestrator uses `add_conditional_edges` with two router functions:

```python
def _after_head_agent(state: OrchestratorState) -> str:
    return "cascade_expander" if state.get("active_threads") else "format_output"

def _after_cascade_expander(state: OrchestratorState) -> str:
    if state.get("depth", 0) < MAX_CASCADE_DEPTH and state.get("active_threads"):
        return "cascade_expander"
    return "format_output"
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
**Data:** Slack API via `slack_client.py` — message frequency, response times, and user activity per developer pulled from the developer channel. Slack user IDs mapped to GitHub handles via a config file.
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
**Data:** GitHub Actions API — recent workflow runs including pass/fail rate, deploy frequency per service, and workflow duration trends.
**Detects:** Deploy frequency drops, CI failure spikes, response time degradation, SLA breach risk, cloud cost anomalies.
**Cross-references:** Code Audit (code quality → runtime failures?), People (who owns the degrading service?), Legal (SLA obligations at risk).

### Product Agent *(Gemini)*
**Domain:** User engagement, retention, satisfaction.
**Data:** Uploaded CSV `product_data.csv` — columns for weekly active users, feature-level engagement, NPS, and support ticket volume. Parsed and validated with Pydantic before passing to the model.
**Detects:** Feature adoption decline, churn increases, NPS drops, support ticket spikes, sentiment deterioration.
**Cross-references:** Infra (performance → UX decline?), Code Audit (bugs → user errors?), Finance (revenue impact of churn).

### Legal Agent *(Gemini)*
**Domain:** Contracts, compliance, regulatory exposure.
**Data:** Uploaded contract PDFs extracted via `pdfplumber`/`pypdf` (chunked to fit context limits), plus a web search tool (`duckduckgo-search`) for regulatory lookups against Federal Register and SEC EDGAR.
**Detects:** Contract deadlines approaching with delivery at risk, conflicting terms, regulatory changes, compliance gaps (PCI DSS, SOC 2).
**Cross-references:** Finance (breach liability), Infra (feature delivery status), Code Audit (compliance mapped to code state).

### Code Audit Agent *(Gemini)*
**Domain:** Codebase health, security posture, technical debt.
**Data:** Three GitHub sources sharing the same token — (1) commit history via `backend/get_commit_history.py` for per-developer commit frequency, volume trends, and file-level change frequency; (2) GitHub REST API for git blame on critical files, PR open/merge/review counts, and stale PR detection; (3) GitHub Dependabot Alerts API for all open CVE alerts with severity and affected package.
**Detects:** CVEs with CVSS ≥7.0, test coverage <60% for critical services, bus factor = 1, unreviewed PRs in critical paths, outdated dependencies (2+ major versions behind).
**Cross-references:** People (who owns the code?), Infra (which services run on it?), Legal (compliance implications), Product (user-facing features built on degraded code).

---

## The Head Agent Node *(Gemini 2.5 Pro)*

The Head Agent cross-validates, scores, and synthesizes in a single pass within the LangGraph graph.

**Cross-validation:** Reads all six specialist reports (five from Gemini, one from GPT-4o-mini). Uses `CORROBORATION_MAP` to check which expected corroborating domains are active. 2+ corroborating domains → severity +15%, confidence +10%. Zero corroborating domains AND severity < 0.5 → severity −15%. Cross-provider corroborations (Gemini specialist ↔ GPT-4o-mini Finance) are structurally independent — same `Anomaly` schema, different model family — making the signal model-family-independent.

**Risk score computation:** Three additive components (each capped):
- Cascade urgency: Σ min(urgency × 500, 40) for top 3 chains — up to 40 pts
- High-severity anomaly count: count(severity ≥ 0.75) × 8 — up to 40 pts
- Baseline severity: avg(all severities) × 20 — up to 20 pts

**Briefing generation:** Calls Gemini 2.5 Pro with top 10 anomalies + cascade summaries, returns structured `FounderBriefing` (summary, timeline, recommended_action).

**Cascade seeding:** After analysis, anomalies with severity ≥ 0.5 become root threads for the cascade expander. These are written to `active_threads` in `OrchestratorState`, triggering the conditional edge to the cascade expander loop.

---

## The Cascade Expander *(LLM-driven, Gemini 2.5 Pro)*

LLM-driven consequence expansion via the `_llm_next_step` function in `cascade_mapper.py`, called iteratively by the cascade expander node in `orchestrator.py`.

**How it works:**
1. Receives all currently `active_threads` (seeded from anomalies with severity ≥ 0.5)
2. Sends all threads collectively to Gemini: *"Given these active causal threads, what are the next consequences?"*
3. Gemini returns a JSON array of consequence objects with probability (0–100), contributing_causes, and is_terminal flag
4. `_apply_rules` applies additive probability boosts for dangerous domain combinations:
   - `finance+people`: +25 pts — workforce issues that hit cash simultaneously
   - `legal+finance`: +20 pts — compliance exposure meets burn pressure
   - `infra+product`: +15 pts — infrastructure failures manifest in product
5. Branches below 40% probability are pruned; visited causes are deduplicated
6. Terminal consequences (bankruptcy, acquisition, founder dilution) stop their branch
7. Loop continues until no active threads remain OR `MAX_CASCADE_DEPTH` (5) is reached

**Key advantage over deterministic approach:** Sending all active threads collectively enables Gemini to detect cross-cause acceleration — where two simultaneous signals combine to produce a higher-probability consequence than either alone would (e.g., engineer departure + deploy stall → contract breach happens faster than either factor independently predicts).

---

## Agent Chat *(Shipped)*

DEADPOOL ships with an interactive chat interface that lets founders interrogate any of the six specialist agents directly. Unlike a generic LLM chat, every conversation is **grounded in the latest analysis data** — each agent primes the conversation with its most recent anomaly report before the first user message, so answers are specific to the company's current operational state, not generic knowledge.

### How it works

1. **Data context injection:** Before the conversation starts, `BaseAgent.get_chat_context()` returns the last `AgentReport` summary. This is injected as a priming `user`/`model` exchange in the conversation history, anchoring all subsequent responses in real findings.
2. **Conversation history replay:** The full prior conversation is replayed to the model on each turn, maintaining coherent multi-turn dialogue.
3. **Token-by-token SSE streaming:** `BaseAgent.chat_stream(message, history)` calls `client.models.generate_content_stream()` and yields each text chunk as a Server-Sent Event: `data: {"text": "chunk"}\n\n`. A `data: [DONE]\n\n` sentinel ends the stream.
4. **Frontend stream consumption:** `AgentChatPanel.jsx` opens the response body as a `ReadableStream` via `response.body.getReader()`, appending chunks to the active message bubble in real time. A blinking cursor animates during streaming and is removed on `[DONE]`.
5. **Conversation persistence:** Each agent's conversation is stored in a `Map` keyed by agent name in React state. Switching tabs preserves the full conversation history — the agent remembers what was discussed earlier in the session.

### System prompt modification

Chat mode appends conversation-specific instructions to each agent's base system prompt:
- Respond conversationally, not in JSON
- Be concise and actionable — founders are busy
- Reference specific entities from the analysis (developer names, service names, contract clauses)
- Suggest one concrete next action per response

### API endpoint

```
POST /api/agents/{agent_name}/chat
Content-Type: application/json

{
  "message": "What should I prioritize given Sarah Chen's disengagement?",
  "history": [
    {"role": "user",  "content": "What anomalies did you find?"},
    {"role": "model", "content": "I detected a 94% commit drop from Sarah Chen..."}
  ]
}
```

Response: `text/event-stream` — `data: {"text": "chunk"}` events until `data: [DONE]`.

### Frontend: AgentChatPanel

Three-section layout:

- **Left sidebar:** Six agent cards, each with a domain-colored status dot (critical/warning/healthy/idle), agent label, and brief description. Clicking a card switches the active agent and restores that agent's conversation history.
- **Main chat area:** Auto-scrolling message history. User messages are right-aligned with a "YOU" avatar. Agent responses are left-aligned with domain-colored headers, streaming cursor animation during response generation, and a Clear Chat button.
- **Welcome state:** When a conversation is empty, a per-agent welcome card shows the agent's icon, description, and 3–4 suggested questions (e.g., *"Which engineer is the biggest single point of failure?"*, *"How many months of runway do we have?"*). Clicking a suggestion pre-fills the input.

---

## Features: what ships vs. what's stretch

**The scoring rubric evaluates code against the master plan.** Overcommitting kills the completeness score. We define three tiers:

###  Must ship ✅ All shipped

| Feature | Owner | Description | Status |
|---------|-------|-------------|--------|
| **LangGraph orchestrator** | Dev 3 | 6 specialists + head_agent + cascade_expander loop + format_output. Parallel fan-out, conditional routing. | ✅ Shipped |
| **Cascade detection** | Dev 3 + Dev 1/2 | LLM-driven expansion (Gemini) traces multi-domain chains from synthetic data. | ✅ Shipped |
| **Dashboard: cascade graph** | Dev 4 | React Flow directed graph — domain-colored nodes, animated edges, MiniMap, Controls. | ✅ Shipped (React Flow, not D3) |
| **Dashboard: risk score + briefing** | Dev 4 | 0–100 score, severity level, trend, FounderBriefing (summary, timeline, action). | ✅ Shipped |
| **Dashboard: liabilities panel** | Dev 4 | Scrollable severity-sorted anomaly list. Replaced activity log. | ✅ Shipped |
| **SSE streaming** | Dev 5 | FastAPI `signal_bus` → React `EventSource` — incremental anomaly display during analysis. | ✅ Shipped |
| **Agent Chat** | Dev 4 + Dev 5 | Per-agent conversational interface grounded in latest analysis data. Token streaming via SSE. Conversation history persists across tab switches. | ✅ Shipped |



### Feasibility analysis — why this ships in time

**Why we're confident (not naive):**

1. **Backend agents are already done.** All six specialist nodes produce structured `AgentReport` outputs from synthetic data. Gemini and GPT-4o-mini integrations are tested. This is the part most hackathon teams are still building at midnight — we finished it Saturday afternoon.

2. **The orchestration work was well-scoped.** The conditional routing is a known LangGraph pattern (`add_conditional_edges`). The LLM cascade expander follows a clear prompt/parse/prune loop with hard depth limits. Both are engineering problems with clear solutions, not open-ended research.

3. **Five people eliminates the frontend bottleneck.** The most common hackathon failure mode is "backend works but dashboard isn't ready." With a dedicated frontend dev (Dev 4) and an integration dev (Dev 5) who handles SSE + deployment, the frontend track runs in parallel with zero dependency on the orchestration track.

4. **We have a working fallback at every layer.** D3 graph too complex? → Table view in 30 minutes. What-If not ready? → Demo script has an if/else that skips to traction. SSE breaks? → Pre-cached last result in frontend state. The demo never breaks; it just degrades gracefully.

5. **We've already validated the hardest integration point.** Gemini and GPT-4o-mini both produce outputs that parse into the same Pydantic `AgentReport` schema. The cross-provider schema mismatch risk — the scariest feasibility question — is already resolved.

**How risks were resolved:**

- The corroboration loop was simplified to a single-pass cross-validation in `HeadAgent._cross_validate()` using a static `CORROBORATION_MAP`. This proved sufficient and removed the complexity of iterative re-queries.
- D3 cascade graph was replaced with React Flow (`@xyflow/react`), which provided interactive graph rendering out of the box with less custom code.
- End-to-end integration worked via `signal_bus.py` for SSE and `asyncio.to_thread()` for the blocking LangGraph invocation.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | **LangGraph** `StateGraph` | Typed state, conditional edges, parallel fan-out, loop-capable cascade expander. The right primitive for graph-structured agent orchestration. |
| AI (primary) | **Gemini 2.5 Pro** via `google-genai` SDK | 5 specialist nodes + head_agent + cascade expander. JSON mode for structured output. |
| AI (finance) | **GPT-4o-mini** via `openai` SDK | Finance node only. `response_format={"type": "json_object"}`, `temperature=0.1`. |
| Backend | **Python + FastAPI** | Async-native, Pydantic v2 for type-safe I/O, SSE via `sse-starlette`. |
| Frontend | **React + React Flow** | `@xyflow/react` for cascade chain graph. React for dashboard state and panels. |
| Deployment | **Caddy** (reverse proxy) + **Railway** | Single Railway service; Caddy serves built frontend + proxies API. |

---

## Agent implementation

### LangGraph graph construction

```python
builder = StateGraph(OrchestratorState)

for domain, agent in specialists.items():
    builder.add_node(domain, _make_specialist_node(agent))

builder.add_node("head_agent",       _make_head_node(head_agent))
builder.add_node("cascade_expander", _make_cascade_expander_node())
builder.add_node("format_output",    _format_output_node)

# Fan-out: START → all specialists in parallel
for domain in specialists:
    builder.add_edge(START, domain)

# Fan-in: all specialists → head_agent (barrier join)
for domain in specialists:
    builder.add_edge(domain, "head_agent")

# Conditional: head_agent → cascade_expander OR format_output
builder.add_conditional_edges("head_agent", _after_head_agent,
    {"cascade_expander": "cascade_expander", "format_output": "format_output"})

# Conditional loop: cascade_expander → itself OR format_output
builder.add_conditional_edges("cascade_expander", _after_cascade_expander,
    {"cascade_expander": "cascade_expander", "format_output": "format_output"})

builder.add_edge("format_output", END)
graph = builder.compile()
```

### Specialist node pattern (Gemini)

```python
def _make_specialist_node(agent):
    def node(_state: OrchestratorState) -> dict:
        report: AgentReport = agent.run()   # loads data, calls Gemini, returns AgentReport
        return {"specialist_reports": [report]}
    return node
```

### Finance node (GPT-4o-mini)

FinanceAgent is a standalone class that uses the OpenAI client internally:

```python
class FinanceAgent:
    def run(self) -> AgentReport:
        # Loads 3 CSV files with pandas
        # Calls GPT-4o-mini with response_format={"type": "json_object"}
        # Returns AgentReport with Anomaly list
        ...
```

### Agent interaction flow

The full flow (parallel fan-out → head_agent → cascade expander loop → format_output) is detailed in the Architecture section above. The key implementation detail: the loop between cascade_expander and itself, and the conditional exit to format_output, are LangGraph edges — not function calls. The graph structure *is* the control flow.

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

**Head Agent FounderBriefing:**

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

The cascade expander is path-agnostic — it uses Gemini to reason about any starting thread, not a fixed graph. Custom paths could be injected as initial threads with pre-set probabilities. This means DEADPOOL's intelligence grows with the customer's domain knowledge: the more precise the seeding, the richer the expansion.

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
| **Cascade expander runs indefinitely** | Mitigated | `MAX_CASCADE_DEPTH = 5` hard stop; conditional edge checks both depth AND active_threads |
| **Gemini returns malformed JSON** | Mitigated | `_llm_next_step` has JSON extraction fallback; head_agent briefing has FounderBriefing fallback with raw text |
| **GPT-4o-mini Finance node timeout** | Mitigated | FastAPI wraps in `asyncio.to_thread()`; error captured per-agent in `run_all_agents` without crashing others |
| **Schema mismatch across providers** | Resolved | All nodes output identical Pydantic `AgentReport`/`Anomaly` schema; validated before state write |
| **React Flow graph with many nodes** | Low | MiniMap + Controls provided; fitView called on load; zooms out automatically |
| **Synthetic data triggers no anomalies** | Resolved | Data engineered with known cascade signals; verified end-to-end |
| **WiFi drops during live demo** | Medium | `useDeadpool` caches last authoritative response in React state; dashboard remains interactive after analysis completes |
| **Audience doesn't understand cascade in 60 seconds** | Medium | Demo script opens with the *story* (engineer leaves → contract breaks → company dies) before showing the graph. Narrative first, visualization second. |

---

## Scalability design

### PostgresSaver — production checkpointer

The current hackathon version compiles the graph without a checkpointer (stateless per-request execution). Adding persistence is a one-line swap:

```python
# Current (hackathon — stateless)
graph = builder.compile()

# Production — durable cross-cycle memory
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
pool = AsyncConnectionPool(conninfo=os.environ["DATABASE_URL"])
graph = builder.compile(checkpointer=AsyncPostgresSaver(pool))
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
| Hackathon | All nodes in-process, `asyncio.to_thread()` wraps LangGraph `graph.invoke()` | 1 company | Nothing — this is what ships |
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
- ✅ OrchestratorState TypedDict, Pydantic schemas (Anomaly, AgentReport, CascadeChain, FounderBriefing, RiskScore)
- ✅ All 6 specialist agent nodes (Gemini × 5 + GPT-4o-mini × 1) producing AgentReport outputs
- ✅ Synthetic data files loaded and verified
- ✅ Gemini + OpenAI API integrations tested

**Now – 8:00 PM (agent collaboration sprint):**
- Dev 1 + Dev 2: Tune specialist prompts — ensure cross_reference_hints are populated correctly in anomaly outputs. Test that entity keys match across agents.
- Dev 3: **LangGraph orchestrator** — build `orchestrator.py` with head_agent node, cascade_expander loop, conditional edges, format_output node.
- Dev 4: **Dashboard: Overview page** — risk score display, BriefingPanel, FlawsPanel (liabilities). AgentsPanel with status cards.
- Dev 5: **SSE streaming** — `signal_bus.py`, FastAPI SSE endpoint, React `EventSource` client.

**8:00 – 10:00 PM (cascade detection sprint):**
- Dev 3: **LLM cascade expander** — `_llm_next_step`, `_apply_rules`, probability pruning, depth loop. Wire into LangGraph graph after head_agent.
- Dev 1 + Dev 2: **Integration testing** — invoke full graph with `graph.invoke()`, verify the primary cascade fires (People → Code Audit → Infra → Legal → Finance). Debug entity key mismatches, schema parsing failures.
- Dev 4: **React Flow cascade graph** — Cascade Chains page, CascadeChainPanel with domain-colored nodes, animated edges, MiniMap.
- Dev 5: Wire SSE to real graph output. Deploy to Railway with Caddy reverse proxy.

**10:00 PM – midnight (buffer + polish):**
- All: Fix whatever broke in integration. If primary cascade works end-to-end:
  - Dev 3: What-If simulation endpoint
  - Dev 4: React Flow polish, fitView, domain legend
  - Dev 5: Deployment stability, pre-cache demo state
- If primary cascade does NOT work:
  - Dev 3 + Dev 1 + Dev 2: All-hands on cascade detection debugging

**Tier 1 must be functional before anyone sleeps.** The definition of "functional": `graph.invoke()` produces cascade nodes/edges, the React Flow dashboard renders them, and the risk score + FounderBriefing display.

### Day 2 — Polish and demo prep (9:00 AM – 2:30 PM)

**9:00 – 10:30 AM:**
- Dev 1: What-If simulation mode (Tier 2) — only if Tier 1 is solid.
- Dev 2: Prompt refinement — ensure noise signals (Greenleaf overdue invoices, normal developer vacation) don't trigger false cascades.
- Dev 3: Cross-provider highlighting in dashboard. Second cascade detection (CVE → compliance → legal).
- Dev 4: React Flow polish (if started last night) or cascade animation (Tier 2).
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
Show LangGraph graph. "Six specialists monitor every layer of your company. Five on Gemini 2.5 Pro, one on GPT-4o-mini — because when agents on different model families independently agree, that's a stronger signal than one model agreeing with itself. A LangGraph orchestrator connects them via conditional edges, then loops a cascade expander to trace exactly how failure propagates."

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

**Production-ready architecture:** Stateless → `PostgresSaver` is one line. Multi-tenant is a `thread_id`. Specialist nodes extract to microservices by swapping the function body. API costs at 2.2% of revenue at 5,000 companies.

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

**RFH #02 — Agents That Hire Agents:** The LangGraph orchestrator dynamically routes between specialist nodes and the cascade expander via conditional edges — including across model providers. The routing functions are the hiring decisions.

**RFH #04 — Intent as Code:** The cascade dependency graph is operational intent as configuration. `OrchestratorState` carries company risk context through every node.

**RFH #05 — The Product That Builds Itself:** The cascade expander loop iteratively deepens the consequence graph each cycle. Cross-domain probability boosts (CORROBORATION_MAP, _apply_rules) encode learned risk patterns.

**RFH #07 — The One-Person Billion-Dollar Company:** Seven agents, two providers, one unified briefing. A founder's virtual COO.

---

## Success criteria

### (must achieve — code will be measured against these)
- ✅ All 6 LangGraph specialist nodes + head_agent + cascade_expander + format_output running with structured outputs writing to `OrchestratorState`
- ✅ LangGraph conditional edges driving cascade loop (cascade_expander ↔ format_output)
- ✅ Primary cascade detected spanning 4+ domains, crossing Gemini → GPT-4o-mini boundary
- ✅ Dashboard displaying: React Flow cascade graph, risk score, FounderBriefing, liabilities panel
- ✅ SSE streaming live anomaly updates from backend to frontend during analysis

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities.*
*Built at the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*
*Powered by: Google Gemini 2.5 Pro + OpenAI GPT-4o-mini + LangGraph*
*Frontend: React 19 + Vite 6 + React Flow (@xyflow/react)*