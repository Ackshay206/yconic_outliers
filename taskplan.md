# DEADPOOL — Frontend ↔ Backend Integration Task Plan

## Problem Statement

The frontend and backend are **disconnected** — the hook (`useDeadpool.js`) expects `data.score` and `data.top_cascades[].nodes` but the backend actually returns `data.riskScore` and `data.nodes`. The UI also needs:
- "Flaws" renamed to **Liabilities** with agent attribution
- A new **Cascade Chain** tab using React Flow
- **Real-time streaming** via the existing SSE endpoint

---

## Backend Response Contract (Verified from `/api/head-agent/analyze`)

```json
{
  "riskScore": 57.9,          ← top-level (NOT "score")
  "trend": "stable",
  "activeCascades": 21,
  "severityLevel": "high",
  "timestamp": "...",
  "briefing": {
    "summary": "...",
    "timeline": "...",
    "recommended_action": "..."
  },
  "nodes": [                  ← flat list of ALL liability nodes
    {
      "id": "bus_factor_of_1...",
      "domain": "code_audit",         ← maps to DOMAIN_COLORS
      "status": "OCCURRED",
      "title": "Bus Factor of 1...",
      "subtitle": "Code quality & security",
      "description": "A single developer...",
      "agentName": "Code Audit Agent", ← show this in UI
      "evidence": "developer_name: ...",
      "cascadeProbability": 0.92,      ← use as severity [0-1]
      "position": { "x": 0, "y": 100 }
    }
  ],
  "edges": [],                ← React Flow edges (may be empty)
  "activeChains": [           ← cascade chain groupings
    {
      "label": "Cascade #1 — Code Audit",
      "chain": ["Bus Factor of 1 for Repo 'Reghunaath/brainrot'"],
      "domains": ["code_audit"],
      "prob": 0.92
    }
  ]
}
```

---

## Phase 1 — Fix Data Contract (`useDeadpool.js`)

**File:** `frontend/hooks/useDeadpool.js`

### Changes:
1. `data.score` → `data.riskScore`
2. `data.top_cascades[].nodes` → `data.nodes` (flat array)
3. Map node fields:
   - `node.domain` → `agentId`
   - `node.agentName` → `agentName` (new field to pass)
   - `node.title` → `type`
   - `node.description` → `desc`
   - `node.cascadeProbability` → `severity`
   - `node.subtitle` → `subtitle`
   - `node.evidence` → `evidence`
4. Add new state: `activeChains`, `cascadeNodes`, `cascadeEdges`, `severityLevel`, `trend`
5. Agent statuses: derive from `node.domain` + `node.cascadeProbability`

### SSE Streaming (real-time liability updates):
- On `runAnalysis()`, open `EventSource` to `GET /api/sse/updates`
- Listen for `anomaly` events → immediately add to liabilities list
- Listen for `risk_score` events → update risk score in real-time
- When the POST `/api/head-agent/analyze` resolves → close SSE, merge final state
- The SSE streams data from `signal_bus` as each specialist agent finishes

```
Timeline:
  t=0s    User clicks "Run Analysis"
  t=0s    SSE connection opens + POST /analyze sent
  t=5s    People agent done → SSE fires anomaly events → UI shows people liabilities
  t=8s    Finance agent done → SSE fires → UI shows finance liabilities
  t=...   All 6 agents done → head agent + cascade mapper run
  t=~30s  POST resolves → cascade chains rendered, SSE closed
```

---

## Phase 2 — Rename Flaws → Liabilities + Agent Attribution

**File:** `frontend/components/FlawsPanel.jsx`

### Changes:
1. Title: `"Flaws Detected"` → `"Liabilities Detected"`
2. Each card shows:
   - Domain color pill (from `DOMAIN_COLORS`)
   - Agent name badge (e.g., "Code Audit Agent")
   - Severity badge (critical/high/medium based on `cascadeProbability`)
   - Title + subtitle
   - Description (truncated, expandable)
   - Evidence (collapsed by default)

---

## Phase 3 — Cascade Chain Visualization

**Library:** `@xyflow/react` (React Flow v12)

**File:** `frontend/components/CascadeChainPanel.jsx`

### Layout Strategy:
- Each `activeChain` becomes a **row** of connected nodes
- Nodes within a chain flow **left → right**
- Chains stacked **vertically** with spacing
- Chain header shows: label + overall probability badge
- Node color = `DOMAIN_COLORS[domain]`
- Animated edges between connected nodes
- Mini-map + zoom controls
- "Fit View" button on load

### Data Transformation:
```javascript
// Build React Flow nodes + edges from activeChains + nodes
function buildFlowGraph(activeChains, allNodes) {
  const nodeMap = new Map(allNodes.map(n => [n.title, n]));
  const rfNodes = [], rfEdges = [];
  let yOffset = 0;

  activeChains.forEach((chain, chainIdx) => {
    chain.chain.forEach((title, nodeIdx) => {
      const meta = nodeMap.get(title);
      rfNodes.push({
        id: `${chainIdx}_${nodeIdx}`,
        type: 'cascadeNode',
        position: { x: nodeIdx * 360, y: yOffset },
        data: { title, meta, domain: chain.domains[nodeIdx] ?? chain.domains[0], prob: chain.prob, chainLabel: chain.label },
      });
      if (nodeIdx > 0) {
        rfEdges.push({
          id: `e_${chainIdx}_${nodeIdx}`,
          source: `${chainIdx}_${nodeIdx - 1}`,
          target: `${chainIdx}_${nodeIdx}`,
          animated: true,
          style: { stroke: '#FF2020', strokeWidth: 2 },
        });
      }
    });
    yOffset += 200;
  });

  return { rfNodes, rfEdges };
}
```

---

## Phase 4 — Tab Navigation

**File:** `frontend/App.jsx`

### Changes:
- Right column gets a **tab bar** at the top: `[ Liabilities (N) | Cascade Chains (N) ]`
- Active tab shows the corresponding panel
- Tab counts update as data streams in

---

## Phase 5 — Enhanced Risk Index

**File:** `frontend/components/RiskIndex.jsx`

### Changes:
- Show `riskScore` as large number
- Show `severityLevel` badge (low/medium/high/critical)
- Show `trend` arrow (↑ increasing / → stable / ↓ decreasing)
- Show `activeCascades` count

---

## File Change Summary

| File | Change Type | Priority |
|------|-------------|----------|
| `hooks/useDeadpool.js` | Fix data mapping + SSE streaming | Critical |
| `components/FlawsPanel.jsx` | Rename + agent attribution | High |
| `components/CascadeChainPanel.jsx` | New file — React Flow | High |
| `components/RiskIndex.jsx` | Add severity + trend display | Medium |
| `App.jsx` | Add tab navigation | High |
| `package.json` | Add @xyflow/react | High |

---

## Testing Checklist

- [ ] `POST /api/head-agent/analyze` response fields map correctly (no undefined values)
- [ ] Risk score displays as number (not `NaN` or `undefined`)
- [ ] Briefing shows summary, timeline, recommended_action
- [ ] Liabilities list populates with correct agentName attribution
- [ ] Domain colors match agent domain in each liability card
- [ ] SSE streams anomalies in real-time before POST completes
- [ ] Cascade Chain tab renders React Flow graph with colored nodes
- [ ] Edges animate when present
- [ ] Tabs switch correctly without remounting
- [ ] Agent panel statuses update (critical/warning/healthy) after analysis
