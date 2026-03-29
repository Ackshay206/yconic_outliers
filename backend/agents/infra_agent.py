"""
Infra Agent — monitors system reliability, deployment frequency, and CI/CD health.

Data sources:
  - GitHub Actions API (via PyGithub): workflow runs, deploy frequency,
    pass/fail rates, duration trends per service.
  - Fallback: infrastructure.json if GITHUB_TOKEN or GITHUB_REPO not set.

Requires GITHUB_TOKEN and GITHUB_REPO (e.g. "owner/repo") environment variables.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agents.base_agent import BaseAgent

FALLBACK_JSON = Path(__file__).parent.parent / "data" / "infrastructure.json"
LOOKBACK_DAYS = 30

SYSTEM_PROMPT = """You are the Infrastructure Agent for DEADPOOL, a startup risk monitoring system.

Your domain is system reliability, deployment operations, and runtime performance.

You analyze infrastructure data (deploy frequency, CI/CD health, workflow pass/fail rates)
and identify anomalies that signal service degradation, delivery risk, or operational failure.

Critical signals to watch:
- Deploy frequency dropping to zero for any service over a 2-week window
- CI/CD failure rate exceeding 20% for any workflow
- Workflow run duration increasing significantly (2x baseline = performance regression)
- Feature completion stalling (repeated workflow failures blocking delivery)
- A single service showing consistently failing pipelines

Cross-reference with:
- code_audit: is code quality causing the CI failures?
- people: who owns the failing service and are they still active?
- legal: which SLA obligations are at risk from this degradation?

Name the specific workflow/service, cite failure counts, and flag deadline risk.
Output only the JSON array."""


class InfraAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="infra", system_prompt=SYSTEM_PROMPT)

    def load_data(self) -> dict:
        """
        Load infrastructure data from two sources and merge them.

        ``infrastructure.json`` is always loaded as the static baseline (service
        topology, SLA obligations, deployment targets). If ``GITHUB_TOKEN`` and
        ``GITHUB_REPO`` are set, live GitHub Actions workflow run data is fetched
        on top and added under the ``github_actions`` key. This dual-source
        approach means the agent always has *something* to analyse even without
        GitHub credentials.
        """
        # Always load infrastructure.json as primary static source
        data = self._load_infrastructure_json()

        # Also pull live GitHub Actions on top if credentials are set
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO", "")

        if token and repo_name:
            try:
                github_data = self._fetch_github_actions(token, repo_name)
                data["github_actions"] = github_data.get("workflows", [])
                data["data_sources"].append(github_data["data_sources"][0])
            except Exception as exc:
                data["github_actions_error"] = str(exc)

        return data


    def _fetch_github_actions(self, token: str, repo_name: str) -> dict:
        from github import Github

        g = Github(token)
        repo = g.get_repo(repo_name)

        since = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

        # Fetch all workflow runs in the lookback window
        runs_by_workflow: dict[str, list[dict]] = defaultdict(list)

        for run in repo.get_workflow_runs():
            run_dt = run.created_at
            # PyGithub returns naive datetimes for some fields; make aware
            if run_dt.tzinfo is None:
                run_dt = run_dt.replace(tzinfo=timezone.utc)
            if run_dt < since:
                break  # Runs are returned newest-first; stop when past the window

            duration_sec = None
            if run.updated_at and run.created_at:
                updated = run.updated_at
                created = run.created_at
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                duration_sec = int((updated - created).total_seconds())

            runs_by_workflow[run.name].append({
                "id": run.id,
                "status": run.status,
                "conclusion": run.conclusion,
                "branch": run.head_branch,
                "event": run.event,
                "created_at": run.created_at.isoformat(),
                "duration_sec": duration_sec,
                "run_number": run.run_number,
                "actor": run.actor.login if run.actor else None,
            })

        # Summarize per workflow
        workflow_summaries = []
        for workflow_name, runs in runs_by_workflow.items():
            total = len(runs)
            failures = sum(1 for r in runs if r["conclusion"] == "failure")
            successes = sum(1 for r in runs if r["conclusion"] == "success")
            durations = [r["duration_sec"] for r in runs if r["duration_sec"] is not None]
            avg_duration = int(sum(durations) / len(durations)) if durations else None

            # Deploy frequency: runs per week
            runs_per_week = round(total / (LOOKBACK_DAYS / 7), 1)

            workflow_summaries.append({
                "workflow_name": workflow_name,
                "total_runs": total,
                "successes": successes,
                "failures": failures,
                "failure_rate": round(failures / total, 3) if total else 0,
                "runs_per_week": runs_per_week,
                "avg_duration_sec": avg_duration,
                "recent_runs": runs[:5],  # Last 5 for evidence
            })

        return {
            "data_sources": [f"GitHub Actions API ({repo_name}, last {LOOKBACK_DAYS} days)"],
            "repo": repo_name,
            "lookback_days": LOOKBACK_DAYS,
            "workflows": workflow_summaries,
        }

    def _load_infrastructure_json(self) -> dict:
        """Load the static infrastructure baseline from ``data/infrastructure.json``."""
        if FALLBACK_JSON.exists():
            with open(FALLBACK_JSON) as f:
                data = json.load(f)
            data["data_sources"] = ["infrastructure.json"]
            return data
        return {"data_sources": []}
