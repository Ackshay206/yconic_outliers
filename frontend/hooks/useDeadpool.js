// ─── hooks/useDeadpool.js ──────────────────────────────────────────────────────
import { useState, useCallback, useRef } from "react";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const AGENT_NAMES = ["people", "finance", "infra", "product", "legal", "code_audit"];
const INITIAL_STATUSES = Object.fromEntries(AGENT_NAMES.map(n => [n, "idle"]));

// Maps a cascadeProbability [0-1] to a severity category
function toSeverityStatus(prob) {
  if (prob >= 0.75) return "critical";
  if (prob >= 0.5)  return "warning";
  return "healthy";
}

// Converts a backend node object into a normalised liability item for the UI
function nodeToLiability(node) {
  return {
    agentId:   node.domain      ?? "unknown",
    agentName: node.agentName   ?? node.domain ?? "Unknown Agent",
    type:      node.title       ?? "Unknown Risk",
    subtitle:  node.subtitle    ?? "",
    severity:  node.cascadeProbability ?? 0,
    desc:      node.description ?? "",
    evidence:  node.evidence    ?? "",
    status:    node.status      ?? "OCCURRED",
    nodeId:    node.id          ?? "",
  };
}

export function useDeadpool() {
  const [agentStatuses, setAgentStatuses] = useState(INITIAL_STATUSES);
  const [liabilities,   setLiabilities]   = useState([]);      // was "anomalies"
  const [cascadeChains, setCascadeChains] = useState([]);      // activeChains array
  const [cascadeNodes,  setCascadeNodes]  = useState([]);      // nodes array (for RF)
  const [cascadeEdges,  setCascadeEdges]  = useState([]);      // edges array (for RF)
  const [riskScore,     setRiskScore]     = useState(null);
  const [severityLevel, setSeverityLevel] = useState(null);
  const [trend,         setTrend]         = useState(null);
  const [briefing,      setBriefing]      = useState(null);
  const [running,       setRunning]       = useState(false);
  const [done,          setDone]          = useState(false);
  const [error,         setError]         = useState(null);

  // Ref to the active SSE connection so we can close it on completion
  const sseRef = useRef(null);

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

    // ── 1. Open SSE for real-time liability streaming ─────────────────────────
    //
    // The backend publishes anomalies to signal_bus as each specialist agent
    // finishes.  The SSE endpoint streams those events so liabilities appear in
    // the UI incrementally — before the full POST resolves.
    //
    const seenNodeIds = new Set();

    try {
      const es = new EventSource(`${BASE}/api/sse/updates`);
      sseRef.current = es;

      es.addEventListener("anomaly", (evt) => {
        try {
          const anomaly = JSON.parse(evt.data);
          // Guard: only add each unique anomaly once
          if (seenNodeIds.has(anomaly.id)) return;
          seenNodeIds.add(anomaly.id);

          const item = {
            agentId:   anomaly.agent_domain ?? "unknown",
            agentName: anomaly.agent_domain
              ? anomaly.agent_domain.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase()) + " Agent"
              : "Unknown Agent",
            type:      anomaly.title       ?? "Unknown Risk",
            subtitle:  anomaly.description ?? "",
            severity:  anomaly.severity    ?? 0,
            desc:      anomaly.description ?? "",
            evidence:  JSON.stringify(anomaly.evidence ?? {}),
            status:    "OCCURRED",
            nodeId:    anomaly.id ?? "",
          };

          setLiabilities(prev =>
            [...prev, item].sort((a, b) => b.severity - a.severity)
          );

          // Update agent status immediately when we receive its anomaly
          setAgentStatuses(prev => {
            const cur = prev[item.agentId] ?? "processing";
            const next = toSeverityStatus(item.severity);
            // Only escalate, never downgrade while running
            const order = { processing: 0, healthy: 1, warning: 2, critical: 3 };
            return {
              ...prev,
              [item.agentId]: order[next] > order[cur] ? next : cur,
            };
          });
        } catch (_) { /* ignore malformed events */ }
      });

      es.addEventListener("risk_score", (evt) => {
        try {
          const rs = JSON.parse(evt.data);
          if (rs.score != null) setRiskScore(rs.score);
          if (rs.severity_level) setSeverityLevel(rs.severity_level);
          if (rs.trend)          setTrend(rs.trend);
        } catch (_) { /* ignore */ }
      });

      es.onerror = () => {
        // Non-fatal: SSE disconnects are expected once analysis finishes
        es.close();
        sseRef.current = null;
      };
    } catch (sseErr) {
      // SSE not available — proceed with POST-only mode
      console.warn("[DEADPOOL] SSE unavailable, falling back to POST-only mode:", sseErr);
    }

    // ── 2. POST /api/head-agent/analyze — authoritative final response ─────────
    try {
      const res = await fetch(`${BASE}/api/head-agent/analyze`, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // ── Risk score
      // Backend returns { riskScore, severityLevel, trend } (NOT { score })
      setRiskScore(data.riskScore ?? null);
      setSeverityLevel(data.severityLevel ?? null);
      setTrend(data.trend ?? null);

      // ── Briefing
      setBriefing(data.briefing ?? null);

      // ── Liabilities — authoritative list from data.nodes
      // data.nodes is a flat array of all liability nodes across all cascades.
      if (Array.isArray(data.nodes) && data.nodes.length > 0) {
        const items = data.nodes
          .map(nodeToLiability)
          .sort((a, b) => b.severity - a.severity);
        setLiabilities(items);
      }

      // ── Cascade chain data for the Cascade Chains tab
      setCascadeChains(data.activeChains ?? []);
      setCascadeNodes(data.nodes ?? []);
      setCascadeEdges(data.edges ?? []);

      // ── Agent statuses — final authoritative values
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
      // Close SSE now that the authoritative response has arrived
      if (sseRef.current) {
        sseRef.current.close();
        sseRef.current = null;
      }
      setRunning(false);
      setDone(true);
    }
  }, [running]);

  return {
    agentStatuses,
    liabilities,      // renamed from "anomalies"
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
