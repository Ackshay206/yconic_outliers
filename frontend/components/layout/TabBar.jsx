// ─── TabBar.jsx ───────────────────────────────────────────────────────────────
const TABS = [
  { id: "ingest",  label: "📥  Data Ingestion & Agent Analysis" },
  { id: "cascade", label: "🕸️  Cascade Visualization" },
];

export default function TabBar({ active, onChange }) {
  return (
    <div style={{ borderBottom: "1px solid #1e293b", padding: "0 32px", display: "flex" }}>
      {TABS.map(t => (
        <button key={t.id} onClick={() => onChange(t.id)} style={{
          padding: "14px 24px", background: "none", border: "none", cursor: "pointer",
          color: active === t.id ? "#6366f1" : "#475569",
          borderBottom: active === t.id ? "2px solid #6366f1" : "2px solid transparent",
          fontWeight: active === t.id ? 700 : 400,
          fontSize: 13, letterSpacing: 0.5, transition: "all 0.2s",
        }}>{t.label}</button>
      ))}
    </div>
  );
}