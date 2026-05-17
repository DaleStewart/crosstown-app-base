# 🎤 Feature Summary: Voice Interaction (002-voice-interaction)

> **Branch**: `002-voice-interaction` | **Status**: ✅ Shipped — Production (2026-04-21, revision `azd-1776792457`)
> **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Tasks**: [tasks.md](./tasks.md)
> **Post-Ship Artifacts**: [Azure Realtime API Schema Skill](../../../.squad/skills/azure-realtime-api-schema/SKILL.md) | [CHANGELOG](../../../CHANGELOG.md) | [Release v0.1.5](../../../docs/RELEASE_NOTES.md)

---

## 📋 Feature Overview

The **Voice Interaction** feature adds a real-time spoken conversation channel to the 47 Doors Universal Front Door Support Agent, allowing students to speak naturally with the AI instead of typing. Audio travels directly from the browser to the Azure OpenAI GPT-4o Realtime API over WebRTC — the backend never touches raw audio, only lightweight token issuance and tool call relay. The same 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) that powers text chat is exposed as Realtime API function tools, giving voice conversations identical capability: ticket creation, knowledge article retrieval, escalation, and ticket status checks.

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Browser (React)                          │
│                                                                  │
│   VoiceMicButton  VoiceStatusIndicator  VoiceTranscript          │
│        └──────────────── useVoice hook ─────────────────┘        │
│                               │                                  │
│          ┌────────────────────┼────────────────────────┐         │
│          │ POST /api/realtime/session (ephemeral token) │         │
│          │ WS   /api/realtime/ws     (tool relay)       │         │
└──────────┼────────────────────┼────────────────────────┼─────────┘
           │                    │                         │
           │          ┌─────────▼─────────┐              │
           │          │    FastAPI Backend  │              │
           │          │                   │              │
           │          │  POST /session    │              │
           │          │  WS /ws           │              │
           │          │  GET /health      │              │
           │          │                   │              │
           │          │  RealtimeService  │              │
           │          │  ┌──────────────┐ │              │
           │          │  │ MockRealtime │ │ (demo/dev)   │
           │          │  │ AzureRealtime│ │ (production) │
           │          │  └──────────────┘ │              │
           │          │                   │              │
           │          │  3-Agent Pipeline │              │
           │          │  QueryAgent       │              │
           │          │  RouterAgent      │              │
           │          │  ActionAgent      │              │
           │          └─────────┬─────────┘              │
           │                    │ Tool execution relay    │
           │                    │                         │
           │  WebRTC Audio/SDP  │                         │
           │  (Direct — no backend proxy)                 │
           │                    │                         │
┌──────────▼────────────────────▼─────────────────────────▼───────┐
│                  Azure OpenAI Realtime API                        │
│              gpt-4o-realtime-preview (WebRTC)                     │
│                                                                  │
│   Tool calls: analyze_and_route_query  check_ticket_status        │
│               search_knowledge_base    escalate_to_human          │
└──────────────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- 🔒 **No audio proxy** — browser ↔ Azure OpenAI direct WebRTC; backend never sees audio bytes
- 🔑 **Ephemeral tokens** — TTL ≤ 60 s, single-use; the Azure API key never leaves the backend
- ♻️ **Shared session** — voice and text share the same `session_id` and conversation history
- 🧪 **Mock mode** — full-featured demo and CI mode with no Azure credentials required

---

## 📖 User Stories

| Priority | Story | Acceptance Criteria (Summary) |
|----------|-------|-------------------------------|
| **P1 🎯 MVP** | **Voice Support Request** — Student speaks a request and hears the agent respond with a ticket ID, KB articles, and SLA expectations | Mic click → listening state shown; "I forgot my password" → ticket created → agent speaks back within 10 s; VAD end-of-speech response starts within 2 s |
| **P2** | **Voice Escalation & Human Handoff** — Policy/sensitivity keywords trigger escalation and verbal confirmation | "I want a refund" → escalation ticket + verbal SLA; "I need a person" → immediate escalation; sensitive topics (Title IX) → urgent priority + supportive response |
| **P3** | **Hybrid Text + Voice in Same Session** — Session context preserved across modality switches | Text message → switch to voice → ask follow-up → agent remembers prior context; voice transcript appears in chat thread with 🔊 icon |
| **P4** | **Voice Accessibility** — Works with keyboard-only navigation and screen readers | Enter key activates mic; Escape stops voice; ARIA live regions announce all state changes; transcript added to screen reader live region |
| **P5 🎯 MVP** | **Graceful Degradation** — System falls back to text-only when voice is unavailable | API unavailable → mic button disabled with message; WebRTC drop → auto-fallback to text with conversation preserved; `voice_enabled=false` → mic button not rendered |

