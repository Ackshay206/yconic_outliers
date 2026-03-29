# DEADPOOL

### **D**ependency **E**valuation **A**nd **D**ownstream **P**rediction **O**f **O**perational **L**iabilities

*Seven AI agents. One mission. See the kill chain before it kills your startup.*

---

## The problem

Startups don't die from one thing. They die from a chain reaction that nobody mapped until it was too late.

A mobile engineer quietly disengages. Nobody notices for three weeks. The feed algorithm he was building stops improving and the Branded Content SDK he was architecting stops making progress. A critical enterprise deal — $516K/year with VibeCheck Media, the company's path to real brand monetization revenue — has a delivery clause tied to that SDK. The deadline passes. The deal collapses. The startup stays pre-revenue (aside from a trickle of $2,400/month in Brainrot Pro subscriptions), burning $80K/month on $535K in the bank. Runway shrinks month by month. The down-round clause in the investor agreement triggers. The company is effectively dead.

Every signal was visible. The GitHub commits were declining. The deployment frequency was dropping. The contract deadline was approaching. The revenue concentration was documented. The investor terms were signed. Creator engagement metrics were softening. But no tool, no dashboard, no human connected these dots across domains until the post-mortem.

This is the problem DEADPOOL solves.

---

## The company: Brainrot

Brainrot is a Gen Z social media platform built around short-form video, meme culture, and AI-native content moderation. Founded by an ex-TikTok PM and an ex-Discord engineer, Brainrot differentiates from TikTok and Instagram with an algorithm that prioritizes "authentic chaos" — raw, unpolished, culturally-aware content over manufactured influencer polish. The platform reached 340K MAU in six months, has a growing creator program, and is pursuing brand partnerships as its primary monetization path through a Branded Content SDK that lets advertisers create native, creator-style sponsored content inside the app.

The company is a 10-person seed-stage startup based in Brooklyn, backed by $975K total funding ($175K pre-seed angel + $800K seed from Velocity Capital). They are pre-revenue aside from ~160 Brainrot Pro subscribers paying $14.99/month for ad-free access and exclusive filters. The make-or-break moment: a $516K/year enterprise brand partnership deal with VibeCheck Media that depends on shipping the Branded Content SDK by April 15, 2026.

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

When the People Agent flags that a key engineer's commit activity dropped 60% and they've gone on unpaid leave, the Head Agent doesn't just pass that through. It asks the Code Audit Agent: "What's the state of the code areas this engineer owns?" Code Audit responds: zero code reviews in 14 days, test coverage dropped from 79% to 58%, and there's an unpatched CVE in the video processing dependency that handles creator uploads. The Head Agent then asks the Infra Agent: "What feature was this engineer building?" Infra responds: the Branded Content SDK is stalled at 31% completion — no one else has context on the feed-service integration. The Head Agent then asks Finance: "What depends on the Branded Content SDK?" Finance responds: the VibeCheck Media enterprise deal ($516K/year, currently in procurement) has an April 15 hard deadline for SDK deployment. If the deal collapses, the company stays effectively pre-revenue at $2,400/month in Brainrot Pro subscriptions with $535K cash and $80K/month burn — that's 6.6 months of runway with no path to extending it. Within 3.7 months of that, the down-round clause in the Velocity Capital agreement triggers. Meanwhile, the Product Agent reports that feed quality has been declining for weeks — the recommendation algorithm that Engineer 3 was tuning is now serving stale and low-quality content, driving creators to competitor Fizz.

