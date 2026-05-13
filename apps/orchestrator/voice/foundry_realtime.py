from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import AsyncIterator
from typing import Any

from azure.identity.aio import DefaultAzureCredential

from voice.base import (
    AudioDelta,
    Final,
    ToolCall,
    ToolSpec,
    TranscriptDelta,
    VoiceEvent,
)

REALTIME_SCOPE = "https://cognitiveservices.azure.com/.default"


class FoundryRealtimeSession:
    """Thin wrapper around an Azure OpenAI Realtime WebSocket.

    The class is intentionally split from the actual websocket client so unit
    tests can drive `_inbound` directly without touching the network.
    """

    def __init__(self, ws: Any | None = None) -> None:
        self._ws = ws
        self._inbound: asyncio.Queue[VoiceEvent | None] = asyncio.Queue()
        self._closed = False

    async def send_audio(self, pcm: bytes) -> None:
        if self._ws is None or self._closed:
            return
        msg = {
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(pcm).decode("ascii"),
        }
        await self._ws.send(json.dumps(msg))

    async def send_text(self, text: str) -> None:
        if self._ws is None or self._closed:
            return
        msg = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        }
        await self._ws.send(json.dumps(msg))
        await self._ws.send(json.dumps({"type": "response.create"}))

    async def events(self) -> AsyncIterator[VoiceEvent]:
        while True:
            ev = await self._inbound.get()
            if ev is None:
                return
            yield ev

    async def submit_tool_result(self, call_id: str, result: dict[str, Any]) -> None:
        if self._ws is None or self._closed:
            return
        msg = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result),
            },
        }
        await self._ws.send(json.dumps(msg))
        await self._ws.send(json.dumps({"type": "response.create"}))

    async def close(self) -> None:
        self._closed = True
        await self._inbound.put(None)
        if self._ws is not None:
            await self._ws.close()

    async def _ingest(self, raw: str) -> None:
        """Translate a raw Foundry event JSON string into a VoiceEvent."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return
        ev = self._translate(data)
        if ev is not None:
            await self._inbound.put(ev)

    def _translate(self, data: dict[str, Any]) -> VoiceEvent | None:
        kind = data.get("type", "")
        if kind == "response.audio.delta":
            audio = data.get("delta", "")
            if isinstance(audio, str) and audio:
                return AudioDelta(audio_b64=audio)
        if kind == "response.audio_transcript.delta":
            text = data.get("delta", "")
            if isinstance(text, str):
                return TranscriptDelta(role="assistant", text=text, final=False)
        if kind == "response.audio_transcript.done":
            text = data.get("transcript", "")
            if isinstance(text, str):
                return TranscriptDelta(role="assistant", text=text, final=True)
        if kind == "conversation.item.input_audio_transcription.completed":
            text = data.get("transcript", "")
            if isinstance(text, str):
                return TranscriptDelta(role="user", text=text, final=True)
        if kind == "response.function_call_arguments.done":
            name = str(data.get("name", ""))
            call_id = str(data.get("call_id", ""))
            args_raw = data.get("arguments", "{}")
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else {}
            except json.JSONDecodeError:
                args = {}
            return ToolCall(name=name, arguments=args, call_id=call_id)
        if kind == "response.done":
            text = ""
            response = data.get("response", {})
            outputs = response.get("output", []) if isinstance(response, dict) else []
            for item in outputs:
                if not isinstance(item, dict):
                    continue
                for c in item.get("content", []):
                    if isinstance(c, dict) and "transcript" in c:
                        text = str(c["transcript"])
            return Final(text=text, citations=[])
        return None


class FoundryRealtimeProvider:
    name = "foundry_realtime"

    def __init__(self, endpoint: str, deployment: str) -> None:
        self._endpoint = endpoint
        self._deployment = deployment

    async def _get_token(self) -> str:
        async with DefaultAzureCredential() as cred:
            token = await cred.get_token(REALTIME_SCOPE)
            return token.token

    async def open_session(
        self, system_prompt: str, tools: list[ToolSpec]
    ) -> FoundryRealtimeSession:
        # Lazy import so tests don't require network.
        import websockets

        token = await self._get_token()
        url = (
            self._endpoint.rstrip("/")
            + f"/openai/realtime?api-version=2024-10-01-preview&deployment={self._deployment}"
        )
        headers = [("Authorization", f"Bearer {token}")]
        ws = await websockets.connect(url, additional_headers=headers)
        session = FoundryRealtimeSession(ws)

        tool_specs = [
            {
                "type": "function",
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters or {"type": "object", "properties": {}},
            }
            for t in tools
        ]
        await ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "instructions": system_prompt,
                        "tools": tool_specs,
                        "modalities": ["text", "audio"],
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                    },
                }
            )
        )

        async def pump() -> None:
            try:
                async for raw in ws:
                    if isinstance(raw, bytes):
                        continue
                    await session._ingest(raw)
            finally:
                await session._inbound.put(None)

        asyncio.create_task(pump())
        return session
