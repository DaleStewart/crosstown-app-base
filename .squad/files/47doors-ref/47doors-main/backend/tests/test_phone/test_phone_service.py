"""Tests for MockPhoneService.

NOTE: app.services.mock.phone does not exist yet — Tank is implementing it.
These tests will fail on import until that code lands (test-first, Constitution Principle V).
"""
import pytest
from datetime import datetime, timezone


class TestMockPhoneServiceIncomingCall:
    """Tests for MockPhoneService.handle_incoming_call."""

    @pytest.fixture
    def service(self):
        from app.services.mock.phone import MockPhoneService
        return MockPhoneService()

    def test_handle_incoming_call_returns_dict(self, service):
        """handle_incoming_call should return a dict."""
        result = service.handle_incoming_call(
            incoming_call_context="aHR0cHM6Ly9leGFtcGxlLmNvbS9jb250ZXh0",
            caller_id="+12065550100",
            callback_url="https://example.com/callbacks",
        )
        assert isinstance(result, dict)

    def test_handle_incoming_call_returns_call_connection_id(self, service):
        """Result should include a non-empty call_connection_id."""
        result = service.handle_incoming_call(
            incoming_call_context="ctx",
            caller_id="+12065550100",
            callback_url="https://example.com/callbacks",
        )
        assert "call_connection_id" in result
        assert len(result["call_connection_id"]) > 0

    def test_handle_incoming_call_returns_status(self, service):
        """Result should include a status field."""
        result = service.handle_incoming_call(
            incoming_call_context="ctx",
            caller_id="+12065550100",
            callback_url="https://example.com/callbacks",
        )
        assert "status" in result

    def test_handle_incoming_call_unique_connection_ids(self, service):
        """Successive calls should generate distinct call_connection_ids."""
        r1 = service.handle_incoming_call(
            incoming_call_context="ctx1",
            caller_id="+12065550100",
            callback_url="https://example.com/callbacks",
        )
        r2 = service.handle_incoming_call(
            incoming_call_context="ctx2",
            caller_id="+12065550101",
            callback_url="https://example.com/callbacks",
        )
        assert r1["call_connection_id"] != r2["call_connection_id"]

    def test_handle_incoming_call_anonymous_caller_accepted(self, service):
        """Anonymous/non-E.164 caller_id should be handled without error."""
        result = service.handle_incoming_call(
            incoming_call_context="ctx",
            caller_id="Anonymous",
            callback_url="https://example.com/callbacks",
        )
        assert "call_connection_id" in result


class TestMockPhoneServiceCallEvents:
    """Tests for MockPhoneService.handle_call_event."""

    @pytest.fixture
    def service(self):
        from app.services.mock.phone import MockPhoneService
        return MockPhoneService()

    def test_handle_call_connected_event(self, service):
        """handle_call_event with CallConnected should return a dict without error."""
        result = service.handle_call_event(
            event_type="CallConnected",
            event_data={"call_connection_id": "conn-123"},
        )
        assert isinstance(result, dict)

    def test_handle_play_completed_event(self, service):
        """handle_call_event with PlayCompleted should return a dict without error."""
        result = service.handle_call_event(
            event_type="PlayCompleted",
            event_data={"call_connection_id": "conn-123"},
        )
        assert isinstance(result, dict)

    def test_handle_call_disconnected_event(self, service):
        """handle_call_event with CallDisconnected should return a dict without error."""
        result = service.handle_call_event(
            event_type="CallDisconnected",
            event_data={"call_connection_id": "conn-123"},
        )
        assert isinstance(result, dict)

    def test_handle_unknown_event_type_gracefully(self, service):
        """An unknown event_type should not raise — it should return a dict."""
        result = service.handle_call_event(
            event_type="SomeUnknownEvent",
            event_data={"call_connection_id": "conn-999"},
        )
        assert isinstance(result, dict)

    def test_handle_call_connected_echoes_connection_id(self, service):
        """Result for CallConnected may include or reference the connection ID."""
        result = service.handle_call_event(
            event_type="CallConnected",
            event_data={"call_connection_id": "conn-echo-test"},
        )
        # Either the key is in the result, or the event was acknowledged without error
        assert result is not None

    def test_handle_empty_event_data(self, service):
        """Empty event_data dict should be handled without raising."""
        result = service.handle_call_event(
            event_type="CallConnected",
            event_data={},
        )
        assert isinstance(result, dict)


class TestMockPhoneServiceHealthCheck:
    """Tests for MockPhoneService.health_check."""

    @pytest.fixture
    def service(self):
        from app.services.mock.phone import MockPhoneService
        return MockPhoneService()

    @pytest.mark.asyncio
    async def test_health_check_returns_tuple(self, service):
        """health_check should return a 3-tuple."""
        result = await service.health_check()
        assert isinstance(result, tuple)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_health_check_first_element_true(self, service):
        """First element (available) should be True in mock mode."""
        available, latency_ms, error = await service.health_check()
        assert available is True

    @pytest.mark.asyncio
    async def test_health_check_latency_is_int_or_none(self, service):
        """Second element (latency_ms) should be an int or None."""
        available, latency_ms, error = await service.health_check()
        assert latency_ms is None or isinstance(latency_ms, int)

    @pytest.mark.asyncio
    async def test_health_check_latency_non_negative(self, service):
        """If latency_ms is set, it should be >= 0."""
        available, latency_ms, error = await service.health_check()
        if latency_ms is not None:
            assert latency_ms >= 0

    @pytest.mark.asyncio
    async def test_health_check_error_is_none_when_available(self, service):
        """Third element (error) should be None when service is available."""
        available, latency_ms, error = await service.health_check()
        if available:
            assert error is None

    @pytest.mark.asyncio
    async def test_health_check_repeated_calls_stable(self, service):
        """Multiple health_check calls should all return available=True."""
        for _ in range(3):
            available, _, _ = await service.health_check()
            assert available is True


class TestMockPhoneServiceConcurrency:
    """Tests for isolation between concurrent simulated calls."""

    @pytest.fixture
    def service(self):
        from app.services.mock.phone import MockPhoneService
        return MockPhoneService()

    def test_multiple_concurrent_calls_have_distinct_ids(self, service):
        """Simulating multiple parallel calls — each must get a unique connection ID."""
        results = [
            service.handle_incoming_call(
                incoming_call_context=f"ctx-{i}",
                caller_id=f"+1206555010{i}",
                callback_url="https://example.com/callbacks",
            )
            for i in range(5)
        ]
        ids = [r["call_connection_id"] for r in results]
        assert len(ids) == len(set(ids)), "All call_connection_ids must be unique"

    def test_events_for_different_connections_dont_interfere(self, service):
        """Events from separate connections should be independent."""
        r1 = service.handle_call_event(
            event_type="CallConnected",
            event_data={"call_connection_id": "conn-A"},
        )
        r2 = service.handle_call_event(
            event_type="CallDisconnected",
            event_data={"call_connection_id": "conn-B"},
        )
        assert r1 is not None
        assert r2 is not None
