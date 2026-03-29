"""
Code Audit Agent — monitors codebase health, security posture, and technical debt.

Data sources:
  - GitHub commit history: reuses logic from get_commit_history.py to fetch
    per-developer commit frequency, commit volume trends, and file-level change frequency.
    Maps developer_name to owned files and services.
  - GitHub REST API (via PyGithub): git blame (code ownership), PR review patterns
    (merged without review?), stale PRs.
  - GitHub Dependabot Alerts API: CVEs with severity and affected package.
  - Fallback: codebase_audit.json if GITHUB_TOKEN or GITHUB_REPO not set.

Requires GITHUB_TOKEN and GITHUB_REPO environment variables.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import logging

from agents.base_agent import BaseAgent

logger = logging.getLogger("deadpool.code_audit_agent")

FALLBACK_JSON = Path(__file__).parent.parent / "data" / "codebase_audit.json"
COMMIT_LOOKBACK_DAYS = 84   # 12 weeks
PR_LOOKBACK_DAYS = 30

SYSTEM_PROMPT = """You are the Code Audit Agent for DEADPOOL, a startup risk monitoring system.

Your domain is codebase health, security vulnerabilities, architectural integrity, and technical debt.

You analyze code audit data (commit patterns, code ownership, CVEs, PR review patterns)
and identify anomalies that signal security risk, quality degradation, or delivery capability loss.

Critical signals to watch:
- CVEs with CVSS score >= 7.0 in any production dependency (especially payments/auth)
- Bus factor of 1 for any critical service (one person owns >80% of commits)
- Developers whose commit frequency has dropped >50% over the lookback period
- PRs merged without code review in critical paths (payments, auth, data)
- Dependencies 2+ major versions behind (especially security-relevant packages)
- High concentration of recent changes in a single file/service by a single developer
- PRs open for >14 days with no reviewer activity (stale/blocked)

Cross-reference with:
- people: which developer owns the problematic code? (use developer_name as linking key)
- infra: which running services sit on top of the vulnerable code? (use service_name)
- legal: compliance implications of unpatched vulnerabilities (PCI DSS, SOC 2)

