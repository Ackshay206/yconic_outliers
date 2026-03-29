import React from "react";
import { Handle, Position } from "@xyflow/react";
import { STATUS_CONFIG } from "../../constants/cascade";

// Deadpool-themed domain accent — everything channels through red
const DOMAIN_ACCENT = {
  people:  "#dc2626",
  finance: "#dc2626",
  product: "#f87171",
  infra:   "#f87171",
  legal:   "#a8a29e",
  market:  "#a8a29e",
};

export function CascadeFlowNode({ data, selected }) {
  const accent = DOMAIN_ACCENT[data.domain] || "#dc2626";
  const status = STATUS_CONFIG[data.status] || STATUS_CONFIG.POSSIBLE;

  return (
    <div
      style={{
        background: "#1a1a1a",
        border: `1px solid ${selected ? "#dc2626" : "#2a1a1a"}`,
        borderTop: `2px solid ${selected ? "#dc2626" : accent}`,
        borderRadius: 8,
        padding: "14px 16px",
        width: 220,
        cursor: "pointer",
        boxShadow: selected
          ? "0 0 24px rgba(220,38,38,0.25), 0 0 48px rgba(220,38,38,0.08)"
          : "0 2px 8px rgba(0,0,0,0.5)",
        transition: "all 0.2s ease",
      }}
    >
      {/* Top row: domain + status badges */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span
          style={{
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: 1.2,
            color: "#a8a29e",
            textTransform: "uppercase",
          }}
        >
          {data.domain}
        </span>
        <span
          style={{
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: 0.5,
            color: status.color,
            background: status.bg,
            border: `1px solid ${status.border}`,
            padding: "2px 6px",
            borderRadius: 3,
          }}
        >
          {status.label}
        </span>
      </div>

      {/* Title + subtitle */}
      <div style={{ fontSize: 13, fontWeight: 700, color: "#e5e5e5", marginBottom: 3, lineHeight: 1.3 }}>
        {data.title}
      </div>
      <div style={{ fontSize: 10, color: "#737373", marginBottom: 10, lineHeight: 1.3, fontStyle: "italic" }}>
        {data.subtitle}
      </div>

      {/* Metrics row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #2a2a2a", paddingTop: 8 }}>
        <div>
          <div style={{ fontSize: 8, color: "#737373", letterSpacing: 0.8, marginBottom: 2, textTransform: "uppercase" }}>Cascade</div>
          <div style={{ fontSize: 16, fontWeight: 900, color: "#dc2626" }}>
            {Math.round(data.cascadeProbability * 100)}%
          </div>
        </div>
      </div>

      {/* Handles */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#dc2626", border: "2px solid #1a1a1a", width: 8, height: 8 }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: "#dc2626", border: "2px solid #1a1a1a", width: 8, height: 8 }}
      />
    </div>
  );
}
