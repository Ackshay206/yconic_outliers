"""
Product Agent — monitors user engagement, retention, and satisfaction signals.

Data sources:
  - product_data.csv: weekly active users, feature-level engagement,
    NPS, CSAT, churn rates, support ticket volume.
  - r/BrainrotGenz (Reddit): live user sentiment, complaints, feature feedback,
    and organic reactions scraped via Reddit's public JSON API.

Requires GOOGLE_API_KEY (inherited from BaseAgent / Gemini).
"""
from __future__ import annotations

import json
from pathlib import Path

from backend.agents.base_agent import BaseAgent

CSV_PATH          = Path(__file__).parent.parent / "data" / "csv" / "product_data.csv"
FALLBACK_JSON     = Path(__file__).parent.parent / "data" / "product_metrics.json"
REDDIT_CACHE_JSON = Path(__file__).parent.parent / "data" / "reddit_brainrotgenz.json"
SUBREDDIT = "BrainrotGenz"

SYSTEM_PROMPT = """You are the Product Agent for DEADPOOL, a startup risk monitoring system.

Your domain is user engagement, retention, churn, and customer satisfaction.

You have TWO data sources:

1. PRODUCT METRICS (CSV) — quantitative signals:
   - Weekly active users, feature adoption rates, NPS, CSAT, churn rates,
     support ticket volume, session duration, error rates.

2. REDDIT DATA (r/BrainrotGenz) — qualitative signals:
   - Real user posts and comments about the app, scraped from the subreddit.
   - Analyze post titles, selftext, and comments for sentiment, complaints,
     praise, feature requests, and bug reports.
   - High-upvote posts and comments carry stronger signal weight.
   - Look for recurring themes across multiple posts — single posts are noise,
     patterns are signal.

CRITICAL SIGNALS TO WATCH:

Quantitative (CSV):
- Feature adoption declining >20% week-over-week
- Weekly active users dropping on a core revenue-generating feature
- NPS score dropping below 30 (warning) or 20 (critical)
- CSAT dropping below 3.0
- Churn rate exceeding 5% monthly or accelerating week-over-week
- Error rate spikes on key user journeys (especially payments flows)
- Support ticket volume increasing >50% with negative sentiment
- Session duration declining (users leaving faster)

Qualitative (Reddit):
- Surge in complaint posts about a specific feature (especially the For You Feed
  or payments flow)
- Users explicitly saying they are leaving, deleting the app, or switching to a competitor
- Bug reports appearing in multiple posts/comments
- Negative sentiment dominating recent posts (last 7 days especially)
- Low engagement posts on the subreddit (few upvotes/comments = community disengagement)
- Positive signals: praise posts, feature requests, community growth

SYNTHESIS:
When both data sources agree (e.g. CSV shows churn rising AND Reddit shows
users complaining about the same feature), treat this as corroborated and
raise severity. When they conflict, note the discrepancy in your evidence.

Cross-reference with:
- infra: is system performance (latency, errors) driving the UX decline?
- code_audit: are bugs causing the errors users see?
- finance: what is the revenue impact of this churn trend?

Be specific about which features are affected, by how much, and over what timeframe.
Quote specific Reddit post titles or comment text as evidence where relevant.
Output only the JSON array."""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="product", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        """Load product CSV metrics and scrape Reddit for live user sentiment."""
        data: dict = {}

        # --- Source 1: Product metrics CSV ---
        if CSV_PATH.exists():
            data.update(self._load_csv())
        elif FALLBACK_JSON.exists():
            import json as _json
            with open(FALLBACK_JSON) as f:
                data.update(_json.load(f))
            data["data_sources"] = data.get("data_sources", []) + ["product_metrics.json (fallback)"]
        else:
            data["data_sources"] = []
            data["status"] = "no product CSV data found"

        # --- Source 2: Reddit scrape (with cached JSON fallback) ---
        reddit_data = None
        try:
            from backend.utils.reddit_scraper import fetch_subreddit_data
            reddit_data = fetch_subreddit_data(SUBREDDIT, max_pages=3, fetch_comments=True)
        except Exception as exc:
            import logging as _logging
            _logging.getLogger("deadpool.product_agent").warning(
                "Reddit scrape failed: %s — falling back to cached JSON", exc
            )

        # Fall back to cached JSON if scrape failed or returned no posts
        if not reddit_data or not reddit_data.get("posts"):
            if REDDIT_CACHE_JSON.exists():
                with open(REDDIT_CACHE_JSON) as _f:
                    reddit_data = json.load(_f)
                reddit_data["_source"] = "cached (reddit_brainrotgenz.json)"
                data.setdefault("data_sources", []).append(f"r/{SUBREDDIT} (cached JSON fallback)")
            else:
                reddit_data = {"posts": [], "_source": "no data available"}

        data["reddit"] = reddit_data
        if "_source" not in reddit_data:
            data.setdefault("data_sources", []).append(f"r/{SUBREDDIT} (Reddit live)")

        return data

    def _load_csv(self) -> dict:
        """
        product_data.csv has multiple sections separated by blank lines and
        comment rows starting with '#' or '##'. Parse each section separately.
        """
        data: dict = {"data_sources": ["product_data.csv"]}

        try:
            raw_lines = CSV_PATH.read_text().splitlines()

            sections: dict[str, list[str]] = {}
            current_section_lines: list[str] = []
            current_header: str | None = None

            for line in raw_lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    if current_header and current_section_lines:
                        sections[current_header] = current_section_lines
                    current_header = None
                    current_section_lines = []
                    continue

                if current_header is None:
                    current_header = stripped
                    current_section_lines = [stripped]
                else:
                    current_section_lines.append(stripped)

            if current_header and current_section_lines:
                sections[current_header] = current_section_lines

            import io
            import csv as _csv

            for _, lines in sections.items():
                if len(lines) < 2:
                    continue
                reader = _csv.DictReader(io.StringIO("\n".join(lines)))
                rows = [dict(r) for r in reader]
                if not rows:
                    continue
                section_key = rows[0].get(list(rows[0].keys())[0], "section")
                cleaned = [{k: v for k, v in r.items() if k and v != ""} for r in rows]
                data.setdefault(section_key, []).extend(cleaned)

        except Exception as exc:
            data["parse_error"] = str(exc)

        return data
