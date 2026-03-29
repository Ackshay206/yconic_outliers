// ─── components/BriefingPanel.jsx ─────────────────────────────────────────────
import React from "react";

export default function BriefingPanel({ briefing }) {
  if (!briefing) return null;

  // API returns briefing as either a plain string or a FounderBriefing object
  const summary = typeof briefing === "string" ? briefing : briefing.summary;
  const timeline = typeof briefing === "string" ? null : briefing.timeline;
  const action = typeof briefing === "string" ? null : briefing.recommended_action;

  return (
    <div style={{
      background: "#0A0A0A",
      border: "1px solid #3D0000",
      borderRadius: 8,
      padding: "16px 20px",
      display: "flex",
      flexDirection: "column",
      gap: 12,
      flexShrink: 0,
    }}>
      <div style={{
        fontSize: 22, fontWeight: 900, fontStyle: "italic", textTransform: "uppercase",
        letterSpacing: "-0.5px",
        background: "linear-gradient(90deg, #FF2020, #7A0000)",
        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
      }}>
        Founder Briefing
      </div>

      {/* Summary */}
      {summary && (
        <p style={{ margin: 0, fontSize: 11, color: "#888888", fontStyle: "italic", lineHeight: 1.6 }}>
          {summary}
        </p>
      )}

      {/* Timeline */}
      {timeline && (
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            fontSize: 10, fontWeight: 700, letterSpacing: "0.05em",
            color: "#F59E0B", textTransform: "uppercase",
          }}>
            Timeline
          </span>
          <span style={{ fontSize: 11, fontStyle: "italic", color: "#F59E0B" }}>
            {timeline}
          </span>
        </div>
      )}

      {/* Recommended Action */}
      {action && (
        <div style={{
          background: "#1A0000",
          border: "1px solid #7A0000",
          borderRadius: 6,
          padding: "10px 14px",
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "#FF2020", marginBottom: 4 }}>
            Recommended Action
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#FFFFFF", lineHeight: 1.5 }}>
            {action}
          </div>
        </div>
      )}
    </div>
  );
}
