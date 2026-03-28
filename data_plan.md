# DEADPOOL — Agent Data Specification & Synthetic Data Guide

### Data architecture, agent-to-data mapping, interaction patterns, and synthetic data schemas

---

## 1. Data flow overview

Every agent in DEADPOOL follows the same cycle: **ingest → analyze → emit anomalies**. This document defines exactly what each agent ingests, how agents cross-reference each other's data, and the precise JSON schemas for all synthetic data files.

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

**Example cross-reference chain:**

```
People agent finds: "Engineer 3 (Mobile)" commit drop → on leave
        │
        ▼ (developer_name → service ownership)
Infra agent checks: "payments-service" deploy velocity — stalled
        │
        ▼ (service_name + feature_name → pipeline deal)
Finance agent checks: Nexus Corp pipeline deal linked to "Payments API v2" — at_risk, probability 0.35
        │
        ▼ (pipeline deal lost → runway impact)
Finance agent checks: without Nexus revenue, runway = 6.7 months, declining
        │
        ▼ (funding terms → runway threshold)
Finance agent checks: down-round clause triggers at runway < 3 months — ~3.6 months away
```

---

## 4. Synthetic data schemas

### 4.1 People Agent — `team_activity.json`

**Purpose:** Simulate 12 weeks of developer activity for a 12-person engineering team. One developer (the cascade trigger) shows a gradual disengagement pattern.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
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
      "department": "string — engineering | product | design",
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
- Add natural noise: one developer takes a 1-week vacation (commits drop to 0-2, then recover). Another has a spike week before a launch. These are non-cascading anomalies the agent should correctly ignore.

For the cascade trigger developer:
- Weeks 1-7: strong, consistent output (commits 28-42, reviews 9-15, response time 1.5-3 hours).
- Weeks 8-9: subtle decline (commits 18-24, reviews 5-8, response time 6-10 hours).
- Weeks 10-11: clear decline (commits 5-10, reviews 1-3, response time 24-48 hours).
- Week 12: near-zero (commits 0-3, reviews 0, response time null or 72+ hours).
- `is_key_person: true` and `owns_services: ["payments-service", "auth-service"]`.

**Sample entry (cascade trigger — week 12):**

