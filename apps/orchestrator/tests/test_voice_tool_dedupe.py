"""Regression tests for the tool-mediated duplicate-assistant-turn bug
and the streaming-detection gap.

Bug 1 — Sean 2026-05-17 UAT (after PR #45 deploy):
  User asked "About L2 service to Brooklyn". Model called
  ``get_disruption_status({line:"L2"})`` (cycle 1), then spoke the answer
  in cycle 2. Sean's UI shows the SAME assistant text appearing TWICE
  for that single user question.

  Root cause: when Foundry returns ``response.done`` for cycle 1 with
  outputs=[message, function_call] (model spoke during the tool call),
  OR when the model re-speaks the same answer in cycle 2 after the
  tool result, the orchestrator forwards a SECOND
  ``response.audio_transcript.done`` (transcript_delta final=True) with
  identical text. The frontend's ``final`` reducer has content-equality
  dedupe from PR #43, but the ``transcript_delta`` reducer does NOT —
  so the second finalized assistant transcript creates a new bubble.

  Fix: orchestrator suppresses any transcript_delta(role=assistant,
  final=True) whose text matches the most-recently-forwarded finalized
  assistant text on the same turn. The frontend gets defense-in-depth
  content-equality dedupe in its transcript_delta handler.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from agent.orchestrator import TurnAccumulator, _handle_event
from voice.base import Final, ToolCall, TranscriptDelta


class _Captor:
    def __init__(self) -> None:
        self.frames: list[dict[str, Any]] = []

    async def __call__(self, payload: dict[str, Any]) -> None:
        self.frames.append(payload)


@pytest.mark.asyncio
async def test_tool_mediated_duplicate_transcript_is_deduped() -> None:
    """Reproduces Sean's 2026-05-17 UAT bug.

    Sequence (verbatim from a tool-mediated turn):
      1. transcript_delta deltas → unfinalized bubble.
      2. transcript_delta(final=True, FULL) — cycle 1's audio_transcript.done.
      3. ToolCall — model also called the tool in cycle 1.
      4. Final(FULL) for cycle 1 — orchestrator suppresses text via the
         existing PR #43 dedupe.
      5. transcript_delta(final=True, FULL) — cycle 2 (after tool result)
         re-emits the exact same answer. WITHOUT THE FIX this creates a
         duplicate finalized bubble on the frontend.
      6. Final(FULL) for cycle 2 — suppressed.

    Assertion: exactly ONE finalized assistant transcript_delta is
    forwarded to the client with non-empty text.
    """
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()
    tools.dispatch = AsyncMock(return_value={"citations": [], "warnings": []})

    full = "L2 service is operating normally right now."

    # Cycle 1: model speaks the answer AND calls the tool.
    await _handle_event(
        TranscriptDelta(role="assistant", text="L2 service ", final=False),
        session, tools, turn, captor,
    )
    await _handle_event(
        TranscriptDelta(role="assistant", text=full, final=True),
        session, tools, turn, captor,
    )
    await _handle_event(
        ToolCall(name="get_disruption_status", arguments={"line": "L2"}, call_id="c1"),
        session, tools, turn, captor,
    )
    await _handle_event(Final(text=full, citations=[]), session, tools, turn, captor)

    # Cycle 2: model re-speaks the same answer after the tool result.
    await _handle_event(
        TranscriptDelta(role="assistant", text=full, final=True),
        session, tools, turn, captor,
    )
    await _handle_event(Final(text=full, citations=[]), session, tools, turn, captor)

    # Exactly one finalized assistant transcript with text reaches the client.
    final_assistant_frames = [
        f for f in captor.frames
        if f["type"] == "transcript_delta"
        and f["role"] == "assistant"
        and f["final"] is True
        and f["text"]
    ]
    assert len(final_assistant_frames) == 1, (
        f"Expected 1 finalized assistant transcript_delta with text; "
        f"got {len(final_assistant_frames)}. This is Sean's duplicate bug. "
        f"Frames: {captor.frames!r}"
    )
    assert final_assistant_frames[0]["text"] == full


@pytest.mark.asyncio
async def test_dedupe_clears_on_server_driven_user_turn_boundary() -> None:
    """Regression: caught by adversarial review (gpt-5.3-codex 2026-05-17).

    In continuous mode / server VAD, turn boundaries arrive as a finalized
    user-role transcript_delta WITHOUT any client-side `text`/`stop`. The
    dedupe field MUST be cleared on that signal too, or a legitimately
    identical next answer is silently dropped.
    """
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    same = "L1 service is operating normally."

    # Turn 1: assistant says X, Final.
    await _handle_event(
        TranscriptDelta(role="assistant", text=same, final=True),
        session, tools, turn, captor,
    )
    await _handle_event(Final(text=same, citations=[]), session, tools, turn, captor)

    # Server-VAD boundary: a finalized user transcript arrives (NO text/stop).
    await _handle_event(
        TranscriptDelta(role="user", text="and L2?", final=True),
        session, tools, turn, captor,
    )

    # Turn 2: assistant happens to give an identical-looking answer.
    # This MUST reach the client (it's a real new answer).
    await _handle_event(
        TranscriptDelta(role="assistant", text=same, final=True),
        session, tools, turn, captor,
    )

    finals = [
        f for f in captor.frames
        if f["type"] == "transcript_delta"
        and f["role"] == "assistant"
        and f["final"] is True
        and f["text"]
    ]
    assert len(finals) == 2, (
        "Both turns must surface their assistant answer even when the texts "
        f"are identical; got {len(finals)}. Frames: {captor.frames!r}"
    )


@pytest.mark.asyncio
async def test_different_text_after_tool_call_is_not_deduped() -> None:
    """Counter-case: legitimately different cycle 2 text must NOT be dropped.

    If the model says "Let me check L2..." then after the tool result says
    something genuinely new like "L2 has a planned weekend closure", the
    second transcript must reach the client.
    """
    turn = TurnAccumulator()
    captor = _Captor()
    session = AsyncMock()
    tools = AsyncMock()

    await _handle_event(
        TranscriptDelta(role="assistant", text="Let me check L2 status.", final=True),
        session, tools, turn, captor,
    )
    await _handle_event(Final(text="Let me check L2 status.", citations=[]),
                       session, tools, turn, captor)

    await _handle_event(
        TranscriptDelta(
            role="assistant",
            text="L2 has a planned weekend closure.",
            final=True,
        ),
        session, tools, turn, captor,
    )
    await _handle_event(Final(text="L2 has a planned weekend closure.", citations=[]),
                       session, tools, turn, captor)

    assistant_finals = [
        f for f in captor.frames
        if f["type"] == "transcript_delta"
        and f["role"] == "assistant"
        and f["final"] is True
        and f["text"]
    ]
    assert len(assistant_finals) == 2, (
        "Two distinct assistant turns must both reach the client; "
        f"got: {[f['text'] for f in assistant_finals]}"
    )
