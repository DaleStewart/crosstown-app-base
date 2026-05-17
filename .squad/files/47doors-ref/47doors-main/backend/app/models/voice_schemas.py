"""
Pydantic schemas for the 47 Doors voice interaction feature.
Matches the data model specification in specs/002-voice-interaction/data-model.md.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.voice_enums import VoiceRole, VoiceSessionStatus  # noqa: F401


# =============================================================================
# Transcript Models
# =============================================================================


class VoiceMessage(BaseModel):
    """A single voice transcript entry — one spoken turn."""

    id: str = Field(..., description="UUID for this transcript entry")
    session_id: str = Field(..., description="Parent session identifier")
    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="PII-filtered transcribed text"
    )
    role: Literal["user", "assistant"] = Field(
        ...,
        description="Speaker role"
    )
    input_modality: Literal["voice"] = Field(
        default="voice",
        description="Always 'voice' — distinguishes from text ChatRequest turns"
    )
    timestamp: datetime = Field(..., description="When this turn was spoken")
    is_pii_filtered: bool = Field(
        default=False,
        description="True if PII was detected and scrubbed from content"
    )


# =============================================================================
# Session Token Models
# =============================================================================


class RealtimeSessionRequest(BaseModel):
    """Request body for POST /api/realtime/session."""

    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID. Auto-generated (UUID) if not provided."
    )
    voice: str = Field(
        default="alloy",
        description="Azure OpenAI voice name (alloy, echo, fable, onyx, nova, shimmer)"
    )
    instructions: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="System prompt override. Uses default agent instructions if omitted."
    )


class RealtimeSessionResponse(BaseModel):
    """Response from POST /api/realtime/session."""

    session_id: str = Field(
        ...,
        description="Session identifier (matches request or newly generated)"
    )
    token: str = Field(
        ...,
        description="Short-lived ephemeral credential (≤60 s TTL)"
    )
    expires_at: datetime = Field(
        ...,
        description="Token expiry — reject connections after this time"
    )
    endpoint: str = Field(
        ...,
        description="Azure OpenAI Realtime API WebRTC endpoint URL"
    )
    deployment: str = Field(
        ...,
        description="Model deployment name (e.g. gpt-realtime)"
    )


# =============================================================================
# Tool Call Models
# =============================================================================


class ToolDefinition(BaseModel):
    """A function tool exposed to the Azure OpenAI Realtime API."""

    name: str = Field(..., description="Tool function name (e.g. analyze_and_route_query)")
    description: str = Field(..., description="Natural-language description for the model")
    parameters: dict = Field(
        ...,
        description="JSON Schema object describing the function parameters"
    )
    type: Literal["function"] = Field(
        default="function",
        description="Always 'function' — Realtime API tool type"
    )


class ToolCallRequest(BaseModel):
    """
    Inbound tool call from the Realtime API (received over WS relay).
    Transient — never persisted.
    """

    call_id: str = Field(
        ...,
        description="Unique call identifier provided by the Realtime API"
    )
    tool_name: str = Field(..., description="Name of the tool to invoke")
    arguments: dict = Field(
        default_factory=dict,
        description="Parsed arguments matching the ToolDefinition parameter schema"
    )


class ToolCallResponse(BaseModel):
    """
    Outbound tool result sent back to the Realtime API (sent over WS relay).
    Transient — never persisted.
    """

    call_id: str = Field(..., description="Echoes the call_id from ToolCallRequest")
    result: str = Field(
        ...,
        description="JSON-serialized, PII-filtered pipeline output"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if tool execution failed; None on success"
    )


# =============================================================================
# Server-Side Session State
# =============================================================================


class VoiceState(BaseModel):
    """Server-side state for an active or recently-closed voice session."""

    session_id: str = Field(
        ...,
        description="Shared session identifier (same UUID as text Session)"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Hashed user identifier (SHA-256) — None if anonymous"
    )
    status: Literal["active", "disconnected", "expired"] = Field(
        ...,
        description="Lifecycle status of this voice session"
    )
    created_at: datetime = Field(..., description="When the voice session was established")
    last_activity: datetime = Field(..., description="Timestamp of most recent voice turn")
    transcript: list[VoiceMessage] = Field(
        default_factory=list,
        max_length=100,
        description="Append-only list of PII-filtered transcript entries"
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id_hash(cls, v: Optional[str]) -> Optional[str]:
        """If provided, user_id must be a 64-character SHA-256 hex string."""
        if v is not None and len(v) != 64:
            raise ValueError("user_id must be a 64-character SHA-256 hex string")
        return v
