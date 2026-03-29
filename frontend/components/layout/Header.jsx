// ─── Header.jsx ───────────────────────────────────────────────────────────────
import { getRiskColor } from "../../utils/riskColor";

export default function Header({ riskScore, showScore }) {
  const c = getRiskColor(riskScore);
  return (
    <div style={{
      borderBottom: "1px solid #1e293b", padding: "16px 32px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      background: "rgba(2,8,23,0.95)", backdropFilter: "blur(12px)",
      position: "sticky", top: 0, zIndex: 100,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: "linear-gradient(135deg,#ef4444,#7c3aed)",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18,
        }}>☠️</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: 2, color: "#f1f5f9" }}>DEADPOOL</div>
          <div style={{ fontSize: 10, color: "#475569", letterSpacing: 1 }}>
            DEPENDENCY EVALUATION AND DOWNSTREAM PREDICTION OF OPERATIONAL LIABILITIES
          </div>
        </div>
      </div>

      {showScore && (
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 10, color: "#475569", letterSpacing: 1 }}>COMPANY RISK SCORE</div>
            <div style={{ fontSize: 28, fontWeight: 900, color: c, lineHeight: 1 }}>{riskScore}</div>
          </div>
          <div style={{
            width: 48, height: 48, borderRadius: "50%",
            border: `3px solid ${c}`,
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20,
          }}>
            {riskScore >= 70 ? "🔴" : "🟡"}
          </div>
        </div>
      )}
    </div>
  );
}
