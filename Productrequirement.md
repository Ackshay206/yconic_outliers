# DEADPOOL — Product Requirements Document

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

**Version:** 2.0  
**Date:** March 28, 2026  
**Author:** [Team Name]  
**Hackathon:** yconic New England Inter-Collegiate AI Hackathon  
**Track:** AI Innovation Hack ($10,000)

---

## 1. Executive summary

DEADPOOL is a multi-agent startup immune system that continuously monitors every operational layer of a company — legal, finance, infrastructure, product, people, and codebase — and maps how a single anomaly in one domain cascades into downstream failures across all others.

A Head Agent orchestrates the entire swarm, arbitrating cross-domain conflicts, prioritizing which cascades matter most, and delivering a unified risk picture to the founder. Unlike dashboards that show isolated metrics, DEADPOOL builds a live dependency graph across domains and traces risk forward through causal chains, giving founders the ability to see — and stop — cascading failures before the first domino tips.

**Core thesis:** Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

---

## 2. Problem statement

### The failure no one sees coming

Startup founders operate with fragmented visibility. Legal reviews contracts in isolation. Finance tracks burn rate without knowing an engineer just quit. Product monitors churn without knowing a key integration is about to break. Nobody is reading the codebase for structural rot that will blow up next quarter. Each domain operates in a silo, and the connections between domains — where cascading failures originate — are invisible.

### Current state

- Founders use 6-12 separate tools to monitor their company (GitHub, Stripe, Slack, Google Sheets, legal folders, analytics dashboards).
- No tool connects signals across domains.
- Code quality tools (SonarQube, CodeClimate) exist but never talk to business context — a critical vulnerability means nothing to them if it's in the service that your biggest client depends on.
- Post-mortems consistently reveal that the fatal chain reaction was visible in the data months before the company died — but no one connected the dots.
- No single "brain" synthesizes all signals into a unified risk picture with clear action priorities.

### Why now

- Multi-agent AI orchestration makes it possible to run domain-specialized reasoning continuously.
- Real-time data APIs exist for every operational domain.
- LLMs can now analyze code structure, detect architectural anti-patterns, and reason about technical debt in business context.
- The cost of running specialized AI agents has dropped to where continuous monitoring is economically viable for startups.

---

## 3. Product vision

**One sentence:** DEADPOOL is the air traffic control system for startup survival — a Head Agent commanding six specialist agents that watch everything, connect everything, and tell you exactly which chain of events will kill your company before it happens.

**What If mode:** Founders can simulate scenarios ("What if this engineer leaves?" / "What if this client churns?" / "What if we skip the security patch?") and watch the cascade recalculate in real-time.

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

### 5.0 Architecture overview — the 7-agent hierarchy

DEADPOOL runs a hierarchical multi-agent system: six specialist agents report to one Head Agent. The specialists are domain experts. The Head Agent is the strategist.

```
                    ┌──────────────┐
                    │  HEAD AGENT  │
                    │  (Overseer)  │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────┴──────┐ ┌────┴────┐ ┌───────┴──────┐
     │ People Agent│ │ Finance │ │  Infra Agent  │
     │             │ │  Agent  │ │              │
     └─────────────┘ └─────────┘ └──────────────┘
            │              │              │
     ┌──────┴──────┐ ┌────┴────┐ ┌───────┴──────┐
     │Product Agent│ │  Legal  │ │  Code Audit  │
     │             │ │  Agent  │ │    Agent     │
     └─────────────┘ └─────────┘ └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  Signal Bus  │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   Cascade    │
                    │    Mapper    │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   Founder    │
                    │  Dashboard   │
                    └──────────────┘
```

### 5.1 Head Agent — the overseer

The Head Agent is the brain of DEADPOOL. It does not monitor data directly — it orchestrates, arbitrates, and synthesizes.

**Responsibilities:**

- Receives all anomaly events from the signal bus before they reach the cascade mapper.
- Cross-validates anomalies: when the People Agent flags an engineer's declining commits, the Head Agent asks the Code Audit Agent "is this person's code area also degrading?" and the Infra Agent "are their services showing symptoms?" — corroborating or downgrading the signal.
- Resolves conflicting signals: if the Finance Agent says runway is fine but the Legal Agent says a contract breach is imminent, the Head Agent weighs both signals and determines which cascade path is dominant.
- Prioritizes cascades: when multiple cascade chains are active, the Head Agent ranks them by time-to-impact, reversibility, and financial severity — then surfaces the top 3 to the founder.
- Generates the unified company risk score by weighting all active cascades.
- Produces the founder-facing narrative: a plain-language briefing that explains what's happening, why it matters, and what to do first.
- Triggers the "What If" simulation engine when the founder adjusts scenario sliders.

