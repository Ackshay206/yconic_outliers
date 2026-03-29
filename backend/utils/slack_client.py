"""
Slack API client for the People Agent.

Pulls raw message text from Slack channels grouped by developer.
The People Agent's Claude call handles all sentiment/emotion analysis
directly — this module is purely a data fetcher.

Requires SLACK_BOT_TOKEN with scopes:
  channels:history, channels:read, users:read, groups:history, groups:read

Falls back gracefully when the token is not configured.
"""
from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("deadpool.slack")


class SlackClient:
    """Fetches raw Slack message text grouped by user for sentiment analysis."""

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self._client = None
        self._connected = False

        if self.token:
            try:
                from slack_sdk import WebClient

                self._client = WebClient(token=self.token)
                auth = self._client.auth_test()
                if auth["ok"]:
                    self._connected = True
                    logger.info("Slack connected as %s in workspace %s",
                                auth.get("user"), auth.get("team"))
                else:
                    logger.warning("Slack auth_test failed: %s", auth)
            except ImportError:
                logger.error("slack-sdk not installed — run: pip install slack-sdk")
            except Exception as exc:
                logger.warning("Slack connection failed: %s", exc)

    @property
    def is_connected(self) -> bool:
        return self._connected

    def status(self) -> dict[str, Any]:
        """Return connection status (for /api/slack/status)."""
        if not self.token:
            return {"connected": False, "reason": "SLACK_BOT_TOKEN not set"}
        if not self._connected:
            return {"connected": False, "reason": "auth_test failed or slack-sdk missing"}
        try:
            auth = self._client.auth_test()
            return {
                "connected": True,
                "workspace": auth.get("team"),
                "bot_user": auth.get("user"),
                "bot_id": auth.get("bot_id"),
            }
        except Exception as exc:
            return {"connected": False, "reason": str(exc)}

    # ------------------------------------------------------------------
    # Main entry point: fetch raw messages grouped by user
    # ------------------------------------------------------------------

    def fetch_messages_by_user(
        self,
        days: int = 42,
        user_email_map: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """
        Pull Slack messages for the workspace over *days*, group by user,
        and return raw message text + metadata.

        Returns None when not connected (caller should proceed without Slack data).

        Output format per user:
        {
          "Developer Name": {
            "total_messages": 142,
            "messages": [
              {"text": "...", "channel": "#engineering", "ts": "2026-03-21T10:30:00", "is_thread_reply": false},
              ...
            ]
          }
        }
        """
        if not self._connected:
            return None

        try:
            users = self._list_users()
            channels = self._list_channels()
            oldest = _ts(datetime.now(timezone.utc) - timedelta(days=days))

            per_user: dict[str, list[dict]] = defaultdict(list)

            for ch in channels:
                self._collect_messages(ch["id"], ch["name"], oldest, per_user)

            return self._compile(per_user, users, user_email_map)
        except Exception as exc:
            logger.exception("Failed to fetch Slack messages: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Internal: Slack API calls
    # ------------------------------------------------------------------

    def _list_users(self) -> list[dict]:
        """Return non-bot, non-deleted workspace members."""
        members = []
        cursor = None
        while True:
            resp = self._client.users_list(cursor=cursor, limit=200)
            for m in resp["members"]:
                if m.get("is_bot") or m.get("deleted") or m.get("id") == "USLACKBOT":
                    continue
                members.append({
                    "id": m["id"],
                    "name": m.get("real_name") or m.get("name", ""),
                    "email": m.get("profile", {}).get("email", ""),
                })
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        return members

    def _list_channels(self) -> list[dict]:
        """Return public + private channels the bot is a member of."""
        channels = []
        for types in ("public_channel", "private_channel"):
            cursor = None
            while True:
                resp = self._client.conversations_list(
                    types=types, cursor=cursor, limit=200, exclude_archived=True,
                )
                for ch in resp.get("channels", []):
                    if ch.get("is_member"):
                        channels.append({"id": ch["id"], "name": ch["name"]})
                cursor = resp.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
        return channels

    def _collect_messages(
        self,
        channel_id: str,
        channel_name: str,
        oldest: str,
        per_user: dict[str, list[dict]],
    ) -> None:
        """Page through channel history, collecting raw message text per user."""
        cursor = None
        while True:
            resp = self._client.conversations_history(
                channel=channel_id, oldest=oldest, cursor=cursor, limit=200,
            )
            for msg in resp.get("messages", []):
                uid = msg.get("user")
                text = msg.get("text", "").strip()
                if not uid or msg.get("subtype") or not text:
                    continue

                ts = float(msg["ts"])
                per_user[uid].append({
                    "text": text,
                    "channel": f"#{channel_name}",
                    "ts": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_thread_reply": bool(
                        msg.get("thread_ts") and msg["thread_ts"] != msg["ts"]
                    ),
                })

            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
            time.sleep(0.3)

    # ------------------------------------------------------------------
    # Compile: resolve user IDs → names and structure output
    # ------------------------------------------------------------------

    def _compile(
        self,
        per_user: dict[str, list[dict]],
        users: list[dict],
        email_map: dict[str, str] | None,
    ) -> dict[str, Any]:
        uid_to_name: dict[str, str] = {}
        for u in users:
            resolved = u["name"]
            if email_map and u["email"] in email_map:
                resolved = email_map[u["email"]]
            uid_to_name[u["id"]] = resolved

        result: dict[str, Any] = {}
        for uid, messages in per_user.items():
            name = uid_to_name.get(uid, uid)
            messages.sort(key=lambda m: m["ts"])
            result[name] = {
                "total_messages": len(messages),
                "messages": messages,
            }

        return result


def _ts(dt: datetime) -> str:
    """Convert a datetime to a Slack-style epoch timestamp string."""
    return str(int(dt.timestamp()))


# Singleton — initialized once, importable everywhere
slack = SlackClient()
