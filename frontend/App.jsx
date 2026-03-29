import React from "react";
import Header  from "./components/layout/Header";
import TabBar  from "./components/layout/TabBar";
import IngestTab  from "./components/ingest/IngestTab";
import CascadeTab from "./components/cascade/CascadeTab";
import { useAgentProcessor } from "./hooks/useAgentProcessor";
import { CASCADE_MOCK_DATA } from "./constants/cascade";

export default function App() {
  const [tab, setTab] = React.useState("ingest");
  const { files, agentStatus, processing, processed, handleFile, runAnalysis } = useAgentProcessor();

  return (
    <div style={{ minHeight: "100vh", background: "#0d0d0d", color: "#d4d4d4", fontFamily: "'Inter', sans-serif", fontSize: 14 }}>
      <Header riskScore={CASCADE_MOCK_DATA.riskScore} showScore={processed} />
      <TabBar active={tab} onChange={setTab} />

      <div style={{ padding: "28px 32px", ...(tab === "cascade" ? {} : { maxWidth: 1200, margin: "0 auto" }) }}>
        {tab === "ingest" && (
          <IngestTab
            files={files}
            agentStatus={agentStatus}
            processing={processing}
            processed={processed}
            onFile={handleFile}
            onRun={runAnalysis}
          />
        )}
        {tab === "cascade" && <CascadeTab />}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes dashFlow { to { stroke-dashoffset: -20; } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0d0d0d; }
        ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
        .react-flow__controls button { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; color: #737373 !important; }
        .react-flow__controls button:hover { background: #2a2a2a !important; }
        .react-flow__controls button svg { fill: #737373 !important; }
      `}</style>
    </div>
  );
}
