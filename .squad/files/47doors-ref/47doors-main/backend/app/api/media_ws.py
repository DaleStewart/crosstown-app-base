"""WebSocket bridge: ACS media streaming ↔ Azure OpenAI Realtime API.

Routes:
  WS /ws/acs-media  — bidirectional audio relay between ACS Call Automation
                       media streaming and the Azure OpenAI Realtime API.

ACS cannot authenticate directly to Azure OpenAI (disableLocalAuth=true,
no ACS managed identity configured). This bridge uses the backend's own
managed identity to open an authenticated WebSocket to the Realtime API,
then relays audio frames in both directions.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import websockets
from azure.core.credentials import AccessToken
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.dependencies import get_realtime_service, get_settings
from app.services.azure.phone import PHONE_SYSTEM_PROMPT
from app.services.transcript_bus import transcript_bus

logger = logging.getLogger(__name__)

router = APIRouter()


class _TokenManager:
    """Thread-safe managed-identity token cache for the OpenAI WebSocket."""

    def __init__(self) -> None:
        self._credential = None
        self._token: Optional[AccessToken] = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        refresh_buffer = 300
        needs_refresh = (
            not self._token
            or datetime.now(timezone.utc) >= datetime.fromtimestamp(
                self._token.expires_on - refresh_buffer, tz=timezone.utc
            )
        )
        if needs_refresh:
            async with self._lock:
                if not self._credential:
                    from azure.identity.aio import ManagedIdentityCredential
                    self._credential = ManagedIdentityCredential()
                self._token = await self._credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                )
                logger.info("Media bridge: MI token acquired")
        return self._token.token


_token_mgr = _TokenManager()


@router.websocket("/acs-media")
async def acs_media_bridge(ws: WebSocket) -> None:
    """Bridge ACS media streaming to Azure OpenAI Realtime API.

    Audio flow:
      Caller → ACS → [this WS] → Azure OpenAI Realtime → [this WS] → ACS → Caller
    """
    await ws.accept()
    settings = get_settings()
    call_id = str(uuid4())
    call_start = datetime.now(timezone.utc)
    logger.info("Media bridge: ACS WebSocket connected (call_id=%s)", call_id)

    # Notify SSE subscribers that a new call has started
    await transcript_bus.publish({
        "type": "call_started",
        "call_id": call_id,
        "timestamp": call_start.isoformat(),
        "phone_number": "+19132171946",
    })
    logger.info(
        "Media bridge: published call_started (call_id=%s, subscribers=%d)",
        call_id, transcript_bus.subscriber_count,
    )

    openai_ws = None
    session_ready = asyncio.Event()
    # Accumulator for caller transcription deltas keyed by item_id.
    # Some Azure Realtime API (preview) sessions emit `.delta` events but
    # never a `.completed` event, which would leave the caller transcript
    # invisible. We buffer deltas and flush on `.completed` OR when the
    # caller stops speaking.
    caller_transcript_buf: dict[str, str] = {}
    caller_published: set[str] = set()

    async def _flush_caller_transcript(item_id: str | None) -> None:
        if not item_id:
            # Flush anything buffered if we don't know the item_id.
            for iid in list(caller_transcript_buf.keys()):
                await _flush_caller_transcript(iid)
            return
        if item_id in caller_published:
            return
        text = caller_transcript_buf.pop(item_id, "").strip()
        if not text:
            return
        caller_published.add(item_id)
        logger.info(
            "Media bridge: Caller said (call_id=%s, item=%s): %s",
            call_id, item_id, text[:120],
        )
        await transcript_bus.publish({
            "type": "user_speech",
            "text": text,
            "call_id": call_id,
        })

    try:
        token = await _token_mgr.get_token()

        openai_url = (
            f"{settings.azure_openai_endpoint.replace('https://', 'wss://')}"
            f"/openai/realtime"
            f"?api-version={settings.azure_openai_realtime_api_version}"
            f"&deployment={settings.azure_openai_realtime_deployment}"
        )
        logger.info(
            f"Media bridge: connecting to OpenAI Realtime "
            f"deployment={settings.azure_openai_realtime_deployment}"
        )

        openai_ws = await websockets.connect(
            openai_url,
            additional_headers={"Authorization": f"Bearer {token}"},
        )
        logger.info("Media bridge: OpenAI Realtime WebSocket connected")

        # ------------------------------------------------------------------
        # Coroutine: read OpenAI messages, forward audio & handle events
        # ------------------------------------------------------------------
        async def _openai_receiver() -> None:
            nonlocal openai_ws
            realtime_svc = get_realtime_service()
            tools = await realtime_svc.get_tool_definitions()
            tool_defs = [
                {
                    "type": "function",
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                }
                for t in tools
            ]

            async for raw in openai_ws:
                msg = json.loads(raw)
                t = msg.get("type", "")

                if t != "response.audio.delta":  # avoid log flood
                    logger.debug("Media bridge: event type=%s", t)

                # -- Session lifecycle ------------------------------------
                if t == "session.created":
                    logger.info("Media bridge: session.created — sending config")
                    # NOTE: This endpoint (`/openai/realtime?api-version=2025-04-01-preview`)
                    # requires FLAT session-level fields and REJECTS the nested
                    # `audio: {input, output}` block with
                    # `unknown_parameter: session.audio`. The nested schema is only
                    # valid on the `/openai/v1/realtime/calls` WebRTC endpoint.
                    await openai_ws.send(json.dumps({
                        "type": "session.update",
                        "session": {
                            "instructions": PHONE_SYSTEM_PROMPT,
                            "voice": settings.realtime_voice,
                            "input_audio_format":  "pcm16",
                            "output_audio_format": "pcm16",
                            "input_audio_transcription": {"model": "whisper-1"},
                            "turn_detection": {
                                "type": "server_vad",
                                "threshold": 0.5,
                                "prefix_padding_ms": 300,
                                "silence_duration_ms": settings.realtime_vad_threshold_ms,
                            },
                            "tools": tool_defs,
                        },
                    }))
                    logger.info("Media bridge: session.update sent")
                    session_ready.set()
                    continue

                if t == "session.updated":
                    logger.info("Media bridge: session.updated confirmed")
                    continue

                # -- Audio to caller (via ACS) ----------------------------
                if t == "response.audio.delta":
                    delta = msg.get("delta", "")
                    if delta:
                        await ws.send_text(json.dumps({
                            "kind": "AudioData",
                            "audioData": {"data": delta},
                        }))
                    continue

                # -- Barge-in: stop AI playback when user speaks ----------
                if t == "input_audio_buffer.speech_started":
                    try:
                        await ws.send_text(json.dumps({
                            "kind": "StopAudio",
                            "stopAudio": {},
                        }))
                    except Exception:
                        pass
                    continue

                # Flush any buffered caller transcript deltas when speech ends
                # or the buffer is committed — guards against missing `.completed`.
                if t in ("input_audio_buffer.speech_stopped",
                         "input_audio_buffer.committed"):
                    await _flush_caller_transcript(msg.get("item_id"))
                    continue

                # -- Transcript logging -----------------------------------
                # Support both preview and GA event names for agent speech transcript
                if t in ("response.audio_transcript.done", "response.output_audio_transcript.done"):
                    text = msg.get("transcript", "")
                    logger.info(
                        "Media bridge: AI said (call_id=%s): %s",
                        call_id, text[:120],
                    )
                    await transcript_bus.publish({
                        "type": "agent_speech",
                        "text": text,
                        "call_id": call_id,
                    })
                    logger.debug(
                        "Media bridge: published agent_speech to %d subscribers",
                        transcript_bus.subscriber_count,
                    )
                    continue

                if t == "conversation.item.input_audio_transcription.completed":
                    item_id = msg.get("item_id")
                    text = (msg.get("transcript") or "").strip()
                    if text and item_id and item_id not in caller_published:
                        caller_published.add(item_id)
                        caller_transcript_buf.pop(item_id, None)
                        logger.info(
                            "Media bridge: Caller said (call_id=%s): %s",
                            call_id, text[:120],
                        )
                        await transcript_bus.publish({
                            "type": "user_speech",
                            "text": text,
                            "call_id": call_id,
                        })
                    else:
                        # Fall back to flushing any buffered deltas for this item.
                        await _flush_caller_transcript(item_id)
                    continue

                # Accumulate caller transcript deltas — some sessions only emit
                # deltas, never a `.completed`. Flush on speech_stopped below.
                if t == "conversation.item.input_audio_transcription.delta":
                    item_id = msg.get("item_id") or ""
                    delta = msg.get("delta") or ""
                    if item_id and delta:
                        caller_transcript_buf[item_id] = (
                            caller_transcript_buf.get(item_id, "") + delta
                        )
                    continue

                # -- Tool calls -------------------------------------------
                if t == "response.function_call_arguments.done":
                    fn_call_id = msg.get("call_id", "")
                    name = msg.get("name", "")
                    logger.info(f"Media bridge: tool call '{name}'")
                    try:
                        args = json.loads(msg.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = {}
                    result = await realtime_svc.execute_tool(
                        fn_call_id, name, args, "phone-call"
                    )
                    await openai_ws.send(json.dumps({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": fn_call_id,
                            "output": result.result or result.error or "",
                        },
                    }))
                    await openai_ws.send(json.dumps({"type": "response.create"}))
                    logger.info(f"Media bridge: tool '{name}' result sent")
                    summary = (result.result or result.error or "")[:200]
                    await transcript_bus.publish({
                        "type": "tool_call",
                        "tool": name,
                        "summary": summary,
                        "call_id": call_id,
                    })
                    logger.info(
                        "Media bridge: published tool_call '%s' (call_id=%s)",
                        name, call_id,
                    )
                    continue

                # -- Errors -----------------------------------------------
                if t == "error":
                    logger.error(
                        f"Media bridge: OpenAI error: {msg.get('error', {})}"
                    )
                    continue

                # Known noise events — ignore silently
                if t in (
                    "response.created", "response.done",
                    "response.output_item.added", "response.output_item.done",
                    "response.content_part.added", "response.content_part.done",
                    "response.audio.done",
                    "response.output_audio_transcript.delta",
                    "response.audio_transcript.delta",  # keep for compat
                    "conversation.item.created",
                    "response.function_call_arguments.delta",
                ):
                    continue

                logger.debug(f"Media bridge: unhandled OpenAI event: {t}")

        # ------------------------------------------------------------------
        # Coroutine: read ACS media messages, forward audio to OpenAI
        # ------------------------------------------------------------------
        async def _acs_sender() -> None:
            try:
                while True:
                    raw = await ws.receive_text()
                    msg = json.loads(raw)
                    kind = msg.get("kind", "")

                    if kind == "AudioMetadata":
                        meta = msg.get("audioMetadata", {})
                        logger.info(
                            f"Media bridge: ACS audio — "
                            f"rate={meta.get('sampleRate')} "
                            f"enc={meta.get('encoding')} "
                            f"ch={meta.get('channels')}"
                        )
                        continue

                    if kind == "AudioData":
                        b64 = msg.get("audioData", {}).get("data", "")
                        silent = msg.get("audioData", {}).get("silent", False)
                        if b64 and not silent:
                            await session_ready.wait()
                            await openai_ws.send(json.dumps({
                                "type": "input_audio_buffer.append",
                                "audio": b64,
                            }))
                        continue

                    logger.debug(f"Media bridge: ACS msg kind={kind}")
            except WebSocketDisconnect:
                logger.info("Media bridge: ACS disconnected")
            except Exception as exc:
                logger.error(f"Media bridge: ACS read error: {exc}")

        # Run both; when one ends (hangup), cancel the other.
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(_openai_receiver()),
                asyncio.create_task(_acs_sender()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    except websockets.exceptions.InvalidStatus as exc:
        logger.error(
            f"Media bridge: OpenAI WS handshake rejected — "
            f"HTTP {exc.response.status_code}"
        )
    except Exception as exc:
        logger.error(f"Media bridge: fatal error: {exc}", exc_info=True)
    finally:
        # Publish call_ended before tearing down connections
        duration = (datetime.now(timezone.utc) - call_start).total_seconds()
        try:
            await transcript_bus.publish({
                "type": "call_ended",
                "call_id": call_id,
                "duration_seconds": round(duration),
            })
            logger.info(
                "Media bridge: published call_ended (call_id=%s, duration=%ds)",
                call_id, round(duration),
            )
        except Exception:
            pass
        if openai_ws is not None:
            try:
                await openai_ws.close()
            except Exception:
                pass
        try:
            await ws.close()
        except Exception:
            pass
        logger.info("Media bridge: session ended (call_id=%s)", call_id)
