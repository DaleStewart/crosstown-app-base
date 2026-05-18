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
        # Tracks whether we've forwarded a finalized assistant transcript to the
        # client this turn (via response.output_audio_transcript.done). Foundry
        # GA also emits a `response.done` carrying the same transcript text; if
        # we forwarded that text again as a `final` frame the frontend reducer
        # would render it as a SECOND assistant bubble (Sean's duplicate-turn
        # bug, 2026-05-18). The Final frame is still sent so the frontend can
        # clear `awaitingResponse` and attach citations — only the redundant
        # text is suppressed.
        self.assistant_transcript_sent = False
        # True from the first assistant frame of a response until the matching
        # Final arrives. Used by the auto-interrupt path: if a new user turn
        # (audio commit via `stop`, or a `text` message) arrives while this is
        # set, the relay sends `response.cancel` to Foundry BEFORE forwarding
        # the new turn. Without that, Foundry interleaves two responses and
        # Sean hears the "voice changes mid-stream / keeps repeating" symptom
        # (2026-05-17).
        self.response_in_flight = False
        # True while a cancel has been requested but the matching `response.done`
        # / `Final` has not yet arrived. Used to suppress the (now-stale)
        # assistant transcript text on the trailing Final — without this, the
        # text accumulated up to the cancel point gets rendered as if it were
        # a normal completed turn, defeating the point of the stop button.
        self.cancel_pending = False
        # Tracks the text of the most-recently-forwarded FINALIZED assistant
        # transcript_delta on this turn. Used to dedupe tool-mediated re-emits
        # (Sean's 2026-05-17 UAT bug after PR #45):
        #
        # When the model speaks AND calls a tool in cycle 1, then re-speaks the
        # same answer in cycle 2 after the tool result, Foundry emits two
        # `response.audio_transcript.done` events with identical text. PR #43's
        # dedupe only covers the Final-frame echo of an already-streamed
        # transcript — not a second finalized transcript_delta across cycle
        # boundaries. The frontend `transcript_delta` reducer creates a new
        # bubble when the previous one is already finalized, so without this
        # the user sees the same answer twice.
        #
        # We clear this per-RESPONSE on Final (matching how
        # assistant_transcript_sent resets), so a legitimately different
        # cycle-2 answer still reaches the client.
        self.last_finalized_assistant_text = ""

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
                    # Auto-interrupt: if a response is still streaming, cancel it
                    # before queuing the new user turn so Foundry doesn't
                    # interleave two responses. See TurnAccumulator.response_in_flight.
                    if turn.response_in_flight:
                        await _cancel_inflight(session, turn, send_json)
                    user_text = str(parsed.get("text", ""))
                    turn.user_text = (turn.user_text + " " + user_text).strip()
                    # New user turn → clear the per-turn dedupe state so a
                    # legitimately-identical answer to a different question
                    # still reaches the client.
                    turn.last_finalized_assistant_text = ""
                    await session.send_text(user_text)
                    # send_text fires `response.create` under the hood. Mark the
                    # request as in-flight NOW (before any assistant frame
                    # arrives) so a follow-up user turn that races in still
                    # auto-cancels. Caught by adversarial review: prior code
                    # only flipped in_flight on the first assistant delta,
                    # leaving a window where two responses could overlap.
                    turn.response_in_flight = True
                elif kind == "stop":
                    # Flush the audio buffer and trigger a model response.
                    # Do NOT break — stay in the receive loop so events pumped
                    # back from Foundry can reach the client.  The WS close
                    # from disconnect() will produce a websocket.disconnect
                    # message that breaks the loop cleanly.
                    if session is not None:
                        # Auto-interrupt before committing the new audio: this
                        # is the path that fixes "voice changes mid-stream"
                        # without any UI action (Sean's #1 complaint).
                        if turn.response_in_flight:
                            await _cancel_inflight(session, turn, send_json)
                        commit = getattr(session, "commit_audio", None)
                        if callable(commit):
                            # New user audio turn → clear per-turn dedupe.
                            turn.last_finalized_assistant_text = ""
                            await commit()
                            # commit_audio sends `response.create`. Mark in-flight
                            # immediately so a barge-in before the first assistant
                            # frame still auto-cancels. (See `text` handler above.)
                            turn.response_in_flight = True
                elif kind == "cancel_response":
                    # Explicit "stop button" from the UI. Cancel even if our
                    # in-flight flag is unset (e.g., we missed the first frame
                    # or the user is preemptively stopping a pending turn) —
                    # `response.cancel` is a no-op server-side when idle.
                    if session is not None:
                        await _cancel_inflight(session, turn, send_json, force=True)
                else:
                    await send_json({"type": "error", "message": f"unknown type {kind}"})
            elif data is not None:
                if session is not None:
                    await session.send_audio(bytes(data))
    finally:
        if session is not None:
            await session.close()
        await store.upsert_turn(conversation_id, turn.to_dict())


