"""
Shared JSON parsing utilities for DEADPOOL agent responses.

All specialist agents receive LLM output that may be wrapped in markdown
code fences or nested inside a JSON object wrapper key. These utilities
centralise the stripping and unwrapping logic so each agent doesn't
re-implement it.
"""
from __future__ import annotations

import json
import logging
import re
import uuid

from models import Anomaly

logger = logging.getLogger("deadpool.parsing")


def strip_markdown_fences(raw: str) -> str:
    """Remove markdown code fences (```json ... ``` or ``` ... ```) from a string."""
    return re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()


def parse_anomaly_list(raw: str, domain: str) -> list[Anomaly]:
    """
    Parse an LLM response into a validated list of Anomaly objects.

    Handles:
    - Markdown code fences (``` or ```json)
    - Bare JSON arrays: [...]
    - Dict-wrapped arrays: {"anomalies": [...]} / {"results": [...]} / any list value

    The dict-unwrapping path is needed for OpenAI's json_object response mode,
    which guarantees a JSON object but not a bare array. Gemini agents typically
    return a bare array, which falls through to the bracket-search path.

    Args:
        raw:    Raw text from the LLM.
        domain: Agent domain string used for ID generation and warning messages.

    Returns:
        List of validated Anomaly objects. Empty list on any parse failure.
    """
    text = strip_markdown_fences(raw)

    # Try full json.loads first (handles both arrays and wrapped objects)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Fall back to bracket-search for responses with leading/trailing text
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            return []
        try:
            parsed = json.loads(text[start: end + 1])
        except json.JSONDecodeError:
            return []

    # Unwrap dict wrapper keys (e.g. {"anomalies": [...]})
    if isinstance(parsed, dict):
        for key in ("anomalies", "results", "data", "items"):
            if key in parsed and isinstance(parsed[key], list):
                parsed = parsed[key]
                break
        else:
            # Try any list value
            for v in parsed.values():
                if isinstance(v, list):
                    parsed = v
                    break
            else:
                return []

    if not isinstance(parsed, list):
        return []

    anomalies: list[Anomaly] = []
    for item in parsed:
        if "id" not in item or not item["id"]:
            item["id"] = f"{domain}_{uuid.uuid4().hex[:8]}"
        item["agent_domain"] = domain
        try:
            anomalies.append(Anomaly(**item))
        except Exception as exc:
            logger.warning("[%s] Skipping malformed anomaly: %s", domain, exc)

    return anomalies
