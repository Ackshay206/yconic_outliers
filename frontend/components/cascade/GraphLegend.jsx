import { DOMAIN_COLORS } from "../../constants/agents";

// ─── GraphLegend ──────────────────────────────────────────────────────────────
export function GraphLegend() {
  return (
    <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
      {Object.entries(DOMAIN_COLORS).map(([domain, color]) => (
        <div key={domain} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#94a3b8" }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: color }} />
          {domain.charAt(0).toUpperCase() + domain.slice(1)}
        </div>
      ))}
      <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#475569", marginLeft: "auto" }}>
        <div style={{ width: 20, height: 2, background: "#6366f1" }} /> Active
        <div style={{ width: 20, height: 1, borderTop: "1px dashed #475569" }} /> Inactive
      </div>
    </div>
  );
}


