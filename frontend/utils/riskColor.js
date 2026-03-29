// ─── utils/riskColor.js ───────────────────────────────────────────────────────
export function getRiskColor(score) {
  if (score >= 70) return "#ef4444";
  if (score >= 45) return "#f59e0b";
  if (score >= 20) return "#10b981";
  return "#6366f1";
}

