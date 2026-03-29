// ─── mockOutputs.js ───────────────────────────────────────────────────────────
export const MOCK_AGENT_OUTPUTS = {
  people: {
    status: "critical",
    anomalies: [
      { type: "Key-Person Disengagement", severity: 0.82, entity: "Engineer 3 (Mobile)",
        desc: "Commit activity dropped 68% over 6 weeks. Owns DM microservice exclusively. No PRs merged in 18 days.",
        linked: ["product","infra"] },
      { type: "Bus Factor Risk", severity: 0.71, entity: "Payments Service",
        desc: "Engineer 1 is sole contributor to payments service for past 3 sprints.",
        linked: ["infra","finance"] },
    ],
  },
  finance: {
    status: "critical",
    anomalies: [
      { type: "Revenue Concentration", severity: 0.74, entity: "TechCorp (46.9%)",
        desc: "Single client exceeds 40% threshold. Invoice $31,200 now 28 days overdue. Down-round clause activates below $4.75M valuation.",
        linked: ["legal","people"] },
      { type: "Burn Rate Acceleration", severity: 0.68, entity: "AWS Infrastructure",
        desc: "Cloud costs grew 144% in 90 days ($2,400 → $5,200/mo) with no corresponding revenue growth. Runway now 10.5 months.",
        linked: ["infra"] },
    ],
  },
  product: {
    status: "critical",
    anomalies: [
      { type: "Feature Abandonment", severity: 0.85, entity: "DM / Messaging",
        desc: "Drop-off rate 81%, error rate 38.4%, rage clicks up 3,617% since Jan. NPS collapsed from +42 to -14.",
        linked: ["people","infra"] },
      { type: "Churn Acceleration", severity: 0.79, entity: "Global — All Users",
        desc: "Weekly churn rate 6.4% (was 0.7% in Jan). Feb cohort month-1 retention 52% vs 74% for Oct cohort.",
        linked: ["finance"] },
    ],
  },
  infra: {
    status: "warning",
    anomalies: [
      { type: "Deploy Velocity Drop", severity: 0.61, entity: "messaging-service",
        desc: "No deployments to messaging-service in 21 days. CI pipeline shows 3 failing test suites unaddressed.",
        linked: ["people","product"] },
    ],
  },
  legal: {
    status: "warning",
    anomalies: [
      { type: "SLA Exposure", severity: 0.62, entity: "TechCorp MSA",
        desc: "99.5% uptime SLA at risk. DM feature downtime may trigger breach clause. Review within 14 days.",
        linked: ["product","finance"] },
    ],
  },
  market: {
    status: "healthy",
    anomalies: [],
  },
};

