// ─── utils/formatters.js ──────────────────────────────────────────────────────
export function formatFileSize(bytes) {
  if (typeof bytes !== "number" || !isFinite(bytes) || bytes < 0) return "0.0 KB";
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function severityLabel(sev) {
  if (typeof sev !== "number" || !isFinite(sev)) return "LOW";
  if (sev >= 0.7) return "HIGH";
  if (sev >= 0.5) return "MED";
  return "LOW";
}

export function severityColor(sev) {
  if (typeof sev !== "number" || !isFinite(sev)) return "#10b981";
  if (sev >= 0.7) return "#ef4444";
  if (sev >= 0.5) return "#f59e0b";
  return "#10b981";
}

export function capitalize(str) {
  if (typeof str !== "string" || str.length === 0) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}