**Implementation:**

```
Head Agent receives: anomaly_events[], agent_states{}, cascade_chains[]

Every cycle:
  1. Collect all new anomalies from signal bus
  2. For each anomaly, query 1-2 other agents for corroboration
  3. Assign a validated_severity (may differ from the reporting agent's severity)
  4. Feed validated anomalies into cascade mapper
  5. Rank resulting cascade chains by urgency
  6. Generate founder briefing with top 3 cascades + recommended actions
  7. Update company risk score
```

**System prompt:**

```
You are the Head Agent of DEADPOOL, a startup risk intelligence system.
You oversee six specialist agents: People, Finance, Infra, Product, Legal, and Code Audit.

Your job:
1. Receive anomaly reports from all agents.
2. Cross-validate each anomaly by requesting corroboration from related agents.
3. Resolve conflicts when agents disagree.
4. Rank cascade chains by urgency (time-to-impact × severity × reversibility).
5. Produce a founder briefing: top 3 risks, plain language, specific actions.

You think like a seasoned COO who has seen startups die. You are direct, specific, and never vague.
When agents disagree, you explain your reasoning for which signal you trust more.

Return JSON with:
- validated_anomalies: array of anomalies with adjusted severity and corroboration notes
- cascade_rankings: ordered array of cascade chain IDs with urgency scores
- founder_briefing: string, 3-5 sentences, plain language
- risk_score: float 0-100
- top_action: string, the single most important thing the founder should do right now
```

### 5.2 Specialist agents

Six specialist agents, each with a clearly defined domain, data responsibilities, and anomaly detection scope. Each agent reports to the Head Agent via the signal bus.

| Agent | Domain | What it owns | What it does NOT own |
|-------|--------|-------------|---------------------|
| **People Agent** | Team health, engagement, key-person risk | Developer activity patterns, team sentiment, workload distribution, hiring pipeline | Code quality (→ Code Audit), deployment metrics (→ Infra) |
| **Finance Agent** | Cash flow, runway, revenue, funding terms | Burn rate, revenue by client, runway projections, investor clause tracking, accounts receivable | Contract legal language (→ Legal), pricing competitive analysis (→ Code Audit via market positioning) |
| **Infra Agent** | System reliability, deployment, operations | Uptime, response times, deploy frequency, CI/CD health, cloud costs, incident tracking | Code architecture issues (→ Code Audit), feature usage (→ Product) |
| **Product Agent** | User engagement, retention, satisfaction | WAU/DAU, feature adoption, churn rate, NPS, support tickets, user sentiment | System performance causing UX issues (→ Infra), code bugs causing errors (→ Code Audit) |
| **Legal Agent** | Contracts, compliance, IP, regulatory | Contract deadlines, clause analysis, compliance obligations, regulatory changes, IP exposure | Financial modeling of contract loss (→ Finance), technical compliance (→ Code Audit for PCI/SOC2) |
| **Code Audit Agent** | Codebase health, security, architecture | Technical debt scoring, dependency vulnerabilities, architecture anti-patterns, test coverage, security scan, code ownership concentration | Runtime performance (→ Infra), developer behavior patterns (→ People) |

**Agent data sources and anomaly signals (detailed):**

**People Agent**
- Data: GitHub API (commit frequency, PR activity per developer), Slack API (message frequency, response times)
- Detects: commit drop >50% week-over-week, prolonged silence from key contributors, workload concentration on single person, PR review bottlenecks, hiring pipeline stalls
- Links to: Code Audit (which code areas are affected), Infra (which services are owned by the person), Finance (payroll cost of the person)

**Finance Agent**
- Data: CSV/Google Sheets upload, Stripe API (test mode), uploaded cap table
- Detects: runway <6 months, revenue concentration >40% in single client, burn rate acceleration, payment delays, approaching investor clause thresholds
- Links to: Legal (contract values and renewal dates), People (headcount cost impact), Product (revenue-driving feature health)

**Infra Agent**
- Data: GitHub Actions API, health endpoint monitoring, UptimeRobot/BetterStack API, cloud cost tracking
- Detects: deploy frequency drop, CI failure rate spike, response time degradation, uptime breach approaching SLA thresholds, cloud cost anomaly
- Links to: Code Audit (are code issues causing the failures?), People (who owns the degrading service?), Legal (SLA obligations at risk)

