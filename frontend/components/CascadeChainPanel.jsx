// ─── components/CascadeChainPanel.jsx ─────────────────────────────────────────
// Full-page cascade chain visualization using @xyflow/react.
//
// Layout: nodes are arranged in a horizontal grid (COLS per row).
// Within each activeChain that has multiple nodes, nodes stay in the same row
// connected left→right. Single-node chains fill grid slots.
// Adjacent grid nodes are connected by animated arrows to show cascade flow.

import { useEffect, useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  useReactFlow,
  ReactFlowProvider,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { DOMAIN_COLORS } from "../constants/agents";

// ── Layout constants ──────────────────────────────────────────────────────────
const NODE_W  = 260;
const NODE_H  = 130;
const X_GAP   = 70;
const Y_GAP   = 56;

// ── Helpers ───────────────────────────────────────────────────────────────────
function severityLabel(p) {
  if (p >= 0.75) return "CRITICAL";
  if (p >= 0.5)  return "HIGH";
  return "MEDIUM";
}
function severityColor(p) {
  if (p >= 0.75) return "#FF2020";
  if (p >= 0.5)  return "#F59E0B";
  return "#888888";
}

// ── Custom node component ─────────────────────────────────────────────────────
function CascadeNodeComponent({ data }) {
  const { title, agentName, domain, prob, description } = data;
  const domainColor = DOMAIN_COLORS[domain] ?? "#888888";
  const sevLabel    = severityLabel(prob);
  const sevColor    = severityColor(prob);

  return (
    <div style={{
      width: NODE_W,
      background: "#0E0E0E",
      border: `1px solid ${domainColor}44`,
      borderLeft: `3px solid ${domainColor}`,
      borderRadius: 8,
      padding: "10px 13px",
      boxShadow: `0 0 24px ${domainColor}18`,
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* Agent + severity */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 7 }}>
        <span style={{
          display: "inline-flex", alignItems: "center", gap: 5,
          fontSize: 9, fontWeight: 700, textTransform: "uppercase",
          letterSpacing: "0.06em", color: domainColor,
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: "50%",
            background: domainColor, boxShadow: `0 0 5px ${domainColor}`,
          }} />
          {agentName}
        </span>
        <span style={{
          fontSize: 8, fontWeight: 900, textTransform: "uppercase", letterSpacing: "0.08em",
          padding: "2px 5px", borderRadius: 3,
          background: `${sevColor}20`, color: sevColor,
          border: `1px solid ${sevColor}44`,
        }}>
          {sevLabel}
        </span>
      </div>

      {/* Title */}
      <div style={{
        fontSize: 11, fontWeight: 700, color: "#FFFFFF",
        lineHeight: 1.35, marginBottom: description ? 5 : 10,
        display: "-webkit-box", WebkitLineClamp: 2,
        WebkitBoxOrient: "vertical", overflow: "hidden",
      }}>
        {title}
      </div>

      {/* Description */}
      {description && (
        <div style={{
          fontSize: 9, color: "#666666", fontStyle: "italic", lineHeight: 1.4,
          marginBottom: 8,
          display: "-webkit-box", WebkitLineClamp: 2,
          WebkitBoxOrient: "vertical", overflow: "hidden",
        }}>
          {description}
        </div>
      )}

      {/* Probability bar */}
      <div style={{ height: 2, borderRadius: 1, background: "#1A1A1A", overflow: "hidden" }}>
        <div style={{
          width: `${Math.round(prob * 100)}%`, height: "100%",
          background: `linear-gradient(90deg, ${domainColor}, ${domainColor}66)`,
        }} />
      </div>
      <div style={{ marginTop: 3, fontSize: 8, color: "#444", fontWeight: 700 }}>
        CASCADE {Math.round(prob * 100)}%
      </div>

      <Handle type="target" position={Position.Left}
        style={{ background: domainColor, width: 8, height: 8, border: "2px solid #0E0E0E" }} />
      <Handle type="source" position={Position.Right}
        style={{ background: domainColor, width: 8, height: 8, border: "2px solid #0E0E0E" }} />
    </div>
  );
}

const NODE_TYPES = { cascadeNode: CascadeNodeComponent };

// ── Build React Flow graph ────────────────────────────────────────────────────
// Strategy:
//   - Multi-node chains: place nodes in a single row, connected left→right.
//   - Single-node chains: pack them into a grid (COLS wide), connected
//     left→right within each grid row to show cascade flow sequence.
function buildFlowGraph(activeChains, allNodes) {
  const metaByTitle = new Map(allNodes.map(n => [n.title, n]));
  const rfNodes = [];
  const rfEdges = [];

  // Separate multi-node chains from single-node chains
  const multiChains  = activeChains.filter(c => (c.chain?.length ?? 0) > 1);
  const singleChains = activeChains.filter(c => (c.chain?.length ?? 0) <= 1);

  let yOffset = 0;

  // ── Render multi-node chains as dedicated horizontal rows ──────────────────
  multiChains.forEach((chain, ci) => {
    const titles  = chain.chain ?? [];
    const domains = chain.domains ?? [];

    titles.forEach((title, ni) => {
      const meta   = metaByTitle.get(title) ?? {};
      const domain = domains[ni] ?? domains[0] ?? meta.domain ?? "unknown";
      const color  = DOMAIN_COLORS[domain] ?? "#888888";
      const id     = `multi_${ci}_${ni}`;

      rfNodes.push({
        id,
        type: "cascadeNode",
        position: { x: ni * (NODE_W + X_GAP), y: yOffset },
        data: {
          title, agentName: meta.agentName ?? domain, domain,
          prob: meta.cascadeProbability ?? chain.prob ?? 0,
          description: meta.description ?? "",
        },
      });

      if (ni > 0) {
        const prevDomain = domains[ni - 1] ?? domains[0];
        const edgeColor  = DOMAIN_COLORS[prevDomain] ?? "#888888";
        rfEdges.push({
          id: `e_multi_${ci}_${ni}`,
          source: `multi_${ci}_${ni - 1}`,
          target: id,
          animated: true,
          style: { stroke: edgeColor, strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: edgeColor, width: 14, height: 14 },
        });
      }
    });

    yOffset += NODE_H + Y_GAP;
  });

  // ── Single-node chains: one long horizontal row, all connected left→right ───
  if (singleChains.length > 0) {
    if (yOffset > 0) yOffset += Y_GAP;

    singleChains.forEach((chain, si) => {
      const title  = chain.chain?.[0] ?? chain.label;
      const domain = chain.domains?.[0] ?? "unknown";
      const meta   = metaByTitle.get(title) ?? {};
      const id     = `single_${si}`;

      rfNodes.push({
        id,
        type: "cascadeNode",
        position: { x: si * (NODE_W + X_GAP), y: yOffset },
        data: {
          title, agentName: meta.agentName ?? domain, domain,
          prob: meta.cascadeProbability ?? chain.prob ?? 0,
          description: meta.description ?? "",
        },
      });

      if (si > 0) {
        const prevDomain = singleChains[si - 1]?.domains?.[0] ?? "unknown";
        const edgeColor  = DOMAIN_COLORS[prevDomain] ?? "#888888";
        rfEdges.push({
          id: `e_single_${si}`,
          source: `single_${si - 1}`,
          target: id,
          animated: true,
          style: { stroke: edgeColor, strokeWidth: 1.5, strokeDasharray: "6 3" },
          markerEnd: { type: MarkerType.ArrowClosed, color: edgeColor, width: 12, height: 12 },
        });
      }
    });
  }

  return { rfNodes, rfEdges };
}

// ── Empty state ───────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <div style={{
      height: "100%", display: "flex", flexDirection: "column",
      justifyContent: "center", alignItems: "center", gap: 16,
      color: "#555555", textAlign: "center",
    }}>
      <span className="material-icons" style={{ fontSize: 52, color: "rgba(255,32,32,0.3)" }}>
        account_tree
      </span>
      <div>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#888888", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
          No Active Cascades
        </div>
        <div style={{ fontSize: 12, color: "#555555", maxWidth: 280 }}>
          Run the analysis to map risk cascade chains across all operational domains.
        </div>
      </div>
    </div>
  );
}

