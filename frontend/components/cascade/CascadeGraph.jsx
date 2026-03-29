import React from "react";
import { HARDCODED_CASCADE } from "../../constants/cascade";
import { DOMAIN_COLORS } from "../../constants/agents";
import { useCascadeAnimation } from "../../hooks/useCascaseAnimation";
import { CascadeEdge } from "./CascadeEdge";
import { CascadeNode } from "./CascadeNode";

// ─── CascadeGraph ─────────────────────────────────────────────────────────────
export function CascadeGraph() {
  const { nodes, edges } = HARDCODED_CASCADE;
  const { pulse, animStep } = useCascadeAnimation(edges.length);
  const [hoveredNode, setHoveredNode] = React.useState(null);

  const nodeMap = {};
  nodes.forEach(n => nodeMap[n.id] = n);
  const W = 960, H = 580;

  return (
    <div style={{ background: "#0a0f1e", border: "1px solid #1e293b", borderRadius: 12, padding: 24, marginBottom: 24, overflowX: "auto" }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", minWidth: 720 }}>
        <defs>
          {nodes.map(n => (
            <radialGradient key={n.id} id={`grad_${n.id}`} cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stopColor={DOMAIN_COLORS[n.domain]} stopOpacity="0.4" />
              <stop offset="100%" stopColor={DOMAIN_COLORS[n.domain]} stopOpacity="0.05" />
            </radialGradient>
          ))}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L0,6 L8,3 z" fill="#475569" />
          </marker>
        </defs>

        {edges.map((e, i) => (
          <CascadeEdge key={i} edge={e} nodeMap={nodeMap}
            active={i <= animStep % (edges.length + 1)} />
        ))}

        {nodes.map(n => (
          <CascadeNode key={n.id} node={n} pulse={pulse}
            hovered={hoveredNode === n.id}
            onEnter={() => setHoveredNode(n.id)}
            onLeave={() => setHoveredNode(null)} />
        ))}
      </svg>
    </div>
  );
}

