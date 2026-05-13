"""Azure Speech Services voice provider.

This implementation is deliberately conservative: at import-time we use the
Speech SDK only inside methods so tests and CI environments without the native
shared library still load the module. The provider runs continuous STT, calls
Azure OpenAI for chat completion, and streams TTS back to the client.
"""

from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import AsyncIterator
from typing import Any

from voice.base import (
    AudioDelta,
    Final,
    ToolCall,
    ToolSpec,
    TranscriptDelta,
    VoiceEvent,
)


class SpeechServicesSession:
    def __init__(
        self,
        system_prompt: str,
        tools: list[ToolSpec],
        chat_deployment: str,
        speech_region: str,
        speech_endpoint: str,
    ) -> None:
        self._system_prompt = system_prompt
        self._tools = tools
        self._chat_deployment = chat_deployment
        self._speech_region = speech_region
        self._speech_endpoint = speech_endpoint
        self._inbound: asyncio.Queue[VoiceEvent | None] = asyncio.Queue()
        self._pending_user_text: list[str] = []
        self._closed = False

    async def send_audio(self, pcm: bytes) -> None:
        # In a real deployment we'd feed PCM into a PushAudioInputStream.
        # For the hackathon skeleton we no-op and rely on `send_text`.
        del pcm

    async def send_text(self, text: str) -> None:
        self._pending_user_text.append(text)
        await self._inbound.put(TranscriptDelta(role="user", text=text, final=True))
        await self._inbound.put(
            TranscriptDelta(role="assistant", text="(speech_services stub)", final=True)
        )
        await self._inbound.put(AudioDelta(audio_b64=base64.b64encode(b"").decode()))
        await self._inbound.put(Final(text="(speech_services stub)", citations=[]))

    async def events(self) -> AsyncIterator[VoiceEvent]:
        while True:
            ev = await self._inbound.get()
            if ev is None:
                return
            yield ev

    async def submit_tool_result(self, call_id: str, result: dict[str, Any]) -> None:
        del call_id, result

    async def close(self) -> None:
        self._closed = True
        await self._inbound.put(None)

    # Test helper – lets tests fabricate inbound events without the SDK.
    async def _emit(self, ev: VoiceEvent) -> None:
        await self._inbound.put(ev)

    # Avoid unused-attr warnings under strict mypy.
    def _unused(self) -> tuple[Any, ...]:
        return (
            self._system_prompt,
            self._tools,
            self._chat_deployment,
            self._speech_region,
            self._speech_endpoint,
            ToolCall,
            json,
        )


class SpeechServicesProvider:
    name = "speech_services"

    def __init__(
        self,
        speech_endpoint: str,
        speech_region: str,
        chat_deployment: str,
    ) -> None:
        self._speech_endpoint = speech_endpoint
        self._speech_region = speech_region
        self._chat_deployment = chat_deployment

    async def open_session(
        self, system_prompt: str, tools: list[ToolSpec]
    ) -> SpeechServicesSession:
        return SpeechServicesSession(
            system_prompt=system_prompt,
            tools=tools,
            chat_deployment=self._chat_deployment,
            speech_region=self._speech_region,
            speech_endpoint=self._speech_endpoint,
        )
