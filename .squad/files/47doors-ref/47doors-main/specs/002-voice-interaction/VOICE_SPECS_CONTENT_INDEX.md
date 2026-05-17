# 47 Doors Voice Feature: COMPLETE SPECS CONTENT INDEX

**Generated**: 2026-02-06  
**Scope**: All voice feature specifications extracted and indexed  
**Status**: Ready for implementation planning

---

## DOCUMENT 1: specs/002-voice-interaction/spec.md

### Lines 1-35: Header & Problem Statement
- Feature Branch: 002-voice-interaction
- Status: Draft
- Problem: "47 front doors" - students underserved by text-only interface
- Solution Vision: Real-time voice using Azure OpenAI GPT-4o Realtime API with WebRTC

### Lines 8-14: Vision Statement
**Key Quote**: "Add a voice channel to the existing 47 Doors support agent so students can have a natural spoken conversation with the system. The voice agent uses the same 3-agent pipeline (intent detection, routing, ticket creation, KB retrieval) as the text chat, but through the Azure OpenAI GPT-4o Realtime API with WebRTC transport."

### Lines 16-114: User Scenarios & Testing (Mandatory)

**User Story 1: Voice Support Request (P1)**
- **Acceptance**: Click mic → say "I forgot my password" → receive ticket ID + guidance within 10 seconds
- **Key Scenarios**:
  1. Microphone permission requested, "listening" indicator shown
  2. Voice agent invokes analyze_and_route_query tool, routes to IT, speaks ticket ID
  3. Facilities request extracts building entity, routes correctly
  4. Response starts within 2 seconds of student finishing utterance

**User Story 2: Voice Escalation & Human Handoff (P2)**
- **Trigger**: Policy keywords (refund, appeal, etc.), sensitive topics (Title IX, mental health)
- **Acceptance**: Detects escalation, creates ticket, speaks confirmation + expected response time
- **Scenarios**:
  1. "Can I get a refund?" → escalates with SLA
  2. "I need to talk to a person" → immediate escalation
  3. Sensitive topics → urgent escalation with supportive language

**User Story 3: Hybrid Text+Voice in Same Session (P3)**
- **Acceptance**: Type message → switch to voice → reference previous message → context preserved
- **Scenarios**:
  1. Ask "What's the status of the ticket I just created?" after creating via text
  2. Switch from voice back to text seamlessly
  3. Transcripts show speaker icon for visual distinction

**User Story 4: Voice Accessibility (P4)**
- **Acceptance**: Keyboard-only activation, screen reader announcements, no visual dependency
- **Scenarios**:
  1. Press Enter on mic button → voice activates with audible indicator
  2. Screen reader announces state changes
  3. Press Escape to end voice mode

**User Story 5: Voice Error Handling & Degradation (P5)**
- **Acceptance**: Graceful fallback to text when voice unavailable
- **Scenarios**:
  1. Realtime API unavailable → mic button disabled with message
  2. WebRTC connection drops → auto-fallback to text, conversation preserved
  3. Browser doesn't support WebRTC → text chat remains functional
  4. voice_enabled=false → mic button not rendered

### Lines 101-114: Edge Cases
- Non-English queries: Model instructs student to speak English, provides multilingual support line
- Background noise: System asks for clarification
- PII in speech: Raw audio not stored, system prompt prevents repetition, transcripts filtered
- Long utterances: Realtime API handles incrementally
- Barge-in (interruption): Realtime API detects and stops agent speech
- Concurrent sessions: Only one voice session per tab

### Lines 116-164: Functional Requirements (23 Total)

#### Voice Connection & Transport (VFR-001 to VFR-005)
- VFR-001: Microphone toggle button in chat input area
- VFR-002: gpt-4o-realtime-preview model via WebRTC (browser RTCPeerConnection direct to Azure)
- VFR-003: **CRITICAL**: Backend issues ephemeral tokens (POST /api/realtime/session) - DO NOT expose API key
- VFR-004: Server-side VAD (voice activity detection) for natural turn-taking
- VFR-005: User interruption support (barge-in) - student can speak while agent responds

