# DEADPOOL — Product Requirements Document

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

**Version:** 1.0  
**Date:** March 28, 2026  
**Author:** [Team Name]  
**Hackathon:** yconic New England Inter-Collegiate AI Hackathon  
**Track:** AI Innovation Hack ($10,000)

---

## 1. Executive summary

DEADPOOL is a multi-agent startup immune system that continuously monitors every operational layer of a company — legal, finance, infrastructure, product, people, and market — and maps how a single anomaly in one domain cascades into a company-ending failure across all others.

Unlike dashboards that show isolated metrics, DEADPOOL builds a live dependency graph across domains and traces risk forward through causal chains, giving founders the ability to see — and stop — cascading failures before the first domino tips.

**Core thesis:** Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

---

## 2. Problem statement

### The failure no one sees coming

Startup founders operate with fragmented visibility. Legal reviews contracts in isolation. Finance tracks burn rate without knowing an engineer just quit. Product monitors churn without knowing a key integration is about to break. Each domain operates in a silo, and the connections between domains — where cascading failures originate — are invisible.

### Current state

- Founders use 6-12 separate tools to monitor their company (GitHub, Stripe, Slack, Google Sheets, legal folders, analytics dashboards).
- No tool connects signals across domains.
- Post-mortems consistently reveal that the fatal chain reaction was visible in the data months before the company died — but no one connected the dots.
- Existing "startup health" tools show static scorecards, not causal chains.

### Why now

- Multi-agent AI orchestration makes it possible to run domain-specialized reasoning continuously.
- Real-time data APIs exist for every operational domain.
- The cost of running specialized AI agents has dropped to where continuous monitoring is economically viable for startups.

---

## 3. Product vision

**One sentence:** DEADPOOL is the air traffic control system for startup survival — it watches everything, connects everything, and tells you exactly which chain of events will kill your company before it happens.

**What If mode:** Founders can simulate scenarios ("What if this engineer leaves?" / "What if this client churns?") and watch the cascade recalculate in real-time.

---

## 4. Target users

### Primary: Early-stage startup founders (Seed to Series B)

- Running teams of 5-50 people
- Operating across multiple domains with limited oversight capacity
- Making high-stakes decisions with incomplete cross-domain information

### Secondary: Startup operators / Chiefs of Staff

- Responsible for cross-functional visibility
- Currently stitching together reports from multiple tools manually

### Hackathon demo persona

- A solo founder running a 12-person SaaS startup
- Uses GitHub, Slack, Stripe, Google Sheets, and standard SaaS contracts
- Has no dedicated ops person connecting signals across domains

---

## 5. System architecture

### 5.1 Agent layer

Six specialized agents, each with a defined domain, data sources, and anomaly detection logic.

| Agent | Domain | Data sources | Anomaly signals |
|-------|--------|-------------|-----------------|
| People agent | Team health & key-person risk | GitHub API (commit frequency, PR activity), Slack API (message frequency, response times) | Commit drop >50% week-over-week, prolonged silence from key contributors, workload concentration on single person |
| Finance agent | Burn rate, runway, revenue | CSV/Google Sheets upload, Stripe API (test mode) | Runway <6 months, revenue concentration >40% in single client, burn rate acceleration, payment delays |
| Infra agent | System reliability & deployment | GitHub Actions API, health endpoint monitoring, UptimeRobot/BetterStack API | Deploy frequency drop, CI failure rate spike, response time degradation, cloud cost anomaly |
| Product agent | User engagement & retention | Plausible/PostHog API, support ticket data | Feature adoption decline, churn rate increase, NPS drop, support ticket sentiment shift |
| Legal agent | Contracts, compliance, IP | Uploaded contract PDFs, Federal Register API, SEC EDGAR | Contract deadline approaching, conflicting terms across agreements, regulatory change in relevant sector |
| Market agent | Competitive landscape & trends | Claude API with web search tool, Crunchbase API, Google Trends (via SerpAPI) | Competitor funding round, market sentiment shift, regulatory announcement, pricing pressure |

### 5.2 Signal bus

- Central event queue where all agents publish detected anomalies.
- Each anomaly event includes: `agent_source`, `severity` (0-1), `timestamp`, `entity_affected`, `description`, and `linked_entities` (cross-domain references).
- Implemented as an in-memory event store (JSON array) with a polling interval of 5 minutes for the MVP.

### 5.3 Cascade mapper

The core intelligence layer. Receives anomaly events from the signal bus and traces them forward through a dependency graph.

**Dependency graph structure:**

