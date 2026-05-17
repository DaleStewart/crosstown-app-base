# Tasks: Voice Interaction for 47 Doors

**Feature**: 002-voice-interaction
**Branch**: `002-voice-interaction`
**Input**: Design documents from `specs/002-voice-interaction/`
**Prerequisites**: plan.md ✅ spec.md ✅ data-model.md ✅ contracts/voice-api.yaml ✅ research.md ✅
**Constitution**: v1.1.0 — Principle V (Test-First) applies: tests are written **before** implementation in every phase.
**Last Updated**: 2026-04-21
**Shipped**: Production (2026-04-21, revision `azd-1776792457`)

### Implementation Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Setup | ✅ Complete | Config, .env, Bicep, test skeletons |
| Phase 2: Foundational | ✅ Complete | Models, types, services, DI wiring |
| Phase 3: US1 Core Voice | ✅ Complete | Endpoints, WebRTC hook, UI components — **LIVE ON AZURE** |
| Phase 4: US2 Escalation | ⏸️ Deferred | Existing pipeline escalation covers this; voice-specific logic not needed for production demo |
| Phase 5: US3 Hybrid | ⏸️ Deferred | Session sharing works; dedicated hybrid UI not required for MVP |
| Phase 6: US4 Accessibility | ⏸️ Deferred | Basic keyboard support shipped; full WCAG audit post-MVP |
| Phase 7: US5 Degradation + Evals | ✅ Complete | Health endpoint, degradation, eval pack, runbook |
| Phase 8: Polish | ⏸️ Deferred | Core security verified; full hardening review post-production |

### Deployment Notes (discovered during implementation)
- **Auth**: Managed identity via `ManagedIdentityCredential` — API key auth disabled by Azure policy (`disableLocalAuth: true`)
- **Ephemeral tokens**: `/openai/v1/realtime/client_secrets` returns `{"value": "eph_...", "expires_at": "...", "session": {...}}`
- **WebRTC URL**: Frontend connects to `{endpoint}/openai/v1/realtime/calls` with Bearer ephemeral token
- **Docker**: `.dockerignore` prevents `.env` from leaking into container images (critical for MI auth)
- **Dependencies**: `aiohttp>=3.9.0` required in both `requirements.txt` and `pyproject.toml`

## Format: `- [ ] T### [P?] [US?] Description with exact file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[US#]**: User story label — required for Phase 3 and later tasks
- Setup and Foundational phases carry no story label
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure) ✅

**Purpose**: Voice-specific environment configuration, .env wiring, and Bicep infrastructure — unblocks all later work.

- [x] T001 Add voice config fields to `backend/app/core/config.py`: `voice_enabled: bool = True`, `azure_openai_realtime_deployment: str = ""`, `azure_openai_realtime_api_version: str = "2025-04-01-preview"`, `realtime_voice: str = "alloy"`, `realtime_vad_threshold_ms: int = 500`; expose as `Settings` fields with validator that auto-sets `voice_enabled=False` when `azure_openai_realtime_deployment` is empty and `mock_mode=False`
- [x] T002 [P] Add voice environment variable stubs to `.env.example`: `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview`, `AZURE_OPENAI_REALTIME_API_VERSION=2025-04-01-preview`, `VOICE_ENABLED=true`, `REALTIME_VOICE=alloy`, `REALTIME_VAD_THRESHOLD_MS=500` with comments explaining each var
- [x] T003 [P] Add `gpt-4o-realtime-preview` model deployment to `infra/main.bicep` inside the existing Azure OpenAI resource block: model `gpt-4o-realtime-preview`, version `2025-04-01`, sku `Standard`, capacity `1`; output the deployment name so it can be referenced in app settings
- [x] T004 [P] Create `backend/tests/test_voice/__init__.py` (empty) to register the test package; also create stub files `test_config.py`, `test_models.py`, `test_mock_service.py`, `test_endpoints.py`, `test_pii_filter.py` each containing a single `pass` placeholder so pytest collection succeeds immediately
- [x] T005 [P] Create `frontend/tests/voice/` directory with placeholder files `useVoice.test.ts`, `VoiceMicButton.test.tsx`, `voice-e2e.spec.ts` each exporting a single `describe` block with a `todo` test so Vitest/Playwright collection succeeds immediately

**Checkpoint**: Config, .env stubs, Bicep, and test skeletons are all in place. `cd backend && python -m pytest backend/tests/test_voice/ -x` should pass (all stubs).

---

## Phase 2: Foundational (Blocking Prerequisites) ✅

**Purpose**: Pydantic models, TypeScript types, service interface, mock service, Azure service, and DI wiring — **must complete before any user story work begins**.

⚠️ **CRITICAL**: No user story phase can start until this phase is complete and passing.

### Tests First (Constitution Principle V)

- [x] T006 [P] Write `backend/tests/test_voice/test_config.py`: tests that (1) `voice_enabled` defaults to `True` when `mock_mode=True`, (2) `voice_enabled` auto-sets to `False` when deployment is empty and `mock_mode=False`, (3) `realtime_vad_threshold_ms` accepts valid integer; all tests must **fail** before T001 is implemented
- [x] T007 [P] Write `backend/tests/test_voice/test_models.py`: tests for all Pydantic v2 models — `VoiceMessage` (content length bounds, PII flag default), `RealtimeSessionRequest` (optional session_id, default voice), `RealtimeSessionResponse` (required fields), `ToolDefinition` (type literal), `ToolCallRequest`, `ToolCallResponse` (error default None), `VoiceState` (user_id SHA-256 validator, transcript max 100); all tests must **fail** before T009 is implemented

