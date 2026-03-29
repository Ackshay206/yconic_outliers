// ─── hooks/useAgentProcessor.js ───────────────────────────────────────────────
import { useState } from "react";
import { MOCK_AGENT_OUTPUTS } from "../constants/mockOutputs";

export function useAgentProcessor() {
  const [files, setFiles]           = useState({});
  const [agentStatus, setAgentStatus] = useState({});
  const [processing, setProcessing] = useState(false);
  const [processed, setProcessed]   = useState(false);

  const handleFile = (slotId, agentId, file) => {
    setFiles(f => ({ ...f, [slotId]: { file, agentId, name: file.name, size: file.size } }));
    setAgentStatus(s => ({ ...s, [agentId]: "uploaded" }));
  };

  const runAnalysis = () => {
    if (processing) return;
    setProcessing(true);
    const agents = [...new Set(Object.values(files).map(f => f.agentId))];
    let i = 0;
    const tick = setInterval(() => {
      if (i >= agents.length) {
        clearInterval(tick);
        setProcessing(false);
        setProcessed(true);
        return;
      }
      const id = agents[i];
      setAgentStatus(s => ({ ...s, [id]: "processing" }));
      setTimeout(() => {
        const out = MOCK_AGENT_OUTPUTS[id];
        setAgentStatus(s => ({ ...s, [id]: out?.status || "healthy" }));
      }, 800);
      i++;
    }, 900);
  };

  return { files, agentStatus, processing, processed, handleFile, runAnalysis };
}


