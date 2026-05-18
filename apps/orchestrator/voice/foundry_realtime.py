from __future__ import annotations

import asyncio
import base64
import json
import logging
import sys
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

# Dedicated logger so operators can grep container logs for `voice.foundry`.
# Sean has been chasing the missing user transcript across 3 PRs — these logs
# make the relay path observable end-to-end without another spawn cycle.
logger = logging.getLogger("voice.foundry")
if not logger.handlers:
    # Match uvicorn's default formatter so lines interleave cleanly.
    _h = logging.StreamHandler(sys.stderr)
    _h.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class FoundryRealtimeSession:
    """Thin wrapper around an Azure OpenAI Realtime WebSocket.

    The class is intentionally split from the actual websocket client so unit
    tests can drive `_inbound` directly without touching the network.
    """

    def __init__(self, ws: Any | None = None) -> None:
        self._ws = ws
        self._inbound: asyncio.Queue[VoiceEvent | None] = asyncio.Queue()
        self._closed = False

    async def commit_audio(self) -> None:
        """Flush the audio buffer and ask the model to respond.

        Called when the client signals end-of-utterance (push-to-talk release).
        With server_vad this is belt-and-suspenders; without it, it is required.
        Without an explicit commit + response.create, the model never processes speech.
        """
        if self._ws is None or self._closed:
            return
        await self._ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        await self._ws.send(json.dumps({"type": "response.create"}))

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

    async def cancel(self) -> None:
        """Tell Foundry to abort the in-flight response.

        Resolves Sean's "keeps talking / voice changes mid-stream" symptom
        (2026-05-17). Without this, Foundry GA streams the entire response
        even after the user starts a new turn, and a second `response.create`
        interleaves with the still-running first response — producing the
        overlapping voices / repeated text he saw.

        We send `response.cancel` unconditionally and let the server ignore it
        if no response is active. The GA endpoint treats an extra cancel as a
        no-op rather than an error (verified: OpenAI Realtime API reference,
        `response.cancel` event — no required fields, server is tolerant of
        canceling when idle). Keeping this idempotent lets the relay fire
        defensively on every new user commit without bookkeeping races.
        """
        if self._ws is None or self._closed:
            return
        await self._ws.send(json.dumps({"type": "response.cancel"}))

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
            logger.warning("foundry.recv non-json frame (%d bytes)", len(raw))
            return
        kind = data.get("type", "<missing>")
        ev = self._translate(data)
        if ev is None:
            # We received a Foundry frame and chose not to forward — log so we
            # can see e.g. an input_audio_transcription.failed or an unknown
            # event name we should be handling.
            logger.info("foundry.recv DROP type=%s", kind)
            return
        logger.info(
            "foundry.recv EMIT type=%s -> %s", kind, type(ev).__name__
        )
        await self._inbound.put(ev)

    def _translate(self, data: dict[str, Any]) -> VoiceEvent | None:
        kind = data.get("type", "")
        # GA Realtime API (the /openai/v1/realtime endpoint we connect to) renamed
        # response events with an `output_` prefix. The preview names are kept as
        # fallbacks for older deployments and existing test fixtures. Without the
        # GA names, the only client-bound frame was `{type: "final"}` from
        # response.done — exactly Sean's "no transcript_delta, no audio" symptom.
        # Ref: Foundry Realtime Preview→GA migration guide.
        if kind in ("response.output_audio.delta", "response.audio.delta"):
            audio = data.get("delta", "")
            if isinstance(audio, str) and audio:
                return AudioDelta(audio_b64=audio)
        if kind in (
            "response.output_audio_transcript.delta",
            "response.audio_transcript.delta",
        ):
            text = data.get("delta", "")
            if isinstance(text, str):
                return TranscriptDelta(role="assistant", text=text, final=False)
        if kind in (
            "response.output_audio_transcript.done",
            "response.audio_transcript.done",
        ):
            text = data.get("transcript", "")
            if isinstance(text, str):
                return TranscriptDelta(role="assistant", text=text, final=True)
        # Input-audio transcription events: the migration guide does not call out
        # a rename, but some GA builds emit `conversation.item.input_transcript.*`
        # while others retain `input_audio_transcription.*`. Accept both shapes.
        if kind in (
            "conversation.item.input_audio_transcription.delta",
            "conversation.item.input_transcript.delta",
        ):
            text = data.get("delta", "")
            if isinstance(text, str) and text:
                return TranscriptDelta(role="user", text=text, final=False)
        if kind in (
            "conversation.item.input_audio_transcription.completed",
            "conversation.item.input_transcript.completed",
        ):
            text = data.get("transcript", "")
            if isinstance(text, str):
                return TranscriptDelta(role="user", text=text, final=True)
        if kind in (
            "conversation.item.input_audio_transcription.failed",
            "conversation.item.input_transcript.failed",
        ):
            return None
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
            has_message = False
            for item in outputs:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "function_call":
                    continue
                has_message = True
                for c in item.get("content", []):
                    if isinstance(c, dict):
                        if "transcript" in c:
                            text = str(c["transcript"])
                        elif "text" in c:
                            text = str(c["text"])
            if has_message or not outputs:
                return Final(text=text, citations=[])
            return None
        return None