### Implementation

- [x] T008 [P] Create `backend/app/models/voice_enums.py` with `VoiceSessionStatus(str, Enum)` values `ACTIVE`, `DISCONNECTED`, `EXPIRED`; and `VoiceRole(str, Enum)` values `USER`, `ASSISTANT`; follow existing `backend/app/models/enums.py` pattern
- [x] T009 [P] Create `backend/app/models/voice_schemas.py` with Pydantic v2 models exactly matching `specs/002-voice-interaction/data-model.md`: `VoiceMessage`, `RealtimeSessionRequest`, `RealtimeSessionResponse`, `ToolDefinition`, `ToolCallRequest`, `ToolCallResponse`, `VoiceState`; import enums from `voice_enums.py`; use `Field(...)`, `field_validator`, `Literal` per existing `backend/app/models/schemas.py` conventions
- [x] T010 [P] Create `frontend/src/types/voice.ts` with TypeScript types matching `specs/002-voice-interaction/data-model.md`: `VoiceUIState` enum (Idle, Connecting, Listening, Processing, Speaking, Error), `VoiceMessage` interface (id, content, role, timestamp), `VoiceConfig` interface (sessionEndpoint, wsEndpoint, voice, vadThreshold); use `camelCase` for all field names
- [x] T011 Add `RealtimeServiceInterface` (abstract base class) to `backend/app/services/interfaces.py` with three abstract async methods: `create_session(session_id, voice, instructions) -> RealtimeSessionResponse`, `get_tool_definitions() -> list[ToolDefinition]`, `execute_tool(call_id, tool_name, arguments, session_id) -> ToolCallResponse`; import models from `voice_schemas.py`
- [x] T012 [P] Write `backend/tests/test_voice/test_mock_service.py`: tests that `MockRealtimeService.create_session()` returns a `RealtimeSessionResponse` with non-empty token and `expires_at` in the future; `get_tool_definitions()` returns exactly 4 tools with names matching the 4 pipeline tools; `execute_tool("analyze_and_route_query", {"query": "test"}, session_id)` returns a `ToolCallResponse` with no error field; all tests must **fail** before T013 is implemented
- [x] T013 Implement `MockRealtimeService` in `backend/app/services/mock/realtime.py`: `create_session()` returns a fake ephemeral token (`eph_mock_<uuid4>`), endpoint `http://localhost:8000/mock`, deployment `gpt-4o-realtime-preview`, expires 60 s from now; `get_tool_definitions()` returns the 4 tool definitions (analyze_and_route_query, check_ticket_status, search_knowledge_base, escalate_to_human) with full JSON Schema parameters; `execute_tool()` delegates to the existing agent pipeline via DI injected `AgentService`; implement `RealtimeServiceInterface`
- [x] T014 Implement `AzureRealtimeService` in `backend/app/services/azure/realtime.py`: uses managed identity (`ManagedIdentityCredential`) to call `POST https://{endpoint}/openai/v1/realtime/client_secrets` with Bearer token; parses response `{"value": ..., "expires_at": ..., "session": ...}` to `RealtimeSessionResponse`; returns 503-raising `VoiceUnavailableError` on HTTP failure; `get_tool_definitions()` same as mock; `execute_tool()` delegates to existing agent pipeline; implement `RealtimeServiceInterface`
- [x] T015 Wire `RealtimeServiceInterface` DI in `backend/app/dependencies.py`: add `get_realtime_service() -> RealtimeServiceInterface` factory — returns `MockRealtimeService` when `settings.use_mock_services` is `True`, `AzureRealtimeService` when `False`; follow existing `get_llm_service()` / `get_ticket_service()` pattern in the same file

**Checkpoint**: `cd backend && python -m pytest backend/tests/test_voice/test_config.py backend/tests/test_voice/test_models.py backend/tests/test_voice/test_mock_service.py -x` must pass. User story work can now begin in parallel.

---

## Phase 3: US1 — Voice Support Request (Priority: P1) 🎯 MVP Core ✅

**Goal**: Student clicks mic → speaks request → voice agent invokes 3-agent pipeline tools → speaks back ticket ID + KB articles.

**Independent Test**: Click mic, say "I forgot my password", verify agent speaks ticket ID and KB guidance within 10 s.

**Maps to**: VFR-001 through VFR-009, VFR-024, VFR-025

### Tests First — Backend (Constitution Principle V)

