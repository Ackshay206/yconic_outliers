import React from "react";
import { FILE_SLOTS } from "../../constants/fileSlots";
import { FileSlot } from "./FileSlot";


// ─── FileUploadPanel ──────────────────────────────────────────────────────────
export function FileUploadPanel({ files, processing, processed, onFile, onRun }) {
  const count = Object.keys(files).length;
  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Upload Startup Data</div>
        <div style={{ fontSize: 12, color: "#64748b" }}>Upload data files for each monitoring agent. Supported: CSV, JSON, PDF</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {FILE_SLOTS.map(slot => (
          <FileSlot key={slot.id} slot={slot} uploaded={files[slot.id]} onFile={onFile} />
        ))}
      </div>
      <button onClick={onRun} disabled={count === 0 || processing} style={{
        marginTop: 16, width: "100%", padding: 14, borderRadius: 8, border: "none",
        background: count > 0 ? "linear-gradient(135deg,#6366f1,#8b5cf6)" : "#1e293b",
        color: count > 0 ? "#fff" : "#475569",
        fontWeight: 700, fontSize: 14, cursor: count > 0 ? "pointer" : "not-allowed",
        letterSpacing: 1, transition: "all 0.2s",
      }}>
        {processing ? "⚡ Running Agents…" : processed ? "✓ Re-Run Analysis" : `⚡ Run DEADPOOL Analysis (${count} file${count !== 1 ? "s" : ""})`}
      </button>
    </div>
  );
}