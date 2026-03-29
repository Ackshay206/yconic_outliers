import { useState } from "react";
import { AGENTS, DOMAIN_COLORS } from "../../constants/agents";
import { severityColor } from "../../utils/formatter";

// ─── AnomalyCard ──────────────────────────────────────────────────────────────
export function AnomalyCard({ anomaly, agentId, index }) {
  const [open, setOpen] = useState(false);
  const c = severityColor(anomaly.severity);
  return (
    <div style={{ background: "#020817", border: `1px solid ${c}30`, borderRadius: 8, overflow: "hidden" }}>
      <div onClick={() => setOpen(o => !o)} style={{ padding: "12px 16px", cursor: "pointer", display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 44, height: 44, borderRadius: 8, background: `${c}15`, border: `1px solid ${c}40`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
          <div style={{ fontSize: 14, fontWeight: 800, color: c }}>{Math.round(anomaly.severity * 100)}</div>
          <div style={{ fontSize: 8, color: c, letterSpacing: 0.5 }}>SEV</div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 13 }}>{anomaly.type}</div>
          <div style={{ fontSize: 11, color: "#64748b" }}>{anomaly.entity}</div>
        </div>
        <span style={{ color: "#475569", fontSize: 12 }}>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={{ padding: "12px 16px", borderTop: `1px solid ${c}20`, background: `${c}05` }}>
          <p style={{ color: "#94a3b8", fontSize: 12, margin: "0 0 10px", lineHeight: 1.6 }}>{anomaly.desc}</p>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span style={{ fontSize: 11, color: "#475569" }}>Cross-references:</span>
            {anomaly.linked.map(lid => {
              const la = AGENTS.find(a => a.id === lid);
              return la ? (
                <span key={lid} style={{ fontSize: 11, background: `${DOMAIN_COLORS[lid]}20`, color: DOMAIN_COLORS[lid], padding: "2px 8px", borderRadius: 10, border: `1px solid ${DOMAIN_COLORS[lid]}40` }}>
                  {la.icon} {la.label}
                </span>
              ) : null;
            })}
          </div>
        </div>
      )}
    </div>
  );
}
