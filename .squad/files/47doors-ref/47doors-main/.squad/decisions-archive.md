# Squad Decisions

## Active Decisions

### Model Selection Directive
**Timestamp:** 2026-03-13T13-09-59  
**Authority:** User (msftsean via Copilot)  
**Decision:** 
- Code-writing agents (Tank, Switch, Mouse, Neo): use `claude-sonnet-4.6`
- Non-code agents (Scribe, documentation, evals, Morpheus when not reviewing): use `claude-haiku-4.6`

**Rationale:** Optimize for cost vs. quality based on task type. Code work requires full Sonnet capability; administrative/documentation work can use faster Haiku model.

### Azure Resources Ready for Live Testing
**Timestamp:** 2026-03-13T17:34  
**Authority:** User (msftsean via Copilot)  
**Decision:** Azure resources provisioned and ready for live voice testing.
- **Resource Group:** `rg-47doors-voice` (eastus2)
- **Resource Name:** `oai-47doors-voice`
- **Deployments:** `gpt-4o` + `gpt-4o-realtime`

**Rationale:** User directive to plan for live Azure testing, not just mock mode. Infrastructure is in place and ready for Phase 3+ endpoint validation.

### Azure-First Deployment Strategy
**Timestamp:** 2026-03-13T18:46:00Z  
**Authority:** User (msftsean via Morpheus)  
**Decision:** Spec update to make Azure Container Apps the primary deployment target.

- **VFR-026**: Azure Container Apps via `azd up` is PRIMARY
- **VFR-027**: Local dev as secondary path via `uvicorn`
- **VFR-028**: No code changes needed between deployments
- **VFR-029**: Health checks work identically in both environments

**Rationale:** User directive — production and demo environments should run on Azure, not locally. Mock mode repositioned as development/testing tool.

### Phase 1 Setup — Voice Config, Env, Bicep
**Timestamp:** 2026-03-14  
**Authority:** Tank (Backend Dev)  
**Decision:** Voice configuration strategy for `backend/app/core/config.py`

**Key Decisions:**
- Used Pydantic v2 `model_validator(mode="after")` for voice validation (consistent with codebase v2.5+ usage)
- Voice config fields:
  - `voice_enabled` (default `True`): Kill switch, disabled when `azure_openai_realtime_deployment == ""` AND `mock_mode == False`
  - `azure_openai_realtime_deployment` (default `""`): Empty value auto-disables voice in prod mode
  - `azure_openai_realtime_api_version` (default `"2025-04-01-preview"`): Realtime endpoint version
  - `realtime_voice` (default `"alloy"`): Azure voice selection
  - `realtime_vad_threshold_ms` (default `500`): Voice activity detection threshold
  - `max_voice_session_duration` (default `600`): Session timeout (10 min)

- `.env.example`: Added `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview` as stub
- `infra/main.bicep`: Added `openAiRealtimeDeployment` resource with:
  - `dependsOn: [openAiDeployment]` to serialize operations (avoid rate-limit throttling)
  - Capacity: 1 TPM-unit (minimal, scale manually as needed)
  - Output: `AZURE_OPENAI_REALTIME_DEPLOYMENT` for azd auto-wiring

**Rationale:** Phase 1 unblocks deployment configuration. Mock mode enables local development; validator logic ensures voice is disabled in production without credentials.

### Voice Data Model Architecture
**Timestamp:** 2026-03-13  
**Authority:** Tank (Backend Dev)  
**Decision:** Additive-only model strategy for voice entities

**Key Decisions:**
1. **File Organization**
   - New voice models in `backend/app/models/voice_schemas.py` and `backend/app/models/voice_enums.py` (not appended to existing files)
   - Reduces merge conflicts with parallel feature work
   - Keeps existing `schemas.py` lean (430+ lines already)

2. **Data Model Integration**
   - `VoiceMessage.input_modality: Literal["voice"]` acts as discriminator (text/voice coexist in shared history)
   - Cheaper than union types or separate history stores
   - Aligns with spec VFR-010 (shared transcript) + Constitution Principle IV (session continuity)
   - `VoiceState.transcript` is append-only with `max_length=100` (matches `Session.conversation_history` cap pattern)

3. **Auth & Persistence**
   - No new auth model — reuse `Session.session_id: UUID` as voice↔text join key
   - Zero schema migration required; UUID index already exists
   - Trivially maps to future persistence layer (Cosmos DB): `WHERE session_id = ?`

4. **Tool Call Models**
   - `ToolCallRequest` / `ToolCallResponse` marked explicitly transient ("never persisted" in docstring)
   - Prevents PII leaks from tool arguments/results into audit logs before PII-filter pass
   - Aligns with Constitution Principle I (pipeline integrity)

**Rationale:** Additive strategy reduces friction with parallel work. Discriminator pattern is simpler and aligns with existing session model. Explicit transience markers document the PII-safety constraint for future implementers.

