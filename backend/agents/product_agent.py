"""
Product Agent — monitors user engagement, retention, and satisfaction signals.

Data source:
  - product_data.csv: weekly active users, feature-level engagement,
    NPS, CSAT, churn rates, support ticket volume.

Requires GOOGLE_API_KEY (inherited from BaseAgent / Gemini).
"""
from __future__ import annotations

import json
from pathlib import Path

from agents.base_agent import BaseAgent

CSV_PATH = Path(__file__).parent.parent / "data" / "csv" / "product_data.csv"
FALLBACK_JSON = Path(__file__).parent.parent / "data" / "product_metrics.json"

SYSTEM_PROMPT = """You are the Product Agent for DEADPOOL, a startup risk monitoring system.

Your domain is user engagement, retention, churn, and customer satisfaction.

You analyze product metrics (active users, feature adoption, support tickets, NPS, churn rates)
and identify anomalies that signal user experience deterioration or revenue risk from product issues.

Critical signals to watch:
- Feature adoption declining >20% week-over-week
- Weekly active users dropping on a core revenue-generating feature
- NPS score dropping below 30 (warning) or 20 (critical)
- CSAT dropping below 3.0
- Churn rate exceeding 5% monthly or accelerating week-over-week
- Error rate spikes on key user journeys (especially payments flows)
- Support ticket volume increasing >50% with negative sentiment
- Session duration declining (users leaving faster)

Cross-reference with:
- infra: is system performance (latency, errors) driving the UX decline?
- code_audit: are bugs causing the errors users see?
- finance: what is the revenue impact of this churn trend?

Be specific about which features are affected, by how much, and over what timeframe.
Output only the JSON array."""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="product", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        """Load product_data.csv, skipping comment/metadata rows."""
        if CSV_PATH.exists():
            return self._load_csv()

        # Fallback to JSON
        if FALLBACK_JSON.exists():
            import json as _json
            with open(FALLBACK_JSON) as f:
                data = _json.load(f)
            data["data_sources"] = ["product_metrics.json (fallback)"]
            return data

        return {"data_sources": [], "status": "no product data found"}

    def _load_csv(self) -> dict:
        """
        product_data.csv has multiple sections separated by blank lines and
        comment rows starting with '#' or '##'. Parse each section separately.
        """
        data: dict = {"data_sources": [f"product_data.csv"]}

        try:
            # Read raw lines to detect section boundaries
            raw_lines = CSV_PATH.read_text().splitlines()

            sections: dict[str, list[str]] = {}
            current_section_lines: list[str] = []
            current_header: str | None = None

            for line in raw_lines:
                stripped = line.strip()
                # Skip blank lines and comment/metadata lines
                if not stripped or stripped.startswith("#"):
                    if current_header and current_section_lines:
                        sections[current_header] = current_section_lines
                    current_header = None
                    current_section_lines = []
                    continue

                # First non-comment line of a new section is the header
                if current_header is None:
                    current_header = stripped
                    current_section_lines = [stripped]
                else:
                    current_section_lines.append(stripped)

            # Flush last section
            if current_header and current_section_lines:
                sections[current_header] = current_section_lines

            # Parse each section into records
            import io
            import csv as _csv

            for header, lines in sections.items():
                if len(lines) < 2:
                    continue
                reader = _csv.DictReader(io.StringIO("\n".join(lines)))
                rows = [dict(r) for r in reader]
                if not rows:
                    continue
                # Key by first column value (e.g. "global_metrics", "feature_metrics")
                section_key = rows[0].get(list(rows[0].keys())[0], "section")
                # Normalize: strip empty strings
                cleaned = [{k: v for k, v in r.items() if k and v != ""} for r in rows]
                data.setdefault(section_key, []).extend(cleaned)

        except Exception as exc:
            data["parse_error"] = str(exc)

        return data