**Product Agent**
- Data: Plausible/PostHog API, support ticket data, NPS survey results
- Detects: feature adoption decline, churn rate increase, NPS drop below threshold, support ticket volume spike, sentiment shift in tickets
- Links to: Infra (is system performance causing the UX decline?), Code Audit (are bugs causing the errors users see?), Finance (revenue impact of churn)

**Legal Agent**
- Data: Uploaded contract PDFs, Federal Register API, SEC EDGAR
- Detects: contract deadline approaching with delivery at risk, conflicting terms across agreements, regulatory change requiring compliance action, IP exposure from open-source usage
- Links to: Finance (financial impact of breach), Infra (delivery deadlines tied to services), Code Audit (compliance requirements like PCI DSS, SOC 2)

**Code Audit Agent**
- Data: GitHub API (repository analysis), static analysis results (uploaded or generated), `package.json` / `requirements.txt` dependency parsing
- Detects: critical dependency vulnerabilities (CVE severity ≥ 7.0), test coverage dropping below thresholds, code ownership concentration (bus factor = 1), architecture anti-patterns (circular dependencies, god classes, missing error handling in critical paths), security misconfigurations, outdated dependencies with known exploits, technical debt accumulation rate
- Links to: People (who wrote/owns the problematic code?), Infra (which services are affected?), Legal (compliance implications of vulnerabilities), Product (which user-facing features sit on top of the bad code?)

### 5.3 Signal bus

- Central event queue where all six specialist agents publish detected anomalies.
- The Head Agent subscribes to the signal bus and receives all events in real-time.
- Each anomaly event includes: `agent_source`, `severity` (0-1), `timestamp`, `entity_affected`, `description`, `linked_entities` (cross-domain references), and `corroboration_requested` (which other agents should validate this).
- Implemented as an in-memory event store (JSON array) with a polling interval of 5 minutes for the MVP.
- The Head Agent may inject `head_agent_override` events that adjust or retract anomalies after cross-validation.

### 5.4 Cascade mapper