class FoundryRealtimeProvider:
    name = "foundry_realtime"

    def __init__(self, endpoint: str, deployment: str, transcription_deployment: str = "") -> None:
        self._endpoint = endpoint
        self._deployment = deployment
        self._transcription_deployment = transcription_deployment

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
        base = self._endpoint.rstrip("/")
        if base.startswith("https://"):
            base = "wss://" + base[len("https://") :]
        elif base.startswith("http://"):
            base = "ws://" + base[len("http://") :]
        url = base + f"/openai/v1/realtime?model={self._deployment}"
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
                        "type": "realtime",
                        "instructions": system_prompt,
                        "tools": tool_specs,
                        "tool_choice": "auto",
                        "output_modalities": ["audio"],
                    },
                }
            )
        )

        session_ready: asyncio.Event = asyncio.Event()
        session_error: list[str] = []
        # Phase 2 diagnostics: capture any error event that arrives in the brief
        # window after we fire the transcription session.update. Fire-and-forget
        # was hiding regressions (Sean's DevTools showed no user_transcript ever),
        # so we now surface rejections to stderr instead of silently absorbing them.
        phase2_active = False
        phase2_error: list[str] = []
        phase2_ack: asyncio.Event = asyncio.Event()

        async def pump() -> None:
            try:
                async for raw in ws:
                    if isinstance(raw, bytes):
                        continue
                    try:
                        evt = json.loads(raw)
                        etype = evt.get("type", "")
                        if etype == "session.updated":
                            if not session_ready.is_set():
                                session_ready.set()
                            elif phase2_active:
                                phase2_ack.set()
                        elif etype == "error":
                            msg = evt.get("error", {}).get("message", str(evt))
                            if phase2_active:
                                phase2_error.append(msg)
                                phase2_ack.set()
                                print(
                                    f"[foundry_realtime] Phase 2 transcription "
                                    f"session.update rejected: {msg}",
                                    file=sys.stderr,
                                    flush=True,
                                )
                            else:
                                session_error.append(msg)
                                session_ready.set()  # unblock wait_for so we can raise
                    except json.JSONDecodeError:
                        pass
                    await session._ingest(raw)
            finally:
                await session._inbound.put(None)

        asyncio.create_task(pump())
        await asyncio.wait_for(session_ready.wait(), timeout=10.0)
        if session_error:
            raise RuntimeError(f"Foundry session.update rejected: {session_error[0]}")

        # Phase 2 (conditional): enable input audio transcription so Foundry emits
        # `conversation.item.input_audio_transcription.{delta,completed}` events,
        # which `_translate` converts to user-role TranscriptDelta frames and the
        # browser renders as user turns. Without this, the only client-bound frame
        # is `{type: "final"}` and the user's words are invisible (Sean's bug).
        #
        # Format: the canonical OpenAI Realtime WS schema uses the FLAT field
        # `session.input_audio_transcription.model`. gpt-4o-mini-transcribe is the
        # GA transcription model and is documented under this flat field. We also
        # include the nested `audio.input.transcription.model` for forward-compat
        # with future GA schema revisions — extra keys are ignored by the server.
        #
        # DANGER: an invalid deployment name will close the WebSocket. Only send
        # when AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT is explicitly configured
        # (default is ""). PR #38 wired the deployment in foundry.bicep.
        if self._transcription_deployment:
            phase2_active = True
            logger.info(
                "foundry.send session.update phase2 transcription deployment=%s "
                "language=en (flat+nested)",
                self._transcription_deployment,
            )
            # GA-ONLY nested form. The flat `session.input_audio_transcription`
            # field is rejected by the GA `/openai/v1/realtime` endpoint with
            # `Unknown parameter: 'session.input_audio_transcription'` (observed
            # 2026-05-18 in swedencentral orchestrator logs). Because the entire
            # session.update is atomic, sending both forms in one payload caused
            # the nested form to be discarded along with the rejected flat form
            # — silently disabling transcription, which is why Sean has not seen
            # a user transcript across 5 prior PR attempts.
            #
            # 47doors uses the same GA-only nested form successfully in
            # production: see backend/app/services/azure/realtime.py:124-138.
            await ws.send(
                json.dumps(
                    {
                        "type": "session.update",
                        "session": {
                            # GA requires session.type on every session.update.
                            "type": "realtime",
                            # Nested form (GA v1 schema). `language` is ISO 639-1
                            # and pins gpt-4o-mini-transcribe; without it short
                            # utterances were mislabelled as Korean.
                            "audio": {
                                "input": {
                                    "transcription": {
                                        "model": self._transcription_deployment,
                                        "language": "en",
                                    },
                                },
                            },
                        },
                    }
                )
            )
            # Brief wait so any rejection is logged before we hand back the session.
            # We do NOT raise — keep the voice loop running even if transcription
            # can't be enabled (assistant still works). Surface the failure in logs
            # so Sean / Brady can diagnose without staring at DevTools.
            try:
                await asyncio.wait_for(phase2_ack.wait(), timeout=2.0)
                if phase2_error:
                    logger.warning(
                        "foundry phase2 ack=error msg=%s", phase2_error[0]
                    )
                else:
                    logger.info("foundry phase2 ack=session.updated (transcription enabled)")
            except TimeoutError:
                logger.warning(
                    "foundry phase2 ack=timeout (no session.updated or error in 2s) — "
                    "transcription may be silently disabled"
                )
            phase2_active = False
            if phase2_error:
                print(
                    "[foundry_realtime] transcription disabled for this session "
                    f"(deployment={self._transcription_deployment!r}); "
                    "user-turn transcripts will not be emitted.",
                    file=sys.stderr,
                    flush=True,
                )

        return session