#### Voice Agent Behavior (VFR-006 to VFR-010)
- VFR-006: Use same system prompt as text agent, add voice-specific instructions
- VFR-007: Expose existing 3-agent pipeline as Realtime API function tools:
  - analyze_and_route_query
  - check_ticket_status
  - search_knowledge_base
  - escalate_to_human
- VFR-008: Backend WebSocket relay executes tools against existing pipeline
- VFR-009: Spell out ticket IDs clearly (character by character)
- VFR-010: **CRITICAL**: Do NOT repeat PII back (SSN, credit card, etc.)

#### Session & Context (VFR-011 to VFR-013)
- VFR-011: Voice conversations share session_id with text conversations
- VFR-012: Voice transcripts appended to chat with speaker icon
- VFR-013: Audit logs include input_modality: "voice" field

#### User Interface (VFR-014 to VFR-018)
- VFR-014: 6 visual states: idle (gray), listening (pulsing green), processing (spinner), connected (solid green), error (red), disabled (grayed)
- VFR-015: Real-time waveform/volume indicator during voice session
- VFR-016: Voice transcripts in chat with microphone icon
- VFR-017: Keyboard accessible (Enter to activate, Escape to deactivate)
- VFR-018: ARIA live region announcements for state changes

#### Configuration & Degradation (VFR-019 to VFR-022)
- VFR-019: voice_enabled config flag (default: true)
- VFR-020: Fallback to text on unavailability with notification
- VFR-021: Health check includes realtime_api status
- VFR-022: Mock mode supports voice via mock Realtime service

#### Infrastructure (VFR-023 to VFR-025)
- VFR-023: Bicep includes gpt-4o-realtime-preview deployment
- VFR-024: POST /api/realtime/session endpoint for ephemeral tokens
- VFR-025: WebSocket /api/realtime/ws endpoint for tool relay

### Lines 157-164: Non-Functional Requirements (5 Total)

- VNFR-001: Response latency < 2 seconds (end of utterance to speech start, excluding tool execution)
- VNFR-002: Tool execution within 5 seconds (same as text)
- VNFR-003: Voice doesn't degrade text chat (separate connections)
- VNFR-004: Works in Chrome 90+, Firefox 85+, Edge 90+, Safari 15+
- VNFR-005: **CRITICAL**: Raw audio never stored/logged, only PII-filtered text

### Lines 171-181: Success Criteria (6 Total)

- VSC-001: Students complete full support request via voice in 15 seconds
- VSC-002: Voice escalation 100% (all policy/sensitivity triggers fire)
- VSC-003: 95% correct intent detection (transcript vs. text baseline)
- VSC-004: Text↔Voice modality switching preserves session 100%
- VSC-005: Graceful degradation activates within 3 seconds
- VSC-006: Voice doesn't increase text latency > 50ms p95

### Lines 182-197: Dependencies & Out of Scope

**Dependencies**:
- Azure OpenAI gpt-4o-realtime-preview (production required)
- Browser WebRTC (native)
- FastAPI WebSocket (native via Starlette)
- Existing 3-agent pipeline (will wrap as tools)

**Out of Scope v1**:
- Phone/telephony, avatars, voice biometric auth, multi-language, translation, voice cloning, recording, analytics, multi-party

---

## DOCUMENT 2: specs/002-voice-interaction/plan.md

### Lines 1-10: Header & Summary
- Branch: 002-voice-interaction
- Spec: spec.md
- Goal: Add real-time voice using Realtime API with WebRTC
- Key Design: Voice and text share same session_id for seamless modality switching

### Lines 11-20: Technical Context
- Languages: Python 3.11 (backend), TypeScript 5.x (frontend)
- Dependencies: FastAPI + Starlette WebSocket, React 18 + native WebRTC, Azure OpenAI Realtime API
- Target: Chrome 90+, Firefox 85+, Edge 90+, Safari 15+
- Performance: <2s voice latency, <5s tool execution
- Key Constraint: No raw audio storage, PII never repeated, graceful degradation to text

### Lines 22-35: Constitution Compliance Check

