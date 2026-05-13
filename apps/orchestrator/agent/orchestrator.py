from __future__ import annotations

import base64
import json
import uuid
from typing import Any

from fastapi import WebSocket

from agent.tools import ToolRegistry
from storage.cosmos import ConversationStore
from system_prompt import SYSTEM_PROMPT
from voice.base import (
    AudioDelta,
    Final,
    ToolCall,
    TranscriptDelta,
    VoiceProvider,
    VoiceSession,
)


class TurnAccumulator:
    """Builds up a single conversation turn as deltas arrive."""

    def __init__(self) -> None:
        self.user_text = ""
        self.assistant_text = ""
        self.tool_calls: list[dict[str, Any]] = []
        self.citations: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "user": self.user_text,
            "assistant": self.assistant_text,
            "tool_calls": list(self.tool_calls),
            "citations": list(self.citations),
        }


async def run_voice_session(
    ws: WebSocket,
    provider: VoiceProvider,
    tools: ToolRegistry,
    store: ConversationStore,
) -> None:
    """Bridge a frontend WebSocket to a voice provider session.

    Frontend protocol is documented in apps/orchestrator/README.md.
    """
    await ws.accept()

    conversation_id: str = str(uuid.uuid4())
    session: VoiceSession | None = None
    turn = TurnAccumulator()

    async def send_json(payload: dict[str, Any]) -> None:
        await ws.send_text(json.dumps(payload))

    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            text = msg.get("text")
            data = msg.get("bytes")

            if text is not None:
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    await send_json({"type": "error", "message": "invalid json"})
                    continue

                kind = parsed.get("type")
                if kind == "start":
                    cid = parsed.get("conversationId")
                    if isinstance(cid, str) and cid:
                        conversation_id = cid
                    if session is None:
                        session = await provider.open_session(SYSTEM_PROMPT, tools.specs)
                        # Spawn the model->client pump.
                        await _spawn_event_pump(session, ws, tools, turn, send_json)
                elif kind == "text":
                    if session is None:
                        session = await provider.open_session(SYSTEM_PROMPT, tools.specs)
                        await _spawn_event_pump(session, ws, tools, turn, send_json)
                    user_text = str(parsed.get("text", ""))
                    turn.user_text = (turn.user_text + " " + user_text).strip()
                    await session.send_text(user_text)
                elif kind == "stop":
                    break
                else:
                    await send_json({"type": "error", "message": f"unknown type {kind}"})
            elif data is not None:
                if session is not None:
                    await session.send_audio(bytes(data))
    finally:
        if session is not None:
            await session.close()
        await store.upsert_turn(conversation_id, turn.to_dict())


async def _spawn_event_pump(
    session: VoiceSession,
    ws: WebSocket,
    tools: ToolRegistry,
    turn: TurnAccumulator,
    send_json: Any,
) -> None:
    import asyncio

    async def pump() -> None:
        try:
            async for ev in session.events():
                await _handle_event(ev, session, tools, turn, send_json)
        except Exception as exc:  # pragma: no cover - defensive
            try:
                await send_json({"type": "error", "message": str(exc)})
            except Exception:
                pass

    asyncio.create_task(pump())
    # Avoid unused-import warning under strict mypy
    del ws


async def _handle_event(
    ev: Any,
    session: VoiceSession,
    tools: ToolRegistry,
    turn: TurnAccumulator,
    send_json: Any,
) -> None:
    if isinstance(ev, TranscriptDelta):
        if ev.role == "user" and ev.final:
            turn.user_text = (turn.user_text + " " + ev.text).strip()
        if ev.role == "assistant":
            turn.assistant_text = (turn.assistant_text + ev.text).strip()
        await send_json(
            {
                "type": "transcript_delta",
                "role": ev.role,
                "text": ev.text,
                "final": ev.final,
            }
        )
    elif isinstance(ev, AudioDelta):
        await send_json({"type": "audio_delta", "audio_b64": ev.audio_b64})
    elif isinstance(ev, ToolCall):
        turn.tool_calls.append(
            {"name": ev.name, "arguments": ev.arguments, "call_id": ev.call_id}
        )
        await send_json(
            {
                "type": "tool_call",
                "name": ev.name,
                "args": ev.arguments,
                "call_id": ev.call_id,
            }
        )
        try:
            result = await tools.dispatch(ev.name, ev.arguments)
        except Exception as exc:
            result = {"error": str(exc), "citations": [], "warnings": [str(exc)]}
        citations = result.get("citations", []) if isinstance(result, dict) else []
        warnings = result.get("warnings", []) if isinstance(result, dict) else []
        if isinstance(citations, list):
            turn.citations.extend(c for c in citations if isinstance(c, dict))
        await send_json(
            {
                "type": "tool_result",
                "name": ev.name,
                "citations": citations,
                "warnings": warnings,
            }
        )
        await session.submit_tool_result(ev.call_id, result)
    elif isinstance(ev, Final):
        if ev.text:
            turn.assistant_text = ev.text
        if ev.citations:
            turn.citations.extend(ev.citations)
        await send_json(
            {"type": "final", "text": ev.text, "citations": ev.citations}
        )


def encode_pcm(pcm: bytes) -> str:
    return base64.b64encode(pcm).decode("ascii")
