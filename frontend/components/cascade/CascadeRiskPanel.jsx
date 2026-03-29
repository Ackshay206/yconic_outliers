import React from "react";
import { DOMAIN_COLORS } from "../../constants/agents";
import { getRiskColor } from "../../utils/riskColor";

const EDGE_SEVERITY_LEGEND = [
  { label: "Critical", color: "#dc2626" },
  { label: "High",     color: "#f87171" },
  { label: "Medium",   color: "#a8a29e" },
];

export function CascadeRiskPanel({ riskScore, trend, activeCascades }) {
  const riskColor = getRiskColor(riskScore);
  const trendUp = trend === "increasing";

  return (
    <div
      style={{
        width: 260,
        minWidth: 260,
        background: "#111111",
        borderRight: "1px solid #2a1a1a",
        padding: "24px 18px",
        overflowY: "auto",
        height: "100%",
      }}
    >
      {/* Header */}
      <div style={{
        fontSize: 16,
        color: "#dc2626",
        letterSpacing: 1.5,
        fontWeight: 800,
        fontStyle: "italic",
        textTransform: "uppercase",
        marginBottom: 20,
      }}>
        Risk Index
      </div>

      {/* Risk Score */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 4, marginBottom: 6 }}>
        <span style={{ fontSize: 48, fontWeight: 900, color: "#dc2626", lineHeight: 1 }}>
          {riskScore}
        </span>
        <span style={{ fontSize: 14, color: "#525252", fontWeight: 600 }}>/100</span>
      </div>

      {/* Trend */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 4,
          fontSize: 11,
          fontWeight: 700,
          color: trendUp ? "#dc2626" : "#a8a29e",
          marginBottom: 24,
        }}
      >
        {trendUp ? "▲" : "▼"} {trendUp ? "INCREASING" : "DECREASING"}
      </div>

      {/* Active Cascades */}
      <div
        style={{
          background: "#1a1a1a",
          border: "1px solid #2a1a1a",
          borderTop: "2px solid #dc2626",
          borderRadius: 6,
          padding: "14px 14px",
          marginBottom: 28,
        }}
      >
        <div style={{ fontSize: 9, color: "#737373", letterSpacing: 1, fontWeight: 700, marginBottom: 6, textTransform: "uppercase" }}>Active Cascades</div>
        <div style={{ fontSize: 28, fontWeight: 900, color: "#dc2626" }}>{activeCascades}</div>
      </div>

      {/* Domain Legend */}
      <div style={{ fontSize: 10, color: "#737373", letterSpacing: 1, fontWeight: 700, marginBottom: 10, textTransform: "uppercase" }}>
        Domains
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 28 }}>
        {Object.entries(DOMAIN_COLORS).map(([domain, color]) => (
          <div key={domain} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "#a3a3a3" }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: color, flexShrink: 0 }} />
            {domain.charAt(0).toUpperCase() + domain.slice(1)}
          </div>
        ))}
      </div>

      {/* Edge Severity Legend */}
      <div style={{ fontSize: 10, color: "#737373", letterSpacing: 1, fontWeight: 700, marginBottom: 10, textTransform: "uppercase" }}>
        Threat Level
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {EDGE_SEVERITY_LEGEND.map((item) => (
          <div key={item.label} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "#a3a3a3" }}>
            <div style={{ width: 18, height: 0, borderTop: `2px dashed ${item.color}`, flexShrink: 0 }} />
            {item.label}
          </div>
        ))}
      </div>
    </div>
  );
}
