"""Regression tests for the voice-relay dedupe + user-transcript fixes.

Background — Sean's 2026-05-18 bug (5 prior PRs failed to land it):
  1. Every assistant turn appeared twice in the UI.
  2. The user's spoken question never appeared.

Root causes (proven from container logs at 02:25–02:30Z):
  1. Foundry GA emits both `response.output_audio_transcript.done` (carries
     the full transcript) AND `response.done` (Final with the same text).
     The relay forwarded both with text, producing two bubbles.
  2. The phase-2 `session.update` we sent to enable input transcription used
     BOTH the flat `input_audio_transcription` field AND the nested
     `audio.input.transcription` field. The GA endpoint rejects the flat
     field; rejection is atomic so the nested form is discarded too —
     silently disabling user-audio transcription.

47doors reference: `backend/app/services/azure/realtime.py:119-138` sends
only the nested form and works in production.
"""

from __future__ import annotations

from typing import Any, Self  # noqa: F401  (kept for type hints elsewhere)
from unittest.mock import AsyncMock

import pytest

from agent.orchestrator import TurnAccumulator, _handle_event
from voice.base import Final, TranscriptDelta


class _Captor:
    def __init__(self) -> None:
        self.frames: list[dict[str, Any]] = []

    async def __call__(self, payload: dict[str, Any]) -> None:
        self.frames.append(payload)


@pytest.mark.asyncio
async def test_final_after_assistant_transcript_done_is_text_empty() -> None:
    """When assistant transcript already streamed final=True, suppress Final.text.

    Reproduces the duplicate assistant turn: prior to the fix the orchestrator
    forwarded a `final` frame with the same text as the just-finalized
    transcript_delta. The frontend reducer appended that as a second bubble.
    """
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    # Simulate Foundry GA event stream:
    #   response.output_audio_transcript.delta (×N)
    #   response.output_audio_transcript.done  → TranscriptDelta(final=True, text=FULL)
    #   response.done                          → Final(text=FULL)
    await _handle_event(
        TranscriptDelta(role="assistant", text="L1 service is fully ", final=False),
        session, tools, turn, captor,
    )
    await _handle_event(
        TranscriptDelta(role="assistant", text="suspended right now.", final=False),
        session, tools, turn, captor,
    )
    await _handle_event(
        TranscriptDelta(
            role="assistant", text="L1 service is fully suspended right now.", final=True
        ),
        session, tools, turn, captor,
    )
    await _handle_event(
        Final(text="L1 service is fully suspended right now.", citations=[]),
        session, tools, turn, captor,
    )

    finals = [f for f in captor.frames if f["type"] == "final"]
    assert len(finals) == 1, captor.frames
    assert finals[0]["text"] == "", (
        "Final.text must be suppressed once transcript_delta(final=True) was sent; "
        "otherwise frontend renders a duplicate assistant bubble. "
        f"Got: {finals[0]!r}"
    )
    # Persistence is preserved on the accumulator for Cosmos upsert.
    assert turn.assistant_text == "L1 service is fully suspended right now."


@pytest.mark.asyncio
async def test_final_without_prior_transcript_keeps_text() -> None:
    """Text-only / non-voice providers still need Final.text to render."""
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    await _handle_event(
        Final(text="Doors held cluster on L2.", citations=[]),
        session, tools, turn, captor,
    )

    finals = [f for f in captor.frames if f["type"] == "final"]
    assert len(finals) == 1
    assert finals[0]["text"] == "Doors held cluster on L2."


@pytest.mark.asyncio
async def test_multiple_responses_reset_dedupe_flag() -> None:
    """Caught by adversarial review (gpt-5.3-codex): the dedupe flag must reset
    per response. Otherwise the second Final in a multi-turn conversation is
    incorrectly blanked even when it had no streaming transcript.
    """
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    # Response 1: streamed voice → transcript_delta(final=True) + Final
    await _handle_event(
        TranscriptDelta(role="assistant", text="L1 suspended.", final=True),
        session, tools, turn, captor,
    )
    await _handle_event(
        Final(text="L1 suspended.", citations=[]),
        session, tools, turn, captor,
    )
    # Response 2: text-only / no streaming transcript_delta this turn.
    await _handle_event(
        Final(text="Follow-up text answer.", citations=[]),
        session, tools, turn, captor,
    )

    finals = [f for f in captor.frames if f["type"] == "final"]
    assert len(finals) == 2
    assert finals[0]["text"] == ""  # Response 1 deduped (text in transcript_delta).
    assert finals[1]["text"] == "Follow-up text answer.", (
        "Response 2 should NOT be blanked — flag must reset between responses."
    )


@pytest.mark.asyncio
async def test_user_transcript_completed_forwards_one_frame() -> None:
    """A single user transcript completion must produce exactly one frame."""
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    await _handle_event(
        TranscriptDelta(
            role="user", text="any trains down on L1?", final=True
        ),
        session, tools, turn, captor,
    )

    user_frames = [
        f
        for f in captor.frames
        if f["type"] == "transcript_delta" and f["role"] == "user"
    ]
    assert len(user_frames) == 1
    assert user_frames[0]["text"] == "any trains down on L1?"
    assert user_frames[0]["final"] is True
    assert turn.user_text == "any trains down on L1?"


