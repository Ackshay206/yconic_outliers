import { ACTIVE_CHAINS } from "../../constants/cascade";
import { DOMAIN_COLORS } from "../../constants/agents";

// ─── CascadeChainList ─────────────────────────────────────────────────────────
export function CascadeChainList() {
  return (
    <div>
      <div style={{ fontSize: 15, fontWeight: 700, color: "#f1f5f9", marginBottom: 14 }}>Active Cascade Chains</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {ACTIVE_CHAINS.map((c, i) => (
          <div key={i} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, padding: "14px 16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9" }}>{c.label}</div>
              <div style={{ fontSize: 12, color: c.prob >= 0.3 ? "#ef4444" : "#f59e0b", fontWeight: 700 }}>
                End-to-end probability: {Math.round(c.prob * 100)}%
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
              {c.chain.map((node, ni) => (
                <div key={ni} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <div style={{ padding: "4px 10px", borderRadius: 4, background: `${DOMAIN_COLORS[c.domains[ni]]}15`, border: `1px solid ${DOMAIN_COLORS[c.domains[ni]]}40`, color: DOMAIN_COLORS[c.domains[ni]], fontSize: 11, fontWeight: 600 }}>
                    {node}
                  </div>
                  {ni < c.chain.length - 1 && <span style={{ color: "#334155", fontSize: 14 }}>→</span>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
