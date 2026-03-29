// ─── components/layout/Header.jsx ─────────────────────────────────────────────

export default function Header({ running, onRun, activePage, onPageChange, showCascades }) {
  const navTabs = [
    { id: "overview",  label: "Overview" },
    ...(showCascades ? [{ id: "cascades", label: "Cascade Chains" }] : []),
  ];

  return (
    <div style={{
      height: 48, background: "#0E0E0E",
      borderBottom: "1px solid #3D0000",
      display: "flex", alignItems: "center",
      justifyContent: "space-between",
      padding: "0 24px",
      position: "sticky", top: 0, zIndex: 100,
      flexShrink: 0,
    }}>
      {/* Left: branding */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, flex: "0 0 auto" }}>
        <span style={{
          fontSize: 20, fontWeight: 900, letterSpacing: "-0.5px",
          background: "linear-gradient(90deg, #FF2020, #B00000)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          DEADPOOL
        </span>
        <span style={{
          fontSize: 10, fontWeight: 700, textTransform: "uppercase",
          letterSpacing: "0.2em", color: "#888888",
        }}>
          Startup Risk Intelligence
        </span>
      </div>

      {/* Center: nav tabs */}
      <div style={{ display: "flex", alignItems: "stretch", height: "100%", gap: 0 }}>
        {navTabs.map(tab => {
          const active = tab.id === activePage;
          return (
            <button
              key={tab.id}
              onClick={() => onPageChange(tab.id)}
              style={{
                background: "none",
                border: "none",
                borderBottom: active ? "2px solid #FF2020" : "2px solid transparent",
                color: active ? "#FFFFFF" : "#555555",
                fontSize: 11, fontWeight: 700,
                textTransform: "uppercase", letterSpacing: "0.1em",
                padding: "0 18px",
                cursor: "pointer",
                transition: "color 0.15s, border-color 0.15s",
                display: "flex", alignItems: "center",
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.color = "#AAAAAA"; }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.color = "#555555"; }}
            >
              {tab.label}
              {tab.id === "cascades" && (
                <span style={{
                  marginLeft: 7, fontSize: 9, fontWeight: 900,
                  background: active ? "rgba(255,32,32,0.2)" : "rgba(255,255,255,0.06)",
                  color: active ? "#FF2020" : "#555555",
                  border: active ? "1px solid rgba(255,32,32,0.4)" : "1px solid #2A2A2A",
                  borderRadius: 10, padding: "1px 6px",
                }}>
                  LIVE
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Right: action */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, flex: "0 0 auto" }}>
        <button
          onClick={onRun}
          disabled={running}
          style={{
            background: running ? "#3D0000" : "linear-gradient(135deg, #FF2020, #7A0000)",
            color: running ? "#888888" : "#FFFFFF",
            border: "none", borderRadius: 6,
            padding: "8px 20px",
            fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em",
            cursor: running ? "not-allowed" : "pointer",
            transition: "opacity 0.2s",
            opacity: running ? 0.7 : 1,
          }}
        >
          {running ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>
    </div>
  );
}
