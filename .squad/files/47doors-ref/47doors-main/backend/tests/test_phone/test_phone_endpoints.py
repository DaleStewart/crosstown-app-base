"""Tests for phone API endpoints.

Tests:
  GET  /api/phone/health        — phone availability check
  POST /api/phone/incoming      — Event Grid webhook (validation handshake + IncomingCall)
  POST /api/phone/callbacks     — Call Automation callback events

NOTE: app.api.phone does not exist yet — Tank is implementing it.
These tests will fail on import until that code lands (test-first, Constitution Principle V).
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


@pytest.fixture
def client():
    """Synchronous TestClient — default test surface for phone endpoints."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/phone/health
# ---------------------------------------------------------------------------

class TestPhoneHealth:
    """GET /api/phone/health endpoint tests."""

    def test_health_returns_200(self, client):
        """GET /api/phone/health should return HTTP 200."""
        response = client.get("/api/phone/health")
        assert response.status_code == 200

    def test_health_contains_phone_available(self, client):
        """Response should include phone_available boolean."""
        data = client.get("/api/phone/health").json()
        assert "phone_available" in data
        assert isinstance(data["phone_available"], bool)

    def test_health_contains_mock_mode(self, client):
        """Response should include mock_mode boolean."""
        data = client.get("/api/phone/health").json()
        assert "mock_mode" in data
        assert isinstance(data["mock_mode"], bool)

    def test_health_contains_phone_enabled(self, client):
        """Response should include phone_enabled boolean."""
        data = client.get("/api/phone/health").json()
        assert "phone_enabled" in data
        assert isinstance(data["phone_enabled"], bool)

    def test_health_mock_mode_true_in_test_env(self, client):
        """In the test environment (MOCK_MODE=true) mock_mode should be True."""
        data = client.get("/api/phone/health").json()
        assert data["mock_mode"] is True

    def test_health_phone_available_true_in_mock_mode(self, client):
        """Mock mode always reports phone_available=True."""
        data = client.get("/api/phone/health").json()
        assert data["phone_available"] is True


# ---------------------------------------------------------------------------
# POST /api/phone/incoming — Event Grid validation handshake
# ---------------------------------------------------------------------------

