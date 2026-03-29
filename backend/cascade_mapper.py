"""
CascadeMapper utilities for DEADPOOL.

Provides the LLM-based next-step consequence predictor (_llm_next_step)
and the domain rules engine (_apply_rules) used by the orchestrator's
cascade_expander LangGraph node.
"""
from __future__ import annotations

import json

import google.genai as genai
from google.genai import types as genai_types

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROB_THRESHOLD = 40  # Stop a branch below this probability

TERMINAL_STATES = {
    "bankruptcy",
    "forced_acquisition",
    "hostile_board_takeover",
    "regulatory_seizure",
    "founder_dilution_loss",
    "mass_exodus_collapse",
}

RULES: dict[str, int] = {
    # domain_pair or single domain → probability floor boost (additive)
    "finance+people": 25,
    "legal+finance": 20,
    "infra+product": 15,
}


# ---------------------------------------------------------------------------
# Rules engine
# ---------------------------------------------------------------------------

def _apply_rules(domains_present: list[str], base_prob: float) -> float:
    """
    Boost probability if known dangerous domain combinations are active.
    Purely additive — caps at 99 to keep LLM output meaningful.
    """
    boost = 0
    active = set(domains_present)
    for combo, b in RULES.items():
        parts = set(combo.split("+"))
        if parts.issubset(active):
            boost += b
    return min(base_prob + boost, 99.0)


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def _llm_next_step(
    client: genai.Client,
    active_threads: list[dict],
    depth: int,
) -> list[dict]:
    """
    Ask the LLM: given all currently active causal threads, what are the
    next consequences and their probabilities?

    Returns a list of consequence dicts:
      {
        "cause": str,
        "probability": float,
        "contributing_causes": [str],   # which active threads fed into this
        "is_terminal": bool,
        "terminal_state": str | null
      }
    """
    prompt = f"""
You are a startup risk cascade analyst. Given the currently active causal threads 
in a startup, identify the next set of consequences.

Rules:
- Return the next set of consequence scenarios (as a JSON array; do not wrap in prose).
- For each consequence, assign a probability (0-100) that it materializes.
- Where two or more active threads combine to accelerate a consequence, list 
  all contributing causes and reflect the acceleration in a higher probability.
- Mark a consequence as terminal if it results in the founder losing control 
  of the company. Terminal states include: {", ".join(sorted(TERMINAL_STATES))}.
- Be precise and concise. No filler text.

Currently active threads (depth {depth}):
{json.dumps(active_threads, indent=2)}

Respond ONLY with a JSON array. Each element:
{{
  "cause": "<consequence description>",
  "probability": <float 0-100>,
  "contributing_causes": ["<cause from active threads>"],
  "is_terminal": <true|false>,
  "terminal_state": "<terminal state key or null>"
}}
"""
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            max_output_tokens=2000,
            response_mime_type="application/json",
        ),
    )

    raw = (response.text or "").strip()
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract a JSON array from prose/markdown
        start = raw.find("[")
        end   = raw.rfind("]")
        if start != -1 and end != -1:
            try:
                result = json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    # Gemini sometimes wraps the array in an object e.g. {"consequences": [...]}
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                return v
    return []

