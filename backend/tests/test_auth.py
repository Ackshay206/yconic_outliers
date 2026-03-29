"""
test_auth.py — Verify all API keys and tokens are valid before starting Phase 1.

Run with:
    python test_auth.py

All checks are independent — a failure in one does not stop the others.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PASS = "✓"
FAIL = "✗"
SKIP = "–"

results: list[tuple[str, str, str]] = []  # (service, status, message)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
def check_gemini():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        results.append(("Gemini", FAIL, "GOOGLE_API_KEY not set in .env"))
        return
    try:
        import google.genai as genai
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model="gemini-2.5-pro",
            contents="Reply with the single word: ok",
        )
        text = resp.text.strip().lower()
        if "ok" in text:
            results.append(("Gemini", PASS, f"gemini-2.5-pro responded: '{resp.text.strip()}'"))
        else:
            results.append(("Gemini", PASS, f"gemini-2.5-pro reachable, response: '{resp.text.strip()}'"))
    except Exception as exc:
        results.append(("Gemini", FAIL, str(exc)))


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
def check_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        results.append(("OpenAI", FAIL, "OPENAI_API_KEY not set in .env"))
        return
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
            max_tokens=5,
        )
        text = resp.choices[0].message.content.strip()
        results.append(("OpenAI", PASS, f"gpt-4o-mini responded: '{text}'"))
    except Exception as exc:
        results.append(("OpenAI", FAIL, str(exc)))


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
def check_github():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        results.append(("GitHub", FAIL, "GITHUB_TOKEN not set in .env"))
        return
    try:
        from github import Github, GithubException
        g = Github(token)
        user = g.get_user()
        login = user.login
        # Check scopes needed for agents
        rate = g.get_rate_limit()
        results.append(("GitHub", PASS, f"Authenticated as '{login}' | API calls remaining: {rate.core.remaining}"))
    except Exception as exc:
        results.append(("GitHub", FAIL, str(exc)))


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------
def check_slack():
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        results.append(("Slack", FAIL, "SLACK_BOT_TOKEN not set in .env"))
        return
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        client = WebClient(token=token)
        auth = client.auth_test()
        if auth["ok"]:
            # Also verify required scopes by attempting a channels list
            try:
                client.conversations_list(limit=1)
                scope_note = "channels:read scope confirmed"
            except SlackApiError:
                scope_note = "Warning: channels:read scope may be missing"
            results.append(("Slack", PASS, f"Bot '{auth['user']}' in workspace '{auth['team']}' | {scope_note}"))
        else:
            results.append(("Slack", FAIL, f"auth_test returned ok=False: {auth}"))
    except Exception as exc:
        results.append(("Slack", FAIL, str(exc)))


# ---------------------------------------------------------------------------
# Run all checks and print results
# ---------------------------------------------------------------------------
def main():
    print("\n=== DEADPOOL — API Auth Check ===\n")

    check_gemini()
    check_openai()
    check_github()
    check_slack()

    # Print results table
    col_w = 10
    for service, status, message in results:
        print(f"  [{status}] {service:<10} {message}")

    print()
    failures = [s for s, status, _ in results if status == FAIL]
    if failures:
        print(f"  {len(failures)} check(s) failed: {', '.join(failures)}")
        print("  See above for details. Fix .env entries before starting Phase 1.\n")
        sys.exit(1)
    else:
        print("  All checks passed. Ready for Phase 1.\n")


if __name__ == "__main__":
    main()
