# Feature Specification: Voice Interaction for 47 Doors

**Feature Branch**: `002-voice-interaction`
**Created**: 2026-02-06
**Updated**: 2026-04-21
**Status**: ✅ Shipped — Production (2026-04-21, revision `azd-1776792457`) — Browser voice + phone bridge (+1-913-217-1946) verified on Azure Container Apps
**Constitution**: v1.1.0 (voice-specific principles in III, VI, VII)
**Input**: User description: "Add real-time voice conversation using Azure OpenAI GPT-4o Realtime API via WebRTC, enabling students to speak naturally with the support agent instead of typing"
**MVP Scope**: User Stories P1 (Core Voice) + P5 (Degradation) + Eval Pack — Azure Container Apps deployment (local dev as fallback)

## Problem Statement

The current 47 Doors support agent only accepts text input. Many students — especially those with accessibility needs, those multitasking, or those who find it easier to describe complex problems verbally — are underserved by a text-only interface. Voice interaction provides a more natural, faster, and more inclusive way to get support. The demo of a healthcare voice agent showed how dynamic, real-time voice conversations with tool-calling agents dramatically improve user experience and resolution speed.

## Vision

Add a voice channel to the existing 47 Doors support agent so students can have a natural spoken conversation with the system. The voice agent uses the same 3-agent pipeline (intent detection, routing, ticket creation, KB retrieval) as the text chat, but through the Azure OpenAI GPT-4o Realtime API with WebRTC transport (browser) or direct WebSocket (phone bridge). Students click a microphone button, speak their request, and hear the agent respond in real-time — including ticket confirmations, knowledge article summaries, and escalation notices. Alternatively, students can call +1 (913) 217-1946 to access the same voice agent via Azure Communication Services. Text chat remains fully functional alongside voice.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Voice Support Request (Priority: P1)

A student clicks the microphone button and speaks a support request. The voice agent hears them, processes their request through the existing 3-agent pipeline (via tool calls), and speaks back with a ticket confirmation, relevant KB articles, and SLA expectations.

**Why this priority**: This is the core voice experience. If only this story ships, students can already have a complete voice-driven support interaction — the same value as text chat but through speech.

**Independent Test**: Can be fully tested by clicking the mic button, saying "I forgot my password", and verifying the agent speaks back with a ticket ID and password reset guidance within 10 seconds.

**Acceptance Scenarios**:

1. **Given** a student is on the chat page, **When** they click the microphone button, **Then** the browser requests microphone permission and the UI shows a "listening" indicator (pulsing waveform).
2. **Given** the student is connected via voice, **When** they say "I forgot my password", **Then** the voice agent invokes the `analyze_and_route_query` tool, creates a ticket routed to IT, and speaks back the ticket ID and relevant KB article summaries.
3. **Given** the student speaks a facilities request like "The elevator in Smith Hall is broken", **When** processed, **Then** the voice agent creates a Facilities ticket, speaks the ticket ID, and offers relevant maintenance articles.
4. **Given** the voice agent is processing a tool call, **When** the tool executes, **Then** the student hears a brief audio cue or the agent says "Let me look that up for you" before delivering results.
5. **Given** the student is speaking and the voice agent detects they've finished (voice activity detection), **When** processing begins, **Then** the response starts within 2 seconds of the student finishing their utterance.

---

### User Story 2 - Voice Escalation and Human Handoff (Priority: P2)

A student speaks a request that requires human judgment (policy keywords, sensitive topics, or explicit human request). The voice agent recognizes this, creates an escalation ticket, and verbally confirms that a human will follow up.

**Why this priority**: Escalation is a safety-critical requirement from the constitution. Voice escalation must work identically to text escalation.

**Independent Test**: Can be tested by saying "I want to appeal my grade" via voice and verifying the agent speaks back an escalation confirmation with expected response time.

**Acceptance Scenarios**:

1. **Given** a student says "I want a refund for this semester", **When** the voice agent detects "refund" as a policy keyword, **Then** it escalates to human review and verbally informs the student a human will respond within the SLA.
2. **Given** a student says "I need to talk to a person", **When** the voice agent detects the human request phrase, **Then** it immediately confirms escalation and provides estimated wait time.
3. **Given** a student mentions sensitive topics (Title IX, mental health), **When** detected, **Then** the voice agent escalates with urgent priority and speaks a supportive acknowledgment directing them to immediate resources.

---

### User Story 3 - Hybrid Text and Voice in Same Session (Priority: P3)

A student switches between typing and speaking within the same conversation. The session context is preserved across modality switches — a student can start by typing, switch to voice, and the agent remembers the full conversation history.

**Why this priority**: Flexibility between input modes is important for real-world use (e.g., starting with text in a quiet library, then switching to voice when walking outside).

