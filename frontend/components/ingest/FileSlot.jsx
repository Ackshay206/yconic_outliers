import { DOMAIN_COLORS } from "../../constants/agents";
import { formatFileSize } from "../../utils/formatter";

// ─── FileSlot ─────────────────────────────────────────────────────────────────
export function FileSlot({ slot, uploaded, onFile }) {
  const color = DOMAIN_COLORS[slot.agent];
  return (
    <label style={{
      display: "flex", alignItems: "center", gap: 12, padding: "12px 16px",
      background: uploaded ? `${color}10` : "#0f172a",
      border: `1px solid ${uploaded ? color + "50" : "#1e293b"}`,
      borderRadius: 8, cursor: "pointer", transition: "all 0.2s",
    }}>
      <input type="file" accept={slot.ext} style={{ display: "none" }}
        onChange={e => e.target.files[0] && onFile(slot.id, slot.agent, e.target.files[0])} />
      <div style={{
        width: 36, height: 36, borderRadius: 6,
        background: `${color}20`, border: `1px solid ${color}40`,
        display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16,
      }}>{slot.icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, color: "#e2e8f0", fontSize: 13 }}>{slot.label}</div>
        <div style={{ fontSize: 11, color: uploaded ? color : "#475569" }}>
          {uploaded ? `✓ ${uploaded.name} (${formatFileSize(uploaded.size)})` : `Drop ${slot.ext} file here`}
        </div>
      </div>
      {uploaded ? <span style={{ color, fontSize: 18 }}>✓</span>
        : <span style={{ fontSize: 11, color: "#334155", background: "#1e293b", padding: "4px 10px", borderRadius: 4 }}>Browse</span>}
    </label>
  );
}
