"""
CascadeMapper agent for DEADPOOL.

Takes root causes from HeadAgent and builds a directed consequence graph,
following causal chains until every branch either:
  - drops below PROB_THRESHOLD (40%), or
  - reaches a founder-control-loss terminal state.

Branches are evaluated collectively at each level so cross-cause
acceleration is captured.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

import google.genai as genai
from google.genai import types as genai_types

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROB_THRESHOLD = 40  # Stop a branch below this probability
MAX_DEPTH = 10       # Hard stop to prevent runaway chains

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
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CascadeNode:
    cause: str
    probability: float          # 0–100
    contributing_causes: list[str] = field(default_factory=list)
    children: list["CascadeNode"] = field(default_factory=list)
    terminal: bool = False
    terminal_state: Optional[str] = None
    depth: int = 0


@dataclass
class CascadeResult:
    roots: list[CascadeNode]    # One per root cause from head agent
    reached_terminal: bool      # True if any branch hit a control-loss state
    terminal_states_hit: list[str]
    max_depth_reached: int


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


# ---------------------------------------------------------------------------
# Core cascade logic
# ---------------------------------------------------------------------------

def _build_cascade(
    client: genai.Client,
    root_causes: list[str],
    domains_present: list[str],
) -> CascadeResult:
    """
    Iteratively expand the cascade graph level by level.
    Each level passes all active threads to the LLM together so
    cross-cause interactions are captured.
    """
    terminal_states_hit: list[str] = []
    max_depth_reached = 0

    # Seed the first level with root causes at 100% (they already happened)
    root_nodes: list[CascadeNode] = [
        CascadeNode(cause=rc, probability=100.0, depth=0)
        for rc in root_causes
    ]

    # Track all nodes at the current depth so we pass them collectively
    # to the LLM — this is what enables cross-cause acceleration detection.
    depth_map: dict[int, list[CascadeNode]] = {0: root_nodes}

    visited_causes: set[str] = set(root_causes)

    current_depth = 0

    while current_depth < MAX_DEPTH:
        active_nodes = depth_map.get(current_depth, [])
        if not active_nodes:
            break

        # Only pass threads that are still alive (above threshold, not terminal)
        live_threads = [
            {"cause": n.cause, "probability": n.probability}
            for n in active_nodes
            if not n.terminal and n.probability >= PROB_THRESHOLD
        ]
        if not live_threads:
            break

        max_depth_reached = current_depth
        next_depth = current_depth + 1

        raw_consequences = _llm_next_step(client, live_threads, current_depth)

        next_nodes: list[CascadeNode] = []

        for c in raw_consequences:
            prob = float(c["probability"])
            prob = _apply_rules(domains_present, prob)

            # Deduplicate — if this consequence already exists in the graph,
            # skip spawning a new branch (prevents infinite loops)
            if c["cause"] in visited_causes:
                continue
            visited_causes.add(c["cause"])

            node = CascadeNode(
                cause=c["cause"],
                probability=prob,
                contributing_causes=c.get("contributing_causes", []),
                terminal=c.get("is_terminal", False),
                terminal_state=c.get("terminal_state"),
                depth=next_depth,
            )

            # Attach to parent nodes that contributed.
            # Fall back to attaching to all active parents if no exact match is
            # found — the LLM rarely reproduces the cause string verbatim.
            contributing = set(c.get("contributing_causes", []))
            attached = False
            for parent in active_nodes:
                if parent.cause in contributing:
                    parent.children.append(node)
                    attached = True
            if not attached:
                for parent in active_nodes:
                    parent.children.append(node)

            if node.terminal:
                if node.terminal_state:
                    terminal_states_hit.append(node.terminal_state)
                next_nodes.append(node)
                continue  # Don't expand past terminal

            if prob < PROB_THRESHOLD:
                next_nodes.append(node)
                continue  # Branch dies here — still record it, don't expand

            next_nodes.append(node)

        depth_map[next_depth] = next_nodes
        current_depth += 1

    return CascadeResult(
        roots=root_nodes,
        reached_terminal=len(terminal_states_hit) > 0,
        terminal_states_hit=list(set(terminal_states_hit)),
        max_depth_reached=max_depth_reached,
    )


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CascadeMapperAgent:
    """
    Standalone agent — receives root causes and domains from HeadAgent output,
    returns a fully expanded CascadeResult.
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def run(self, root_causes: list[str], domains_present: list[str]) -> CascadeResult:
        return _build_cascade(self.client, root_causes, domains_present)