**Summary Table**:
| Principle | Compliance | Notes |
|-----------|-----------|-------|
| I. Bounded Agent Authority | ✅ PASS | Same bounded tools via Realtime API function calling |
| II. Human Escalation | ✅ PASS | escalate_to_human tool exposed, all triggers work |
| III. Privacy-First | ✅ PASS | Raw audio not stored, transcripts PII-filtered, audit logs include input_modality |
| IV. Stateful Context | ✅ PASS | Shared session_id, modality switching preserves history |
| V. Test-First | ✅ PASS | All endpoints/tools have tests, mock Realtime enables testing |
| VI. Accessibility | ✅ PASS | Keyboard accessible, screen reader announcements, additive not replacement |
| VII. Graceful Degradation | ✅ PASS | WebRTC failure → text fallback, health check includes realtime_api |

### Lines 40-54: Data Flow Diagram

`
Student (browser)
  ├─ Text: POST /api/chat → FastAPI → 3-agent pipeline → JSON
  │
  └─ Voice: WebRTC audio ──────────────→ Azure OpenAI Realtime API
                                            │
           Browser ← WebRTC audio ────────┤
           (agent speech)                 │
                                           │
           When tool call needed:         │
           Azure OpenAI → WebSocket → Backend /api/realtime/ws
              Tool handler invokes 3-agent pipeline
              Returns result via WS → Azure OpenAI (continues)
`

### Lines 56-66: Key Design Decisions
1. **WebRTC (not WebSocket audio)**: Lowest latency, browser direct to Azure
2. **Backend WebSocket relay for tools only**: Limited to issuing tokens and executing tools
3. **Shared session context**: Same session_id enables seamless switching
4. **Mock support**: MockRealtimeService for dev/demo without Azure

### Lines 68-128: Project Structure

**Backend Changes**:
- pp/api/realtime.py - NEW
- pp/services/interfaces.py - MODIFY
- pp/services/azure/realtime_service.py - NEW
- pp/services/mock/realtime_service.py - NEW
- pp/core/config.py - MODIFY
- pp/core/dependencies.py - MODIFY
- pp/models/schemas.py - MODIFY

**Frontend Changes**:
- src/components/VoiceChat.tsx - NEW
- src/components/MicButton.tsx - NEW
- src/hooks/useVoiceChat.ts - NEW
- src/components/ChatInput.tsx - MODIFY
- src/components/ChatContainer.tsx - MODIFY
- src/components/MessageBubble.tsx - MODIFY
- src/api/client.ts - MODIFY

**Infrastructure**:
- infra/main.bicep - MODIFY (add gpt-4o-realtime-preview)

---

## DOCUMENT 3: specs/002-voice-interaction/tasks.md

### Lines 1-10: Header & Format
- Input: Design documents from /specs/002-voice-interaction/
- Format: [ID] [P?] [Story] Description
- [P] = Parallel (can run independently)
- [Story] = User story reference (US1, US2, etc.)

### Lines 14-24: Phase 1 - Setup (Shared Infrastructure)

**5 Tasks (all parallel)**:
- T001: Voice/realtime config settings (config.py)
  - voice_enabled (bool)
  - azure_openai_realtime_deployment (str)
  - azure_openai_realtime_api_version (str, "2025-04-01-preview")
  - realtime_voice (str, "marin")
  - realtime_vad_threshold (float, 0.5)

- T002: RealtimeServiceInterface (services/interfaces.py)
  - create_session() → dict (token + endpoint)
  - get_tool_definitions() → list[dict]
  - execute_tool(tool_name, arguments, session_id) → dict

- T003: Voice types (frontend/src/types/index.ts)
  - VoiceState enum
  - VoiceMessage extending Message
  - RealtimeSessionResponse

- T004: input_modality field
  - Add "text" | "voice" to AuditLog and ChatMessage

- T005: Bicep deployment (infra/main.bicep)
  - gpt-4o-realtime-preview
  - Version: 2025-04-01

### Lines 26-40: Phase 2 - Backend Voice Services

**6 Tasks (T006-T011)**:
- T006: MockRealtimeService
  - Fake token, tool definitions, delegation to existing agents
- T007: AzureRealtimeService
  - Azure REST API calls, tool execution delegation
- T008: Register in dependencies.py
- T009: Create realtime.py endpoints
  - POST /api/realtime/session
  - WebSocket /api/realtime/ws
- T010: Mount router in routes.py
- T011: Update health check

