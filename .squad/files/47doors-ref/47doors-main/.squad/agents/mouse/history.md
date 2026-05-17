# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### Phone Call-In Feature Tests — 2026-03-19

**What was tested:**
- `test_phone_schemas.py` — All 5 Pydantic models: `IncomingCallEvent`, `CallEventRequest`,
  `CallState`, `PhoneHealthResponse`, `EventGridValidationEvent`. Covered valid construction,
  missing required fields, optional fields defaulting to None, Literal status validation
  (ringing/connected/disconnected/failed), edge cases (empty strings, very long caller IDs,
  non-E.164 formats, boolean coercion).
- `test_phone_service.py` — `MockPhoneService` contracts: `handle_incoming_call` (unique IDs,
  anonymous callers), `handle_call_event` for all known event types (CallConnected,
  PlayCompleted, CallDisconnected) and unknown types (graceful handling), `health_check`
  tuple structure, concurrency isolation (5 parallel calls, distinct IDs, no cross-state
  contamination).
- `test_phone_endpoints.py` — Three endpoints via `TestClient`: `GET /api/phone/health`
  (200, all three boolean fields present, mock_mode=True in test env), `POST
  /api/phone/incoming` (Event Grid SubscriptionValidation handshake echoing validationCode,
  IncomingCall events, empty/invalid payloads → 400/422), `POST /api/phone/callbacks`
  (CallConnected, CallDisconnected, PlayCompleted, optional result_info, unknown event type,
  empty/missing-field bodies → 400/422).

**Patterns used:**
- Lazy imports inside test methods so tests fail with ImportError when Tank's code isn't there
  yet (not at collection time) — same pattern as `test_voice/test_models.py`
- `_make_valid(**overrides)` helper factories for multi-field model tests
- Class-per-contract grouping (`class TestCallState:`, `class TestIncomingCall:`, etc.)
- `pytest.raises(Exception)` (not `ValidationError`) for Pydantic v2 compat
- Conftest's `MOCK_MODE=true` via `autouse=True` `set_test_env` fixture drives all env setup;
  no per-file env manipulation needed
- Endpoint tests use `TestClient(app)` fixture (sync) — no async client needed for HTTP tests
- Event Grid validation handshake tested as a distinct class from IncomingCall events

**Edge cases covered:**
- `CallState` rejects `"active"` and `"unknown"` (not in the phone Literal — not the voice Literal)
- Empty payload (`b""`) and malformed JSON on POST endpoints → 400 or 422
- Empty JSON array `[]` on incoming endpoint → 400 or 422
- `EventGridValidationEvent` without `validationUrl` (optional field)
- Multiple concurrent simulated calls produce distinct `call_connection_id` values
- Anonymous/non-E.164 caller IDs flow through without rejection

**Key decision:**
- Did NOT enforce E.164 format at the schema level — the spec says `caller_id: str` with no
  format constraint. Tested the pass-through explicitly rather than testing a constraint that
  doesn't exist. See `mouse-phone-tests.md` decision file.

### GPT-4o to GPT-4.1 Migration — Test Impact — 2026-03-20

**What was scanned and updated:**
- Systematically searched all backend test files (`backend/tests/`) for hardcoded model references:
  - `gpt-4o` (found in 4 files, 5 occurrences)
  - `gpt-4o-realtime-preview` (found in 1 file, 2 occurrences)
  - Old API versions `2024-05-01-preview`, `2024-02-15-preview`, etc. (found in test_gpt4o_evals.py)

**Files updated:**
1. `backend/tests/conftest.py` line 255: Changed `AZURE_OPENAI_DEPLOYMENT` from `"gpt-4o"` to `"gpt-4.1"`
2. `backend/tests/test_voice/test_config.py` lines 21, 32: Updated Settings fixtures from `"gpt-4o"` to `"gpt-4.1"`
3. `backend/tests/test_voice/test_models.py` lines 141, 161: Updated RealtimeSessionResponse fixtures from `"gpt-4o-realtime-preview"` to `"gpt-4.1-realtime-preview"`
4. `backend/tests/test_gpt4o_evals.py` lines 52, 216–217: Updated deployment defaults from `"gpt-4o"` to `"gpt-4.1"` and API version from `"2024-05-01-preview"` to `"2024-12-01-preview"`

**Test results:**
- All 447 tests pass; 97 eval tests skipped (require real Azure credentials, intentional)
- No regressions detected
- Conftest fixture-driven environment setup ensures all tests pick up the new deployment name

**Key decision:**
- Assumed `"gpt-4.1"` as the migration target and `"2024-12-01-preview"` as the API version.
  Tank's infra changes confirmed these choices (check `.squad/decisions.md` for full record).
