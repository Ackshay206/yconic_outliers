import React from "react";
import Header        from "./components/layout/Header";
import AgentsPanel   from "./components/AgentsPanel";
import FlawsPanel    from "./components/FlawsPanel";
import RiskIndex     from "./components/RiskIndex";
import ErrorBoundary from "./components/ErrorBoundary";
import { useDeadpool } from "./hooks/useDeadpool";

function AppInner() {
  const { agentStatuses, anomalies, cascadeSteps, riskScore, running, error, runAnalysis } = useDeadpool();

  return (
    <div style={{
      height: "100%",
      background: "#0E0E0E", color: "#FFFFFF",
      fontFamily: "'Inter', sans-serif",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <Header running={running} onRun={runAnalysis} />
      {error && (
        <div style={{
          background: "#3D0000", color: "#FF6060", fontSize: 12, fontWeight: 600,
          padding: "8px 24px", borderBottom: "1px solid #7A0000", flexShrink: 0,
        }}>
          Analysis error: {error}
        </div>
      )}

      {/* Two-column body */}
      <div style={{
        flex: 1, display: "grid", gridTemplateColumns: "3fr 7fr",
        gap: 0, overflow: "hidden",
      }}>

        {/* Left column: Agents */}
        <div style={{
          background: "#0A0A0A",
          borderRight: "1px solid #3D0000",
          overflow: "hidden",
          padding: 24,
        }}>
          <AgentsPanel agentStatuses={agentStatuses} />
        </div>

        {/* Right column: Flaws Detected + Risk Index */}
        <div style={{
          background: "#111111",
          display: "flex", flexDirection: "column",
          padding: 24, gap: 24, overflow: "hidden",
        }}>
          <FlawsPanel anomalies={anomalies} />
          <div style={{ flexShrink: 0 }}>
            <RiskIndex score={riskScore} />
          </div>
        </div>
      </div>

      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        html, body, #root { height: 100%; overflow: hidden; margin: 0; padding: 0; }
        @keyframes spin { to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0E0E0E; }
        ::-webkit-scrollbar-thumb { background: #3D0000; border-radius: 2px; }
        .material-icons {
          font-family: 'Material Icons';
          font-weight: normal;
          font-style: normal;
          line-height: 1;
          letter-spacing: normal;
          text-transform: none;
          display: inline-block;
          white-space: nowrap;
          direction: ltr;
          -webkit-font-feature-settings: 'liga';
          font-feature-settings: 'liga';
          -webkit-font-smoothing: antialiased;
        }
      `}</style>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppInner />
    </ErrorBoundary>
  );
}
