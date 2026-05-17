"""Phone call-in feature automated evaluation harness.

Runs scripted phone call scenarios via MockPhoneService and validates:
1. Inbound call handling for various caller types
2. Call lifecycle events (Connected, Disconnected, MediaStreaming)
3. PHONE_SYSTEM_PROMPT contains key phone-specific instructions
4. Health check reports healthy
5. Concurrent calls do not interfere
6. Unknown event types are handled gracefully
7. Error scenarios (empty context, missing caller_id)

Usage: python -m pytest backend/tests/test_phone/eval_harness.py -v
"""
import pytest
from app.services.mock.phone import MockPhoneService
from app.services.azure.phone import PHONE_SYSTEM_PROMPT


EVAL_SCENARIOS = [
    {
        "name": "Standard support call",
        "caller_id": "+15551234567",
        "incoming_call_context": "eyJhbGciOiJub25lIn0.eyJjYWxsZXJJZCI6IisxNTU1MTIzNDU2NyJ9.",
        "callback_url": "https://example.edu/api/phone/events",
        "expect_status": "connecting",
    },
    {
        "name": "Unknown caller",
        "caller_id": "unknown",
        "incoming_call_context": "eyJhbGciOiJub25lIn0.eyJjYWxsZXJJZCI6InVua25vd24ifQ==.",
        "callback_url": "https://example.edu/api/phone/events",
        "expect_status": "connecting",
    },
    {
        "name": "International caller",
        "caller_id": "+442012345678",
        "incoming_call_context": "eyJhbGciOiJub25lIn0.eyJjYWxsZXJJZCI6Iis0NDIwMTIzNDU2NzgifQ==.",
        "callback_url": "https://example.edu/api/phone/events",
        "expect_status": "connecting",
    },
    {
        "name": "Campus extension caller",
        "caller_id": "x1234",
        "incoming_call_context": "eyJhbGciOiJub25lIn0.eyJjYWxsZXJJZCI6IngxMjM0In0=.",
        "callback_url": "https://example.edu/api/phone/events",
        "expect_status": "connecting",
    },
]

LIFECYCLE_EVENT_SCENARIOS = [
    {
        "name": "CallConnected event",
        "event_type": "Microsoft.Communication.CallConnected",
        "event_data": {"callConnectionId": "mock-call-abc123"},
        "expect_action": "call_connected",
        "expect_keys": ["started_at"],
    },
    {
        "name": "CallConnected bare type",
        "event_type": "CallConnected",
        "event_data": {"callConnectionId": "mock-call-def456"},
        "expect_action": "call_connected",
        "expect_keys": ["started_at"],
    },
    {
        "name": "CallDisconnected event",
        "event_type": "Microsoft.Communication.CallDisconnected",
        "event_data": {"callConnectionId": "mock-call-ghi789"},
        "expect_action": "call_disconnected",
        "expect_keys": ["ended_at"],
    },
    {
        "name": "MediaStreamingStarted event",
        "event_type": "Microsoft.Communication.MediaStreamingStarted",
        "event_data": {"callConnectionId": "mock-call-jkl012"},
        "expect_action": "media_streaming_started",
        "expect_keys": [],
    },
    {
        "name": "MediaStreamingStopped event",
        "event_type": "Microsoft.Communication.MediaStreamingStopped",
        "event_data": {"callConnectionId": "mock-call-mno345"},
        "expect_action": "media_streaming_stopped",
        "expect_keys": [],
    },
    {
        "name": "Unknown event type",
        "event_type": "Microsoft.Communication.SomeNewEvent",
        "event_data": {"callConnectionId": "mock-call-pqr678"},
        "expect_action": "unhandled",
        "expect_keys": ["event_type"],
    },
]


