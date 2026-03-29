// ─── components/LandingPage.jsx ───────────────────────────────────────────────
import { useState, useEffect } from "react";

// Full name broken into acronym segments
const ACRONYM = [
  { letter: "D", rest: "ependency"   },
  { letter: "E", rest: "valuation"   },
  { letter: "A", rest: "nd"          },
  { letter: "D", rest: "ownstream"   },
  { letter: "P", rest: "rediction"   },
  { letter: "O", rest: "f"           },
  { letter: "O", rest: "perational"  },
  { letter: "L", rest: "iabilities"  },
];

const TAGLINES = [
  "8 AI agents. One unified threat model.",
  "Know which domino falls first — before it does.",
  "Built for founders who can't afford to be surprised.",
];

// ── Scanline overlay ───────────────────────────────────────────────────────────
function Scanlines() {
  return (
    <div style={{
      position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none",
      backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px)",
    }} />
  );
}

// ── Red radial glow behind center ─────────────────────────────────────────────
function Glow() {
  return (
    <div style={{
      position: "absolute", inset: 0, zIndex: 0, pointerEvents: "none",
      background: "radial-gradient(ellipse 60% 50% at 50% 50%, rgba(180,0,0,0.18) 0%, transparent 70%)",
    }} />
  );
}

// ── Corner grid decoration ────────────────────────────────────────────────────
function CornerGrid({ corner }) {
  const isRight = corner === "right";
  return (
    <div style={{
      position: "absolute",
      top: 0, [isRight ? "right" : "left"]: 0,
      width: 220, height: 220,
      zIndex: 1, pointerEvents: "none",
      opacity: 0.12,
      backgroundImage: `
        linear-gradient(rgba(255,32,32,0.6) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,32,32,0.6) 1px, transparent 1px)
      `,
      backgroundSize: "28px 28px",
      maskImage: isRight
        ? "radial-gradient(ellipse at top right, black 30%, transparent 70%)"
        : "radial-gradient(ellipse at top left,  black 30%, transparent 70%)",
      WebkitMaskImage: isRight
        ? "radial-gradient(ellipse at top right, black 30%, transparent 70%)"
        : "radial-gradient(ellipse at top left,  black 30%, transparent 70%)",
    }} />
  );
}

// ── Floating threat particles ──────────────────────────────────────────────────
const PARTICLES = Array.from({ length: 18 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: 1 + Math.random() * 2,
  dur: 4 + Math.random() * 8,
  delay: Math.random() * 6,
  opacity: 0.15 + Math.random() * 0.25,
}));

function Particles() {
  return (
    <div style={{ position: "absolute", inset: 0, zIndex: 0, pointerEvents: "none" }}>
      {PARTICLES.map(p => (
        <div key={p.id} style={{
          position: "absolute",
          left: `${p.x}%`, top: `${p.y}%`,
          width: p.size, height: p.size,
          borderRadius: "50%",
          background: "#FF2020",
          opacity: p.opacity,
          animation: `particlePulse ${p.dur}s ${p.delay}s ease-in-out infinite alternate`,
        }} />
      ))}
    </div>
  );
}