- [x] T016 [P] [US1] Write `backend/tests/test_voice/test_endpoints.py::test_create_session_mock_mode` — POST `/api/realtime/session` with `{"voice": "alloy"}` returns HTTP 200, body matches `RealtimeSessionResponse` schema (session_id UUID, non-empty token, future expires_at, endpoint, deployment); test must **fail** before T023 is implemented
- [x] T017 [P] [US1] Write `backend/tests/test_voice/test_endpoints.py::test_create_session_with_existing_session_id` — POST `/api/realtime/session` with `{"session_id": "<existing_uuid>", "voice": "shimmer"}` returns the same `session_id` in the response; test must **fail** before T023 is implemented
- [x] T018 [P] [US1] Write `backend/tests/test_voice/test_endpoints.py::test_websocket_tool_call_relay` — connect WebSocket to `/api/realtime/ws?session_id=<uuid>&token=<mock_token>`, send a `tool_call_request` message for `analyze_and_route_query` with `{"query": "password reset"}`, assert response is a `tool_call_response` JSON with matching `call_id` and non-empty `result`; test must **fail** before T025 is implemented
- [x] T019 [P] [US1] Write `backend/tests/test_voice/test_endpoints.py::test_websocket_invalid_token_closes_4001` — connect WebSocket with a bad token, assert the connection is closed with code 4001; test must **fail** before T025 is implemented
- [x] T020 [P] [US1] Write `backend/tests/test_voice/test_pii_filter.py::test_pii_not_echoed_in_tool_result` — call `execute_tool("analyze_and_route_query", {"query": "my SSN is 123-45-6789"}, session_id)`, assert `result` field does not contain `123-45-6789`; test must **fail** before T013 PII filtering is wired

### Tests First — Frontend (Constitution Principle V)

- [x] T021 [P] [US1] Write `frontend/tests/voice/useVoice.test.ts`: (1) initial state is `VoiceUIState.Idle`, (2) `startVoice()` transitions through `Connecting` then `Listening`, (3) `stopVoice()` returns to `Idle`, (4) `isVoiceSupported` is `true` in jsdom when RTCPeerConnection is mocked; mock `createRealtimeSession` API call; tests must **fail** before T027 is implemented
- [x] T022 [P] [US1] Write `frontend/tests/voice/VoiceMicButton.test.tsx`: (1) renders mic icon in idle state, (2) Enter key triggers `onToggle`, (3) Escape key triggers `onToggle` when active, (4) `aria-label` updates to "End voice conversation" when state is Listening, (5) disabled prop prevents toggle; tests must **fail** before T028 is implemented

### Implementation — Backend

- [x] T023 [US1] Create `backend/app/api/realtime.py`: implement `POST /api/realtime/session` endpoint — validate request body as `RealtimeSessionRequest`, generate `session_id` UUID if not provided, call `realtime_service.create_session(session_id, voice, instructions)`, return `RealtimeSessionResponse`; raise `HTTPException(503)` with `ErrorResponse` body when `VoiceUnavailableError` is caught; match schema from `specs/002-voice-interaction/contracts/voice-api.yaml`
- [x] T024 [US1] Implement WebSocket endpoint `GET /api/realtime/ws` in `backend/app/api/realtime.py`: validate `session_id` and `token` query params on connect (close 4001 on token mismatch, 4002 on session not found); receive JSON frames, deserialize as `ToolCallRequest`, call `realtime_service.execute_tool()`, serialize `ToolCallResponse` and send back; send `SessionUpdateMessage` frames on connect/disconnect; handle `WebSocketDisconnect` gracefully
- [x] T025 [US1] Implement 4 tool definitions in `backend/app/services/azure/realtime.py` `get_tool_definitions()`: `analyze_and_route_query` (query: string — analyze student query, detect intent, create ticket, return ticket_id + KB articles), `check_ticket_status` (ticket_id: string), `search_knowledge_base` (query: string, top_k: int default 3), `escalate_to_human` (reason: string, priority: string enum low/medium/high/urgent); each with full JSON Schema `parameters` dict
- [x] T026 [US1] Add voice system prompt to `backend/app/services/azure/realtime.py`: base prompt inherits 47 Doors agent instructions; voice additions: "Speak concisely. Do not use markdown formatting. Spell out ticket IDs character by character (e.g., T-K-T dash I-T dash two zero two six...). Do not repeat any personal identifying information the student provides. If you cannot understand the request, ask for clarification."; store as `VOICE_SYSTEM_PROMPT` constant
- [x] T027 [US1] Mount realtime router in `backend/app/main.py`: `from backend.app.api.realtime import router as realtime_router; app.include_router(realtime_router, prefix="/api/realtime", tags=["Realtime"])`; place after existing chat router include

### Implementation — Frontend

