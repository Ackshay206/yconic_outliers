// ─── hooks/useDeadpool.js ──────────────────────────────────────────────────────
import { useState, useCallback } from "react";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const AGENT_NAMES = ["people", "finance", "infra", "product", "legal", "code_audit"];
const INITIAL_STATUSES = Object.fromEntries(AGENT_NAMES.map(n => [n, "idle"]));

function toSeverityStatus(prob) {
  if (prob >= 0.75) return "critical";
  if (prob >= 0.5)  return "warning";
  return "healthy";
}

function nodeToLiability(node) {
  return {
    agentId:   node.domain             ?? "unknown",
    agentName: node.agentName          ?? node.domain ?? "Unknown Agent",
    type:      node.title              ?? "Unknown Risk",
    subtitle:  node.subtitle           ?? "",
    severity:  node.cascadeProbability ?? 0,
    desc:      node.description        ?? "",
    evidence:  node.evidence           ?? "",
    status:    node.status             ?? "OCCURRED",
    nodeId:    node.id                 ?? "",
  };
}

export function useDeadpool() {
  const [agentStatuses, setAgentStatuses] = useState(INITIAL_STATUSES);
  const [liabilities,   setLiabilities]   = useState([]);
  const [cascadeChains, setCascadeChains] = useState([]);
  const [cascadeNodes,  setCascadeNodes]  = useState([]);
  const [cascadeEdges,  setCascadeEdges]  = useState([]);
  const [riskScore,     setRiskScore]     = useState(null);
  const [severityLevel, setSeverityLevel] = useState(null);
  const [trend,         setTrend]         = useState(null);
  const [briefing,      setBriefing]      = useState(null);
  const [running,       setRunning]       = useState(false);
  const [done,          setDone]          = useState(false);
  const [error,         setError]         = useState(null);

  const runAnalysis = useCallback(async () => {
    if (running) return;

    setRunning(true);
    setDone(false);
    setError(null);
    setLiabilities([]);
    setCascadeChains([]);
    setCascadeNodes([]);
    setCascadeEdges([]);
    setRiskScore(null);
    setSeverityLevel(null);
    setTrend(null);
    setBriefing(null);
    setAgentStatuses(Object.fromEntries(AGENT_NAMES.map(n => [n, "processing"])));

    try {
      const res = await fetch(`${BASE}/api/head-agent/analyze`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setRiskScore(data.riskScore ?? null);
      setSeverityLevel(data.severityLevel ?? null);
      setTrend(data.trend ?? null);
      setBriefing(data.briefing ?? null);

      if (Array.isArray(data.nodes) && data.nodes.length > 0) {
        const items = data.nodes
          .map(nodeToLiability)
          .sort((a, b) => b.severity - a.severity);
        setLiabilities(items);
      }

      setCascadeChains(data.activeChains ?? []);
      setCascadeNodes(data.nodes ?? []);
      setCascadeEdges(data.edges ?? []);

      const domainMaxProb = {};
      (data.nodes ?? []).forEach(node => {
        const d = node.domain;
        if (!d) return;
        if (!domainMaxProb[d] || node.cascadeProbability > domainMaxProb[d]) {
          domainMaxProb[d] = node.cascadeProbability ?? 0;
        }
      });

      setAgentStatuses(
        Object.fromEntries(
          AGENT_NAMES.map(n => [n, toSeverityStatus(domainMaxProb[n] ?? 0)])
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

  return {
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
  };
}