def test_phase2_session_update_uses_only_nested_transcription_form() -> None:
    """The flat `session.input_audio_transcription` field is rejected by GA.

    Hard evidence (orchestrator container logs, 2026-05-18T02:30:27Z):
        Phase 2 transcription session.update rejected:
        Unknown parameter: 'session.input_audio_transcription'.

    Because session.update is atomic, sending both forms in one payload caused
    the nested form (which IS accepted) to be discarded along with the rejected
    flat form — silently disabling transcription. This is the reason no user
    transcript reached the browser across 5 prior PR attempts.

    47doors uses the same GA-only nested shape successfully:
    `.squad/files/47doors-ref/47doors-main/backend/app/services/azure/realtime.py:124-138`.

    We assert on the PAYLOAD STRUCTURE rather than module source so that
    comments / docstrings explaining the historical bug do not trip the test.
    """
    import asyncio
    import json as _json

    import voice.foundry_realtime as fr

    sent: list[str] = []

    class _FakeWS:
        async def send(self, payload: str) -> None:
            sent.append(payload)

        async def close(self) -> None:
            pass

    async def _drive() -> None:
        ws = _FakeWS()
        # Mimic the phase-2 path: directly invoke the same json.dumps shape
        # foundry_realtime.py uses (we can't easily call open_session without
        # network). We do this by importing the function body — simulate the
        # documented contract: send a session.update whose `session` dict pins
        # transcription via nested `audio.input.transcription` only.
        #
        # To keep the test honest we monkey-patch websockets.connect to return
        # our fake WS and run the real `open_session` with a stubbed handshake.
        # Simpler approach: directly assert by extracting the json.dumps call
        # we'd build by mimicking the code. But that just re-tests our own
        # mock. The most defensible approach is structural: exec a guarded
        # subset of the function. Since reaching open_session requires real
        # azure-identity, we instead capture by patching DefaultAzureCredential
        # and websockets.connect.
        from unittest.mock import AsyncMock, MagicMock, patch

        # Build a minimal fake websocket that records all sent payloads and
        # immediately acks every session.update so open_session's wait_for
        # calls return promptly.
        ack_lock = asyncio.Lock()
        sent_payloads: list[str] = []

        class _AsyncIterWS:
            def __init__(self) -> None:
                self._queue: asyncio.Queue[str] = asyncio.Queue()
                self._closed = False

            async def send(self, payload: str) -> None:
                sent_payloads.append(payload)
                # Immediately ack any session.update.
                try:
                    parsed = _json.loads(payload)
                except _json.JSONDecodeError:
                    return
                if parsed.get("type") == "session.update":
                    await self._queue.put(_json.dumps({"type": "session.updated"}))

            def __aiter__(self) -> Self:
                return self

            async def __anext__(self) -> str:
                if self._closed:
                    raise StopAsyncIteration
                return await self._queue.get()

            async def close(self) -> None:
                self._closed = True

        fake_ws = _AsyncIterWS()

        async def _fake_connect(*_args: object, **_kwargs: object) -> _AsyncIterWS:
            return fake_ws

        class _FakeToken:
            token = "fake-token"

        class _FakeCred:
            async def __aenter__(self) -> _FakeCred:
                return self

            async def __aexit__(self, *_args: object) -> None:
                pass

            async def get_token(self, _scope: str) -> _FakeToken:
                return _FakeToken()

        with patch.object(fr, "DefaultAzureCredential", _FakeCred), patch.dict(
            "sys.modules",
            {"websockets": MagicMock(connect=_fake_connect)},
        ):
            provider = fr.FoundryRealtimeProvider(
                endpoint="https://example.openai.azure.com",
                deployment="gpt-realtime",
                transcription_deployment="gpt-4o-mini-transcribe",
            )
            session = await provider.open_session(system_prompt="x", tools=[])
            await session.close()
        # Silence unused symbols.
        del ws, AsyncMock, ack_lock

        # Find the phase-2 transcription session.update (the second one).
        updates = [
            _json.loads(p)
            for p in sent_payloads
            if _json.loads(p).get("type") == "session.update"
        ]
        assert len(updates) >= 2, (
            f"Expected at least 2 session.update payloads (handshake + phase-2); "
            f"got {len(updates)}: {updates!r}"
        )
        phase2 = updates[1]["session"]

        # Flat field MUST NOT be present — it triggers the GA rejection that
        # silently disabled transcription across 5 prior PRs.
        assert "input_audio_transcription" not in phase2, (
            f"Flat `input_audio_transcription` field present in phase-2 "
            f"session.update — GA endpoint rejects this atomically. "
            f"Use only `audio.input.transcription`. Payload: {phase2!r}"
        )
        # Nested form MUST be present with the language pin.
        transcription = (
            phase2.get("audio", {}).get("input", {}).get("transcription", {})
        )
        assert transcription.get("model") == "gpt-4o-mini-transcribe", phase2
        assert transcription.get("language") == "en", phase2
        # session.type=realtime is required on every GA session.update.
        assert phase2.get("type") == "realtime", phase2

    asyncio.run(_drive())