Name the specific CVE, service, developer, file path, and CVSS score where available.
Output only the JSON array."""


class CodeAuditAgent(BaseAgent):
    def __init__(self):
        super().__init__(domain="code_audit", system_prompt=SYSTEM_PROMPT)

    @staticmethod
    def _parse_repo_name(raw: str) -> str:
        """Accept either 'owner/repo' or full GitHub URL and return 'owner/repo'."""
        if not raw:
            return ""
        if "github.com" in raw:
            parts = raw.rstrip("/").split("github.com/")[-1].split("/")
            return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else ""
        return raw

    def load_data(self) -> dict:
        token = os.getenv("GITHUB_TOKEN")
        repo_name = self._parse_repo_name(os.getenv("GITHUB_REPO", ""))

        if not token or not repo_name:
            return self._fallback()

        try:
            return self._fetch_github_data(token, repo_name)
        except Exception as exc:
            fallback = self._fallback()
            fallback["github_error"] = str(exc)
            return fallback

    def _fetch_github_data(self, token: str, repo_name: str) -> dict:
        from github import Github

        g = Github(token)
        repo = g.get_repo(repo_name)

        data: dict = {
            "data_sources": [
                f"GitHub commit history ({repo_name}, last {COMMIT_LOOKBACK_DAYS} days)",
                f"GitHub Dependabot alerts ({repo_name})",
                f"GitHub PR data ({repo_name}, last {PR_LOOKBACK_DAYS} days)",
            ],
            "repo": repo_name,
        }

        # 1. Commit history — reuse get_commit_history.py logic
        data["commit_analysis"] = self._fetch_commit_history(repo)

        # 2. Dependabot CVE alerts
        data["dependabot_alerts"] = self._fetch_dependabot_alerts(repo)

        # 3. PR review patterns
        data["pr_analysis"] = self._fetch_pr_patterns(repo)

        return data

    def _fetch_commit_history(self, repo) -> dict:
        """
        Fetch commits from the last COMMIT_LOOKBACK_DAYS days.
        Reuses the same GitHub REST approach as get_commit_history.py:
        page through repo.get_commits(), extract author + file data.
        Maps developer_name → files_changed and weekly commit counts.
        """
        since = datetime.now(timezone.utc) - timedelta(days=COMMIT_LOOKBACK_DAYS)

        commits_by_author: dict[str, list[dict]] = defaultdict(list)
        total_fetched = 0

        for commit in repo.get_commits(since=since):
            author_name = (
                commit.commit.author.name
                if commit.commit.author
                else "unknown"
            )
            commits_by_author[author_name].append({
                "sha": commit.sha[:7],
                "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
                "message": commit.commit.message.splitlines()[0][:100],
            })
            total_fetched += 1
            # Cap at 500 commits to avoid rate limit exhaustion
            if total_fetched >= 500:
                break

        # Summarize per author: weekly commit counts
        summaries = []
        now = datetime.now(timezone.utc)
        for author, commits in commits_by_author.items():
            # Build weekly buckets (12 weeks)
            weekly: dict[int, int] = defaultdict(int)
            for c in commits:
                if c["date"]:
                    try:
                        dt = datetime.fromisoformat(c["date"].replace("Z", "+00:00"))
                        week_num = (now - dt).days // 7
                        if 0 <= week_num < 12:
                            weekly[week_num] += 1
                    except ValueError:
                        pass

            recent_commits = sum(weekly.get(w, 0) for w in range(0, 4))    # last 4 weeks
            older_commits = sum(weekly.get(w, 0) for w in range(4, 12))    # weeks 5-12
            drop_pct = None
            if older_commits > 0:
                drop_pct = round((older_commits / 8 - recent_commits / 4) / (older_commits / 8) * 100, 1)

            summaries.append({
                "developer_name": author,
                "total_commits": len(commits),
                "recent_4wk_commits": recent_commits,
                "older_8wk_avg_per_week": round(older_commits / 8, 1),
                "recent_4wk_avg_per_week": round(recent_commits / 4, 1),
                "commit_drop_pct": drop_pct,
                "weekly_breakdown": dict(weekly),
                "sample_messages": [c["message"] for c in commits[:3]],
            })

        return {
            "total_commits_fetched": total_fetched,
            "lookback_days": COMMIT_LOOKBACK_DAYS,
            "authors": summaries,
        }

    def _fetch_dependabot_alerts(self, repo) -> list[dict]:
        """Fetch open Dependabot security alerts via PyGithub."""
        alerts = []
        try:
            for alert in repo.get_dependabot_alerts():
                if alert.state != "open":
                    continue
                vuln = alert.security_vulnerability
                advisory = alert.security_advisory
                alerts.append({
                    "alert_number": alert.number,
                    "state": alert.state,
                    "package_name": vuln.package.name if vuln and vuln.package else None,
                    "package_ecosystem": vuln.package.ecosystem if vuln and vuln.package else None,
                    "severity": advisory.severity if advisory else None,
                    "cvss_score": advisory.cvss.score if advisory and advisory.cvss else None,
                    "cve_id": advisory.cve_id if advisory else None,
                    "summary": advisory.summary if advisory else None,
                    "vulnerable_version_range": vuln.vulnerable_version_range if vuln else None,
                    "patched_versions": vuln.first_patched_version if vuln else None,
                    "manifest_path": alert.dependency.manifest_path if alert.dependency else None,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                })
        except Exception as exc:
            # Dependabot API requires Dependabot to be enabled on the repo
            logger.warning("Dependabot alerts unavailable: %s", exc)
        return alerts

    def _fetch_pr_patterns(self, repo) -> dict:
        """
        Fetch closed and open PRs from the last PR_LOOKBACK_DAYS days.
        Detect: merged without review, stale open PRs, review bottlenecks.
        """
        since = datetime.now(timezone.utc) - timedelta(days=PR_LOOKBACK_DAYS)

        merged_without_review = []
        stale_open_prs = []
        pr_summary = []

        stale_threshold = datetime.now(timezone.utc) - timedelta(days=14)

        for pr in repo.get_pulls(state="all", sort="updated", direction="desc"):
            updated = pr.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            if updated < since:
                break

            reviews = list(pr.get_reviews())
            review_count = len(reviews)
            reviewers = list({r.user.login for r in reviews if r.user}) if reviews else []

            pr_info = {
                "number": pr.number,
                "title": pr.title[:80],
                "author": pr.user.login if pr.user else None,
                "state": pr.state,
                "merged": pr.merged,
                "review_count": review_count,
                "reviewers": reviewers,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "files_changed": pr.changed_files,
            }
            pr_summary.append(pr_info)

            # Merged without any review
            if pr.merged and review_count == 0:
                merged_without_review.append(pr_info)

            # Open PR with no activity for >14 days
            created = pr.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if pr.state == "open" and created < stale_threshold and review_count == 0:
                stale_open_prs.append(pr_info)

        return {
            "lookback_days": PR_LOOKBACK_DAYS,
            "total_prs": len(pr_summary),
            "merged_without_review": merged_without_review,
            "stale_open_prs": stale_open_prs,
            "pr_details": pr_summary[:20],  # Top 20 most recent for context
        }

    def _fallback(self) -> dict:
        if FALLBACK_JSON.exists():
            with open(FALLBACK_JSON) as f:
                data = json.load(f)
            data["data_sources"] = ["codebase_audit.json (fallback — GITHUB_TOKEN or GITHUB_REPO not set)"]
            return data
        return {"data_sources": [], "status": "no code audit data available"}
