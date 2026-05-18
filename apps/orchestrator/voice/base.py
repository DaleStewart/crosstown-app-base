from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscriptDelta:
    role: Literal["user", "assistant"]
    text: str
    final: bool = False
    type: Literal["transcript_delta"] = "transcript_delta"


@dataclass
class AudioDelta:
    audio_b64: str
    type: Literal["audio_delta"] = "audio_delta"


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    call_id: str
    type: Literal["tool_call"] = "tool_call"


@dataclass
class Final:
    text: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    type: Literal["final"] = "final"


VoiceEvent = TranscriptDelta | AudioDelta | ToolCall | Final


@runtime_checkable
class VoiceSession(Protocol):
    async def send_audio(self, pcm: bytes) -> None: ...

    async def send_text(self, text: str) -> None: ...

    def events(self) -> AsyncIterator[VoiceEvent]: ...

    async def submit_tool_result(self, call_id: str, result: dict[str, Any]) -> None: ...

    async def cancel(self) -> None:
        """Cancel the in-flight model response.

        Implementations should send the provider's cancellation frame
        (Foundry/OpenAI Realtime: ``response.cancel``) and be a no-op when
        no response is currently streaming. Must be idempotent — the
        orchestrator may call this defensively before forwarding a new
        user turn even when no response is active.
        """
        ...

    async def close(self) -> None: ...


@runtime_checkable
class VoiceProvider(Protocol):
    name: str

    async def open_session(
        self, system_prompt: str, tools: list[ToolSpec]
    ) -> VoiceSession: ...