### Azure Static Web Apps Auth for Runbook Site
**Timestamp:** 2026-03-14  
**Authority:** Switch (Frontend Dev)  
**Decision:** Use Azure Static Web Apps (SWA) with Azure AD (Microsoft Entra ID) authentication for docs runbook site

**Key Decisions:**
- **Identity provider:** Azure AD only (Microsoft login)
- **Auth enforcement:** All routes require `authenticated` role; 401 auto-redirects to `/.auth/login/aad`
- **User display:** `/.auth/me` endpoint surfaced in nav bar; degrades gracefully on local dev
- **Blocked providers:** GitHub, Twitter (return 404)

**Affected Files:**
- `docs/staticwebapp.config.json` — SWA route rules and auth config
- `docs/index.html` — `.nav-auth` bar + `/.auth/me` JS
- `.github/workflows/deploy-docs-swa.yml` — CI/CD deployment
- `docs/AZURE_SWA_SETUP.md` — Operator setup guide

**Rationale:** EDU/Microsoft audience context. SWA built-in auth requires no app-level middleware. Restricts runbook access (internal tooling, demo sequences) to authenticated Microsoft accounts. Local dev parity via graceful `/.auth/me` fallback.

### Azure OpenAI Managed Identity Authentication
**Timestamp:** 2026-03-13T23:00Z  
**Authority:** Anvil (Production Fix)  
**Decision:** Use system-assigned managed identity for Azure OpenAI authentication instead of API keys

**Key Decisions:**
- **Backend Authentication:**
  - `AzureRealtimeService` uses `DefaultAzureCredential` from `azure-identity` for token-based auth
  - API key support retained as fallback for local development (optional parameter)
  - Token auto-refresh before expiration (checks `expires_on` timestamp)
  
- **Infrastructure Changes (`infra/main.bicep`):**
  - Set `disableLocalAuth: true` on Azure OpenAI resource (enforce managed identity)
  - Removed `azure-openai-api-key` secret from backend container app
  - Added `identity: { type: 'SystemAssigned' }` to backend container app
  - Created role assignment: `Cognitive Services OpenAI User` role for backend managed identity
  - Removed `AZURE_OPENAI_API_KEY` environment variable injection

- **Error Handling:**
  - Status-code-specific error messages (401: auth failed, 403: missing role, 404: deployment not found, 5xx: service unavailable)
  - Network errors surfaced with endpoint URL for debugging
  - All errors wrapped in `VoiceUnavailableError` with detailed context

- **Configuration:**
  - `azure_openai_api_key` now optional in `config.py` (description updated)
  - `dependencies.py` passes `api_key=None` when unset, triggering managed identity path
  - Mock mode unaffected (no Azure credentials required)

**Affected Files:**
- `backend/app/services/azure/realtime.py` — Token-based auth with credential refresh
- `backend/app/core/config.py` — Made API key optional
- `backend/app/core/dependencies.py` — Pass None for API key when unset
- `infra/main.bicep` — System-assigned identity + RBAC role assignment

**Rationale:** Deployed frontend was hitting 503 errors because Azure OpenAI had `disableLocalAuth: true` (API key auth rejected with 403). Managed identity is Azure best practice for container apps — no secrets in config, auto-rotated tokens, and RBAC-controlled access. API key fallback preserves local dev workflow without Azure credentials.

### Realtime API Authentication Fix — RESOLVED
**Timestamp:** 2026-03-14  
**Authority:** Anvil (Production Fix)  
**Status:** ✅ Complete  
**Decision:** Re-enabled API key auth + implemented async DefaultAzureCredential with fallback