- [x] T028 [P] [US1] Create `frontend/src/hooks/useVoice.ts`: state machine using `useReducer` with `VoiceUIState`; `startVoice()` calls `createRealtimeSession()`, then creates `RTCPeerConnection` to returned endpoint with ephemeral token as Bearer auth, adds local mic audio track, creates data channel `"oai-tools"` for tool call events; sets state Connecting → Listening on ICE connected; `stopVoice()` closes peer connection, sets state → Idle; `handleDataChannelMessage()` parses tool_call_request events and relays to backend WS then sends result back via data channel; expose `{ voiceState, startVoice, stopVoice, transcript, isVoiceSupported }`; `isVoiceSupported = typeof RTCPeerConnection !== "undefined"`
- [x] T029 [P] [US1] Create `frontend/src/components/VoiceMicButton.tsx`: button renders HeroIcons `MicrophoneIcon`; maps `VoiceUIState` to Tailwind classes — idle: `text-gray-400 hover:text-gray-600`, connecting: `text-yellow-400 animate-pulse`, listening: `text-green-500 animate-pulse`, processing: render `ArrowPathIcon` spinning, speaking: `text-green-600`, error: `text-red-500`; `aria-label` = dynamic per state; `aria-pressed` = true when active; `onKeyDown` handles Enter (toggle) and Escape (stop); props: `voiceState: VoiceUIState`, `onToggle: () => void`, `disabled?: boolean`
- [x] T030 [P] [US1] Create `frontend/src/components/VoiceTranscript.tsx`: renders a list of `VoiceMessage` entries as chat bubbles; user messages right-aligned with `MicrophoneIcon` badge, assistant messages left-aligned with `SpeakerWaveIcon` badge; each bubble shows `content` and formatted `timestamp`; uses `role: "user" | "assistant"` to pick alignment/color; export `VoiceTranscript: React.FC<{ messages: VoiceMessage[] }>`
- [x] T031 [P] [US1] Create `frontend/src/components/VoiceStatusIndicator.tsx`: displays a status bar visible only when `voiceState !== VoiceUIState.Idle`; shows human-readable state label ("Connecting…", "Listening — speak now", "Processing your request…", "Agent is responding…", "Voice unavailable"); renders a simple CSS pulse animation for Listening and Speaking states; accepts `voiceState: VoiceUIState` prop
- [x] T032 [US1] Integrate voice components into `frontend/src/containers/ChatContainer.tsx`: import `useVoice`, `VoiceMicButton`, `VoiceTranscript`, `VoiceStatusIndicator`; render `VoiceStatusIndicator` above the message list when voice is active; render `VoiceMicButton` in the chat input area alongside the Send button; append `VoiceTranscript` messages to the unified message list as they arrive from `useVoice.transcript`; pass `sessionId` from existing `useChat` hook to `useVoice` config
- [x] T033 [P] [US1] Add `createRealtimeSession(request: Partial<RealtimeSessionRequest>): Promise<RealtimeSessionResponse>` to `frontend/src/api/client.ts` (or equivalent API client file): POST to `/api/realtime/session`, parse response as `RealtimeSessionResponse`, throw `VoiceUnavailableError` on 503

**Checkpoint**: `cd backend && python -m pytest backend/tests/test_voice/test_endpoints.py -x` passes. Click mic button in browser (mock mode) → voice state transitions → transcript appears in chat.

---

## Phase 4: US2 — Voice Escalation and Human Handoff (Priority: P2)

**Goal**: Voice agent escalates policy/sensitive/human-request queries identically to text escalation.

**Independent Test**: Say "I want to appeal my grade" via voice → agent speaks escalation confirmation with SLA.

**Maps to**: VFR-007 (`escalate_to_human` tool), US2 acceptance scenarios

### Tests First (Constitution Principle V)

- [ ] T034 [P] [US2] Write `backend/tests/test_voice/test_endpoints.py::test_escalate_to_human_tool_via_voice` — call `execute_tool("escalate_to_human", {"reason": "student wants grade appeal", "priority": "medium"}, session_id)`, assert `ToolCallResponse.result` contains an escalation ticket ID and `error` is None; test must **fail** before T037 is wired
- [ ] T035 [P] [US2] Write `backend/tests/test_voice/test_endpoints.py::test_policy_keyword_triggers_escalation` — call `execute_tool("analyze_and_route_query", {"query": "I want a refund for this semester"}, session_id)`, assert result includes `escalated: true` or `department: "human_escalation"`; test must **fail** until existing pipeline escalation logic is verified wired to voice tools
- [ ] T036 [P] [US2] Write `backend/tests/test_voice/test_endpoints.py::test_sensitive_topic_urgent_escalation` — call `execute_tool("analyze_and_route_query", {"query": "I need to report a Title IX incident"}, session_id)`, assert result includes `priority: "urgent"` and escalation; test must **fail** until pipeline logic is verified
- [ ] T037 [P] [US2] Write `backend/tests/test_voice/test_endpoints.py::test_escalation_audit_log_includes_voice_modality` — after a voice tool call that triggers escalation, assert the audit log entry contains `input_modality: "voice"`; test must **fail** before T039 is implemented

### Implementation

- [ ] T038 [US2] Update `escalate_to_human` tool definition in `backend/app/services/azure/realtime.py` `get_tool_definitions()`: set description to "Transfer the student to a human support agent. Use this when the student explicitly asks for a human, mentions policy-related topics (appeals, waivers, refunds, financial aid), or discusses sensitive topics (Title IX, mental health, discrimination, threats, safety). Provide the reason and set priority to 'urgent' for Title IX and mental health topics."
- [ ] T039 [US2] Add `input_modality: "voice"` field to audit log writes in `backend/app/api/realtime.py` `execute_tool()` handler: when a tool call is executed in a voice session, pass `input_modality="voice"` to the audit log entry; follow the same audit log pattern used in `backend/app/api/chat.py`
- [ ] T040 [P] [US2] Add voice escalation state display to `frontend/src/components/VoiceStatusIndicator.tsx`: when a `tool_call_request` for `escalate_to_human` is detected in the data channel, show a status message "Connecting you to a support agent…" until the tool result is received