**Independent Test**: Can be tested by sending a text message first, then switching to voice and asking a follow-up question that references the text conversation.

**Acceptance Scenarios**:

1. **Given** a student sends a text message creating a ticket, **When** they switch to voice and ask "What's the status of the ticket I just created?", **Then** the voice agent retrieves the ticket from the session context and speaks the status.
2. **Given** a student is in a voice conversation, **When** they click the mic button to end voice mode and type a message, **Then** the text chat continues with the same session context.
3. **Given** a voice conversation is active, **When** the transcript of the voice exchange is displayed in the chat thread, **Then** both voice and text messages appear chronologically with clear visual distinction (voice messages show a speaker icon).

---

### User Story 4 - Voice Accessibility (Priority: P4)

A student who cannot easily type (motor impairments, visual impairments, or temporary injuries) uses voice as their primary interaction mode. The voice interface works with assistive technologies, can be activated via keyboard shortcuts, and provides clear audio feedback for all actions.

**Why this priority**: Accessibility is a constitutional requirement (Principle VI). Voice interaction is inherently more accessible for certain disabilities but must be implemented correctly.

**Independent Test**: Can be tested by activating voice mode using only keyboard navigation and verifying screen reader announcements for all state changes.

**Acceptance Scenarios**:

1. **Given** a student navigates the interface with keyboard only, **When** they focus on the microphone button and press Enter, **Then** voice mode activates with an audible indicator and screen reader announcement.
2. **Given** a student is using a screen reader, **When** the voice agent speaks a response, **Then** the transcript is also added to the screen reader's live region so it can be reviewed.
3. **Given** a student wants to stop voice mode, **When** they press Escape or click the mic button again, **Then** voice mode ends with an audible indicator and focus returns to the text input.

---

### User Story 5 - Voice Error Handling and Degradation (Priority: P5)

When the Realtime API is unavailable, the microphone fails, or network conditions are poor, the system degrades gracefully to text-only mode with clear user communication.

**Why this priority**: Graceful degradation is a constitutional requirement (Principle VII). Voice is an enhancement, not a replacement for text.

**Independent Test**: Can be tested by simulating a WebRTC connection failure and verifying the system falls back to text mode with an informative message.

**Acceptance Scenarios**:

1. **Given** the Azure OpenAI Realtime API is unavailable, **When** a student clicks the microphone button, **Then** the system displays a message "Voice mode is temporarily unavailable. Please use text chat." and the mic button shows a disabled state.
2. **Given** a voice session is active and the WebRTC connection drops, **When** the disconnection is detected, **Then** the system automatically falls back to text mode and displays "Voice connection lost. Switching to text chat. Your conversation has been preserved."
3. **Given** the browser does not support WebRTC or the student denies microphone permission, **When** they attempt to use voice, **Then** the system shows an appropriate message and the text chat remains fully functional.
4. **Given** the voice feature is disabled via configuration (`voice_enabled=false`), **When** the page loads, **Then** the microphone button is not rendered at all.

---

### Edge Cases

- What happens when a student speaks in a language other than English?
  - v1 supports English only; the Realtime API will attempt to process but may misinterpret. The system prompt instructs the model to inform the student that English is required and direct them to the multilingual support line.
- What happens when background noise makes speech unintelligible?
  - The model's built-in VAD may not trigger on noise alone. If the model cannot extract meaningful intent, it asks for clarification ("I didn't quite catch that. Could you please repeat your request?").
- What happens when a student speaks PII (SSN, credit card number)?
  - The Realtime API processes audio server-side; raw audio is NOT stored. The system prompt instructs the model to NOT repeat PII back and to flag it for secure handling. Transcripts in the chat thread are PII-filtered before display.
- How does the system handle very long voice utterances?
  - The Realtime API handles streaming audio natively. For very long monologues, the model will process incrementally. The system prompt instructs the model to summarize and ask for confirmation if the request seems to cover multiple topics.
- What happens if the student interrupts the agent while it's speaking?
  - The Realtime API with server VAD supports interruption detection. The model stops its current response and listens for the new input. This is a native feature of the WebRTC transport.
- What about concurrent voice sessions from the same student?
  - Only one voice session per browser tab is allowed. Opening a second tab defaults to text-only mode.

## Requirements *(mandatory)*

### Functional Requirements

