# Data Model: Voice Interaction (002-voice-interaction)

**Phase**: 1 — Entity definitions
**Author**: Tank (Backend Dev)
**Date**: 2026-03-13
**Feature**: Real-time voice conversation via Azure OpenAI GPT-4o Realtime API

Patterns follow the existing codebase:
- **Backend**: Pydantic v2 with `Field(...)`, `field_validator`, `Literal` types — matches `backend/app/models/schemas.py`
- **Enums**: `str, Enum` subclasses — matches `backend/app/models/enums.py`
- **Frontend**: TypeScript interfaces and `enum` — matches `frontend/src/` conventions

---

## Backend Entities — Pydantic v2

### Enumerations

```python
# backend/app/models/voice_enums.py

from enum import Enum


class VoiceSessionStatus(str, Enum):
    """Server-side lifecycle status of a voice session."""
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"


class VoiceRole(str, Enum):
    """Speaker role in a voice transcript entry."""
    USER = "user"
    ASSISTANT = "assistant"
```

---

### VoiceMessage

Voice transcript entry — one spoken turn from either the student or the agent.

```python
# backend/app/models/voice_schemas.py

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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
```

**Notes**:
- `content` stores only the PII-filtered transcript — Constitution Principle III.
- `input_modality` is a discriminator field so consumers can distinguish voice turns from text turns in a unified conversation history.
- No audio data; no audio references.

---

### RealtimeSessionRequest

Request body for `POST /api/realtime/session` — initiates token issuance.

```python
class RealtimeSessionRequest(BaseModel):
    """Request body for POST /api/realtime/session."""

    session_id: Optional[str] = Field(
        default=None,
        description="Existing session ID. Auto-generated (UUID) if not provided."
    )
    voice: str = Field(
        default="marin",
        description="Azure OpenAI voice name (alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar)"
    )
    instructions: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="System prompt override. Uses default agent instructions if omitted."
    )
```

---

### RealtimeSessionResponse

Response from `POST /api/realtime/session` — contains the ephemeral token.

```python
class RealtimeSessionResponse(BaseModel):
    """Response from POST /api/realtime/session."""

    session_id: str = Field(..., description="Session identifier (matches request or newly generated)")
    token: str = Field(..., description="Short-lived ephemeral credential (≤60 s TTL)")
    expires_at: datetime = Field(..., description="Token expiry — reject connections after this time")
    endpoint: str = Field(..., description="Azure OpenAI Realtime API WebRTC endpoint URL")
    deployment: str = Field(..., description="Model deployment name (e.g. gpt-4o-realtime-preview)")
```

**Notes**:
- `token` is a scoped, time-limited credential — the Azure OpenAI API key never leaves the backend.
- `expires_at` allows the frontend to proactively refresh before the token lapses.

---

### ToolDefinition

A tool definition advertised to the Realtime API at session start.

```python
class ToolDefinition(BaseModel):
    """A function tool exposed to the Azure OpenAI Realtime API."""

    name: str = Field(..., description="Tool function name (e.g. analyze_and_route_query)")
    description: str = Field(..., description="Natural-language description for the model")
    parameters: dict = Field(..., description="JSON Schema object describing the function parameters")
    type: Literal["function"] = Field(
        default="function",
        description="Always 'function' — Realtime API tool type"
    )
```

---

### ToolCallRequest

An incoming tool invocation from the Realtime API, received over the backend WebSocket relay.

```python
class ToolCallRequest(BaseModel):
    """
    Inbound tool call from the Realtime API (received over WS relay).
    Transient — never persisted.
    """

    call_id: str = Field(..., description="Unique call identifier provided by the Realtime API")
    tool_name: str = Field(..., description="Name of the tool to invoke")
    arguments: dict = Field(
        default_factory=dict,
        description="Parsed arguments matching the ToolDefinition parameter schema"
    )
```

---

### ToolCallResponse

The result to send back to the Realtime API over the WS relay.

```python
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
```

