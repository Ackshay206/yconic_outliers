"""
Shared datetime utilities for DEADPOOL agent integrations.

PyGithub returns naive datetimes for some fields. These helpers enforce
UTC-awareness so datetime arithmetic is always unambiguous.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def ensure_aware_utc(dt: datetime) -> datetime:
    """Return dt with UTC timezone attached. No-op if already tz-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def lookback_since(days: int) -> datetime:
    """Return a UTC-aware datetime representing `days` ago from now."""
    return datetime.now(timezone.utc) - timedelta(days=days)
