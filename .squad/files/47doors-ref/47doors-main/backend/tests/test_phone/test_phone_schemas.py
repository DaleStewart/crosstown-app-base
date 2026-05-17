"""Tests for phone Pydantic models.

NOTE: app.models.phone_schemas is created by Tank in parallel. These tests will
fail on import until that code lands — that is intentional (test-first,
Constitution Principle V).
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4


class TestIncomingCallEvent:
    """Tests for IncomingCallEvent model."""

    def _make_valid(self, **overrides):
        from app.models.phone_schemas import IncomingCallEvent
        defaults = dict(
            incoming_call_context="aHR0cHM6Ly9leGFtcGxlLmNvbS9jb250ZXh0",
            caller_id="+12065550100",
            callee_id="+14255550199",
            correlation_id=str(uuid4()),
        )
        defaults.update(overrides)
        return IncomingCallEvent(**defaults)

    def test_valid_incoming_call_event(self):
        """A fully-specified IncomingCallEvent should be created without error."""
        event = self._make_valid()
        assert event.caller_id == "+12065550100"
        assert event.callee_id == "+14255550199"
        assert event.incoming_call_context

    def test_missing_incoming_call_context_raises(self):
        """Omitting incoming_call_context should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import IncomingCallEvent
            IncomingCallEvent(
                caller_id="+12065550100",
                callee_id="+14255550199",
                correlation_id=str(uuid4()),
            )

    def test_missing_caller_id_raises(self):
        """Omitting caller_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import IncomingCallEvent
            IncomingCallEvent(
                incoming_call_context="context-token",
                callee_id="+14255550199",
                correlation_id=str(uuid4()),
            )

    def test_missing_callee_id_raises(self):
        """Omitting callee_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import IncomingCallEvent
            IncomingCallEvent(
                incoming_call_context="context-token",
                caller_id="+12065550100",
                correlation_id=str(uuid4()),
            )

    def test_missing_correlation_id_raises(self):
        """Omitting correlation_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import IncomingCallEvent
            IncomingCallEvent(
                incoming_call_context="context-token",
                caller_id="+12065550100",
                callee_id="+14255550199",
            )

    def test_very_long_caller_id_stored(self):
        """A very long caller_id string should be stored (schema shouldn't cap it)."""
        long_id = "+1" + "2" * 50
        event = self._make_valid(caller_id=long_id)
        assert event.caller_id == long_id

    def test_empty_string_incoming_call_context_accepted(self):
        """Empty string incoming_call_context stores as-is (no format enforcement)."""
        event = self._make_valid(incoming_call_context="")
        assert event.incoming_call_context == ""

    def test_non_e164_caller_id_accepted(self):
        """Schema does not enforce E.164 — arbitrary strings are stored."""
        event = self._make_valid(caller_id="Anonymous")
        assert event.caller_id == "Anonymous"

    def test_uuid_correlation_id_stored(self):
        """A UUID string correlation_id should be stored as-is."""
        cid = str(uuid4())
        event = self._make_valid(correlation_id=cid)
        assert event.correlation_id == cid


class TestCallEventRequest:
    """Tests for CallEventRequest model."""

    def _make_valid(self, **overrides):
        from app.models.phone_schemas import CallEventRequest
        defaults = dict(
            call_connection_id="conn-abc-123",
            event_type="CallConnected",
        )
        defaults.update(overrides)
        return CallEventRequest(**defaults)

    def test_valid_call_event_request(self):
        """A fully-specified CallEventRequest should be created without error."""
        req = self._make_valid()
        assert req.call_connection_id == "conn-abc-123"
        assert req.event_type == "CallConnected"

    def test_result_info_defaults_none(self):
        """result_info should default to None when not provided."""
        req = self._make_valid()
        assert req.result_info is None

    def test_result_info_accepts_dict(self):
        """result_info should accept a dict payload."""
        info = {"reason": "Completed", "code": 200}
        req = self._make_valid(result_info=info)
        assert req.result_info == info

    def test_missing_call_connection_id_raises(self):
        """Omitting call_connection_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import CallEventRequest
            CallEventRequest(event_type="CallConnected")

    def test_missing_event_type_raises(self):
        """Omitting event_type should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import CallEventRequest
            CallEventRequest(call_connection_id="conn-abc-123")

    def test_empty_string_event_type_stored(self):
        """Empty string event_type is stored as-is (no enum enforcement at schema level)."""
        req = self._make_valid(event_type="")
        assert req.event_type == ""


class TestCallState:
    """Tests for CallState model."""

    def _make_valid(self, **overrides):
        from app.models.phone_schemas import CallState
        defaults = dict(
            call_connection_id="conn-xyz-456",
            caller_id="+12065550100",
            status="ringing",
            started_at=datetime.now(timezone.utc),
        )
        defaults.update(overrides)
        return CallState(**defaults)

    def test_valid_call_state_ringing(self):
        """A CallState with status='ringing' should be created without error."""
        state = self._make_valid(status="ringing")
        assert state.status == "ringing"

    def test_status_connected_accepted(self):
        """status='connected' is a valid literal value."""
        state = self._make_valid(status="connected")
        assert state.status == "connected"

    def test_status_disconnected_accepted(self):
        """status='disconnected' is a valid literal value."""
        state = self._make_valid(status="disconnected")
        assert state.status == "disconnected"

    def test_status_failed_accepted(self):
        """status='failed' is a valid literal value."""
        state = self._make_valid(status="failed")
        assert state.status == "failed"

    def test_status_invalid_rejected(self):
        """An invalid status literal should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(status="unknown")

    def test_status_active_rejected(self):
        """'active' is not a valid phone call status and should be rejected."""
        with pytest.raises(Exception):
            self._make_valid(status="active")

    def test_ended_at_defaults_none(self):
        """ended_at should default to None for an active call."""
        state = self._make_valid()
        assert state.ended_at is None

    def test_ended_at_accepts_datetime(self):
        """ended_at should accept a datetime value."""
        ended = datetime.now(timezone.utc)
        state = self._make_valid(ended_at=ended)
        assert state.ended_at == ended

    def test_missing_call_connection_id_raises(self):
        """Omitting call_connection_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import CallState
            CallState(
                caller_id="+12065550100",
                status="ringing",
                started_at=datetime.now(timezone.utc),
            )

    def test_missing_caller_id_raises(self):
        """Omitting caller_id should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import CallState
            CallState(
                call_connection_id="conn-xyz-456",
                status="ringing",
                started_at=datetime.now(timezone.utc),
            )

    def test_missing_started_at_raises(self):
        """Omitting started_at should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import CallState
            CallState(
                call_connection_id="conn-xyz-456",
                caller_id="+12065550100",
                status="ringing",
            )

    def test_caller_id_very_long_stored(self):
        """A very long caller_id is stored as-is."""
        long_id = "+1" + "9" * 40
        state = self._make_valid(caller_id=long_id)
        assert state.caller_id == long_id


class TestPhoneHealthResponse:
    """Tests for PhoneHealthResponse model."""

    def _make_valid(self, **overrides):
        from app.models.phone_schemas import PhoneHealthResponse
        defaults = dict(
            phone_available=True,
            mock_mode=True,
            phone_enabled=True,
        )
        defaults.update(overrides)
        return PhoneHealthResponse(**defaults)

    def test_valid_health_response(self):
        """A fully-specified PhoneHealthResponse should be created without error."""
        resp = self._make_valid()
        assert resp.phone_available is True
        assert resp.mock_mode is True
        assert resp.phone_enabled is True

    def test_all_false_accepted(self):
        """All-False PhoneHealthResponse is valid (phone unavailable state)."""
        resp = self._make_valid(phone_available=False, mock_mode=False, phone_enabled=False)
        assert resp.phone_available is False
        assert resp.phone_enabled is False

    def test_missing_phone_available_raises(self):
        """Omitting phone_available should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import PhoneHealthResponse
            PhoneHealthResponse(mock_mode=True, phone_enabled=True)

    def test_missing_mock_mode_raises(self):
        """Omitting mock_mode should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import PhoneHealthResponse
            PhoneHealthResponse(phone_available=True, phone_enabled=True)

    def test_missing_phone_enabled_raises(self):
        """Omitting phone_enabled should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import PhoneHealthResponse
            PhoneHealthResponse(phone_available=True, mock_mode=True)

    def test_non_boolean_phone_available_coerced(self):
        """Pydantic should coerce truthy values to bool for phone_available."""
        resp = self._make_valid(phone_available=1)
        assert resp.phone_available is True


class TestEventGridValidationEvent:
    """Tests for EventGridValidationEvent model."""

    def test_valid_with_both_fields(self):
        """EventGridValidationEvent with both fields should succeed."""
        from app.models.phone_schemas import EventGridValidationEvent
        evt = EventGridValidationEvent(
            validationCode="abc123",
            validationUrl="https://rp-eastus.eventgrid.azure.net/validate?code=abc123",
        )
        assert evt.validationCode == "abc123"
        assert evt.validationUrl is not None

    def test_valid_without_validation_url(self):
        """validationUrl is optional — omitting it should succeed."""
        from app.models.phone_schemas import EventGridValidationEvent
        evt = EventGridValidationEvent(validationCode="xyz456")
        assert evt.validationCode == "xyz456"
        assert evt.validationUrl is None

    def test_validation_url_defaults_none(self):
        """validationUrl should default to None when not supplied."""
        from app.models.phone_schemas import EventGridValidationEvent
        evt = EventGridValidationEvent(validationCode="test")
        assert evt.validationUrl is None

    def test_missing_validation_code_raises(self):
        """Omitting validationCode should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.phone_schemas import EventGridValidationEvent
            EventGridValidationEvent(
                validationUrl="https://rp-eastus.eventgrid.azure.net/validate?code=abc123"
            )

    def test_empty_validation_code_accepted(self):
        """Empty string validationCode is stored as-is (no length enforcement)."""
        from app.models.phone_schemas import EventGridValidationEvent
        evt = EventGridValidationEvent(validationCode="")
        assert evt.validationCode == ""

    def test_validation_code_stored_exactly(self):
        """validationCode is stored without modification."""
        from app.models.phone_schemas import EventGridValidationEvent
        code = "ABCDEF-1234-XYZ"
        evt = EventGridValidationEvent(validationCode=code)
        assert evt.validationCode == code
