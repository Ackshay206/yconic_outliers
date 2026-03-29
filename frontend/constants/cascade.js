// ─── cascade.js ──────────────────────────────────────────────────────────────
import mockData from "./cascadeMockData.json";

export const STATUS_CONFIG = {
  OCCURRED:  { label: "CRITICAL", bg: "#dc262630", color: "#dc2626", border: "#dc262660" },
  LIKELY:    { label: "HIGH",     bg: "#dc262620", color: "#f87171", border: "#f8717140" },
  POSSIBLE:  { label: "MEDIUM",   bg: "#78716c20", color: "#a8a29e", border: "#a8a29e40" },
};

export const CASCADE_MOCK_DATA = mockData;
export const ACTIVE_CHAINS = mockData.activeChains;