**Checkpoint**: `cd backend && python -m pytest backend/tests/test_voice/test_endpoints.py::test_escalate_to_human_tool_via_voice backend/tests/test_voice/test_endpoints.py::test_policy_keyword_triggers_escalation -x` passes.

---

## Phase 5: US3 — Hybrid Text and Voice in Same Session (Priority: P3)

**Goal**: Students switch between typing and speaking; session context is preserved across modality switches.

**Independent Test**: Send a text message creating a ticket, switch to voice, ask "what's the status?" — agent answers with correct ticket.

**Maps to**: VFR-011, VFR-012, VFR-013

### Tests First (Constitution Principle V)

- [ ] T041 [P] [US3] Write `backend/tests/test_voice/test_endpoints.py::test_voice_shares_session_id_with_text` — create a text session via POST `/api/chat` with a ticket, then POST `/api/realtime/session` with the same `session_id`, then call `execute_tool("check_ticket_status", {"ticket_id": "<id>"}, session_id)` — assert result includes the ticket created in the text session; test must **fail** before T043 is implemented
- [ ] T042 [P] [US3] Write `backend/tests/test_voice/test_endpoints.py::test_voice_transcript_appended_with_input_modality` — after a voice tool call, retrieve the session's conversation history and assert a `VoiceMessage` entry with `input_modality: "voice"` exists alongside existing text messages; test must **fail** before T044 is implemented

### Implementation

- [ ] T043 [US3] Ensure `backend/app/api/realtime.py` `POST /session` handler: when an existing `session_id` is provided, look up the session in the session store (same store used by text chat); if not found, create a new session with that ID; all subsequent tool calls in the voice session read/write to this shared session context
- [ ] T044 [US3] Append `VoiceMessage` transcript entries to the shared session's `conversation_history` in `backend/app/api/realtime.py` WebSocket handler: after each successful tool call, create a `VoiceMessage(id=uuid4(), session_id=session_id, content=filtered_transcript, role=role, input_modality="voice", timestamp=now())` and append to session store; reuse existing session store `append_message()` pattern
- [ ] T045 [US3] Update `frontend/src/containers/ChatContainer.tsx`: pass the existing `sessionId` from `useChat` hook to `useVoice` config object so both hooks share the same session; when `useVoice.transcript` emits new voice messages, interleave them chronologically in the unified message list
- [ ] T046 [P] [US3] Update `frontend/src/components/VoiceTranscript.tsx`: add a `SpeakerWaveIcon` (HeroIcons) badge to assistant voice message bubbles and a `MicrophoneIcon` badge to user voice message bubbles; ensure voice messages visually distinguish from text messages in the unified chat thread (e.g., light blue background vs. white)

**Checkpoint**: A full hybrid session works: text message → voice follow-up referencing text context → voice transcript appears alongside text messages with speaker icons.

---

## Phase 6: US4 — Voice Accessibility (Priority: P4)

**Goal**: Voice interface works with keyboard-only navigation, screen readers, and assistive technologies.

**Independent Test**: Activate voice using only Tab/Enter keyboard navigation; verify screen reader announces all state changes.

**Maps to**: VFR-017, VFR-018, US4 acceptance scenarios

### Tests First (Constitution Principle V)

- [ ] T047 [P] [US4] Write `frontend/tests/voice/VoiceMicButton.test.tsx::test_keyboard_activation` — render `VoiceMicButton`, simulate Tab focus then Enter keydown, assert `onToggle` is called; simulate Escape keydown when active, assert `onToggle` is called again; test must **fail** if T049 keyboard handlers are missing
- [ ] T048 [P] [US4] Write `frontend/tests/voice/VoiceMicButton.test.tsx::test_aria_attributes` — assert `aria-pressed="false"` in Idle state; assert `aria-pressed="true"` in Listening state; assert `aria-label` changes from "Start voice conversation" to "End voice conversation" between states; assert `role="button"` is present; test must **fail** before T049 ARIA implementation

### Implementation

- [ ] T049 [US4] Harden keyboard and ARIA support in `frontend/src/components/VoiceMicButton.tsx`: add `tabIndex={0}`, `role="button"`, `aria-pressed={isActive}`, `aria-label={stateLabel}`; add `onKeyDown` handler — Enter calls `onToggle()`, Escape calls `onToggle()` only if currently active; ensure button is native `<button>` element (not `<div>`) for implicit keyboard support
- [ ] T050 [P] [US4] Add `aria-live="polite"` region to `frontend/src/components/VoiceStatusIndicator.tsx`: a visually hidden `<span aria-live="polite" aria-atomic="true">` that announces: "Connecting to voice agent" (Connecting), "Listening — speak now" (Listening), "Processing your request" (Processing), "Agent is responding" (Speaking), "Voice mode ended" (back to Idle), "Voice unavailable: {reason}" (Error); update the span text on every state change
- [ ] T051 [US4] Ensure voice transcript messages in `frontend/src/components/VoiceTranscript.tsx` are appended to the same ARIA live region used by the existing chat message list in `ChatContainer.tsx`; confirm the live region uses `aria-live="polite"` and `aria-relevant="additions"` so screen readers announce new voice messages
- [ ] T052 [P] [US4] Add focus management to `frontend/src/containers/ChatContainer.tsx`: when voice mode ends (state transitions to Idle or Error), call `chatInputRef.current?.focus()` to return focus to the text input so keyboard users do not lose their place

