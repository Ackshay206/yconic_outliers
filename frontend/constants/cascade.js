// ─── cascade.js ──────────────────────────────────────────────────────────────
export const HARDCODED_CASCADE = {
  riskScore: 78,
  trend: "increasing",
  activeCascades: 3,
  nodes: [
    { id: "eng3_disengage",       x: 80,  y: 200, domain: "people",  label: "Engineer 3\nDisengagement",      severity: 0.82 },
    { id: "dm_feature_broken",    x: 280, y: 140, domain: "product", label: "DM Feature\nBroken",             severity: 0.78 },
    { id: "churn_spike",          x: 480, y: 100, domain: "product", label: "Churn Rate\nSpike +6.4%",        severity: 0.85 },
    { id: "revenue_drop",         x: 660, y: 140, domain: "finance", label: "Revenue\nCliff Risk",            severity: 0.71 },
    { id: "down_round",           x: 820, y: 200, domain: "finance", label: "Down-Round\nTrigger",            severity: 0.58 },
    { id: "techcorp_overdue",     x: 80,  y: 380, domain: "finance", label: "TechCorp AR\n28 Days Overdue",   severity: 0.74 },
    { id: "revenue_concentration",x: 280, y: 340, domain: "finance", label: "Revenue\nConcentration 46%",     severity: 0.68 },
    { id: "deploy_drop",          x: 280, y: 480, domain: "infra",   label: "Deploy Velocity\nDropped 60%",   severity: 0.61 },
    { id: "ci_failures",          x: 480, y: 440, domain: "infra",   label: "CI Failure\nRate Spike",         severity: 0.55 },
    { id: "contract_risk",        x: 660, y: 380, domain: "legal",   label: "SLA Contract\nAt Risk",          severity: 0.62 },
  ],
  edges: [
    { from: "eng3_disengage",        to: "dm_feature_broken",     prob: 0.82 },
    { from: "eng3_disengage",        to: "deploy_drop",            prob: 0.71 },
    { from: "dm_feature_broken",     to: "churn_spike",            prob: 0.78 },
    { from: "churn_spike",           to: "revenue_drop",           prob: 0.74 },
    { from: "revenue_drop",          to: "down_round",             prob: 0.58 },
    { from: "techcorp_overdue",      to: "revenue_concentration",  prob: 0.68 },
    { from: "revenue_concentration", to: "revenue_drop",           prob: 0.61 },
    { from: "deploy_drop",           to: "ci_failures",            prob: 0.55 },
    { from: "ci_failures",           to: "contract_risk",          prob: 0.52 },
    { from: "contract_risk",         to: "revenue_drop",           prob: 0.48 },
  ],
};

export const ACTIVE_CHAINS = [
  {
    label: "Cascade #1",
    chain: ["Engineer 3 Disengagement","DM Feature Broken","Churn Spike +6.4%","Revenue Cliff","Down-Round Trigger"],
    domains: ["people","product","product","finance","finance"],
    prob: 0.28,
  },
  {
    label: "Cascade #2",
    chain: ["TechCorp AR Overdue","Revenue Concentration 46%","Revenue Cliff","Down-Round Trigger"],
    domains: ["finance","finance","finance","finance"],
    prob: 0.31,
  },
  {
    label: "Cascade #3",
    chain: ["Deploy Velocity Drop","CI Failure Spike","SLA Contract Breach","Revenue Cliff"],
    domains: ["infra","infra","legal","finance"],
    prob: 0.19,
  },
];

