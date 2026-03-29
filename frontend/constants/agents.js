export const AGENTS = [
  { id: "people",  label: "People Agent",  color: "#6366f1", icon: "👥", desc: "GitHub commit activity, Slack signals, key-person risk" },
  { id: "finance", label: "Finance Agent", color: "#10b981", icon: "💰", desc: "Burn rate, runway, revenue concentration, AR aging" },
  { id: "product", label: "Product Agent", color: "#f59e0b", icon: "📊", desc: "Churn, NPS, feature adoption, support ticket sentiment" },
  { id: "infra",   label: "Infra Agent",   color: "#ef4444", icon: "⚙️",  desc: "Deploy frequency, CI failures, uptime, cloud costs" },
  { id: "legal",   label: "Legal Agent",   color: "#8b5cf6", icon: "⚖️",  desc: "Contract deadlines, compliance gaps, IP exposure" },
  { id: "code_audit", label: "Code Audit",  color: "#06b6d4", icon: "🔍", desc: "Commit history, CVEs, bus factor, test coverage, deploy velocity" },
];

export const DOMAIN_COLORS = {
  people:     "#6366f1",
  finance:    "#10b981",
  product:    "#f59e0b",
  infra:      "#ef4444",
  legal:      "#8b5cf6",
  code_audit: "#06b6d4",
};