No single agent could produce this insight. The Head Agent synthesized signals from five specialists into a cascade chain with quantified probability at every link. That's the product.

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
**Detects:** Commit drops exceeding 50% week-over-week, prolonged silence from key contributors, workload concentration on a single person, PR review bottlenecks. In Brainrot's case, the critical signal is Engineer 3 (Mobile/Feed) going from 35 commits/week to near-zero over five weeks while owning the feed algorithm and Branded Content SDK.  
**Cross-references:** Code Audit (which code areas are affected by the person's decline), Infra (which services the person owns), Finance (payroll cost and hiring pipeline impact).

### Finance Agent
**Domain:** Cash flow, runway, revenue pipeline, funding terms.  
**Data sources:** Three CSV files — `deadpool_finance_data.csv` (transaction ledger covering every dollar from Brainrot's founding through March 2026), `deadpool_revenue_pipeline.csv` (Brainrot Pro subscriptions, Drip Culture Agency overdue invoices, and pipeline deals including the VibeCheck Media $516K/year enterprise brand partnership), `deadpool_funding_runway.csv` (Velocity Capital terms, down-round clause, monthly summaries, and runway scenario projections).  
**Detects:** Runway approaching 6-month threshold, burn rate acceleration (especially from unoptimized video CDN costs), pipeline deals at risk due to feature dependencies (VibeCheck deal probability dropped from 0.85 to 0.30), overdue invoices (Drip Culture Agency $12K outstanding), approaching investor clause thresholds (down-round at runway < 3 months), revenue projections under different scenarios showing best case at 15.3 months runway vs worst case at 3.7 months to clause trigger.  
**Cross-references:** Legal (contract terms and deadlines), People (headcount cost impact, key-person dependency on pipeline deals), Infra (feature delivery status blocking pipeline deals), Product (churn impact on subscription revenue and creator retention).

### Infra Agent
**Domain:** System reliability, deployment operations, performance.  
**Data sources:** GitHub Actions API, health endpoint monitoring, UptimeRobot/BetterStack API, cloud cost tracking.  
**Detects:** Deploy frequency drops (feed-service went from 4-5 deploys/week to zero), CI failure rate spikes, response time degradation (feed-service latency up 4x from video processing bottlenecks), uptime approaching SLA breach thresholds, cloud cost anomalies (video CDN costs tripled due to unoptimized MediaConvert pipeline that nobody is maintaining since DevOps is fire-fighting feed outages).  
**Cross-references:** Code Audit (are code quality issues causing the runtime failures?), People (who owns the degrading service and are they active?), Legal (SLA obligations at risk from the degradation).

### Product Agent
**Domain:** User engagement, retention, satisfaction, creator health.  
**Data sources:** Plausible/PostHog API, support ticket data, NPS survey results, creator dashboard metrics.  
**Detects:** Feature adoption decline (Branded Content beta usage dropping as SDK stalls), churn rate increases (creator accounts deactivating up 3x since February), NPS dropping below threshold (from +42 to -5 over 5 weeks), support ticket volume spikes (content moderation complaints and feed quality complaints surging), sentiment deterioration in creator communications, top creators publicly posting about switching to Fizz.  
**Cross-references:** Infra (is feed-service performance driving the UX decline?), Code Audit (are bugs in the recommendation algorithm causing the degraded feed?), Finance (revenue impact of creator churn on both subscriptions and the VibeCheck deal — VibeCheck wants access to Brainrot's creator network, which is eroding).

### Legal Agent
**Domain:** Contracts, compliance, intellectual property, regulatory exposure.  
**Data sources:** Uploaded contract PDFs parsed for key clauses, Federal Register API, SEC EDGAR, COPPA compliance requirements.  
**Detects:** Contract deadlines approaching with delivery at risk (VibeCheck Media April 15 SDK deadline), conflicting terms across multiple agreements, regulatory changes requiring compliance action (new COPPA enforcement re: Gen Z platforms handling under-18 users), IP exposure from open-source license conflicts in the video processing pipeline, GDPR implications of the recommendation algorithm's data collection.  
**Cross-references:** Finance (financial impact of contract breach including refund liabilities — VibeCheck walking away means $516K/year never materializes), Infra (delivery progress on Branded Content SDK tied to contractual obligations), Code Audit (compliance requirements like COPPA and SOC 2 mapped to actual code state of content moderation and data handling services).

### Code Audit Agent
**Domain:** Codebase health, security posture, architectural integrity, technical debt.  
**Data sources:** GitHub API (file change frequency, code ownership via git blame, PR merge patterns), dependency scanning (package.json/requirements.txt parsed against CVE databases), static analysis signals (test coverage, cyclomatic complexity, code duplication ratio).  
**Detects:** Critical dependency vulnerabilities with CVSS score 7.0 or above (unpatched CVE in the video processing library ffmpeg-wasm used for creator uploads), test coverage dropping below 60% for critical services (feed-service dropped from 79% to 58%), bus factor of 1 for feed-service and content-moderation-service (both owned solely by Engineer 3), pull requests merged without review in critical paths, circular dependencies between feed-service and content-moderation-service, missing error handling in the recommendation algorithm's fallback logic, video processing dependencies more than 2 major versions behind.  
**Cross-references:** People (who wrote and owns the problematic code? — Engineer 3 is the sole contributor to feed-service), Infra (which running services sit on top of the vulnerable code? — the entire content delivery pipeline), Legal (compliance implications of unpatched vulnerabilities in a platform handling Gen Z user data including minors), Product (which user-facing features are built on the degraded code? — the core feed experience that defines Brainrot's value proposition).

---

## The Head Agent

The Head Agent is the brain of DEADPOOL. It does not monitor data directly. It orchestrates, arbitrates, and synthesizes.

**Cross-validation:** For every anomaly a specialist agent flags, the Head Agent queries one to two other agents for corroboration before passing it to the cascade mapper. This eliminates false positives and enriches true positives with cross-domain context. An anomaly that is confirmed by multiple agents gets its severity raised. An anomaly that is contradicted gets downgraded or retracted. For Brainrot, the Head Agent's cross-validation is particularly powerful because the cascade touches nearly every domain: a people problem (Engineer 3) manifests as a code quality problem (bus factor, CVE), which causes an infrastructure problem (feed-service degradation), which drives a product problem (creator churn, feed quality), which threatens a financial outcome (VibeCheck deal collapse), which triggers a legal consequence (investor clause).

**Conflict resolution:** When agents produce signals that appear to contradict each other, the Head Agent resolves the conflict with explicit reasoning. Example: Finance Agent reports healthy runway (6.9 months). Legal Agent flags imminent contract breach risk on the VibeCheck deal. The Head Agent models the scenario forward — if the VibeCheck deal collapses because the Branded Content SDK isn't delivered by April 15, $516K/year in brand revenue never materializes, the creator exodus to Fizz accelerates (reducing Brainrot Pro subscription revenue), and runway recalculates to a declining trajectory. Legal's signal dominates. The Head Agent documents why, including the second-order effect: VibeCheck's 200+ brand advertisers choosing Fizz instead would effectively validate the competitor and make future brand deals harder to close.

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

1. **Key-person departure → code ownership gap → code quality degradation → delivery delays → contract breach → revenue loss → runway crisis.** This is the primary demo cascade. It passes through five of the six specialist agents and produces a dramatic, legible story on stage. For Brainrot, this traces from Engineer 3's disengagement through the feed-service collapse, Branded Content SDK stall, VibeCheck deal death, and ultimately the Velocity Capital down-round clause trigger.

2. **Critical CVE in dependency → compliance breach → legal exposure → investor confidence loss → funding risk.** This cascade starts with the Code Audit Agent finding the unpatched ffmpeg-wasm vulnerability in Brainrot's video processing pipeline and demonstrates how a technical vulnerability in a Gen Z social platform handling minor users' data cascades into an existential business threat via COPPA exposure.

3. **Test coverage decline → undetected bugs shipped → user-facing errors → churn spike → revenue drop.** This cascade connects Code Audit to Product to Finance, showing how invisible code quality erosion in the feed algorithm produces visible business damage — in Brainrot's case, the degraded recommendation algorithm serving low-quality content that drives creators to Fizz.

4. **Technical debt accumulation → deploy velocity drop → feature delivery failure → competitive loss.** This cascade shows how architectural rot slows the entire company down. For Brainrot, the circular dependency between feed-service and content-moderation-service means every change risks breaking both, and the video processing pipeline's outdated dependencies make feature iteration impossible.

5. **Client revenue concentration → single client churn → revenue cliff → down-round trigger.** A pure finance-legal cascade that every seed-stage founder recognizes immediately. Brainrot's entire monetization thesis depends on the VibeCheck deal — without it, there is no path from $2,400/month in subscriptions to sustainable revenue.

6. **Infrastructure degradation → SLA breach → contract penalty → burn rate spike → runway compression.** This cascade shows how operational issues compound into financial damage through contractual mechanisms. For Brainrot, the unoptimized video CDN spending ($7,200/month and climbing vs. an estimated $2,400/month if properly configured) is silently accelerating burn rate while DevOps is distracted by feed-service outages.

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

A toggle switches the dashboard into simulation mode. Sliders appear for key scenario variables: "Key engineer leaves," "Biggest client churns," "Critical CVE discovered," "Cloud costs double," "Top 10 creators leave for Fizz." As sliders move, the Head Agent recalculates all cascade chains in real-time and generates a new briefing for the simulated scenario. The dashboard shows a side-by-side comparison of current state versus simulated state, including how creator network health affects the VibeCheck deal probability.

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

For the hackathon demo, we use carefully constructed synthetic data that represents Brainrot — a realistic seed-stage Gen Z social media startup over 12 weeks. The data is designed so that agents genuinely discover cascade chains from the data — they are not told what to find.

The company narrative: Brainrot launched its beta in late 2025, hit 100K signups by December, grew to 340K MAU by March 2026, and is pursuing brand partnerships as its monetization model. The founding team is strong (ex-TikTok, ex-Discord), the product has real traction (Gen Z users love the "authentic chaos" feed), but a single engineer's departure threatens to unravel everything because the feed algorithm, content moderation pipeline, and Branded Content SDK all have a bus factor of one.

Six JSON data files, one per specialist agent domain, plus three CSV files for the Finance Agent:

- **deadpool_finance_data.csv** — Transaction-level ledger from Sep 2025 through Mar 2026: every income event (funding rounds, Brainrot Pro subscription revenue) and every expense (salaries by person, video CDN costs, API fees for content moderation, reimbursements, coworking rent). Running balance tracked. Covers $175K pre-seed from Kevin Tran's angel syndicate, $800K seed from Velocity Capital, team growing from 2 founders to 10 employees, burn rate escalation driven heavily by unoptimized video delivery infrastructure, and the emerging cash crisis.

- **deadpool_revenue_pipeline.csv** — Revenue actuals (Brainrot Pro subscriptions at $14.99/month), accounts receivable (Drip Culture Agency overdue invoices from a branded content pilot), and pipeline deals with probabilities. The VibeCheck Media enterprise deal ($516K/year) is in procurement with a hard April 15 deadline tied to the Branded Content SDK. Pipeline status degrades from 0.85 probability to 0.30 as Engineer 3 goes on leave and competitor Fizz enters the conversation. Secondary pipeline includes NovaBrands (stalled — champion left) and StudyHive (delayed by COPPA/SOC 2 gaps).

- **deadpool_funding_runway.csv** — Funding round details, investor clause terms (Velocity Capital down-round trigger at runway < 3 months, consequence: Jenna Okafor takes board control), monthly financial summaries (burn, revenue, cash, runway), and scenario projections (base case 6.9 months vs. VibeCheck closes at 15.3 months vs. worst case 3.7 months to clause trigger).

- **team_activity.json** — 10 team members with weekly commit, PR, and response time data. Engineer 3 (Mobile/Feed) shows gradual disengagement: 60% commit drop in Feb, on unpaid leave in March. Other team members show normal patterns with realistic noise including a designer taking a week off for a wedding and a DevOps engineer having a spike week before a CDN migration.

- **infrastructure.json** — 6 microservices with weekly deploy counts, uptime percentages, response times, error rates, and cloud costs. The feed-service and content-moderation-service degrade in correlation with Engineer 3's decline. Video CDN costs are the standout anomaly — $7,200/month and climbing when they should be $2,400/month with proper optimization. Other services (api-gateway, creator-dashboard, notification-service, analytics-pipeline) remain stable.

- **product_metrics.json** — Weekly active users (340K MAU peak, now declining), feature-level engagement data (feed session duration dropping, Branded Content beta usage cratering), support ticket volume and sentiment (content moderation complaints up 3x, creator accounts deactivating), NPS scores (dropped from +42 to -5), and churn rates (creator churn up 3x). The feed experience — Brainrot's core value proposition — shows clear degradation while other features like creator onboarding and direct messaging remain healthy.

- **contracts.json** — VibeCheck Media deal terms (draft contract with April 15 Branded Content SDK delivery clause, $516K/year annual value), Drip Culture Agency pilot (payment dispute), StudyHive pilot (delayed by COPPA compliance). Investor agreement with down-round clause. COPPA compliance obligation linked to content-moderation-service and user data handling — particularly sensitive given Brainrot's Gen Z audience includes users under 18.

- **codebase_audit.json** — Repository-level analysis including file change frequency, code ownership maps, dependency vulnerability scan results (CVE in ffmpeg-wasm video processing library), test coverage per service (feed-service dropped to 58%), PR review patterns (PRs merged without review in feed-service critical paths), and architecture signals (circular dependency between feed-service and content-moderation-service). The feed-service has a bus factor of 1, and Engineer 3 is the sole meaningful contributor.

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

This is the cascade we demonstrate on stage. It passes through People → Code Audit → Infra → Finance (pipeline) → Finance (runway) → Finance (investor terms), showing DEADPOOL's cross-domain intelligence. The Brainrot narrative makes this particularly compelling because every founder in the room understands what happens when your best engineer quietly checks out and they're the only person who understands the code that your biggest deal depends on.

```
Step 1 │ PEOPLE AGENT detects
       │ Engineer 3 (Mobile/Feed) commit activity dropped 60%, now on unpaid leave
       │ Sole architect of feed algorithm + Branded Content SDK
       │ Severity: 0.85 → Head Agent validates to 0.88
       │ (Code Audit confirms: 0 code reviews in feed-service for 14 days)
       │
       ▼ Conditional probability: 0.78
       │
Step 2 │ CODE AUDIT AGENT confirms
       │ feed-service: bus factor = 1, test coverage dropped to 58%,
       │ unpatched CVE-2026-3847 (CVSS 8.4) in ffmpeg-wasm video processing dependency
       │ Circular dependency with content-moderation-service means changes risk both
       │ Severity: 0.84
       │
       ▼ Conditional probability: 0.72
       │
Step 3 │ INFRA AGENT reports
       │ feed-service deploy frequency: 0 in last 2 weeks
       │ Branded Content SDK at 31% completion, deadline in 18 days
       │ Video CDN costs at $7,200/mo (should be $2,400 — no one optimizing)
       │ Projected miss: 35+ days overdue. No other engineer has context.
       │ Severity: 0.81
       │
       ▼ Conditional probability: 0.65
       │
Step 4 │ FINANCE AGENT (pipeline) flags
       │ VibeCheck Media deal ($516K/year) in procurement — hard deadline April 15
       │ for Branded Content SDK deployment. Deal probability dropped from 0.85 to 0.30.
       │ VibeCheck CEO asking for status update. They're evaluating Fizz.
       │ If VibeCheck chooses Fizz, their 200+ brand advertisers validate the competitor.
       │ Severity: 0.90
       │
       ▼ Conditional probability: 0.70
       │
Step 5 │ FINANCE AGENT (runway) calculates
       │ Without VibeCheck: $535K cash, $80K/month burn, $2.4K/month revenue
       │ Runway: 6.6 months and declining — no revenue inflection path
       │ Drip Culture Agency $12K overdue compounds cash position
       │ Video CDN overspend silently accelerating burn by $4,800/month
       │ Severity: 0.77
       │
       ▼ Conditional probability: 0.60
       │
Step 6 │ FINANCE AGENT (investor terms) projects
       │ Down-round clause triggers at runway < 3 months
       │ At current burn: ~3.7 months until trigger
       │ Velocity Capital converts at 50% discount with 2x liquidation preference
       │ Jenna Okafor takes full board seat — founder diluted below control threshold
       │ END STATE: Company effectively lost
       │
       │ Overall cascade probability: 0.17
       │ Time to impact: 112 days
       │ Financial impact: $1.5M+ (deal lost + dilution + runway crisis + creator network collapse)
```

**Head Agent briefing for this cascade:**

> "Engineer 3 has been disengaging since February and is now on unpaid leave. He's the only person with context on the feed algorithm and the Branded Content SDK — which is at 31% completion with 18 days until the VibeCheck Media deadline. The Code Audit Agent found an unpatched critical vulnerability in the video processing pipeline and test coverage on feed-service has collapsed to 58%. VibeCheck Media's $516K/year enterprise brand deal requires the SDK live by April 15 or the deal collapses — and they're already talking to Fizz. Without that deal, you're a pre-revenue company burning $80K/month with $535K in the bank. That's 6.6 months of runway with no path to extending it. In 3.7 months you hit the down-round clause threshold, and Velocity Capital takes board control. Meanwhile, your video CDN is burning $4,800/month more than it should because nobody is optimizing it. Resolve Engineer 3's situation or start knowledge transfer to a backup engineer this week. Contact VibeCheck about a deadline extension before April 1."

---

## Execution plan

### Day 1 — Build the engine (12:00 PM – midnight)

**12:00 – 1:00 PM:** Repository setup, project scaffold (React + FastAPI), deployment pipeline, shared constants file defining all entity linking keys. Confirm all synthetic data files are consistent (Brainrot company narrative, entity names aligned across all JSON/CSV files).

**1:00 – 3:00 PM (parallel tracks):**
- Dev 1: People Agent + Finance Agent — data ingestion from team_activity.json and three CSV files, anomaly detection prompts tuned to Brainrot's team structure and financial model, signal bus integration.
- Dev 2: Infra Agent + Code Audit Agent — GitHub API integration, dependency scanning for the video processing pipeline, CVE cross-referencing, feed-service degradation detection.
- Dev 3: Dashboard scaffold — React layout, D3 graph component with Brainrot-themed color scheme, Head Agent briefing panel, risk score display.

**3:00 – 5:00 PM (parallel tracks):**
- Dev 1: Product Agent + Legal Agent — creator engagement metrics parsing, content moderation complaint analysis, contract clause extraction for VibeCheck deal terms and COPPA obligations.
- Dev 2: Head Agent core logic — signal bus subscription, cross-validation routing between specialists (especially the People → Code Audit → Infra → Finance chain), briefing generation prompt tuned to produce founder-readable output.
- Dev 3: Signal bus implementation + cascade mapper integration with dependency graph. Pre-seed the six cascade paths with Brainrot-specific baseline probabilities.

**5:00 – 7:00 PM:** Full team integration sprint. Wire all six specialists → signal bus → Head Agent → cascade mapper → dashboard. First end-to-end test with Brainrot synthetic data. Verify the primary cascade (Engineer 3 → feed-service → VibeCheck deal → runway crisis) fires correctly.

**7:00 – 8:00 PM:** Dinner.

**8:00 PM – midnight:** Testing, debugging, first live cascade detection. Verify Head Agent cross-validation produces coherent corroboration — especially the critical path where it connects Engineer 3's people data to the code audit findings to the infra degradation to the financial impact. Fix edge cases. Ensure graceful degradation if any single agent fails. Test that noise anomalies (Drip Culture overdue invoices, NovaBrands stalled deal) don't trigger false cascade alerts.

### Day 2 — Polish and traction (9:00 AM – 2:30 PM)

**9:00 – 10:30 AM:**
- Dev 1: "What If" simulation mode powered by Head Agent cascade recalculation. Key sliders: "Engineer 3 returns," "VibeCheck deal probability," "Top creators leave for Fizz," "Video CDN optimized."
- Dev 2: Head Agent activity log UI showing cross-validation reasoning and conflict resolution between Finance (healthy runway number) and Legal (imminent contract breach).
- Dev 3: Landing page for signups with social sharing integration. Messaging: "Every startup has a DEADPOOL score. What's yours?"

**10:30 AM – 12:00 PM:**
- Dev 1 + Dev 2: Cascade animation polish (the primary cascade should animate smoothly from the People node through all five downstream nodes), alert notification system, Code Audit Agent deep scan visualization showing the ffmpeg-wasm CVE and bus factor analysis.
- Dev 3: Drive signups — share landing page across social media, hackathon Slack channels, and in-person with attendees. Target: founders and early-stage team leads in the room.

**12:00 – 1:30 PM:** Demo rehearsal. Run through the 3-minute script at least three times. Test every transition. Prepare for questions. Have backup talking points for: "How does this scale beyond synthetic data?" and "What's the pricing model?"

**1:30 – 2:30 PM:** Final polish. Freeze code. Prepare demo environment with pre-loaded Brainrot data and fallback states.

---

## Demo script (3 minutes)

**0:00 – 0:30 | The hook.**
"Startups don't die from one thing. They die from a chain reaction nobody saw coming. We built DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities. Seven AI agents. One mission: see the kill chain before it kills you."

**0:30 – 0:45 | Architecture flash.**
Show the 7-agent hierarchy on screen. "Six specialist agents monitor every layer of your company — your team, your money, your infrastructure, your product, your contracts, and your code. One Head Agent connects the dots across all of them."

**0:45 – 1:45 | Live cascade.**
Walk through the primary cascade on the dashboard using Brainrot as the demo company. "Meet Brainrot — a Gen Z social media platform with 340K monthly active users. The People Agent detected that their lead mobile engineer went from strong contributor to unpaid leave in five weeks. The Code Audit Agent confirmed: the feed-service has a bus factor of 1, an unpatched critical CVE in the video processing pipeline, and test coverage is collapsing. The Infra Agent reported the Branded Content SDK is stuck at 31% completion with an April 15 deadline. The Finance Agent connected this to the VibeCheck Media deal — $516K per year, the company's only path to real revenue — and calculated: if this SDK doesn't ship, the deal dies, VibeCheck takes their 200 brand advertisers to competitor Fizz, the company stays pre-revenue burning $80K a month, and the down-round clause triggers in 3.7 months. Here's the cascade chain on screen — every link, every probability, every dollar amount."

**1:45 – 2:15 | What If mode.**
Toggle simulation. "But what if we act? Watch." Drag the "engineer leaves" slider to 100%. The Head Agent recalculates in real-time. New briefing appears. "Now watch what happens when we assign a backup engineer and optimize the video CDN." Adjust the sliders. Cascade probability drops. Risk score drops. Monthly burn decreases by $4,800 from CDN optimization alone. "DEADPOOL doesn't just find the problem — it tells you exactly where to break the chain."

**2:15 – 2:45 | Traction.**
Flash the landing page. Show signup count. "We launched this landing page 20 hours ago. [X] founders have already signed up to get their DEADPOOL score."

**2:45 – 3:00 | Close.**
"Every startup has a DEADPOOL score right now. Most founders don't know theirs. Now they can."

---

## Why this wins

**Innovative use of AI:** Seven-agent hierarchical orchestration with a Head Agent that cross-validates across domains, resolves conflicts between agents, and generates strategic briefings. The Code Audit Agent brings codebase intelligence into business risk analysis — something no existing tool does. The cascade from a single engineer's GitHub activity to a board-control-changing investor clause trigger is the kind of insight that takes a human board advisor weeks to piece together, if they ever do. This isn't six chatbots in a trenchcoat. This is emergent intelligence from structured multi-agent coordination.

**Traction:** Landing page deployed by Day 1 evening. Target: 20+ signups from hackathon attendees and social media. Every signup is a founder who wants their DEADPOOL score.

**Product-market fit:** Every founder in the room has experienced siloed monitoring. Every founder has been blindsided by a chain reaction they could have predicted. The Head Agent's unified briefing is the feature that makes people say "I need this yesterday." The Brainrot demo makes it visceral — everyone in the room either knows a startup that lost a key engineer or has been that key engineer.

**Creative AI use:** The cascade mapper produces insights that no individual agent could generate. The Head Agent's cross-validation creates a system where the whole is demonstrably greater than the sum of its parts. The Code Audit Agent catches what traditional code quality tools miss — business context for technical debt. A bus factor of 1 isn't just a code smell; it's a $516K revenue risk.

**Ship It Ugly:** We're not building a polished SaaS. We're building a working intelligence system that detects real cascades from real data. The cascade chain on stage is the product. Everything else is a wrapper.

---

## Request for Hacks alignment

**RFH #02 — Agents That Hire Agents:** The Head Agent dynamically queries specialist agents based on the situation. In the post-hackathon vision, it could autonomously spin up new specialist agents as the company grows or enters new domains — for example, a "Creator Health Agent" specifically for social platforms like Brainrot that depend on creator networks.

**RFH #04 — Intent as Code:** The dependency graph is a company's operational intent encoded as configuration — "these are the causal relationships that matter to us." Every agent inherits the company's priorities through the graph structure. For Brainrot, the graph encodes that creator retention matters more than raw MAU because the VibeCheck deal depends on a healthy creator network.

**RFH #05 — The Product That Builds Itself:** DEADPOOL's dependency graph improves over time as the Head Agent observes which cascades materialize and which don't. The system learns which cross-domain links are real and which are noise. After six months, DEADPOOL knows that for Brainrot, a 30% commit drop from a feed-service contributor is a high-severity signal, while a 30% drop from an analytics-pipeline contributor is low-severity noise.

**RFH #07 — The One-Person Billion-Dollar Company:** DEADPOOL gives a solo founder the operational awareness of a 50-person leadership team. The Head Agent is their virtual COO — always watching, always connecting, always briefing. For a two-founder team like Brainrot's, where the CEO and CTO are both heads-down on product and fundraising, DEADPOOL catches the signals they're too busy to see.

---

## Success criteria

- All 7 agents running and producing structured output from Brainrot's synthetic data.
- At least one detected cascade spanning 3+ agent domains including the Code Audit Agent.
- Head Agent generating coherent founder briefings with cross-validated evidence that tell the Brainrot story.
- Working "What If" simulation mode demonstrated on stage (show the effect of reassigning an engineer and optimizing video CDN costs).
- 20+ landing page signups.
- The audience understands the cascade chain in under 60 seconds.

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities.*  
*Built at the yconic New England Inter-Collegiate AI Hackathon — March 28-29, 2026.*  
*Track: AI Innovation Hack · Request for Hacks: #02, #04, #05, #07*