class TestIncomingCallValidationHandshake:
    """Event Grid SubscriptionValidation handshake on POST /api/phone/incoming."""

    def test_validation_handshake_returns_200(self, client):
        """Subscription validation event should return HTTP 200."""
        payload = [
            {
                "id": str(uuid4()),
                "eventType": "Microsoft.EventGrid.SubscriptionValidated",
                "subject": "",
                "eventTime": "2026-01-01T00:00:00Z",
                "data": {
                    "validationCode": "abc-validation-code-xyz",
                    "validationUrl": "https://rp-eastus.eventgrid.azure.net/validate?code=abc",
                },
                "dataVersion": "1",
            }
        ]
        response = client.post(
            "/api/phone/incoming",
            json=payload,
            headers={"aeg-event-type": "SubscriptionValidation"},
        )
        assert response.status_code == 200

    def test_validation_handshake_echoes_code(self, client):
        """Response to validation handshake must echo validationResponse."""
        validation_code = "MY-VALIDATION-CODE-12345"
        payload = [
            {
                "id": str(uuid4()),
                "eventType": "Microsoft.EventGrid.SubscriptionValidated",
                "subject": "",
                "eventTime": "2026-01-01T00:00:00Z",
                "data": {
                    "validationCode": validation_code,
                },
                "dataVersion": "1",
            }
        ]
        response = client.post(
            "/api/phone/incoming",
            json=payload,
            headers={"aeg-event-type": "SubscriptionValidation"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "validationResponse" in data
        assert data["validationResponse"] == validation_code

    def test_validation_handshake_without_url_returns_200(self, client):
        """Validation payload without validationUrl is still valid."""
        payload = [
            {
                "id": str(uuid4()),
                "eventType": "Microsoft.EventGrid.SubscriptionValidated",
                "subject": "",
                "eventTime": "2026-01-01T00:00:00Z",
                "data": {
                    "validationCode": "code-without-url",
                },
                "dataVersion": "1",
            }
        ]
        response = client.post(
            "/api/phone/incoming",
            json=payload,
            headers={"aeg-event-type": "SubscriptionValidation"},
        )
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/phone/incoming — IncomingCall event
# ---------------------------------------------------------------------------

class TestIncomingCall:
    """IncomingCall event handling on POST /api/phone/incoming."""

    def _incoming_call_payload(self, caller_id="+12065550100"):
        return [
            {
                "id": str(uuid4()),
                "eventType": "Microsoft.Communication.IncomingCall",
                "subject": "incomingCall",
                "eventTime": "2026-01-01T00:00:00Z",
                "data": {
                    "incomingCallContext": "aHR0cHM6Ly9leGFtcGxlLmNvbS9jb250ZXh0",
                    "from": {"rawId": caller_id},
                    "to": {"rawId": "+14255550199"},
                    "correlationId": str(uuid4()),
                },
                "dataVersion": "1",
            }
        ]

    def test_incoming_call_returns_200(self, client):
        """IncomingCall event should return HTTP 200."""
        response = client.post(
            "/api/phone/incoming",
            json=self._incoming_call_payload(),
            headers={"aeg-event-type": "Notification"},
        )
        assert response.status_code == 200

    def test_incoming_call_returns_json(self, client):
        """IncomingCall event response should be valid JSON."""
        response = client.post(
            "/api/phone/incoming",
            json=self._incoming_call_payload(),
            headers={"aeg-event-type": "Notification"},
        )
        assert response.status_code == 200
        assert response.json() is not None

    def test_incoming_call_anonymous_caller_accepted(self, client):
        """An anonymous/restricted caller_id should not cause a 4xx/5xx."""
        response = client.post(
            "/api/phone/incoming",
            json=self._incoming_call_payload(caller_id="Anonymous"),
            headers={"aeg-event-type": "Notification"},
        )
        assert response.status_code == 200

    def test_incoming_call_missing_payload_returns_error(self, client):
        """An empty body should return 400 or 422."""
        response = client.post(
            "/api/phone/incoming",
            content=b"",
            headers={"Content-Type": "application/json", "aeg-event-type": "Notification"},
        )
        assert response.status_code in (400, 422)

    def test_incoming_call_invalid_json_returns_error(self, client):
        """Malformed JSON body should return 400 or 422."""
        response = client.post(
            "/api/phone/incoming",
            content=b"not-json",
            headers={"Content-Type": "application/json", "aeg-event-type": "Notification"},
        )
        assert response.status_code in (400, 422)

    def test_incoming_call_empty_array_returns_error(self, client):
        """An empty JSON array payload should return 400 or 422."""
        response = client.post(
            "/api/phone/incoming",
            json=[],
            headers={"aeg-event-type": "Notification"},
        )
        assert response.status_code in (400, 422)


# ---------------------------------------------------------------------------
# POST /api/phone/callbacks — Call Automation events
# ---------------------------------------------------------------------------

class TestCallCallbacks:
    """Call Automation callback events on POST /api/phone/callbacks."""

    def _callback_payload(self, event_type="CallConnected", call_connection_id="conn-test-123"):
        return {
            "call_connection_id": call_connection_id,
            "event_type": event_type,
        }

    def test_call_connected_callback_returns_200(self, client):
        """CallConnected callback should return HTTP 200."""
        response = client.post(
            "/api/phone/callbacks",
            json=self._callback_payload(event_type="CallConnected"),
        )
        assert response.status_code == 200

    def test_call_disconnected_callback_returns_200(self, client):
        """CallDisconnected callback should return HTTP 200."""
        response = client.post(
            "/api/phone/callbacks",
            json=self._callback_payload(event_type="CallDisconnected"),
        )
        assert response.status_code == 200

    def test_play_completed_callback_returns_200(self, client):
        """PlayCompleted callback should return HTTP 200."""
        response = client.post(
            "/api/phone/callbacks",
            json=self._callback_payload(event_type="PlayCompleted"),
        )
        assert response.status_code == 200

    def test_callback_with_result_info_returns_200(self, client):
        """Callback with optional result_info should return HTTP 200."""
        response = client.post(
            "/api/phone/callbacks",
            json={
                "call_connection_id": "conn-test-456",
                "event_type": "CallConnected",
                "result_info": {"reason": "Completed", "code": 200},
            },
        )
        assert response.status_code == 200

    def test_callback_returns_json(self, client):
        """Callback response should be valid JSON."""
        response = client.post(
            "/api/phone/callbacks",
            json=self._callback_payload(),
        )
        assert response.status_code == 200
        assert response.json() is not None

    def test_unknown_event_type_callback_handled(self, client):
        """An unknown event_type should not cause a 5xx — should return 200 or 400."""
        response = client.post(
            "/api/phone/callbacks",
            json=self._callback_payload(event_type="UnknownEventType"),
        )
        assert response.status_code in (200, 400)

    def test_empty_body_callback_returns_error(self, client):
        """An empty body should return 400 or 422."""
        response = client.post(
            "/api/phone/callbacks",
            content=b"",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (400, 422)

    def test_missing_event_type_returns_error(self, client):
        """Body missing event_type should return 200 with error detail (resilient parsing)."""
        response = client.post(
            "/api/phone/callbacks",
            json={"call_connection_id": "conn-test-789"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["error"] == "missing_event_type"

    def test_missing_connection_id_returns_error(self, client):
        """Body missing call_connection_id should return 200 with error detail (resilient parsing)."""
        response = client.post(
            "/api/phone/callbacks",
            json={"event_type": "CallConnected"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["error"] == "missing_call_connection_id"
