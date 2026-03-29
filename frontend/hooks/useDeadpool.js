// ─── hooks/useDeadpool.js ──────────────────────────────────────────────────────
import { useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const AGENT_NAMES = ["people", "finance", "infra", "product", "legal", "code_audit"];
const INITIAL_STATUSES = Object.fromEntries(AGENT_NAMES.map(n => [n, "idle"]));

export function useDeadpool() {
  const [agentStatuses, setAgentStatuses] = useState(INITIAL_STATUSES);
  const [anomalies, setAnomalies]         = useState([]);
  const [cascadeSteps, setCascadeSteps]   = useState([]);
  const [riskScore, setRiskScore]         = useState(null);
  const [briefing, setBriefing]           = useState(null);
  const [running, setRunning]             = useState(false);
  const [done, setDone]                   = useState(false);
  const [error, setError]                 = useState(null);

  const runAnalysis = useCallback(async () => {
    if (running) return;

    setRunning(true);
    setDone(false);
    setError(null);
    setAnomalies([]);
    setCascadeSteps([]);
    setRiskScore(null);
    setBriefing(null);
    setAgentStatuses(Object.fromEntries(AGENT_NAMES.map(n => [n, "processing"])));

    try {
      const res = await fetch(`${BASE}/api/head-agent/analyze`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Risk score + briefing
      setRiskScore(data.score ?? null);
      setBriefing(data.briefing ?? null);

      // Cascade steps from top cascade chain (CascadeChain.nodes, CascadeNode.title)
      const topCascade = data.top_cascades?.[0];
      if (topCascade?.nodes?.length) {
        setCascadeSteps(
          topCascade.nodes.slice(0, 5).map((node, i) => ({
            number: String(i + 1).padStart(2, "0"),
            label: node.title,
          }))
        );
      }

      // Flaws from all cascade nodes across all top cascades
      const allNodes = (data.top_cascades || []).flatMap(c => c.nodes || []);
      const flaws = allNodes
        .map(node => ({
          agentId: node.agent_domain,
          type: node.title,
          severity: node.severity,
          entity: node.agent_domain,
          desc: node.evidence || "",
        }))
        .sort((a, b) => b.severity - a.severity);
      setAnomalies(flaws);

      // Agent statuses derived from cascade node severities per domain
      const domainSeverities = {};
      allNodes.forEach(node => {
        const d = node.agent_domain;
        if (!domainSeverities[d] || node.severity > domainSeverities[d]) {
          domainSeverities[d] = node.severity;
        }
      });

      setAgentStatuses(
        Object.fromEntries(
          AGENT_NAMES.map(n => {
            const sev = domainSeverities[n] ?? 0;
            if (sev >= 0.75) return [n, "critical"];
            if (sev >= 0.5)  return [n, "warning"];
            return [n, "healthy"];
          })
        )
      );

    } catch (err) {
      console.error("[DEADPOOL] Analysis failed:", err);
      setError(err.message || "Analysis failed");
      setAgentStatuses(Object.fromEntries(AGENT_NAMES.map(n => [n, "idle"])));
    } finally {
      setRunning(false);
      setDone(true);
    }
  }, [running]);

  return { agentStatuses, anomalies, cascadeSteps, riskScore, briefing, running, done, error, runAnalysis };
}