**Voice Connection & Transport**
- **VFR-001**: System MUST provide a microphone toggle button in the chat input area that initiates a WebRTC connection to the Azure OpenAI Realtime API
- **VFR-002**: System MUST use the `gpt-4o-realtime-preview` model via WebRTC transport (browser RTCPeerConnection direct to Azure OpenAI endpoint)
- **VFR-003**: System MUST obtain an ephemeral authentication token from the backend (`POST /api/realtime/session`) before establishing the WebRTC connection, to avoid exposing the Azure OpenAI API key to the client
- **VFR-004**: System MUST support server-side voice activity detection (VAD) for natural turn-taking, with configurable silence detection threshold
- **VFR-005**: System MUST support user interruption (barge-in) — when the student speaks while the agent is responding, the agent stops and listens

**Voice Agent Behavior**
- **VFR-006**: The voice agent MUST use the same system prompt foundation as the text agent, with voice-specific additions (e.g., "Speak concisely. Do not use markdown formatting. Spell out ticket IDs character by character.")
- **VFR-007**: The voice agent MUST expose the existing 3-agent pipeline as Realtime API function tools: `analyze_and_route_query`, `check_ticket_status`, `search_knowledge_base`, `escalate_to_human`
- **VFR-008**: When a tool call is invoked, the backend WebSocket relay MUST execute the tool against the existing agent pipeline and return the result to the Realtime API session
- **VFR-009**: The voice agent MUST speak ticket IDs clearly (e.g., "T-K-T dash I-T dash two zero two six zero two zero six dash zero zero four two")
- **VFR-010**: The voice agent MUST NOT repeat PII back to the student (SSN, credit card numbers, etc.)

**Session & Context**
- **VFR-011**: Voice conversations MUST share the same session context (session_id, conversation_history) as text conversations, enabling seamless modality switching
- **VFR-012**: Voice message transcripts MUST be appended to the chat message thread with a visual indicator distinguishing them from typed messages
- **VFR-013**: Audit logs for voice interactions MUST include the same fields as text interactions, plus `input_modality: "voice"` to distinguish the channel

**User Interface**
- **VFR-014**: The microphone button MUST show clear visual states: idle (gray), listening (pulsing green animation), processing (spinner), connected (solid green), error (red), disabled (grayed out)
- **VFR-015**: During a voice session, the chat area MUST display a real-time waveform or volume indicator showing microphone input level
- **VFR-016**: Voice transcripts (both student and agent) MUST appear in the chat thread as message bubbles with a speaker/microphone icon
- **VFR-017**: The microphone button MUST be keyboard accessible (focusable, activatable via Enter, deactivatable via Escape)
- **VFR-018**: Voice state changes MUST be announced to screen readers via ARIA live regions

**Configuration & Degradation**
- **VFR-019**: Voice feature MUST be toggleable via a `voice_enabled` configuration flag (defaults to `true` when a Realtime API deployment is configured)
- **VFR-020**: When the Realtime API is unavailable or WebRTC connection fails, the system MUST fall back to text-only mode with a user-visible notification
- **VFR-021**: The backend MUST provide a voice-specific health check (`GET /api/health` should include `realtime_api` service status)
- **VFR-022**: Mock mode MUST be available for development and testing via `MOCK_MODE=true`, simulating tool calls and returning canned responses. Production and demo environments MUST use live Azure OpenAI connections (`MOCK_MODE=false`)

**Infrastructure**
- **VFR-023**: The Azure infrastructure (Bicep) MUST include a `gpt-4o-realtime-preview` model deployment in the Azure OpenAI resource
- **VFR-024**: The backend MUST expose a `POST /api/realtime/session` endpoint that creates an ephemeral session token for WebRTC authentication
- **VFR-025**: The backend MUST expose a WebSocket endpoint (`/api/realtime/ws`) for relaying tool call execution between the Realtime API session and the existing agent pipeline

**Deployment**
- **VFR-026**: The PRIMARY deployment target MUST be Azure Container Apps via `azd up`, with environment variables configured in the Container App
- **VFR-027**: Local development MUST be supported as a secondary path for debugging and development, using `uvicorn` directly
- **VFR-028**: The system MUST support both Azure-hosted and local deployment without code changes — only environment variable differences
- **VFR-029**: Health check endpoints (`/api/health`, `//api/realtime/health`) MUST work identically in both Azure and local environments

### Non-Functional Requirements

- **VNFR-001**: Voice response latency MUST be under 2 seconds from end of student utterance to start of agent speech (excluding tool execution time)
- **VNFR-002**: Tool execution during voice interactions MUST complete within 5 seconds (same as text chat pipeline)
- **VNFR-003**: Voice sessions MUST not degrade text chat performance (voice uses separate WebRTC/WebSocket connections)
- **VNFR-004**: The voice feature MUST work in modern browsers that support WebRTC (Chrome 90+, Firefox 85+, Edge 90+, Safari 15+)
- **VNFR-005**: Raw audio MUST NOT be stored or logged; only text transcripts (PII-filtered) are persisted

### Key Entities