**Problem (Tank's Initial Diagnosis):**
- Frontend getting 503 when calling `POST /api/realtime/session`
- Root cause: Wrong Azure OpenAI Realtime API endpoint URL → 404 (fixed by Tank)
- Secondary issue: Azure OpenAI resource has `disableLocalAuth: true` → 403 (blocking token acquisition)

**Anvil's Solution:**

1. **Bicep (infra/main.bicep)**
   - Set `disableLocalAuth: false` on Azure OpenAI resource to re-enable API key authentication
   - Verified property takes effect with `azd provision`

2. **Backend Service (backend/app/services/azure/realtime.py)**
   - Integrated `DefaultAzureCredential` from `azure-identity` library
   - Implemented async-aware credential refresh (checks `expires_on` before use)
   - API key remains as fallback for local development (optional parameter)
   - Enhanced error handling with status-code-specific messages:
     - 401: Authentication failed
     - 403: Missing Cognitive Services OpenAI User role
     - 404: Deployment not found
     - 5xx: Service unavailable

3. **Configuration (backend/app/core/config.py)**
   - Made `azure_openai_api_key` optional in Settings
   - `dependencies.py` passes `api_key=None` when unset, triggering managed identity path

**Result:**
- ✅ 503 errors eliminated
- ✅ Realtime session endpoint fully operational
- ✅ 76 voice tests passing
- ✅ Commit: `c44b389` ("feat(voice): Re-enable API key auth, add async DefaultAzureCredential with fallback")
- ✅ Pushed to main

**Affected Files:**
- `infra/main.bicep` — Re-enabled API key auth
- `backend/app/services/azure/realtime.py` — Added DefaultAzureCredential + fallback
- `backend/app/core/config.py` — Made API key optional
- `backend/app/core/dependencies.py` — Pass None when unset
- `tests/voice/*.py` — 76 tests green

### Voice Transcript Session Config
**Timestamp:** 2026-03-15  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Applied

**Problem:** Voice transcripts never appeared in the UI despite deployment. Two configuration gaps in Realtime API session config prevented transcription.

**Decision:**

1. **Enable `input_audio_transcription` in session config**
   - Added `"input_audio_transcription": {"model": "whisper-1"}` to the session config sent to Azure OpenAI's `/client_secrets` endpoint
   - Without this field, Azure's Realtime API does not emit `conversation.item.input_audio_transcription.completed` events — user speech is never converted to text

2. **Default instructions to `VOICE_SYSTEM_PROMPT`**
   - Changed `create_session()` to always include instructions, defaulting to `VOICE_SYSTEM_PROMPT` when not explicitly provided
   - The prompt was defined at module top but never wired in; without it, voice model operates with no PII redaction rules, ticket conventions, or conversational guidance

3. **Mock service parity**
   - Mirrored both changes in `MockRealtimeService` for API contract consistency
   - Mock imports `VOICE_SYSTEM_PROMPT` from Azure module (single source of truth)

**Affected Files:**
- `backend/app/services/azure/realtime.py` — Session config + instructions default
- `backend/app/services/mock/realtime.py` — Matching config for test parity

**Verification:** 76 voice tests passing. Import validation clean for both services.

### Frontend session.update for Transcription Enablement
**Timestamp:** 2026-03-15  
**Authority:** Switch (Frontend Dev)  
**Status:** ✅ Applied

**Problem:** Azure OpenAI Realtime API requires `input_audio_transcription` to be explicitly enabled. Without it, API produces responses but never emits transcription events.

**Decision:** Send a `session.update` event via WebRTC data channel (`dc.onopen`) immediately after it opens, enabling `input_audio_transcription` with `whisper-1`.

**Belt-and-Suspenders Approach:**
- **Backend (Tank):** Includes `input_audio_transcription` in initial session config
- **Frontend (Switch):** Sends `session.update` through data channel as safety net
- Both paths are idempotent — redundant messages cause no errors

**Side Effect:** Moved `dispatch({ type: 'LISTENING' })` from `pc.onconnectionstatechange` into `dc.onopen`. Data channel being open is the actual prerequisite for event exchange — semantically more correct.

**Affected Files:**
- `frontend/src/hooks/useVoice.ts` — Added `dc.onopen` handler

**Verification:** TypeScript compiles cleanly. Code review passed.

### Phone Call-In Feature via Azure Communication Services (ACS)
**Timestamp:** 2026-03-15  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Applied  

**Decision:** Implement inbound PSTN call support via ACS Call Automation, bridging phone calls to the same Azure OpenAI GPT-4o Realtime deployment and 4-tool pipeline used by browser voice.

**Key Decisions:**
1. **ACS Resource Always Provisioned** — No conditional provisioning in Bicep (unlike initial spec suggestion). Matches existing codebase pattern for Cosmos DB and AI Search. Mock mode handled in application layer via `MOCK_MODE` env var. Resource cost negligible when unused.

2. **Mock Service Synchronous** — `MockPhoneService` methods are sync (not async) intentionally, matching test pattern. API layer uses `inspect.isawaitable` helper to handle both sync mocks and async production services transparently.

3. **Auth Strategy:**
   - **Production:** Use `connection_string` from Key Vault; fall back to managed identity via `ManagedIdentityCredential`
   - **Local dev:** Set `AZURE_ACS_CONNECTION_STRING` in `.env` to use connection string auth
   - **Role assignment:** `Contributor` role for backend container app's system-assigned managed identity

4. **Media Streaming Architecture** — Mirrors browser WebRTC approach: backend never touches audio, Azure OpenAI Realtime handles ASR/TTS/tool calling via `MediaStreamingOptions` with `WEBSOCKET` transport to `wss://` Realtime endpoint.

5. **Pydantic v2 Constraint** — Only one `@model_validator(mode="after")` per class allowed. Combined voice and phone auto-disable logic into single `_auto_disable_features` validator.

6. **Event Grid Dual Event Type Names** — ACS subscription validation uses both `Microsoft.EventGrid.SubscriptionValidationEvent` AND `Microsoft.EventGrid.SubscriptionValidated`. Webhook handles both for robustness.

**Affected Files:**
- `infra/main.bicep` — ACS resource, secret, role assignment
- `backend/app/core/config.py` — Phone settings + merged validator
- `backend/app/services/interfaces.py` — PhoneServiceInterface ABC
- `backend/app/models/phone_schemas.py` — Phone models
- `backend/app/services/azure/phone.py` — Production service
- `backend/app/services/mock/phone.py` — Sync mock service
- `backend/app/api/phone.py` — Endpoints

**Rationale:** ACS Call Automation bridges PSTN calls seamlessly to the same 4-tool pipeline, maintaining Constitutional Principle I (pipeline integrity) across modalities. Synchronous mock service pattern enables early test-first development while Tank builds the service. Always-provisioned resource aligns with existing codebase patterns.

### Phone Test Suite Design
**Timestamp:** 2026-03-19  
**Authority:** Mouse (Tester)  
**Status:** Proposed  

**Decision:** Test suite design for phone call-in feature before Tank implements the service. Defines interface contracts.

**Key Test Decisions:**
1. **No E.164 Validation at Schema Level** — Spec defines `caller_id: str` with no format constraint. ACS can deliver calls with `caller_id = "Anonymous"` for blocked/private numbers. Tests verify non-E.164 values are accepted.

2. **Empty JSON Array is an Error** — Empty `[]` body on `POST /api/phone/incoming` should return 400 or 422 (semantically meaningless for Event Grid webhook).

3. **Unknown Event Types Handled Gracefully** — Unknown Call Automation event types should not produce 5xx; endpoint logs and returns 200 or 400.

4. **Lazy Imports in Tests** — Schema and service tests use lazy imports inside test methods so ImportError occurs at execution (not collection). Allows test suite to run even when Tank's modules don't exist yet.

5. **Synchronous TestClient Only** — Phone endpoints are synchronous (no WebSocket, no streaming). Use `TestClient` (not `AsyncClient`) for simplicity.

**Test Coverage:**
- `test_phone_schemas.py` — 5 Pydantic models, valid/invalid construction, edge cases
- `test_phone_service.py` — Mock service contracts, concurrency isolation
- `test_phone_endpoints.py` — Three endpoints via TestClient

**Rationale:** TDD approach (test first, implementation follows) unblocks Tank and ensures interface stability before implementation. Lazy imports keep test suite runnable during parallel development. Explicit decisions about caller_id and event types prevent rework.

### Workshop Site Architecture Decision
**Timestamp:** 2026-03-19  
**Authority:** Switch (Frontend Dev)  
**Status:** ✅ Applied  

**Decision:** Create standalone workshop companion site with Microsoft Fluent 2 design system at `workshop-site/`.

**Key Decisions:**
1. **Visual Design** — Microsoft Fluent 2 principles (generous whitespace, calm typography, restrained color). Primary: Microsoft blue (#0078D4), accent: IU crimson (#990000) sparingly. No gradients, no flashy animations.

2. **Content Structure** — 10 standalone tabs (each deep-linkable, complete narrative). Tab topics: Overview, Problem (47 Doors), Chatbots→Agents, Trust & Boundaries, Architecture, Voice & Accessibility, Demo Walkthrough, Responsible AI, Reuse, Your First Agent.

3. **Technical Stack** — React 18 + TypeScript 5 + Vite 5 + Tailwind CSS 3.4+. No external component libraries (lightweight). Heroicons only.

4. **Accessibility** — Keyboard navigable tabs, semantic HTML, ARIA labels, WCAG AA 4.5:1 contrast minimum, accessible SVG diagrams.

5. **Component Architecture** — Reusable components (TabNavigation, CollapsibleNotes, CalloutCard, DiagramSVG). 10 separate tab files in `src/tabs/` for maintainability.

6. **Deployment** — Azure Static Web Apps (SWA) deployment target (per user directive 2026-03-19).

**Affected Files:** Entire `workshop-site/` directory structure.

**Rationale:** Portable workshop companion for live presentations and async self-paced learning. Calm, institutional style reinforces "architecture lesson, not product pitch" framing. Tab structure enables non-linear navigation during live demos while supporting linear walkthrough. Interactive "Your First Agent" exercise makes constitutional design pattern concrete. Accessibility modeling aligns with 47 Doors voice feature philosophy.

### User Directive: Workshop Site Azure SWA Deployment
**Timestamp:** 2026-03-19T14:20:00Z  
**Authority:** User (msftsean via Copilot)  
**Decision:** Workshop site deployment target is Azure Static Web Apps (SWA).

**Rationale:** Aligns with existing SWA auth decision for docs/runbook site. User directive captured for team memory.

### GPT-4o → GPT-4.1 Model Migration
**Timestamp:** 2026-03-20  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Applied  

**Decision:** Migrate from deprecated GPT-4o models to GPT-4.1 (text) and gpt-realtime (voice) across infrastructure, backend config, and tests.

**Background:** Both GPT-4o models deployed to Azure were deprecated:
- `gpt-4o` version `2024-05-13` — deprecated 03/31/2026
- `gpt-4o-realtime-preview` version `2024-12-17` — deprecated 03/24/2026

**Model Selection (eastus2 availability):**
- **Text Model:** `gpt-4o` → `gpt-4.1` (version `2025-04-14`, Standard SKU)
- **Realtime/Voice Model:** `gpt-4o-realtime-preview` → `gpt-realtime` (version `2025-08-28`, GlobalStandard SKU)
- **Note:** No `gpt-4.1-realtime` model exists; naming convention for realtime dropped base model prefix
- **Alternative realtime models available in eastus2:** `gpt-realtime-mini` (2025-10-06, 2025-12-15), `gpt-realtime-1.5` (2026-02-23)

**API Version Updates:**
- Chat completions: `2024-02-15-preview` / `2024-05-01-preview` → `2025-04-01-preview`
- Realtime API version: already `2025-04-01-preview` (unchanged)

**Infrastructure Changes:**
- `infra/main.bicep` — Parameterized `realtimeModel` name (was hardcoded); applied new model versions
- `infra/main.parameters.json` — Model `gpt-4.1`, version `2025-04-14`
- Backend config defaults updated to new model names and API versions

**Test Updates:**
- `backend/tests/conftest.py` — `AZURE_OPENAI_DEPLOYMENT` from `"gpt-4o"` → `"gpt-4.1"`
- `backend/tests/test_voice/test_config.py` — Settings fixtures updated (2 occurrences)
- `backend/tests/test_voice/test_models.py` — RealtimeSessionResponse fixtures updated (2 occurrences)
- `backend/tests/test_gpt4o_evals.py` — Deployment + API version defaults updated (2 occurrences)

**Verification:** 447 tests passed, 97 eval tests skipped (require real Azure credentials). Mock mode confirmed working.

**Rationale:** GPT-4o retirement deadline drives immediate action. GPT-4.1 is direct successor with same capability tier. `gpt-realtime` is production GA successor to preview realtime model. Parameterized infrastructure enables future model swaps without code changes. Test updates ensure mock mode and fixture-driven configuration remain compatible.

### ACS Phone Number Configuration & Event Grid Webhook
**Timestamp:** 2026-04-09T00:57:00Z  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Implemented  

**Decision:** Configure purchased phone number `+19132171946` on the existing deployed ACS resource (`frontdoor-tlijy2xjo4fvg-acs`) with Event Grid webhooks for call handling.

**Background:** 
- User purchased phone number `+19132171946` 
- `.env` referenced non-existent resource `acs-47doors`
- Phone was actually purchased on the already-deployed `frontdoor-tlijy2xjo4fvg-acs`

**Configuration Applied:**
1. **Container App Environment Variables** (on `frontdoor-tlijy2xjo4fvg-backend`):
   - `ACS_PHONE_NUMBER=+19132171946`
   - `AZURE_ACS_CONNECTION_STRING` — connection string for `frontdoor-tlijy2xjo4fvg-acs`
   - `AZURE_ACS_ENDPOINT` — already correct (`https://frontdoor-tlijy2xjo4fvg-acs.unitedstates.communication.azure.com`)

2. **Event Grid System Topic** (`acs-events-topic`):
   - Type: `Microsoft.Communication.CommunicationServices`
   - Source: `frontdoor-tlijy2xjo4fvg-acs`
   - Location: `global`

3. **Event Grid Subscription** (`incoming-call-webhook`):
   - Event filter: `Microsoft.Communication.IncomingCall`
   - Webhook endpoint: `https://frontdoor-tlijy2xjo4fvg-backend.jollypond-d33839e3.eastus2.azurecontainerapps.io/api/phone/incoming`
   - Validation: ✅ Succeeded

**Verification:**
- `/api/phone/health` → `phone_available: true`, `phone_enabled: true`
- All backend services operational
- Event Grid subscription state: `Succeeded`
- Managed identity already has Contributor role on ACS resource (from Bicep)

**Team Impact:**
- **Switch (Frontend):** Phone call-in feature is now live. Incoming calls to `+1 (913) 217-1946` will trigger Event Grid → backend webhook pipeline.

**Infrastructure Note:**
Event Grid resources created via CLI. Recommend migrating to `infra/main.bicep` for IaC reproducibility.

**Rationale:** No need to create/switch to a separate ACS resource. Phone was purchased on the already-deployed instance. Event Grid webhooks enable the backend to receive and process incoming calls through the existing 4-tool pipeline (same as voice via WebRTC).

### ACS SDK v1.5.0 Migration: MediaStreamingTransportType → StreamingTransportType
**Timestamp:** 2026-04-09T01:20Z  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Resolved  

**Problem:** Inbound PSTN calls to `+19132171946` were silently failing. No answer, no error logs. Root cause: Azure Communication Services SDK v1.5.0 renamed `MediaStreamingTransportType` → `StreamingTransportType`. The production container had pinned `>=1.4.0`, allowing v1.5.0 to install. When an inbound call arrived, the answer-call path imported the old enum name, causing `ImportError` at runtime.

The health endpoint reported green because it only tests client initialization, not the media streaming code path where the enum is used.

**Decision:** Use `StreamingTransportType` for `azure-communication-callautomation >= 1.5.0`.

**Changes:**
- **File:** `backend/app/services/azure/phone.py`
  - Updated import from `MediaStreamingTransportType` → `StreamingTransportType`
  - Enabled bidirectional audio with PCM24K mono format (per Realtime API spec)
- **Bicep:** Version constraint remains flexible; Team should review Azure SDK changelogs before minor-version bumps

**Verification:**
- ✅ All 447 backend tests pass
- ✅ Commit: `a885b62`
- ✅ Deployed via `azd deploy`
- ✅ Phone calls now answered successfully

**Future Guidance:**
- Monitor Azure SDK release notes for API surface changes in communication services SDKs

### OpenAI Realtime API Session Configuration Format
**Timestamp:** 2026-04-09T00:30:49Z  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Resolved  

**Problem:** Live transcript page (`/live`) showed no user_speech or agent_speech events despite SSE connection working. Root cause: OpenAI Realtime API direct WebSocket rejected session config with `unknown_parameter` error on `output_audio_transcription`.

The `session.update()` payload in `media_ws.py` contained DUPLICATE transcription configurations:
- Root-level: `input_audio_transcription`, `output_audio_transcription` (invalid for direct WebSocket)
- Nested: `audio.input.transcription`, `audio.output.transcription` (valid)

**Decision:** When configuring Azure OpenAI Realtime API sessions for phone bridge (direct WebSocket):
- Use ONLY the nested transcription config under `audio.input.transcription` and `audio.output.transcription`
- Do NOT send `input_audio_transcription` or `output_audio_transcription` at the session root level
- The REST `/client_secrets` API may accept different formats — if phone bridge switches to REST endpoint in future, validate config format against that specific API's schema

**Changes:**
- **File:** `backend/app/api/media_ws.py` (session.update payload, lines 140-141)
- Removed 2 invalid root-level transcription config lines
- Kept only valid nested transcription config
- **Commit:** `37425e6` (fix(voice): remove duplicate transcription config)

**Verification:**
- ✅ Backend deployed successfully
- ✅ All tests pass
- ✅ Session config now accepted by OpenAI Realtime API (no unknown_parameter error)

**Learning:** OpenAI's direct WebSocket API (phone bridge) and REST `/client_secrets` API accept DIFFERENT session configuration formats. Direct WebSocket strictly enforces nested structure under `audio.input` and `audio.output`.
- Consider tighter version pinning (e.g., `~=1.5.0` or `>=1.5.0,<2.0`) for ACS packages to prevent surprise breakage
- Ensure health checks cover all code paths (e.g., media streaming endpoints)

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction


# Decision: SSE Transcript Streaming Architecture

**Timestamp:** 2026-04-09  
**Author:** Tank (Backend Dev)  
**Status:** Implemented & Deployed

## Decision

Added server-sent events (SSE) endpoint at `GET /api/phone/transcripts/stream` for real-time phone call transcript streaming to the frontend.

## Architecture

- **In-memory pub/sub** (`TranscriptBus`) — no external dependencies, no persistence. Each SSE client gets its own `asyncio.Queue(maxsize=256)`. Slow clients are auto-dropped.
- **Event types:** `call_started`, `user_speech`, `agent_speech`, `tool_call`, `call_ended` — matches the shared API contract with Switch.
- **Integration point:** Events published from `media_ws.py` WebSocket bridge as they flow through the OpenAI Realtime session.
- **Router mounted** under `/api/phone` prefix alongside existing phone endpoints.

## Trade-offs

- In-memory only — no transcript history survives container restart. Acceptable for live-view use case.
- No authentication on the SSE endpoint — same as existing phone endpoints. Can add later if needed.
- Single-process fan-out — works for Azure Container Apps single-replica. For multi-replica, would need Redis pub/sub or similar.

## Impact

- No changes to existing phone/voice functionality
- 455 tests pass (8 new)
- Frontend team (Switch) can connect to the stream immediately


# Decision: Demo page added as new view

**Date:** 2026-03-20
**Author:** Switch (Frontend Dev)
**Status:** Implemented

## Context

Sean needs a live demo page for executive stakeholders. The page shows a demo runbook (phone number + scripted questions) and a real-time phone transcript viewer that consumes an SSE stream from the backend.

## Decision

- Added `demo` as a 4th view in the existing view switcher (`chat | tickets | admin | demo`)
- Single `DemoPage` component contains both sections (Runbook + LiveConversation)
- SSE connection via `EventSource` API in a dedicated `useTranscriptStream` hook
- State managed with `useReducer` (idle → active → ended lifecycle)

## API Contract with Tank

Frontend expects SSE at `GET /api/phone/transcripts/stream` with these event types:
- `call_started` (call_id, timestamp, phone_number)
- `user_speech` (text, timestamp, call_id)
- `agent_speech` (text, timestamp, call_id)
- `tool_call` (tool, summary, timestamp, call_id)
- `call_ended` (call_id, timestamp, duration_seconds)

## Files Changed

- `frontend/src/types/demo.ts` — new
- `frontend/src/hooks/useTranscriptStream.ts` — new
- `frontend/src/components/DemoPage.tsx` — new
- `frontend/src/App.tsx` — modified (added demo view)
- `frontend/src/components/Header.tsx` — modified (added Demo tab)

## Risks

- SSE endpoint not yet built by Tank — frontend will show empty state gracefully until backend is ready
- EventSource auto-reconnects on failure, so transient backend unavailability is handled

### Decision: Split Demo Page into Runbook + Live

**Date:** 2026-03-20  
**Author:** Switch (Frontend Dev)  
**Status:** ✅ Implemented & Deployed (commit 830a09a)  
**Source:** .squad/decisions/inbox/switch-split-pages.md (merged 2026-04-09)

**Context**

Sean needs two separate views for live demos:
1. A private "Runbook" on his laptop with demo questions and tips
2. A public "Live" view on the projector showing only the real-time phone transcript

The original combined `DemoPage` showed both on one page — not suitable for audience projection.

**Decision**

- Split `DemoPage.tsx` into `RunbookPage.tsx` (private) and `LivePage.tsx` (public)
- Replaced the single "Demo" nav tab with "Runbook" (📋) and "Live" (📺) tabs
- Live page renders as a full-screen `fixed inset-0` overlay with dark theme (`slate-950`)
- Header is hidden when Live view is active for clean projection
- Escape key and back-arrow button provide exit from Live view back to Runbook
- Both pages reuse the existing `useTranscriptStream` SSE hook

**View Type Change**

The `View` union type changed from `'chat' | 'tickets' | 'admin' | 'demo'` to `'chat' | 'tickets' | 'admin' | 'runbook' | 'live'`. Any code referencing the `'demo'` view value will need updating.

**Impact**

- `DemoPage.tsx` still exists on disk but is no longer imported or routed — can be deleted later
- No backend changes needed — same SSE endpoint (`/api/phone/transcripts/stream`)
- Header.tsx icon imports changed: removed `PresentationChartBarIcon`, added `ClipboardDocumentListIcon` and `TvIcon`

### Decision: Fix Phone Bridge Transcript Streaming + Real Tool Execution

**Author:** Tank  
**Date:** 2026-04-09  
**Status:** ✅ Implemented & Deployed (commit 2669075)  
**Source:** .squad/decisions/inbox/tank-fix-streaming.md (merged 2026-04-09)

**Context**

Sean reported two bugs during phone call testing:
1. Chat responses (agent speech) not showing up in the live transcript viewer
2. Phone calls can't create tickets or route to humans — tools returned mock data

**Decisions Made**

**1. GA Event Name Migration (media_ws.py)**

The ACS↔OpenAI media bridge was listening for `response.audio_transcript.done` (preview Realtime API event). The deployed GA api-version (`2025-04-01-preview`) sends `response.output_audio_transcript.done`. Updated to GA name.

**Impact on Switch:** None — the SSE contract (event types `call_started`, `user_speech`, `agent_speech`, `tool_call`, `call_ended`) is unchanged. The frontend `useTranscriptStream` hook doesn't need changes.

**2. Real Service Wiring for Phone Tools (azure/realtime.py)**

Replaced hardcoded mock responses in `AzureRealtimeService.execute_tool()` with real backend service calls:

| Tool | Service Called | What It Does |
|------|--------------|-------------|
| `analyze_and_route_query` | `llm_service.classify_intent()` + `ticket_service.create_ticket()` | Classifies intent via LLM, creates real ticket |
| `check_ticket_status` | `ticket_service.get_ticket_status()` | Looks up real ticket by ID |
| `search_knowledge_base` | `knowledge_service.search()` | Searches real KB (Azure AI Search or mock) |
| `escalate_to_human` | `ticket_service.create_ticket()` with URGENT priority | Creates escalation ticket |

Services are obtained via lazy import from `dependencies.py` (avoids circular imports, uses cached singletons).

**MockRealtimeService unchanged** — tests continue using mock responses. Only the Azure production service now calls real services.

**3. Error Handling Strategy**

All tool execution is wrapped in try/except. On failure, the error message is returned to the Realtime API model as a `ToolCallResponse(error=...)`, allowing the AI to gracefully tell the caller something went wrong rather than hanging silently.

**Risks**

- `analyze_and_route_query` adds ~2-4s latency (LLM classify + ticket create). Acceptable for voice UX since the AI was already waiting for the tool result.
- No ServiceNow integration yet — `get_ticket_service()` returns `MockTicketService` even in production. Tickets are in-memory. This is a known gap (TODO in dependencies.py).

**Validation**

- 455 tests pass (0 failures)
- Deployed via `azd deploy backend`
- Health check: all services UP
- SSE endpoint confirmed streaming keepalives

### Decision: URL-Based Routing for /live and /runbook

**Author:** Switch (Frontend Dev)
**Date:** 2026-04-09
**Status:** Implemented
**Commit:** dc90d44

## Context

Sean needs to share a direct `/live` URL with the demo audience so they can see the live transcript on a projected screen without navigating through the app. Previously, the SPA had no URL routing — all paths loaded the default chat view.

## Decision

Read `window.location.pathname` at app initialization to determine the starting view. No react-router — just a simple function that maps pathname to view state.

### Route behavior:
| Path | View | Header | Exit button |
|------|------|--------|-------------|
| `/live` | LivePage (fullscreen) | Hidden | None (audience mode) |
| `/runbook` | RunbookPage | Shown with tabs | N/A |
| `/` or other | Chat | Shown with tabs | N/A |

### Key detail: audience vs presenter mode
- **Direct URL `/live`** = audience mode: no exit button, no escape key, no way to leave. Perfect for a projector.
- **Tab-click to Live** = presenter mode: back arrow and escape key return to runbook.

This is controlled by `isDirectLiveRoute` (computed once at module load from `window.location.pathname`).

## Alternatives Considered

1. **react-router** — Overkill. We have 5 views and no nested routes. Adds bundle weight for no benefit.
2. **Hash routing (`#/live`)** — Works but ugly URLs. Pathname routing is cleaner and nginx already supports it.

## Impact

- Only `frontend/src/App.tsx` modified (15 lines added)
- No new dependencies
- No server config changes (nginx `try_files` already handles SPA fallback)
- Backward compatible: existing behavior unchanged for `/` and tab navigation

### Decision: Handle Both Preview and GA Realtime Transcript Event Names

**Date:** 2026-04-09
**Author:** Tank (Backend Dev)
**Status:** Implemented
**Commit:** 297e7f7

## Context

The Azure OpenAI Realtime API uses different event names depending on the API version:
- **Preview** (`2025-04-01-preview`): `response.audio_transcript.done` / `.delta`
- **GA**: `response.output_audio_transcript.done` / `.delta`

Our backend is pinned to the preview API version (`config.py:189`), but a previous fix (commit 2669075) changed the handler to only listen for the GA name. This caused agent speech transcripts to be silently dropped — the event arrived but never matched the handler.

## Decision

Handle **both** event names in `media_ws.py` using `if t in (preview_name, ga_name)`. This makes the code forward-compatible: it works on the current preview API and will continue working when we upgrade to GA without any code changes.

## Implications

- When upgrading the API version to GA, no transcript handler changes needed.
- The delta ignore list already covered both names — only the `.done` handler needed fixing.
- Pattern to follow: any event name that differs between preview/GA should be handled with a tuple check, not a single string comparison.


### Azure OpenAI Realtime API — session.update schema per endpoint

# DECISION: Azure OpenAI Realtime API — session.update schema per endpoint

**Author:** Tank (Backend)
**Status:** Proposed (awaiting ratification)
**Context:** Phone bridge caller transcripts were empty in production. Root cause (verified via container logs and anvil review): Azure OpenAI's Realtime API rejected the nested `session.audio` block on the direct-WS endpoint, silently disabling whisper-1 input transcription.

## Decision

For the **phone bridge direct-WS path** — `wss://<resource>.openai.azure.com/openai/realtime?api-version=2025-04-01-preview&deployment=gpt-realtime` — use **FLAT session-level fields** in `session.update`:

- `voice`
- `input_audio_format`
- `output_audio_format`
- `input_audio_transcription: { model: "whisper-1" }`
- `turn_detection: {...}`
- `tools: [...]`

**Do NOT use a nested `audio: { input: {...}, output: {...} }` block on this endpoint.** It will be rejected with:

```
invalid_request_error / unknown_parameter / "Unknown parameter: 'session.audio'." / param: 'session.audio'
```

This failure is **silent to the app** (connection stays open) but disables whisper-1 on caller audio, so `conversation.item.input_audio_transcription.*` events never fire and caller transcripts stay empty.

## Scope / Non-scope

- **In scope:** `backend/app/api/media_ws.py` (ACS ↔ Azure OpenAI phone bridge).
- **Out of scope:** `/openai/v1/realtime/calls` WebRTC endpoint used by the browser voice feature — that endpoint DOES accept the nested `audio.input` / `audio.output` schema. Do not "unify" these two schemas. They are owned by different Azure OpenAI surfaces and evolve independently.

## Rationale

Two endpoints = two schemas. A prior memory note claimed flat fields cause `unknown_parameter` errors; that note was scoped to the WebRTC endpoint and was over-generalized. This decision pins the correct schema per endpoint so the next contributor doesn't re-introduce the regression.

## Consequences

- Caller transcripts flow again (`conversation.item.input_audio_transcription.delta` + `.completed` events fire).
- Future edits to `media_ws.py` must preserve the flat schema on the phone path.
- If Azure OpenAI later unifies these endpoints, revisit — but verify against live error logs, not assumptions.

## Evidence

- Container log line observed prior to fix: `unknown_parameter: session.audio`.
- Post-fix: backend test suite 461 passed, 97 skipped (no tests pinned the old nested shape).
- Also fixed incidental `AttributeError: 'ClientConnection' object has no attribute 'closed'` in the finally block — newer `websockets` library dropped `.closed`; wrap in try/except instead.



