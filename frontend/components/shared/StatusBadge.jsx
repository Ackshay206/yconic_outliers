// ─── StatusBadge (shared primitive) ──────────────────────────────────────────
export function StatusBadge({ status }) {
  const cfg = {
    critical: { bg: "rgba(239,68,68,0.15)",   color: "#ef4444", label: "CRITICAL" },
    warning:  { bg: "rgba(245,158,11,0.15)",  color: "#f59e0b", label: "WARNING"  },
    healthy:  { bg: "rgba(16,185,129,0.15)",  color: "#10b981", label: "HEALTHY"  },
    idle:     { bg: "rgba(100,116,139,0.15)", color: "#64748b", label: "IDLE"     },
    uploaded: { bg: "rgba(99,102,241,0.15)",  color: "#6366f1", label: "UPLOADED" },
    processing:{ bg:"rgba(245,158,11,0.15)", color: "#f59e0b", label: "RUNNING"  },
  }[status] ?? { bg: "rgba(100,116,139,0.15)", color: "#64748b", label: "IDLE" };

  return (
    <span style={{
      background: cfg.bg, color: cfg.color,
      border: `1px solid ${cfg.color}40`,
      borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700, letterSpacing: 1,
    }}>{cfg.label}</span>
  );
}
