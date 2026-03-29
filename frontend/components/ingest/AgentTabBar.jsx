import { AGENTS } from "../../constants/agents";
import { MOCK_AGENT_OUTPUTS } from "../../constants/mockOutputs";

// ─── AgentTabBar ──────────────────────────────────────────────────────────────
export function AgentTabBar({ active, onChange }) {
  return (
    <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
      {AGENTS.map(a => {
        const out = MOCK_AGENT_OUTPUTS[a.id];
        const isActive = active === a.id;
        return (
          <button key={a.id} onClick={() => onChange(a.id)} style={{
            padding: "6px 14px", borderRadius: 20,
            border: `1px solid ${isActive ? a.color : "#1e293b"}`,
            background: isActive ? `${a.color}20` : "#0f172a",
            color: isActive ? a.color : "#64748b",
            fontSize: 12, fontWeight: isActive ? 700 : 400, cursor: "pointer",
          }}>
            {a.icon} {a.label.replace(" Agent", "")}
            {out?.anomalies?.length > 0 && (
              <span style={{ marginLeft: 6, background: "#ef444430", color: "#ef4444", borderRadius: 10, padding: "1px 6px", fontSize: 10 }}>
                {out.anomalies.length}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}