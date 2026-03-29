// ─── components/RiskIndex.jsx ─────────────────────────────────────────────────
import React from "react";

export default function RiskIndex({ score }) {
  const display = score != null ? `${Number(score).toFixed(2)}%` : "0.00%";

  return (
    <div style={{
      background: "#1C1C1C", padding: 16, borderRadius: 6,
    }}>
      <div style={{
        fontSize: 9, fontWeight: 700, textTransform: "uppercase",
        letterSpacing: "0.08em", color: "#888888", marginBottom: 6,
      }}>
        Risk Index
      </div>
      <div style={{
        fontSize: 22, fontWeight: 900, color: "#FF2020",
        lineHeight: 1, letterSpacing: "-0.5px",
      }}>
        {display}
      </div>
    </div>
  );
}
