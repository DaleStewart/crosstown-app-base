"""Tests for voice Pydantic models.

NOTE: app.models.voice_schemas and app.models.voice_enums are created by Tank
in parallel. These tests will fail on import until that code lands — that is
intentional (test-first, Constitution Principle V).
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4


class TestVoiceEnums:
    """Tests for VoiceSessionStatus and VoiceRole enums."""

    def test_voice_session_status_values(self):
        """VoiceSessionStatus should have active, disconnected, expired."""
        from app.models.voice_enums import VoiceSessionStatus
        assert VoiceSessionStatus.ACTIVE.value == "active"
        assert VoiceSessionStatus.DISCONNECTED.value == "disconnected"
        assert VoiceSessionStatus.EXPIRED.value == "expired"

    def test_voice_role_values(self):
        """VoiceRole should have user and assistant."""
        from app.models.voice_enums import VoiceRole
        assert VoiceRole.USER.value == "user"
        assert VoiceRole.ASSISTANT.value == "assistant"

    def test_voice_session_status_is_str_enum(self):
        """VoiceSessionStatus values should be usable as strings."""
        from app.models.voice_enums import VoiceSessionStatus
        assert VoiceSessionStatus.ACTIVE == "active"

    def test_voice_role_is_str_enum(self):
        """VoiceRole values should be usable as strings."""
        from app.models.voice_enums import VoiceRole
        assert VoiceRole.USER == "user"


class TestVoiceMessage:
    """Tests for VoiceMessage model."""

    def _make_valid(self, **overrides):
        from app.models.voice_schemas import VoiceMessage
        defaults = dict(
            id=str(uuid4()),
            session_id=str(uuid4()),
            content="I forgot my password",
            role="user",
            timestamp=datetime.now(timezone.utc),
        )
        defaults.update(overrides)
        return VoiceMessage(**defaults)

    def test_valid_voice_message(self):
        """A fully-specified VoiceMessage should be created without error."""
        msg = self._make_valid()
        assert msg.content == "I forgot my password"
        assert msg.role == "user"

    def test_input_modality_defaults_voice(self):
        """input_modality should default to 'voice'."""
        msg = self._make_valid()
        assert msg.input_modality == "voice"

    def test_is_pii_filtered_defaults_false(self):
        """is_pii_filtered should default to False."""
        msg = self._make_valid()
        assert msg.is_pii_filtered is False

    def test_content_min_length_enforced(self):
        """Empty content should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(content="")

    def test_content_max_length_enforced(self):
        """Content exceeding 4000 chars should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(content="x" * 4001)

    def test_content_exactly_4000_chars_accepted(self):
        """Content of exactly 4000 characters should be accepted."""
        msg = self._make_valid(content="a" * 4000)
        assert len(msg.content) == 4000

    def test_role_assistant_accepted(self):
        """role='assistant' should be a valid value."""
        msg = self._make_valid(role="assistant")
        assert msg.role == "assistant"

    def test_role_invalid_rejected(self):
        """An invalid role value should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(role="system")


class TestRealtimeSessionRequest:
    """Tests for RealtimeSessionRequest model."""

    def test_session_id_defaults_none(self):
        """session_id should default to None."""
        from app.models.voice_schemas import RealtimeSessionRequest
        req = RealtimeSessionRequest()
        assert req.session_id is None

    def test_voice_defaults_alloy(self):
        """voice should default to 'alloy'."""
        from app.models.voice_schemas import RealtimeSessionRequest
        req = RealtimeSessionRequest()
        assert req.voice == "alloy"

    def test_explicit_session_id(self):
        """An explicit session_id should be stored."""
        from app.models.voice_schemas import RealtimeSessionRequest
        sid = str(uuid4())
        req = RealtimeSessionRequest(session_id=sid)
        assert req.session_id == sid

    def test_instructions_defaults_none(self):
        """instructions should default to None."""
        from app.models.voice_schemas import RealtimeSessionRequest
        req = RealtimeSessionRequest()
        assert req.instructions is None

    def test_instructions_max_length_enforced(self):
        """instructions exceeding 2000 chars should raise a validation error."""
        from app.models.voice_schemas import RealtimeSessionRequest
        with pytest.raises(Exception):
            RealtimeSessionRequest(instructions="x" * 2001)


class TestRealtimeSessionResponse:
    """Tests for RealtimeSessionResponse model."""

    def _make_valid(self, **overrides):
        from app.models.voice_schemas import RealtimeSessionResponse
        defaults = dict(
            session_id=str(uuid4()),
            token="ephemeral-token-abc123",
            expires_at=datetime.now(timezone.utc),
            endpoint="https://eastus.openai.azure.com/openai/realtime",
            deployment="gpt-4.1-realtime-preview",
        )
        defaults.update(overrides)
        return RealtimeSessionResponse(**defaults)

    def test_all_required_fields_present(self):
        """RealtimeSessionResponse should be created with all required fields."""
        resp = self._make_valid()
        assert resp.token == "ephemeral-token-abc123"
        assert resp.endpoint
        assert resp.deployment

    def test_missing_token_raises(self):
        """Omitting token should raise a validation error."""
        with pytest.raises(Exception):
            from app.models.voice_schemas import RealtimeSessionResponse
            RealtimeSessionResponse(
                session_id=str(uuid4()),
                expires_at=datetime.now(timezone.utc),
                endpoint="https://example.com",
                deployment="gpt-4.1-realtime-preview",
            )

    def test_session_id_stored(self):
        """session_id should be stored as-is."""
        sid = str(uuid4())
        resp = self._make_valid(session_id=sid)
        assert resp.session_id == sid


