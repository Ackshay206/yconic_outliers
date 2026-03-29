// ─── components/AgentChatPanel.jsx ────────────────────────────────────────────
// Chat interface for all 6 specialist agents with token streaming.

import { useState, useRef, useEffect, useCallback } from "react";
import { AGENTS, DOMAIN_COLORS } from "../constants/agents";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

// ── Agent sidebar card ─────────────────────────────────────────────────────────
function AgentCard({ agent, active, status, onClick }) {
  const color = DOMAIN_COLORS[agent.id] ?? "#888888";
  const isActive = active === agent.id;

  return (
    <button
      onClick={() => onClick(agent.id)}
      style={{
        width: "100%",
        background: isActive ? `${color}14` : "transparent",
        border: "none",
        borderLeft: `3px solid ${isActive ? color : "transparent"}`,
        borderRadius: "0 6px 6px 0",
        padding: "12px 14px",
        cursor: "pointer",
        textAlign: "left",
        transition: "background 0.15s, border-color 0.15s",
        display: "flex",
        alignItems: "center",
        gap: 10,
      }}
      onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
      onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = "transparent"; }}
    >
      {/* Status dot */}
      <span style={{
        width: 7, height: 7, borderRadius: "50%", flexShrink: 0,
        background: status === "critical" ? "#FF2020"
                  : status === "warning"  ? "#F59E0B"
                  : status === "healthy"  ? "#10B981"
                  : color,
        boxShadow: isActive ? `0 0 8px ${color}` : "none",
      }} />

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 11, fontWeight: 700,
          color: isActive ? "#FFFFFF" : "#888888",
          textTransform: "uppercase", letterSpacing: "0.05em",
          transition: "color 0.15s",
        }}>
          {agent.label}
        </div>
        <div style={{
          fontSize: 9, color: "#444444", marginTop: 2,
          overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
        }}>
          {agent.desc}
        </div>
      </div>
    </button>
  );
}

