"""In-memory async pub/sub bus for phone call transcript events.

Subscribers receive events via per-client asyncio.Queue instances.
The bus is a singleton — import ``transcript_bus`` and use directly.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)


class TranscriptBus:
    """Broadcast transcript events to all active SSE subscribers."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def publish(self, event: dict[str, Any]) -> None:
        """Push *event* to every active subscriber queue."""
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            dead: list[asyncio.Queue] = []
            for q in self._subscribers:
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    dead.append(q)
            for q in dead:
                self._subscribers.discard(q)
                logger.warning("TranscriptBus: dropped slow subscriber")

    @asynccontextmanager
    async def subscribe(self) -> AsyncGenerator[asyncio.Queue, None]:
        """Context manager that yields a Queue receiving broadcast events."""
        q: asyncio.Queue = asyncio.Queue(maxsize=256)
        async with self._lock:
            self._subscribers.add(q)
        logger.info(
            "TranscriptBus: subscriber added (total=%d)", len(self._subscribers)
        )
        try:
            yield q
        finally:
            async with self._lock:
                self._subscribers.discard(q)
            logger.info(
                "TranscriptBus: subscriber removed (total=%d)",
                len(self._subscribers),
            )

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


# Module-level singleton — import this directly.
transcript_bus = TranscriptBus()
