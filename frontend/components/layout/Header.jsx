import React from "react";

export default function Header({ running, onRun }) {
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
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
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

      {/* Right: action items */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
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