// ── Inner canvas (needs ReactFlowProvider above it) ───────────────────────────
function FlowCanvas({ rfNodes: initNodes, rfEdges: initEdges }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges);
  const { fitView } = useReactFlow();

  useEffect(() => {
    setNodes(initNodes);
    setEdges(initEdges);
    const t = setTimeout(() => fitView({ padding: 0.12, duration: 500 }), 60);
    return () => clearTimeout(t);
  }, [initNodes, initEdges, setNodes, setEdges, fitView]);

  const onInit = useCallback(
    () => fitView({ padding: 0.12, duration: 500 }),
    [fitView]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={NODE_TYPES}
      onInit={onInit}
      fitView
      proOptions={{ hideAttribution: true }}
      style={{ background: "#080808" }}
      minZoom={0.1}
      maxZoom={2}
    >
      <Background color="#161616" gap={28} size={1} />
      <Controls
        style={{ background: "#111111", border: "1px solid #3D0000", borderRadius: 6 }}
        showInteractive={false}
      />
      <MiniMap
        style={{ background: "#111111", border: "1px solid #3D0000" }}
        nodeColor={n => DOMAIN_COLORS[n.data?.domain] ?? "#444"}
        maskColor="rgba(0,0,0,0.75)"
      />
    </ReactFlow>
  );
}

