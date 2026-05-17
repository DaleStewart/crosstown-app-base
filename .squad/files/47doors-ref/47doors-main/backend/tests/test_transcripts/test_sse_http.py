"""HTTP-level integration tests for the SSE transcript stream.

Tests route registration, response headers, and verifies the SSE generator
works at the full app level (not just in isolation).

NOTE: httpx ASGITransport does not support true SSE streaming (it buffers
the entire response). Generator-level streaming is tested in
test_transcript_bus.py. Full end-to-end streaming is tested in the
Playwright suite (live-transcript.spec.ts).
"""

import asyncio
import json
import os

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MOCK_MODE", "true")


class TestSSERouteConfiguration:
    """Verify the SSE endpoint is mounted correctly in the app."""

    def test_route_exists_at_expected_path(self):
        from app.main import app

        paths = [r.path for r in app.routes]
        assert "/api/phone/transcripts/stream" in paths

    def test_route_is_get_method(self):
        from app.main import app

        for route in app.routes:
            if hasattr(route, "path") and route.path == "/api/phone/transcripts/stream":
                assert "GET" in route.methods
                break
        else:
            pytest.fail("SSE route not found")

    def test_transcripts_router_shares_phone_prefix(self):
        """Transcripts router is mounted at /api/phone, same prefix as phone
        router. This means /api/phone/transcripts/stream is the full path."""
        from app.main import app

        phone_paths = [
            r.path for r in app.routes
            if hasattr(r, "path") and r.path.startswith("/api/phone")
        ]
        assert "/api/phone/transcripts/stream" in phone_paths
        # Phone health should also be here
        assert "/api/phone/health" in phone_paths


class TestSSEResponseHeaders:
    """Verify the StreamingResponse returns correct SSE headers."""

    @pytest.mark.asyncio
    async def test_response_media_type_and_headers(self):
        """Check that the SSE endpoint returns the correct content type and
        anti-buffering headers (critical for nginx/proxy passthrough)."""
        from unittest.mock import AsyncMock

        from app.api.transcripts import stream_transcripts

        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = True  # disconnect immediately

        response = await stream_transcripts(mock_request)

        assert response.media_type == "text/event-stream"
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("connection") == "keep-alive"
        assert response.headers.get("x-accel-buffering") == "no"


class TestSSEGeneratorIntegration:
    """Test the SSE generator with the real TranscriptBus singleton."""

    @pytest.mark.asyncio
    async def test_singleton_bus_delivers_events_to_generator(self):
        """Publish events to the module-level transcript_bus singleton and
        verify the SSE generator (which also uses that singleton) yields them."""
        from unittest.mock import AsyncMock

        from app.api.transcripts import _event_generator
        from app.services.transcript_bus import transcript_bus

        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        gen = _event_generator(mock_request)
        received: list[dict] = []

        test_events = [
            {"type": "call_started", "call_id": "int-1", "phone_number": "+19132171946"},
            {"type": "user_speech", "text": "How do I register?", "call_id": "int-1"},
            {"type": "agent_speech", "text": "Visit the portal.", "call_id": "int-1"},
            {"type": "tool_call", "tool": "search_kb", "summary": "3 results", "call_id": "int-1"},
            {"type": "call_ended", "call_id": "int-1", "duration_seconds": 45},
        ]

        async def _read():
            async for chunk in gen:
                if chunk.startswith("data: "):
                    received.append(json.loads(chunk[len("data: "):].strip()))
                    if len(received) >= len(test_events):
                        return

        async def _publish():
            await asyncio.sleep(0.05)
            for ev in test_events:
                await transcript_bus.publish(ev)

        await asyncio.wait_for(
            asyncio.gather(_read(), _publish()),
            timeout=5.0,
        )

        assert len(received) == 5
        assert [e["type"] for e in received] == [
            "call_started", "user_speech", "agent_speech", "tool_call", "call_ended",
        ]
        assert received[1]["text"] == "How do I register?"
        assert received[2]["text"] == "Visit the portal."
        assert received[4]["duration_seconds"] == 45
        # Timestamps should be auto-added
        for e in received:
            assert "timestamp" in e

    @pytest.mark.asyncio
    async def test_sse_format_is_valid(self):
        """Each SSE frame must be 'data: {json}\\n\\n' — verify exact format."""
        from unittest.mock import AsyncMock

        from app.api.transcripts import _event_generator
        from app.services.transcript_bus import transcript_bus

        mock_request = AsyncMock()
        mock_request.is_disconnected.return_value = False

        gen = _event_generator(mock_request)
        raw_chunks: list[str] = []

        async def _read():
            async for chunk in gen:
                raw_chunks.append(chunk)
                if chunk.startswith("data: "):
                    return

        async def _publish():
            await asyncio.sleep(0.05)
            await transcript_bus.publish({
                "type": "user_speech", "text": "hello", "call_id": "fmt-1"
            })

        await asyncio.wait_for(
            asyncio.gather(_read(), _publish()),
            timeout=5.0,
        )

        data_chunks = [c for c in raw_chunks if c.startswith("data: ")]
        assert len(data_chunks) == 1
        # Must end with \n\n for SSE spec compliance
        assert data_chunks[0].endswith("\n\n")
        # JSON must be parseable
        json_str = data_chunks[0][len("data: "):].strip()
        payload = json.loads(json_str)
        assert payload["type"] == "user_speech"
