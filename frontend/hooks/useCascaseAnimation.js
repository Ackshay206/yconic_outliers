// ─── hooks/useCascadeAnimation.js ────────────────────────────────────────────
import { useState, useEffect } from "react";

export function useCascadeAnimation(edgeCount) {
  const [pulse, setPulse]       = useState(0);
  const [animStep, setAnimStep] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setPulse(p => (p + 1) % 100), 50);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setAnimStep(s => (s + 1) % (edgeCount + 1)), 600);
    return () => clearInterval(t);
  }, [edgeCount]);

  return { pulse, animStep };
}