class TestToolDefinition:
    """Tests for ToolDefinition model."""

    def _make_valid(self, **overrides):
        from app.models.voice_schemas import ToolDefinition
        defaults = dict(
            name="analyze_and_route_query",
            description="Classifies user intent and routes to a department",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}},
        )
        defaults.update(overrides)
        return ToolDefinition(**defaults)

    def test_type_literal_default_function(self):
        """type should default to 'function'."""
        tool = self._make_valid()
        assert tool.type == "function"

    def test_name_stored(self):
        """Tool name should be stored correctly."""
        tool = self._make_valid(name="check_ticket_status")
        assert tool.name == "check_ticket_status"

    def test_parameters_dict_stored(self):
        """parameters dict should be stored as-is."""
        params = {"type": "object", "properties": {}}
        tool = self._make_valid(parameters=params)
        assert tool.parameters == params


class TestToolCallRequest:
    """Tests for ToolCallRequest model."""

    def test_arguments_default_empty_dict(self):
        """arguments should default to an empty dict."""
        from app.models.voice_schemas import ToolCallRequest
        req = ToolCallRequest(call_id="call-1", tool_name="check_ticket_status")
        assert req.arguments == {}

    def test_call_id_and_tool_name_stored(self):
        """call_id and tool_name should be stored correctly."""
        from app.models.voice_schemas import ToolCallRequest
        req = ToolCallRequest(
            call_id="call-42",
            tool_name="search_knowledge_base",
            arguments={"query": "password reset"},
        )
        assert req.call_id == "call-42"
        assert req.tool_name == "search_knowledge_base"
        assert req.arguments == {"query": "password reset"}

    def test_missing_call_id_raises(self):
        """Omitting call_id should raise a validation error."""
        from app.models.voice_schemas import ToolCallRequest
        with pytest.raises(Exception):
            ToolCallRequest(tool_name="search_knowledge_base")


class TestToolCallResponse:
    """Tests for ToolCallResponse model."""

    def test_error_defaults_none(self):
        """error should default to None on success."""
        from app.models.voice_schemas import ToolCallResponse
        resp = ToolCallResponse(call_id="call-1", result='{"status": "ok"}')
        assert resp.error is None

    def test_call_id_echoed(self):
        """call_id should be stored and match the request call_id."""
        from app.models.voice_schemas import ToolCallResponse
        resp = ToolCallResponse(call_id="call-99", result='{"ticket_id": "TKT-IT-20260101-0001"}')
        assert resp.call_id == "call-99"

    def test_error_can_be_set(self):
        """error field can carry a non-None string on failure."""
        from app.models.voice_schemas import ToolCallResponse
        resp = ToolCallResponse(call_id="call-1", result="", error="Tool execution failed")
        assert resp.error == "Tool execution failed"

    def test_missing_result_raises(self):
        """Omitting result should raise a validation error."""
        from app.models.voice_schemas import ToolCallResponse
        with pytest.raises(Exception):
            ToolCallResponse(call_id="call-1")


class TestVoiceState:
    """Tests for VoiceState model."""

    def _make_valid(self, **overrides):
        from app.models.voice_schemas import VoiceState
        now = datetime.now(timezone.utc)
        defaults = dict(
            session_id=str(uuid4()),
            status="active",
            created_at=now,
            last_activity=now,
        )
        defaults.update(overrides)
        return VoiceState(**defaults)

    def test_valid_voice_state(self):
        """A fully-specified VoiceState should be created without error."""
        vs = self._make_valid()
        assert vs.status == "active"
        assert vs.transcript == []

    def test_user_id_defaults_none(self):
        """user_id should default to None for anonymous sessions."""
        vs = self._make_valid()
        assert vs.user_id is None

    def test_valid_sha256_user_id_accepted(self):
        """A 64-character hex string should be accepted as user_id."""
        import hashlib
        uid = hashlib.sha256(b"student123").hexdigest()
        vs = self._make_valid(user_id=uid)
        assert vs.user_id == uid

    def test_short_user_id_rejected(self):
        """A user_id shorter than 64 chars should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(user_id="tooshort")

    def test_non_64_char_user_id_rejected(self):
        """A user_id that is not 64 chars should fail even if it looks like hex."""
        with pytest.raises(Exception):
            self._make_valid(user_id="abc123" * 5)  # 30 chars

    def test_transcript_defaults_empty_list(self):
        """transcript should default to an empty list."""
        vs = self._make_valid()
        assert vs.transcript == []

    def test_status_invalid_value_rejected(self):
        """An invalid status should raise a validation error."""
        with pytest.raises(Exception):
            self._make_valid(status="unknown")

    def test_status_disconnected_accepted(self):
        """status='disconnected' is a valid lifecycle value."""
        vs = self._make_valid(status="disconnected")
        assert vs.status == "disconnected"

    def test_status_expired_accepted(self):
        """status='expired' is a valid lifecycle value."""
        vs = self._make_valid(status="expired")
        assert vs.status == "expired"
