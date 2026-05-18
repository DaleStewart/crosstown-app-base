from __future__ import annotations

import json

import pytest

from voice.base import AudioDelta, Final, ToolCall, TranscriptDelta
from voice.foundry_realtime import FoundryRealtimeSession


@pytest.fixture
def session() -> FoundryRealtimeSession:
    return FoundryRealtimeSession(ws=None)


def test_translate_audio_delta(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "response.audio.delta", "delta": "abc=="})  # noqa: SLF001
    assert isinstance(ev, AudioDelta)
    assert ev.audio_b64 == "abc=="


def test_translate_audio_delta_ga(session: FoundryRealtimeSession) -> None:
    # GA renamed response.audio.delta -> response.output_audio.delta.
    ev = session._translate(  # noqa: SLF001
        {"type": "response.output_audio.delta", "delta": "abc=="}
    )
    assert isinstance(ev, AudioDelta)
    assert ev.audio_b64 == "abc=="


def test_translate_audio_delta_empty_ignored(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "response.audio.delta", "delta": ""})  # noqa: SLF001
    assert ev is None


def test_translate_assistant_transcript_delta(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "response.audio_transcript.delta", "delta": "hel"})  # noqa: SLF001
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "assistant"
    assert ev.text == "hel"
    assert ev.final is False


def test_translate_assistant_transcript_delta_ga(session: FoundryRealtimeSession) -> None:
    # GA renamed response.audio_transcript.delta -> response.output_audio_transcript.delta.
    ev = session._translate(  # noqa: SLF001
        {"type": "response.output_audio_transcript.delta", "delta": "hel"}
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "assistant"
    assert ev.text == "hel"
    assert ev.final is False


def test_translate_assistant_transcript_done(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "response.audio_transcript.done", "transcript": "Hello."})  # noqa: SLF001
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "assistant"
    assert ev.final is True


def test_translate_assistant_transcript_done_ga(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {"type": "response.output_audio_transcript.done", "transcript": "Hello."}
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "assistant"
    assert ev.final is True


def test_translate_user_transcript_completed(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "transcript": "doors held on L2",
        }
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "user"
    assert ev.text == "doors held on L2"
    assert ev.final is True


def test_translate_user_transcript_delta(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "conversation.item.input_audio_transcription.delta",
            "delta": "doors",
        }
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "user"
    assert ev.text == "doors"
    assert ev.final is False


def test_translate_user_transcript_delta_empty_ignored(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {"type": "conversation.item.input_audio_transcription.delta", "delta": ""}
    )
    assert ev is None


def test_translate_user_transcript_failed_returns_none(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "conversation.item.input_audio_transcription.failed",
            "error": {"code": "audio_unintelligible", "message": "Could not transcribe audio."},
        }
    )
    assert ev is None


def test_translate_user_transcript_completed_ga(session: FoundryRealtimeSession) -> None:
    # Some GA builds emit conversation.item.input_transcript.completed.
    ev = session._translate(  # noqa: SLF001
        {
            "type": "conversation.item.input_transcript.completed",
            "transcript": "doors held on L2",
        }
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "user"
    assert ev.text == "doors held on L2"
    assert ev.final is True


def test_translate_user_transcript_delta_ga(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {"type": "conversation.item.input_transcript.delta", "delta": "doors"}
    )
    assert isinstance(ev, TranscriptDelta)
    assert ev.role == "user"
    assert ev.text == "doors"
    assert ev.final is False


def test_translate_tool_call(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "response.function_call_arguments.done",
            "name": "search_logs",
            "call_id": "call-abc",
            "arguments": '{"q": "doors"}',
        }
    )
    assert isinstance(ev, ToolCall)
    assert ev.name == "search_logs"
    assert ev.call_id == "call-abc"
    assert ev.arguments == {"q": "doors"}


def test_translate_response_done_with_message(session: FoundryRealtimeSession) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "audio", "transcript": "No anomalies found."}],
                    }
                ]
            },
        }
    )
    assert isinstance(ev, Final)
    assert ev.text == "No anomalies found."


def test_translate_response_done_function_call_only_returns_none(
    session: FoundryRealtimeSession,
) -> None:
    ev = session._translate(  # noqa: SLF001
        {
            "type": "response.done",
            "response": {
                "output": [{"type": "function_call", "name": "search_logs"}]
            },
        }
    )
    assert ev is None


def test_translate_unknown_returns_none(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "unknown.event", "data": "x"})  # noqa: SLF001
    assert ev is None


def test_translate_error_event_returns_none(session: FoundryRealtimeSession) -> None:
    ev = session._translate({"type": "error", "error": {"message": "bad param"}})  # noqa: SLF001
    assert ev is None


@pytest.mark.asyncio
async def test_ingest_dedupes_consecutive_identical_user_partial_deltas(
    session: FoundryRealtimeSession,
) -> None:
    """Foundry GA double-emits identical input_audio_transcription.delta frames
    (~1ms apart). Streaming partials grow; identical text == duplicate.
    Evidence: rg-crosstown-dryrun-may15/orchestrator 2026-05-18T04:24:37.242Z
    and 04:24:37.243Z both emitting "받" with final=False."""
    frame = json.dumps(
        {
            "type": "conversation.item.input_audio_transcription.delta",
            "delta": "받",
        }
    )
    await session._ingest(frame)  # noqa: SLF001
    await session._ingest(frame)  # noqa: SLF001  duplicate

    ev1 = await session._inbound.get()  # noqa: SLF001
    assert isinstance(ev1, TranscriptDelta)
    assert ev1.role == "user"
    assert ev1.text == "받"
    assert session._inbound.empty(), (  # noqa: SLF001
        "Second identical partial delta should have been deduped, "
        "but it landed on the inbound queue."
    )