class TestPhoneEvalHarness:
    """Automated evaluation harness for phone call-in feature acceptance."""

    @pytest.fixture
    def service(self):
        return MockPhoneService()

    # ── Inbound call scenarios ─────────────────────────────────────────────

    @pytest.mark.parametrize("scenario", EVAL_SCENARIOS, ids=[s["name"] for s in EVAL_SCENARIOS])
    def test_inbound_call_scenario(self, service, scenario):
        """Each caller type should receive a well-formed call connection response."""
        result = service.handle_incoming_call(
            incoming_call_context=scenario["incoming_call_context"],
            caller_id=scenario["caller_id"],
            callback_url=scenario["callback_url"],
        )

        assert result["status"] == scenario["expect_status"], (
            f"Scenario '{scenario['name']}': expected status={scenario['expect_status']}, "
            f"got {result['status']}"
        )
        assert result["caller_id"] == scenario["caller_id"], (
            f"Scenario '{scenario['name']}': caller_id mismatch"
        )
        assert result["call_connection_id"].startswith("mock-call-"), (
            f"Scenario '{scenario['name']}': call_connection_id has unexpected prefix"
        )

    # ── Call lifecycle events ──────────────────────────────────────────────

    @pytest.mark.parametrize(
        "scenario",
        LIFECYCLE_EVENT_SCENARIOS,
        ids=[s["name"] for s in LIFECYCLE_EVENT_SCENARIOS],
    )
    def test_call_lifecycle_event(self, service, scenario):
        """Each ACS lifecycle event should produce the expected action dict."""
        result = service.handle_call_event(
            event_type=scenario["event_type"],
            event_data=scenario["event_data"],
        )

        assert result["action"] == scenario["expect_action"], (
            f"Event '{scenario['name']}': expected action={scenario['expect_action']}, "
            f"got {result['action']}"
        )
        assert result["call_connection_id"] == scenario["event_data"]["callConnectionId"], (
            f"Event '{scenario['name']}': call_connection_id mismatch"
        )
        for key in scenario["expect_keys"]:
            assert key in result, (
                f"Event '{scenario['name']}': expected key '{key}' missing from result"
            )

    # ── PHONE_SYSTEM_PROMPT validation ─────────────────────────────────────

    def test_system_prompt_exists(self):
        """PHONE_SYSTEM_PROMPT must be non-empty."""
        assert PHONE_SYSTEM_PROMPT, "PHONE_SYSTEM_PROMPT must not be empty"
        assert len(PHONE_SYSTEM_PROMPT) > 50, "PHONE_SYSTEM_PROMPT is suspiciously short"

    def test_system_prompt_instructs_brief_responses(self):
        """Prompt must instruct the agent to keep responses brief for phone callers."""
        lower = PHONE_SYSTEM_PROMPT.lower()
        brief_indicators = ["brief", "concise", "short", "sentence"]
        assert any(word in lower for word in brief_indicators), (
            "PHONE_SYSTEM_PROMPT should instruct brief/concise responses"
        )

    def test_system_prompt_instructs_spell_ticket_ids(self):
        """Prompt must instruct spelling out ticket IDs character by character."""
        lower = PHONE_SYSTEM_PROMPT.lower()
        assert "spell" in lower or "character" in lower, (
            "PHONE_SYSTEM_PROMPT should instruct spelling ticket IDs aloud"
        )

    def test_system_prompt_instructs_no_pii(self):
        """Prompt must instruct the agent not to repeat caller PII."""
        lower = PHONE_SYSTEM_PROMPT.lower()
        pii_indicators = ["pii", "personal", "ssn", "identifying", "do not repeat", "not repeat"]
        assert any(phrase in lower for phrase in pii_indicators), (
            "PHONE_SYSTEM_PROMPT should instruct agent not to repeat PII"
        )

    def test_system_prompt_no_markdown_formatting(self):
        """Prompt must remind agent not to use markdown (bullets, headers) by ear."""
        lower = PHONE_SYSTEM_PROMPT.lower()
        no_markdown_indicators = ["markdown", "bullet", "numbered list", "formatting"]
        assert any(word in lower for word in no_markdown_indicators), (
            "PHONE_SYSTEM_PROMPT should warn against markdown formatting"
        )

    # ── Health check ───────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_health_check_is_healthy(self, service):
        """Mock service health check must report healthy with no error message."""
        healthy, latency, error = await service.health_check()
        assert healthy is True, "MockPhoneService.health_check() should return healthy=True"
        assert latency == 0, "MockPhoneService.health_check() should return latency=0"
        assert error is None, f"MockPhoneService.health_check() returned unexpected error: {error}"

    # ── Concurrent calls ───────────────────────────────────────────────────

    def test_concurrent_calls_do_not_interfere(self, service):
        """Multiple simultaneous calls should each get distinct connection IDs."""
        callers = ["+15550000001", "+15550000002", "+15550000003"]

        results = [
            service.handle_incoming_call(
                incoming_call_context=f"ctx-{caller}",
                caller_id=caller,
                callback_url="https://example.edu/api/phone/events",
            )
            for caller in callers
        ]

        connection_ids = [r["call_connection_id"] for r in results]
        assert len(set(connection_ids)) == len(callers), (
            "Concurrent calls must receive distinct call_connection_ids; "
            f"got: {connection_ids}"
        )

        for caller, result in zip(callers, results):
            assert result["caller_id"] == caller, (
                f"Caller {caller} got back wrong caller_id: {result['caller_id']}"
            )

    # ── Unknown / graceful event handling ──────────────────────────────────

    def test_unknown_event_returns_unhandled(self, service):
        """Unrecognised event types must return action='unhandled' without raising."""
        result = service.handle_call_event(
            event_type="Microsoft.Communication.FutureUnknownEvent",
            event_data={"callConnectionId": "mock-call-zzz999"},
        )
        assert result["action"] == "unhandled", (
            f"Unknown event should produce action='unhandled', got {result['action']}"
        )
        assert "event_type" in result, "Unhandled result should echo back the event_type"

    # ── Error / edge-case scenarios ────────────────────────────────────────

    def test_empty_incoming_call_context(self, service):
        """Empty incoming_call_context should still return a valid (mock) response."""
        result = service.handle_incoming_call(
            incoming_call_context="",
            caller_id="+15551234567",
            callback_url="https://example.edu/api/phone/events",
        )
        assert result["status"] == "connecting"
        assert result["call_connection_id"].startswith("mock-call-")

    def test_missing_caller_id(self, service):
        """Empty caller_id should still return a valid (mock) response with that value."""
        result = service.handle_incoming_call(
            incoming_call_context="some-context",
            caller_id="",
            callback_url="https://example.edu/api/phone/events",
        )
        assert result["status"] == "connecting"
        assert result["caller_id"] == ""

    def test_event_with_missing_call_connection_id(self, service):
        """Events lacking callConnectionId should fall back to a safe default."""
        result = service.handle_call_event(
            event_type="CallConnected",
            event_data={},  # no callConnectionId key
        )
        assert result["action"] == "call_connected"
        assert "call_connection_id" in result
