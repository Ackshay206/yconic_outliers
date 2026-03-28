# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

*Seven AI agents. One mission. See the kill chain before it kills your startup.*

---

## The problem

Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

A lead engineer quietly disengages. Nobody notices for three weeks. The payments service she owns stops getting deployed. A critical feature deadline slips. The contract with your biggest client — 42% of revenue — has a delivery clause tied to that feature. The contract lapses. Revenue craters overnight. Your runway drops below three months. The down-round clause in your investor agreement triggers. The company is effectively dead.

Every signal was visible. The GitHub commits were declining. The deployment frequency was dropping. The contract deadline was approaching. The revenue concentration was documented. The investor terms were signed. But no tool, no dashboard, no human connected these dots across domains until the post-mortem.

This is the problem DEADPOOL solves.

---

## The vision

DEADPOOL is a multi-agent startup immune system. Seven AI agents continuously monitor every operational layer of a company — people, finance, infrastructure, product, legal, and codebase — and a Head Agent orchestrates them all, connecting signals across domains to map exactly how a single anomaly cascades into a company-ending failure.

We don't show you isolated metrics. We show you the domino chain. And we show you which domino to catch.

---

## Architecture

### The 7-agent hierarchy

DEADPOOL runs a hierarchical multi-agent system. Six specialist agents are domain experts. One Head Agent is the strategist. The specialists monitor. The Head Agent thinks.

```
                         ┌──────────────────┐
                         │    HEAD AGENT     │
                         │    (Overseer)     │
                         │                  │
                         │  Cross-validates  │
                         │  Resolves conflicts│
                         │  Ranks cascades   │
                         │  Briefs founder   │
                         └────────┬─────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
        ┌───────┴───────┐ ┌──────┴──────┐ ┌────────┴────────┐
        │ People Agent  │ │Finance Agent│ │   Infra Agent   │
        │               │ │             │ │                 │
        │ Team health   │ │ Cash flow   │ │ System uptime   │
        │ Key-person    │ │ Runway      │ │ Deploy velocity │
        │ Engagement    │ │ Revenue     │ │ CI/CD health    │
        └───────────────┘ └─────────────┘ └─────────────────┘
                │                 │                 │
        ┌───────┴───────┐ ┌──────┴──────┐ ┌────────┴────────┐
        │ Product Agent │ │ Legal Agent │ │ Code Audit Agent│
        │               │ │             │ │                 │
        │ User engage.  │ │ Contracts   │ │ CVEs & vulns    │
        │ Churn signals │ │ Compliance  │ │ Tech debt       │
        │ NPS & support │ │ Deadlines   │ │ Bus factor      │
        └───────────────┘ └─────────────┘ └─────────────────┘
                                  │
                         ┌────────┴─────────┐
                         │    Signal Bus     │
                         │  (Anomaly events) │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │  Cascade Mapper   │
                         │                  │
                         │  Traces anomalies │
                         │  through cross-   │
                         │  domain dependency │
                         │  graph            │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │    Dashboard      │
                         │                  │
                         │  Risk score       │
                         │  Cascade chains   │
                         │  Founder briefing │
                         │  What-If mode     │
                         └──────────────────┘
```

### How the agents work together

Every specialist agent monitors its domain on a continuous cycle: ingest data, analyze for anomalies, emit structured anomaly events to the signal bus. But the magic isn't in the individual agents — it's in the Head Agent connecting them.

When the People Agent flags that a key engineer's commit activity dropped 94% over five weeks, the Head Agent doesn't just pass that through. It asks the Code Audit Agent: "What's the state of the code areas this engineer owns?" Code Audit responds: zero code reviews in 14 days, test coverage dropped from 82% to 61%, and there's an unpatched CVE in the payments service dependency. The Head Agent then asks the Legal Agent: "Are there any contracts tied to the payments service?" Legal responds: Nexus Corp contract Section 4.2 requires Payments API v2 delivery by April 15, breach triggers termination without penalty. The Head Agent asks Finance: "What happens if Nexus Corp revenue disappears?" Finance responds: 42% revenue loss, runway drops to 2.5 months, triggering the down-round clause.

