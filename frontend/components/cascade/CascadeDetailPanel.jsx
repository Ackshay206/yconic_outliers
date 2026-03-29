import React from "react";
import { STATUS_CONFIG } from "../../constants/cascade";
import { getRiskColor } from "../../utils/riskColor";

export function CascadeDetailPanel({ node, onClose }) {
  if (!node) return null;

  const status = STATUS_CONFIG[node.status] || STATUS_CONFIG.POSSIBLE;

  const metrics = [
    { label: "Cascade Prob",      value: `${Math.round(node.cascadeProbability * 100)}%`,      color: getRiskColor(node.cascadeProbability * 100) },
  ];

  return (
    <div
      style={{
        width: 320,
        minWidth: 320,
        background: "#111111",
        borderLeft: "1px solid #2a1a1a",
        padding: "20px 18px",
        overflowY: "auto",
        height: "100%",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{
          fontSize: 14,
          color: "#dc2626",
          letterSpacing: 1.5,
          fontWeight: 800,
          fontStyle: "italic",
          textTransform: "uppercase",
        }}>
          Event Detail
        </span>
        <button
          onClick={onClose}
          style={{
            background: "#1a1a1a",
            border: "1px solid #2a2a2a",
            borderRadius: 4,
            color: "#737373",
            cursor: "pointer",
            padding: "4px 10px",
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          Close
        </button>
      </div>

      {/* Status badge */}
      <span
        style={{
          display: "inline-block",
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: 0.5,
          color: status.color,
          background: status.bg,
          border: `1px solid ${status.border}`,
          padding: "3px 8px",
          borderRadius: 3,
          marginBottom: 12,
        }}
      >
        {status.label}
      </span>

      {/* Title, subtitle */}
      <div style={{ fontSize: 17, fontWeight: 800, color: "#e5e5e5", marginBottom: 4, lineHeight: 1.3 }}>
        {node.title}
      </div>
      <div style={{ fontSize: 12, color: "#dc2626", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 16 }}>
        {node.agentName}
      </div>

      {/* Description */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 12, color: "#a3a3a3", lineHeight: 1.7, fontStyle: "italic" }}>
          {node.description}
        </div>
      </div>

      {/* Evidence */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 10, color: "#737373", letterSpacing: 1, fontWeight: 700, marginBottom: 8, textTransform: "uppercase" }}>Evidence</div>
        <div
          style={{
            fontSize: 11,
            color: "#d4d4d4",
            lineHeight: 1.7,
            background: "#1a1a1a",
            border: "1px solid #2a1a1a",
            borderLeft: "2px solid #dc2626",
            borderRadius: 4,
            padding: 12,
          }}
        >
          {node.evidence}
        </div>
      </div>

      {/* Metrics grid */}
      <div style={{ fontSize: 10, color: "#737373", letterSpacing: 1, fontWeight: 700, marginBottom: 10, textTransform: "uppercase" }}>Metrics</div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
        {metrics.map((m, i) => (
          <div
            key={i}
            style={{
              background: "#1a1a1a",
              border: "1px solid #2a2a2a",
              borderRadius: 6,
              padding: "10px 10px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 8, color: "#737373", letterSpacing: 0.8, marginBottom: 4, textTransform: "uppercase" }}>
              {m.label}
            </div>
            <div style={{ fontSize: 16, fontWeight: 900, color: m.color }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