// ── Single chat bubble ─────────────────────────────────────────────────────────
function ChatBubble({ msg, agentColor, agentLabel }) {
  const isUser  = msg.role === "user";
  const isEmpty = !msg.text && msg.streaming;

  return (
    <div style={{
      display: "flex",
      flexDirection: isUser ? "row-reverse" : "row",
      gap: 10,
      marginBottom: 16,
      alignItems: "flex-start",
    }}>
      {/* Avatar */}
      <div style={{
        width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
        background: isUser ? "#1E1E1E" : `${agentColor}22`,
        border: `1px solid ${isUser ? "#2A2A2A" : agentColor + "55"}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 10, fontWeight: 700,
        color: isUser ? "#888888" : agentColor,
      }}>
        {isUser ? "YOU" : "AI"}
      </div>

      {/* Bubble */}
      <div style={{
        maxWidth: "72%",
        background: isUser ? "#1A1A1A" : "#0E0E0E",
        border: `1px solid ${isUser ? "#2A2A2A" : agentColor + "33"}`,
        borderRadius: isUser ? "12px 4px 12px 12px" : "4px 12px 12px 12px",
        padding: "10px 14px",
      }}>
        {!isUser && (
          <div style={{
            fontSize: 8, fontWeight: 700, textTransform: "uppercase",
            letterSpacing: "0.08em", color: agentColor,
            marginBottom: 5,
          }}>
            {agentLabel}
          </div>
        )}
        <div style={{
          fontSize: 12, color: isUser ? "#AAAAAA" : "#CCCCCC",
          lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "break-word",
        }}>
          {msg.text}
          {/* Streaming cursor */}
          {msg.streaming && (
            <span style={{
              display: "inline-block", width: 2, height: 13,
              background: agentColor, marginLeft: 2, verticalAlign: "middle",
              animation: "blink 0.7s step-end infinite",
            }} />
          )}
          {isEmpty && (
            <span style={{ color: "#444", fontStyle: "italic" }}>thinking…</span>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Empty / welcome state ──────────────────────────────────────────────────────
function WelcomeState({ agent, agentColor }) {
  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      gap: 16, padding: 32, textAlign: "center",
    }}>
      <div style={{
        width: 56, height: 56, borderRadius: "50%",
        background: `${agentColor}14`,
        border: `1px solid ${agentColor}44`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 22,
      }}>
        {agent.icon}
      </div>
      <div>
        <div style={{ fontSize: 14, fontWeight: 700, color: "#FFFFFF", marginBottom: 6 }}>
          Chat with {agent.label}
        </div>
        <div style={{ fontSize: 11, color: "#555555", maxWidth: 300, lineHeight: 1.6 }}>
          {agent.desc}
        </div>
      </div>
      <div style={{
        display: "flex", flexDirection: "column", gap: 8, width: "100%", maxWidth: 340,
      }}>
        {getSuggestions(agent.id).map((s, i) => (
          <div key={i} style={{
            fontSize: 11, color: agentColor, opacity: 0.7,
            padding: "6px 12px",
            border: `1px solid ${agentColor}22`,
            borderRadius: 6,
            cursor: "default",
            letterSpacing: "0.02em",
          }}>
            "{s}"
          </div>
        ))}
      </div>
    </div>
  );
}

function getSuggestions(agentId) {
  const map = {
    people:     ["Who are the key-person risks on the team?", "How is developer sentiment trending?", "What's the bus factor risk?"],
    finance:    ["What's our runway?", "Which client has the highest revenue concentration?", "How is burn rate trending?"],
    infra:      ["Are there any deployment failures?", "What's our uptime looking like?", "What cloud cost risks exist?"],
    product:    ["Why is churn accelerating?", "What's our NPS trend?", "Which features have the highest error rates?"],
    legal:      ["Are there any contract breaches approaching?", "What compliance gaps exist?", "Which contracts are expiring soon?"],
    code_audit: ["What are the top CVEs in our codebase?", "What's our test coverage situation?", "Who owns the most critical code?"],
  };
  return map[agentId] ?? [];
}

// ── Main panel ────────────────────────────────────────────────────────────────
export default function AgentChatPanel({ agentStatuses }) {
  const [activeAgent, setActiveAgent]   = useState("people");
  const [conversations, setConversations] = useState({}); // agentId → [{role, text, streaming?}]
  const [input, setInput]               = useState("");
  const [streaming, setStreaming]       = useState(false);
  const abortRef                        = useRef(null);
  const bottomRef                       = useRef(null);
  const inputRef                        = useRef(null);

  const agent      = AGENTS.find(a => a.id === activeAgent);
  const agentColor = DOMAIN_COLORS[activeAgent] ?? "#888888";
  const messages   = conversations[activeAgent] ?? [];

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const switchAgent = (id) => {
    if (streaming) {
      abortRef.current?.abort();
      setStreaming(false);
    }
    setActiveAgent(id);
    setInput("");
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg   = { role: "user",  text };
    const agentMsg  = { role: "model", text: "", streaming: true };

    // Build history from existing conversation (exclude any in-flight streaming msg)
    const history = messages
      .filter(m => !m.streaming)
      .map(m => ({ role: m.role, text: m.text }));

    setConversations(prev => ({
      ...prev,
      [activeAgent]: [...(prev[activeAgent] ?? []), userMsg, agentMsg],
    }));
    setInput("");
    setStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${BASE}/api/agents/${activeAgent}/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: text, history }),
        signal:  controller.signal,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer    = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";          // keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") break;
          try {
            const { text: chunk } = JSON.parse(payload);
            setConversations(prev => {
              const msgs = [...(prev[activeAgent] ?? [])];
              const last = msgs[msgs.length - 1];
              if (last?.streaming) {
                msgs[msgs.length - 1] = { ...last, text: last.text + chunk };
              }
              return { ...prev, [activeAgent]: msgs };
            });
          } catch (_) { /* malformed chunk — skip */ }
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        setConversations(prev => {
          const msgs = [...(prev[activeAgent] ?? [])];
          const last = msgs[msgs.length - 1];
          if (last?.streaming) {
            msgs[msgs.length - 1] = { ...last, text: last.text || "Error: " + err.message, streaming: false };
          }
          return { ...prev, [activeAgent]: msgs };
        });
      }
    } finally {
      // Mark streaming as done — remove the cursor
      setConversations(prev => {
        const msgs = [...(prev[activeAgent] ?? [])];
        const last = msgs[msgs.length - 1];
        if (last?.streaming) {
          msgs[msgs.length - 1] = { ...last, streaming: false };
        }
        return { ...prev, [activeAgent]: msgs };
      });
      setStreaming(false);
    }
  }, [input, streaming, activeAgent, messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setConversations(prev => ({ ...prev, [activeAgent]: [] }));
  };

  return (
    <div style={{
      display: "flex", height: "100%", overflow: "hidden",
      background: "#0A0A0A",
    }}>

      {/* ── Left sidebar: agent list ───────────────────────────────────────── */}
      <div style={{
        width: 200, flexShrink: 0,
        borderRight: "1px solid #1E1E1E",
        display: "flex", flexDirection: "column",
        paddingTop: 8,
        overflowY: "auto",
      }}>
        <div style={{
          fontSize: 9, fontWeight: 700, textTransform: "uppercase",
          letterSpacing: "0.15em", color: "#333333",
          padding: "4px 16px 10px",
        }}>
          Specialist Agents
        </div>
        {AGENTS.map(a => (
          <AgentCard
            key={a.id}
            agent={a}
            active={activeAgent}
            status={agentStatuses?.[a.id] ?? "idle"}
            onClick={switchAgent}
          />
        ))}
      </div>

      {/* ── Right: chat area ───────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>

        {/* Chat header */}
        <div style={{
          height: 48, flexShrink: 0,
          borderBottom: "1px solid #1E1E1E",
          display: "flex", alignItems: "center",
          padding: "0 20px", gap: 10,
          justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{
              width: 8, height: 8, borderRadius: "50%",
              background: agentColor, boxShadow: `0 0 8px ${agentColor}`,
            }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: "#FFFFFF" }}>
              {agent?.label}
            </span>
            <span style={{ fontSize: 10, color: "#444444" }}>
              {agent?.desc}
            </span>
          </div>
          {messages.length > 0 && (
            <button onClick={clearChat} style={{
              background: "none", border: "1px solid #2A2A2A", borderRadius: 4,
              color: "#555555", fontSize: 9, fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.08em",
              padding: "3px 8px", cursor: "pointer",
            }}
              onMouseEnter={e => { e.currentTarget.style.color = "#FF2020"; e.currentTarget.style.borderColor = "#FF2020"; }}
              onMouseLeave={e => { e.currentTarget.style.color = "#555555"; e.currentTarget.style.borderColor = "#2A2A2A"; }}
            >
              Clear
            </button>
          )}
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: "auto",
          padding: "20px 24px",
          display: "flex", flexDirection: "column",
        }}>
          {messages.length === 0 ? (
            <WelcomeState agent={agent} agentColor={agentColor} />
          ) : (
            messages.map((msg, i) => (
              <ChatBubble
                key={i}
                msg={msg}
                agentColor={agentColor}
                agentLabel={agent?.label}
              />
            ))
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div style={{
          flexShrink: 0,
          borderTop: "1px solid #1E1E1E",
          padding: "12px 20px",
          display: "flex", gap: 10, alignItems: "flex-end",
          background: "#0A0A0A",
        }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Ask ${agent?.label} anything…`}
            rows={1}
            style={{
              flex: 1,
              background: "#111111",
              border: `1px solid ${input ? agentColor + "44" : "#2A2A2A"}`,
              borderRadius: 8,
              color: "#FFFFFF",
              fontSize: 12,
              padding: "10px 14px",
              resize: "none",
              outline: "none",
              fontFamily: "'Inter', sans-serif",
              lineHeight: 1.5,
              transition: "border-color 0.15s",
              maxHeight: 120,
              overflowY: "auto",
            }}
            onInput={e => {
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || streaming}
            style={{
              background: (!input.trim() || streaming)
                ? "#1A1A1A"
                : `linear-gradient(135deg, ${agentColor}, ${agentColor}99)`,
              border: "none",
              borderRadius: 8,
              padding: "10px 18px",
              color: (!input.trim() || streaming) ? "#444444" : "#FFFFFF",
              fontSize: 11, fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.08em",
              cursor: (!input.trim() || streaming) ? "not-allowed" : "pointer",
              transition: "all 0.15s",
              flexShrink: 0,
              height: 40,
            }}
          >
            {streaming ? "…" : "Send"}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0; }
        }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
      `}</style>
    </div>
  );
}