The core intelligence layer. Receives **validated** anomaly events from the Head Agent (not raw events from the signal bus) and traces them forward through a dependency graph.

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
          "target": "code_quality_degradation",
          "conditional_probability": 0.78,
          "reasoning": "Engineer owns critical code paths with no backup reviewer"
        },
        {
          "target": "deploy_deadline_missed",
          "conditional_probability": 0.72,
          "reasoning": "Engineer owns payments microservice with hard deadline"
        }
      ]
    },
    {
      "id": "code_quality_degradation",
      "domain": "code_audit",
      "description": "Critical service accumulates unreviewed code, rising vulnerability count",
      "downstream": [
        {
          "target": "infra_degradation",
          "conditional_probability": 0.65,
          "reasoning": "Unreviewed code ships bugs to production"
        },
        {
          "target": "compliance_breach",
          "conditional_probability": 0.45,
          "reasoning": "Unpatched CVEs violate PCI DSS requirements"
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

1. Head Agent validates anomaly and pushes to cascade mapper.
2. Cascade mapper identifies the anomaly type and looks up its node in the dependency graph.
3. For each downstream edge, the Head Agent queries the relevant specialist agent for current state data to calculate a live conditional probability.
4. If the probability exceeds a threshold (default: 0.25), the mapper continues tracing forward.
5. Chain probabilities are multiplied along the path to produce an end-to-end cascade probability.
6. The Head Agent computes a company risk score as a weighted sum of all active cascade chains, ranked by urgency.

**Dynamic probability adjustment:** Probabilities are not static. The Head Agent coordinates re-queries to specialist agents at each step to adjust based on current data. If the engineer's commits recover, the Head Agent downgrades the entire downstream chain.

### 5.5 Dependency graph — initial seed

The MVP ships with a pre-built dependency graph encoding common startup failure cascades. The Code Audit Agent adds new cascade paths that no traditional hackathon project would catch:

- Key-person departure → code ownership gap → code quality degradation → delivery delays → contract breach → revenue loss → runway crisis
- Critical CVE in dependency → compliance breach → legal exposure → investor confidence loss → funding risk
- Test coverage decline → undetected bugs → user-facing errors → churn spike → revenue drop
- Technical debt accumulation → deploy velocity drop → feature delivery failure → competitive loss
- Client concentration risk → single client churn → revenue cliff → down-round trigger
- Architecture anti-pattern → cascading service failures → SLA breach → contract penalty → burn rate spike

Each path is encoded as nodes and edges with baseline probabilities. The Head Agent adjusts these in real-time based on corroborated agent data.

---

## 6. Feature requirements

### 6.1 MVP (hackathon deliverable — 24 hours)

**P0 — Must ship (all 7 agents)**

- Six working specialist agents: People (GitHub API), Finance (CSV upload), Infra (GitHub Actions + health check), Product (analytics data), Legal (contract parsing), Code Audit (repo analysis + dependency scanning).
- Head Agent orchestrating all six: cross-validation, conflict resolution, cascade ranking, founder briefing generation.
- Signal bus collecting anomalies from all agents with Head Agent subscription.
- Cascade mapper with at least 4 pre-built cascade chains including at least one that passes through the Code Audit Agent.
- Dashboard displaying: active anomalies by agent, Head Agent status panel, cascade chain visualization (animated node-to-node), company risk score, and founder briefing.
- At least one detected cascade that spans 3+ agent domains.

**P1 — Ship if time allows (Day 2 morning)**

- "What If" simulation mode with sliders for scenario exploration, powered by the Head Agent recalculating cascades.
- Head Agent conflict resolution log (show when agents disagreed and how the Head Agent resolved it).
- Timeline view showing risk score changes over the monitoring period.
- Code Audit Agent deep scan: architecture diagram generation from repo analysis.

**P2 — Demo polish (Day 2 afternoon)**

- Animated cascade chain visualization with probability scores appearing as the chain propagates.
- Head Agent "thinking" animation showing cross-validation in progress.
- Alert notifications when a new cascade chain is detected.
- Export cascade report as shareable summary.

### 6.2 Post-hackathon (product roadmap)

- Custom dependency graph builder (founders define their own causal relationships).
- Direct integrations: Slack, Linear, Jira, Stripe, QuickBooks, Notion, SonarQube, Snyk.
- Historical cascade analysis (retroactively map what killed past startups using public data).
- Multi-company benchmarking (anonymized cascade patterns across the user base).
- Investor view (portfolio-level cascade monitoring across multiple startups).
- Head Agent learning: the Head Agent improves its cross-validation heuristics based on which cascades actually materialized.

---

## 7. Technical specifications

### 7.1 Tech stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + D3.js | D3 for dependency graph visualization, React for dashboard state management |
| Backend | Python + FastAPI | Async-native, Pydantic v2 for type-safe agent I/O, automatic OpenAPI docs. Handles API polling, signal bus, and Head Agent orchestration. |
| AI orchestration | Anthropic Claude API (claude-sonnet-4-6) | Each specialist agent is a specialized system prompt. Head Agent uses a more comprehensive prompt with cross-validation routing to query specialists. |
| Data ingestion | JSON synthetic data files (hackathon MVP), GitHub REST API, CSV upload for financials, pip-audit for dependency scanning | Covers all six agents with minimal integration work |
| Real-time updates | Server-Sent Events (SSE) via sse-starlette | Push cascade updates and Head Agent briefings to the dashboard without polling |
| Deployment | Vercel (frontend) + Railway or Render (backend) | Free tiers, deploy in minutes |

### 7.2 Agent implementation pattern

Every specialist agent follows the same pattern — only the system prompt and data sources change:

```
SpecialistAgent(domain, system_prompt, data_sources[]) → Anomaly[]

Every 5 minutes:
  1. Poll data sources for latest state
  2. Send state + system prompt to Claude API
  3. Claude returns structured JSON: anomalies detected, severity, entities affected
  4. Publish anomalies to signal bus
  5. Head Agent receives and cross-validates
```

The Head Agent follows a different pattern — it orchestrates rather than monitors:

```
HeadAgent(specialist_agents[], signal_bus, cascade_mapper) → ValidatedAnomalies[], CascadeRankings[], FounderBriefing

Every cycle (triggered by new anomalies on signal bus):
  1. Collect all new anomalies from signal bus
  2. For each anomaly:
     a. Identify which specialist agents should corroborate
     b. Query those agents for supporting/contradicting evidence
     c. Assign validated_severity (may differ from original)
     d. Tag with corroboration_status: confirmed | partial | unconfirmed | contradicted
  3. Feed validated anomalies into cascade mapper
  4. Rank resulting cascades by: time_to_impact × severity × (1 - reversibility)
  5. Generate founder briefing: top 3 cascades, plain language, specific next action
  6. Push briefing + risk score to dashboard
```

**Head Agent system prompt:**

```
You are the Head Agent of DEADPOOL, a startup risk intelligence system.
You command six specialist agents: People, Finance, Infra, Product, Legal, and Code Audit.

You receive anomaly reports from all agents. Your responsibilities:

1. CROSS-VALIDATE: For each anomaly, request evidence from 1-2 related agents.
   - People flags engineer decline → ask Code Audit about that engineer's code areas
   - Code Audit flags vulnerability → ask Legal about compliance implications
   - Finance flags revenue risk → ask Legal about the relevant contract terms
   - Infra flags degradation → ask Code Audit if code issues are the root cause
   - Product flags churn → ask Infra if system issues are driving it
   - Legal flags deadline → ask Infra about delivery progress

2. RESOLVE CONFLICTS: When agents disagree, explain your reasoning.
   Example: Finance says runway is fine (9 months). Legal says contract breach is imminent.
   You weigh: breach causes $400K revenue loss → recalculate runway → now 4 months. Legal wins.

3. RANK CASCADES: Score each cascade chain as:
   urgency = time_to_impact_days⁻¹ × severity × (1 - reversibility)
   Surface the top 3 to the founder.

4. BRIEF THE FOUNDER: 3-5 sentences. No jargon. Name the risk, the timeline, and the one action to take now.

Return JSON:
- validated_anomalies: [{anomaly_id, original_severity, validated_severity, corroboration_status, corroboration_notes}]
- cascade_rankings: [{cascade_id, urgency_score, time_to_impact_days, top_action}]
- founder_briefing: string
- risk_score: float 0-100
- top_action: string
```

**Specialist agent system prompt template:**

```
You are the {domain} monitoring agent for a startup, reporting to the Head Agent of DEADPOOL.
Analyze the following data and identify anomalies that could indicate risk.

For each anomaly, return JSON with:
- anomaly_type: string
- severity: float (0-1)
- confidence: float (0-1)
- entity_affected: string
- description: string
- evidence: {metric, current_value, baseline_value, deviation_percent}
- linked_entities: [{entity, entity_type, relationship}]
- corroboration_requested: string[] (which other agents should validate this)

Respond ONLY with valid JSON array. No preamble.
```

### 7.3 Code Audit Agent — detailed implementation

The Code Audit Agent is unique because it analyzes the codebase itself, not operational metrics. It bridges the gap between technical debt and business risk.

**Data sources:**

```
1. GitHub API — repository-level analysis:
   - File change frequency (hotspot detection)
   - Code ownership per file/directory (git blame analysis)
   - PR merge patterns (are PRs merged without review?)
   - Branch staleness (unmerged branches with critical changes)

2. Dependency scanning:
   - Parse package.json / requirements.txt / go.mod
   - Cross-reference with CVE databases (NVD API or npm audit output)
   - Flag dependencies with known critical vulnerabilities

3. Static analysis signals (uploaded or generated):
   - Test coverage percentage per service
   - Cyclomatic complexity of critical paths
   - Code duplication ratio
   - Error handling coverage in critical services

4. Architecture analysis:
   - Service dependency mapping (from import statements + API calls)
   - Circular dependency detection
   - Single-point-of-failure identification (one file imported everywhere)
```

**Anomaly detection rules:**

| Signal | Threshold | Severity | Cascade potential |
|--------|-----------|----------|-------------------|
| CVE with CVSS ≥ 7.0 in production dependency | Any occurrence | 0.8-1.0 | → Legal (compliance), Infra (exploit risk) |
| Test coverage drops below 60% for critical service | Per-service check | 0.6-0.8 | → Infra (undetected bugs), Product (user-facing errors) |
| Bus factor = 1 for critical service | Only one contributor in 90 days | 0.7-0.9 | → People (key-person risk), Infra (no backup) |
| PRs merged without review in critical service | Any in last 2 weeks | 0.5-0.7 | → Infra (quality risk), Product (potential bugs) |
| Dependency >2 major versions behind | Per-dependency | 0.4-0.6 | → Legal (compliance), Infra (compatibility risk) |
| Circular dependency detected | Any occurrence | 0.5-0.7 | → Infra (cascading failures), Product (feature coupling) |
| Error handling missing in payment/auth paths | Any occurrence | 0.7-0.9 | → Legal (PCI compliance), Finance (transaction risk) |

### 7.4 Cascade mapper logic

```
function traceCascade(anomaly, graph, headAgent):
  chain = [anomaly]
  current = anomaly
  
  while current.downstream exists:
    for each edge in current.downstream:
      // Head Agent queries the target specialist agent for live state
      liveState = headAgent.querySpecialist(edge.target_domain)
      
      // Head Agent adjusts probability based on corroborated evidence
      adjustedProbability = headAgent.calculateProbability(edge, liveState)
      
      if adjustedProbability > THRESHOLD:
        nextNode = {
          ...edge.target,
          probability: chain.last.probability * adjustedProbability,
          corroborated_by: headAgent.getCorroborationLog()
        }
        chain.push(nextNode)
        current = nextNode
      else:
        break  // cascade chain broken — Head Agent logs why
  
  return chain
```

### 7.5 API rate limits and constraints

| API | Rate limit | Polling interval | Notes |
|-----|-----------|-----------------|-------|
| GitHub REST API | 5,000 req/hr (authenticated) | Every 5 min | Use personal access token, cache responses. Code Audit Agent may use more calls for repo analysis. |
| Claude API | Standard rate limits | On-demand per agent cycle | ~7 calls per cycle (6 specialists + 1 Head Agent). Head Agent may make 2-3 additional calls for cross-validation. |
| NVD API (CVE data) | 5 req/30 sec (no key), 50 req/30 sec (with key) | Every 30 min | Cache CVE lookups aggressively — vulnerabilities don't change every 5 minutes. |
| UptimeRobot | 10 req/min | Every 5 min | Free tier sufficient for MVP |

---

## 8. Data model

### 8.1 Anomaly event

```json
{
  "id": "uuid",
  "agent_source": "people | finance | infra | product | legal | code_audit",
  "anomaly_type": "string",
  "severity": 0.0-1.0,
  "confidence": 0.0-1.0,
  "entity_affected": "string",
  "entity_type": "developer | service | client | contract | dependency | file",
  "description": "string",
  "evidence": {
    "metric": "string",
    "current_value": "any",
    "baseline_value": "any",
    "deviation_percent": "float"
  },
  "linked_entities": [
    {"entity": "string", "entity_type": "string", "relationship": "string"}
  ],
  "corroboration_requested": ["string — agent domains to cross-check"],
  "timestamp": "ISO 8601",
  "raw_data": {}
}
```

### 8.2 Head Agent validated anomaly

```json
{
  "anomaly_id": "uuid — reference to original anomaly",
  "original_severity": 0.0-1.0,
  "validated_severity": 0.0-1.0,
  "corroboration_status": "confirmed | partial | unconfirmed | contradicted",
  "corroboration_notes": "string — Head Agent's reasoning",
  "corroborating_agents": ["string — which agents provided evidence"],
  "override_reason": "string | null — why severity was changed",
  "validated_at": "ISO 8601"
}
```

### 8.3 Cascade chain

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
      "agent_evidence": "string",
      "head_agent_corroboration": "string"
    }
  ],
  "end_state": "string",
  "overall_probability": 0.0-1.0,
  "urgency_score": 0.0-1.0,
  "company_risk_contribution": 0.0-1.0,
  "detected_at": "ISO 8601",
  "last_updated": "ISO 8601"
}
```

### 8.4 Company risk score

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
  "founder_briefing": "string — Head Agent's plain-language summary",
  "top_action": "string — single most important thing to do now",
  "updated_at": "ISO 8601"
}
```