- Realtime deployment migration confirmed as `gpt-realtime` (Tank's decision on naming).

**Session coordination:** Parallel spawn 2026-04-08T17:25 with Tank. Orchestration log: `.squad/orchestration-log/2026-04-08T17-25-mouse.md`

### Playwright Deployment Eval Suite — 2026-04-09

**What was created:**
- `frontend/tests/e2e/eval.spec.ts` — 24-test evaluation suite for live deployment testing
- Updated `frontend/playwright.config.ts` — added `BASE_URL` env var override, skips local `webServer` when targeting live

**Existing test baseline (run against live deployment):**
- 43 total existing tests: 32 passed, 10 failed, 1 skipped
- 5 smoke tests failed: hardcoded `http://localhost:8000` backend URLs (ECONNREFUSED)
- 4 accessibility tests failed: real axe-core violations (color contrast, WCAG compliance)
- 1 chat test failed: "Talk to Human" button not found (timeout — likely UI label mismatch)
- 1 voice test skipped: placeholder only

**Eval suite results (live deployment):**
- 24 total eval tests: 22 passed, 2 failed
- Homepage, chat, sessions, error handling, voice UI, performance: ALL PASS
- Two KB quality failures detected (real issues, not test bugs):
  1. "How do I register for classes?" → AI asked clarifying question instead of answering
  2. "How do I apply for financial aid?" → AI routed to IT Support instead of Financial Aid
- Performance: page loads ~1.3s, chat API ~3-4s avg, health endpoint ~1s (warm), 5.4s (cold start)

**Config patterns established:**
- `BASE_URL` env var overrides `baseURL` in playwright config (defaults to localhost:5173)
- `BACKEND_URL` env var for direct API tests (auto-derived from BASE_URL by replacing `-frontend` with `-backend`)
- `webServer` block conditionally skipped when `BASE_URL` is set (no local server startup for live testing)
- Health endpoint threshold set to 10s to accommodate Azure Container App cold starts
- All eval tests tagged with `@eval` for selective execution

**Key finding:**
- The 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) misroutes some queries:
  registration goes to clarification loop, financial aid goes to IT.
  These are real demo risks that should be addressed before the next demo.

### Live Transcript SSE Pipeline Diagnosis — 2026-04-10

**Symptom:**
- Live page (`/live`) shows "Call connected" but no user_speech or agent_speech
  transcript events appear during phone calls.

**What was tested:**
- `test_sse_http.py` — 6 new tests: route configuration (path, method, prefix
  sharing), response headers (text/event-stream, no-cache, X-Accel-Buffering=no),
  generator integration with singleton TranscriptBus, SSE frame format validation.
- `live-transcript.spec.ts` — 10 new Playwright E2E tests: idle state "Waiting for
  call…", call_started rendering, user_speech caller bubble, agent_speech AI bubble,
  tool_call pulsing badge, call_ended with duration, full lifecycle (7 events),
  SSE URL path verification, accessibility (role=log, aria-live=polite),
  malformed data resilience.
- Ran all existing `test_transcripts/` tests — 8 pre-existing + 6 new = 14 pass.
- Ran Playwright suite — 10/10 pass (chromium).

**Components verified working:**
- ✅ TranscriptBus pub/sub (singleton, multiple subscribers, slow subscriber drop)
- ✅ SSE generator (_event_generator) yields correct `data: {json}\n\n` frames
- ✅ Route registered at `/api/phone/transcripts/stream` (GET, under /api/phone prefix)
- ✅ Response headers: text/event-stream, no-cache, keep-alive, X-Accel-Buffering=no
- ✅ nginx location block `/api/phone/transcripts/stream` with proxy_buffering off
- ✅ Frontend useTranscriptStream hook → EventSource → LivePage rendering

**ROOT CAUSE FOUND — media_ws.py session.update schema is WRONG:**
- The code (lines 136-158) sends a nested `audio` object:
  ```json
  "audio": {
    "input": { "format": "pcm16", "transcription": {"model": "whisper-1"} },
    "output": { "format": "pcm16", "voice": "marin" }
  }
  ```
- The Azure OpenAI Realtime API expects FLAT session properties:
  ```json
  "input_audio_format": "pcm16",
  "input_audio_transcription": { "model": "whisper-1" },
  "voice": "marin"
  ```
- Confirmed via official Azure SDK (azure-samples/aoai-realtime-audio-sdk README).
- The API silently ignores the nested `audio` object → transcription is never enabled.
- `call_started` still works because it's published on WebSocket accept (before OpenAI).
- `user_speech`/`agent_speech` never fire because the transcription events from OpenAI
  (`conversation.item.input_audio_transcription.completed`,
  `response.output_audio_transcript.done`) are never generated.

**Fix required (for Tank):**
- In `backend/app/api/media_ws.py` lines 140-149, replace:
  ```python
  "audio": {
      "input": {"format": "pcm16", "transcription": {"model": "whisper-1"}},
      "output": {"format": "pcm16", "voice": settings.realtime_voice},
  },
  ```
  with:
  ```python
  "input_audio_format": "pcm16",
  "input_audio_transcription": {"model": "whisper-1"},
  "voice": settings.realtime_voice,
  ```

**Fix applied (by Tank, commit c7669e0):**
- Exact fix implemented as prescribed above
- Removed nested udio object
- Moved config to flat session properties
- All 461 backend tests now pass
- Backend re-deployed and healthy

**Learnings:**
- Azure OpenAI Realtime API silently ignores malformed session.update payloads
- The SDK samples use flat properties; nested udio object is not in the published schema
- Transcription is disabled when config is missing (no error, no events)
- SSE infrastructure (nginx buffering, TranscriptBus, generator) was working perfectly — issue was 100% upstream (no config)
- Test-driven diagnosis was critical: without the test suite, this would have taken 8+ hours of manual debugging

### Cross-Team Update — 2026-04-21

**Status:** Phone bridge verified on prod, full doc sweep landed

- Phone bridge transcript schema fix verified live on prod (revision azd-1776792457)
- Full doc sweep completed across specs, runbook, release notes, participant guide, coach guide
- Backend tests: 461/461 green
- Frontend: TypeScript clean
- See .squad/decisions.md for complete decision log
