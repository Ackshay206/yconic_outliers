// ─── components/FlawsPanel.jsx (Liabilities Panel) ────────────────────────────
import { useState } from "react";
import { DOMAIN_COLORS } from "../constants/agents";

// ── Severity helpers ────────────────────────────────────────────────────────────
function getSeverityLabel(severity) {
  if (severity >= 0.75) return "critical";
  if (severity >= 0.5)  return "high";
  return "medium";
}

const BADGE = {
  critical: { background: "linear-gradient(135deg, #FF2020, #7A0000)", color: "#FFFFFF", border: "none" },
  high:     { background: "linear-gradient(135deg, #C91D11, #5A0000)", color: "#FFFFFF", border: "none" },
  medium:   { background: "transparent", color: "#888888", border: "1px solid #3D0000" },
};

function SeverityBadge({ level }) {
  const s = BADGE[level];
  return (
    <span style={{
      fontSize: 8, fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.08em",
      padding: "2px 6px", borderRadius: 3,
      background: s.background, color: s.color, border: s.border,
      flexShrink: 0,
    }}>
      {level}
    </span>
  );
}

// ── Domain color dot + agent name pill ────────────────────────────────────────
function AgentPill({ agentId, agentName }) {
  const color = DOMAIN_COLORS[agentId] ?? "#888888";
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em",
      color, flexShrink: 0,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: "50%",
        background: color, flexShrink: 0,
        boxShadow: `0 0 6px ${color}88`,
      }} />
      {agentName}
    </span>
  );
}

// ── Single liability card ──────────────────────────────────────────────────────
function LiabilityCard({ item, isLast }) {
  const [expanded, setExpanded] = useState(false);
  const level = getSeverityLabel(item.severity);
  const domainColor = DOMAIN_COLORS[item.agentId] ?? "#888888";

  return (
    <div>
      <div
        style={{
          padding: "14px 16px",
          cursor: item.evidence ? "pointer" : "default",
          borderLeft: `2px solid ${domainColor}`,
          transition: "background 0.15s",
        }}
        onClick={() => item.evidence && setExpanded(e => !e)}
        onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.02)"; }}
        onMouseLeave={e => { e.currentTarget.style.background = ""; }}
      >
        {/* Row 1: severity badge + title */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
          <SeverityBadge level={level} />
          <span style={{ fontSize: 12, fontWeight: 700, color: "#FFFFFF", lineHeight: 1.4, flex: 1 }}>
            {item.type}
          </span>
        </div>

        {/* Row 2: agent pill + subtitle */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: item.desc ? 6 : 0, flexWrap: "wrap" }}>
          <AgentPill agentId={item.agentId} agentName={item.agentName} />
          {item.subtitle && (
            <span style={{ fontSize: 9, color: "#555555", fontStyle: "italic" }}>
              {item.subtitle}
            </span>
          )}
        </div>

        {/* Row 3: description */}
        {item.desc && (
          <div style={{ fontSize: 11, color: "#888888", fontStyle: "italic", lineHeight: 1.5 }}>
            {item.desc}
          </div>
        )}

        {/* Row 4: expand cue for evidence */}
        {item.evidence && (
          <div style={{
            marginTop: 6, fontSize: 9, color: domainColor, fontWeight: 700,
            textTransform: "uppercase", letterSpacing: "0.05em", opacity: 0.7,
          }}>
            {expanded ? "▲ Hide evidence" : "▼ Show evidence"}
          </div>
        )}

        {/* Expanded evidence */}
        {expanded && item.evidence && (
          <div style={{
            marginTop: 8,
            padding: "8px 10px",
            background: "#111111",
            border: "1px solid #2A2A2A",
            borderRadius: 4,
            fontSize: 10,
            color: "#666666",
            fontFamily: "monospace",
            lineHeight: 1.6,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}>
            {item.evidence}
          </div>
        )}
      </div>
      {!isLast && <div style={{ height: 1, background: "#1A1A1A", margin: "0 16px" }} />}
    </div>
  );
}

// ── Main panel ────────────────────────────────────────────────────────────────
export default function FlawsPanel({ liabilities }) {
  const items = liabilities || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "baseline", gap: 10,
        marginBottom: 16, flexShrink: 0,
      }}>
        <div style={{
          fontSize: 22, fontWeight: 900, fontStyle: "italic", textTransform: "uppercase",
          letterSpacing: "-0.5px",
          background: "linear-gradient(90deg, #FF2020, #7A0000)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          Liabilities Detected
        </div>
        {items.length > 0 && (
          <span style={{
            fontSize: 11, fontWeight: 700, color: "#FF2020",
            background: "rgba(255,32,32,0.1)",
            border: "1px solid rgba(255,32,32,0.3)",
            borderRadius: 10, padding: "1px 7px",
          }}>
            {items.length}
          </span>
        )}
      </div>

      {/* List */}
      <div style={{
        flex: 1,
        border: "1px solid #3D0000",
        borderRadius: 12,
        background: "#0A0A0A",
        overflowY: "auto",
        minHeight: 0,
      }}>
        {items.length === 0 ? (
          <div style={{
            height: "100%", display: "flex", flexDirection: "column",
            justifyContent: "center", alignItems: "center", gap: 16,
            color: "#555555", padding: 32, textAlign: "center",
          }}>
            <div style={{
              width: 80, height: 80, borderRadius: "50%",
              background: "rgba(255, 32, 32, 0.05)",
              border: "1px dashed rgba(255, 32, 32, 0.2)",
              display: "flex", justifyContent: "center", alignItems: "center",
              boxShadow: "0 0 30px rgba(255, 32, 32, 0.05)",
              animation: "pulse 3s infinite alternate",
            }}>
              <span className="material-icons" style={{ fontSize: 36, color: "rgba(255, 32, 32, 0.6)" }}>
                radar
              </span>
            </div>
            <div>
              <div style={{
                fontSize: 16, fontWeight: 700, color: "#888888",
                letterSpacing: "0.05em", marginBottom: 6, textTransform: "uppercase",
              }}>
                System Ready
              </div>
              <div style={{ fontSize: 12, lineHeight: 1.6, color: "#555555", maxWidth: 280, margin: "0 auto" }}>
                Awaiting manual override. Initiate the analysis to detect operational
                liabilities and cascade risks.
              </div>
            </div>
            <style>{`
              @keyframes pulse {
                0%   { box-shadow: 0 0 20px rgba(255,32,32,0.02); border-color: rgba(255,32,32,0.1); }
                100% { box-shadow: 0 0 40px rgba(255,32,32,0.10); border-color: rgba(255,32,32,0.4); }
              }
            `}</style>
          </div>
        ) : (
          items.map((item, i) => (
            <LiabilityCard key={item.nodeId || i} item={item} isLast={i === items.length - 1} />
          ))
        )}
      </div>
    </div>
  );
}
