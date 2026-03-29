import { AGENTS } from "../../constants/agents";
import { MOCK_AGENT_OUTPUTS } from "../../constants/mockOutputs";
import { AgentTabBar } from "./AgentTabBar";
import { AnomalyCard } from "./AnomalyCard";
import { StatusBadge } from "../shared/StatusBadge";

// ─── AgentOutputPanel ─────────────────────────────────────────────────────────
export function AgentOutputPanel({ activeAgent, onSelect }) {
  const agent = AGENTS.find(a => a.id === activeAgent);
  const out   = MOCK_AGENT_OUTPUTS[activeAgent];
  if (!agent || !out) return null;

  return (
    <div>
      <div style={{ borderTop: "1px solid #1e293b", paddingTop: 24, marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9" }}>Agent Analysis Output</div>
        <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>Click an agent to view its findings</div>
      </div>

      <AgentTabBar active={activeAgent} onChange={onSelect} />

      <div style={{ background: "#0f172a", border: `1px solid ${agent.color}30`, borderRadius: 12, overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: `1px solid ${agent.color}20`, display: "flex", justifyContent: "space-between", alignItems: "center", background: `${agent.color}08` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 22 }}>{agent.icon}</span>
            <div>
              <div style={{ fontWeight: 700, color: "#f1f5f9" }}>{agent.label}</div>
              <div style={{ fontSize: 11, color: "#475569" }}>Last run: just now · {out.anomalies.length} anomal{out.anomalies.length !== 1 ? "ies" : "y"} detected</div>
            </div>
          </div>
          <StatusBadge status={out.status} />
        </div>

        {out.anomalies.length === 0 ? (
          <div style={{ padding: 32, textAlign: "center", color: "#10b981" }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>✓</div>
            <div style={{ fontWeight: 600 }}>No anomalies detected</div>
            <div style={{ fontSize: 12, color: "#475569", marginTop: 4 }}>All signals within normal parameters</div>
          </div>
        ) : (
          <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {out.anomalies.map((a, i) => (
              <AnomalyCard key={i} anomaly={a} agentId={activeAgent} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
