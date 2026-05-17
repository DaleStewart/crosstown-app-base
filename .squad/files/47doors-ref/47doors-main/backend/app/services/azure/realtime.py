"""
Azure OpenAI Realtime API service for production voice interaction.
Manages ephemeral session tokens and tool call delegation.
"""

VOICE_SYSTEM_PROMPT = """You are the 47 Doors Universal Front Door Support Agent, speaking with a university student or staff member.

Voice-specific instructions:
- Speak concisely and naturally. Do not use markdown formatting.
- Spell out ticket IDs character by character (e.g., "T-K-T dash I-T dash two zero two six...").
- Do NOT repeat any personal identifying information the student provides (SSN, email, phone, student ID).
- If you cannot understand the request, ask for clarification politely.
- When providing search results, summarize the top result conversationally rather than listing all results.
- Acknowledge the student's concern before providing solutions.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from azure.core.credentials import AccessToken

from app.models.voice_schemas import RealtimeSessionResponse, ToolCallResponse, ToolDefinition
from app.services.interfaces import RealtimeServiceInterface

logger = logging.getLogger(__name__)


class VoiceUnavailableError(Exception):
    """Raised when Azure OpenAI Realtime API is unavailable."""
    pass


class AzureRealtimeService(RealtimeServiceInterface):
    """Production implementation using the Azure OpenAI Realtime API with managed identity."""

    def __init__(
        self,
        endpoint: str,
        deployment: str,
        api_version: str = "2025-04-01-preview",
        api_key: Optional[str] = None,
        credential: Optional[object] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.deployment = deployment
        self.api_version = api_version
        self.api_key = api_key
        self.credential = credential
        self._client = httpx.AsyncClient(timeout=30.0)
        self._token: Optional[AccessToken] = None
        self._credential_lock = asyncio.Lock()

    async def _get_auth_header(self) -> dict[str, str]:
        """Get authentication header using managed identity or API key fallback."""
        if self.api_key:
            logger.info("Realtime auth: using API key")
            return {"api-key": self.api_key}
        
        if not self.credential:
            async with self._credential_lock:
                if not self.credential:
                    from azure.identity.aio import ManagedIdentityCredential
                    self.credential = ManagedIdentityCredential()
                    logger.info("Realtime auth: created ManagedIdentityCredential")
        
        REFRESH_BUFFER_SECONDS = 300
        needs_refresh = (
            not self._token 
            or datetime.now(timezone.utc) >= datetime.fromtimestamp(
                self._token.expires_on - REFRESH_BUFFER_SECONDS, tz=timezone.utc
            )
        )
        
        if needs_refresh:
            try:
                self._token = await self.credential.get_token("https://cognitiveservices.azure.com/.default")
                logger.info(f"Realtime auth: token acquired, expires_on={self._token.expires_on}")
            except Exception as exc:
                logger.error(f"Realtime auth: token acquisition failed: {exc}")
                raise VoiceUnavailableError(
                    f"Failed to acquire managed identity token: {exc}"
                ) from exc
        
        return {"Authorization": f"Bearer {self._token.token}"}

    async def create_session(
        self,
        session_id: str,
        voice: str,
        instructions: Optional[str] = None,
    ) -> RealtimeSessionResponse:
        """Create an ephemeral realtime session via the Azure OpenAI API."""
        url = f"{self.endpoint}/openai/v1/realtime/client_secrets"
        
        try:
            auth_header = await self._get_auth_header()
        except VoiceUnavailableError:
            raise
        except Exception as exc:
            raise VoiceUnavailableError(
                f"Authentication setup failed: {exc}"
            ) from exc
        
        auth_type = "Bearer" if "Authorization" in auth_header else "api-key"
        logger.info(f"Realtime create_session: url={url}, auth_type={auth_type}, deployment={self.deployment}")
        
        headers = {
            **auth_header,
            "Content-Type": "application/json",
        }
        
        # Use GA nested format for session config in /client_secrets body.
        # Preview flat fields (voice, input_audio_transcription) cause 500;
        # GA nested fields (audio.input.transcription, audio.output.voice) work.
        session_config = {
            "session": {
                "type": "realtime",
                "model": self.deployment,
                "instructions": instructions or VOICE_SYSTEM_PROMPT,
                "audio": {
                    "input": {
                        "transcription": {
                            "model": "whisper-1",
                        },
                    },
                    "output": {
                        "voice": voice,
                        "transcription": {
                            "model": "whisper-1",
                        },
                    },
                },
            },
        }

        # Try with output transcription first; fall back without it if rejected.
        # The frontend session.update also requests it as a backup.
        response = None
        for attempt, config in enumerate([session_config, None]):
            if config is None:
                # Build fallback config without audio.output.transcription
                fallback = {
                    "session": {
                        **session_config["session"],
                        "audio": {
                            "input": session_config["session"]["audio"]["input"],
                            "output": {"voice": voice},
                        },
                    },
                }
                config = fallback
                logger.warning("Retrying /client_secrets without audio.output.transcription")

            try:
                response = await self._client.post(url, headers=headers, json=config)
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                error_detail = exc.response.text
                # Retry on server error only on first attempt
                if attempt == 0 and status_code >= 500:
                    logger.warning(f"Realtime API rejected config (attempt 1): {status_code}")
                    continue
                logger.error(f"Realtime API error: status={status_code}, auth_type={auth_type}, detail={error_detail}")
                if status_code == 401:
                    error_msg = f"Authentication failed (401): Credentials rejected. auth_type={auth_type}. Details: {error_detail}"
                elif status_code == 403:
                    error_msg = f"Authorization failed (403): auth_type={auth_type}. Details: {error_detail}"
                elif status_code == 404:
                    error_msg = f"Endpoint not found (404): deployment='{self.deployment}', url={url}. Details: {error_detail}"
                elif status_code >= 500:
                    error_msg = f"Azure OpenAI service error ({status_code}): {error_detail}"
                else:
                    error_msg = f"Azure OpenAI Realtime API error ({status_code}): {error_detail}"
                raise VoiceUnavailableError(error_msg) from exc
            except httpx.RequestError as exc:
                raise VoiceUnavailableError(
                    f"Network error reaching Azure OpenAI Realtime API at {url}: {exc}"
                ) from exc

        data = response.json()
        # Azure /client_secrets returns: {"value": "eph_...", "expires_at": "...", "session": {...}}
        token = data.get("value", "")
        expires_at_str = data.get("expires_at")
        
        if not token:
            logger.error(f"Realtime: empty ephemeral token from API. Response keys: {list(data.keys())}")
            raise VoiceUnavailableError("Azure OpenAI returned empty ephemeral token")
        
        logger.info(f"Realtime: ephemeral token acquired, len={len(token)}, expires_at={expires_at_str}")
        
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
        
        return RealtimeSessionResponse(
            session_id=session_id,
            token=token,
            expires_at=expires_at,
            endpoint=self.endpoint,
            deployment=self.deployment,
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
        """Delegate a Realtime API tool call to real backend services."""
        from app.core.dependencies import (
            get_knowledge_service,
            get_llm_service,
            get_ticket_service,
        )

        ticket_svc = get_ticket_service()
        knowledge_svc = get_knowledge_service()

        try:
            if tool_name == "analyze_and_route_query":
                query = arguments.get("query", "")
                logger.info("execute_tool: analyze_and_route_query query=%s", query[:100])

                # Classify intent via LLM (same as text chat QueryAgent)
                llm_svc = get_llm_service()
                query_result = await llm_svc.classify_intent(query)
                dept_enum = query_result.department_suggestion
                intent = query_result.intent

                from app.models.enums import Priority

                # Escalation-worthy queries get URGENT, else MEDIUM
                priority_enum = Priority.URGENT if query_result.requires_escalation else Priority.MEDIUM

                # Create a real ticket
                ticket_id, ticket_url = await ticket_svc.create_ticket(
                    department=dept_enum,
                    priority=priority_enum,
                    summary=f"Phone call: {query[:150]}",
                    description=f"Submitted via phone call (session {session_id}). Query: {query}",
                    student_id_hash=f"phone-{session_id}",
                )
                logger.info("execute_tool: created ticket %s dept=%s", ticket_id, dept_enum.value)

                result = json.dumps({
                    "intent": intent or "general_question",
                    "department": dept_enum.value,
                    "confidence": query_result.confidence,
                    "requires_escalation": query_result.requires_escalation,
                    "ticket_id": ticket_id,
                    "ticket_url": ticket_url,
                })

            elif tool_name == "check_ticket_status":
                ticket_id = arguments.get("ticket_id", "")
                logger.info("execute_tool: check_ticket_status id=%s", ticket_id)

                status_resp = await ticket_svc.get_ticket_status(ticket_id)
                if status_resp:
                    result = json.dumps({
                        "ticket_id": status_resp.ticket_id,
                        "status": status_resp.status.value if hasattr(status_resp.status, 'value') else str(status_resp.status),
                        "department": status_resp.department.value if hasattr(status_resp.department, 'value') else str(status_resp.department),
                        "assigned_to": status_resp.assigned_to or "Unassigned",
                        "summary": status_resp.summary or "",
                    })
                else:
                    result = json.dumps({
                        "ticket_id": ticket_id,
                        "status": "not_found",
                        "message": f"No ticket found with ID {ticket_id}",
                    })

            elif tool_name == "search_knowledge_base":
                query = arguments.get("query", "")
                logger.info("execute_tool: search_knowledge_base query=%s", query[:100])

                articles = await knowledge_svc.search(query=query, limit=3)
                result = json.dumps({
                    "articles": [
                        {
                            "article_id": a.article_id,
                            "title": a.title,
                            "snippet": a.snippet or "",
                            "relevance_score": float(a.relevance_score) if a.relevance_score else 0.0,
                        }
                        for a in articles
                    ]
                })
                logger.info("execute_tool: KB returned %d articles", len(articles))

            elif tool_name == "escalate_to_human":
                reason = arguments.get("reason", "Caller requested human agent")
                department = arguments.get("department", "IT")
                logger.info("execute_tool: escalate_to_human reason=%s dept=%s", reason[:80], department)

                from app.models.enums import Department, Priority

                try:
                    dept_enum = Department(department)
                except ValueError:
                    dept_enum = Department.ESCALATE_TO_HUMAN

                ticket_id, ticket_url = await ticket_svc.create_ticket(
                    department=dept_enum,
                    priority=Priority.URGENT,
                    summary=f"ESCALATION: {reason[:150]}",
                    description=f"Phone caller requested human escalation. Reason: {reason}. Session: {session_id}",
                    student_id_hash=f"phone-{session_id}",
                )
                logger.info("execute_tool: escalation ticket created %s", ticket_id)

                result = json.dumps({
                    "escalated": True,
                    "reason": reason,
                    "department": department,
                    "ticket_id": ticket_id,
                    "ticket_url": ticket_url,
                    "message": f"Escalation ticket {ticket_id} created. A human agent will follow up.",
                })
            else:
                return ToolCallResponse(
                    call_id=call_id,
                    result="",
                    error=f"Unknown tool: {tool_name}",
                )

        except Exception as exc:
            logger.error("execute_tool: %s failed: %s", tool_name, exc, exc_info=True)
            return ToolCallResponse(
                call_id=call_id,
                result="",
                error=f"Tool execution failed: {exc}",
            )

        return ToolCallResponse(call_id=call_id, result=result, error=None)

    async def close(self) -> None:
        """Close the HTTP client and credential."""
        await self._client.aclose()
        if hasattr(self.credential, 'close'):
            await self.credential.close()
