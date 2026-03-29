import React from "react";
import { getBezierPath } from "@xyflow/react";

const SEVERITY_COLORS = {
  high:   "#dc2626",
  medium: "#f87171",
  low:    "#a8a29e",
};

export function CascadeFlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  style = {},
}) {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const color = SEVERITY_COLORS[data?.severity] || SEVERITY_COLORS.medium;

  return (
    <path
      id={id}
      d={edgePath}
      fill="none"
      stroke={color}
      strokeWidth={1.5}
      strokeDasharray="6 4"
      strokeOpacity={0.6}
      style={{
        ...style,
        animation: "dashFlow 1s linear infinite",
      }}
    />
  );
}
