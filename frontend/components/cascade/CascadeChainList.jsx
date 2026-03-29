import { ACTIVE_CHAINS } from "../../constants/cascade";

// ─── CascadeChainList ─────────────────────────────────────────────────────────
export function CascadeChainList() {
  return (
    <div>
      <div style={{
        fontSize: 15,
        fontWeight: 800,
        fontStyle: "italic",
        color: "#dc2626",
        textTransform: "uppercase",
        letterSpacing: 1.5,
        marginBottom: 14,
      }}>
        Active Cascade Chains
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {ACTIVE_CHAINS.map((c, i) => (
          <div key={i} style={{ background: "#1a1a1a", border: "1px solid #2a1a1a", borderRadius: 6, padding: "14px 16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#e5e5e5" }}>{c.label}</div>
              <div style={{ fontSize: 12, color: c.prob >= 0.3 ? "#dc2626" : "#f87171", fontWeight: 700 }}>
                End-to-end: {Math.round(c.prob * 100)}%
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
              {c.chain.map((node, ni) => (
                <div key={ni} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <div style={{
                    padding: "5px 12px",
                    borderRadius: 4,
                    background: "#111111",
                    border: "1px solid #2a2a2a",
                    borderTop: "2px solid #dc2626",
                    color: "#d4d4d4",
                    fontSize: 11,
                    fontWeight: 600,
                  }}>
                    <span style={{ color: "#dc2626", fontWeight: 800, marginRight: 6, fontSize: 10 }}>
                      {String(ni + 1).padStart(2, "0")}
                    </span>
                    {node}
                  </div>
                  {ni < c.chain.length - 1 && <span style={{ color: "#dc2626", fontSize: 14, fontWeight: 700 }}>›</span>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