```json
{
  "name": "Sarah Chen",
  "role": "Lead Backend Engineer",
  "department": "engineering",
  "hire_date": "2024-03-15",
  "is_key_person": true,
  "owns_services": ["payments-service", "auth-service"],
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

The Finance Agent consumes three CSV files that together cover the full financial picture: transaction history, revenue pipeline, and funding/runway model.

#### 4.2a Transaction Ledger — `deadpool_finance_data.csv`

**Purpose:** Complete transaction-level record of every dollar in and out from company founding (Sep 2025) through current date (Mar 2026). This is the source of truth for cash position, burn rate, and expense breakdown.

**Columns:** `date, category, subcategory, description, amount, running_balance, notes`

**Key characteristics of the existing data:**
- Funding: $150K pre-seed (Sep 2025) + $750K seed (Nov 2025) = $900K total raised
- Team grows from 2 founders to 10 employees (2 founders, 5 engineers, 1 designer, 1 PM, 1 marketing, 1 DevOps, 1 data analyst)
- Monthly payroll peaks at ~$72K (10 people), drops to ~$65K in March when Engineer 3 goes on unpaid leave
- Cloud costs escalate from $210/mo to $5,200/mo (unoptimized — DevOps distracted)
- Revenue is minimal: only $1,200/mo from ~80 SMB subscribers at $15/mo
- Final cash balance: ~$493K
- Notes field contains cascade-relevant signals: `*** Commit activity dropped 60%`, `*** ON LEAVE - unpaid. DM feature stalled.`, `*** Burn rate accelerating`

**This file already exists and is the source of truth. Do not regenerate.**

#### 4.2b Revenue Pipeline — `deadpool_revenue_pipeline.csv`

**Purpose:** Track all revenue sources, outstanding invoices, and pipeline deals with their probabilities and feature dependencies. The critical data for the Finance Agent is that the Nexus Corp enterprise deal ($423K/year) depends on Payments API v2 shipping by April 15 — and that feature is stalled because Engineer 3 is on leave.

**Columns:** `record_type, date, client_name, description, amount, status, linked_feature, linked_service, contract_id, payment_terms, days_overdue, probability, notes`

**Record types:**
- `revenue` — Collected subscription revenue (SMB self-serve)
- `invoice` — Accounts receivable with payment status and overdue tracking
- `pipeline` — Enterprise deals in progress with close probability and feature dependencies
- `revenue_projection` — Forward-looking scenarios

**Key data points:**
- SMB subscriptions: $840–$1,200/month, growth stalling, churn increasing from payments errors
- Greenleaf Consulting: two invoices totaling $9K overdue (56 and 27 days) — noise anomaly, not cascade-critical
- Nexus Corp pipeline: $423K/year deal, probability degraded from 0.85 → 0.35 as Engineer 3 situation deteriorated. `linked_feature: "Payments API v2"`, `linked_service: "payments-service"`. Hard deadline April 15.
- Patel Industries pipeline: $96K/year deal stalled (champion left) — secondary risk
- BrightPath Education: $18K/year deal delayed by SOC 2 gap — minor

**Cascade-critical pipeline entry:**
```csv
pipeline,2026-03-15,Nexus Corp,Enterprise contract - at risk,423360.00,at_risk,Payments API v2,payments-service,CTR-DRAFT-047,Prepaid Annual,0,0.35,*** Nexus Corp CFO emailed asking for status update on API v2. Engineer 3 on leave. No one else has context. Deadline April 15.
```

#### 4.2c Funding Terms & Runway — `deadpool_funding_runway.csv`

**Purpose:** Investor agreement terms (especially the down-round clause), monthly financial summaries, and runway scenario modeling. This is where the Finance Agent detects the final node of the cascade: if Nexus deal fails → no revenue inflection → runway erodes → investor clause triggers.

**Columns:** `record_type, date, field, value, detail, threshold, status, notes`

**Record types:**
- `funding_round` — Round details (amount, valuation, instrument type)
- `investor_clause` — Specific clause terms with trigger metrics and consequences
- `monthly_summary` — Aggregated monthly financials (derived from the transaction ledger)
- `runway_scenario` — Projected outcomes under different assumptions

**Key data points:**
- Pre-seed: $150K SAFE at $1.5M cap (David Park angel syndicate)
- Seed: $750K priced round at $4.75M post-money (Horizon Ventures, Maria Santos)
- Down-round clause: triggers when `runway_months < 3`. Consequence: investor converts at 50% discount with 2x liquidation preference and full board seat. Current status: `monitoring`
- Current runway: 6.7 months (base case, no Nexus revenue)
- Best case (Nexus closes): runway extends to 13.2 months
- Worst case (Nexus lost + churn accelerates): ~3.6 months until down-round trigger

**Cascade-critical clause:**
```csv
investor_clause,2025-11-01,clause_name,Anti-dilution (full ratchet),Horizon Ventures seed agreement - Section 5.2,runway_months < 3,monitoring,Triggers if runway drops below 3 months before Series A close
```

**Cascade-critical scenario:**
```csv
runway_scenario,2026-03-28,months_to_trigger,6.6,Months until runway < 3 (investor clause),3.0,warning,*** ~3.6 months until down-round clause triggers if no revenue inflection
```

---

### 4.3 Infra Agent — `infrastructure.json`

**Purpose:** Simulate service health, deployment pipelines, and system performance for 5-6 microservices. The payments service shows degradation correlated with the lead engineer's declining activity.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
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

For healthy services (4-5 services):
- Deploys: 2-6 per week, stable.
- Uptime: 99.90-99.99%, stable.
- Response time: 25-60ms, stable.
- Error rate: 0.001-0.005, stable.
- Cloud cost: stable with minor fluctuations.

For the cascade-affected service (payments-service):
- Weeks 1-7: healthy (deploys 3-6, uptime 99.9%+, response 40-55ms).
- Weeks 8-9: subtle degradation (deploys drop to 1-2, uptime 99.7-99.9%, response 65-95ms).
- Weeks 10-11: visible degradation (deploys 0-1, uptime 99.1-99.5%, response 130-200ms, error rate climbing).
- Week 12: critical (deploys 0, uptime 98.2%, response 245ms, error rate 0.04+).
- `critical_deadline.completion_percent: 34` with `due_date` in 18 days and `estimated_completion` projecting 45+ days.

**Service dependency map (include in synthetic data):**

```json
{
  "services": [
    {"name": "api-gateway", "owner": "Marcus Johnson", "tier": "critical", "dependencies": ["auth-service", "payments-service", "dashboard-ui"]},
    {"name": "auth-service", "owner": "Sarah Chen", "tier": "critical", "dependencies": []},
    {"name": "payments-service", "owner": "Sarah Chen", "tier": "critical", "dependencies": ["auth-service"]},
    {"name": "dashboard-ui", "owner": "Marcus Johnson", "tier": "standard", "dependencies": ["api-gateway"]},
    {"name": "notification-service", "owner": "Priya Sharma", "tier": "standard", "dependencies": ["api-gateway"]},
    {"name": "analytics-pipeline", "owner": "Jake Torres", "tier": "internal", "dependencies": []}
  ]
}
```

---

### 4.4 Legal Agent — `contracts.json`

**Purpose:** Simulate the company's active contracts, investor agreements, and compliance obligations. Key contracts have clauses that create hard deadlines linked to infrastructure deliverables.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
    "total_active_contracts": "integer",
    "total_value_at_risk": "float"
  },
  "client_contracts": [
    {
      "id": "string — unique contract ID",
      "client": "string — client name, links to Finance agent",
      "type": "string — SaaS Enterprise Agreement | Annual Subscription | Usage-Based",
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
      "regulation": "string — e.g. PCI DSS, GDPR, SOC 2",
      "applicable_services": ["string — service names"],
      "current_status": "string — compliant | audit_due | non_compliant",
      "next_audit_date": "ISO 8601 date",
      "risk_level": "string — low | medium | high"
    }
  ]
}
```

