"""Regression tests for the stop-button + auto-interrupt feature.

Background — Sean's 2026-05-17 bug:
  1. "This thing keeps repeating itself. As a matter of fact, it just keeps
     talking. The person's voice changes." — caused by Foundry not auto-
     cancelling the in-flight response when a new user audio commit arrives.
     Two responses interleave; voice/text overlap.
  2. "Is there some way that I can have a stop button…" — user has no
     escape hatch while the assistant drones on.

Fix scope (this PR):
  - Add `cancel_response` WS message handled by the orchestrator → forwards
    `response.cancel` to Foundry.
  - Auto-cancel when a new user audio commit (`stop`) or `text` arrives
    while a response is in flight.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import main as main_module
from agent.orchestrator import TurnAccumulator, _cancel_inflight, _handle_event
from agent.tools import ToolRegistry
from storage.cosmos import ConversationStore
from tests.conftest import FakeContainer, FakeProvider, FakeSession
from voice.base import AudioDelta, Final, ToolCall, TranscriptDelta


class _Captor:
    def __init__(self) -> None:
        self.frames: list[dict[str, Any]] = []

    async def __call__(self, payload: dict[str, Any]) -> None:
        self.frames.append(payload)


@pytest.mark.asyncio
async def test_assistant_frame_marks_response_in_flight() -> None:
    """First assistant frame must flip the in-flight flag so a follow-up user
    turn knows to auto-cancel."""
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    assert turn.response_in_flight is False
    await _handle_event(
        TranscriptDelta(role="assistant", text="L1 service ", final=False),
        session, tools, turn, captor,
    )
    assert turn.response_in_flight is True

    # Final clears it (response completed naturally).
    await _handle_event(Final(text="L1 service is fine.", citations=[]),
                       session, tools, turn, captor)
    assert turn.response_in_flight is False


@pytest.mark.asyncio
async def test_cancel_inflight_sends_response_cancel_and_notifies_client() -> None:
    """The explicit cancel path must invoke session.cancel and tell the client."""
    turn = TurnAccumulator()
    turn.response_in_flight = True
    captor = _Captor()
    session = FakeSession()

    await _cancel_inflight(session, turn, captor)

    assert session.cancel_calls == 1
    assert turn.cancel_pending is True
    assert turn.response_in_flight is False
    cancelled = [f for f in captor.frames if f["type"] == "response_cancelled"]
    assert len(cancelled) == 1


@pytest.mark.asyncio
async def test_cancel_inflight_noop_when_idle() -> None:
    """No response in flight → cancel must be a no-op (avoid spurious cancel
    frames to Foundry which could race with a new response.create)."""
    turn = TurnAccumulator()
    captor = _Captor()
    session = FakeSession()

    await _cancel_inflight(session, turn, captor)
    assert session.cancel_calls == 0
    assert captor.frames == []


@pytest.mark.asyncio
async def test_cancel_inflight_force_fires_even_when_idle() -> None:
    """Explicit user stop must work even if our flag never flipped (e.g. the
    cancel arrived before the first assistant frame)."""
    turn = TurnAccumulator()
    captor = _Captor()
    session = FakeSession()

    await _cancel_inflight(session, turn, captor, force=True)
    assert session.cancel_calls == 1
    assert any(f["type"] == "response_cancelled" for f in captor.frames)


@pytest.mark.asyncio
async def test_late_assistant_frames_dropped_after_cancel() -> None:
    """Foundry keeps streaming for a short window after response.cancel.
    Those late frames must NOT reach the client — that defeats the stop button."""
    turn = TurnAccumulator()
    turn.response_in_flight = True
    captor = _Captor()
    session = FakeSession()
    tools = AsyncMock()

    await _cancel_inflight(session, turn, captor)
    # Two stragglers arrive after the cancel.
    await _handle_event(
        TranscriptDelta(role="assistant", text="extra text", final=False),
        session, tools, turn, captor,
    )
    await _handle_event(AudioDelta(audio_b64="AAAA"),
                       session, tools, turn, captor)
    await _handle_event(
        Final(text="extra text complete", citations=[]),
        session, tools, turn, captor,
    )

    # No transcript/audio frame should have been emitted for the stragglers.
    out_types = [f["type"] for f in captor.frames]
    assert "transcript_delta" not in out_types
    assert "audio_delta" not in out_types
    # The trailing Final still goes through (so the frontend clears its
    # awaiting/streaming state) but with blank text.
    finals = [f for f in captor.frames if f["type"] == "final"]
    assert len(finals) == 1
    assert finals[0]["text"] == ""
    # Per-response flags reset for the next turn.
    assert turn.cancel_pending is False
    assert turn.response_in_flight is False


@pytest.mark.asyncio
async def test_user_transcript_still_flows_during_cancel_window() -> None:
    """User-role transcripts describe what the user just said; they must not
    be dropped just because the previous assistant response was cancelled."""
    turn = TurnAccumulator()
    turn.cancel_pending = True
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    await _handle_event(
        TranscriptDelta(role="user", text="new question", final=True),
        session, tools, turn, captor,
    )

    user_frames = [
        f for f in captor.frames
        if f["type"] == "transcript_delta" and f["role"] == "user"
    ]
    assert len(user_frames) == 1


@pytest.fixture
def client_with_fakes(monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, FakeSession]:
    fake_session = FakeSession()
    # Queue an assistant frame so the response_in_flight flag flips when the
    # pump drains. The test then sends a follow-up turn and asserts cancel.
    fake_session.queue(
        TranscriptDelta(role="assistant", text="streaming...", final=False)
    )
    provider = FakeProvider(fake_session)

    container = FakeContainer()
    store = ConversationStore(container)

    reg = ToolRegistry("http://x")
    reg._specs = []  # noqa: SLF001
    reg._loaded = True  # noqa: SLF001

    async def fake_dispatch(*_a: Any, **_kw: Any) -> dict[str, Any]:
        return {"result": "ok", "citations": [], "warnings": []}
    monkeypatch.setattr(reg, "dispatch", fake_dispatch)

    main_module.app.state.provider = provider
    main_module.app.state.tools = reg
    main_module.app.state.store = store
    return TestClient(main_module.app), fake_session


def test_ws_explicit_cancel_response_message(
    client_with_fakes: tuple[TestClient, FakeSession],
) -> None:
    """End-to-end through the WS: client sends `cancel_response` → orchestrator
    calls session.cancel and replies with response_cancelled frame."""
    import time

    client, fake_session = client_with_fakes
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps(
            {"type": "start", "conversationId": "c1", "mode": "push_to_talk"}
        ))
        # Drain the queued assistant frame so the in-flight flag flips.
        ws.receive_text()  # transcript_delta
        # Give the pump a moment.
        time.sleep(0.05)
        ws.send_text(json.dumps({"type": "cancel_response"}))
        cancelled = ws.receive_text()
        assert json.loads(cancelled)["type"] == "response_cancelled"
        ws.send_text(json.dumps({"type": "stop"}))

    assert fake_session.cancel_calls >= 1


def test_ws_auto_cancels_on_new_audio_commit(
    client_with_fakes: tuple[TestClient, FakeSession],
) -> None:
    """The "voice changes mid-stream" fix: new audio commit while a response is
    in flight must trigger response.cancel BEFORE the new commit_audio call.
    This is the fix that works without any UI action."""
    import time

    client, fake_session = client_with_fakes
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps(
            {"type": "start", "conversationId": "c1", "mode": "push_to_talk"}
        ))
        # Receive the streaming assistant frame → flips response_in_flight.
        ws.receive_text()
        time.sleep(0.05)
        # User commits a new audio turn while the assistant is still streaming.
        ws.send_text(json.dumps({"type": "stop"}))
        # Expect a response_cancelled frame.
        frame = ws.receive_text()
        assert json.loads(frame)["type"] == "response_cancelled"

    # Cancel was sent BEFORE the audio commit. With auto-interrupt working,
    # cancel_calls == 1 and committed == 1, with cancel coming first.
    assert fake_session.cancel_calls == 1
    assert fake_session.committed == 1


def test_ws_auto_cancels_on_new_text_turn(
    client_with_fakes: tuple[TestClient, FakeSession],
) -> None:
    """Same auto-interrupt for the text-input path: user types a follow-up
    while the previous response is still streaming."""
    import time

    client, fake_session = client_with_fakes
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps(
            {"type": "start", "conversationId": "c1", "mode": "push_to_talk"}
        ))
        ws.receive_text()  # drain streaming assistant frame
        time.sleep(0.05)
        ws.send_text(json.dumps({"type": "text", "text": "different question"}))
        frame = ws.receive_text()
        assert json.loads(frame)["type"] == "response_cancelled"

    assert fake_session.cancel_calls == 1
    assert "different question" in fake_session.sent_text


# ---------------------------------------------------------------------------
# Regression tests from adversarial code review (gpt-5.3-codex 2026-05-17)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_force_cancel_when_idle_does_not_poison_next_response() -> None:
    """If the user hits stop AFTER the previous response completed,
    force=True still sends `response.cancel` (server-safe) but MUST NOT set
    `cancel_pending` — otherwise the NEXT assistant response is silently
    blanked because no matching Final exists to clear the flag.
    """
    turn = TurnAccumulator()
    assert turn.response_in_flight is False
    captor = _Captor()
    session = FakeSession()
    tools = AsyncMock()

    await _cancel_inflight(session, turn, captor, force=True)
    assert session.cancel_calls == 1
    assert turn.cancel_pending is False, (
        "cancel_pending must not poison the next response when forced-cancel "
        "fires while idle"
    )

    await _handle_event(
        TranscriptDelta(role="assistant", text="next answer", final=True),
        session, tools, turn, captor,
    )
    assistant_frames = [
        f for f in captor.frames
        if f["type"] == "transcript_delta" and f["role"] == "assistant"
    ]
    assert len(assistant_frames) == 1
    assert assistant_frames[0]["text"] == "next answer"


@pytest.mark.asyncio
async def test_tool_calls_dropped_during_cancel_pending() -> None:
    """A ToolCall arriving during cancel_pending must NOT dispatch + submit
    a tool result. submit_tool_result triggers a fresh `response.create`,
    resurrecting the work the user stopped and racing with their new turn.
    """
    turn = TurnAccumulator()
    turn.cancel_pending = True
    captor = _Captor()
    session = FakeSession()
    tools = AsyncMock()

    await _handle_event(
        ToolCall(name="search_logs", arguments={"q": "x"}, call_id="c1"),
        session, tools, turn, captor,
    )

    tools.dispatch.assert_not_called()
    assert not any(f["type"] in ("tool_call", "tool_result") for f in captor.frames)
    assert session.tool_results == []


def test_auto_cancel_fires_before_first_assistant_frame(
    client_with_fakes: tuple[TestClient, FakeSession],
) -> None:
    """`response_in_flight` must be set when `response.create` is sent (via
    send_text/commit_audio), not just when the first assistant frame arrives.
    Otherwise a barge-in between request and first delta won't auto-cancel.
    """
    import time

    client, fake_session = client_with_fakes
    # No assistant frames queued — covers the pre-first-frame window.
    fake_session._events = []  # noqa: SLF001

    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(json.dumps(
            {"type": "start", "conversationId": "c1", "mode": "push_to_talk"}
        ))
        ws.send_text(json.dumps({"type": "text", "text": "first"}))
        time.sleep(0.05)
        ws.send_text(json.dumps({"type": "text", "text": "second"}))
        frame = ws.receive_text()
        assert json.loads(frame)["type"] == "response_cancelled"

    assert fake_session.cancel_calls == 1
    assert "first" in fake_session.sent_text
    assert "second" in fake_session.sent_text