**Notes**:
- `result` is always PII-filtered before serialisation — Constitution Principle III, layer 2.
- Both `ToolCallRequest` and `ToolCallResponse` are WS-scoped and transient; they are never written to the session store or audit log.

---

### VoiceState (server-side session tracker)

Tracks an active voice session on the server. Stored in the session store alongside the text `Session`.

```python
class VoiceState(BaseModel):
    """Server-side state for an active or recently-closed voice session."""

    session_id: str = Field(..., description="Shared session identifier (same UUID as text Session)")
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
```

**Notes**:
- `session_id` is the join key to the existing text `Session` model — Constitution Principle IV / spec VFR-010.
- `transcript` is append-only; entries are never edited or deleted.
- `user_id` follows the same hashing contract as `student_id_hash` in `Session` (schemas.py).

---

## Frontend Types — TypeScript

### VoiceUIState (enum)

Maps to the 6-state voice state machine. Drives component rendering and ARIA live-region announcements.

```typescript
// frontend/src/types/voice.ts

export enum VoiceUIState {
  Idle       = "idle",
  Connecting = "connecting",
  Listening  = "listening",
  Processing = "processing",
  Speaking   = "speaking",
  Error      = "error",
}
```

---

### VoiceMessage (frontend display type)

Transcript entry for display in the chat thread alongside text `ChatMessage` entries.

```typescript
export interface VoiceMessage {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}
```

---

### VoiceConfig

Configuration passed to the `useVoice` hook.

```typescript
export interface VoiceConfig {
  /** URL for POST /api/realtime/session */
  sessionEndpoint: string;
  /** URL for the WS tool-relay endpoint ws://…/api/realtime/ws/{sessionId} */
  wsEndpoint: string;
  /** Azure voice name (default: "alloy") */
  voice: string;
  /** Voice Activity Detection silence threshold in milliseconds (default: 500) */
  vadThreshold: number;
}
```

---

## Entity Relationships

```
VoiceState (server)
  │  session_id ──── joins ───► Session (existing, schemas.py)
  │
  └── transcript: VoiceMessage[]   (append-only)
        └── input_modality = "voice"   (discriminates from text turns)

ToolCallRequest  ─── WS-scoped, transient ───► ToolCallResponse
  (never persisted)                              (never persisted)

RealtimeSessionRequest ──► RealtimeSessionResponse
  (one per voice session start)

Frontend VoiceUIState enum ──► drives VoicePanel component rendering
                           └──► drives ARIA live region announcements
```

---

## State Machine — Voice UI

Six states with deterministic transitions. Each state maps to a distinct UI indicator (spec VFR-014) and an ARIA live-region announcement (Constitution Principle VI).

```
idle ──────────────► connecting ──────────────► listening
                         │                         │
                         │ (WebRTC/token fail)      │ (mic fail)
                         ▼                         ▼
                       error ◄──────────────── error
                         │
                         ▼
                        idle

listening ────► processing ────► speaking ────► idle
                    │                │
                    │ (pipeline fail) │ (TTS fail)
                    ▼                ▼
                  error            error
                    │
                    ▼
                   idle
```

| State | UI Indicator | ARIA Announcement |
|---|---|---|
| `idle` | Mic button (default) | — |
| `connecting` | Spinner on mic button | "Connecting to voice agent" |
| `listening` | Pulsing waveform | "Listening — speak now" |
| `processing` | Thinking indicator | "Processing your request" |
| `speaking` | Speaking waveform | "Agent is responding" |
| `error` | Error badge on mic button | "Voice unavailable: {reason}" |

**Error recovery**: All error transitions return to `idle` after a 2-second display delay, enabling retry without a page reload.

---

## Field Naming Conventions

Follows the existing `schemas.py` conventions:
- `snake_case` for all Python field names
- `camelCase` for all TypeScript field names
- `datetime` fields use `datetime` (Python) / `Date` (TypeScript) — no plain epoch integers
- Optional fields use `Optional[T]` with `default=None` (not `T | None` union syntax) for consistency with existing models
- Validators use `@field_validator` + `@classmethod` (Pydantic v2 pattern — matches `ChatResponse.validate_ticket_id`)
