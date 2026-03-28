"""
Finance Agent — monitors cash flow, runway, revenue concentration, and funding terms.
"""
from __future__ import annotations

import json
import os

from agents.base_agent import BaseAgent

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/financials.json")

SYSTEM_PROMPT = """You are the Finance Agent for DEADPOOL, a startup risk monitoring system.

Your domain is cash flow, runway, revenue concentration, burn rate, and investor terms.

You analyze financial data and identify anomalies that signal existential financial risk.

Critical signals to watch:
- Runway dropping below 6 months (red alert below 3 months)
- Revenue concentration: any single client representing >30% of revenue
- Burn rate acceleration month-over-month
- Investor clause thresholds approaching (e.g., down-round clauses, anti-dilution triggers)
- Payment delays from major clients
- Refund liabilities from contract breaches

Cross-reference with:
- legal: contract values, renewal dates, and breach terms for concentrated revenue clients
- people: headcount costs and hiring pipeline expenses
- product: health of revenue-generating features

Name specific clients, dollar amounts, and timelines. Output only the JSON array."""

class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="finance", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
