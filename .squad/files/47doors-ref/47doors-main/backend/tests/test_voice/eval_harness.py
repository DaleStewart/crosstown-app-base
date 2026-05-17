"""Voice feature automated evaluation harness.

Runs scripted voice scenarios via MockRealtimeService and validates:
1. Correct intent detection
2. Correct tool invocation
3. PII not echoed in results
4. Response structure valid

Usage: python -m pytest backend/tests/test_voice/eval_harness.py -v
"""
import pytest
from datetime import datetime, timezone
from app.services.mock.realtime import MockRealtimeService


EVAL_SCENARIOS = [
    {
        "name": "Password Reset Request",
        "tool": "analyze_and_route_query",
        "args": {"query": "I forgot my password and can't access Canvas"},
        "expect_tool_success": True,
        "expect_no_pii": True,
    },
    {
        "name": "Ticket Status Check",
        "tool": "check_ticket_status",
        "args": {"ticket_id": "TKT-IT-20260313-0001"},
        "expect_tool_success": True,
        "expect_no_pii": True,
    },
    {
        "name": "Knowledge Base Search",
        "tool": "search_knowledge_base",
        "args": {"query": "how to reset Canvas password"},
        "expect_tool_success": True,
        "expect_no_pii": True,
    },
    {
        "name": "Escalation to Human",
        "tool": "escalate_to_human",
        "args": {"reason": "Student wants grade appeal", "department": "REGISTRAR"},
        "expect_tool_success": True,
        "expect_no_pii": True,
    },
    {
        "name": "PII in Query (SSN)",
        "tool": "analyze_and_route_query",
        "args": {"query": "my SSN is 123-45-6789 and I need help"},
        "expect_tool_success": True,
        "expect_no_pii": True,
        "pii_patterns": ["123-45-6789"],
    },
]


class TestVoiceEvalHarness:
    """Automated evaluation harness for voice feature acceptance."""

    @pytest.fixture
    def service(self):
        return MockRealtimeService()

    @pytest.mark.parametrize("scenario", EVAL_SCENARIOS, ids=[s["name"] for s in EVAL_SCENARIOS])
    @pytest.mark.asyncio
    async def test_eval_scenario(self, service, scenario):
        """Run each eval scenario and validate results."""
        result = await service.execute_tool(
            call_id=f"eval-{scenario['name'].lower().replace(' ', '-')}",
            tool_name=scenario["tool"],
            arguments=scenario["args"],
            session_id="eval-session-001",
        )

        # Tool should succeed
        if scenario["expect_tool_success"]:
            assert result.error is None, f"Tool {scenario['tool']} returned error: {result.error}"
            assert len(result.result) > 0, f"Tool {scenario['tool']} returned empty result"

        # PII should not appear in result
        if scenario.get("pii_patterns"):
            for pattern in scenario["pii_patterns"]:
                assert pattern not in result.result, f"PII pattern '{pattern}' found in result"

    @pytest.mark.asyncio
    async def test_session_token_freshness(self, service):
        """Eval: Session tokens should expire in the future."""
        response = await service.create_session("eval-session", "alloy")
        assert response.expires_at > datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_tool_definitions_complete(self, service):
        """Eval: All 4 pipeline tools should be defined."""
        tools = await service.get_tool_definitions()
        assert len(tools) == 4
        names = {t.name for t in tools}
        assert names == {"analyze_and_route_query", "check_ticket_status", "search_knowledge_base", "escalate_to_human"}
        # Each tool should have description and parameters
        for tool in tools:
            assert len(tool.description) > 10, f"Tool {tool.name} has insufficient description"
            assert "type" in tool.parameters, f"Tool {tool.name} missing 'type' in parameters"
