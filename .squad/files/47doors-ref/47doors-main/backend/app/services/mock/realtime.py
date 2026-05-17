"""
Mock Realtime service for testing and demo mode.
Returns deterministic responses without requiring Azure credentials.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from app.models.voice_schemas import RealtimeSessionResponse, ToolCallResponse, ToolDefinition
from app.services.azure.realtime import VOICE_SYSTEM_PROMPT
from app.services.interfaces import RealtimeServiceInterface


class MockRealtimeService(RealtimeServiceInterface):
    """Mock implementation of the Azure OpenAI Realtime API service."""

    async def create_session(
        self,
        session_id: str,
        voice: str,
        instructions: Optional[str] = None,
    ) -> RealtimeSessionResponse:
        """Return a mock ephemeral session token."""
        self._last_session_config = {
            "session": {
                "type": "realtime",
                "model": "gpt-realtime",
                "audio": {"output": {"voice": voice}},
                "input_audio_transcription": {"model": "whisper-1"},
                "instructions": instructions or VOICE_SYSTEM_PROMPT,
            },
        }
        return RealtimeSessionResponse(
            session_id=session_id,
            token=f"eph_mock_{uuid4()}",
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=60),
            endpoint="http://localhost:8000/mock",
            deployment="gpt-realtime",
        )

    async def get_tool_definitions(self) -> list[ToolDefinition]:
        """Return the 4 pipeline tool definitions."""
        return [
            ToolDefinition(
                name="analyze_and_route_query",
                description="Analyze a student support query, classify intent, and route to the appropriate department.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The user's support query",
                        }
                    },
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="check_ticket_status",
                description="Check the current status of a support ticket by its ID.",
                parameters={
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket ID to check status for",
                        }
                    },
                    "required": ["ticket_id"],
                },
            ),
            ToolDefinition(
                name="search_knowledge_base",
                description="Search the university knowledge base for articles related to a query.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for knowledge base",
                        }
                    },
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="escalate_to_human",
                description="Escalate the current support session to a human agent in the specified department.",
                parameters={
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for escalation",
                        },
                        "department": {
                            "type": "string",
                            "description": "Target department",
                        },
                    },
                    "required": ["reason"],
                },
            ),
        ]

    async def execute_tool(
        self,
        call_id: str,
        tool_name: str,
        arguments: dict,
        session_id: str,
    ) -> ToolCallResponse:
        """Execute a mock pipeline tool call."""
        if tool_name == "analyze_and_route_query":
            result = json.dumps({
                "intent": "general_question",
                "department": "IT",
                "confidence": 0.85,
                "requires_escalation": False,
                "ticket_id": f"TKT-IT-MOCK-{uuid4().hex[:8].upper()}",
            })
        elif tool_name == "check_ticket_status":
            ticket_id = arguments.get("ticket_id", "TKT-MOCK-0001")
            result = json.dumps({
                "ticket_id": ticket_id,
                "status": "in_progress",
                "department": "IT",
                "created_at": "2026-01-01T10:00:00Z",
                "estimated_resolution": "2026-01-01T14:00:00Z",
                "assigned_to": "Support Team",
            })
        elif tool_name == "search_knowledge_base":
            result = json.dumps({
                "articles": [
                    {
                        "article_id": "KB-001",
                        "title": "How to Reset Your Password",
                        "snippet": "Visit the IT portal at https://it.university.edu and click 'Forgot Password'.",
                        "relevance_score": 0.92,
                    },
                    {
                        "article_id": "KB-002",
                        "title": "VPN Setup Guide",
                        "snippet": "Download the VPN client from the software portal and use your university credentials.",
                        "relevance_score": 0.74,
                    },
                ]
            })
        elif tool_name == "escalate_to_human":
            result = json.dumps({
                "escalated": True,
                "reason": arguments.get("reason", "User requested escalation"),
                "department": arguments.get("department", "IT"),
                "ticket_id": f"ESC-MOCK-{uuid4().hex[:8].upper()}",
                "message": "A human agent will be with you shortly.",
            })
        else:
            return ToolCallResponse(
                call_id=call_id,
                result="",
                error=f"Unknown tool: {tool_name}",
            )

        return ToolCallResponse(call_id=call_id, result=result, error=None)