---

## 9. UI/UX specifications

### 9.1 Dashboard layout

**Primary view — cascade map:**

- Full-width directed graph showing all active cascade chains.
- Nodes color-coded by domain (blue = people, green = finance, orange = infra, purple = product, red = legal, cyan = code audit).
- Edge thickness represents probability. Edges below threshold are dashed/gray.
- Animated pulse along active cascade chains (node lights up, pulse travels along edge to next node).
- Click any node to expand details and see the specialist agent's raw evidence + Head Agent's corroboration notes.

**Top bar — risk score + Head Agent briefing:**

- Single large number (0-100) with color indicator (green/yellow/orange/red).
- Trend arrow (up/down/stable) with sparkline showing last 24 hours.
- Count of active cascades.
- Head Agent briefing banner: 2-3 sentence plain-language summary of the current risk state.
- "Top action" call-to-action button showing the Head Agent's recommended next step.

**Side panel — agent status:**

- Seven agent cards (Head Agent at top, six specialists below).
- Head Agent card shows: last cross-validation time, conflicts resolved, current corroboration in progress.
- Specialist cards show: last poll time, anomalies detected, current status (healthy/warning/critical), corroboration status from Head Agent.
- Click any specialist to expand and see latest findings.

### 9.2 "What If" mode

- Toggle button switches dashboard to simulation mode.
- Sliders appear for key variables: "Key engineer leaves" (0-100%), "Biggest client churns" (0-100%), "Critical CVE discovered" (0-100%), "Cloud costs double" (0-100%).
- Head Agent recalculates all cascades in real-time as sliders move.
- Side-by-side comparison: current state vs simulated state.
- Head Agent generates a new briefing for the simulated scenario.

