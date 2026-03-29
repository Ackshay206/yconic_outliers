"""
Retrieve all commit history and GitHub Actions pipeline history from a GitHub repository.

Secrets are loaded from a .env file in the same directory.
The script prompts for all inputs interactively at runtime.

Setup:
    1. Create a .env file with: GITHUB_TOKEN=ghp_xxxx
    2. pip install requests python-dotenv
    3. python get_commit_history.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from the script's directory
load_dotenv(Path(__file__).parent / ".env")


def prompt(label: str, default: str | None = None, required: bool = True) -> str | None:
    hint = f" [{default}]" if default else (" (optional, press Enter to skip)" if not required else "")
    value = input(f"{label}{hint}: ").strip()
    if not value:
        if default:
            return default
        if required:
            print(f"  '{label}' is required.")
            sys.exit(1)
        return None
    return value


def github_get(url: str, headers: dict, params: dict | None = None) -> requests.Response:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:
        sys.exit("Error: Unauthorized. Check your GITHUB_TOKEN in .env.")
    if response.status_code == 404:
        sys.exit(f"Error: Resource not found at {url}. Repo may be private or not exist.")
    if response.status_code == 403:
        reset = response.headers.get("X-RateLimit-Reset")
        reset_time = datetime.fromtimestamp(int(reset)).strftime("%H:%M:%S") if reset else "unknown"
        sys.exit(f"Error: Rate limit exceeded. Resets at {reset_time}. Add GITHUB_TOKEN to .env.")
    if not response.ok:
        sys.exit(f"Error {response.status_code}: {response.json().get('message', 'Unknown error')}")
    return response


def get_all_commits(repo: str, headers: dict, branch: str | None) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/commits"
    params: dict = {"per_page": 100}
    if branch:
        params["sha"] = branch

    commits = []
    page = 1

    while True:
        params["page"] = page
        response = github_get(url, headers, params)
        batch = response.json()
        if not batch:
            break

        commits.extend(batch)
        print(f"  Fetched page {page} ({len(commits)} commits so far)...", end="\r")

        if "next" not in response.links:
            break
        page += 1

    print()
    return commits


def get_all_workflow_runs(repo: str, headers: dict, branch: str | None) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    params: dict = {"per_page": 100}
    if branch:
        params["branch"] = branch

    runs = []
    page = 1

    while True:
        params["page"] = page
        response = github_get(url, headers, params)
        data = response.json()
        batch = data.get("workflow_runs", [])
        if not batch:
            break

        runs.extend(batch)
        print(f"  Fetched page {page} ({len(runs)} runs so far)...", end="\r")

        if "next" not in response.links:
            break
        page += 1

    print()
    return runs


def format_commit(raw: dict) -> dict:
    commit = raw.get("commit", {})
    author = commit.get("author", {})
    committer = commit.get("committer", {})
    return {
        "sha": raw.get("sha"),
        "short_sha": raw.get("sha", "")[:7],
        "message": commit.get("message", "").splitlines()[0],
        "author_name": author.get("name"),
        "author_email": author.get("email"),
        "author_date": author.get("date"),
        "committer_name": committer.get("name"),
        "committer_date": committer.get("date"),
        "url": raw.get("html_url"),
    }


def format_workflow_run(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "workflow_name": raw.get("display_title"),
        "status": raw.get("status"),        # queued | in_progress | completed
        "conclusion": raw.get("conclusion"), # success | failure | cancelled | skipped | None
        "branch": raw.get("head_branch"),
        "commit_sha": raw.get("head_sha", "")[:7],
        "event": raw.get("event"),           # push | pull_request | schedule | workflow_dispatch ...
        "run_number": raw.get("run_number"),
        "run_attempt": raw.get("run_attempt"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "run_started_at": raw.get("run_started_at"),
        "url": raw.get("html_url"),
        "actor": raw.get("actor", {}).get("login"),
    }


def main():
    print("=== GitHub Repository History Fetcher ===\n")

    # Inputs
    repo = prompt("Repository (owner/repo or full GitHub URL)")
    if repo.startswith("http"):
        parts = repo.rstrip("/").split("github.com/")[-1].split("/")
        repo = f"{parts[0]}/{parts[1]}"
    if "/" not in repo:
        sys.exit("Error: Must be in 'owner/repo' format.")

    branch = prompt("Branch (default branch if blank)", required=False)
    commits_file = prompt("Commits output file (e.g. commits.json, blank to print)", required=False)
    runs_file = prompt("Workflow runs output file (e.g. runs.json, blank to print)", required=False)
    raw_mode = prompt("Save full raw API response? (y/N)", default="N").lower() == "y"

    # Secret from .env (not prompted)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("\n  Token loaded from .env.")
    else:
        print("\n  No GITHUB_TOKEN found in .env — using unauthenticated (60 req/hr limit).")

    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Fetch commits
    print(f"\n[1/2] Fetching commits for {repo}" + (f" on branch '{branch}'" if branch else "") + "...")
    raw_commits = get_all_commits(repo, headers, branch)
    commits = raw_commits if raw_mode else [format_commit(c) for c in raw_commits]
    print(f"  Total commits: {len(commits)}")

    # Fetch GitHub Actions runs
    print(f"\n[2/2] Fetching GitHub Actions runs for {repo}" + (f" on branch '{branch}'" if branch else "") + "...")
    raw_runs = get_all_workflow_runs(repo, headers, branch)
    runs = raw_runs if raw_mode else [format_workflow_run(r) for r in raw_runs]
    print(f"  Total workflow runs: {len(runs)}")

    print()
    # Save / print commits
    if commits_file:
        with open(commits_file, "w", encoding="utf-8") as f:
            json.dump(commits, f, indent=2, ensure_ascii=False)
        print(f"Commits saved to {commits_file}")
    else:
        print("--- COMMITS ---")
        for c in (commits if not raw_mode else [format_commit(c) for c in commits]):
            print(f"  {c['short_sha']}  {c['author_date']}  {c['author_name']:<20}  {c['message']}")

    # Save / print workflow runs
    if runs_file:
        with open(runs_file, "w", encoding="utf-8") as f:
            json.dump(runs, f, indent=2, ensure_ascii=False)
        print(f"Workflow runs saved to {runs_file}")
    else:
        print("\n--- WORKFLOW RUNS ---")
        for r in (runs if not raw_mode else [format_workflow_run(r) for r in runs]):
            conclusion = r['conclusion'] or r['status']
            print(f"  #{r['run_number']}  {r['created_at']}  {r['name']:<30}  {conclusion}")


if __name__ == "__main__":
    main()