**Checkpoint**: Navigate interface with keyboard only — Tab to mic button, Enter to activate, Escape to stop; screen reader announces all transitions.

---

## Phase 7: US5 — Error Handling & Degradation + Eval Pack (Priority: P5) ✅

**Goal**: Graceful degradation to text-only mode on any failure; full eval pack for demo readiness.

**Independent Test**: Simulate WebRTC failure → system falls back to text mode within 3 s with context preserved.

**Maps to**: VFR-019, VFR-020, VFR-021, VFR-022

### Tests First (Constitution Principle V)

- [x] T053 [P] [US5] Write `backend/tests/test_voice/test_endpoints.py::test_health_endpoint_mock_mode` — GET `/api/realtime/health` returns HTTP 200 with `{"status": "ok", "realtime_available": true, "mock_mode": true}`; test must **fail** before T057 is implemented
- [x] T054 [P] [US5] Write `backend/tests/test_voice/test_endpoints.py::test_session_returns_503_when_voice_disabled` — set `voice_enabled=False` in test settings override, POST `/api/realtime/session`, assert HTTP 503 with `ErrorResponse` body `{"error": "service_unavailable", "message": "...Use text chat instead."}` ; test must **fail** before T058 is implemented
- [x] T055 [P] [US5] Write `backend/tests/test_voice/test_endpoints.py::test_websocket_session_not_found_closes_4002` — connect WebSocket with a valid token format but a `session_id` that does not exist in the session store, assert connection closes with code 4002; test must **fail** before T024 close-code handling is complete
- [x] T056 [P] [US5] Write `frontend/tests/voice/useVoice.test.ts::test_webrtc_failure_transitions_to_error` — mock `RTCPeerConnection` to fire an `iceconnectionstatechange` event with state `"failed"`, assert `voiceState` transitions to `VoiceUIState.Error` and `errorMessage` is non-empty; test must **fail** before T059 is implemented

### Implementation

- [x] T057 [US5] Implement `GET /api/realtime/health` endpoint in `backend/app/api/realtime.py`: return `VoiceHealthResponse(status="ok", realtime_available=settings.voice_enabled, mock_mode=settings.use_mock_services)`; when `use_mock_services=False`, optionally perform a lightweight probe of the Azure OpenAI realtime endpoint and set `realtime_available=False` on HTTP error; always return HTTP 200 (use `realtime_available` field for capability detection)
- [x] T058 [US5] Enforce `voice_enabled=False` in `POST /api/realtime/session` in `backend/app/api/realtime.py`: add guard at start of handler — if `not settings.voice_enabled`, immediately return `JSONResponse(status_code=503, content=ErrorResponse(error="service_unavailable", message="Voice mode is temporarily unavailable. Please use text chat.").dict())`
- [x] T059 [US5] Add WebRTC failure → error state in `frontend/src/hooks/useVoice.ts`: listen for `RTCPeerConnection.oniceconnectionstatechange`; when state becomes `"failed"` or `"disconnected"`, dispatch `{ type: "ERROR", message: "Voice connection lost. Switching to text chat. Your conversation has been preserved." }`; transition to `VoiceUIState.Error` then after 2 s auto-transition to `Idle`; close peer connection and release microphone track
- [x] T060 [P] [US5] Add microphone permission denial handling in `frontend/src/hooks/useVoice.ts`: wrap `navigator.mediaDevices.getUserMedia()` in try/catch; on `NotAllowedError` dispatch `{ type: "ERROR", message: "Microphone access is required for voice mode. Please allow microphone access in your browser settings." }`; on `NotFoundError` dispatch error "No microphone detected"
- [x] T061 [P] [US5] Add browser WebRTC feature detection to `frontend/src/hooks/useVoice.ts`: set `isVoiceSupported = typeof RTCPeerConnection !== "undefined" && typeof navigator.mediaDevices?.getUserMedia === "function"`; expose from hook; callers use this to hide `VoiceMicButton` entirely when unsupported
- [x] T062 [US5] Add startup health check to `frontend/src/containers/ChatContainer.tsx`: on mount, call `GET /api/realtime/health`; if `realtime_available === false`, set `voiceEnabled=false` state to suppress `VoiceMicButton` rendering; if `realtime_available === true`, render `VoiceMicButton`; handle fetch error gracefully (default `voiceEnabled=false` on error)
- [x] T063 [US5] Update `MockRealtimeService` in `backend/app/services/mock/realtime.py` to support scripted voice simulation: add `simulate_tool_sequence()` that returns a canned sequence of `ToolCallRequest` events with mock results; log `"[VOICE SIMULATION]"` to console when executing tool calls in mock mode; when `voice_enabled=False`, raise `VoiceUnavailableError` from `create_session()`

### Eval Pack