@pytest.mark.asyncio
async def test_ingest_passes_through_growing_user_partial_deltas(
    session: FoundryRealtimeSession,
) -> None:
    """True streaming partials change text between frames. Don't dedupe those."""
    f1 = json.dumps(
        {"type": "conversation.item.input_audio_transcription.delta", "delta": "do"}
    )
    f2 = json.dumps(
        {"type": "conversation.item.input_audio_transcription.delta", "delta": "doors"}
    )
    await session._ingest(f1)  # noqa: SLF001
    await session._ingest(f2)  # noqa: SLF001
    ev1 = await session._inbound.get()  # noqa: SLF001
    ev2 = await session._inbound.get()  # noqa: SLF001
    assert isinstance(ev1, TranscriptDelta) and ev1.text == "do"
    assert isinstance(ev2, TranscriptDelta) and ev2.text == "doors"


@pytest.mark.asyncio
async def test_ingest_resets_dedupe_state_on_completed(
    session: FoundryRealtimeSession,
) -> None:
    """After `.completed`, a future turn starting with the same text as the
    previous partial must NOT be falsely suppressed."""
    partial = json.dumps(
        {"type": "conversation.item.input_audio_transcription.delta", "delta": "hi"}
    )
    completed = json.dumps(
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "transcript": "hi there",
        }
    )
    await session._ingest(partial)  # noqa: SLF001
    await session._ingest(completed)  # noqa: SLF001
    # New turn begins with the same partial text — must pass through.
    await session._ingest(partial)  # noqa: SLF001
    # Drain queue.
    events = []
    while not session._inbound.empty():  # noqa: SLF001
        events.append(await session._inbound.get())  # noqa: SLF001
    # partial, completed, partial-again all forwarded.
    assert len(events) == 3
    assert events[0].text == "hi"
    assert events[1].final is True
    assert events[2].text == "hi"


@pytest.mark.asyncio
async def test_ingest_resets_dedupe_state_on_failed(
    session: FoundryRealtimeSession,
) -> None:
    """Reviewer-caught regression: `.failed` ends a turn like `.completed`,
    but returns None from `_translate`. Must still clear dedupe state, else
    the next turn's first partial matching the failed turn's last partial
    is falsely suppressed."""
    partial = json.dumps(
        {"type": "conversation.item.input_audio_transcription.delta", "delta": "hi"}
    )
    failed = json.dumps(
        {
            "type": "conversation.item.input_audio_transcription.failed",
            "error": {"code": "audio_unintelligible", "message": "no speech"},
        }
    )
    await session._ingest(partial)  # noqa: SLF001
    await session._ingest(failed)  # noqa: SLF001
    await session._ingest(partial)  # noqa: SLF001  fresh turn, same first syllable

    events = []
    while not session._inbound.empty():  # noqa: SLF001
        events.append(await session._inbound.get())  # noqa: SLF001
    assert len(events) == 2, (
        f"Expected 2 forwarded partials (failed turn drops, but new turn must "
        f"pass through); got {len(events)}"
    )
    assert events[0].text == "hi"
    assert events[1].text == "hi"


@pytest.mark.asyncio
async def test_ingest_logs_error_event_contents(
    session: FoundryRealtimeSession, caplog: pytest.LogCaptureFixture
) -> None:
    """Foundry GA emits `type=error` frames mid-stream that previously were
    silently dropped (only `DROP type=error` logged, no code/message). The
    transcription model regression on 2026-05-18 was undiagnosable without
    error contents. Surface them at ERROR level so operators can grep
    `voice.foundry.*ERROR` in container logs and recover the actual reason."""
    import logging as _logging

    # The voice.foundry logger sets propagate=False (to avoid duplicate uvicorn
    # output), so pytest's caplog — which hooks the root logger — won't see
    # these records. Attach caplog's handler directly to the module logger.
    foundry_logger = _logging.getLogger("voice.foundry")
    foundry_logger.addHandler(caplog.handler)
    try:
        frame = json.dumps(
            {
                "type": "error",
                "event_id": "evt_42",
                "error": {
                    "type": "invalid_request_error",
                    "code": "unknown_parameter",
                    "param": "session.audio.input.transcription.language",
                    "message": "language is not supported for gpt-4o-mini-transcribe",
                },
            }
        )
        with caplog.at_level(_logging.ERROR, logger="voice.foundry"):
            await session._ingest(frame)  # noqa: SLF001
    finally:
        foundry_logger.removeHandler(caplog.handler)
    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert error_records, "Expected an ERROR-level log line for the Foundry error frame."
    combined = " ".join(r.getMessage() for r in error_records)
    assert "evt_42" in combined
    assert "unknown_parameter" in combined
    assert "session.audio.input.transcription.language" in combined
    assert "language is not supported" in combined
