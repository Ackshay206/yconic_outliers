# DEADPOOL — Agent Data Specification & Synthetic Data Guide

### Data architecture, agent-to-data mapping, interaction patterns, and synthetic data schemas

---

## 1. Data flow overview

Every agent in DEADPOOL follows the same cycle: **ingest → analyze → emit anomalies**. This document defines exactly what each agent ingests, how agents cross-reference each other's data, and the precise JSON schemas for all synthetic data files.

The demo company is **Brainrot** — a Gen Z social media platform built around short-form video, meme culture, and AI-native content moderation. 340K MAU, 10-person team, $975K total raised, burning $80K/month, pursuing a $516K/year brand partnership deal with VibeCheck Media that depends on a Branded Content SDK shipping by April 15, 2026.

```
Data Sources (JSON files / APIs)
        │
        ▼
┌─────────────────────┐
│   Agent Layer        │
│                      │
│  People ─── Finance  │
│    │  ╲      ╱  │    │
│    │   Cascade  │    │
│    │   Mapper   │    │
│    │  ╱      ╲  │    │
│  Infra ──── Legal    │
│    │          │      │
│  Product ── Market   │
└─────────────────────┘
        │
        ▼
   Signal Bus (anomaly events)
        │
        ▼
   Cascade Mapper (dependency graph traversal)
        │
        ▼
   Founder Dashboard
```

---

## 2. Agent-to-data interaction matrix

| Agent | Primary data | Cross-references | Emits to |
|-------|-------------|-----------------|----------|
| People | `team_activity.json` | Infra (service ownership), Finance (payroll cost) | Signal bus, Cascade mapper |
| Finance | `deadpool_finance_data.csv` + `deadpool_revenue_pipeline.csv` + `deadpool_funding_runway.csv` | Legal (contract terms tied to pipeline deals), People (headcount cost, key-person blocking deals), Product (churn impact on subscription revenue) | Signal bus, Cascade mapper |
| Infra | `infrastructure.json` | People (service owners), Legal (SLA deadlines), Product (error rates) | Signal bus, Cascade mapper |
| Legal | `contracts.json` | Finance (contract values, funding terms), Infra (delivery deadlines), Market (regulatory signals) | Signal bus, Cascade mapper |
| Product | `product_metrics.json` | Infra (service health causing UX issues), Finance (revenue impact of churn), People (support team capacity) | Signal bus, Cascade mapper |
| Market | `market_signals.json` | Finance (pricing pressure impact), Legal (regulatory changes), Product (competitive feature gaps) | Signal bus, Cascade mapper |

---

## 3. Cross-reference linking keys

Agents connect data across domains using shared entity keys. These keys must be consistent across all data files.

| Link key | Used by | Connects |
|----------|---------|----------|
| `developer_name` | People ↔ Infra | Maps a person to the services they own |
| `service_name` | Infra ↔ Legal ↔ Product | Maps a service to its SLA, contract obligations, and user-facing metrics |
| `client_name` | Finance ↔ Legal | Maps revenue concentration to contract terms and renewal risk |
| `feature_name` | Infra ↔ Legal ↔ Product | Maps a deliverable to its deadline, service, and user engagement |
| `competitor_name` | Market ↔ Product ↔ Finance | Maps competitive threats to product gaps and pricing pressure |

