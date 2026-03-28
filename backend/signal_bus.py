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
    def __init__(self, max_size: int = 500):
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
        self._events.clear()


# Module-level singleton — import this everywhere
bus = SignalBus()