```json
{
  "nodes": [
    {
      "id": "engineer_disengagement",
      "domain": "people",
      "description": "Key engineer commit activity drops significantly",
      "downstream": [
        {
          "target": "deploy_deadline_missed",
          "conditional_probability": 0.72,
          "reasoning": "Engineer owns payments microservice with hard deadline"
        }
      ]
    },
    {
      "id": "deploy_deadline_missed",
      "domain": "infra",
      "downstream": [
        {
          "target": "client_contract_lapse",
          "conditional_probability": 0.58,
          "reasoning": "Contract clause requires feature delivery by date"
        }
      ]
    }
  ]
}
```

**Cascade detection algorithm:**

1. Agent publishes anomaly to signal bus.
2. Cascade mapper identifies the anomaly type and looks up its node in the dependency graph.
3. For each downstream edge, the mapper queries the relevant agent for current state data to calculate a live conditional probability.
4. If the probability exceeds a threshold (default: 0.25), the mapper continues tracing forward.
5. Chain probabilities are multiplied along the path to produce an end-to-end cascade probability.
6. A company risk score is computed as a weighted sum of all active cascade chains.

**Dynamic probability adjustment:** Probabilities are not static. The cascade mapper re-queries agents at each step to adjust based on current data. If the engineer's commits recover, the entire downstream chain probability drops.

### 5.4 Dependency graph — initial seed

The MVP ships with a pre-built dependency graph encoding common startup failure cascades:

- Key-person departure → delivery delays → contract breach → revenue loss → runway crisis
- Client concentration risk → single client churn → revenue cliff → down-round trigger
- Technical debt accumulation → deploy velocity drop → feature delivery failure → competitive loss
- Regulatory change → compliance gap → legal exposure → investor confidence loss
- Competitor funding round → pricing pressure → margin compression → burn rate acceleration
- Infrastructure degradation → user experience decline → churn spike → revenue drop

Each path is encoded as nodes and edges with baseline probabilities derived from startup failure research. The cascade mapper adjusts these in real-time based on agent data.

---

## 6. Feature requirements

### 6.1 MVP (hackathon deliverable — 24 hours)

**P0 — Must ship**