### 9.3 Head Agent activity log

- Scrollable log showing the Head Agent's cross-validation activity.
- Entries like: "People Agent flagged Sarah Chen disengagement (severity 0.85). Queried Code Audit Agent — confirmed: payments-service has 0 code reviews in 14 days. Validated severity raised to 0.91."
- Shows conflict resolutions: "Finance Agent reports runway 9.4 months (healthy). Legal Agent flags Nexus Corp contract breach risk. HEAD AGENT OVERRIDE: If Nexus Corp revenue lost, runway recalculates to 4.2 months. Escalating to critical."

### 9.4 Cascade alert

When a new cascade chain is detected or an existing chain's probability crosses a threshold:

- Toast notification with Head Agent's summary of the cascade.
- Cascade chain highlighted/animated on the graph.
- Alert log with timestamp, full chain details, and Head Agent's recommended intervention.

---

## 10. Judging alignment

Mapping DEADPOOL to the AI Innovation Hack judging rubric:

| Criterion | How DEADPOOL scores |
|-----------|---------------------|
| **Innovative use of AI** | 7-agent hierarchical orchestration with a Head Agent that cross-validates, resolves conflicts, and generates strategic briefings. The Code Audit Agent brings codebase intelligence into business risk analysis — something no existing tool does. |
| **Traction (user signups)** | Deploy a landing page, drive signups from hackathon attendees. Target: 20+ signups during the event. Pitch it as "sign up to get your startup's DEADPOOL score." |
| **Social media traction** | Live-tweet cascade detections. Post the Head Agent's briefings. Visual cascade animations are inherently shareable. The Code Audit Agent finding a real CVE in a demo repo is content gold. |
| **Product-market fit evidence** | Every founder in the room has experienced the problem of siloed monitoring. The Head Agent's unified briefing is the feature that makes people say "I need this." The Code Audit Agent catches what code quality tools miss — business context. |
| **Creative AI use** | Seven agents with hierarchical reasoning. The Head Agent produces insights none of the individual agents could generate alone. Cross-validation creates emergent intelligence — the whole is greater than the sum. |

