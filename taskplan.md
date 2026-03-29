# DEADPOOL — Task Plan

---

## Phase 1 — Data Source Integration

Define and wire the real data source for each specialist agent.

### People Agent
- [ ] Slack API only(use logic from slack_client.py): connect `slack_client.py` to the developer channel. Pull message frequency, response times, and user activity per developer. Map Slack user IDs to GitHub handles via a config file.
- [ ] Output: structured engagement signals per developer (message frequency, response time, silence duration) passed to the agent prompt.

### Finance Agent
- [ ] CSV ingestion: accept upload of `deadpool_finance_data.csv`, `deadpool_revenue_pipeline.csv`, `deadpool_funding_runway.csv`.
- [ ] Parse and validate with Pydantic before passing to GPT-4o-mini.
- [ ] Ensure column names and types are documented so companies know what format to provide.

### Legal Agent
- [ ] PDF ingestion: use `pdfplumber` or `pypdf` to extract text from uploaded contract PDFs.
- [ ] Web search tool: integrate `serpapi` or `duckduckgo-search` for regulatory lookups (Federal Register, SEC EDGAR).
- [ ] Chunk long contracts before passing to Gemini (stay within context limits).

### Product Agent
- [ ] Reddit API (`praw`): search for subreddits relevant to the product, pull recent posts/comments mentioning the product name. Sentiment signal. (ignore this data source for now)
- [ ] User engagement CSV(product_data.csv): accept upload with columns for weekly active users, feature-level engagement, NPS, support ticket volume. Parse and validate.

### Infra Agent
- [ ] GitHub Actions API: fetch recent workflow runs — pass/fail rate, deploy frequency per service, workflow duration trends.
- [ ] Json file explaining the infrastructure ( ignore this data source for now )

### Code Audit Agent
- [ ] GitHub commit history: reuse logic from `backend/get_commit_history.py` to fetch per-developer commit frequency, commit volume trends, and file-level change frequency. Maps `developer_name` to owned files and services.
- [ ] GitHub REST API: git blame per critical file to establish code ownership, PR open/merge/review counts, PR review patterns (merged without review?), stale PRs. Same GitHub token as Infra Agent.
- [ ] GitHub Dependabot Alerts API: fetch all open CVE alerts with severity and affected package. Same token — no extra credentials needed.

---

## Phase 2 — Individual Agent Testing

Test each agent in isolation. Confirm it fetches data correctly, calls its model, and returns a valid `AgentReport` with `Anomaly` objects.

### Test checklist per agent
- [ ] Data fetches without error (API call succeeds, CSV parses, PDF extracts)
- [ ] Raw data passed to model produces a valid JSON response
- [ ] Response parses into `AgentReport` via Pydantic without errors
- [ ] `Anomaly` objects have correct `agent_domain`, non-null `severity`, `confidence`, `affected_entities`, and `cross_reference_hints`
- [ ] `cross_reference_hints` reference real entity keys (`developer_name`, `service_name`, `client_name`, `feature_name`) that exist in other agents' data

### Per-agent specific tests
- **People**: confirm Sarah Chen (or equivalent trigger developer) shows up as a flagged anomaly with `agent_domain="people"` and `cross_reference_hints` pointing to a service name.
- **Finance**: confirm Nexus Corp revenue concentration anomaly is detected. Confirm runway calculation matches manual calculation from CSV.
- **Legal**: confirm contract deadline anomaly is extracted from PDF. Confirm `cross_reference_hints` references the correct service and client names.
- **Product**: confirm Reddit sentiment anomaly is generated. Confirm feature-level engagement decline is flagged.
- **Infra**: confirm payments-service deploy frequency anomaly is detected. Confirm `service_name` matches Code Audit and Legal data.
- **Code Audit**: confirm CVE anomaly is detected with CVSS score. Confirm bus factor = 1 is detected for payments-service. Confirm `developer_name` matches People agent data.

---

## Phase 3 — LangGraph Node Definition

Define each agent as a LangGraph node and wire the `StateGraph`.

- [ ] Define `DEADPOOLState` TypedDict with all required keys and `Annotated[list, operator.add]` reducer for `anomalies`.
- [ ] Wrap each agent's `run()` method as a LangGraph node function: accepts `DEADPOOLState`, returns state delta dict.
- [ ] Implement `initial_fanout` function using the `Send` API to dispatch all six specialists in parallel.
- [ ] Implement `head_supervisor_node`: reads all `domain_reports`, calls Gemini to reason about cross-domain implications, writes `corroboration_queue` and increments `iteration`.
- [ ] Implement `supervisor_router`: reads `corroboration_queue` and `iteration`, returns list of node names or `"cascade_mapper"`.
- [ ] Implement `cascade_mapper_node`: wraps existing `cascade_mapper.py` logic as a node, reads `anomalies` from state, writes `cascade_chains`.
- [ ] Implement `briefing_node`: ranks cascades by urgency, calls Gemini for founder briefing, writes `risk_score` and `briefing`.
- [ ] Add all nodes and edges to `StateGraph`. Add `MemorySaver` checkpointer. Compile the graph.
- [ ] Update `main.py` to invoke the compiled graph instead of the current direct agent calls.

---

## Phase 4 — Multi-Agent Orchestration Testing

Test the full graph end-to-end.

- [ ] Run `app.invoke()` with a `thread_id` and the demo synthetic data. Confirm the graph completes without hanging.
- [ ] Verify `iteration` counter caps corroboration at 2 passes — add an assertion that `state["iteration"] <= 2` at `END`.
- [ ] Verify the primary cascade (People → Code Audit → Infra → Legal → Finance → Finance investor) is detected and appears in `cascade_chains`.
- [ ] Verify cross-provider corroboration: Legal (Gemini) and Finance (GPT-4o-mini) both flag the Nexus Corp risk. Head Supervisor notes this as model-independent corroboration in state.
- [ ] Verify `MemorySaver` persists state: invoke the graph twice with the same `thread_id`. Second invocation should read prior checkpoint and adjust cascade probabilities.
- [ ] Test the `whatif_params` flow: inject `{"scenario_type": "engineer_leaves", "severity_multiplier": 1.5}` into state. Confirm People anomaly severity is boosted and cascade probability increases.
- [ ] Test SSE streaming: confirm `signal_bus` events flow to the React dashboard in real time as nodes complete.
- [ ] Test graceful degradation: mock one specialist to raise an exception. Confirm the graph continues with remaining agents and returns a partial result rather than failing entirely.

---

## Milestones

| Milestone | Done when |
|-----------|-----------|
| Phase 1 complete | All 6 agents fetch real data without errors |
| Phase 2 complete | All 6 agents individually return valid `AgentReport` with expected anomalies |
| Phase 3 complete | `app.invoke()` runs the full compiled graph without errors on synthetic data |
| Phase 4 complete | Primary cascade detected end-to-end, cross-provider corroboration visible in state, What-If mode works |
