"""Tests for PII filtering in voice tool responses.

T020: PII values in query arguments must not be echoed in tool results.

These tests verify the MockRealtimeService does not parrot back raw user input
that may contain sensitive data (SSN, email, phone number).
"""
import pytest

from app.services.mock.realtime import MockRealtimeService


class TestVoicePiiFilter:
    """PII must not leak through voice tool responses."""

    @pytest.fixture
    def service(self):
        return MockRealtimeService()

    async def test_pii_not_echoed_in_tool_result(self, service):
        """T020a: SSN in query must not appear verbatim in tool result."""
        result = await service.execute_tool(
            call_id="pii-test-1",
            tool_name="analyze_and_route_query",
            arguments={"query": "my SSN is 123-45-6789"},
            session_id="pii-test-session",
        )
        assert result.error is None
        assert "123-45-6789" not in result.result

    async def test_email_not_echoed_in_tool_result(self, service):
        """T020b: Email in query must not appear verbatim in tool result."""
        result = await service.execute_tool(
            call_id="pii-test-2",
            tool_name="analyze_and_route_query",
            arguments={"query": "my email is student@university.edu and I need help"},
            session_id="pii-test-session",
        )
        assert result.error is None
        # Mock response should not echo the raw input query back
        assert "student@university.edu" not in result.result

    async def test_phone_not_echoed_in_tool_result(self, service):
        """T020c: Phone number in query must not appear verbatim in tool result."""
        result = await service.execute_tool(
            call_id="pii-test-3",
            tool_name="search_knowledge_base",
            arguments={"query": "call me at 555-123-4567"},
            session_id="pii-test-session",
        )
        assert result.error is None
        assert "555-123-4567" not in result.result

    async def test_credit_card_not_echoed_in_tool_result(self, service):
        """T020d: Credit card number in query must not appear verbatim in tool result."""
        result = await service.execute_tool(
            call_id="pii-test-4",
            tool_name="analyze_and_route_query",
            arguments={"query": "my card number is 4111-1111-1111-1111"},
            session_id="pii-test-session",
        )
        assert result.error is None
        assert "4111-1111-1111-1111" not in result.result

    async def test_tool_result_is_non_empty_after_pii_query(self, service):
        """T020e: Tool result must still be non-empty when query contains PII."""
        result = await service.execute_tool(
            call_id="pii-test-5",
            tool_name="analyze_and_route_query",
            arguments={"query": "SSN 123-45-6789 I need password help"},
            session_id="pii-test-session",
        )
        assert result.error is None
        assert result.result  # non-empty response