**Synthetic data generation rules:**

- Include 3-4 client contracts. Nexus Corp has the feature delivery clause. Patel Industries has an SLA clause tied to uptime. One smaller contract is clean (noise).
- The investor agreement has the down-round clause with `trigger_metric: "runway_months"` and `trigger_threshold: 3`.
- Include a PCI DSS compliance obligation linked to the payments service. If the payments service is degraded, PCI compliance is also at risk.
- At least one contract should be in `compliant` status to show the agent correctly ignores non-issues.

**Cascade-critical contracts:**

```json
{
  "pipeline_contracts": [
    {
      "id": "CTR-DRAFT-047",
      "client": "Nexus Corp",
      "status": "in_procurement",
      "annual_value": 423360,
      "clauses": [
        {
          "section": "Section 4.2",
          "title": "Feature delivery prerequisite",
          "summary": "Contract execution contingent on Payments API v2 deployed to production by April 15, 2026. If not delivered, Nexus Corp walks.",
          "deadline": "2026-04-15",
          "linked_service": "payments-service",
          "linked_feature": "Payments API v2",
          "failure_consequence": "Deal collapses. $423,360/year revenue never materializes. Company remains pre-revenue.",
          "financial_impact": 423360,
          "status": "at_risk"
        }
      ]
    }
  ],
  "active_contracts": [
    {
      "id": "CTR-2025-063",
      "client": "Greenleaf Consulting",
      "status": "dispute",
      "annual_value": 54000,
      "clauses": [
        {
          "section": "Section 2.1",
          "title": "Deliverable acceptance",
          "summary": "Client claims analytics integration deliverable incomplete. Withholding payment.",
          "deadline": null,
          "linked_service": "analytics-pipeline",
          "linked_feature": "Analytics Dashboard",
          "breach_consequence": "$9,000 in receivables at risk",
          "financial_impact": 9000,
          "status": "monitoring"
        }
      ]
    }
  ]
}
```

---

### 4.5 Product Agent — `product_metrics.json`

**Purpose:** Simulate user engagement, feature adoption, support ticket trends, and churn signals. Degradation in the payments feature correlates with the infra issues.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
    "product": "Acme Payments Platform",
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
        "weekly_active_users": "integer",
        "daily_active_users_avg": "integer",
        "new_signups": "integer",
        "churn_count": "integer",
        "churn_rate": "float — 0-1",
        "nps_score": "integer — -100 to 100",
        "csat_score": "float — 0-5"
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

Global metrics should show a healthy product with a slow deterioration starting week 8:
- WAU: stable at 4200-4400 weeks 1-7, then declining 3-5% per week.
- NPS: 38-44 weeks 1-7, then dropping to single digits / negative by week 12.
- Churn rate: 1.5-2.2% weeks 1-7, then climbing to 8-9% by week 12.

Feature metrics should show the payments dashboard as the source of the product decline:
- Payments dashboard sessions and duration decline sharply from week 8.
- Payments dashboard error rate climbs from 0.2% to 12%+ (mirrors infra degradation).
- Other features (onboarding, analytics dashboard) stay stable — the problem is isolated to payments.

