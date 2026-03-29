// ─── components/AgentsPanel.jsx ───────────────────────────────────────────────
import React, { useState, useEffect } from "react";

const AGENTS = [
  { id: "people",     label: "People",     icon: "group",           processing: ["Scanning commits", "Checking activity", "Profiling team", "Mapping contributors"] },
  { id: "finance",    label: "Finance",    icon: "account_balance", processing: ["Auditing ledgers", "Analyzing burn rate", "Checking runway", "Reviewing AR aging"] },
  { id: "infra",      label: "Infra",      icon: "dns",             processing: ["Checking uptime", "Scanning deploy logs", "Reviewing SLAs", "Probing services"] },
  { id: "product",    label: "Product",    icon: "insights",        processing: ["Indexing metrics", "Analyzing churn", "Reviewing retention", "Checking error rates"] },
  { id: "legal",      label: "Legal",      icon: "gavel",           processing: ["Reviewing contracts", "Checking SLA clauses", "Scanning obligations", "Flagging deadlines"] },
  { id: "code_audit", label: "Code Audit", icon: "code",            processing: ["Scanning dependencies", "Checking CVEs", "Auditing coverage", "Mapping bus factor"] },
];

const STATUS_COLOR = {
  idle:       "#555555",
  processing: "#F59E0B",
  critical:   "#FF2020",
  warning:    "#F59E0B",
  healthy:    "#10B981",
};

const STATUS_GLOW = {
  idle:       "none",
  processing: "0 0 8px rgba(245,158,11,0.6)",
  critical:   "0 0 8px rgba(255,32,32,0.6)",
  warning:    "0 0 8px rgba(245,158,11,0.6)",
  healthy:    "0 0 8px rgba(16,185,129,0.6)",
};

const STATIC_TEXT = {
  idle:     "Standby",
  critical: "Critical risk",
  warning:  "Anomaly detected",
  healthy:  "All clear",
};

function AgentCard({ agent, status }) {
  const [msgIndex, setMsgIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (status !== "processing") return;
    setMsgIndex(0);
    
    let timerId;
    const tick = () => {
      setMsgIndex(i => (i + 1) % agent.processing.length);
      const nextDelay = 3500 + Math.random() * 3000; // 3.5s to 6.5s, avg ~5s
      timerId = setTimeout(tick, nextDelay);
    };
    
    const startDelay = 500 + Math.random() * 4500; // 0.5s to 5.0s
    timerId = setTimeout(tick, startDelay);

    return () => clearTimeout(timerId);
  }, [status, agent.processing.length]);

  const dotColor = STATUS_COLOR[status];
  const dotGlow  = STATUS_GLOW[status];
  const text     = status === "processing"
    ? agent.processing[msgIndex]
    : (STATIC_TEXT[status] || "Standby");

  return (
    <div 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
      background: "rgba(30, 30, 30, 0.5)",
      backdropFilter: "blur(12px)",
      WebkitBackdropFilter: "blur(12px)",
      border: "1px solid rgba(255, 60, 60, 0.15)",
      borderTop: "2px solid #FF2020",
      boxShadow: isHovered ? "0 8px 32px rgba(255, 32, 32, 0.25)" : "0 4px 30px rgba(0, 0, 0, 0.5)",
      borderRadius: 8,
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      textAlign: "center",
      padding: "0 12px",
      gap: 6,
      transform: isHovered ? "translateY(-4px)" : "translateY(0)",
      transition: "transform 0.2s ease-out, box-shadow 0.2s ease-out",
      cursor: "pointer",
    }}>
      <span className="material-icons" style={{
        fontSize: 28,
        color: status === "idle" ? "#3D0000" : dotColor,
        transition: "color 0.4s",
        lineHeight: 1,
      }}>
        {agent.icon}
      </span>
      <div style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "#888888" }}>
        {agent.label}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
        <div style={{
          width: 8, height: 8, borderRadius: "50%",
          background: dotColor, boxShadow: dotGlow, flexShrink: 0,
          transition: "background 0.4s, box-shadow 0.4s",
          animation: status === "processing" ? "pulseDot 1.5s infinite" : "none",
        }} />
        <span style={{ fontSize: 14, fontWeight: 600, color: "#FFFFFF", transition: "opacity 0.3s" }}>
          {text}
        </span>
      </div>
    </div>
  );
}

export default function AgentsPanel({ agentStatuses }) {
  return (
    <div style={{ display: "grid", gridTemplateRows: "auto 1fr", height: "100%", gap: 16 }}>
      <style>{`
        @keyframes pulseDot {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.4); opacity: 0.7; }
        }
      `}</style>
      <div style={{
        fontSize: 22, fontWeight: 900, fontStyle: "italic", textTransform: "uppercase",
        letterSpacing: "-0.5px",
        background: "linear-gradient(90deg, #FF2020, #7A0000)",
        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
      }}>
        Agents
      </div>

      <div style={{
        display: "grid", gridTemplateColumns: "1fr 1fr", gridTemplateRows: "repeat(3, 1fr)", gap: 16,
        minHeight: 0,
      }}>
        {AGENTS.map(agent => (
          <AgentCard key={agent.id} agent={agent} status={agentStatuses[agent.id] || "idle"} />
        ))}
      </div>
    </div>
  );
}