// ── Public component ──────────────────────────────────────────────────────────
export default function CascadeChainPanel({ cascadeChains, cascadeNodes }) {
  const chains = cascadeChains ?? [];
  const nodes  = cascadeNodes  ?? [];

  const { rfNodes, rfEdges } = useMemo(
    () => buildFlowGraph(chains, nodes),
    [chains, nodes]
  );

  const hasData = chains.length > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", padding: "20px 24px", background: "#0A0A0A" }}>
      {/* Header row */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
          <div style={{
            fontSize: 22, fontWeight: 900, fontStyle: "italic", textTransform: "uppercase",
            letterSpacing: "-0.5px",
            background: "linear-gradient(90deg, #FF2020, #7A0000)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>
            Active Cascade Chains
          </div>
          {chains.length > 0 && (
            <span style={{
              fontSize: 11, fontWeight: 700, color: "#FF2020",
              background: "rgba(255,32,32,0.1)", border: "1px solid rgba(255,32,32,0.3)",
              borderRadius: 10, padding: "1px 8px",
            }}>
              {chains.length} chains · {nodes.length} nodes
            </span>
          )}
        </div>

        {/* Domain legend */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "flex-end" }}>
          {Object.entries(DOMAIN_COLORS).map(([domain, color]) => (
            <span key={domain} style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              fontSize: 9, fontWeight: 700, textTransform: "uppercase",
              letterSpacing: "0.05em", color: "#666666",
            }}>
              <span style={{ width: 8, height: 8, borderRadius: 2, background: color, flexShrink: 0 }} />
              {domain.replace("_", " ")}
            </span>
          ))}
        </div>
      </div>

      {/* Canvas */}
      <div style={{
        flex: 1, minHeight: 0,
        border: "1px solid #3D0000",
        borderRadius: 12,
        overflow: "hidden",
      }}>
        {!hasData ? (
          <EmptyState />
        ) : (
          <ReactFlowProvider>
            <FlowCanvas rfNodes={rfNodes} rfEdges={rfEdges} />
          </ReactFlowProvider>
        )}
      </div>

      {/* React Flow style overrides */}
      <style>{`
        .react-flow__controls-button {
          background: #111111 !important; border-color: #3D0000 !important;
          color: #888888 !important; fill: #888888 !important;
        }
        .react-flow__controls-button:hover {
          background: #1A1A1A !important; color: #FFFFFF !important; fill: #FFFFFF !important;
        }
        .react-flow__minimap-mask { fill: rgba(0,0,0,0.75); }
        .react-flow__edge-path { stroke-linecap: round; }
      `}</style>
    </div>
  );
}
