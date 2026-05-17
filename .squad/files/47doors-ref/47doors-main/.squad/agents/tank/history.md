# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Core Context

### Foundational Architecture Patterns (Phase 0 Research, 2026-03-13)

Tank established the voice interaction architecture during Phase 0 research:
- WebRTC transports audio direct browser → Azure; backend never touches audio bits
- Ephemeral tokens (≤60s TTL) issued by `POST /api/realtime/session`; API keys server-side only
- Tool calls flow over dedicated WS relay `/api/realtime/ws/{session_id}`, routed through QueryAgent → RouterAgent → ActionAgent pipeline (Constitution I)
- Three-layer PII filter: pre-tool, post-tool, pre-speech (Constitution III)
- Mock mode: full `RealtimeService` mock implementing `RealtimeServiceInterface`, controlled via `settings.use_mock_services`
- Voice transcript entries use `input_modality = "voice"` discriminator in shared session history (same `session_id` UUID as text)
- `eastus2` primary region; initial deployment target was `gpt-4o-realtime-preview`

**Key patterns established:**
- New voice models go in `backend/app/models/voice_schemas.py` and `backend/app/models/voice_enums.py`
- Service interfaces in `backend/app/services/interfaces.py` (ABC pattern)
- Config additions in `backend/app/core/config.py` with `model_validator(mode="after")` for Pydantic v2

**Pydantic v2 Gotcha — Multiple Model Validators:**
- Only one `@model_validator(mode="after")` per class allowed. Defining a second silently OVERRIDES the first. Solution: combine all after-validators into single method (e.g., `_auto_disable_features` for voice+phone auto-disable logic).

---

## Team Updates

### 2026-04-09T04:52Z — Transcript Event Compatibility Fix

Tank fixed event name mismatch in `backend/src/speech_agent/routes/media_ws.py`:
- **Problem:** Handler did not accept both preview (`response.audio_transcript.done`) and GA (`response.output_audio_transcript.done`) event names from Azure OpenAI API
- **Solution:** Updated handler to accept both variants for compatibility across API lifecycle versions
- **Test Status:** All 461 tests passed
- **Commit:** 297e7f7
- **Deploy:** Backend deployed and pushed

**Cross-agent note:** Switch simultaneously added URL routing for /live and /runbook pages (commit dc90d44). Both changes deployed without blocking issues. Voice interaction pipeline remains stable.

---

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### ARCHIVED: Phone Architecture & Azure Realtime Auth (2026-03-14 through 2026-03-15)

**Phone feature overview:** ACS Call Automation bridges PSTN → WebSocket → Azure OpenAI Realtime. Audio never touches backend (same pattern as browser WebRTC). Reused `gpt-4o-realtime` deployment + 4-tool pipeline with phone-specific prompt (terse, no markdown).

**Key patterns:** PhoneServiceInterface + AzurePhoneService follow ABC pattern as RealtimeService. MockPhoneService is synchronous (tests call without await); API layer uses `inspect.isawaitable()` to handle both. ACS webhook events have two validation types; Event Grid/Call Automation formats are normalized. Callback URL reconstruction required reading X-Forwarded-Proto/Host headers for public HTTPS in Container Apps.

**Config:** `phone_enabled`, `azure_acs_endpoint`, `azure_acs_connection_string`, `acs_phone_number`, `max_call_duration` in config.py. ACS resource always provisioned in main.bicep with Contributor role assignment. SDK: `azure-communication-callautomation>=1.5.0` (note: v1.5.0 renamed MediaStreamingTransportType → StreamingTransportType).

**Key fixes:** (1) SDK import break — StreamingTransportType enum fix; (2) Media relay bridge — new `/ws/acs-media` WebSocket proxy for ACS → OpenAI auth; (3) Transcription config — added `input_audio_transcription` to session.update; (4) Realtime auth — fixed endpoint to `/openai/v1/realtime/client_secrets`, added DefaultAzureCredential with API key fallback, async token refresh.

### 2026-04-09 — Phone Call Failure Diagnosis (SDK Import Break)

**Root cause:** Inbound PSTN calls to `+19132171946` were never answered. Event Grid delivered `IncomingCall` events successfully to `/api/phone/incoming`, but the handler crashed with `ImportError: cannot import name 'MediaStreamingTransportType' from 'azure.communication.callautomation'`. The SDK (v1.5.0, installed via `>=1.4.0` pin) renamed `MediaStreamingTransportType` → `StreamingTransportType`. Every call attempt returned 503 Service Unavailable.

