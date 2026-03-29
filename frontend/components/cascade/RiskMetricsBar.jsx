import { DOMAIN_COLORS } from "../../constants/agents";
import { HARDCODED_CASCADE, ACTIVE_CHAINS } from "../../constants/cascade";
import { getRiskColor } from "../../utils/riskColor";
// import { useCascadeAnimation } from "../../hooks/useCascadeAnimation";

// ─── RiskMetricsBar ───────────────────────────────────────────────────────────
export function RiskMetricsBar({ riskScore, activeCascades, trend }) {
  const c = getRiskColor(riskScore);
  const criticalNodes = HARDCODED_CASCADE.nodes.filter(n => n.severity >= 0.7).length;
  const metrics = [
    { label: "Risk Score",      value: riskScore,      suffix: "/100",        color: c        },
    { label: "Active Cascades", value: activeCascades,  suffix: "",            color: "#f59e0b"},
    { label: "Trend",           value: "↑",            suffix: " Increasing",  color: "#ef4444"},
    { label: "Critical Nodes",  value: criticalNodes,  suffix: " nodes",       color: "#8b5cf6"},
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 24 }}>
      {metrics.map((m, i) => (
        <div key={i} style={{ background: "#0f172a", border: `1px solid ${m.color}30`, borderRadius: 10, padding: "16px 20px" }}>
          <div style={{ fontSize: 11, color: "#475569", letterSpacing: 1, marginBottom: 6 }}>{m.label.toUpperCase()}</div>
          <div style={{ fontSize: 26, fontWeight: 800, color: m.color }}>
            {m.value}<span style={{ fontSize: 13, fontWeight: 400, color: "#64748b" }}>{m.suffix}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