- [x] T064 [P] [US5] Create `specs/002-voice-interaction/evals/manual-smoke-test.md`: step-by-step manual test script covering (1) mock mode voice: mic → "password reset" → ticket spoken, (2) voice escalation: "I need to appeal my grade" → escalation confirmed, (3) hybrid: text message → voice follow-up with same context, (4) keyboard-only accessibility flow, (5) degradation: disable voice config → mic button hidden; each scenario includes expected result and pass/fail criterion
- [x] T065 [P] [US5] Create `backend/tests/test_voice/eval_harness.py`: an automated eval script that runs 5 scripted voice queries via mock tool calls and measures (1) correct intent detection, (2) correct tool invocation, (3) PII not echoed in results, (4) audit log `input_modality` field present; prints a summary table with pass/fail counts; runnable with `python -m pytest backend/tests/test_voice/eval_harness.py -v`
- [x] T066 [P] [US5] Create `specs/002-voice-interaction/evals/logging-checklist.md`: checklist for verifying all required audit fields are present in voice interactions — `input_modality: "voice"`, `session_id`, `tool_name`, `pii_detected` flag, `timestamp`; include sample log output and instructions for running `python -m pytest backend/tests/test_voice/test_pii_filter.py -v` to validate PII filtering
- [x] T067 [US5] Create `DEMO_RUNBOOK.md` (moved to repo root): step-by-step demo guide covering: (1) prerequisites (`VOICE_ENABLED=true`, `USE_MOCK_SERVICES=true`), (2) startup commands (`docker-compose up` or `uvicorn` + `npm run dev`), (3) demo scenario A — full voice support request in mock mode, (4) demo scenario B — voice escalation, (5) demo scenario C — hybrid text+voice, (6) showing health endpoint response, (7) troubleshooting common issues (WebRTC not available, mic denied)
- [x] T068 [P] [US5] Create `specs/002-voice-interaction/FEATURE_SUMMARY.md`: 2-page stakeholder summary covering: feature overview, architecture diagram (WebRTC direct + WS relay), 5 user stories and their acceptance criteria, MVP scope (P1 + P5 + Eval Pack), NFRs met (latency, no raw audio storage, degradation), demo instructions shortlink, constitution principles satisfied

✂️ **MVP CUTLINE — Everything above this line is required for MVP. Phases below are post-MVP.**

---

## Phase 8: Polish & Cross-Cutting Concerns (Post-MVP)

**Purpose**: Security hardening, performance verification, documentation polish, and quickstart validation.

- [ ] T069 [P] Verify 3-layer PII filtering end-to-end in `backend/tests/test_voice/test_pii_filter.py`: write tests for (1) SSN pattern removed from `execute_tool` input, (2) credit card number removed from tool result before relay, (3) phone number removed from `VoiceMessage.content` before session store; all 3 layers per `specs/002-voice-interaction/research.md` Decision 4
- [ ] T070 [P] Add performance assertion to `backend/tests/test_voice/eval_harness.py`: measure round-trip time from `execute_tool()` call to response; assert P95 < 5000 ms; log timing for each of the 4 tools; print latency summary table
- [ ] T071 [P] Update `docs/` (or create `docs/voice-api.md`): document the 3 new API endpoints (`POST /api/realtime/session`, `WS /api/realtime/ws`, `GET /api/realtime/health`) with request/response examples; link to `specs/002-voice-interaction/contracts/voice-api.yaml` as the canonical OpenAPI spec
- [ ] T072 [P] Add voice feature section to `frontend/README.md` (or `docs/frontend.md`): describe the 3 new components (`VoiceMicButton`, `VoiceTranscript`, `VoiceStatusIndicator`) and the `useVoice` hook; include the 6-state machine diagram from `data-model.md`; note browser compatibility requirements (Chrome 90+, Firefox 85+, Edge 90+, Safari 15+)
- [ ] T073 Validate `specs/002-voice-interaction/quickstart.md` (if it exists) or `README.md` voice section: follow the quickstart instructions in a clean environment (`mock_mode=true`), verify a full voice conversation completes end-to-end in under 5 minutes from `git clone`; file a bug if any step fails
- [ ] T074 [P] Add WebSocket session ownership enforcement to `backend/app/api/realtime.py`: reject a second WebSocket connection for the same `session_id` with close code 4002 "Session already has an active connection"; prevents concurrent voice sessions from the same session context
- [ ] T075 Security review `backend/app/api/realtime.py`: verify (1) ephemeral token TTL ≤ 60 s is enforced, (2) token is validated against `session_id` on WS connect, (3) Azure OpenAI API key is never serialized into any response body, (4) `instructions` field in session request is sanitized (max 2000 chars, no prompt injection via system-level characters); add any missing guards

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
  └──► Phase 2 (Foundational) — BLOCKS all user stories
          ├──► Phase 3 (US1) 🎯 MVP Core — BLOCKS Phases 4, 5, 6, 7
          │       ├──► Phase 4 (US2 Escalation) — builds on US1 tool infra
          │       ├──► Phase 5 (US3 Hybrid) — builds on US1 session sharing
          │       ├──► Phase 6 (US4 Accessibility) — hardens US1 components
          │       └──► Phase 7 (US5 Degradation + Evals) — wraps US1 error paths
          │               └──► ✂️ MVP CUTLINE
          └──► Phase 8 (Polish) — depends on all phases complete
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|-----------|----------------------|
| US1 (P1) | Phase 2 complete | Nothing (first story) |
| US2 (P2) | Phase 3 complete | US3, US4, US5 after US1 |
| US3 (P3) | Phase 3 complete | US2, US4, US5 after US1 |
| US4 (P4) | Phase 3 complete | US2, US3, US5 after US1 |
| US5 (P5) | Phase 3 complete | US2, US3, US4 after US1 |