**Fix:** Updated `backend/app/services/azure/phone.py` to import `StreamingTransportType` (correct name) and `AudioFormat`. Also enabled `enable_bidirectional=True` and set `audio_format=AudioFormat.PCM24_K_MONO` per current SDK docs for Azure OpenAI Realtime integration.

**Debugging pattern for phone issues:**
1. Hit `/api/phone/health` first — health check only tests client init, not the answer_call path, so it can show green while calls fail
2. Check `az containerapp logs show` for the actual runtime error — the ImportError only fires at call-answer time (lazy import inside `handle_incoming_call`)
3. Event Grid subscription was healthy (provisioningState=Succeeded, correct endpoint URL, correct filter)
4. Managed identity had Contributor role on ACS — sufficient for Call Automation
5. The SDK `>=` pin in requirements.txt means the container may get a newer version than dev tested with — watch for API surface changes in `azure-communication-callautomation`

**Key takeaway:** Pin SDK versions more tightly (e.g., `~=1.4.0` or `>=1.4.0,<2.0`) to avoid surprise breaking changes from enum renames in minor releases.

**SDK fix applied:** `StreamingTransportType` is the correct enum name for `azure-communication-callautomation >= 1.5.0`. Future work: migrate SDK pins to `~=1.5.0` or `>=1.5.0,<2.0` to lock this version and prevent future enum renames from breaking production calls.

### 2026-04-09 — Silent Audio Fix (WebSocket Bridge for Media Relay)

**Problem:** After the SDK fix above, calls were answered but produced dead air. ACS media streaming was configured to connect directly to Azure OpenAI Realtime API WebSocket, but:
- Azure OpenAI had `disableLocalAuth=true` (Entra ID only)
- ACS resource had NO managed identity to authenticate with  
- `MediaStreamingOptions.transport_url` provided no auth header mechanism
- CloudEvents callback handler crashed due to incorrect field mapping (looked for `callConnectionId` at top level instead of nested in Call Automation events)

**Solution:** Created WebSocket bridge at `/ws/acs-media` to proxy ACS media through the authenticated backend connection:
```
PSTN → ACS → WS [backend /ws/acs-media] → WS [Azure OpenAI Realtime API]
```

**Key changes:**
- New file: `backend/app/api/media_ws.py` (296 lines) — WebSocket relay with session config
- Modified: `phone.py` service — updated `transport_url` to point to backend bridge
- Modified: `phone.py` API — fixed CloudEvents parsing (multi-layer to handle both Event Grid and Call Automation formats)
- Modified: `main.py` — registered `/ws/acs-media` route

**Pattern established:** Backend WebSocket bridge is the documented Azure pattern for ACS→OpenAI Realtime. Backend already has the RBAC role (Cognitive Services OpenAI User), so no infra changes needed. Audio format is compatible (PCM24K mono both ways).

**Testing:** All 447 tests pass. Audio now flows bidirectionally on answered PSTN calls.

### 2026-04-09 — SSE Transcription Config & Nginx Fix (Live Transcript)

**Problem:** Live transcript viewer (`/live` page) connected to `/api/phone/transcripts/stream` SSE endpoint but received no transcript events. Audio was flowing correctly.

