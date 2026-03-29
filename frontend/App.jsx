import React from "react";
import Header  from "./components/layout/Header";
import TabBar  from "./components/layout/TabBar";
import IngestTab  from "./components/ingest/IngestTab";
import CascadeTab from "./components/cascade/CascadeTab";
import { useAgentProcessor } from "./hooks/useAgentProcessor";
import { HARDCODED_CASCADE } from "./constants/cascade";

export default function App() {
  const [tab, setTab] = React.useState("ingest");
  const { files, agentStatus, processing, processed, handleFile, runAnalysis } = useAgentProcessor();

  return (
    <div style={{ minHeight: "100vh", background: "#020817", color: "#e2e8f0", fontFamily: "'Inter', sans-serif", fontSize: 14 }}>
      <Header riskScore={HARDCODED_CASCADE.riskScore} showScore={processed} />
      <TabBar active={tab} onChange={setTab} />

      <div style={{ padding: "28px 32px", maxWidth: 1200, margin: "0 auto" }}>
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
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #020817; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
      `}</style>
    </div>
  );
}