### Within Each Phase

1. Tests marked **[P]** can be launched together before any implementation
2. Models before services (Phase 2: T008/T009 before T011/T013)
3. Service interface before service implementations (T011 before T013/T014)
4. Backend endpoints before frontend integration (T023–T027 before T032)
5. Each phase should be independently runnable: `python -m pytest backend/tests/test_voice/ -x`

---

## Parallel Execution Examples

### Phase 2 — Foundational (launch all at once after Phase 1)

```bash
# Tests first — all parallel:
Task: T006 Write test_config.py (backend/tests/test_voice/test_config.py)
Task: T007 Write test_models.py (backend/tests/test_voice/test_models.py)
Task: T012 Write test_mock_service.py (backend/tests/test_voice/test_mock_service.py)

# Then models — parallel:
Task: T008 Create voice_enums.py (backend/app/models/voice_enums.py)
Task: T009 Create voice_schemas.py (backend/app/models/voice_schemas.py)
Task: T010 Create voice.ts types (frontend/src/types/voice.ts)

# Then services — T013 and T014 parallel, T015 after T011:
Task: T013 MockRealtimeService (backend/app/services/mock/realtime.py)
Task: T014 AzureRealtimeService (backend/app/services/azure/realtime.py)
```

### Phase 3 — US1 (backend tests parallel, then backend impl, then frontend parallel)

```bash
# Backend tests — all parallel:
Task: T016 test_create_session_mock_mode
Task: T017 test_create_session_with_existing_session_id
Task: T018 test_websocket_tool_call_relay
Task: T019 test_websocket_invalid_token_closes_4001
Task: T020 test_pii_not_echoed_in_tool_result

# Frontend tests — parallel with backend tests:
Task: T021 useVoice.test.ts
Task: T022 VoiceMicButton.test.tsx

# Backend impl — sequential (T023 → T024 → T025 → T026 → T027):
Task: T023 POST /session + WS /ws endpoints
Task: T024 WebSocket relay logic
Task: T025 4 tool definitions
...

# Frontend components — parallel after T028 (useVoice hook) is done:
Task: T029 VoiceMicButton.tsx
Task: T030 VoiceTranscript.tsx
Task: T031 VoiceStatusIndicator.tsx
Task: T033 API client createRealtimeSession()
```

### Phases 4–7 — Run in parallel (separate developers or sequential by priority)

```bash
Developer A: Phase 4 (US2 Escalation) — T034..T040
Developer B: Phase 5 (US3 Hybrid)     — T041..T046
Developer C: Phase 6 (US4 A11y)       — T047..T052
Developer D: Phase 7 (US5 + Evals)    — T053..T068
```

---

## Implementation Strategy

### MVP First (Phases 1–7, through Eval Pack)

Per `specs/002-voice-interaction/spec.md`: **MVP scope = US1 (P1) + US5 Degradation + Eval Pack**.

1. **Phase 1** — Setup (~30 min): config, .env, Bicep, test skeletons
2. **Phase 2** — Foundational (~2 h): models, types, services, DI
3. **Phase 3** — US1 MVP Core (~3–4 h): backend endpoints + frontend voice UI
4. → **STOP and VALIDATE**: `python -m pytest backend/tests/test_voice/ -x` + browser smoke test
5. **Phase 7** — US5 + Evals (~2 h): degradation, health check, eval harness, DEMO_RUNBOOK
6. → **DEMO READY**: All Phases 1–3 + 7 complete = MVP ✅

### Full Delivery (All Phases 1–7)

1. MVP (Phases 1–3 + 7) → Demo / stakeholder sign-off
2. Phase 4 (US2 Escalation) → test → merge
3. Phase 5 (US3 Hybrid) → test → merge
4. Phase 6 (US4 Accessibility) → test → merge
5. Phase 8 (Polish) → final regression → merge to main

### Commit Strategy (per Constitution)

```
feat(voice): Phase 1 - voice config and env setup
feat(voice): Phase 2 - voice models, services, DI (foundational)
feat(voice): Phase 3 - US1 voice support request (MVP core)
feat(voice): Phase 4 - US2 voice escalation
feat(voice): Phase 5 - US3 hybrid text/voice session
feat(voice): Phase 6 - US4 voice accessibility
feat(voice): Phase 7 - US5 degradation + eval pack
feat(voice): Phase 8 - polish and security hardening
```

---

## Notes

- **[P]** = different file, no unresolved dependencies — safe to parallelize
- **[US#]** label maps each task to its user story for traceability and independent delivery
- Tests must be written first and confirmed **failing** before implementation (Constitution Principle V)
- Run `cd backend && python -m pytest backend/tests/test_voice/ -x` after each phase
- Text chat must remain fully functional at every phase checkpoint — test with `python -m pytest backend/tests/ -x --ignore=backend/tests/test_voice`
- Mock mode (`MOCK_MODE=true`) must support a full demo without Azure credentials at all times
