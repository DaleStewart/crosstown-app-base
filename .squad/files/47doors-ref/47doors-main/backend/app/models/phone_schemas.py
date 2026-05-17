"""
Pydantic schemas for the 47 Doors phone call feature.
Covers ACS Call Automation webhook events, call state, and health responses.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Event Grid Models
# =============================================================================


class EventGridValidationEvent(BaseModel):
    """Event Grid subscription validation handshake payload."""

    validationCode: str = Field(
        ...,
        description="One-time code that must be echoed back to complete subscription validation"
    )
    validationUrl: Optional[str] = Field(
        default=None,
        description="Alternative URL-based validation endpoint (not used by this service)"
    )


class IncomingCallEvent(BaseModel):
    """
    Event Grid IncomingCall event payload.
    Sent by ACS to the /api/phone/incoming webhook when a PSTN call arrives.
    """

    incoming_call_context: str = Field(
        ...,
        alias="incomingCallContext",
        description="Opaque ACS context token — required to answer the call"
    )
    caller_id: str = Field(
        ...,
        alias="from",
        description="Caller's phone number in E.164 format (e.g. +15551234567)"
    )
    callee_id: str = Field(
        ...,
        alias="to",
        description="Called phone number in E.164 format"
    )
    correlation_id: str = Field(
        ...,
        alias="correlationId",
        description="ACS correlation identifier for distributed tracing"
    )

    model_config = {"populate_by_name": True}


# =============================================================================
# Call Automation Callback Models
# =============================================================================


class ResultInfo(BaseModel):
    """Detailed result info from a Call Automation operation."""

    code: Optional[int] = Field(default=None, description="HTTP-style status code")
    sub_code: Optional[int] = Field(
        default=None,
        alias="subCode",
        description="ACS sub-code for finer-grained error classification"
    )
    message: Optional[str] = Field(default=None, description="Human-readable result message")

    model_config = {"populate_by_name": True}


class CallEventRequest(BaseModel):
    """
    Single Call Automation callback event.
    ACS POSTs an array of these to /api/phone/callbacks when call state changes.
    """

    call_connection_id: str = Field(
        ...,
        description="ACS call connection identifier"
    )
    event_type: str = Field(
        ...,
        description="Call Automation event type (e.g. CallConnected, CallDisconnected)"
    )
    server_call_id: Optional[str] = Field(
        default=None,
        description="Server-side call identifier for ACS diagnostics"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Distributed tracing correlation identifier"
    )
    result_info: Optional[dict] = Field(
        default=None,
        description="Result info for completed operations (raw dict payload)"
    )


# =============================================================================
# Server-Side Call State
# =============================================================================


class CallState(BaseModel):
    """Server-side state for an active or recently-closed phone call."""

    call_connection_id: str = Field(
        ...,
        description="ACS call connection identifier — primary key for call lookup"
    )
    caller_id: str = Field(
        ...,
        description="Caller's phone number in E.164 format"
    )
    status: Literal["ringing", "connecting", "connected", "disconnected", "ended", "failed"] = Field(
        ...,
        description="Lifecycle status of this phone call"
    )
    started_at: datetime = Field(
        ...,
        description="When the call was answered"
    )
    ended_at: Optional[datetime] = Field(
        default=None,
        description="When the call ended; None if still active"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="ACS correlation identifier for distributed tracing"
    )


# =============================================================================
# Health Check
# =============================================================================


class PhoneHealthResponse(BaseModel):
    """Response from GET /api/phone/health."""

    phone_available: bool = Field(
        ...,
        description="True when the phone service is reachable and phone_enabled=True"
    )
    mock_mode: bool = Field(
        ...,
        description="True when running against the mock implementation"
    )
    phone_enabled: bool = Field(
        ...,
        description="Value of the phone_enabled kill switch in config"
    )
    latency_ms: Optional[int] = Field(
        default=None,
        description="Round-trip latency to ACS in milliseconds (None in mock mode)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if health check failed"
    )
