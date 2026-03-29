# Orchestration Implementation — Task Plan

Implement LangGraph-based orchestration: run all 6 specialist agents in parallel, then have the Head Agent analyze all results and return a `risk_score` and `trigger_point` (most urgent cascade start).

---

## Model Assignments (enforced throughout)

| Agent | Model |
|---|---|
| People, Infra, Product, Legal, Code Audit | `gemini-2.5-flash` |
| Finance | `gpt-4o-mini` |
| Head Agent | `gemini-2.5-pro` |

---

## Task 1 — Fix model in `base_agent.py`

**File:** `backend/agents/base_agent.py`

The base class currently uses `gemini-2.5-pro`. All specialist agents inherit from it — change the model string to `gemini-2.5-flash`.

- [ ] Find the model string (e.g. `"gemini-2.5-pro"` or `"models/gemini-2.5-pro"`) in `BaseAgent.__init__` or `_call_model`
- [ ] Replace with `"gemini-2.5-flash"` (or whatever the correct SDK identifier is)
- [ ] Verify `finance_agent.py` still overrides to `gpt-4o-mini` (it should — don't change it)
- [ ] Verify `head_agent.py` still uses `gemini-2.5-pro` (it should — don't change it)

---

## Task 2 — Add `trigger_point` to `RiskScore` in `models.py`

**File:** `backend/models.py`

`trigger_point` = the single anomaly that, if it tips over, initiates the highest-probability cascade chain. It is the "pull this thread and everything unravels" signal.

- [ ] Add a `TriggerPoint` Pydantic model with fields:
  ```python
  class TriggerPoint(BaseModel):
      anomaly_id: str           # references Anomaly.id
      agent_domain: str         # e.g. "people"
      title: str                # human-readable: e.g. "Sarah Chen disengaging"
      cascade_chain_id: str     # references CascadeChain.id
      urgency_score: float      # 0–1, copied from the chain's urgency_score
      rationale: str            # 1–2 sentence plain-language explanation
  ```
- [ ] Add `trigger_point: Optional[TriggerPoint]` to `RiskScore`

---

## Task 3 — Update `head_agent.py` to output `trigger_point`

**File:** `backend/agents/head_agent.py`

After cascade chains are computed, select the one with the highest `urgency_score` and build a `TriggerPoint` from it.

- [ ] In `analyze()`, after cascade chains are computed, find `best_chain = max(chains, key=lambda c: c.urgency_score)`
- [ ] Build `TriggerPoint` from:
  - `anomaly_id` = `best_chain.trigger_anomaly_id`
  - `agent_domain` = look up the anomaly in `all_anomalies` by id to get its `agent_domain`
  - `title` = look up the anomaly's `title`
  - `cascade_chain_id` = `best_chain.id`
  - `urgency_score` = `best_chain.urgency_score`
  - `rationale` = inline: `f"This cascade has urgency {urgency_score:.2f} and leads to {best_chain.financial_impact} in {best_chain.time_to_impact_days} days."`
- [ ] Attach `trigger_point` to the `RiskScore` before returning it
- [ ] Handle the edge case where no cascade chains are found (`trigger_point = None`)

---

## Task 4 — Rewrite `orchestrator.py` with `DEADPOOLState`

**File:** `backend/orchestrator.py`

Replace the current `OrchestratorState` with `DEADPOOLState`.

- [ ] Rename `OrchestratorState` → `DEADPOOLState`, add `trigger_point: Optional[TriggerPoint]` field alongside `risk_score`:
  ```python
  class DEADPOOLState(TypedDict):
      specialist_reports: Annotated[list[AgentReport], operator.add]
      risk_score: Optional[RiskScore]
      trigger_point: Optional[TriggerPoint]
  ```
- [ ] Update `_make_head_node()` to unpack both `risk_score` and `trigger_point`:
  ```python
  def node(state: DEADPOOLState) -> dict:
      all_anomalies = [a for r in state["specialist_reports"] for a in r.anomalies]
      result: RiskScore = head_agent.analyze(all_anomalies)
      return {
          "risk_score": result,
          "trigger_point": result.trigger_point,
      }
  ```
- [ ] Update `run_pipeline()` initial state to include `trigger_point: None`

---

## Task 5 — Update `main.py` to use `run_pipeline()` and expose `trigger_point`

**File:** `backend/main.py`

- [ ] Import `run_pipeline` from `orchestrator` and call it in the `/api/head-agent/analyze` endpoint via `asyncio.to_thread`
- [ ] Return the full `RiskScore` object directly — `trigger_point` is already a field on it

---

## Task 6 — Smoke test the full pipeline

- [ ] Run `uvicorn main:app --reload` from `backend/`
- [ ] `POST /api/head-agent/analyze` — confirm JSON response has both `risk_score` and `trigger_point` populated
- [ ] Confirm Finance agent uses `gpt-4o-mini`, all others use `gemini-2.5-flash`, head agent uses `gemini-2.5-pro`
- [ ] Confirm `trigger_point.urgency_score` is the highest urgency across all cascade chains