async def _cancel_inflight(
    session: VoiceSession,
    turn: TurnAccumulator,
    send_json: Any,
    force: bool = False,
) -> None:
    """Send `response.cancel` to the provider and notify the client.

    Called from two paths:
      - auto-interrupt: new user turn arrives while a response streams
        (resolves Sean's overlapping-voice bug, 2026-05-17).
      - explicit stop: client sent `cancel_response` (the UI stop button).

    Idempotent: safe to call when no response is in flight (provider treats
    the cancel as a no-op). We always emit a `response_cancelled` frame to
    the client so the frontend can clear its `streaming` state even on the
    auto path.

    Important: `cancel_pending` is only set when there is actually a response
    in flight. If we set it on a force-cancel-while-idle, the NEXT assistant
    response would be silently blanked because no matching Final exists to
    clear the flag. (Caught by adversarial review, gpt-5.3-codex 2026-05-17.)
    """
    import logging as _logging
    _log = _logging.getLogger("voice.relay")
    was_in_flight = turn.response_in_flight
    if not force and not was_in_flight:
        return
    if was_in_flight:
        turn.cancel_pending = True
    turn.response_in_flight = False
    try:
        cancel = getattr(session, "cancel", None)
        if callable(cancel):
            await cancel()
        _log.info(
            "relay.cancel sent response.cancel force=%s was_in_flight=%s",
            force, was_in_flight,
        )
    except Exception as exc:  # pragma: no cover - defensive
        _log.warning("relay.cancel failed: %s", exc)
    try:
        await send_json({"type": "response_cancelled"})
    except Exception:
        pass


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
    import logging as _logging
    _log = _logging.getLogger("voice.relay")
    if isinstance(ev, TranscriptDelta):
        if ev.role == "user" and ev.final:
            turn.user_text = (turn.user_text + " " + ev.text).strip()
            # Server-driven turn boundary (continuous mode / server VAD):
            # the client never sent `text`/`stop`, so the dedupe field never
            # got cleared from the previous turn. Clear it here so a
            # legitimately-identical next answer still reaches the client.
            # (Caught by adversarial review, gpt-5.3-codex 2026-05-17.)
            turn.last_finalized_assistant_text = ""
        if ev.role == "assistant":
            # First assistant frame of a response → mark in-flight so a new
            # user turn auto-cancels (Sean's overlap fix).
            turn.response_in_flight = True
            turn.assistant_text = (turn.assistant_text + ev.text).strip()
            if ev.final:
                turn.assistant_transcript_sent = True
        # If a cancel is pending, drop late assistant frames so the UI doesn't
        # render text/audio the user explicitly stopped. User-role transcripts
        # still flow (they describe what the user just said, not the cancelled
        # response).
        if turn.cancel_pending and ev.role == "assistant":
            return
        # Tool-mediated duplicate guard (Sean's 2026-05-17 UAT bug after PR #45):
        # When the model speaks AND calls a tool in cycle 1, then re-speaks
        # the same answer in cycle 2 after the tool result, Foundry emits two
        # `response.audio_transcript.done` events with identical text. The
        # frontend's transcript_delta reducer creates a new bubble when the
        # previous one is already finalized, producing two identical bubbles.
        # Suppress the duplicate at the relay so the contract stays:
        # "one finalized assistant transcript per logical answer".
        if (
            ev.role == "assistant"
            and ev.final
            and ev.text
            and ev.text == turn.last_finalized_assistant_text
        ):
            _log.info(
                "relay.drop transcript_delta role=assistant final=True "
                "duplicate_of_prior_cycle text_len=%d",
                len(ev.text),
            )
            return
        if ev.role == "assistant" and ev.final and ev.text:
            turn.last_finalized_assistant_text = ev.text
        _log.info(
            "relay.send transcript_delta role=%s final=%s len=%d",
            ev.role, ev.final, len(ev.text or ""),
        )
        await send_json(
            {
                "type": "transcript_delta",
                "role": ev.role,
                "text": ev.text,
                "final": ev.final,
            }
        )
    elif isinstance(ev, AudioDelta):
        if turn.cancel_pending:
            # User hit stop — drop trailing audio chunks. Foundry may keep
            # streaming for a few hundred ms after `response.cancel` (server
            # still flushing). Don't forward; the frontend has already drained
            # its local playback buffer.
            return
        # Audio is part of an in-flight response.
        turn.response_in_flight = True
        _log.debug("relay.send audio_delta bytes_b64=%d", len(ev.audio_b64))
        await send_json({"type": "audio_delta", "audio_b64": ev.audio_b64})
    elif isinstance(ev, ToolCall):
        if turn.cancel_pending:
            # Drop tool calls from a cancelled response. Otherwise we would
            # dispatch the tool AND submit_tool_result (which sends a fresh
            # `response.create`), resurrecting the work the user just stopped
            # and racing with their new turn. Caught by adversarial review
            # (gpt-5.3-codex 2026-05-17). Events bound to this cancelled
            # response are silently discarded; the trailing Final still flows
            # to reset per-response flags.
            _log.info(
                "relay.drop tool_call name=%s call_id=%s cancel_pending=True",
                ev.name, ev.call_id,
            )
            return
        turn.tool_calls.append(
            {"name": ev.name, "arguments": ev.arguments, "call_id": ev.call_id}
        )
        _log.info("relay.send tool_call name=%s call_id=%s", ev.name, ev.call_id)
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
        # submit_tool_result triggers Foundry's cycle-2 `response.create` under
        # the hood. Mark the response in-flight immediately so a barge-in (new
        # audio commit or text turn) during the pre-first-frame window of
        # cycle 2 routes through `_cancel_inflight` instead of racing with
        # Foundry's auto-preempt (which silently ships an empty `output[]`).
        # Without this flag, cycle 2 was being abandoned mid-flight on voice
        # barge-in, producing the "missing assistant response" bug Wanda
        # diagnosed on 2026-05-18.
        turn.response_in_flight = True
    elif isinstance(ev, Final):
        if ev.text and not turn.cancel_pending:
            turn.assistant_text = ev.text
        if ev.citations and not turn.cancel_pending:
            turn.citations.extend(ev.citations)
        # Dedupe: if a finalized assistant transcript was already streamed (via
        # response.output_audio_transcript.done), suppress the text in the
        # `final` frame. Foundry GA emits both for every voice response. The
        # frontend's `final` branch (useVoiceSession.applyFrame) appends a new
        # bubble when text is present and the last line is already final — so
        # echoing the same text here produces a duplicate assistant turn.
        # Also: if a cancel was requested for this response, blank the text —
        # the user pressed stop and we should not splat the (now stale) full
        # text into the transcript.
        out_text = (
            ""
            if (turn.assistant_transcript_sent or turn.cancel_pending)
            else ev.text
        )
        _log.info(
            "relay.send final text_len=%d citations=%d transcript_already_sent=%s "
            "cancel_pending=%s",
            len(out_text or ""), len(ev.citations or []),
            turn.assistant_transcript_sent, turn.cancel_pending,
        )
        await send_json(
            {"type": "final", "text": out_text, "citations": ev.citations}
        )
        # Reset per-response, not per-session. Foundry emits one `response.done`
        # per assistant response; the next response (e.g. after a tool-call
        # roundtrip or a follow-up user turn) starts a fresh streaming cycle
        # and needs the suppression flag cleared. Without this reset, any
        # subsequent text-only Final would be blanked. (Caught by adversarial
        # review of PR; see also test_multiple_responses_reset_flag.)
        turn.assistant_transcript_sent = False
        turn.response_in_flight = False
        turn.cancel_pending = False


def encode_pcm(pcm: bytes) -> str:
    return base64.b64encode(pcm).decode("ascii")
