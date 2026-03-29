// ─── utils/formatters.js ──────────────────────────────────────────────────────
export function formatFileSize(bytes) {
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export function severityLabel(sev) {
  if (sev >= 0.7) return "HIGH";
  if (sev >= 0.5) return "MED";
  return "LOW";
}

export function severityColor(sev) {
  if (sev >= 0.7) return "#ef4444";
  if (sev >= 0.5) return "#f59e0b";
  return "#10b981";
}

export function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
