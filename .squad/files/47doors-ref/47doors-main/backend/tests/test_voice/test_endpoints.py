"""Tests for voice realtime API endpoints.

T016: POST /api/realtime/session returns valid session in mock mode
T017: Providing session_id preserves it in response
T018: WebSocket relays tool calls (placeholder — requires WS route)
T019: Invalid token closes WebSocket with 4001 (placeholder)

These tests will fail until Phase 3 implementation lands (test-first).
"""
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sync_client():
    """Synchronous TestClient — supports WebSocket testing via starlette."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async HTTPX client for async endpoint tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# T016 + T017: POST /api/realtime/session
# ---------------------------------------------------------------------------

class TestCreateSession:
    """POST /api/realtime/session endpoint tests."""

    def test_create_session_mock_mode(self, sync_client):
        """T016: POST /api/realtime/session returns valid session in mock mode."""
        response = sync_client.post(
            "/api/realtime/session",
            json={"voice": "alloy"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "token" in data
        assert len(data["token"]) > 0
        assert "expires_at" in data
        assert "endpoint" in data
        assert "deployment" in data

    def test_create_session_with_existing_session_id(self, sync_client):
        """T017: Providing session_id preserves it in the response."""
        test_id = "test-session-12345"
        response = sync_client.post(
            "/api/realtime/session",
            json={"session_id": test_id, "voice": "shimmer"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == test_id

    def test_create_session_generates_uuid_when_none(self, sync_client):
        """Session ID is auto-generated as a non-empty string when not provided."""
        response = sync_client.post(
            "/api/realtime/session",
            json={"voice": "alloy"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["session_id"]) > 0

    def test_create_session_token_is_ephemeral(self, sync_client):
        """Token should start with 'eph_' prefix in mock mode."""
        response = sync_client.post(
            "/api/realtime/session",
            json={"voice": "alloy"},
        )
        assert response.status_code == 200
        token = response.json()["token"]
        assert token.startswith("eph_")

    def test_create_session_unique_tokens(self, sync_client):
        """Successive calls return different tokens."""
        r1 = sync_client.post("/api/realtime/session", json={"voice": "alloy"})
        r2 = sync_client.post("/api/realtime/session", json={"voice": "alloy"})
        assert r1.json()["token"] != r2.json()["token"]


# ---------------------------------------------------------------------------
# T018 + T019: WebSocket /api/realtime/ws
# ---------------------------------------------------------------------------

class TestWebSocketRelay:
    """WebSocket /api/realtime/ws endpoint tests."""

    def test_websocket_tool_call_relay(self, sync_client):
        """T018: WebSocket relays tool calls and returns function results.

        Uses starlette TestClient which natively supports WebSocket connections.
        """
        session_resp = sync_client.post(
            "/api/realtime/session",
            json={"voice": "alloy"},
        )
        assert session_resp.status_code == 200, (
            "Session endpoint must exist before WS relay test can run"
        )
        session = session_resp.json()
        token = session["token"]
        session_id = session["session_id"]

        with sync_client.websocket_connect(
            f"/api/realtime/ws?session_id={session_id}&token={token}"
        ) as ws:
            tool_call_event = {
                "call_id": "call-t018",
                "tool_name": "analyze_and_route_query",
                "arguments": {"query": "I need help with my password"},
            }
            ws.send_json(tool_call_event)
            response = ws.receive_json()

            assert response.get("call_id") == "call-t018"
            assert "result" in response
            assert len(response["result"]) > 0

    def test_websocket_invalid_token_closes_4001(self, sync_client):
        """T019: Connecting with an invalid token causes close with code 4001."""
        import pytest
        from starlette.websockets import WebSocketDisconnect

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with sync_client.websocket_connect(
                "/api/realtime/ws?session_id=test&token=bad"
            ) as ws:
                ws.receive_json()

        assert exc_info.value.code == 4001