### Lines 45-81: Phase 3 - User Story 1 (MVP)

**4 Backend Tests (T012-T015)**:
- T012: test_create_session
- T013: test_analyze_and_route_query_tool
- T014: test_search_knowledge_base_tool
- T015: test_websocket_tool_execution

**7 Frontend Tasks (T016-T022)**:
- T016: useVoiceChat hook
  - startVoiceSession(), stopVoiceSession(), voiceState, handleToolCall(), transcript
  - Exposes: { startVoiceSession, stopVoiceSession, voiceState, transcript, isVoiceSupported }
- T017: MicButton component (6 states, keyboard accessible)
- T018: VoiceChat component (waveform, status)
- T019: ChatInput integration (add MicButton)
- T020: MessageBubble (speaker icon for voice messages)
- T021: ChatContainer integration (display voice transcripts)
- T022: client.ts addition (createRealtimeSession())

**Checkpoint**: Full voice conversation works end-to-end (MVP)

### Lines 83-98: Phase 4-7 - Additional Features

**Phase 4 (US2)**: Escalation
- T023-T026: Escalation tool tests and system prompt verification

**Phase 5 (US3)**: Hybrid text+voice
- T027-T029: Shared session_id, context preservation tests

**Phase 6 (US4)**: Accessibility
- T030-T032: ARIA announcements, keyboard focus, screen reader

**Phase 7 (US5)**: Error handling
- T033-T036: WebRTC failures, permission denied, health check

### Lines 144-202: Phase 8 - Polish & Dependencies

**Phase Dependencies Table**:
- Phase 1: No dependencies (start immediately)
- Phase 2: Depends on Phase 1
- Phase 3: Depends on Phase 2
- Phase 4-7: Can run in parallel after Phase 3
- Phase 8: Depends on all previous

**Parallel Opportunities**:
- Phase 1: All 5 tasks parallel
- Phase 2: T006 & T007 parallel
- Phase 3: All tests parallel, T017 parallel with T016

**MVP Cutline**: Phases 1-3 complete
- 30 min setup
- 2 hours backend
- 3 hours frontend
- **Total: 1-2 days for full voice MVP**

### Lines 182-202: Implementation Strategy

**MVP First**:
1. Phase 1 (setup, ~30 min)
2. Phase 2 (backend, ~2 hrs)
3. Phase 3 (frontend, ~3 hrs)
4. Stop and validate
5. Demo to stakeholders

**Full Delivery**:
6. Phase 4 (escalation, ~1 hr)
7. Phase 5 (hybrid, ~1 hr)
8. Phase 6 (accessibility, ~1 hr)
9. Phase 7 (error handling, ~1 hr)
10. Phase 8 (polish + regression, ~1 hr)

**Total**: 3-5 days for full feature

---

## SUMMARY TABLE: All Voice Requirements

| Category | Count | Details |
|----------|-------|---------|
| User Stories | 5 | P1-P5 coverage |
| Functional Requirements | 23 | Voice transport, agent behavior, session, UI, config, infra |
| Non-Functional Requirements | 5 | Latency, browser support, no audio storage |
| Success Criteria | 6 | Measurable outcomes for validation |
| Tasks | 41 | 8 phases, parallel execution where possible |
| Backend Tests | 8+ | Endpoints, tools, escalation, errors |
| Constitutional Principles | 7 | All PASS for voice feature |
| Infrastructure Changes | 1 | Single new Bicep deployment |

---

## IMPLEMENTATION ROADMAP

### Day 1
- Morning: Phase 1 (Setup) - 30 min
- Late Morning: Phase 2 (Backend) - 2 hours
- Afternoon: Phase 3 (Frontend) - 3 hours
- **Checkpoint**: Full voice MVP working

### Day 2
- Phase 4 (Escalation) - 1 hour
- Phase 5 (Hybrid mode) - 1 hour
- Phase 6 (Accessibility) - 1 hour
- Phase 7 (Error handling) - 1 hour
- **Checkpoint**: All features working

### Day 3
- Phase 8 (Polish + regression tests) - 1 hour
- **Status**: Ready to ship

---

**✅ ALL SPECIFICATIONS INDEXED AND READY FOR IMPLEMENTATION**
