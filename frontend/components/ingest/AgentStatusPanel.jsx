import { AGENTS } from "../../constants/agents";
import { AgentStatusCard } from "./AgentStatusCard";

// ─── AgentStatusPanel ─────────────────────────────────────────────────────────
export function AgentStatusPanel({ agentStatus, activeAgent, processed, onSelect }) {
  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Agent Status</div>
        <div style={{ fontSize: 12, color: "#64748b" }}>Six specialized monitoring agents, each watching a domain</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {AGENTS.map(agent => (
          <AgentStatusCard key={agent.id} agent={agent}
            status={agentStatus[agent.id]}
            active={activeAgent === agent.id && processed}
            onClick={() => processed && onSelect(agent.id)} />
        ))}
      </div>
    </div>
  );
}