**Root cause (identified by Mouse's test suite):** `media_ws.py` `session.update()` payload did not include `input_audio_transcription` + `output_audio_transcription` config. Azure OpenAI Realtime API silently skips transcript events when transcription is unconfigured.

**Solution (Tank):** Added transcription config to `backend/app/api/media_ws.py`:
```python
input_audio_transcription={"model": "whisper-1"},
output_audio_transcription={"model": "whisper-1"}
```

**Nginx fix (Coordinator):** Added dedicated `location /api/phone/transcripts/stream` block in `frontend/nginx.conf` with:
- `proxy_buffering off` + `proxy_cache off` (disables response buffering)
- `proxy_set_header Connection ""` (uses HTTP keep-alive instead of WebSocket upgrade)
- Path was initially wrong (`/api/transcripts/stream` → fixed to `/api/phone/transcripts/stream`)

**Verification:** All 461 backend tests pass. Backend deployed successfully. Live transcript viewer now functional.

**Key takeaway:** Azure OpenAI Realtime API requires explicit transcription config in session.update to fire transcript events. This is a silent no-op if missing — no error, just no events. Test coverage (Mouse's E2E tests) was critical to surface this.

### ARCHIVED: Voice Config, Bicep, Realtime Endpoints, Frontend Deployment (2026-03-14)

**Phase 1 setup (T001-T003):** Added 6 voice config fields (azure_openai_realtime_deployment, api_version, realtime_voice, vad_threshold, max_voice_session_duration) with auto-disable logic in Pydantic v2 model_validator. Appended stubs to .env.example. Bicep: added gpt-4o-realtime-preview deployment (model v2025-04-01, capacity 1) with dependsOn sequencing.

**Live deployment verification:** azd up completed; deployed with mock_mode=false, voice_enabled=true, realtime_available=true. Resource group rg-vvoice, eastus2, Container Apps, live API working.

**Frontend deployment architecture:** Separate Container App (0.25 vCPU, 0.5Gi, 1-2 replicas), nginx reverse-proxies `/api/*` to backend (eliminates CORS), BACKEND_URL injected via envsubst at startup. WebSocket headers (Upgrade, Connection) configured for voice relay. New Bicep output AZURE_FRONTEND_URL.

**502 Bad Gateway fix:** Added `proxy_ssl_server_name on;` + `proxy_set_header Host $proxy_host;` to nginx. Azure Container Apps uses shared internal IPs + SNI for TLS routing; without SNI, connection reset. Lesson: always use proxy_ssl_server_name for inter-Container-App HTTPS.

**503 Realtime endpoint fix:** API path was wrong (`/openai/realtime/sessions` → correct: `/openai/v1/realtime/client_secrets`). Azure OpenAI had disableLocalAuth=true, blocking API key. Fixed with DefaultAzureCredential + API key fallback, auto-token-refresh. Bicep: disableLocalAuth=false re-enabled API key auth.

### ARCHIVED: GPT-4o Model Migration (2026-03-15)

**Migration:** Text gpt-4o → gpt-4.1 (v2025-04-14, eastus2 Standard). Realtime gpt-4o-realtime-preview → gpt-realtime (v2025-08-28, no "4.1-realtime" variant). API versions updated to 2025-04-01-preview. All changes to config.py + infra/main.bicep. Tests: 458 passed.

### 2026-03-15 — Fix Voice Transcript Config (Session Config Patch)

**Problem**

- Voice feature was live but transcripts never appeared in the UI.
- Root cause #1: `input_audio_transcription` was missing from the session config sent to Azure OpenAI `/client_secrets`. Without it, the Realtime API never emits `conversation.item.input_audio_transcription.completed` events — user speech is never transcribed.
- Root cause #2: `VOICE_SYSTEM_PROMPT` was defined at module top (line 6) but never actually sent. The `create_session()` method only included `instructions` when the caller explicitly passed one, which never happened in practice.

**Fix applied**

1. **`backend/app/services/azure/realtime.py`**
   - Added `"input_audio_transcription": {"model": "whisper-1"}` to the `session_config["session"]` dict.
   - Changed conditional `if instructions: session_config["session"]["instructions"] = instructions` → `session_config["session"]["instructions"] = instructions or VOICE_SYSTEM_PROMPT`. Now the system prompt is always sent.

2. **`backend/app/services/mock/realtime.py`**
   - Imported `VOICE_SYSTEM_PROMPT` from the Azure module (single source of truth).
   - Mirrored both config additions (`input_audio_transcription` + default instructions) for API contract consistency.
   - Stored config in `self._last_session_config` for test introspection.

**Verification:** 76 voice tests passing. Import checks clean for both Azure and mock services.

---

### 2026-04-09 — Phone Callback URL Fix (TLS Termination)

**Problem:** Inbound phone calls were failing at `answer_call()` with error "CallbackUri invalid" (400). The callback URL was being constructed from `request.base_url`, which inside Azure Container Apps resolves to an internal `http://` address. ACS (Azure Communication Services) requires HTTPS public URLs.

**Root cause:** Container Apps ingress performs TLS termination, so the backend sees `http://` requests from an internal address. The fix required extracting the public HTTPS URL from the forwarded headers set by the ingress.

**Solution implemented:**

1. Read `X-Forwarded-Proto` and `Host` headers from the incoming request (set by Container Apps ingress).
2. Reconstruct the public HTTPS callback URL as `https://{Host}/api/phone/callbacks`.
3. Added `PHONE_CALLBACK_BASE_URL` config setting as an explicit override (belt-and-suspenders approach).
4. Updated `backend/app/api/phone.py` to use reconstructed URL in `answer_call()`.

**Files changed:**
- `backend/app/api/phone.py` — callback URL reconstruction in phone event handler
- `backend/app/services/azure/phone.py` — helper function to extract public URL from headers
- Container env: `PHONE_CALLBACK_BASE_URL` set on `frontdoor-tlijy2xjo4fvg-backend`

**Verification:** Deployed to live. Simulated IncomingCall event via Event Grid. Call was answered successfully.

**Decision:** This pattern (read forwarded headers + explicit override config) should be used for any service needing to reconstruct a public callback URL in Container Apps or similar TLS-terminating environments.

**Commit:** 365271d

**Team Coordination:** Paired with Switch's frontend `session.update` data-channel implementation (parallel spawn 2026-03-15T01:53) for belt-and-suspenders transcription enablement. Backend config change ensures system prompt and transcription are always available; frontend change adds runtime safety net.

**Exercise Content Alignment:** Anvil updated all 8 labs and coach guide to reference this phone transcript streaming fix and real tool execution (commit 2669075). Hackathon participants now see voice and phone features as integrated into the wider 47 Doors architecture.

**Orchestration Log:** `.squad/orchestration-log/2026-03-15T01-53-tank.md`

### 2026-03-15 — GPT-4o → GPT-4.1 Model Migration

**Architecture decisions**

- Text model migrated from `gpt-4o` (deprecated 03/31/2026) to `gpt-4.1` version `2025-04-14`. Available in eastus2 with Standard SKU.
- Realtime/voice model migrated from `gpt-4o-realtime-preview` (deprecated 03/24/2026) to `gpt-realtime` version `2025-08-28`. There is NO `gpt-4.1-realtime` — the successor naming convention dropped the base model prefix.
- API version defaults updated from `2024-02-15-preview`/`2024-05-01-preview` to `2025-04-01-preview` for chat completions. Realtime API version was already `2025-04-01-preview`.
- Parameterized `realtimeModel` name in Bicep/ARM templates (was previously hardcoded as `gpt-4o-realtime-preview`). Future model swaps only require parameter changes.
- Other realtime models available in eastus2 as of this date: `gpt-realtime-mini` (2025-10-06, 2025-12-15), `gpt-realtime-1.5` (2026-02-23). Could be alternatives if cost/latency optimization needed.

**Key file paths**

- `infra/main.bicep` — `realtimeModel` param added; realtime resource uses parameterized name/version
- `infra/main.parameters.json` — `gpt-4.1` / `2025-04-14`
- `backend/app/core/config.py` — deployment default `gpt-4.1`, API version `2025-04-01-preview`
- `backend/app/services/azure/llm_service.py` — API version default `2025-04-01-preview`
- `.squad/decisions/inbox/tank-gpt41-migration.md` — full decision record

### 2026-03-20 — GPT-4o → GPT-4.1 Model Migration

**Architecture decisions**

- Text model migrated from `gpt-4o` (deprecated 03/31/2026) to `gpt-4.1` version `2025-04-14`. Available in eastus2 with Standard SKU.
- Realtime/voice model migrated from `gpt-4o-realtime-preview` (deprecated 03/24/2026) to `gpt-realtime` version `2025-08-28`. There is NO `gpt-4.1-realtime` — the successor naming convention dropped the base model prefix.
- API version defaults updated from `2024-02-15-preview`/`2024-05-01-preview` to `2025-04-01-preview` for chat completions. Realtime API version was already `2025-04-01-preview`.
- Parameterized `realtimeModel` name in Bicep/ARM templates (was previously hardcoded as `gpt-4o-realtime-preview`). Future model swaps only require parameter changes.
- Other realtime models available in eastus2 as of this date: `gpt-realtime-mini` (2025-10-06, 2025-12-15), `gpt-realtime-1.5` (2026-02-23). Could be alternatives if cost/latency optimization needed.

**Key file paths**

- `infra/main.bicep` — `realtimeModel` param added; realtime resource uses parameterized name/version
- `infra/main.parameters.json` — `gpt-4.1` / `2025-04-14`
- `backend/app/core/config.py` — deployment default `gpt-4.1`, API version `2025-04-01-preview`
- `backend/app/services/azure/llm_service.py` — API version default `2025-04-01-preview`
- `.squad/decisions/inbox/tank-gpt41-migration.md` — full decision record (merged to decisions.md 2026-04-08)

**Verification:** 447 tests passed, 97 skipped. Mock mode confirmed working. Session log: `.squad/log/2026-04-08T17-25-gpt41-migration.md`

### 2026-04-09 — ACS Phone Number Provisioning & Event Grid Webhook

**Phone number discovery**

- The `.env` referenced an `acs-47doors` resource, but it does NOT exist in subscription `b1ade9aa-...`. Only two ACS resources exist: `frontdoor-tlijy2xjo4fvg-acs` (rg-vvoice) and `cahack-adf7nmuxdcchc-acs` (rg-ca-hack).
- Phone number `+19132171946` was purchased on `frontdoor-tlijy2xjo4fvg-acs` — the already-deployed ACS resource. No resource switch needed.

**Container app environment variables**

- Set `ACS_PHONE_NUMBER=+19132171946` on `frontdoor-tlijy2xjo4fvg-backend`.
- Set `AZURE_ACS_CONNECTION_STRING` with the connection string for `frontdoor-tlijy2xjo4fvg-acs`.
- `AZURE_ACS_ENDPOINT` was already correctly set to `https://frontdoor-tlijy2xjo4fvg-acs.unitedstates.communication.azure.com`.

**Event Grid configuration**

- Created system topic `acs-events-topic` (type `Microsoft.Communication.CommunicationServices`, source: `frontdoor-tlijy2xjo4fvg-acs`, location: `global`).
- Created event subscription `incoming-call-webhook` filtering on `Microsoft.Communication.IncomingCall`, pointing to `https://frontdoor-tlijy2xjo4fvg-backend.jollypond-d33839e3.eastus2.azurecontainerapps.io/api/phone/incoming`.
- Event Grid webhook validation handshake succeeded automatically — confirms the backend's `/api/phone/incoming` endpoint correctly handles `SubscriptionValidationEvent`.

### 2026-04-09 — Phone Transcript Pipeline Fix (OpenAI Session Config)

**Root cause: duplicate transcription config**

- Live transcript page showed "Call connected" but NO transcripts appeared. Logs revealed OpenAI error: `unknown_parameter: 'session.output_audio_transcription'`.
- The `session.update` payload in `media_ws.py` had BOTH root-level `input_audio_transcription` / `output_audio_transcription` AND nested `audio.input.transcription` / `audio.output.transcription` configs.
- OpenAI Realtime API (direct WebSocket) only accepts the nested format under `audio.{input,output}.transcription`. The root-level params are invalid and cause the session config to be rejected.
- Removed the duplicate root-level config (lines 140-141 in media_ws.py). Session config now only sends the nested transcription params.

**Debugging process**

- Used `az containerapp logs show` with grep filters to find OpenAI error in live logs.
- Error appeared at 2026-04-09T04:15:07 UTC: `bridge: OpenAI error: {'type': 'invalid_request_error', 'code': 'unknown_parameter', 'message': "Unknown parameter: 'session.output_audio_transcription'."}`.
- Confirmed the deployed backend image timestamp matched recent deployment.
- Fixed by removing duplicate params, deployed via `azd deploy backend`, all tests passed.

### 2026-04-09 — Transcript Event Name Mismatch (Preview vs GA API)

**Root cause:** Commit 2669075 changed the transcript handler in `media_ws.py` from the preview event name (`response.audio_transcript.done`) to the GA name (`response.output_audio_transcript.done`). But our API version is still `2025-04-01-preview`, which sends the preview name. Events never matched → agent transcripts silently dropped.

**Fix (commit 297e7f7):** Changed the handler to accept BOTH preview and GA event names using `if t in (...)`. The delta ignore list already had both names. Forward-compatible — works on preview now and won't break when we upgrade to GA.

**Key lesson:** When an API has preview vs GA event name differences, always handle both names until the version pin is explicitly upgraded. The API version string in `config.py` is the source of truth for which wire format the server will actually send.

**Key lesson: OpenAI Realtime API session config format**

- For direct WebSocket (phone bridge), transcription config MUST be nested under `audio.input.transcription` and `audio.output.transcription`.
- Do NOT send `input_audio_transcription` or `output_audio_transcription` at the session root level.
- The WebRTC `/client_secrets` endpoint may accept different formats, but the direct WebSocket API enforces strict nesting.

**Verification results**

- `/api/phone/health` → `phone_available: true`, `mock_mode: false`, `phone_enabled: true`, latency 284ms.
- `/api/health` → all services up (LLM, ticketing, knowledge_base, session_store).
- Event Grid subscription provisioning state: `Succeeded`.
- Managed identity (`2eb87eef-7f9f-4855-a964-74f1c7af104f`) already has Contributor on the ACS resource (from Bicep).

**Gotchas**

- `az eventgrid system-topic event-subscription create` uses `--included-event-types`, NOT `--event-types` (the latter is for non-system-topic subscriptions).
- `az communication phonenumber list` requires `--connection-string` flag; resource-name-based listing uses `--comm-service-name` which is separate CLI syntax.
- ACS system topic must use `--location global` (ACS resources are global).
- If `.env` references an ACS resource name, always verify it actually exists in the subscription before using it. The `.env` had `acs-47doors` which was the portal display name, not the deployed resource name.

**Session logs**

- Orchestration log: `.squad/orchestration-log/2026-04-09T00-57-tank.md`
- Session log: `.squad/log/2026-04-09T00-57-phone-provisioning.md`

### 2026-04-09 — Phone CallbackUri Invalid Fix (Second Failure)

**Root cause:** After the SDK `StreamingTransportType` fix (a885b62), inbound calls still failed with `(400) The field CallbackUri is invalid`. Container logs showed this error on every call attempt from Sean's phone.

The issue: `callback_url = str(request.base_url).rstrip("/") + "/api/phone/callbacks"` in `backend/app/api/phone.py` constructs the callback URL from FastAPI's `request.base_url`. Inside Azure Container Apps, TLS is terminated at the ingress. The container sees `http://` scheme (not `https://`). ACS Call Automation requires a publicly-reachable HTTPS callback URL — the internal `http://` URL is rejected.

**Fix applied:**
1. `backend/app/api/phone.py` — Reconstruct public callback URL from `X-Forwarded-Proto` + `Host` headers (set by Container Apps ingress). Falls back to `request.base_url` only if headers are missing.
2. `backend/app/core/config.py` — Added `phone_callback_base_url` config field as an explicit override (belt-and-suspenders).
3. Set `PHONE_CALLBACK_BASE_URL=https://frontdoor-tlijy2xjo4fvg-backend.jollypond-d33839e3.eastus2.azurecontainerapps.io` as container env var.

**Verification:** Simulated IncomingCall event now fails with `(8523) Incoming Call Context is invalid` (expected for fake context) — no more CallbackUri error. Health check green. 100% traffic on latest revision.

**Critical pattern for Azure Container Apps:**
- `request.base_url` inside a Container App returns an internal `http://` URL, NOT the public `https://` URL.
- Any callback URL passed to external services (ACS, Event Grid, etc.) must be reconstructed from forwarded headers or configured explicitly.
- Azure Container Apps ingress sets `X-Forwarded-Proto` and preserves the `Host` header from the original request.

**Debugging sequence for phone failures:**
1. `az containerapp logs show` — look for the actual ACS SDK error (400 vs 8523 vs ImportError)
2. The error `The field CallbackUri is invalid` always means the URL scheme/format is wrong
3. Health check (`/api/phone/health`) does NOT test the answer_call path — it only verifies client initialization

**Commit:** 365271d — `fix(phone): use public HTTPS callback URL for ACS answer_call`

### 2026-04-09 — Silent Audio Fix (WebSocket Bridge for ACS→OpenAI)

**Problem:** Phone call to +19132171946 connected (call picked up, no more 503 or callback errors) but audio was completely silent — dead air in both directions.

**Root cause (two issues):**

1. **ACS media streaming could not authenticate to Azure OpenAI.** The `transport_url` in `MediaStreamingOptions` pointed directly to `wss://{openai}/openai/realtime?deployment=gpt-realtime`. But the OpenAI resource has `disableLocalAuth=true` (only Entra ID/token auth), the ACS resource has NO managed identity (`identity: null`), and there is no ACS→OpenAI RBAC role assignment. ACS simply could not open the WebSocket — silent failure.

2. **Callback handler rejected all events with 400.** ACS Call Automation sends CloudEvents format where `callConnectionId` is nested in the `data` field. The handler looked for it at the top level. Every callback (CallConnected, MediaStreamingStarted/Failed) was rejected with 400, so we never saw the `MediaStreamingFailed` event that would have diagnosed issue #1.

**Fix: Backend WebSocket bridge (`backend/app/api/media_ws.py`)**

Instead of ACS connecting directly to OpenAI (which requires ACS to have its own identity/auth), the backend now acts as a WebSocket relay:

```
PSTN Caller → ACS → WS [backend /ws/acs-media] → WS [Azure OpenAI Realtime API]
                         ↑ backend bridges audio, uses its own managed identity ↑
```

- New `media_ws.py` at route `/ws/acs-media`:
  - Accepts ACS media streaming WebSocket connection
  - Opens authenticated WebSocket to Azure OpenAI Realtime API using backend's managed identity (which already has the RBAC role)
  - Bridges audio bidirectionally (ACS AudioData → OpenAI input_audio_buffer.append, OpenAI response.audio.delta → ACS AudioData)
  - Sends session.update with PHONE_SYSTEM_PROMPT, voice config, VAD, tool definitions
  - Handles tool calls (analyze_and_route_query, check_ticket_status, etc.)
  - Supports barge-in (StopAudio on user speech)
- Updated `phone.py` service: `transport_url` now points to `wss://{hostname}/ws/acs-media` (derived from callback URL)
- Fixed `phone.py` API: callback handler parses CloudEvents (data.callConnectionId) with graceful fallback
- Registered `/ws` router in `main.py`

**Audio format compatibility:** ACS `PCM24_K_MONO` (24kHz, 16-bit, mono) maps directly to OpenAI Realtime `pcm16` (24kHz, 16-bit, mono). No conversion needed.

**Key architectural insight:** ACS media streaming's `transport_url` is a dumb WebSocket pipe. It has NO authentication mechanism. When the target requires auth (like Azure OpenAI with disableLocalAuth), a backend WebSocket bridge is required. This is also the pattern used in all official Azure samples.

**Files changed:**
- `backend/app/api/media_ws.py` (NEW) — WebSocket bridge
- `backend/app/services/azure/phone.py` — transport_url → backend WS
- `backend/app/api/phone.py` — CloudEvents callback parsing
- `backend/app/main.py` — /ws router registration
- `backend/tests/test_phone/test_phone_endpoints.py` — updated for resilient 200 responses

**Commit:** b2d7abc — `feat(voice): add WebSocket bridge for ACS-to-OpenAI audio relay`

**Deployed:** Revision `frontdoor-tlijy2xjo4fvg-backend--azd-1775699845` active. 447 tests pass.

### 2026-04-09 — SSE Transcript Streaming Endpoint

**What:** Added real-time transcript streaming so the frontend can display phone conversations as they happen. Three new components:

1. `backend/app/services/transcript_bus.py` — In-memory async pub/sub using `asyncio.Queue` per subscriber. Module-level singleton (`transcript_bus`). Auto-drops slow subscribers when queue (256) overflows.
2. `backend/app/api/transcripts.py` — SSE endpoint at `GET /api/phone/transcripts/stream`. Returns `text/event-stream` with 15s keepalive. Uses `StreamingResponse`.
3. Wired into `media_ws.py` — publishes `call_started`, `user_speech`, `agent_speech`, `tool_call`, `call_ended` events as they flow through the OpenAI Realtime bridge.

**Naming collision fixed:** OpenAI's `response.function_call_arguments.done` has a `call_id` field (function call ID). Renamed to `fn_call_id` in the bridge to avoid shadowing the phone `call_id` (UUID).

**SSE test pattern:** Testing infinite SSE streams with httpx hangs because the client tries to drain the body on context exit. Solution: test the async generator directly with `AsyncMock` request + `asyncio.wait_for` wrapper + task-based publish/consume pattern.

**Key files:**
- `backend/app/services/transcript_bus.py` — pub/sub bus
- `backend/app/api/transcripts.py` — SSE endpoint
- `backend/app/api/media_ws.py` — event publishing hooks
- `backend/tests/test_transcripts/test_transcript_bus.py` — 8 tests

**API contract (shared with Switch for frontend):**
```
GET /api/phone/transcripts/stream → text/event-stream
Events: call_started, user_speech, agent_speech, tool_call, call_ended
```

**Commit:** 66ff243 — `feat(voice): add SSE endpoint for live phone transcript streaming`

**Deployed:** 455 tests pass. SSE endpoint live at production URL (200, text/event-stream).

### 2026-04-09 — Fix Phone Bridge: Transcript Streaming + Real Tool Execution

**Two bugs found and fixed:**

1. **Agent speech transcripts missing from SSE stream:**
   - `media_ws.py` listened for `response.audio_transcript.done` (preview API event name)
   - GA Realtime API (api-version `2025-04-01-preview`) sends `response.output_audio_transcript.done`
   - Agent speech events were silently dropped → never published to `TranscriptBus`
   - Fix: updated event handler to `response.output_audio_transcript.done`
   - Also added `response.output_audio_transcript.delta` to noise list (kept old name for compat)
   - Added subscriber-count logging on every publish for diagnosability

2. **Phone tool calls returned hardcoded mock data (no real tickets/KB):**
   - `AzureRealtimeService.execute_tool()` had stub implementations for all 4 tools
   - `analyze_and_route_query` returned `TKT-IT-<random>` without creating a real ticket
   - `search_knowledge_base` returned one hardcoded article regardless of query
   - `escalate_to_human` returned fake escalation ID without creating a ticket
   - Fix: wired all tools to real services via lazy import from `dependencies.py`:
     - `analyze_and_route_query` → `llm_service.classify_intent()` + `ticket_service.create_ticket()`
     - `check_ticket_status` → `ticket_service.get_ticket_status()`
     - `search_knowledge_base` → `knowledge_service.search()`
     - `escalate_to_human` → `ticket_service.create_ticket()` with URGENT priority
   - Error handling wraps all tool execution; failures return error string to AI model

**Key lesson:** Realtime API GA changed event names from preview. `response.audio_transcript.done` → `response.output_audio_transcript.done`. Always verify event names against the deployed api-version.

**Key lesson:** `QueryResult.department_suggestion` (not `.department`) is the field name for the classified department. It's a `Department` enum already — no string conversion needed.

**Files changed:**
- `backend/app/api/media_ws.py` — fixed event name, added logging
- `backend/app/services/azure/realtime.py` — replaced mock tool stubs with real service calls

**Tests:** 455 pass (mock service unchanged — tests still use MockRealtimeService)
**Deployed:** `azd deploy backend` SUCCESS, SSE keepalive confirmed, all services healthy.

### 2026-03-16 — Nginx SSE Proxy Buffering Fix

**Problem:** Live transcript page (`/live`) showed "Call connected" but no transcript text. SSE events from `/api/transcripts/stream` were buffered by nginx and never reached the browser in real time.

**Root cause:** The single `/api/` location block used `Connection "upgrade"` (WebSocket header) and had no `proxy_buffering off`. Nginx buffered the entire SSE response, so `text/event-stream` events piled up instead of streaming through. The backend's `X-Accel-Buffering: no` header was insufficient without explicit `proxy_buffering off` in the nginx config.

**Fix:** Added a dedicated `location /api/transcripts/stream` block BEFORE the general `/api/` block with:
- `proxy_buffering off` + `proxy_cache off` — events stream immediately
- `proxy_set_header Connection ""` — SSE needs keep-alive, not WebSocket upgrade
- Same proxy_pass, SSL, and forwarding headers as the main block

The existing `/api/` block with `Connection "upgrade"` remains intact for WebSocket support (`/api/realtime/ws/`).

**Key lesson:** SSE and WebSocket need different nginx proxy settings. WebSocket needs `Connection "upgrade"` + `Upgrade $http_upgrade`. SSE needs `Connection ""` (keep-alive) + `proxy_buffering off`. When a backend serves both, use separate location blocks with the more-specific SSE path first (nginx longest-prefix match).

## Learnings

### 2026 — Azure OpenAI Realtime API schema varies by endpoint (phone bridge transcript fix)

**Authoritative fact — store this.** The Azure OpenAI Realtime API uses **two different session.update schemas** depending on which endpoint you connect to:

| Endpoint | api-version | Schema |
|---|---|---|
| wss://…/openai/realtime?api-version=2025-04-01-preview&deployment=gpt-realtime (direct WS — ACS phone bridge) | 2025-04-01-preview | **FLAT** — top-level voice, input_audio_format, output_audio_format, input_audio_transcription |
| /openai/v1/realtime/calls (WebRTC — browser voice) | GA | **NESTED** — audio: { input: {...}, output: {...} } with transcription sub-object |

If you send the wrong shape you get an **exact error signature** — look for this in the container logs:

```
{'type': 'invalid_request_error', 'code': 'unknown_parameter',
 'message': "Unknown parameter: 'session.audio'.", 'param': 'session.audio'}
```

When the direct-WS path silently rejects session.audio, whisper-1 never runs on caller audio, no conversation.item.input_audio_transcription.* events fire, and caller transcripts are empty — even though agent speech still transcribes fine (because response.audio_transcript.done is independent of the input-transcription config).

**The trap:** A stored memory previously claimed flat fields cause unknown_parameter errors. That was true — but only for the *WebRTC* endpoint. Do NOT generalize the schema of one endpoint to the other. Always check which endpoint media_ws.py is hitting before changing the session shape.

**Fix applied in backend/app/api/media_ws.py:** replaced the nested audio:{input,output} block with flat fields (voice, input_audio_format, output_audio_format, input_audio_transcription) for the phone bridge session.update. Also fixed AttributeError: 'ClientConnection' object has no attribute 'closed' in the finally block (newer websockets library removed .closed — wrap close in try/except instead of gating on it). Added temp diagnostic logging marked "# TEMP_DIAG — revert after verification".

Tests: 461 passed, 97 skipped. No test pinned the old nested shape.

**Production verification (2026-04-21):**
- Deployed as revision azd-1776792457 and tested with phone number +1 (913) 217-1946
- Caller speech transcripts ("conversation.item.input_audio_transcription.completed") now firing correctly on `/live` page
- Agent speech transcripts ("response.audio_transcript.done" / "response.output_audio_transcript.done") already worked
- Fix confirmed by msftsean (Sean) — phone→/live caller transcripts rendering as expected
- TEMP_DIAG logging reverted in commit e687215, pushed, and redeployed successfully (30s deploy)
- Learnings documented in `.squad/skills/azure-realtime-api-schema/SKILL.md` and decision drop at `.squad/decisions/inbox/tank-phone-bridge-verified.md`
