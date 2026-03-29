"""
Legal Agent — monitors contracts, compliance obligations, and regulatory exposure.

Data sources:
  - PDF contracts: extracted text from uploaded contract PDFs via pdfplumber
  - Web search: duckduckgo-search for regulatory lookups (no API key needed)
  - Fallback: contracts.json if no PDFs are present

Requires GOOGLE_API_KEY (inherited from BaseAgent / Gemini).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from agents.base_agent import BaseAgent

DATA_PATH = Path(__file__).parent.parent / "data" / "contracts.json"
PDF_DIR = Path(__file__).parent.parent / "data"

SYSTEM_PROMPT = """You are the Legal Agent for DEADPOOL, a startup risk monitoring system.

Your domain is contracts, compliance, intellectual property, and regulatory exposure.

You analyze contract data (deadlines, delivery clauses, SLA terms, compliance obligations)
and identify anomalies that signal breach risk, liability exposure, or regulatory non-compliance.

Critical signals to watch:
- Contract delivery deadlines within 30 days where delivery is at risk
- Contracts with termination-without-penalty clauses where the company may be in breach
- PCI DSS, SOC 2, or GDPR compliance obligations that are unmet
- SLA thresholds that are close to being breached
- Investor agreement clauses that may be triggered (down-round, anti-dilution)
- Refund or penalty liabilities from contract breaches
- Regulatory changes (from web search context) that require compliance action

Cross-reference with:
- finance: financial impact of contract breach (refund liabilities, revenue loss)
- infra: delivery progress on features tied to contractual obligations
- code_audit: compliance requirements mapped to actual code state

Name the specific contract, client, dollar amount, and exact deadline.
Output only the JSON array."""


class LegalAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="legal", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        data: dict = {"data_sources": []}

        # 1. PDF contracts (primary source)
        pdf_texts = self._extract_pdfs()
        if pdf_texts:
            data["contracts_from_pdfs"] = pdf_texts
            data["data_sources"].append(f"PDFs ({len(pdf_texts)} contracts extracted)")
        else:
            # Fallback to JSON
            if DATA_PATH.exists():
                with open(DATA_PATH) as f:
                    data["contracts"] = json.load(f)
                data["data_sources"].append("contracts.json (fallback — no PDFs found)")

        # 2. Web search for relevant regulatory context
        regulatory_context = self._web_search_regulatory()
        if regulatory_context:
            data["regulatory_context"] = regulatory_context
            data["data_sources"].append("duckduckgo web search (regulatory)")

        return data

    def _extract_pdfs(self) -> list[dict]:
        """Extract text from all PDFs in the data directory using PyMuPDF."""
        if not PDF_DIR.exists():
            return []

        pdf_files = list(PDF_DIR.glob("*.pdf"))
        if not pdf_files:
            return []

        try:
            import fitz  # PyMuPDF
        except ImportError:
            return []

        results = []
        for pdf_path in pdf_files:
            try:
                doc = fitz.open(str(pdf_path))
                pages_text = []
                for page in doc:
                    text = page.get_text()
                    if text:
                        pages_text.append(text.strip())
                doc.close()
                full_text = "\n\n".join(pages_text)

                # Gemini 2.5 Flash supports ~1M token context, but large PDFs with
                # boilerplate can easily hit 100K+ chars. 80K chars (~20K tokens) keeps
                # the request well within the model's optimal reasoning window and avoids
                # excessive latency on very long contracts.
                max_chars = 80_000
                if len(full_text) > max_chars:
                    full_text = full_text[:max_chars] + "\n[...truncated for length]"

                results.append({
                    "filename": pdf_path.name,
                    "pages": len(pages_text),
                    "text": full_text,
                })
            except Exception:
                continue

        return results

    def _web_search_regulatory(self) -> list[dict]:
        """Search for recent regulatory news relevant to SaaS compliance."""
        queries = [
            "PCI DSS 4.0 compliance requirements 2026",
            "SOC 2 Type II audit requirements SaaS startup",
            "GDPR enforcement actions SaaS 2026",
        ]
        results = []
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                for query in queries:
                    hits = list(ddgs.text(query, max_results=2))
                    for hit in hits:
                        results.append({
                            "query": query,
                            "title": hit.get("title", ""),
                            "snippet": hit.get("body", "")[:500],
                            "url": hit.get("href", ""),
                        })
        except Exception:
            pass
        return results
