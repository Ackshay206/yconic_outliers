import React, { useState } from "react";
import { FileUploadPanel } from "./FileUploadPanel";
import { AgentStatusPanel } from "./AgentStatusPanel";
import { AgentOutputPanel } from "./AgentOutputPanel";

// import { AGENTS, DOMAIN_COLORS } from "../../constants/agents";
import { FILE_SLOTS } from "../../constants/fileSlots";
// import { MOCK_AGENT_OUTPUTS } from "../../constants/mockOutputs";
// import { formatFileSize, severityColor } from "../../utils/formatters";

// ─── IngestTab (root) ─────────────────────────────────────────────────────────
export default function IngestTab({ files, agentStatus, processing, processed, onFile, onRun }) {
  const [activeAgent, setActiveAgent] = useState("people");
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 28 }}>
        <FileUploadPanel files={files} processing={processing} processed={processed} onFile={onFile} onRun={onRun} />
        <AgentStatusPanel agentStatus={agentStatus} activeAgent={activeAgent} processed={processed} onSelect={setActiveAgent} />
      </div>

      {processed && <AgentOutputPanel activeAgent={activeAgent} onSelect={setActiveAgent} />}

      {!processed && Object.keys(files).length === 0 && (
        <div style={{ textAlign: "center", padding: "48px 0", color: "#334155" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>☠️</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Upload your startup data to begin</div>
          <div style={{ fontSize: 13 }}>DEADPOOL needs data to find your kill chain</div>
        </div>
      )}
    </div>
  );
}