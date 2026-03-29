import React from "react";
import { RiskMetricsBar } from "./RiskMetricsBar";
import { GraphLegend } from "./GraphLegend";
import { CascadeGraph } from "./CascadeGraph";
import { CascadeChainList } from "./CascadeChainList";
import { HARDCODED_CASCADE } from "../../constants/cascade";

export default function CascadeTab() {
  const { riskScore, trend, activeCascades } = HARDCODED_CASCADE;
  return (
    <div>
      <RiskMetricsBar riskScore={riskScore} activeCascades={activeCascades} trend={trend} />
      <GraphLegend />
      <CascadeGraph />
      <CascadeChainList />
    </div>
  );
}