- Three working agents: People (GitHub API), Infra (GitHub Actions + health check), Finance (CSV upload with analysis).
- Signal bus collecting anomalies from all active agents.
- Cascade mapper with at least 3 pre-built cascade chains that trace forward with live probability scores.
- Dashboard displaying: active anomalies by agent, cascade chain visualization (animated node-to-node), and a single company risk score.
- One live cascade detected from real data (the team's own hackathon repo).

**P1 — Ship if time allows (Day 2 morning)**

- Legal agent parsing uploaded contract PDFs for deadline extraction.
- Market agent using Claude API with web search for live competitor monitoring.
- "What If" simulation mode with sliders for scenario exploration.
- Timeline view showing risk score changes over the hackathon period.

**P2 — Demo polish (Day 2 afternoon)**

- Animated cascade chain visualization with probability scores appearing as the chain propagates.
- Alert notifications when a new cascade chain is detected.
- Export cascade report as shareable summary.

### 6.2 Post-hackathon (product roadmap)

- Custom dependency graph builder (founders define their own causal relationships).
- Direct integrations: Slack, Linear, Jira, Stripe, QuickBooks, Notion.
- Historical cascade analysis (retroactively map what killed past startups using public data).
- Multi-company benchmarking (anonymized cascade patterns across the user base).
- Investor view (portfolio-level cascade monitoring across multiple startups).

---

## 7. Technical specifications

### 7.1 Tech stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + D3.js | D3 for dependency graph visualization, React for dashboard state management |
| Backend | Node.js + Express | Lightweight, fast to scaffold, handles API polling and event bus |
| AI orchestration | Anthropic Claude API (claude-sonnet-4-20250514) | Each agent is a specialized system prompt with function calling for data retrieval |
| Data ingestion | GitHub REST API, CSV parsing (Papaparse), file upload | Covers the three MVP agents with minimal integration work |
| Real-time updates | Server-Sent Events (SSE) or WebSocket | Push cascade updates to the dashboard without polling |
| Deployment | Vercel (frontend) + Railway or Render (backend) | Free tiers, deploy in minutes |

### 7.2 Agent implementation pattern

Each agent follows an identical pattern — only the system prompt and data sources change:

```
Agent(domain, system_prompt, data_sources[]) → Anomaly[]

Every 5 minutes:
  1. Poll data sources for latest state
  2. Send state + system prompt to Claude API
  3. Claude returns structured JSON: anomalies detected, severity, entities affected
  4. Publish anomalies to signal bus
```

**System prompt template (per agent):**

```
You are the {domain} monitoring agent for a startup.
Analyze the following data and identify anomalies that could
indicate risk. For each anomaly, return JSON with:
- anomaly_type: string
- severity: float (0-1)
- entity_affected: string
- description: string
- linked_entities: string[] (cross-domain references)

Respond ONLY with valid JSON array. No preamble.
```

### 7.3 Cascade mapper logic

```
function traceCascade(anomaly, graph, agents):
  chain = [anomaly]
  current = anomaly
  
  while current.downstream exists:
    for each edge in current.downstream:
      // Query the target agent for live state
      liveState = agents[edge.target_domain].getCurrentState()
      
      // Adjust probability based on live data
      adjustedProbability = calculateProbability(edge, liveState)
      
      if adjustedProbability > THRESHOLD:
        nextNode = {
          ...edge.target,
          probability: chain.last.probability * adjustedProbability
        }
        chain.push(nextNode)
        current = nextNode
      else:
        break  // cascade chain broken
  
  return chain
```

### 7.4 API rate limits and constraints

| API | Rate limit | Polling interval | Notes |
|-----|-----------|-----------------|-------|
| GitHub REST API | 5,000 req/hr (authenticated) | Every 5 min | Use personal access token, cache responses |
| Slack API | Tier 3 (50+ req/min) | Every 10 min | Only needed for People agent extension |
| Claude API | Standard rate limits | On-demand per agent cycle | ~6 calls per cycle (one per agent) |
| UptimeRobot | 10 req/min | Every 5 min | Free tier sufficient for MVP |

---

## 8. Data model

### 8.1 Anomaly event

```json
{
  "id": "uuid",
  "agent_source": "people | finance | infra | product | legal | market",
  "anomaly_type": "string",
  "severity": 0.0-1.0,
  "entity_affected": "string",
  "description": "string",
  "linked_entities": ["string"],
  "timestamp": "ISO 8601",
  "raw_data": {}
}
```

### 8.2 Cascade chain

```json
{
  "id": "uuid",
  "trigger_anomaly_id": "uuid",
  "chain": [
    {
      "node_id": "string",
      "domain": "string",
      "description": "string",
      "probability": 0.0-1.0,
      "agent_evidence": "string"
    }
  ],
  "end_state": "string",
  "overall_probability": 0.0-1.0,
  "company_risk_contribution": 0.0-1.0,
  "detected_at": "ISO 8601",
  "last_updated": "ISO 8601"
}
```

### 8.3 Company risk score

```json
{
  "score": 0.0-100.0,
  "active_cascades": 3,
  "highest_risk_cascade": "cascade_id",
  "contributing_factors": [
    {
      "cascade_id": "string",
      "contribution_weight": 0.0-1.0,
      "summary": "string"
    }
  ],
  "trend": "increasing | stable | decreasing",
  "updated_at": "ISO 8601"
}
```

---

## 9. UI/UX specifications

### 9.1 Dashboard layout

**Primary view — cascade map:**

- Full-width directed graph showing all active cascade chains.
- Nodes color-coded by domain (blue = people, green = finance, orange = infra, purple = product, red = legal, teal = market).
- Edge thickness represents probability. Edges below threshold are dashed/gray.
- Animated pulse along active cascade chains (node lights up, pulse travels along edge to next node).
- Click any node to expand details and see the agent's raw evidence.

**Top bar — risk score:**

- Single large number (0-100) with color indicator (green/yellow/orange/red).
- Trend arrow (up/down/stable) with sparkline showing last 24 hours.
- Count of active cascades.

**Side panel — agent status:**

- Six agent cards showing: last poll time, anomalies detected, current status (healthy/warning/critical).
- Click to expand and see the agent's latest findings.

### 9.2 "What If" mode

- Toggle button switches dashboard to simulation mode.
- Sliders appear for key variables: "Key engineer leaves" (0-100%), "Biggest client churns" (0-100%), "Cloud costs double" (0-100%).
- Graph recalculates in real-time as sliders move.
- Side-by-side comparison: current state vs simulated state.

### 9.3 Cascade alert

When a new cascade chain is detected or an existing chain's probability crosses a threshold:

- Toast notification with chain summary.
- Cascade chain highlighted/animated on the graph.
- Alert log with timestamp and full chain details.

---

## 10. Judging alignment

Mapping CascadeAI to the AI Innovation Hack judging rubric:

| Criterion | How CascadeAI scores |
|-----------|---------------------|
| **Innovative use of AI** | Multi-agent orchestration where agents don't just report — they reason about cross-domain causality. The cascade mapper is a novel architecture. |
| **Traction (user signups)** | Deploy a landing page, drive signups from hackathon attendees. Target: 20+ signups during the event. Pitch it as "sign up to get your startup's DEADPOOL score." |
| **Social media traction** | Live-tweet cascade detections. Post the most dramatic cascade chain found during the hackathon. Visual cascade animations are inherently shareable. |
| **Product-market fit evidence** | Every founder in the room has experienced the problem of siloed monitoring. The "What If" mode is the feature that makes people say "I need this." |
| **Creative AI use** | Six agents with emergent cross-domain reasoning. The cascade mapper produces insights none of the individual agents could generate alone. |

---

## 11. Request for Hacks alignment

CascadeAI maps to multiple RFH theses:

- **RFH #05 — The Product That Builds Itself:** DEADPOOL improves its dependency graph over time as it observes more data, making the product self-evolving.
- **RFH #04 — Intent as Code:** The dependency graph is essentially a company's operational intent encoded as a config — "these are the causal relationships that matter to us."
- **RFH #07 — The One-Person Billion-Dollar Company:** DEADPOOL gives a solo founder the operational awareness of a 50-person leadership team.

---

## 12. Hackathon sprint plan

### Day 1 — Build the engine (12:00 PM – midnight)

| Time | Task | Owner |
|------|------|-------|
| 12:00 – 1:00 PM | Set up repo, project scaffold (React + Express), deploy pipeline | Full team |
| 1:00 – 3:00 PM | People agent (GitHub API integration + anomaly detection prompt) | Dev 1 |
| 1:00 – 3:00 PM | Finance agent (CSV parser + burn rate analysis prompt) | Dev 2 |
| 1:00 – 3:00 PM | Dashboard scaffold (React + D3 graph component) | Dev 3 |
| 3:00 – 5:00 PM | Signal bus + cascade mapper core logic | Dev 1 + Dev 2 |
| 3:00 – 5:00 PM | Infra agent (GitHub Actions API + health check) | Dev 3 |
| 5:00 – 7:00 PM | Integration: agents → signal bus → cascade mapper → dashboard | Full team |
| 7:00 – 8:00 PM | Dinner break |  |
| 8:00 – midnight | End-to-end testing, first live cascade detection, bug fixes | Full team |

### Day 2 — Polish and traction (9:00 AM – 2:30 PM)

| Time | Task | Owner |
|------|------|-------|
| 9:00 – 10:30 AM | "What If" simulation mode | Dev 1 |
| 9:00 – 10:30 AM | Legal + Market agents (stretch) | Dev 2 |
| 9:00 – 10:30 AM | Landing page for signups + social sharing | Dev 3 |
| 10:30 – 12:00 PM | Cascade animation polish, alert system | Dev 1 + Dev 3 |
| 10:30 – 12:00 PM | Drive signups: share landing page, post on social | Dev 2 |
| 12:00 – 1:30 PM | Demo rehearsal, edge case fixes | Full team |
| 1:30 – 2:30 PM | Final polish, prepare demo script | Full team |

---

## 13. Demo script (3 minutes)

1. **Hook (30 sec):** "Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities. It sees the kill chain before it kills you."
2. **Live data (60 sec):** Show DEADPOOL running on the team's own hackathon data. Show a real cascade it detected — walk through the chain node by node.
3. **What If (45 sec):** Toggle simulation mode. Drag the "key engineer leaves" slider. Watch the cascade recalculate live. Show how one person's departure cascades into a company-ending event.
4. **Traction (30 sec):** Show the landing page, signup count, social media engagement.
5. **Close (15 sec):** "Every startup has a DEADPOOL score right now. Most founders don't know theirs. We change that."

---

## 14. Success metrics

### Hackathon success

- At least one real cascade detected from live data during the event.
- 20+ landing page signups.
- Working "What If" mode demonstrated on stage.
- Dashboard showing real-time risk score with animated cascade visualization.

### Post-hackathon success (30-day)

- 100+ waitlist signups.
- 5 founder interviews validating the cascade mapping concept.
- One pilot deployment with a real startup.

---

## 15. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| GitHub API rate limiting during demo | Cascade mapper can't refresh | Pre-cache data, implement fallback to last-known state |
| Claude API latency spikes | Agents respond slowly, dashboard feels laggy | Cache agent responses, show "last updated" timestamps, run agents asynchronously |
| No interesting cascade found in real data | Demo falls flat | Seed the dependency graph with a guaranteed cascade path using the team's own data; have a backup synthetic scenario ready |
| D3 graph visualization breaks on complex chains | Dashboard looks broken on stage | Cap visible chain length at 6 nodes, test with maximum cascade depth before demo |
| Team burnout overnight | Code quality drops, bugs multiply | Enforce the study break at 4 PM, sleep in shifts, stop coding at midnight and resume fresh at 9 AM |

---

*Built for the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*  
*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities*  
*Track: AI Innovation Hack · Request for Hacks: #04, #05, #07*