**Example cross-reference chain (Brainrot's primary cascade):**

```
People agent finds: "Jaylen Moore" (Engineer 3 - Mobile/Feed) commit drop → on leave
        │
        ▼ (developer_name → service ownership)
Infra agent checks: "feed-service" deploy velocity — stalled
        │
        ▼ (service_name + feature_name → pipeline deal)
Finance agent checks: VibeCheck Media pipeline deal linked to "Branded Content SDK" — at_risk, probability 0.30
        │
        ▼ (pipeline deal lost → runway impact)
Finance agent checks: without VibeCheck revenue, runway = 6.6 months, declining
        │
        ▼ (funding terms → runway threshold)
Finance agent checks: down-round clause triggers at runway < 3 months — ~3.7 months away
```

---

## 4. Synthetic data schemas

### 4.1 People Agent — `team_activity.json`

**Purpose:** Simulate 12 weeks of developer activity for a 12-person team at Brainrot. One developer (the cascade trigger — Jaylen Moore, Mobile/Feed engineer) shows a gradual disengagement pattern that correlates with the feed-service degradation and Branded Content SDK stall.

**File structure:**

```json
{
  "metadata": {
    "company": "Brainrot Inc.",
    "product": "Brainrot — Gen Z social media platform",
    "team_size": 12,
    "data_period": {
      "start": "2026-01-05",
      "end": "2026-03-28",
      "granularity": "weekly",
      "weeks": 12
    }
  },
  "developers": [
    {
      "name": "string — full name, used as linking key",
      "role": "string — job title",
      "department": "string — engineering | product | design | marketing",
      "hire_date": "ISO 8601 date",
      "is_key_person": "boolean — true if single point of failure",
      "owns_services": ["string — service names this person owns"],
      "weekly_data": [
        {
          "week_start": "ISO 8601 date",
          "commits": "integer — number of commits",
          "pull_requests_opened": "integer",
          "pull_requests_reviewed": "integer",
          "lines_added": "integer",
          "lines_deleted": "integer",
          "avg_pr_review_time_hours": "float — average time to review others' PRs",
          "avg_response_time_hours": "float — average time to respond to mentions/requests",
          "active_days": "integer — days with at least 1 commit (0-7)",
          "longest_inactive_streak_days": "integer — max consecutive days with 0 activity"
        }
      ]
    }
  ]
}
```

**Synthetic data generation rules:**

For normal developers (11 of 12):
- Commits: random between 18-40 per week, slight dip on holiday weeks.
- PR reviews: random between 5-15 per week.
- Response time: 1.5-4 hours, stable.
- Active days: 4-6 per week.
- Add natural noise: Designer 1 takes a 1-week vacation for a wedding (commits drop to 0-2, then recover). DevOps engineer has a spike week before the CDN migration push. Marketing has low commit counts (content, not code) — non-cascading noise the agent should correctly ignore.

For the cascade trigger developer (Jaylen Moore — Engineer 3, Mobile/Feed):
- Weeks 1-7: strong, consistent output (commits 28-42, reviews 9-15, response time 1.5-3 hours). Active on feed algorithm tuning, recommendation model experiments, and early Branded Content SDK architecture.
- Weeks 8-9: subtle decline (commits 18-24, reviews 5-8, response time 6-10 hours). Fewer feed algorithm commits. SDK work slows.
- Weeks 10-11: clear decline (commits 5-10, reviews 1-3, response time 24-48 hours). No SDK commits. Feed algorithm untouched.
- Week 12: near-zero (commits 0-3, reviews 0, response time null or 72+ hours). On unpaid leave.
- `is_key_person: true` and `owns_services: ["feed-service", "content-moderation-service"]`.

**Brainrot team roster (consistent across all data files):**

| Name | Role | Key Services |
|------|------|-------------|
| Mika Patel | Founder/CEO | — (ex-TikTok PM) |
| Derek Hwang | Founder/CTO | api-gateway, auth-service |
| Ava Thornton | Engineer 1 - Full Stack | creator-dashboard, api-gateway |
| Zara Okonkwo | Engineer 2 - Backend/Video | video-processing-service |
| Jaylen Moore | Engineer 3 - Mobile/Feed | feed-service, content-moderation-service |
| Nina Castellano | Designer 1 - Product Design | creator-dashboard (design system) |
| Riley Park | PM 1 - Product Manager | — |
| Sasha Volkov | Marketing 1 - Creator Partnerships | — |
| Kai Andersen | Engineer 4 - DevOps/Infra | video-cdn, deployment pipelines |
| Lena Osei | Data 1 - ML/Recommendation | analytics-pipeline, feed-service (model support) |

**Sample entry (cascade trigger — Jaylen Moore, week 12):**

```json
{
  "name": "Jaylen Moore",
  "role": "Engineer 3 - Mobile/Feed",
  "department": "engineering",
  "hire_date": "2025-11-01",
  "is_key_person": true,
  "owns_services": ["feed-service", "content-moderation-service"],
  "weekly_data": [
    {
      "week_start": "2026-03-23",
      "commits": 2,
      "pull_requests_opened": 0,
      "pull_requests_reviewed": 0,
      "lines_added": 45,
      "lines_deleted": 12,
      "avg_pr_review_time_hours": null,
      "avg_response_time_hours": 78.5,
      "active_days": 1,
      "longest_inactive_streak_days": 5
    }
  ]
}
```

---

### 4.2 Finance Agent — Three CSV files

The Finance Agent consumes three CSV files that together cover Brainrot's full financial picture: transaction history, revenue pipeline, and funding/runway model.

#### 4.2a Transaction Ledger — `deadpool_finance_data.csv`

**Purpose:** Complete transaction-level record of every dollar in and out from Brainrot's founding (Sep 2025) through current date (Mar 2026). This is the source of truth for cash position, burn rate, and expense breakdown.

**Columns:** `date, category, subcategory, description, amount, running_balance, notes`

**Key characteristics of the existing data:**
- Funding: $175K pre-seed (Sep 2025, Kevin Tran angel syndicate) + $800K seed (Nov 2025, Velocity Capital led by Jenna Okafor) = $975K total raised
- Team grows from 2 founders to 10 employees (2 founders, 5 engineers including DevOps + ML, 1 designer, 1 PM, 1 creator partnerships/marketing)
- Monthly payroll peaks at ~$79K (10 people), drops to ~$71K in March when Engineer 3 (Jaylen Moore) goes on unpaid leave
- Cloud/video CDN costs escalate from $340/mo to $7,200/mo — driven by 340K MAU video delivery and unoptimized MediaConvert pipeline (DevOps distracted by feed-service outages)
- Content moderation API costs (Anthropic Claude) escalate from $95/mo to $1,400/mo as hateful content reports surge 3x
- Revenue is minimal: $2,400/mo from ~160 Brainrot Pro subscribers at $14.99/mo (ad-free + exclusive filters)
- Final cash balance: ~$535K
- Notes field contains cascade-relevant signals: `*** Commit activity dropped 60%`, `*** ON LEAVE - unpaid. Branded Content SDK stalled. Feed algorithm degrading.`, `*** Burn rate accelerating`

**This file already exists and is the source of truth. Do not regenerate.**

#### 4.2b Revenue Pipeline — `deadpool_revenue_pipeline.csv`

**Purpose:** Track all revenue sources, outstanding invoices, and pipeline deals with their probabilities and feature dependencies. The critical data for the Finance Agent is that the VibeCheck Media enterprise deal ($516K/year) depends on the Branded Content SDK shipping by April 15 — and that feature is stalled because Engineer 3 is on leave and no one else has context on the feed-service architecture.

**Columns:** `record_type, date, client_name, description, amount, status, linked_feature, linked_service, contract_id, payment_terms, days_overdue, probability, notes`

**Record types:**
- `revenue` — Collected Brainrot Pro subscription revenue
- `invoice` — Accounts receivable with payment status and overdue tracking
- `pipeline` — Enterprise/brand deals in progress with close probability and feature dependencies
- `revenue_projection` — Forward-looking scenarios

**Key data points:**
- Brainrot Pro subscriptions: $1,200–$2,400/month, growth decelerating, churn increasing from feed quality degradation and content moderation gaps
- Drip Culture Agency: two invoices totaling $12K overdue (56 and 27 days) — noise anomaly from a branded content pilot dispute, not cascade-critical
- VibeCheck Media pipeline: $516K/year deal, probability degraded from 0.85 → 0.30 as Engineer 3 situation deteriorated. `linked_feature: "Branded Content SDK"`, `linked_service: "feed-service"`. Hard deadline April 15. VibeCheck actively evaluating competitor Fizz. If VibeCheck chooses Fizz, their 200+ brand advertisers validate the competitor, making all future brand deals harder for Brainrot.
- NovaBrands Inc pipeline: $108K/year in-app commerce deal stalled (champion left) — secondary risk
- StudyHive: $22K/year edu-creator deal delayed by COPPA/SOC 2 gaps — minor

**Cascade-critical pipeline entry:**
```csv
pipeline,2026-03-15,VibeCheck Media,Enterprise brand deal - at risk,516000.00,at_risk,Branded Content SDK,feed-service,CTR-DRAFT-052,Prepaid Annual,0,0.30,*** VibeCheck CEO emailed asking for status on SDK. Engineer 3 on leave — sole architect of feed-service and SDK. No one else has context. Deadline April 15. They're talking to Fizz.
```

#### 4.2c Funding Terms & Runway — `deadpool_funding_runway.csv`

**Purpose:** Investor agreement terms (especially the down-round clause), monthly financial summaries, and runway scenario modeling. This is where the Finance Agent detects the final node of the cascade: if VibeCheck deal fails → no revenue inflection → runway erodes → investor clause triggers → Velocity Capital takes board control.

**Columns:** `record_type, date, field, value, detail, threshold, status, notes`

**Record types:**
- `funding_round` — Round details (amount, valuation, instrument type)
- `investor_clause` — Specific clause terms with trigger metrics and consequences
- `monthly_summary` — Aggregated monthly financials (derived from the transaction ledger)
- `runway_scenario` — Projected outcomes under different assumptions

**Key data points:**
- Pre-seed: $175K SAFE at $1.75M cap (Kevin Tran angel syndicate — ex-Snap exec connected to Gen Z creator ecosystem)
- Seed: $800K priced round at $5M post-money (Velocity Capital, led by Jenna Okafor — thesis: Gen Z social platforms with AI-native content moderation)
- Down-round clause: triggers when `runway_months < 3`. Consequence: Velocity Capital converts at 50% discount with 2x liquidation preference and full board seat. Jenna Okafor takes board control. Current status: `monitoring`
- Current runway: 6.6 months (base case, no VibeCheck revenue)
- Best case (VibeCheck closes): runway extends to 15.3 months, validates brand monetization model
- Worst case (VibeCheck lost + creator churn to Fizz): ~3.7 months until down-round trigger

**Cascade-critical clause:**
```csv
investor_clause,2025-11-01,clause_name,Anti-dilution (full ratchet),Velocity Capital seed agreement - Section 5.2,runway_months < 3,safe,Triggers if runway drops below 3 months before Series A close
```

**Cascade-critical scenario:**
```csv
runway_scenario,2026-03-28,months_to_trigger,6.7,Months until runway < 3 (investor clause),3.0,warning,*** ~3.7 months until down-round clause triggers if no revenue inflection
```

---

### 4.3 Infra Agent — `infrastructure.json`

**Purpose:** Simulate service health, deployment pipelines, and system performance for Brainrot's 6 microservices. The feed-service shows degradation correlated with Jaylen Moore's declining activity. Video CDN costs are a standout anomaly — $7,200/month when they should be $2,400/month with proper optimization.

**File structure:**

```json
{
  "metadata": {
    "company": "Brainrot Inc.",
    "total_services": "integer",
    "data_period": {
      "start": "2026-01-05",
      "end": "2026-03-28",
      "granularity": "weekly",
      "weeks": 12
    }
  },
  "services": [
    {
      "name": "string — service name, used as linking key",
      "owner": "string — developer name, links to People agent",
      "tier": "string — critical | standard | internal",
      "dependencies": ["string — other service names this depends on"],
      "weekly_data": [
        {
          "week_start": "ISO 8601 date",
          "deploys": "integer — successful deployments",
          "failed_builds": "integer — CI pipeline failures",
          "build_pass_rate": "float — 0-1",
          "uptime_percent": "float — 0-100",
          "avg_response_ms": "float — average API response time",
          "p99_response_ms": "float — 99th percentile response time",
          "error_rate": "float — 0-1, percentage of requests returning 5xx",
          "open_incidents": "integer — unresolved incidents",
          "cloud_cost_usd": "float — weekly infrastructure cost"
        }
      ],
      "critical_deadline": {
        "feature": "string — feature name, links to Legal agent contracts",
        "due_date": "ISO 8601 date",
        "completion_percent": "float — 0-100",
        "blockers": ["string — descriptions of blocking issues"],
        "estimated_completion": "ISO 8601 date — current projection",
        "days_overdue_projection": "integer — projected days past deadline (0 if on track)"
      }
    }
  ],
  "global_metrics": {
    "total_weekly_cloud_cost": ["float — total across all services per week"],
    "total_open_incidents": ["integer — total across all services per week"],
    "deployment_velocity_trend": "string — increasing | stable | decreasing"
  }
}
```

**Synthetic data generation rules:**

For healthy services (4-5 services — api-gateway, creator-dashboard, notification-service, analytics-pipeline):
- Deploys: 2-6 per week, stable.
- Uptime: 99.90-99.99%, stable.
- Response time: 25-60ms, stable.
- Error rate: 0.001-0.005, stable.
- Cloud cost: stable with minor fluctuations.

For the cascade-affected service (feed-service):
- Weeks 1-7: healthy (deploys 3-6, uptime 99.9%+, response 40-55ms). Jaylen actively deploying feed algorithm improvements.
- Weeks 8-9: subtle degradation (deploys drop to 1-2, uptime 99.7-99.9%, response 65-95ms). Recommendation quality declining.
- Weeks 10-11: visible degradation (deploys 0-1, uptime 99.1-99.5%, response 130-200ms, error rate climbing). Content moderation latency increasing.
- Week 12: critical (deploys 0, uptime 98.2%, response 280ms, error rate 0.05+). Feed serving stale content. Branded Content SDK features broken.
- `critical_deadline.completion_percent: 31` with `due_date` in 18 days and `estimated_completion` projecting 50+ days.

For the video-processing-service (secondary concern):
- Cloud costs climbing: video CDN at $7,200/month, should be ~$2,400 with MediaConvert optimization. DevOps (Kai Andersen) is aware but pulled to fight feed-service outages.

**Service dependency map (include in synthetic data):**

```json
{
  "services": [
    {"name": "api-gateway", "owner": "Derek Hwang", "tier": "critical", "dependencies": ["auth-service", "feed-service", "creator-dashboard"]},
    {"name": "auth-service", "owner": "Derek Hwang", "tier": "critical", "dependencies": []},
    {"name": "feed-service", "owner": "Jaylen Moore", "tier": "critical", "dependencies": ["content-moderation-service", "video-processing-service"]},
    {"name": "content-moderation-service", "owner": "Jaylen Moore", "tier": "critical", "dependencies": ["feed-service"]},
    {"name": "creator-dashboard", "owner": "Ava Thornton", "tier": "standard", "dependencies": ["api-gateway", "analytics-pipeline"]},
    {"name": "video-processing-service", "owner": "Zara Okonkwo", "tier": "critical", "dependencies": []},
    {"name": "notification-service", "owner": "Ava Thornton", "tier": "standard", "dependencies": ["api-gateway"]},
    {"name": "analytics-pipeline", "owner": "Lena Osei", "tier": "internal", "dependencies": []}
  ]
}
```

Note the circular dependency: `feed-service` depends on `content-moderation-service` (to filter content before serving), and `content-moderation-service` depends on `feed-service` (to access content metadata for moderation decisions). Both are owned by Jaylen Moore. This means any change to either service risks breaking the other — a critical architectural debt.

---

### 4.4 Legal Agent — `contracts.json`

**Purpose:** Simulate Brainrot's active contracts, investor agreements, and compliance obligations. Key contracts have clauses that create hard deadlines linked to infrastructure deliverables. COPPA compliance is particularly relevant given Brainrot's Gen Z audience includes users under 18.

**File structure:**

```json
{
  "metadata": {
    "company": "Brainrot Inc.",
    "total_active_contracts": "integer",
    "total_value_at_risk": "float"
  },
  "client_contracts": [
    {
      "id": "string — unique contract ID",
      "client": "string — client name, links to Finance agent",
      "type": "string — Brand Partnership Agreement | Annual Subscription | Pilot Agreement",
      "signed_date": "ISO 8601 date",
      "renewal_date": "ISO 8601 date",
      "auto_renew": "boolean",
      "annual_value": "float",
      "payment_terms": "string — Net 30 | Net 60 | Prepaid Annual",
      "clauses": [
        {
          "section": "string — clause reference (e.g. Section 4.2)",
          "title": "string — clause title",
          "summary": "string — plain language summary",
          "deadline": "ISO 8601 date | null",
          "linked_service": "string | null — service name, links to Infra agent",
          "linked_feature": "string | null — feature name",
          "breach_consequence": "string — what happens if breached",
          "financial_impact": "float — dollar value at risk",
          "status": "string — compliant | monitoring | at_risk | breached"
        }
      ]
    }
  ],
  "investor_agreements": [
    {
      "id": "string — unique agreement ID",
      "investor": "string",
      "type": "string — SAFE | Convertible Note | Priced Round",
      "date": "ISO 8601 date",
      "amount": "float",
      "clauses": [
        {
          "section": "string",
          "title": "string",
          "summary": "string",
          "trigger_condition": "string — machine-readable condition",
          "trigger_metric": "string — which metric to watch (e.g. runway_months)",
          "trigger_threshold": "float — value that activates the clause",
          "consequence": "string",
          "status": "string — safe | monitoring | approaching | triggered"
        }
      ]
    }
  ],
  "compliance_obligations": [
    {
      "regulation": "string — e.g. COPPA, GDPR, SOC 2",
      "applicable_services": ["string — service names"],
      "current_status": "string — compliant | audit_due | non_compliant",
      "next_audit_date": "ISO 8601 date",
      "risk_level": "string — low | medium | high"
    }
  ]
}
```

**Synthetic data generation rules:**

- Include 3-4 client contracts. VibeCheck Media has the Branded Content SDK delivery clause. Drip Culture Agency has a branded content pilot with a deliverable dispute. StudyHive has an edu-creator pilot delayed by compliance gaps. One smaller contract is clean (noise).
- The investor agreement has the down-round clause with `trigger_metric: "runway_months"` and `trigger_threshold: 3`. Consequence explicitly names Jenna Okafor taking board control.
- Include a COPPA compliance obligation linked to the content-moderation-service and user data handling — critical for a Gen Z platform serving users under 18. If content-moderation-service is degraded (because Jaylen Moore is the sole owner and he's on leave), COPPA compliance is also at risk.
- Include a GDPR obligation linked to the feed-service (recommendation algorithm data collection practices).
- At least one contract should be in `compliant` status to show the agent correctly ignores non-issues.

**Cascade-critical contracts:**

```json
{
  "pipeline_contracts": [
    {
      "id": "CTR-DRAFT-052",
      "client": "VibeCheck Media",
      "status": "in_procurement",
      "annual_value": 516000,
      "clauses": [
        {
          "section": "Section 4.2",
          "title": "SDK delivery prerequisite",
          "summary": "Contract execution contingent on Branded Content SDK deployed to production by April 15, 2026. SDK must enable native branded content creation within Brainrot's feed. If not delivered, VibeCheck walks.",
          "deadline": "2026-04-15",
          "linked_service": "feed-service",
          "linked_feature": "Branded Content SDK",
          "failure_consequence": "Deal collapses. $516,000/year brand revenue never materializes. VibeCheck takes 200+ brand advertisers to competitor Fizz, validating the competitor. Company remains pre-revenue.",
          "financial_impact": 516000,
          "status": "at_risk"
        }
      ]
    }
  ],
  "active_contracts": [
    {
      "id": "CTR-2025-071",
      "client": "Drip Culture Agency",
      "status": "dispute",
      "annual_value": 72000,
      "clauses": [
        {
          "section": "Section 2.1",
          "title": "Campaign metrics deliverable",
          "summary": "Agency claims branded content campaign analytics integration deliverable incomplete. Withholding payment.",
          "deadline": null,
          "linked_service": "analytics-pipeline",
          "linked_feature": "Campaign Analytics Dashboard",
          "breach_consequence": "$12,000 in receivables at risk",
          "financial_impact": 12000,
          "status": "monitoring"
        }
      ]
    }
  ]
}
```

---

### 4.5 Product Agent — `product_metrics.json`

**Purpose:** Simulate user engagement, feature adoption, creator health, support ticket trends, and churn signals for Brainrot. Degradation in the feed experience correlates with the infra issues. Creator exodus to competitor Fizz is the product-level manifestation of the cascade.

**File structure:**

```json
{
  "metadata": {
    "company": "Brainrot Inc.",
    "product": "Brainrot — Gen Z Social Media Platform",
    "data_period": {
      "start": "2026-01-05",
      "end": "2026-03-28",
      "granularity": "weekly",
      "weeks": 12
    }
  },
  "global_metrics": {
    "weekly_data": [
      {
        "week_start": "ISO 8601 date",
        "monthly_active_users": "integer",
        "weekly_active_users": "integer",
        "daily_active_users_avg": "integer",
        "new_signups": "integer",
        "churn_count": "integer",
        "churn_rate": "float — 0-1",
        "creator_accounts_active": "integer",
        "creator_deactivations": "integer",
        "nps_score": "integer — -100 to 100",
        "csat_score": "float — 0-5",
        "videos_uploaded": "integer",
        "avg_session_duration_sec": "float"
      }
    ]
  },
  "feature_metrics": [
    {
      "feature_name": "string — feature name, links to Infra + Legal",
      "linked_service": "string — service name",
      "weekly_data": [
        {
          "week_start": "ISO 8601 date",
          "sessions": "integer — feature usage sessions",
          "unique_users": "integer",
          "avg_session_duration_sec": "float",
          "completion_rate": "float — 0-1, task completion within the feature",
          "error_rate_user_facing": "float — 0-1, percentage of sessions with errors",
          "rage_clicks": "integer — rapid repeated clicks indicating frustration",
          "drop_off_rate": "float — 0-1, users who start but abandon the feature"
        }
      ]
    }
  ],
  "support_tickets": {
    "weekly_data": [
      {
        "week_start": "ISO 8601 date",
        "total_tickets": "integer",
        "by_category": {
          "category_name": "integer"
        },
        "avg_resolution_hours": "float",
        "escalation_count": "integer",
        "sentiment_score": "float — 0-1 where 1 is positive",
        "repeat_contact_rate": "float — 0-1, percentage of tickets from repeat reporters"
      }
    ]
  },
  "cohort_retention": {
    "description": "Monthly cohort retention rates",
    "cohorts": [
      {
        "cohort_month": "YYYY-MM",
        "month_1_retention": "float",
        "month_2_retention": "float",
        "month_3_retention": "float"
      }
    ]
  }
}
```

**Synthetic data generation rules:**

Global metrics should show a product with strong early traction and a deterioration starting week 8 when the feed algorithm stops being maintained:
- MAU: growing to 340K through week 7, then growth stalling and declining 2-4% per week.
- WAU: stable at 85K-95K weeks 1-7, then declining 3-5% per week.
- Creator accounts: growing through week 7 (~2,400 active), then deactivations spike 3x from week 8 onward as top creators notice feed quality decline and start posting about Fizz.
- NPS: 38-44 weeks 1-7, then dropping to single digits / negative by week 12.
- Videos uploaded: growing through week 7, then declining as creators disengage.
- Churn rate: 1.8-2.5% weeks 1-7, then climbing to 9-11% by week 12.

Feature metrics should show the feed as the source of the product decline:
- Feed ("For You" page) session duration decline sharply from week 8. Error rate climbs from 0.3% to 14%+ (mirrors infra degradation). Recommendation quality drop means users see stale/irrelevant content.
- Branded Content beta: usage cratering as the SDK stalls — brands enrolled in the beta can't create new campaigns.
- Other features (creator onboarding, direct messaging, profile/settings) stay stable — the problem is isolated to the feed and content served through it.

Support tickets should spike in "feed quality" and "content moderation" categories from week 8 onward:
- "Feed quality" — users complaining about seeing the same content, irrelevant recommendations, stale memes.
- "Content moderation" — hateful content, harassment, and spam getting through because moderation service is degraded.
- "Creator account issues" — creators unable to access branded content tools, analytics not updating.
- Declining sentiment scores as creator community grows frustrated.

---

### 4.6 Market Agent — `market_signals.json`

**Purpose:** Simulate competitive intelligence, industry trends, and external threats. Fizz — a direct competitor — is making aggressive moves that add time pressure to the cascade. If VibeCheck chooses Fizz over Brainrot, it validates the competitor across the entire brand advertising ecosystem.

**File structure:**

```json
{
  "metadata": {
    "company": "Brainrot Inc.",
    "industry": "Gen Z Social Media / Creator Economy",
    "data_period": {
      "start": "2026-01-01",
      "end": "2026-03-28"
    }
  },
  "competitors": [
    {
      "name": "string — competitor name",
      "relationship": "string — direct | adjacent | emerging",
      "estimated_arr": "float | null",
      "last_funding": {
        "round": "string",
        "amount": "float",
        "date": "ISO 8601 date",
        "lead_investor": "string"
      },
      "signals": [
        {
          "date": "ISO 8601 date",
          "type": "string — funding_round | product_launch | hiring_signal | pricing_change | partnership | acquisition | creator_poach",
          "headline": "string — brief description",
          "details": "string — full context",
          "relevance_to_us": "string — how this impacts Brainrot",
          "affected_domains": ["string — finance | product | legal | people"],
          "urgency": "string — low | medium | high | critical"
        }
      ]
    }
  ],
  "industry_trends": [
    {
      "trend": "string — trend name",
      "direction": "string — growing | stable | declining",
      "impact_on_us": "string — positive | neutral | negative",
      "details": "string",
      "source": "string — where this was observed"
    }
  ],
  "regulatory_signals": [
    {
      "date": "ISO 8601 date",
      "regulation": "string",
      "jurisdiction": "string",
      "summary": "string",
      "affected_services": ["string — service names"],
      "compliance_deadline": "ISO 8601 date | null",
      "status": "string — proposed | enacted | enforced"
    }
  ]
}
```

**Synthetic data generation rules:**

- Create one direct competitor (Fizz) with an aggressive recent trajectory: Series A funding ($12M from a16z), launched a competing branded content platform, poaching Brainrot's top creators, and actively courting VibeCheck Media as a partner.
- Create one adjacent competitor (noise) — e.g., Locket (photo-sharing, different audience segment) with minor signals that don't cascade.
- Include regulatory signals: updated COPPA enforcement guidance specifically targeting Gen Z platforms with algorithmic recommendation and user-generated content. FTC signaling increased scrutiny on platforms where under-18 users interact with branded content — directly relevant to the Branded Content SDK.
- Fizz's signals should have `urgency: "high"` or `"critical"` and `affected_domains` that include finance and product — adding external pressure to the cascade timeline. The key Fizz signal: they're in conversations with VibeCheck Media as an alternative to Brainrot.

---

## 5. Anomaly event schema (output from all agents)

Every agent emits anomalies in this standardized format to the signal bus.

```json
{
  "id": "string — UUID",
  "agent_source": "string — people | finance | infra | product | legal | market",
  "anomaly_type": "string — categorized anomaly name",
  "severity": "float — 0.0 to 1.0",
  "confidence": "float — 0.0 to 1.0, how certain the agent is",
  "entity_affected": "string — primary entity (person, service, client, etc.)",
  "entity_type": "string — developer | service | client | contract | competitor | regulation",
  "description": "string — human-readable explanation",
  "evidence": {
    "metric": "string — which metric triggered this",
    "current_value": "float | string",
    "baseline_value": "float | string",
    "deviation_percent": "float",
    "trend_direction": "string — declining | increasing | volatile",
    "weeks_trending": "integer"
  },
  "linked_entities": [
    {
      "entity": "string — name of related entity",
      "entity_type": "string",
      "relationship": "string — owns | depends_on | contracted_to | competes_with"
    }
  ],
  "cascade_potential": {
    "downstream_domains": ["string — which other agent domains could be affected"],
    "estimated_impact": "string — low | medium | high | critical",
    "time_horizon_days": "integer — how quickly this could cascade"
  },
  "timestamp": "ISO 8601 datetime",
  "data_snapshot": "object — raw data that triggered the anomaly (for audit trail)"
}
```

**Example anomaly (People agent detecting Jaylen Moore's disengagement):**

```json
{
  "id": "anom-2026-0328-001",
  "agent_source": "people",
  "anomaly_type": "key_person_disengagement",
  "severity": 0.85,
  "confidence": 0.91,
  "entity_affected": "Jaylen Moore",
  "entity_type": "developer",
  "description": "Mobile/Feed Engineer commit activity declined 94% over 5 weeks. PR reviews dropped to zero. Response time exceeded 72 hours. Sole owner of feed-service and content-moderation-service — both critical to Brainrot's core experience and the Branded Content SDK.",
  "evidence": {
    "metric": "weekly_commits",
    "current_value": 2,
    "baseline_value": 35,
    "deviation_percent": -94.3,
    "trend_direction": "declining",
    "weeks_trending": 5
  },
  "linked_entities": [
    {"entity": "feed-service", "entity_type": "service", "relationship": "owns"},
    {"entity": "content-moderation-service", "entity_type": "service", "relationship": "owns"}
  ],
  "cascade_potential": {
    "downstream_domains": ["infra", "legal", "finance", "product"],
    "estimated_impact": "critical",
    "time_horizon_days": 18
  },
  "timestamp": "2026-03-28T10:30:00Z",
  "data_snapshot": {
    "week_12_commits": 2,
    "week_11_commits": 8,
    "week_10_commits": 15,
    "baseline_avg_commits": 35
  }
}
```

---

## 6. Cascade chain schema (output from cascade mapper)

```json
{
  "id": "string — UUID",
  "name": "string — human-readable cascade name",
  "trigger_anomaly_id": "string — the anomaly that started the chain",
  "status": "string — active | resolved | monitoring",
  "detected_at": "ISO 8601 datetime",
  "last_updated": "ISO 8601 datetime",
  "chain": [
    {
      "step": "integer — position in chain (1-based)",
      "node_id": "string",
      "domain": "string — which agent domain",
      "entity": "string — affected entity name",
      "event": "string — what happens at this step",
      "probability": "float — cumulative probability at this step",
      "conditional_probability": "float — P(this step | previous step)",
      "evidence_from_agent": "string — what the agent found",
      "time_horizon_days": "integer — estimated days until this step materializes",
      "status": "string — occurred | likely | possible | unlikely"
    }
  ],
  "end_state": {
    "description": "string — final outcome if cascade completes",
    "severity": "string — low | medium | high | catastrophic",
    "financial_impact": "float — estimated dollar impact",
    "reversible": "boolean"
  },
  "overall_probability": "float — product of all conditional probabilities",
  "company_risk_contribution": "float — 0-1, how much this chain contributes to overall risk score",
  "recommended_interventions": [
    {
      "step_to_break": "integer — which chain link to target",
      "action": "string — what the founder should do",
      "urgency": "string — immediate | this_week | this_month",
      "effort": "string — low | medium | high",
      "expected_risk_reduction": "float — 0-1"
    }
  ]
}
```

**Example cascade chain (Brainrot's primary demo cascade):**

```json
{
  "id": "cascade-2026-0328-001",
  "name": "Jaylen Moore disengagement → VibeCheck deal breach → runway crisis",
  "trigger_anomaly_id": "anom-2026-0328-001",
  "status": "active",
  "detected_at": "2026-03-28T10:35:00Z",
  "last_updated": "2026-03-28T10:35:00Z",
  "chain": [
    {
      "step": 1,
      "node_id": "key_person_disengage",
      "domain": "people",
      "entity": "Jaylen Moore",
      "event": "Mobile/Feed engineer activity dropped 94% over 5 weeks. On unpaid leave.",
      "probability": 0.91,
      "conditional_probability": 0.91,
      "evidence_from_agent": "2 commits in week 12 vs 35 baseline. Zero PR reviews. 78-hour response time. Sole owner of feed-service and content-moderation-service.",
      "time_horizon_days": 0,
      "status": "occurred"
    },
    {
      "step": 2,
      "node_id": "critical_deploy_missed",
      "domain": "infra",
      "entity": "feed-service",
      "event": "Branded Content SDK delivery deadline will be missed by 35+ days",
      "probability": 0.66,
      "conditional_probability": 0.72,
      "evidence_from_agent": "SDK at 31% completion. Zero deploys in 2 weeks. Circular dependency with content-moderation-service. No other engineer has feed-service context. Video CDN costs at $7,200/mo (should be $2,400).",
      "time_horizon_days": 18,
      "status": "likely"
    },
    {
      "step": 3,
      "node_id": "client_contract_breach",
      "domain": "legal",
      "entity": "VibeCheck Media — CTR-DRAFT-052",
      "event": "Section 4.2 breached — VibeCheck walks, takes 200+ brand advertisers to Fizz",
      "probability": 0.38,
      "conditional_probability": 0.58,
      "evidence_from_agent": "Contract requires Branded Content SDK by April 15. Current projection: May 30+. VibeCheck CEO actively evaluating Fizz. If Fizz wins VibeCheck, the entire brand advertiser ecosystem validates the competitor.",
      "time_horizon_days": 18,
      "status": "possible"
    },
    {
      "step": 4,
      "node_id": "revenue_cliff",
      "domain": "finance",
      "entity": "VibeCheck Media revenue",
      "event": "Only revenue path collapses. $516K/year never materializes. Brand monetization thesis invalidated.",
      "probability": 0.25,
      "conditional_probability": 0.65,
      "evidence_from_agent": "VibeCheck = only viable path to meaningful revenue. Without it: $2,400/mo subscriptions declining due to feed degradation. NovaBrands deal dead (champion left). StudyHive delayed by COPPA. No other pipeline.",
      "time_horizon_days": 48,
      "status": "possible"
    },
    {
      "step": 5,
      "node_id": "runway_crisis",
      "domain": "finance",
      "entity": "Brainrot runway",
      "event": "Runway drops below 3 months, triggering Velocity Capital down-round clause",
      "probability": 0.19,
      "conditional_probability": 0.75,
      "evidence_from_agent": "Current cash: $535K. Net burn: $78K/month (declining revenue, climbing CDN costs). Without VibeCheck: runway ~6.6 months. After creator exodus to Fizz accelerates churn: ~3.7 months to clause trigger.",
      "time_horizon_days": 112,
      "status": "possible"
    }
  ],
  "end_state": {
    "description": "Down-round clause triggered. Velocity Capital converts at 50% discount with 2x liquidation preference. Jenna Okafor takes full board seat — founder diluted below control threshold. Brand advertisers validated Fizz. Creator network collapsed. Company effectively lost.",
    "severity": "catastrophic",
    "financial_impact": 2016000,
    "reversible": false
  },
  "overall_probability": 0.19,
  "company_risk_contribution": 0.74,
  "recommended_interventions": [
    {
      "step_to_break": 1,
      "action": "Immediate 1:1 with Jaylen Moore. Identify root cause of disengagement. Offer retention package or begin knowledge transfer for feed-service and Branded Content SDK.",
      "urgency": "immediate",
      "effort": "low",
      "expected_risk_reduction": 0.65
    },
    {
      "step_to_break": 2,
      "action": "Assign Lena Osei (ML/Recommendation) as backup on feed-service. Begin pair programming sessions for context transfer. Have Kai Andersen (DevOps) prioritize video CDN cost optimization ($4,800/month savings).",
      "urgency": "immediate",
      "effort": "medium",
      "expected_risk_reduction": 0.45
    },
    {
      "step_to_break": 3,
      "action": "Proactively contact VibeCheck Media CEO. Negotiate deadline extension to May 15. Offer interim demo of Branded Content SDK at current 31% completion. Emphasize Brainrot's creator network advantage over Fizz.",
      "urgency": "this_week",
      "effort": "medium",
      "expected_risk_reduction": 0.35
    }
  ]
}
```

---

## 7. File manifest

Place all data files in `/data/` in the project repo. Finance Agent files are CSV; other agents use JSON.

| File | Agent | Format | Size (approx) | Description |
|------|-------|--------|---------------|-------------|
| `deadpool_finance_data.csv` | Finance | CSV | ~14 KB | Transaction ledger: Sep 2025–Mar 2026, every income/expense with running balance for Brainrot |
| `deadpool_revenue_pipeline.csv` | Finance | CSV | ~4 KB | Brainrot Pro subscriptions, Drip Culture overdue invoices, VibeCheck/NovaBrands/StudyHive pipeline deals |
| `deadpool_funding_runway.csv` | Finance | CSV | ~6 KB | Velocity Capital terms, down-round clause, monthly summaries, runway scenarios |
| `team_activity.json` | People | JSON | ~12 KB | 10 team members × 12 weeks of activity (Jaylen Moore cascade trigger) |
| `infrastructure.json` | Infra | JSON | ~12 KB | 6-8 services × 12 weeks of health metrics (feed-service + video CDN degradation) |
| `contracts.json` | Legal | JSON | ~8 KB | VibeCheck deal terms + Drip Culture dispute + investor agreement + COPPA/GDPR compliance |
| `product_metrics.json` | Product | JSON | ~10 KB | MAU/WAU, creator health, feed engagement, support tickets, NPS, churn |
| `market_signals.json` | Market | JSON | ~6 KB | Fizz competitor intelligence + COPPA regulatory signals |
| `codebase_audit.json` | Code Audit | JSON | ~8 KB | Code ownership, ffmpeg-wasm CVE, test coverage, bus factor, circular dependency |
| `dependency_graph.json` | Cascade Mapper | JSON | ~4 KB | Pre-built node-edge graph with baseline probabilities |

**Total dataset: ~84 KB** — small enough to load entirely in memory, rich enough to power a compelling demo with the Brainrot narrative.

---

## 8. Data generation checklist

Before demo day, verify:

- [ ] All linking keys are consistent across files (`"Jaylen Moore"` / `"feed-service"` / `"VibeCheck Media"` / `"Branded Content SDK"` spelled identically everywhere)
- [ ] Timeline alignment: all files cover the same period (Sep 2025 – Mar 2026 for finance, weeks 1-12 of 2026 for others)
- [ ] Jaylen Moore's disengagement timeline in People data correlates with feed-service degradation in Infra data
- [ ] The VibeCheck Media pipeline deal in `deadpool_revenue_pipeline.csv` references `linked_feature: "Branded Content SDK"` and `linked_service: "feed-service"`
- [ ] The funding terms in `deadpool_funding_runway.csv` show down-round trigger at `runway_months < 3` with correct consequence text (Jenna Okafor takes board control)
- [ ] Monthly summaries in `deadpool_funding_runway.csv` are consistent with the transaction ledger totals in `deadpool_finance_data.csv`
- [ ] Runway scenarios correctly show: base case ~6.6 months, best case (VibeCheck closes) ~15.3 months, worst case ~3.7 months to trigger
- [ ] At least 2-3 non-cascading anomalies exist as noise (Drip Culture overdue invoices, NovaBrands stalled deal, StudyHive COPPA delay, video CDN cost overspend)
- [ ] No data file references an entity that doesn't exist in another file
- [ ] Anomaly severity scores are calibrated: cascade-relevant anomalies are 0.7+ severity, noise anomalies are 0.3-0.5
- [ ] Brainrot team roster (10 names) is consistent: Mika Patel, Derek Hwang, Ava Thornton, Zara Okonkwo, Jaylen Moore, Nina Castellano, Riley Park, Sasha Volkov, Kai Andersen, Lena Osei
- [ ] Competitor name "Fizz" is consistent across market_signals.json, revenue pipeline notes, and contracts.json

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities*  
*Data specification v1.0 — March 28, 2026*  
*Demo company: Brainrot Inc. — Gen Z social media platform*