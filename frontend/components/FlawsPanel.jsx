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
  const items = anomalies || [];
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
        {items.length === 0 ? (
          <div style={{
            height: "100%", display: "flex", flexDirection: "column",
            justifyContent: "center", alignItems: "center", gap: 16,
            color: "#555555", padding: 32, textAlign: "center"
          }}>
            <div style={{
              width: 80, height: 80, borderRadius: "50%",
              background: "rgba(255, 32, 32, 0.05)",
              border: "1px dashed rgba(255, 32, 32, 0.2)",
              display: "flex", justifyContent: "center", alignItems: "center",
              boxShadow: "0 0 30px rgba(255, 32, 32, 0.05)",
              animation: "pulse 3s infinite alternate"
            }}>
              <span className="material-icons" style={{ fontSize: 36, color: "rgba(255, 32, 32, 0.6)" }}>
                radar
              </span>
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "#888888", letterSpacing: "0.05em", marginBottom: 6, textTransform: "uppercase" }}>
                System Ready
              </div>
              <div style={{ fontSize: 12, lineHeight: 1.6, color: "#555555", maxWidth: 280, margin: "0 auto" }}>
                Awaiting manual override. Initiate the analysis to detect operational vulnerabilities and cascade risks.
              </div>
            </div>
            <style>{`
              @keyframes pulse {
                0% { box-shadow: 0 0 20px rgba(255, 32, 32, 0.02); border-color: rgba(255, 32, 32, 0.1); }
                100% { box-shadow: 0 0 40px rgba(255, 32, 32, 0.1); border-color: rgba(255, 32, 32, 0.4); }
              }
            `}</style>
          </div>
        ) : (
          items.map((flaw, i) => {
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
                {i < items.length - 1 && (
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
