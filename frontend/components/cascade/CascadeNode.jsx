import { DOMAIN_COLORS } from "../../constants/agents";

// ─── CascadeNode ──────────────────────────────────────────────────────────────
export function CascadeNode({ node, pulse, hovered, onEnter, onLeave }) {
  const c = DOMAIN_COLORS[node.domain];
  const r = hovered ? 38 : 32;
  const pulseR = r + 10 + Math.sin(pulse * 0.12) * 4;
  return (
    <g style={{ cursor: "pointer" }} onMouseEnter={onEnter} onMouseLeave={onLeave}>
      <circle cx={node.x} cy={node.y} r={pulseR} fill="none" stroke={c} strokeWidth="1"
        strokeOpacity={0.2 + Math.sin(pulse * 0.1) * 0.1} />
      <circle cx={node.x} cy={node.y} r={r + 8} fill={`url(#grad_${node.id})`} />
      <circle cx={node.x} cy={node.y} r={r} fill={`${c}22`} stroke={c}
        strokeWidth={hovered ? 2.5 : 1.5} filter="url(#glow)" />
      <circle cx={node.x} cy={node.y} r={r - 4} fill="none" stroke={c} strokeWidth="3"
        strokeOpacity="0.6"
        strokeDasharray={`${node.severity * 2 * Math.PI * (r - 4)} ${2 * Math.PI * (r - 4)}`}
        transform={`rotate(-90 ${node.x} ${node.y})`} />
      <text x={node.x} y={node.y + 4} textAnchor="middle" fontSize="12" fontWeight="700" fill={c}>
        {Math.round(node.severity * 100)}%
      </text>
      {node.label.split("\n").map((line, li) => (
        <text key={li} x={node.x} y={node.y + r + 14 + li * 13}
          textAnchor="middle" fontSize="10" fill="#cbd5e1" fontWeight={500}>{line}</text>
      ))}
      <rect x={node.x - 20} y={node.y - r - 18} width={40} height={14} rx={7}
        fill={`${c}33`} stroke={`${c}66`} strokeWidth="1" />
      <text x={node.x} y={node.y - r - 7} textAnchor="middle" fontSize="8" fill={c} fontWeight={700}>
        {node.domain.toUpperCase()}
      </text>
    </g>
  );
}