// ── Main landing page ─────────────────────────────────────────────────────────
export default function LandingPage({ onEnter }) {
  const [phase, setPhase] = useState(0);
  // phase 0 = nothing
  // phase 1 = title in
  // phase 2 = acronym in
  // phase 3 = taglines in
  // phase 4 = button in
  // phase 5 = exit animation

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 120),
      setTimeout(() => setPhase(2), 700),
      setTimeout(() => setPhase(3), 1100),
      setTimeout(() => setPhase(4), 1800),
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  const handleEnter = () => {
    setPhase(5);
    setTimeout(onEnter, 700);
  };

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 200,
      background: "#080808",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      fontFamily: "'Inter', sans-serif",
      overflow: "hidden",
      opacity: phase === 5 ? 0 : 1,
      transition: phase === 5 ? "opacity 0.6s ease" : "none",
    }}>
      <Scanlines />
      <Glow />
      <Particles />
      <CornerGrid corner="left" />
      <CornerGrid corner="right" />

      {/* ── Top status bar ─────────────────────────────────────────────────── */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0,
        height: 40, zIndex: 2,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 32px",
        borderBottom: "1px solid rgba(255,32,32,0.12)",
      }}>
        <span style={{ fontSize: 9, fontWeight: 700, color: "#3D0000", letterSpacing: "0.2em", textTransform: "uppercase" }}>
          DEADPOOL // RISK INTELLIGENCE v1.0
        </span>
        <span style={{ fontSize: 9, fontWeight: 700, color: "#3D0000", letterSpacing: "0.2em" }}>
          ● SYSTEM ONLINE
        </span>
      </div>

      {/* ── Main content ───────────────────────────────────────────────────── */}
      <div style={{ position: "relative", zIndex: 2, textAlign: "center", maxWidth: 820, padding: "0 32px" }}>

        {/* DEADPOOL title */}
        <div style={{
          fontSize: "clamp(72px, 12vw, 128px)",
          fontWeight: 900,
          letterSpacing: "-4px",
          lineHeight: 1,
          marginBottom: 8,
          background: "linear-gradient(180deg, #FF2020 0%, #B00000 60%, #5A0000 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          opacity: phase >= 1 ? 1 : 0,
          transform: phase >= 1 ? "translateY(0) scale(1)" : "translateY(20px) scale(0.96)",
          transition: "opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1)",
          textShadow: "none",
          filter: phase >= 1 ? "drop-shadow(0 0 40px rgba(255,32,32,0.35))" : "none",
        }}>
          DEADPOOL
        </div>

        {/* Separator line */}
        <div style={{
          height: 1, margin: "0 auto 28px",
          background: "linear-gradient(90deg, transparent, #FF2020, transparent)",
          opacity: phase >= 1 ? 0.6 : 0,
          width: phase >= 1 ? "60%" : "0%",
          transition: "width 1s ease 0.3s, opacity 0.5s ease 0.3s",
        }} />

        {/* Acronym breakdown — all words on one line, no wrap */}
        <div style={{
          display: "flex", flexDirection: "row", alignItems: "baseline",
          justifyContent: "center", flexWrap: "nowrap",
          gap: "0 14px", marginBottom: 40,
          whiteSpace: "nowrap",
          opacity: phase >= 2 ? 1 : 0,
          transform: phase >= 2 ? "translateY(0)" : "translateY(8px)",
          transition: "opacity 0.6s ease, transform 0.6s ease",
        }}>
          {ACRONYM.map((item, i) => (
            <span key={i} style={{
              fontSize: "clamp(13px, 1.4vw, 18px)", letterSpacing: "0.01em",
              opacity: phase >= 2 ? 1 : 0,
              transition: `opacity 0.4s ease ${i * 0.06}s`,
            }}>
              <span style={{ fontWeight: 900, color: "#FF2020" }}>{item.letter}</span>
              <span style={{ fontWeight: 400, color: "#555555" }}>{item.rest}</span>
            </span>
          ))}
        </div>

        {/* Taglines */}
        <div style={{
          display: "flex", flexDirection: "column", gap: 8,
          marginBottom: 52,
          opacity: phase >= 3 ? 1 : 0,
          transform: phase >= 3 ? "translateY(0)" : "translateY(8px)",
          transition: "opacity 0.6s ease, transform 0.6s ease",
        }}>
          {TAGLINES.map((line, i) => (
            <p key={i} style={{
              margin: 0,
              fontSize: i === 0 ? 15 : 12,
              fontWeight: i === 0 ? 600 : 400,
              color: i === 0 ? "#888888" : "#444444",
              letterSpacing: "0.02em",
              lineHeight: 1.5,
            }}>
              {i === 0 ? line : `— ${line}`}
            </p>
          ))}
        </div>

        {/* CTA button */}
        <div style={{
          opacity: phase >= 4 ? 1 : 0,
          transform: phase >= 4 ? "translateY(0)" : "translateY(10px)",
          transition: "opacity 0.5s ease, transform 0.5s ease",
        }}>
          <button
            onClick={handleEnter}
            style={{
              position: "relative",
              background: "transparent",
              border: "1px solid #FF2020",
              color: "#FF2020",
              fontSize: 11, fontWeight: 900,
              textTransform: "uppercase", letterSpacing: "0.25em",
              padding: "16px 52px",
              borderRadius: 4,
              cursor: "pointer",
              overflow: "hidden",
              transition: "color 0.25s, background 0.25s, box-shadow 0.25s",
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = "#FF2020";
              e.currentTarget.style.color = "#000000";
              e.currentTarget.style.boxShadow = "0 0 40px rgba(255,32,32,0.5)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "#FF2020";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            INITIATE ANALYSIS
          </button>
          <div style={{
            marginTop: 14, fontSize: 9, color: "#2A2A2A",
            letterSpacing: "0.15em", textTransform: "uppercase",
          }}>
            Clearance required · 8 agents · Full-spectrum risk scan
          </div>
        </div>
      </div>

      {/* ── Bottom bar ─────────────────────────────────────────────────────── */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0,
        height: 40, zIndex: 2,
        display: "flex", alignItems: "center", justifyContent: "center",
        gap: 32,
        borderTop: "1px solid rgba(255,32,32,0.08)",
      }}>
        {["People", "Finance", "Infra", "Product", "Legal", "Code Audit", "Head Agent", "Cascade"].map(a => (
          <span key={a} style={{
            fontSize: 8, fontWeight: 700, color: "#2A2A2A",
            letterSpacing: "0.15em", textTransform: "uppercase",
          }}>
            {a}
          </span>
        ))}
      </div>

      <style>{`
        @keyframes particlePulse {
          0%   { opacity: 0.05; transform: scale(1); }
          100% { opacity: 0.35; transform: scale(2.5); }
        }
      `}</style>
    </div>
  );
}
