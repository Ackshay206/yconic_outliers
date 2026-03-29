"""
Signal bus — in-memory event queue for anomalies detected by specialist agents.
Supports publish/subscribe semantics and recent event retrieval.
"""
from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime

from models import Anomaly


class SignalBus:
    """
    In-memory publish/subscribe event bus for anomaly streaming.

    Agents call ``publish()`` after detecting an anomaly. The SSE endpoint
    subscribes via ``subscribe()`` and streams events to connected dashboard
    clients. The ring buffer (``_events``) retains the last ``max_size``
    anomalies so that clients connecting mid-session can catch up on recent
    events via ``get_recent()``.

    Thread safety: ``put_nowait`` is used for non-blocking puts; if a subscriber
    queue is full the event is dropped for that subscriber rather than blocking
    the publishing agent.
    """

    def __init__(self, max_size: int = 500) -> None:
        """
        Args:
            max_size: Ring-buffer capacity. Once full, the oldest event is
                      evicted to make room for the newest. 500 events covers
                      approximately one full analysis cycle across all agents.
        """
        self._events: deque[Anomaly] = deque(maxlen=max_size)
        self._subscribers: list[asyncio.Queue] = []

    def publish(self, anomaly: Anomaly) -> None:
        """Publish an anomaly to the bus and notify all subscribers."""
        self._events.append(anomaly)
        for q in self._subscribers:
            # Non-blocking put; drop if subscriber queue is full
            try:
                q.put_nowait(anomaly)
            except asyncio.QueueFull:
                pass

    def subscribe(self) -> asyncio.Queue:
        """Create a new subscriber queue and return it."""
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        """Remove a subscriber queue."""
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    def get_recent(self, n: int = 50) -> list[Anomaly]:
        """Return the n most recent anomalies."""
        events = list(self._events)
        return events[-n:]

    def clear(self) -> None:
        """Flush all retained events from the ring buffer (used in tests)."""
        self._events.clear()


# Module-level singleton — import this everywhere
bus = SignalBus()
