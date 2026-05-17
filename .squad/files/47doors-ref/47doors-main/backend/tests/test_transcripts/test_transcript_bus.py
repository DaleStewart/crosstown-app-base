"""Tests for the TranscriptBus and SSE transcript streaming endpoint."""

import asyncio
import json
import os

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MOCK_MODE", "true")

from app.services.transcript_bus import TranscriptBus, transcript_bus


# ---------------------------------------------------------------------------
# TranscriptBus unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bus_publish_to_single_subscriber():
    bus = TranscriptBus()
    async with bus.subscribe() as q:
        await bus.publish({"type": "user_speech", "text": "hello", "call_id": "c1"})
        event = q.get_nowait()
        assert event["type"] == "user_speech"
        assert event["text"] == "hello"
        assert "timestamp" in event


@pytest.mark.asyncio
async def test_bus_publish_to_multiple_subscribers():
    bus = TranscriptBus()
    async with bus.subscribe() as q1, bus.subscribe() as q2:
        await bus.publish({"type": "agent_speech", "text": "hi", "call_id": "c2"})
        e1 = q1.get_nowait()
        e2 = q2.get_nowait()
        assert e1["text"] == "hi"
        assert e2["text"] == "hi"


@pytest.mark.asyncio
async def test_bus_subscriber_removed_after_context_exit():
    bus = TranscriptBus()
    async with bus.subscribe():
        assert bus.subscriber_count == 1
    assert bus.subscriber_count == 0


@pytest.mark.asyncio
async def test_bus_preserves_existing_timestamp():
    bus = TranscriptBus()
    ts = "2026-01-01T00:00:00Z"
    async with bus.subscribe() as q:
        await bus.publish({"type": "call_started", "timestamp": ts, "call_id": "c3"})
        event = q.get_nowait()
        assert event["timestamp"] == ts


@pytest.mark.asyncio
async def test_bus_drops_slow_subscriber():
    bus = TranscriptBus()
    async with bus.subscribe() as q:
        for i in range(257):
            await bus.publish({"type": "agent_speech", "text": str(i), "call_id": "c4"})
        assert bus.subscriber_count == 0


# ---------------------------------------------------------------------------
# SSE endpoint tests — test route registration & generator directly
# ---------------------------------------------------------------------------


def test_sse_route_registered():
    """The transcript SSE route is mounted at the expected path."""
    from app.main import app

    paths = [r.path for r in app.routes]
    assert "/api/phone/transcripts/stream" in paths


@pytest.mark.asyncio
async def test_sse_generator_yields_published_events():
    """The SSE generator yields JSON data lines from the transcript bus."""
    from unittest.mock import AsyncMock

    from app.api.transcripts import _event_generator

    mock_request = AsyncMock()
    mock_request.is_disconnected.return_value = False

    gen = _event_generator(mock_request)
    received: list[dict] = []

    async def _read():
        async for chunk in gen:
            if chunk.startswith("data: "):
                received.append(json.loads(chunk[len("data: "):].strip()))
                if len(received) >= 1:
                    return

    async def _drive():
        task = asyncio.create_task(_read())
        await asyncio.sleep(0.05)
        await transcript_bus.publish({
            "type": "user_speech",
            "text": "I need help",
            "call_id": "test-123",
        })
        await task

    await asyncio.wait_for(_drive(), timeout=5.0)

    assert len(received) == 1
    assert received[0]["type"] == "user_speech"
    assert received[0]["text"] == "I need help"
    assert received[0]["call_id"] == "test-123"


@pytest.mark.asyncio
async def test_sse_generator_all_event_types():
    """All transcript event types pass through the SSE generator."""
    from unittest.mock import AsyncMock

    from app.api.transcripts import _event_generator

    mock_request = AsyncMock()
    mock_request.is_disconnected.return_value = False

    events_to_send = [
        {"type": "call_started", "call_id": "m1", "phone_number": "+19132171946"},
        {"type": "user_speech", "text": "password reset", "call_id": "m1"},
        {"type": "agent_speech", "text": "Sure thing", "call_id": "m1"},
        {"type": "tool_call", "tool": "search_kb", "summary": "3 results", "call_id": "m1"},
        {"type": "call_ended", "call_id": "m1", "duration_seconds": 30},
    ]
    received_types: list[str] = []

    gen = _event_generator(mock_request)

    async def _read():
        async for chunk in gen:
            if chunk.startswith("data: "):
                received_types.append(json.loads(chunk[len("data: "):].strip())["type"])
                if len(received_types) >= len(events_to_send):
                    return

    async def _drive():
        task = asyncio.create_task(_read())
        await asyncio.sleep(0.05)
        for ev in events_to_send:
            await transcript_bus.publish(ev)
        await task

    await asyncio.wait_for(_drive(), timeout=5.0)

    assert received_types == [
        "call_started", "user_speech", "agent_speech",
        "tool_call", "call_ended",
    ]