---

## 11. Request for Hacks alignment

DEADPOOL maps to multiple RFH theses:

- **RFH #02 — Agents That Hire Agents:** The Head Agent dynamically queries specialist agents based on the situation. In the post-hackathon vision, it could spin up new specialist agents as the company grows.
- **RFH #05 — The Product That Builds Itself:** DEADPOOL improves its dependency graph over time as it observes more data, making the product self-evolving.
- **RFH #04 — Intent as Code:** The dependency graph is essentially a company's operational intent encoded as a config — "these are the causal relationships that matter to us."
- **RFH #07 — The One-Person Billion-Dollar Company:** DEADPOOL gives a solo founder the operational awareness of a 50-person leadership team, with the Head Agent acting as their virtual COO.

---

## 12. Hackathon sprint plan

### Day 1 — Build the engine (12:00 PM – midnight)

| Time | Task | Owner |
|------|------|-------|
| 12:00 – 1:00 PM | Set up repo, project scaffold (React + Express), deploy pipeline, define shared constants (entity names, linking keys) | Full team |
| 1:00 – 3:00 PM | People Agent + Finance Agent (data ingestion + anomaly detection prompts) | Dev 1 |
| 1:00 – 3:00 PM | Infra Agent + Code Audit Agent (GitHub API integration + dependency scanning) | Dev 2 |
| 1:00 – 3:00 PM | Dashboard scaffold (React + D3 graph component + Head Agent briefing panel) | Dev 3 |
| 3:00 – 5:00 PM | Product Agent + Legal Agent (analytics data + contract parsing) | Dev 1 |
| 3:00 – 5:00 PM | Head Agent core logic (signal bus subscription, cross-validation routing, briefing generation) | Dev 2 |
| 3:00 – 5:00 PM | Signal bus + cascade mapper integration | Dev 3 |
| 5:00 – 7:00 PM | Full integration: all 6 specialists → signal bus → Head Agent → cascade mapper → dashboard | Full team |
| 7:00 – 8:00 PM | Dinner break |  |
| 8:00 – midnight | End-to-end testing, first live cascade detection, Head Agent cross-validation working, bug fixes | Full team |