No single agent could produce this insight. The Head Agent synthesized signals from four specialists into a cascade chain with quantified probability at every link. That's the product.

### Cross-domain linking

Agents connect data through shared entity keys that are consistent across all data sources:

- `developer_name` links People ↔ Code Audit ↔ Infra (who owns what code and which services)
- `service_name` links Infra ↔ Code Audit ↔ Legal ↔ Product (runtime health to code quality to contract obligations to user experience)
- `client_name` links Finance ↔ Legal (revenue concentration to contract terms)
- `feature_name` links Infra ↔ Legal ↔ Product (delivery progress to deadlines to user engagement)

These linking keys are what make cross-domain cascades discoverable.

---

## The six specialist agents

### People Agent
**Domain:** Team health, engagement, key-person risk.  
**Data sources:** GitHub API (commit frequency, PR activity per developer), Slack API (message frequency, response times).  
**Detects:** Commit drops exceeding 50% week-over-week, prolonged silence from key contributors, workload concentration on a single person, PR review bottlenecks.  
**Cross-references:** Code Audit (which code areas are affected by the person's decline), Infra (which services the person owns), Finance (payroll cost and hiring pipeline impact).

### Finance Agent
**Domain:** Cash flow, runway, revenue, funding terms.  
**Data sources:** CSV/Google Sheets upload, Stripe API (test mode), cap table data.  
**Detects:** Runway dropping below 6 months, revenue concentration exceeding 40% in a single client, burn rate acceleration, approaching investor clause thresholds, payment delays.  
**Cross-references:** Legal (contract values and renewal dates), People (headcount cost impact), Product (health of revenue-driving features).

### Infra Agent
**Domain:** System reliability, deployment operations, performance.  
**Data sources:** GitHub Actions API, health endpoint monitoring, UptimeRobot/BetterStack API, cloud cost tracking.  
**Detects:** Deploy frequency drops, CI failure rate spikes, response time degradation, uptime approaching SLA breach thresholds, cloud cost anomalies.  
**Cross-references:** Code Audit (are code quality issues causing the runtime failures?), People (who owns the degrading service and are they active?), Legal (SLA obligations at risk from the degradation).

### Product Agent
**Domain:** User engagement, retention, satisfaction.  
**Data sources:** Plausible/PostHog API, support ticket data, NPS survey results.  
**Detects:** Feature adoption decline, churn rate increases, NPS dropping below threshold, support ticket volume spikes, sentiment deterioration in customer communications.  
**Cross-references:** Infra (is system performance driving the UX decline?), Code Audit (are bugs in the code causing the errors users see?), Finance (revenue impact of the churn trend).

### Legal Agent
**Domain:** Contracts, compliance, intellectual property, regulatory exposure.  
**Data sources:** Uploaded contract PDFs parsed for key clauses, Federal Register API, SEC EDGAR.  
**Detects:** Contract deadlines approaching with delivery at risk, conflicting terms across multiple agreements, regulatory changes requiring compliance action, IP exposure from open-source license conflicts.  
**Cross-references:** Finance (financial impact of contract breach including refund liabilities), Infra (delivery progress on features tied to contractual obligations), Code Audit (compliance requirements like PCI DSS and SOC 2 mapped to actual code state).

### Code Audit Agent
**Domain:** Codebase health, security posture, architectural integrity, technical debt.  
**Data sources:** GitHub API (file change frequency, code ownership via git blame, PR merge patterns), dependency scanning (package.json/requirements.txt parsed against CVE databases), static analysis signals (test coverage, cyclomatic complexity, code duplication ratio).  
**Detects:** Critical dependency vulnerabilities with CVSS score 7.0 or above, test coverage dropping below 60% for critical services, bus factor of 1 for any critical service, pull requests merged without review in critical paths, circular dependencies, missing error handling in payment and authentication code paths, dependencies more than 2 major versions behind.  
**Cross-references:** People (who wrote and owns the problematic code?), Infra (which running services sit on top of the vulnerable code?), Legal (compliance implications of unpatched vulnerabilities), Product (which user-facing features are built on the degraded code?).

---

## The Head Agent

The Head Agent is the brain of DEADPOOL. It does not monitor data directly. It orchestrates, arbitrates, and synthesizes.

**Cross-validation:** For every anomaly a specialist agent flags, the Head Agent queries one to two other agents for corroboration before passing it to the cascade mapper. This eliminates false positives and enriches true positives with cross-domain context. An anomaly that is confirmed by multiple agents gets its severity raised. An anomaly that is contradicted gets downgraded or retracted.

**Conflict resolution:** When agents produce signals that appear to contradict each other, the Head Agent resolves the conflict with explicit reasoning. Example: Finance Agent reports healthy runway (9.4 months). Legal Agent flags imminent contract breach risk. The Head Agent models the scenario forward — if the contract breach causes the client to terminate, 42% of revenue disappears and runway recalculates to 4.2 months. Legal's signal dominates. The Head Agent documents why.

**Cascade ranking:** When multiple cascade chains are active simultaneously, the Head Agent ranks them using a composite urgency formula:

```
urgency = (1 / time_to_impact_days) × severity × (1 - reversibility)
```

Only the top three cascades are surfaced to the founder. Information overload is itself a risk.

**Founder briefing:** The Head Agent produces a 3-5 sentence plain-language briefing that names the risk, states the timeline, and recommends one specific action. No jargon. No dashboards full of numbers. One clear message: "Here's what's about to happen, here's when, and here's what to do right now."

---

## The Cascade Mapper

The cascade mapper is the engine that traces anomalies forward through a pre-built dependency graph of cross-domain causal relationships.

### How it works

1. The Head Agent validates an anomaly and feeds it to the cascade mapper.
2. The mapper looks up the anomaly type in the dependency graph and identifies all downstream nodes.
3. For each downstream edge, the Head Agent queries the relevant specialist agent for live state data and calculates a conditional probability that this link will fire.
4. If the conditional probability exceeds the threshold (default 0.25), the mapper continues tracing forward to the next node.
5. Chain probabilities are multiplied at each link to produce a cumulative end-to-end cascade probability.
6. The Head Agent scores the resulting cascade chain using the urgency formula and adds it to the active cascade list.

### Pre-built cascade paths

The MVP ships with six pre-seeded cascade paths encoding the most common startup failure patterns:

1. **Key-person departure → code ownership gap → code quality degradation → delivery delays → contract breach → revenue loss → runway crisis.** This is the primary demo cascade. It passes through five of the six specialist agents and produces a dramatic, legible story on stage.

2. **Critical CVE in dependency → compliance breach → legal exposure → investor confidence loss → funding risk.** This cascade starts with the Code Audit Agent and demonstrates how a technical vulnerability cascades into an existential business threat.

3. **Test coverage decline → undetected bugs shipped → user-facing errors → churn spike → revenue drop.** This cascade connects Code Audit to Product to Finance, showing how invisible code quality erosion produces visible business damage.

4. **Technical debt accumulation → deploy velocity drop → feature delivery failure → competitive loss.** This cascade shows how architectural rot slows the entire company down.

5. **Client revenue concentration → single client churn → revenue cliff → down-round trigger.** A pure finance-legal cascade that every seed-stage founder recognizes immediately.

6. **Infrastructure degradation → SLA breach → contract penalty → burn rate spike → runway compression.** This cascade shows how operational issues compound into financial damage through contractual mechanisms.

Each path is encoded as nodes and edges with baseline conditional probabilities. The Head Agent adjusts these probabilities in real-time based on corroborated specialist agent data.

---

## Features

### Dashboard — cascade map

The primary interface is a full-width directed graph showing all active cascade chains. Nodes are color-coded by agent domain: blue for People, green for Finance, orange for Infra, purple for Product, red for Legal, cyan for Code Audit. Edge thickness encodes probability. Active cascades animate with a pulse traveling along the chain from trigger to end-state. Clicking any node expands it to show the specialist agent's raw evidence and the Head Agent's corroboration notes.

### Risk score and founder briefing

A single number from 0 to 100 sits at the top of the dashboard with a color indicator shifting from green through yellow and orange to red. A trend arrow shows whether risk is increasing, stable, or decreasing. Below the score, the Head Agent's latest briefing appears as a 2-3 sentence plain-language summary. A "top action" button shows the single most important thing the founder should do right now.

### Head Agent activity log

A scrollable log showing every cross-validation the Head Agent performed. Entries show which specialist flagged what, which other specialists were queried, whether the anomaly was confirmed or contradicted, and how the severity was adjusted. When agents disagree, the log shows the Head Agent's reasoning for which signal it trusted.

### "What If" simulation mode

A toggle switches the dashboard into simulation mode. Sliders appear for key scenario variables: "Key engineer leaves," "Biggest client churns," "Critical CVE discovered," "Cloud costs double." As sliders move, the Head Agent recalculates all cascade chains in real-time and generates a new briefing for the simulated scenario. The dashboard shows a side-by-side comparison of current state versus simulated state.

### Alert system

When a new cascade chain is detected or an existing chain's probability crosses a severity threshold, a toast notification appears with the Head Agent's summary. The cascade chain highlights and animates on the graph. An alert log stores all historical alerts with timestamps and full chain details.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React + D3.js | D3 handles the dependency graph rendering with animated edges and interactive nodes. React manages dashboard state, panels, and real-time updates. |
| Backend | Python + FastAPI | Async-native, Pydantic v2 for type-safe agent I/O, minimal boilerplate. Handles API polling cycles for all six agents, the signal bus event queue, and the Head Agent orchestration loop. |
| AI orchestration | Anthropic Claude API (claude-sonnet-4-6) | Each specialist agent is a Claude call with a specialized system prompt. The Head Agent is a more comprehensive Claude call with cross-validation routing to query specialists. Total: ~10 Claude calls per monitoring cycle. |
| Data ingestion | JSON synthetic data files (hackathon), GitHub REST API, CSV upload for financials, pip-audit output for dependency scanning | Covers all six specialist agents with minimal integration overhead. |
| Real-time updates | Server-Sent Events (SSE) via sse-starlette | Pushes cascade updates, Head Agent briefings, and risk score changes to the dashboard without client-side polling. |
| Deployment | Vercel (frontend) + Railway (backend) | Free tiers, deploy in under 5 minutes, sufficient for hackathon demo traffic. |

---

## Agent implementation

### Specialist agent pattern

Every specialist follows the same cycle. Only the system prompt and data sources differ.

```
SpecialistAgent(domain, system_prompt, data_sources[]) → Anomaly[]

Every 5 minutes:
  1. Poll data sources for latest state
  2. Send current state + system prompt to Claude API
  3. Claude returns structured JSON: anomalies with severity, confidence,
     affected entities, evidence, and cross-references
  4. Publish anomalies to signal bus
  5. Head Agent picks up the anomaly for cross-validation
```

### Head Agent pattern

The Head Agent operates on a different cycle — it's event-driven, triggered by new anomalies on the signal bus.

```
HeadAgent(specialists[], signal_bus, cascade_mapper) → Briefing

On new anomaly:
  1. Identify which specialists should corroborate
     (People flags person → ask Code Audit + Infra)
     (Code Audit flags CVE → ask Legal + Infra)
     (Finance flags revenue risk → ask Legal)
     (Infra flags degradation → ask Code Audit + People)
     (Product flags churn → ask Infra + Code Audit)
     (Legal flags deadline → ask Infra + Finance)
  2. Query those specialists for supporting/contradicting evidence
  3. Assign validated_severity (may raise, lower, or retract)
  4. Feed validated anomaly into cascade mapper
  5. Rank all active cascades by urgency
  6. Generate founder briefing: top 3 risks, plain language, one action
  7. Push briefing + updated risk score to dashboard
```

---

## Data architecture

### Synthetic data strategy

For the hackathon demo, we use carefully constructed synthetic data that represents a realistic seed-stage SaaS startup over 12 weeks. The data is designed so that agents genuinely discover cascade chains from the data — they are not told what to find.

Six JSON data files, one per specialist agent domain:

- **team_activity.json** — 12 developers with weekly commit, PR, and response time data. One developer (the cascade trigger) shows a gradual five-week disengagement pattern. Eleven developers show normal patterns with realistic noise (vacations, sprint spikes).

- **financials.json** — 12 months of revenue by client, expenses by category, cash balance, burn rate, and runway. One client represents 42% of revenue. Investor agreement includes a down-round clause triggered at runway below 3 months.

- **infrastructure.json** — 6 microservices with weekly deploy counts, uptime percentages, response times, error rates, and cloud costs. The payments service degrades in correlation with the lead engineer's decline. Other services remain stable.

- **product_metrics.json** — Weekly active users, feature-level engagement data, support ticket volume and sentiment, NPS scores, and churn rates. The payments dashboard feature shows declining usage and rising errors. Other features remain healthy.

- **contracts.json** — 4 client contracts with parsed clauses including delivery deadlines and SLA guarantees. One investor agreement with a down-round clause. PCI DSS compliance obligation linked to the payments service.

- **codebase_audit.json** — Repository-level analysis including file change frequency, code ownership maps, dependency vulnerability scan results, test coverage per service, PR review patterns, and architecture signals. The payments service has a bus factor of 1, a critical unpatched CVE, and declining test coverage.

All files share consistent entity linking keys: developer names, service names, client names, and feature names are identical across files so the Head Agent and cascade mapper can trace connections.

### Cross-reference linking keys

| Key | Connects |
|-----|----------|
| `developer_name` | People ↔ Code Audit ↔ Infra — maps a person to the code they write and the services they run |
| `service_name` | Infra ↔ Code Audit ↔ Legal ↔ Product — maps a running service to its code health, contract obligations, and user experience |
| `client_name` | Finance ↔ Legal — maps revenue streams to contract terms and breach consequences |
| `feature_name` | Infra ↔ Legal ↔ Product — maps a deliverable to its deadline, deployment status, and user engagement |

---

## Cascade demonstration

### Primary demo cascade (5 agents, 6 nodes)

This is the cascade we demonstrate on stage. It passes through People → Code Audit → Infra → Legal → Finance → Finance (investor terms), showing DEADPOOL's cross-domain intelligence.

```
Step 1 │ PEOPLE AGENT detects
       │ Sarah Chen commit activity dropped 94% over 5 weeks
       │ Severity: 0.85 → Head Agent validates to 0.91
       │ (Code Audit confirms: 0 code reviews in her areas for 14 days)
       │
       ▼ Conditional probability: 0.78
       │
Step 2 │ CODE AUDIT AGENT confirms
       │ payments-service: bus factor = 1, test coverage dropped to 61%,
       │ unpatched CVE-2026-4821 (CVSS 8.1) in payment processing dependency
       │ Severity: 0.82
       │
       ▼ Conditional probability: 0.72
       │
Step 3 │ INFRA AGENT reports
       │ payments-service deploy frequency: 0 in last 2 weeks
       │ Payments API v2 at 34% completion, deadline in 18 days
       │ Projected miss: 30+ days overdue
       │ Severity: 0.79
       │
       ▼ Conditional probability: 0.58
       │
Step 4 │ LEGAL AGENT flags
       │ Nexus Corp contract Section 4.2: delivery of Payments API v2
       │ required by April 15, 2026. Breach = termination without penalty.
       │ Refund liability: $211,680
       │ Severity: 0.88
       │
       ▼ Conditional probability: 0.65
       │
Step 5 │ FINANCE AGENT calculates
       │ Nexus Corp = 42% of revenue ($35,280/month)
       │ Post-loss monthly burn: $80,000 net negative
       │ After refund: cash drops to ~$200,000
       │ Runway: 2.5 months
       │ Severity: 0.92
       │
       ▼ Conditional probability: 0.75
       │
Step 6 │ FINANCE AGENT (investor terms) triggers
       │ Down-round clause activates below 3-month runway
       │ Investor converts at 50% discount with 2x liquidation preference
       │ Founder diluted below control threshold
       │ END STATE: Company effectively lost
       │
       │ Overall cascade probability: 0.19
       │ Time to impact: 75 days
       │ Financial impact: $1.9M+
```

**Head Agent briefing for this cascade:**

> "Your lead backend engineer has been disengaging for five weeks, and she's the only person who can ship the payments feature that Nexus Corp's contract requires by April 15. The Code Audit Agent found an unpatched critical vulnerability in the same service. If the deadline is missed, Nexus Corp can walk — taking 42% of your revenue with them. That drops your runway below three months and triggers the down-round clause in your investor agreement. Talk to Sarah Chen today. Start a knowledge transfer to a backup engineer this week. Contact Nexus Corp about a deadline extension before April 1."

---

## Execution plan

### Day 1 — Build the engine (12:00 PM – midnight)

**12:00 – 1:00 PM:** Repository setup, project scaffold (React + Express), deployment pipeline, shared constants file defining all entity linking keys.

**1:00 – 3:00 PM (parallel tracks):**
- Dev 1: People Agent + Finance Agent — data ingestion, anomaly detection prompts, signal bus integration.
- Dev 2: Infra Agent + Code Audit Agent — GitHub API integration, dependency scanning, CVE cross-referencing.
- Dev 3: Dashboard scaffold — React layout, D3 graph component, Head Agent briefing panel, risk score display.

**3:00 – 5:00 PM (parallel tracks):**
- Dev 1: Product Agent + Legal Agent — analytics data parsing, contract clause extraction.
- Dev 2: Head Agent core logic — signal bus subscription, cross-validation routing between specialists, briefing generation prompt.
- Dev 3: Signal bus implementation + cascade mapper integration with dependency graph.

**5:00 – 7:00 PM:** Full team integration sprint. Wire all six specialists → signal bus → Head Agent → cascade mapper → dashboard. First end-to-end test.

**7:00 – 8:00 PM:** Dinner.

**8:00 PM – midnight:** Testing, debugging, first live cascade detection. Verify Head Agent cross-validation produces coherent corroboration. Fix edge cases. Ensure graceful degradation if any single agent fails.

### Day 2 — Polish and traction (9:00 AM – 2:30 PM)

**9:00 – 10:30 AM:**
- Dev 1: "What If" simulation mode powered by Head Agent cascade recalculation.
- Dev 2: Head Agent activity log UI showing cross-validation reasoning and conflict resolution.
- Dev 3: Landing page for signups with social sharing integration.

**10:30 AM – 12:00 PM:**
- Dev 1 + Dev 2: Cascade animation polish, alert notification system, Code Audit Agent deep scan visualization.
- Dev 3: Drive signups — share landing page across social media, hackathon Slack channels, and in-person with attendees.

**12:00 – 1:30 PM:** Demo rehearsal. Run through the 3-minute script at least three times. Test every transition. Prepare for questions.

**1:30 – 2:30 PM:** Final polish. Freeze code. Prepare demo environment with pre-loaded data and fallback states.

---

## Demo script (3 minutes)

**0:00 – 0:30 | The hook.**
"Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities. Seven AI agents. One mission: see the kill chain before it kills you."

**0:30 – 0:45 | Architecture flash.**
Show the 7-agent hierarchy on screen. "Six specialist agents monitor every layer of your company — your team, your money, your infrastructure, your product, your contracts, and your code. One Head Agent connects the dots across all of them."

**0:45 – 1:45 | Live cascade.**
Walk through the primary cascade on the dashboard. "The Code Audit Agent found a critical CVE in the payments service. The People Agent confirmed the only engineer who can patch it has been disengaged for three weeks. The Legal Agent flagged that this vulnerability violates PCI compliance required by the biggest client's contract. The Finance Agent calculated what happens if that client walks. The Head Agent connected all four signals and predicted: if unaddressed, this leads to contract breach in 18 days, 42% revenue loss, and a runway crisis in 75 days. Here's the cascade chain on screen — every link, every probability, every dollar amount."

**1:45 – 2:15 | What If mode.**
Toggle simulation. "But what if we act? Watch." Drag the "engineer leaves" slider to 100%. The Head Agent recalculates in real-time. New briefing appears. "Now watch what happens when we assign a backup engineer." Adjust the slider. Cascade probability drops. Risk score drops. "DEADPOOL doesn't just find the problem — it tells you exactly where to break the chain."

**2:15 – 2:45 | Traction.**
Flash the landing page. Show signup count. "We launched this landing page 20 hours ago. [X] founders have already signed up to get their DEADPOOL score."

**2:45 – 3:00 | Close.**
"Every startup has a DEADPOOL score right now. Most founders don't know theirs. Now they can."

---

## Why this wins

**Innovative use of AI:** Seven-agent hierarchical orchestration with a Head Agent that cross-validates across domains, resolves conflicts between agents, and generates strategic briefings. The Code Audit Agent brings codebase intelligence into business risk analysis — something no existing tool does. This isn't six chatbots in a trenchcoat. This is emergent intelligence from structured multi-agent coordination.

**Traction:** Landing page deployed by Day 1 evening. Target: 20+ signups from hackathon attendees and social media. Every signup is a founder who wants their DEADPOOL score.

**Product-market fit:** Every founder in the room has experienced siloed monitoring. Every founder has been blindsided by a chain reaction they could have predicted. The Head Agent's unified briefing is the feature that makes people say "I need this yesterday."

**Creative AI use:** The cascade mapper produces insights that no individual agent could generate. The Head Agent's cross-validation creates a system where the whole is demonstrably greater than the sum of its parts. The Code Audit Agent catches what traditional code quality tools miss — business context for technical debt.

**Ship It Ugly:** We're not building a polished SaaS. We're building a working intelligence system that detects real cascades from real data. The cascade chain on stage is the product. Everything else is a wrapper.

---

## Request for Hacks alignment

**RFH #02 — Agents That Hire Agents:** The Head Agent dynamically queries specialist agents based on the situation. In the post-hackathon vision, it could autonomously spin up new specialist agents as the company grows or enters new domains.

**RFH #04 — Intent as Code:** The dependency graph is a company's operational intent encoded as configuration — "these are the causal relationships that matter to us." Every agent inherits the company's priorities through the graph structure.

**RFH #05 — The Product That Builds Itself:** DEADPOOL's dependency graph improves over time as the Head Agent observes which cascades materialize and which don't. The system learns which cross-domain links are real and which are noise.

**RFH #07 — The One-Person Billion-Dollar Company:** DEADPOOL gives a solo founder the operational awareness of a 50-person leadership team. The Head Agent is their virtual COO — always watching, always connecting, always briefing.

---

## Success criteria

- All 7 agents running and producing structured output.
- At least one detected cascade spanning 3+ agent domains including the Code Audit Agent.
- Head Agent generating coherent founder briefings with cross-validated evidence.
- Working "What If" simulation mode demonstrated on stage.
- 20+ landing page signups.
- The audience understands the cascade chain in under 60 seconds.

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities.*  
*Built at the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*  
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*