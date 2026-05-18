from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from agent.tools import ToolRegistry
from storage.cosmos import ConversationStore
from voice.base import (
    AudioDelta,
    Final,
    ToolCall,
    ToolSpec,
    TranscriptDelta,
    VoiceEvent,
)


class FakeSession:
    def __init__(self) -> None:
        self.sent_text: list[str] = []
        self.sent_audio: list[bytes] = []
        self.tool_results: list[tuple[str, dict[str, Any]]] = []
        self._events: list[VoiceEvent] = []
        self.closed = False
        self.cancel_calls = 0
        self.committed = 0

    def queue(self, ev: VoiceEvent) -> None:
        self._events.append(ev)

    async def send_text(self, text: str) -> None:
        self.sent_text.append(text)

    async def send_audio(self, pcm: bytes) -> None:
        self.sent_audio.append(pcm)

    async def submit_tool_result(self, call_id: str, result: dict[str, Any]) -> None:
        self.tool_results.append((call_id, result))

    async def cancel(self) -> None:
        self.cancel_calls += 1

    async def commit_audio(self) -> None:
        self.committed += 1

    async def events(self) -> AsyncIterator[VoiceEvent]:
        for ev in list(self._events):
            yield ev

    async def close(self) -> None:
        self.closed = True


class FakeProvider:
    name = "fake"

    def __init__(self, session: FakeSession) -> None:
        self._session = session
        self.opened: list[tuple[str, list[ToolSpec]]] = []

    async def open_session(
        self, system_prompt: str, tools: list[ToolSpec]
    ) -> FakeSession:
        self.opened.append((system_prompt, list(tools)))
        return self._session


class FakeContainer:
    def __init__(self) -> None:
        self.items: dict[str, dict[str, Any]] = {}

    async def upsert_item(self, body: dict[str, Any]) -> dict[str, Any]:
        self.items[body["id"]] = body
        return body

    async def read_item(self, item: str, partition_key: str) -> dict[str, Any]:
        if item not in self.items:
            raise KeyError(item)
        return self.items[item]


@pytest.fixture
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def fake_provider(fake_session: FakeSession) -> FakeProvider:
    return FakeProvider(fake_session)


@pytest.fixture
def fake_store() -> ConversationStore:
    return ConversationStore(FakeContainer())


@pytest.fixture
def tool_registry() -> ToolRegistry:
    reg = ToolRegistry("http://fake-log-analyst")
    reg._specs = [  # noqa: SLF001
        ToolSpec(
            name="search_logs",
            description="search",
            parameters={"type": "object", "properties": {}},
        )
    ]
    reg._loaded = True  # noqa: SLF001
    return reg


__all__ = [
    "AudioDelta",
    "FakeProvider",
    "FakeSession",
    "Final",
    "ToolCall",
    "TranscriptDelta",
]
