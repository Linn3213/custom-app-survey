"""Per-session state: a persistent event log + an in-memory conversation.

The event bus keeps a history so a phone that reconnects (or connects late)
replays everything it missed — the same resilience the real Dispatch flow has.
"""

from __future__ import annotations

import asyncio
import itertools
from collections.abc import AsyncIterator
from typing import Any

from .config import Settings


class EventBus:
    def __init__(self, history_cap: int = 5000):
        self._history: list[dict[str, Any]] = []
        self._subscribers: set[asyncio.Queue] = set()
        self._counter = itertools.count(1)
        self._cap = history_cap

    def emit(self, type_: str, **data: Any) -> dict[str, Any]:
        event = {"id": next(self._counter), "type": type_, **data}
        self._history.append(event)
        if len(self._history) > self._cap:
            self._history = self._history[-self._cap :]
        for queue in list(self._subscribers):
            queue.put_nowait(event)
        return event

    async def subscribe(self, last_id: int = 0) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        try:
            sent = last_id
            for event in [e for e in self._history if e["id"] > last_id]:
                sent = max(sent, event["id"])
                yield event
            while True:
                event = await queue.get()
                if event["id"] <= sent:
                    continue
                sent = event["id"]
                yield event
        finally:
            self._subscribers.discard(queue)


class Session:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bus = EventBus()
        self.messages: list[dict[str, Any]] = []
        self.status = "idle"
        self.auto_approve = settings.auto_approve_default
        self.pending: dict[str, asyncio.Future] = {}
        self.task: asyncio.Task | None = None

    def set_status(self, status: str) -> None:
        self.status = status
        self.bus.emit("status", status=status)

    def resolve_approval(self, tool_use_id: str, decision: str) -> bool:
        future = self.pending.get(tool_use_id)
        if future is None or future.done():
            return False
        future.set_result(decision)
        return True

    async def interrupt(self) -> None:
        for future in list(self.pending.values()):
            if not future.done():
                future.set_result("deny")
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except (asyncio.CancelledError, Exception):
                pass


class SessionManager:
    """A single persistent session — one thread between phone and computer."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session(self.settings)
        return self._session
