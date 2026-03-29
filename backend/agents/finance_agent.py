"""
Finance Agent — monitors cash flow, runway, revenue concentration, and funding terms.

Data sources:
  - deadpool_finance_data.csv     (transaction ledger: income + expenses)
  - deadpool_revenue_pipeline.csv (revenue actuals, AR, pipeline deals)
  - deadpool_funding_runway.csv   (investor terms, monthly summaries, runway scenarios)

Model: GPT-4o-mini (OpenAI) — fast structured data extraction and precise arithmetic.
Requires OPENAI_API_KEY environment variable.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI

from models import Anomaly, AgentReport

DATA_DIR = Path(__file__).parent.parent / "data" / "csv"

SYSTEM_PROMPT = """You are the Finance Agent for DEADPOOL, a startup risk monitoring system.

Your domain is cash flow, runway, revenue concentration, burn rate, and investor terms.
You receive structured CSV data from three files and must identify financial anomalies.

Critical signals to watch:
- Runway dropping below 6 months (red alert below 3 months)
- Revenue concentration: any single client representing >30% of total revenue
- Burn rate accelerating month-over-month (>10% increase)
- Investor clause thresholds approaching (down-round triggers, anti-dilution)
- Payment delays from major clients (AR overdue >30 days)
- Refund or penalty liabilities from contract breaches
- Pipeline deals at risk due to feature delivery dependencies

Cross-reference with:
- legal: contract values, renewal dates, and breach terms for concentrated revenue clients
- people: headcount costs and hiring pipeline expenses
- product: health of revenue-generating features

Name specific clients, dollar amounts, and timelines.
Output ONLY a valid JSON array of anomaly objects."""


class FinanceAgent:
    """Finance Agent — runs on GPT-4o-mini instead of Gemini."""

    MODEL = "gpt-4o-mini"

    def __init__(self):
        self.domain = "finance"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.last_report: AgentReport | None = None

    def load_data(self) -> dict:
        """Load and parse the three finance CSV files into a structured dict."""
        data: dict = {"data_sources": []}

        # Transactions ledger
        tx_path = DATA_DIR / "deadpool_finance_data.csv"
        if tx_path.exists():
            df = pd.read_csv(tx_path)
            data["transactions"] = df.to_dict(orient="records")
            data["data_sources"].append("deadpool_finance_data.csv")
        else:
            data["transactions"] = []

        # Revenue pipeline
        pipeline_path = DATA_DIR / "deadpool_revenue_pipeline.csv"
        if pipeline_path.exists():
            df = pd.read_csv(pipeline_path)
            data["revenue_pipeline"] = df.to_dict(orient="records")
            data["data_sources"].append("deadpool_revenue_pipeline.csv")
        else:
            data["revenue_pipeline"] = []

        # Funding and runway
        runway_path = DATA_DIR / "deadpool_funding_runway.csv"
        if runway_path.exists():
            df = pd.read_csv(runway_path)
            data["funding_runway"] = df.to_dict(orient="records")
            data["data_sources"].append("deadpool_funding_runway.csv")
        else:
            data["funding_runway"] = []

        return data

    def run(self) -> AgentReport:
        data = self.load_data()
        data_json = json.dumps(data, indent=2)

        user_message = (
            f"Analyze the following finance data and return a JSON array of anomalies.\n\n"
            f"```json\n{data_json}\n```\n\n"
            "Return ONLY a valid JSON array. Each element must match this schema:\n"
            "{\n"
            '  "id": "<unique string>",\n'
            '  "agent_domain": "finance",\n'
            '  "severity": <0.0-1.0>,\n'
            '  "confidence": <0.0-1.0>,\n'
            '  "title": "<short title>",\n'
            '  "description": "<1-2 sentence description>",\n'
            '  "affected_entities": ["<name>", ...],\n'
            '  "evidence": {"key": "value"},\n'
            '  "cross_references": ["<domain>", ...]\n'
            "}\n"
            "Return an empty array [] if no anomalies are detected."
        )

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw = response.choices[0].message.content or ""
        anomalies = self._parse_anomalies(raw)

        keys = list(data.keys())
        summary = f"finance data loaded — keys: {keys}, transactions: {len(data.get('transactions', []))}"
        report = AgentReport(
            agent=self.domain,
            anomalies=anomalies,
            raw_data_summary=summary,
            timestamp=datetime.utcnow(),
        )
        self.last_report = report

        from signal_bus import bus
        for anomaly in anomalies:
            bus.publish(anomaly)

        return report

    def _parse_anomalies(self, raw: str) -> list[Anomaly]:
        text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()

        # GPT-4o-mini with json_object mode may wrap the array in a key
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []

        # Unwrap {"anomalies": [...]} or {"results": [...]} if needed
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

        anomalies: list[Anomaly] = []
        for item in parsed:
            if "id" not in item or not item["id"]:
                item["id"] = f"finance_{uuid.uuid4().hex[:8]}"
            item["agent_domain"] = "finance"
            try:
                anomalies.append(Anomaly(**item))
            except Exception:
                pass
        return anomalies
