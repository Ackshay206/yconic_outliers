import { StatusBadge } from "../shared/StatusBadge";

// ─── AgentStatusCard ──────────────────────────────────────────────────────────
export function AgentStatusCard({ agent, status, active, onClick }) {
  const isProcessing = status === "processing";
  return (
    <div onClick={onClick} style={{
      padding: "12px 16px", borderRadius: 8, cursor: "pointer",
      background: active ? `${agent.color}15` : "#0f172a",
      border: `1px solid ${active ? agent.color + "50" : "#1e293b"}`,
      display: "flex", alignItems: "center", gap: 12, transition: "all 0.2s",
    }}>
      <span style={{ fontSize: 20 }}>{agent.icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: 13, color: "#e2e8f0" }}>{agent.label}</div>
        <div style={{ fontSize: 11, color: "#475569" }}>{agent.desc}</div>
      </div>
      {isProcessing
        ? <div style={{ width: 20, height: 20, border: `2px solid ${agent.color}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
        : <StatusBadge status={status || "idle"} />}
    </div>
  );
}