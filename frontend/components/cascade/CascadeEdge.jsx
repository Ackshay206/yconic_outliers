// ─── CascadeEdge ──────────────────────────────────────────────────────────────
export function CascadeEdge({ edge, nodeMap, active }) {
  const from = nodeMap[edge.from], to = nodeMap[edge.to];
  if (!from || !to) return null;
  const mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2 - 30;
  return (
    <g>
      <path
        d={`M${from.x},${from.y} Q${mx},${my} ${to.x},${to.y}`}
        fill="none"
        stroke={active ? "#6366f1" : "#1e293b"}
        strokeWidth={active ? Math.max(1, edge.prob * 4) : 1}
        strokeOpacity={active ? 0.7 : 0.3}
        strokeDasharray={active ? "none" : "4 4"}
        markerEnd="url(#arrow)"
        filter={active ? "url(#glow)" : "none"}
      />
      {active && (
        <text x={mx} y={my - 6} textAnchor="middle" fontSize="10" fill="#94a3b8">
          {Math.round(edge.prob * 100)}%
        </text>
      )}
    </g>
  );
}