---

## 🎯 MVP Scope

The MVP cutline is **P1 (Core Voice) + P5 (Degradation) + Eval Pack**.

**Included in MVP:**
- ✅ `POST /api/realtime/session` — ephemeral token issuance
- ✅ `WS /api/realtime/ws` — tool call relay to 3-agent pipeline
- ✅ `GET /api/realtime/health` — voice availability check
- ✅ 4 voice tools: `analyze_and_route_query`, `check_ticket_status`, `search_knowledge_base`, `escalate_to_human`
- ✅ `MockRealtimeService` — full simulation for demos and CI (no Azure credentials)
- ✅ `AzureRealtimeService` — production implementation (httpx, `gpt-4o-realtime-preview`)
- ✅ `VoiceMicButton` — 6-state toggle (Idle/Connecting/Listening/Processing/Speaking/Error)
- ✅ `VoiceStatusIndicator` — live status banner with `aria-live="polite"`
- ✅ `VoiceTranscript` — inline voice messages with 🔊 speaker icons
- ✅ `useVoice` hook — complete WebRTC state machine + WS relay
- ✅ `ChatContainer` integration — voice alongside existing text chat
- ✅ Voice system prompt — natural speech output, ticket IDs spelled out, no markdown
- ✅ Graceful degradation — mic button hidden when voice unavailable, text chat unaffected
- ✅ Eval harness — eval prompts, mock baseline, regression detection

**Out of scope (v1):** Phone/SIP/PSTN, visual avatar, voice biometrics, multi-language, voice analytics, simultaneous multi-party voice.

---

## 📊 Non-Functional Requirements Met

| NFR | Requirement | Implementation |
|-----|-------------|----------------|
| **VNFR-001** | Voice response latency < 2 s from end of utterance | Azure OpenAI Realtime API WebRTC transport; server-side VAD; direct browser↔Azure path |
| **VNFR-002** | Tool execution < 5 s | Same pipeline as text chat; async WebSocket relay; non-blocking WS handler |
| **VNFR-003** | Voice does not degrade text chat | Separate WebRTC + WebSocket connections; zero coupling to text HTTP pipeline |
| **VNFR-004** | Modern browser support | WebRTC API (Chrome 90+, Firefox 85+, Edge 90+, Safari 15+); no polyfills required |
| **VNFR-005** | No raw audio stored | Audio travels browser↔Azure only; backend receives only text transcripts; PII-filtered before persistence |

---

## 🧪 Test Coverage

| Layer | Count | Details |
|-------|-------|---------|
| **Backend unit tests** | **435 / 435 ✅** | Config fields, Pydantic models, MockRealtimeService, API endpoints, PII filter, existing pipeline tests, plus 97 GPT-4o model evals |
| **Frontend unit tests** | Vitest | `VoiceMicButton` (6 states, keyboard), `useVoice` (state machine, WS, degradation) |
| **E2E tests** | Playwright | Full mock-mode voice session: click mic → speak → transcript → stop |
| **Eval harness** | Prompt suite | 20 voice eval prompts; mock baseline; regression detection vs. text baseline |
| **Manual smoke test** | Checklist | Per-PR: mic permission, listening state, tool execution, transcript, fallback |

**Backend test file breakdown:**

| File | Coverage |
|------|----------|
| `test_config.py` | Voice config fields, `voice_enabled` flag, mock-mode defaults |
| `test_models.py` | All 7 Pydantic v2 voice models — field bounds, validators, literals |
| `test_mock_service.py` | Token generation, 4 tool definitions, tool execution via pipeline |
| `test_endpoints.py` | `POST /session`, WS handshake, `GET /health`, error cases |
| `test_pii_filter.py` | PII scrubbing of transcripts before persistence |

