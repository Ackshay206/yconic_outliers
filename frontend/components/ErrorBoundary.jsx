// ─── components/ErrorBoundary.jsx ─────────────────────────────────────────────
import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message || "An unexpected error occurred." };
  }

  componentDidCatch(error, info) {
    console.error("[DEADPOOL] Uncaught render error:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
          background: "#0E0E0E", color: "#FF2020", fontFamily: "'Inter', sans-serif",
          flexDirection: "column", gap: 12, padding: 32,
        }}>
          <div style={{ fontSize: 22, fontWeight: 900, textTransform: "uppercase", letterSpacing: "-0.5px" }}>
            Render Error
          </div>
          <div style={{ fontSize: 13, color: "#888888", textAlign: "center", maxWidth: 420 }}>
            {this.state.message}
          </div>
          <button
            onClick={() => this.setState({ hasError: false, message: null })}
            style={{
              marginTop: 8, padding: "8px 20px", borderRadius: 6, border: "none",
              background: "linear-gradient(135deg, #FF2020, #7A0000)",
              color: "#FFFFFF", fontWeight: 700, fontSize: 11,
              textTransform: "uppercase", letterSpacing: "0.12em", cursor: "pointer",
            }}
          >
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