- **RealtimeSession**: Represents an active voice session including session_id (shared with chat Session), WebRTC connection state, ephemeral token expiry, active tool calls, and voice configuration (voice name, VAD settings)
- **VoiceToolDefinition**: Represents a tool exposed to the Realtime API including name, description, JSON schema parameters, and the backend handler function that maps to the existing agent pipeline
- **VoiceMessage**: Extends the existing message model with `modality` field ("text" | "voice"), optional transcript text, and speaker icon indicator

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **VSC-001**: Students can complete a full support request (intent detection → ticket creation → KB articles) via voice within 15 seconds
- **VSC-002**: Voice escalation triggers work identically to text (100% of policy/sensitivity triggers fire correctly)
- **VSC-003**: 95% of voice interactions produce correct intent detection (validated via transcript comparison with text baseline)
- **VSC-004**: Voice-to-text and text-to-voice modality switching preserves session context 100% of the time
- **VSC-005**: Graceful degradation activates within 3 seconds of connection failure, preserving conversation history
- **VSC-006**: Voice interaction does not increase text chat latency by more than 50ms p95

## Assumptions

- Azure OpenAI `gpt-4o-realtime-preview` model is available for deployment in the same region as the existing `gpt-4o` deployment
- Azure Container Apps is the primary deployment target; the backend is deployed via `azd up` with environment variables set in the Container App configuration
- WebRTC is supported in all target browsers without polyfills
- The existing 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) can be invoked synchronously within a WebSocket tool call handler
- Students have access to a microphone (built-in or external) on their device
- The Realtime API supports function/tool calling with custom tools
- Ephemeral token authentication is supported for WebRTC connections to Azure OpenAI

## Azure OpenAI Realtime API: GA vs Preview Format (Lessons Learned)

The GA endpoint has significant differences from preview documentation. These discoveries were made during production deployment and are critical for future maintenance.

### Endpoint Format (GA)
- **Ephemeral token**: `POST {endpoint}/openai/v1/realtime/client_secrets` — no `api-version` param, no deployment in URL path
- **Model/deployment**: Specified in request body as `"model": "{deployment_name}"`, not in URL
- **WebRTC SDP exchange**: `POST {endpoint}/openai/v1/realtime/calls`

### Session Config Format (GA uses nested structure)
- **Preview (flat)**: `"input_audio_transcription": {"model": "whisper-1"}`, `"voice": "marin"`
- **GA (nested)**: `"audio": {"input": {"transcription": {"model": "whisper-1"}}, "output": {"voice": "marin"}}`
- Preview flat fields in `/client_secrets` body cause **HTTP 500** — they are silently ignored in `session.update`
- `audio.output.transcription` in `/client_secrets` also causes **HTTP 500** — backend has a fallback retry that strips this field

### Event Names (GA differs from preview)
| Event | Preview Name | GA Name |
|-------|-------------|---------|
| Agent transcript done | `response.audio_transcript.done` | `response.output_audio_transcript.done` |
| Agent transcript delta | `response.audio_transcript.delta` | `response.output_audio_transcript.delta` |
| User transcript | `conversation.item.input_audio_transcription.completed` | Same in both |
| Fallback transcript | N/A | `response.output_item.done` (contains transcript in `item.content[].transcript`) |

### Default Voice
- Default voice is **`marin`** (OpenAI recommended). Available voices: alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar.

### Authentication
- Key-based auth is **disabled** by Azure policy (`disableLocalAuth: true`)
- Must use managed identity with `Cognitive Services OpenAI User` role
- Token scope: `https://cognitiveservices.azure.com/.default`

## Dependencies

- Azure OpenAI `gpt-4o-realtime-preview` model deployment — **required for production voice**
- Azure Container Apps — **primary deployment target** (via `azd up` and Bicep in `infra/`)
- Browser WebRTC API (`RTCPeerConnection`) — **native, no library needed**
- Backend WebSocket support — **FastAPI native (Starlette WebSocket)**
- Existing 3-agent pipeline — **already implemented, will be wrapped as tools**

## Implemented & Production-Verified

- **Phone/Telephony Channel** (2026-04-21): Azure Communication Services (ACS) media streaming bridge to Azure OpenAI Realtime API supports phone calls to +1 (913) 217-1946. Production-verified with full caller speech transcription. See `.squad/skills/azure-realtime-api-schema/SKILL.md` for endpoint schema asymmetry details.

## Out of Scope (v1)

- Visual avatar or lip-sync animation
- Voice biometric authentication
- Multi-language voice support (English only)
- Voice-to-voice translation
- Custom voice cloning or fine-tuned voice models
- Recording and playback of voice conversations
- Voice analytics (emotion detection from audio tone)
- Simultaneous multi-party voice (student + human agent + AI)
