import React, { useMemo, useCallback } from "react";
import { ReactFlow, Controls, Background } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CASCADE_MOCK_DATA } from "../../constants/cascade";
import { CascadeFlowNode } from "./CascadeFlowNode";
import { CascadeFlowEdge } from "./CascadeFlowEdge";

const nodeTypes = { cascadeNode: CascadeFlowNode };
const edgeTypes = { cascadeEdge: CascadeFlowEdge };

export function CascadeGraph({ onNodeClick, onPaneClick }) {
  const nodes = useMemo(
    () =>
      CASCADE_MOCK_DATA.nodes.map((n) => ({
        id: n.id,
        type: "cascadeNode",
        position: n.position,
        data: {
          domain: n.domain,
          status: n.status,
          title: n.title,
          subtitle: n.subtitle,
          description: n.description,
          agentName: n.agentName,
          evidence: n.evidence,
          cascadeProbability: n.cascadeProbability,
        },
      })),
    []
  );

  const edges = useMemo(
    () =>
      CASCADE_MOCK_DATA.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        type: "cascadeEdge",
        data: { severity: e.severity },
      })),
    []
  );

  const handleNodeClick = useCallback(
    (_event, node) => {
      const sourceNode = CASCADE_MOCK_DATA.nodes.find((n) => n.id === node.id);
      if (sourceNode && onNodeClick) onNodeClick(sourceNode);
    },
    [onNodeClick]
  );

  const handlePaneClick = useCallback(() => {
    if (onPaneClick) onPaneClick();
  }, [onPaneClick]);

  return (
    <div style={{ width: "100%", height: "100%", background: "#111111", overflow: "hidden" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.3}
        maxZoom={1.5}
        style={{ background: "#111111" }}
      >
        <Background color="#1a1a1a" gap={24} size={1} />
        <Controls
          style={{
            background: "#1a1a1a",
            border: "1px solid #2a2a2a",
            borderRadius: 6,
          }}
        />
      </ReactFlow>
    </div>
  );
}
