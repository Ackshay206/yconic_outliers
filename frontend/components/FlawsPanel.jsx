// ─── components/FlawsPanel.jsx ────────────────────────────────────────────────
import React from "react";

function getSeverityLabel(severity) {
  if (severity >= 0.75) return "critical";
  if (severity >= 0.5)  return "high";
  return "medium";
}

const BADGE_STYLE = {
  critical: {
    background: "linear-gradient(135deg, #FF2020, #7A0000)",
    color: "#FFFFFF",
    border: "none",
  },
  high: {
    background: "linear-gradient(135deg, #C91D11, #5A0000)",
    color: "#FFFFFF",
    border: "none",
  },
  medium: {
    background: "transparent",
    color: "#888888",
    border: "1px solid #3D0000",
  },
};

function SeverityBadge({ level }) {
  const s = BADGE_STYLE[level];
  return (
    <span style={{
      fontSize: 8, fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.08em",
      padding: "2px 6px", borderRadius: 3,
      background: s.background, color: s.color, border: s.border,
      flexShrink: 0,
    }}>
      {level}
    </span>
  );
}

function agentLabel(agentId) {
  const map = {
    people: "People Agent", finance: "Finance Agent", infra: "Infra Agent",
    product: "Product Agent", legal: "Legal Agent", code_audit: "Code Audit Agent",
  };
  return map[agentId] || agentId;
}

export default function FlawsPanel({ anomalies }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      <div style={{
        fontSize: 22, fontWeight: 900, fontStyle: "italic", textTransform: "uppercase",
        letterSpacing: "-0.5px", marginBottom: 16,
        background: "linear-gradient(90deg, #FF2020, #7A0000)",
        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        flexShrink: 0,
      }}>
        Flaws Detected
      </div>

      <div style={{
        flex: 1,
        border: "1px solid #3D0000",
        borderRadius: 12,
        background: "#0A0A0A",
        overflowY: "auto",
        minHeight: 0,
      }}>
        {anomalies.length === 0 ? (
          <div style={{
            padding: 24, textAlign: "center", color: "#555555", fontSize: 12,
          }}>
            Run analysis to detect flaws
          </div>
        ) : (
          anomalies.map((flaw, i) => {
            const level = getSeverityLabel(flaw.severity);
            return (
              <div key={i}>
                <div style={{ padding: "14px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <SeverityBadge level={level} />
                    <span style={{ fontSize: 12, fontWeight: 700, color: "#FFFFFF" }}>
                      {flaw.type || flaw.entity || "Anomaly"}
                    </span>
                  </div>
                  <div style={{
                    fontSize: 10, fontWeight: 700, textTransform: "uppercase",
                    color: "#FF2020", marginBottom: 4, letterSpacing: "0.05em",
                  }}>
                    {agentLabel(flaw.agentId)}
                  </div>
                  <div style={{
                    fontSize: 11, color: "#888888", fontStyle: "italic", lineHeight: 1.5,
                  }}>
                    {flaw.desc || flaw.description || ""}
                  </div>
                </div>
                {i < anomalies.length - 1 && (
                  <div style={{ height: 1, background: "#3D0000", margin: "0 16px" }} />
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
