"""Tests for MockRealtimeService.

NOTE: app.services.mock.realtime does not exist yet — Tank is implementing it.
These tests will fail on import until that code lands (test-first, Constitution Principle V).
"""
import pytest
from datetime import datetime, timezone


class TestMockRealtimeService:
    """Mock realtime service contract tests."""

    @pytest.fixture
    def service(self):
        from app.services.mock.realtime import MockRealtimeService
        return MockRealtimeService()

    async def test_create_session_returns_valid_response(self, service):
        """create_session should return RealtimeSessionResponse with non-empty token."""
        response = await service.create_session("test-session-id", "alloy")
        assert response.token
        assert response.session_id == "test-session-id"
        assert response.expires_at > datetime.now(timezone.utc)
        assert response.endpoint
        assert response.deployment

    async def test_create_session_custom_voice(self, service):
        """create_session should accept any voice name and include it or reflect it."""
        response = await service.create_session("test-session-id", "shimmer")
        assert response.session_id == "test-session-id"
        assert response.token

    async def test_create_session_generates_unique_tokens(self, service):
        """Successive create_session calls should produce different tokens."""
        r1 = await service.create_session("session-a", "alloy")
        r2 = await service.create_session("session-b", "alloy")
        assert r1.token != r2.token

    async def test_create_session_expires_in_future(self, service):
        """expires_at should be in the future relative to now."""
        response = await service.create_session("session-exp", "alloy")
        assert response.expires_at > datetime.now(timezone.utc)

    async def test_get_tool_definitions_returns_four_tools(self, service):
        """get_tool_definitions should return exactly 4 pipeline tools."""
        tools = await service.get_tool_definitions()
        assert len(tools) == 4
        tool_names = {t.name for t in tools}
        assert tool_names == {
            "analyze_and_route_query",
            "check_ticket_status",
            "search_knowledge_base",
            "escalate_to_human",
        }

    async def test_get_tool_definitions_type_is_function(self, service):
        """Each ToolDefinition should have type='function'."""
        tools = await service.get_tool_definitions()
        for tool in tools:
            assert tool.type == "function"

    async def test_get_tool_definitions_have_descriptions(self, service):
        """Each ToolDefinition should have a non-empty description."""
        tools = await service.get_tool_definitions()
        for tool in tools:
            assert tool.description

    async def test_get_tool_definitions_have_parameters(self, service):
        """Each ToolDefinition should have a non-empty parameters dict."""
        tools = await service.get_tool_definitions()
        for tool in tools:
            assert isinstance(tool.parameters, dict)

    async def test_execute_tool_returns_success(self, service):
        """execute_tool should return ToolCallResponse with no error."""
        result = await service.execute_tool(
            call_id="call-1",
            tool_name="analyze_and_route_query",
            arguments={"query": "I forgot my password"},
            session_id="test-session-id",
        )
        assert result.call_id == "call-1"
        assert result.error is None
        assert result.result  # non-empty result

    async def test_execute_tool_echoes_call_id(self, service):
        """execute_tool result.call_id must echo the incoming call_id."""
        result = await service.execute_tool(
            call_id="unique-call-xyz",
            tool_name="check_ticket_status",
            arguments={"ticket_id": "TKT-IT-20260101-0001"},
            session_id="test-session-id",
        )
        assert result.call_id == "unique-call-xyz"

    async def test_execute_tool_check_ticket_status(self, service):
        """check_ticket_status tool should return a non-empty result."""
        result = await service.execute_tool(
            call_id="call-2",
            tool_name="check_ticket_status",
            arguments={"ticket_id": "TKT-IT-20260101-0001"},
            session_id="test-session-id",
        )
        assert result.error is None
        assert result.result

    async def test_execute_tool_search_knowledge_base(self, service):
        """search_knowledge_base tool should return a non-empty result."""
        result = await service.execute_tool(
            call_id="call-3",
            tool_name="search_knowledge_base",
            arguments={"query": "how to reset password"},
            session_id="test-session-id",
        )
        assert result.error is None
        assert result.result

    async def test_execute_tool_escalate_to_human(self, service):
        """escalate_to_human tool should return a non-empty result."""
        result = await service.execute_tool(
            call_id="call-4",
            tool_name="escalate_to_human",
            arguments={"reason": "User requested human agent"},
            session_id="test-session-id",
        )
        assert result.error is None
        assert result.result

    async def test_execute_unknown_tool_returns_error(self, service):
        """An unknown tool_name should return a ToolCallResponse with error set."""
        result = await service.execute_tool(
            call_id="call-bad",
            tool_name="nonexistent_tool",
            arguments={},
            session_id="test-session-id",
        )
        assert result.call_id == "call-bad"
        assert result.error is not None
