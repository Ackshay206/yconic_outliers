import React, { useState } from "react";
import { CascadeRiskPanel } from "./CascadeRiskPanel";
import { CascadeGraph } from "./CascadeGraph";
import { CascadeDetailPanel } from "./CascadeDetailPanel";
import { CascadeChainList } from "./CascadeChainList";
import { CASCADE_MOCK_DATA } from "../../constants/cascade";

export default function CascadeTab() {
  const { riskScore, trend, activeCascades } = CASCADE_MOCK_DATA;
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 120px)" }}>
      {/* Section header */}
      <div style={{ marginBottom: 16 }}>
        <h2 style={{
          fontSize: 22,
          fontWeight: 800,
          fontStyle: "italic",
          color: "#dc2626",
          textTransform: "uppercase",
          letterSpacing: 2,
          margin: 0,
        }}>
          Risk Forecast
        </h2>
      </div>

      {/* Top: three-panel layout */}
      <div style={{ display: "flex", flex: 1, minHeight: 0, border: "1px solid #2a1a1a", borderRadius: 8, overflow: "hidden", background: "#111111" }}>
        {/* Left: Risk Panel */}
        <CascadeRiskPanel riskScore={riskScore} trend={trend} activeCascades={activeCascades} />

        {/* Center: Graph */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <CascadeGraph
            onNodeClick={(node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
          />
        </div>

        {/* Right: Detail Panel (conditional) */}
        {selectedNode && (
          <CascadeDetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />
        )}
      </div>

      {/* Bottom: Chain List */}
      <div style={{ marginTop: 20 }}>
        <CascadeChainList />
      </div>
    </div>
  );
}
