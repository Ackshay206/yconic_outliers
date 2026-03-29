// ─── components/RiskIndex.jsx ─────────────────────────────────────────────────

const SEVERITY_COLORS = {
  critical: { bg: "rgba(255,32,32,0.15)",  border: "#FF2020", text: "#FF2020" },
  high:     { bg: "rgba(255,100,0,0.12)",  border: "#F97316", text: "#F97316" },
  medium:   { bg: "rgba(245,158,11,0.12)", border: "#F59E0B", text: "#F59E0B" },
  low:      { bg: "rgba(16,185,129,0.12)", border: "#10B981", text: "#10B981" },
};

const TREND_ICONS = {
  increasing: { icon: "↑", color: "#FF2020", label: "Increasing" },
  stable:     { icon: "→", color: "#F59E0B", label: "Stable"     },
  decreasing: { icon: "↓", color: "#10B981", label: "Decreasing" },
};

export default function RiskIndex({ score, severityLevel, trend }) {
  const display = score != null ? Number(score).toFixed(1) : "—";
  const sev     = SEVERITY_COLORS[severityLevel] ?? null;
  const trendMeta = TREND_ICONS[trend] ?? null;

  return (
    <div style={{
      background: "#111111",
      border: "1px solid #1E1E1E",
      borderRadius: 8,
      padding: "12px 16px",
      display: "flex",
      alignItems: "center",
      gap: 20,
    }}>
      {/* Score */}
      <div style={{ display: "flex", flexDirection: "column", gap: 3, flex: "0 0 auto" }}>
        <div style={{
          fontSize: 9, fontWeight: 700, textTransform: "uppercase",
          letterSpacing: "0.08em", color: "#555555",
        }}>
          Risk Index
        </div>
        <div style={{
          fontSize: 28, fontWeight: 900, color: "#FF2020",
          lineHeight: 1, letterSpacing: "-1px",
        }}>
          {display}
          <span style={{ fontSize: 13, fontWeight: 700, color: "#7A0000", marginLeft: 2 }}>
            /100
          </span>
        </div>
      </div>

      {/* Divider */}
      {(sev || trendMeta) && (
        <div style={{ width: 1, height: 36, background: "#2A2A2A", flexShrink: 0 }} />
      )}

      {/* Severity level */}
      {sev && severityLevel && (
        <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <div style={{
            fontSize: 9, fontWeight: 700, textTransform: "uppercase",
            letterSpacing: "0.08em", color: "#555555",
          }}>
            Severity
          </div>
          <span style={{
            display: "inline-block",
            fontSize: 10, fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.1em",
            padding: "3px 9px", borderRadius: 4,
            background: sev.bg, color: sev.text, border: `1px solid ${sev.border}44`,
          }}>
            {severityLevel}
          </span>
        </div>
      )}

      {/* Trend */}
      {trendMeta && (
        <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <div style={{
            fontSize: 9, fontWeight: 700, textTransform: "uppercase",
            letterSpacing: "0.08em", color: "#555555",
          }}>
            Trend
          </div>
          <div style={{
            display: "flex", alignItems: "center", gap: 5,
            fontSize: 11, fontWeight: 700, color: trendMeta.color,
          }}>
            <span style={{ fontSize: 16, lineHeight: 1 }}>{trendMeta.icon}</span>
            {trendMeta.label}
          </div>
        </div>
      )}
    </div>
  );
}