---

## 🏛️ Constitution Principles Satisfied

The 47 Doors project constitution (v1.1.0) defines non-negotiable engineering principles. All applicable principles are satisfied:

| Principle | Requirement | Satisfied By |
|-----------|-------------|-------------|
| **Principle III** — Privacy First | No raw audio stored; PII-filtered transcripts only | Audio never reaches backend; `PiiFilter` applied before `VoiceMessage` persistence |
| **Principle III** — Ephemeral credentials | Tokens ≤ 60 s TTL, single-use; API key never in frontend | `RealtimeSessionResponse.token` issued by backend; expires_at enforced client-side |
| **Principle IV** — Context Continuity | Voice and text share session context | `session_id` is the same UUID for both modalities; `VoiceState.session_id` joins to `Session` |
| **Principle V** — Test-First Development | Failing tests written before each implementation phase | All voice test files created with failing stubs before implementation; 76 tests pass |
| **Principle VI** — Accessibility | Keyboard accessible; ARIA live regions | Enter activates mic, Escape stops; `VoiceStatusIndicator` has `aria-live="polite"`; transcript in live region |
| **Principle VII** — Graceful Degradation | Voice failure must not break text chat | Separate WebRTC/WS connections; `VOICE_ENABLED=false` removes mic button entirely; fallback auto-triggers on WebRTC drop |
| **Voice Channel Security** | No API key exposure; no audio proxy | Ephemeral token flow; `AzureRealtimeService` runs server-side only |

---

## 📽️ Slide Deck Summary

### What You Saw
- A student spoke a natural request → the same 3-agent pipeline ran → a ticket was created → the agent spoke back the ticket ID and KB articles
- Voice and text share one session: switch modalities mid-conversation without losing context
- The mic button gracefully disappears when voice is unavailable — text chat is always the fallback

### Why You Can Trust It
- **No audio stored** — raw audio travels browser↔Azure only; transcripts are PII-filtered before being written anywhere
- **435 backend tests pass** — voice models, services, endpoints, PII filter, existing pipeline tests, plus 97 GPT-4o model evals (intent, PII, sentiment, entities, urgency, e2e) running via `DefaultAzureCredential`
- **Mock mode works offline** — you just saw it run without any Azure credentials; production is a config flip

### What's Next
- **P2–P4 User Stories**: Voice escalation, hybrid text+voice, accessibility hardening
- **Accessibility hardening**: WCAG 2.1 AA audit; JAWS/NVDA screen reader testing; VAD threshold tuning per environment
- **Analytics**: Voice vs. text resolution rate comparison; per-department intent accuracy; session duration benchmarks

### Deployment Notes (v1)
- **Auth**: Managed identity (`ManagedIdentityCredential`) — API key auth is disabled by Azure subscription policy (`disableLocalAuth: true`)
- **Ephemeral tokens**: Backend calls `/openai/v1/realtime/client_secrets` with Bearer token, returns top-level `value` field
- **WebRTC**: Frontend connects to `{endpoint}/openai/v1/realtime/calls` with ephemeral token as Bearer auth
- **Docker**: `.dockerignore` prevents `.env` from being baked into container images (critical for managed identity auth)
- **Dependencies**: `aiohttp>=3.9.0` required for async credential acquisition
- **Default voice**: `marin` (OpenAI recommended). Available: alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar
- **GA API format**: Session config uses nested `audio.input.transcription` / `audio.output.voice` (preview flat fields cause HTTP 500 in `/client_secrets`)
- **Transcript events**: GA uses `response.output_audio_transcript.done` (not preview's `response.audio_transcript.done`); frontend has fallback extraction from `response.output_item.done`
- **Fallback retry**: Backend retries `/client_secrets` without `audio.output.transcription` on 5xx (field rejected by GA endpoint)

---

*Feature summary for 47 Doors `002-voice-interaction`. Engineering team: Tank (Backend), Trinity (Frontend), Oracle (Architect).*