### Day 2 — Polish and traction (9:00 AM – 2:30 PM)

| Time | Task | Owner |
|------|------|-------|
| 9:00 – 10:30 AM | "What If" simulation mode powered by Head Agent | Dev 1 |
| 9:00 – 10:30 AM | Head Agent activity log UI + conflict resolution display | Dev 2 |
| 9:00 – 10:30 AM | Landing page for signups + social sharing | Dev 3 |
| 10:30 – 12:00 PM | Cascade animation polish, alert system, Code Audit Agent deep scan | Dev 1 + Dev 2 |
| 10:30 – 12:00 PM | Drive signups: share landing page, post on social | Dev 3 |
| 12:00 – 1:30 PM | Demo rehearsal, edge case fixes | Full team |
| 1:30 – 2:30 PM | Final polish, prepare demo script | Full team |

---

## 13. Demo script (3 minutes)

1. **Hook (30 sec):** "Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities. Seven AI agents. One mission: see the kill chain before it kills you."
2. **Architecture flash (15 sec):** Quick visual of the 7-agent hierarchy. "Six specialist agents monitor every layer of your company. One Head Agent connects the dots."
3. **Live cascade (60 sec):** Show DEADPOOL detecting a cascade. Walk through: "The Code Audit Agent found a critical CVE in the payments service. The People Agent confirmed the only engineer who can patch it has been disengaged for 3 weeks. The Legal Agent flagged that this CVE violates PCI compliance required by the biggest client's contract. The Head Agent connected all three signals and predicted: if unaddressed, this leads to contract breach, 42% revenue loss, and a runway crisis in 75 days."
4. **What If (30 sec):** Toggle simulation. Drag the "engineer leaves" slider. Watch the Head Agent recalculate and generate a new briefing in real-time.
5. **Traction (15 sec):** Flash the landing page, signup count.
6. **Close (10 sec):** "Every startup has a DEADPOOL score. Most founders don't know theirs. Now they can."

---

## 14. Success metrics

### Hackathon success

- All 7 agents running (6 specialists + Head Agent).
- At least one detected cascade spanning 3+ agent domains including the Code Audit Agent.
- Head Agent generating coherent founder briefings with cross-validated evidence.
- Working "What If" mode demonstrated on stage.
- 20+ landing page signups.

### Post-hackathon success (30-day)

- 100+ waitlist signups.
- 5 founder interviews validating the cascade mapping concept.
- One pilot deployment with a real startup.
- Head Agent accuracy tracking: what percentage of flagged cascades were actionable.

---

## 15. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| GitHub API rate limiting during demo | Code Audit Agent can't scan, cascade mapper can't refresh | Pre-cache repo analysis data, implement fallback to last-known state. Code Audit Agent caches CVE lookups. |
| Claude API latency spikes | Head Agent cross-validation is slow, dashboard feels laggy | Run specialist agents in parallel (not sequential). Cache Head Agent responses. Show "Head Agent thinking..." animation. |
| Head Agent produces poor cross-validation | Cascades are inaccurate, briefings are vague | Test Head Agent prompt extensively with edge cases. Have a fallback mode where cascade mapper runs without cross-validation. |
| Code Audit Agent finds nothing interesting | Demo loses the code-to-business cascade angle | Seed the synthetic repo data with a guaranteed CVE and a bus-factor-1 service. Pre-populate dependency scan results. |
| Too many agents = too many failure points | Any one agent failing breaks the demo | Each agent operates independently with graceful degradation. Head Agent notes which specialists are offline. Dashboard shows partial data with "agent unavailable" status. |
| Team burnout overnight | Code quality drops, bugs multiply | Enforce the study break at 4 PM, sleep in shifts, stop coding at midnight and resume fresh at 9 AM |

---

*Built for the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*  
*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities*  
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*