Support tickets should spike in the "payments processing errors" category from week 8 onward, with declining sentiment scores.

---

### 4.6 Market Agent — `market_signals.json`

**Purpose:** Simulate competitive intelligence, industry trends, and external threats. One competitor's aggressive moves add time pressure to the cascade.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
    "industry": "B2B Payments Infrastructure",
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
          "type": "string — funding_round | product_launch | hiring_signal | pricing_change | partnership | acquisition",
          "headline": "string — brief description",
          "details": "string — full context",
          "relevance_to_us": "string — how this impacts our company",
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

- Create one direct competitor (PayFlow AI) with an aggressive recent trajectory: Series B funding, product launch in the same space, and hiring spree.
- Create one adjacent competitor (noise) with minor signals that don't cascade.
- Include one regulatory signal (updated PCI DSS requirements) that adds compliance pressure on the payments service.
- PayFlow's signals should have `urgency: "high"` and `affected_domains` that include finance and product — this adds external pressure to the cascade timeline.

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

**Example anomaly (People agent detecting Sarah Chen's disengagement):**

```json
{
  "id": "anom-2026-0328-001",
  "agent_source": "people",
  "anomaly_type": "key_person_disengagement",
  "severity": 0.85,
  "confidence": 0.91,
  "entity_affected": "Sarah Chen",
  "entity_type": "developer",
  "description": "Lead Backend Engineer commit activity declined 94% over 5 weeks. PR reviews dropped to zero. Response time exceeded 72 hours. Owns 2 critical services.",
  "evidence": {
    "metric": "weekly_commits",
    "current_value": 2,
    "baseline_value": 35,
    "deviation_percent": -94.3,
    "trend_direction": "declining",
    "weeks_trending": 5
  },
  "linked_entities": [
    {"entity": "payments-service", "entity_type": "service", "relationship": "owns"},
    {"entity": "auth-service", "entity_type": "service", "relationship": "owns"}
  ],
  "cascade_potential": {
    "downstream_domains": ["infra", "legal", "finance"],
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

**Example cascade chain (the primary demo cascade):**

```json
{
  "id": "cascade-2026-0328-001",
  "name": "Sarah Chen disengagement → Nexus Corp contract breach → runway crisis",
  "trigger_anomaly_id": "anom-2026-0328-001",
  "status": "active",
  "detected_at": "2026-03-28T10:35:00Z",
  "last_updated": "2026-03-28T10:35:00Z",
  "chain": [
    {
      "step": 1,
      "node_id": "key_person_disengage",
      "domain": "people",
      "entity": "Sarah Chen",
      "event": "Lead backend engineer activity dropped 94% over 5 weeks",
      "probability": 0.91,
      "conditional_probability": 0.91,
      "evidence_from_agent": "2 commits in week 12 vs 35 baseline. Zero PR reviews. 78-hour response time.",
      "time_horizon_days": 0,
      "status": "occurred"
    },
    {
      "step": 2,
      "node_id": "critical_deploy_missed",
      "domain": "infra",
      "entity": "payments-service",
      "event": "Payments API v2 delivery deadline will be missed by 30+ days",
      "probability": 0.66,
      "conditional_probability": 0.72,
      "evidence_from_agent": "Feature at 34% completion. Zero deploys in 2 weeks. 3 unresolved blockers. No other engineer has context.",
      "time_horizon_days": 18,
      "status": "likely"
    },
    {
      "step": 3,
      "node_id": "client_contract_breach",
      "domain": "legal",
      "entity": "Nexus Corp — CTR-2025-047",
      "event": "Section 4.2 breached — client can terminate without penalty",
      "probability": 0.38,
      "conditional_probability": 0.58,
      "evidence_from_agent": "Contract requires Payments API v2 by April 15. Current projection: May 25+. Breach consequence: termination + refund.",
      "time_horizon_days": 18,
      "status": "possible"
    },
    {
      "step": 4,
      "node_id": "revenue_cliff",
      "domain": "finance",
      "entity": "Nexus Corp revenue",
      "event": "42% revenue lost + $211K refund liability. Monthly burn exceeds cash inflow.",
      "probability": 0.25,
      "conditional_probability": 0.65,
      "evidence_from_agent": "Nexus Corp = $35,280/month (42% of revenue). Refund clause: $211,680. Post-loss burn rate: $128K/month on $48K revenue.",
      "time_horizon_days": 48,
      "status": "possible"
    },
    {
      "step": 5,
      "node_id": "runway_crisis",
      "domain": "finance",
      "entity": "Company runway",
      "event": "Runway drops below 3 months, triggering investor down-round clause",
      "probability": 0.19,
      "conditional_probability": 0.75,
      "evidence_from_agent": "Current cash: $412K. Post-Nexus burn: $80K/month net. Runway: 5.1 months. After refund: $200K = 2.5 months. Below 3-month threshold.",
      "time_horizon_days": 75,
      "status": "possible"
    }
  ],
  "end_state": {
    "description": "Down-round clause triggered. Investor converts at 50% discount with 2x liquidation preference. Founder diluted below control threshold. Company effectively lost.",
    "severity": "catastrophic",
    "financial_impact": 1923360,
    "reversible": false
  },
  "overall_probability": 0.19,
  "company_risk_contribution": 0.72,
  "recommended_interventions": [
    {
      "step_to_break": 1,
      "action": "Immediate 1:1 with Sarah Chen. Identify root cause of disengagement. Offer retention package or begin knowledge transfer.",
      "urgency": "immediate",
      "effort": "low",
      "expected_risk_reduction": 0.65
    },
    {
      "step_to_break": 2,
      "action": "Assign backup engineer to payments-service. Begin pair programming for context transfer. Reassess delivery timeline.",
      "urgency": "immediate",
      "effort": "medium",
      "expected_risk_reduction": 0.45
    },
    {
      "step_to_break": 3,
      "action": "Proactively contact Nexus Corp. Negotiate deadline extension. Offer interim deliverable or SLA credit.",
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
| `deadpool_finance_data.csv` | Finance | CSV | ~12 KB | Transaction ledger: Sep 2025–Mar 2026, every income/expense with running balance |
| `deadpool_revenue_pipeline.csv` | Finance | CSV | ~3 KB | Revenue actuals, overdue invoices, pipeline deals with probabilities and feature dependencies |
| `deadpool_funding_runway.csv` | Finance | CSV | ~5 KB | Funding rounds, investor clause terms, monthly summaries, runway scenarios |
| `team_activity.json` | People | JSON | ~12 KB | 10 team members × 12 weeks of activity |
| `infrastructure.json` | Infra | JSON | ~12 KB | 6 services × 12 weeks of health metrics |
| `contracts.json` | Legal | JSON | ~8 KB | Pipeline deal terms + investor agreement + compliance |
| `product_metrics.json` | Product | JSON | ~10 KB | Global metrics + feature-level data + support tickets |
| `market_signals.json` | Market | JSON | ~6 KB | 2 competitors + industry trends + regulatory signals |
| `codebase_audit.json` | Code Audit | JSON | ~8 KB | Code ownership, CVE scan, test coverage, bus factor |
| `dependency_graph.json` | Cascade Mapper | JSON | ~4 KB | Pre-built node-edge graph with baseline probabilities |

**Total dataset: ~80 KB** — small enough to load entirely in memory, rich enough to power a compelling demo.

---

## 8. Data generation checklist

Before demo day, verify:

- [ ] All linking keys are consistent across files (`"Engineer 3"` / `"payments-service"` / `"Nexus Corp"` spelled identically everywhere)
- [ ] Timeline alignment: all files cover the same period (Sep 2025 – Mar 2026 for finance, weeks 1-12 of 2026 for others)
- [ ] Engineer 3's disengagement timeline in People data correlates with payments-service degradation in Infra data
- [ ] The Nexus Corp pipeline deal in `deadpool_revenue_pipeline.csv` references `linked_feature: "Payments API v2"` and `linked_service: "payments-service"`
- [ ] The funding terms in `deadpool_funding_runway.csv` show down-round trigger at `runway_months < 3` with correct consequence text
- [ ] Monthly summaries in `deadpool_funding_runway.csv` are consistent with the transaction ledger totals in `deadpool_finance_data.csv`
- [ ] Runway scenarios correctly show: base case ~6.7 months, best case (Nexus closes) ~13.2 months, worst case ~3.6 months to trigger
- [ ] At least 2-3 non-cascading anomalies exist as noise (Greenleaf overdue invoices, Patel Industries stalled deal, BrightPath SOC 2 delay)
- [ ] No data file references an entity that doesn't exist in another file
- [ ] Anomaly severity scores are calibrated: cascade-relevant anomalies are 0.7+ severity, noise anomalies are 0.3-0.5

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities*  
*Data specification v1.0 — March 28, 2026*