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
| Finance | `financials.json` | Legal (contract values), People (headcount cost), Product (revenue-driving features) | Signal bus, Cascade mapper |
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
People agent finds: "Sarah Chen" commit drop
        │
        ▼ (developer_name → service ownership)
Infra agent checks: "payments-service" deploy velocity
        │
        ▼ (service_name → contract obligation)
Legal agent checks: contract CTR-2025-047 deadline for "Payments API v2"
        │
        ▼ (client_name → revenue share)
Finance agent checks: "Nexus Corp" revenue concentration = 42%
        │
        ▼ (funding terms → runway threshold)
Finance agent checks: down-round clause triggers at runway < 3 months
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

### 4.2 Finance Agent — `financials.json`

**Purpose:** Simulate 12 months of startup financials showing healthy early metrics that deteriorate as the cascade unfolds. Revenue is concentrated in one client tied to a feature delivery deadline.

**File structure:**

```json
{
  "metadata": {
    "company": "Acme SaaS Inc.",
    "stage": "Seed",
    "data_period": {
      "start": "2025-04-01",
      "end": "2026-03-31",
      "granularity": "monthly",
      "months": 12
    }
  },
  "monthly_financials": [
    {
      "month": "YYYY-MM",
      "revenue": {
        "total": "float — total monthly revenue",
        "by_client": {
          "client_name": "float — revenue from this client"
        },
        "mrr": "float — monthly recurring revenue",
        "arr": "float — annualized recurring revenue"
      },
      "expenses": {
        "total": "float — total monthly expenses",
        "payroll": "float",
        "cloud_infrastructure": "float",
        "legal_and_compliance": "float",
        "sales_and_marketing": "float",
        "office_and_misc": "float"
      },
      "cash_balance": "float — end of month cash",
      "monthly_burn_rate": "float — expenses minus revenue",
      "runway_months": "float — cash_balance / monthly_burn_rate"
    }
  ],
  "revenue_concentration": {
    "top_client": "string — client name",
    "top_client_share": "float — percentage of total revenue (0-1)",
    "herfindahl_index": "float — revenue concentration index"
  },
  "funding_history": [
    {
      "round": "string — Pre-Seed | Seed | Series A",
      "amount": "float",
      "date": "ISO 8601 date",
      "lead_investor": "string",
      "post_money_valuation": "float",
      "key_terms": {
        "down_round_protection": "string — description of clause",
        "trigger_condition": "string — condition that activates the clause",
        "consequence": "string — what happens when triggered"
      }
    }
  ],
  "accounts_receivable": [
    {
      "client": "string — client name",
      "invoice_amount": "float",
      "due_date": "ISO 8601 date",
      "days_overdue": "integer",
      "status": "string — paid | pending | overdue | at_risk"
    }
  ]
}
```

**Synthetic data generation rules:**

- Revenue should grow steadily months 1-8 (5-8% month-over-month), then flatten months 9-12.
- One client (Nexus Corp) should represent 40-45% of revenue throughout. This is the concentration risk.
- Burn rate should be stable around $120K-$135K/month with payroll as the largest component.
- Runway should start at 12+ months and gradually decline to ~6 months by the current month.
- The down-round clause should trigger at runway < 3 months — this is the final cascade node.
- Include one overdue invoice from a smaller client (noise, not cascade-relevant).

**Key cascade data points:**

```json
{
  "revenue_concentration": {
    "top_client": "Nexus Corp",
    "top_client_share": 0.42,
    "herfindahl_index": 0.28
  },
  "funding_history": [
    {
      "round": "Seed",
      "amount": 1500000,
      "date": "2025-06-01",
      "lead_investor": "Horizon Ventures",
      "post_money_valuation": 8000000,
      "key_terms": {
        "down_round_protection": "Full ratchet anti-dilution with enhanced liquidation preference",
        "trigger_condition": "runway_months < 3 before Series A close",
        "consequence": "Investor converts at 50% discount with 2x liquidation preference and board observer seat"
      }
    }
  ]
}
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
  "client_contracts": [
    {
      "id": "CTR-2025-047",
      "client": "Nexus Corp",
      "annual_value": 423360,
      "clauses": [
        {
          "section": "Section 4.2",
          "title": "Feature delivery obligation",
          "summary": "Payments API v2 must be deployed to production by April 15, 2026",
          "deadline": "2026-04-15",
          "linked_service": "payments-service",
          "linked_feature": "Payments API v2",
          "breach_consequence": "Client may terminate without penalty and receive prorated refund",
          "financial_impact": 423360,
          "status": "at_risk"
        },
        {
          "section": "Section 7.3",
          "title": "Refund on termination for cause",
          "summary": "All prepaid fees for unused period refunded within 30 days of termination",
          "deadline": null,
          "linked_service": null,
          "linked_feature": null,
          "breach_consequence": "Cash outflow of up to $211,680",
          "financial_impact": 211680,
          "status": "monitoring"
        }
      ]
    },
    {
      "id": "CTR-2025-012",
      "client": "Patel Industries",
      "annual_value": 221760,
      "clauses": [
        {
          "section": "Section 3.1",
          "title": "SLA guarantee",
          "summary": "99.5% uptime guaranteed. Three consecutive months below triggers 20% discount",
          "deadline": null,
          "linked_service": "payments-service",
          "linked_feature": null,
          "breach_consequence": "Automatic 20% revenue reduction on this contract",
          "financial_impact": 44352,
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

Place all synthetic data files in `/data/synthetic/` in the project repo.

| File | Agent | Size (approx) | Description |
|------|-------|---------------|-------------|
| `team_activity.json` | People | ~15 KB | 12 developers × 12 weeks of activity |
| `financials.json` | Finance | ~10 KB | 12 months of P&L, client revenue, funding terms |
| `infrastructure.json` | Infra | ~12 KB | 6 services × 12 weeks of health metrics |
| `contracts.json` | Legal | ~8 KB | 4 client contracts + 1 investor agreement + compliance |
| `product_metrics.json` | Product | ~10 KB | Global metrics + feature-level data + support tickets |
| `market_signals.json` | Market | ~6 KB | 2 competitors + industry trends + regulatory signals |
| `dependency_graph.json` | Cascade Mapper | ~4 KB | Pre-built node-edge graph with baseline probabilities |

**Total synthetic dataset: ~65 KB** — small enough to load entirely in memory, rich enough to power a compelling demo.

---

## 8. Data generation checklist

Before demo day, verify:

- [ ] All linking keys are consistent across files (`"Sarah Chen"` spelled identically everywhere, `"payments-service"` matches in all files)
- [ ] Timeline alignment: all files cover weeks 1-12 with the same `week_start` dates
- [ ] The cascade trigger developer's decline correlates with the infra service degradation (same timeline)
- [ ] The contract deadline (April 15) falls within the infra agent's projected miss window
- [ ] The financial model correctly shows runway dropping below 3 months if Nexus Corp revenue is removed + refund is paid
- [ ] At least 2-3 non-cascading anomalies exist as noise (vacation week, one-time blip, minor overdue invoice)
- [ ] No data file references an entity that doesn't exist in another file
- [ ] Anomaly severity scores are calibrated: the cascade-relevant anomalies are 0.7+ severity, noise anomalies are 0.3-0.5

---

*DEADPOOL — Dependency Evaluation And Downstream Prediction Of Operational Liabilities*  
*Data specification v1.0 — March 28, 2026*