import { useState } from "react";
import Header            from "./components/layout/Header";
import AgentsPanel       from "./components/AgentsPanel";
import FlawsPanel        from "./components/FlawsPanel";
import CascadeChainPanel from "./components/CascadeChainPanel";
import RiskIndex         from "./components/RiskIndex";
import BriefingPanel     from "./components/BriefingPanel";
import AgentChatPanel    from "./components/AgentChatPanel";
import LandingPage       from "./components/LandingPage";
import ErrorBoundary     from "./components/ErrorBoundary";
import { useDeadpool }   from "./hooks/useDeadpool";

function AppInner() {
  const {
    agentStatuses,
    liabilities,
    cascadeChains,
    cascadeNodes,
    cascadeEdges,
    riskScore,
    severityLevel,
    trend,
    briefing,
    running,
    done,
    error,
    runAnalysis,
  } = useDeadpool();

  const [landed, setLanded]         = useState(false); // false = show landing
  // "cascades" page only unlocks after analysis completes
  const [activePage, setActivePage] = useState("overview");

  // If analysis re-runs, stay on current page
  const handlePageChange = (page) => {
    if (page === "cascades" && !done) return;
    setActivePage(page);
  };

  return (
    <div style={{
      height: "100%",
      background: "#0E0E0E", color: "#FFFFFF",
      fontFamily: "'Inter', sans-serif",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
      position: "relative",
    }}>
      {/* Loading overlay */}
      {running && (
        <div style={{
          position: "absolute", inset: 0, zIndex: 50,
          background: "rgba(0,0,0,0.4)",
          pointerEvents: "none",
        }} />
      )}

      <Header
        running={running}
        onRun={runAnalysis}
        activePage={activePage}
        onPageChange={handlePageChange}
        showCascades={done && cascadeChains.length > 0}
      />

      {/* Error banner */}
      {error && (
        <div style={{
          background: "#3D0000", color: "#FF6060", fontSize: 12, fontWeight: 600,
          padding: "8px 24px", borderBottom: "1px solid #7A0000", flexShrink: 0,
        }}>
          Analysis error: {error}
        </div>
      )}

      {/* ── PAGE: Agent Chat ──────────────────────────────────────────────── */}
      {activePage === "chat" ? (
        <div style={{ flex: 1, overflow: "hidden" }}>
          <AgentChatPanel agentStatuses={agentStatuses} />
        </div>

      /* ── PAGE: Cascade Chains (full-width) ──────────────────────────────── */
      ) : activePage === "cascades" ? (
        <div style={{ flex: 1, overflow: "hidden" }}>
          <CascadeChainPanel
            cascadeChains={cascadeChains}
            cascadeNodes={cascadeNodes}
            cascadeEdges={cascadeEdges}
          />
        </div>
      ) : (
        /* ── PAGE: Overview (two-column) ──────────────────────────────────── */
        <div style={{
          flex: 1, display: "grid", gridTemplateColumns: "3fr 7fr",
          gap: 0, overflow: "hidden",
        }}>
          {/* Left — Agents */}
          <div style={{
            background: "#0A0A0A",
            borderRight: "1px solid #3D0000",
            overflow: "hidden",
            padding: 24,
          }}>
            <AgentsPanel agentStatuses={agentStatuses} />
          </div>

          {/* Right — Briefing + Liabilities + Risk Index */}
          <div style={{
            background: "#111111",
            display: "flex", flexDirection: "column",
            padding: 24, gap: 20, overflow: "hidden",
          }}>
            <BriefingPanel briefing={briefing} />
            <FlawsPanel liabilities={liabilities} />
            <div style={{ flexShrink: 0 }}>
              <RiskIndex score={riskScore} severityLevel={severityLevel} trend={trend} />
            </div>
          </div>
        </div>
      )}

      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        html, body, #root { height: 100%; overflow: hidden; margin: 0; padding: 0; }
        @keyframes spin { to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0E0E0E; }
        ::-webkit-scrollbar-thumb { background: #3D0000; border-radius: 2px; }
        .material-icons {
          font-family: 'Material Icons'; font-weight: normal; font-style: normal;
          line-height: 1; letter-spacing: normal; text-transform: none;
          display: inline-block; white-space: nowrap; direction: ltr;
          -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga';
          -webkit-font-smoothing: antialiased;
        }
      `}</style>

      {/* Landing page overlays on top — main app is already mounted beneath,
          so when the landing fades out there is no white flash */}
      {!landed && <LandingPage onEnter={() => setLanded(true)} />}
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
