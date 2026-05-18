from __future__ import annotations

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
