# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Core Context

Historical team updates and architectural learnings are consolidated below for future reference.

### Workshop Companion Site (2026-03-19)
Built standalone React + TypeScript + Tailwind CSS site at `workshop-site/` as executive briefing tool.
- **Architecture:** 10 tab-based sections, Tab navigation with keyboard accessibility, reusable components (TabNavigation, CollapsibleNotes, CalloutCard, DiagramSVG)
- **Visual Language:** Microsoft Fluent 2 (generous whitespace, calm typography); Primary: #0078D4 blue, gray #F3F2F1, dark #323130; IU crimson (#990000) as accent only
- **Key Paths:** Site root `workshop-site/`, main app `workshop-site/src/App.tsx`, tabs `workshop-site/src/tabs/*.tsx`, components `workshop-site/src/components/*.tsx`
- **Build:** TypeScript passes, prod build 222.94 kB JS (63.50 kB gzipped), 371 modules, 2.15s

### Azure SWA Auth Migration (2026-03-14)
Runbook docs migrated to Azure Static Web Apps with built-in authentication.
- **Config:** Azure AD (Entra ID) only; `/.auth/login/aad` + `/.auth/logout` anonymous; all other routes require `authenticated` role; 401 redirects to AAD login
- **Integration:** Auth bar in sticky nav (right-aligned), uses `/.auth/me` fetch; graceful degradation on local dev (silent catch if unavailable)
- **Files:** Config `docs/staticwebapp.config.json`, setup guide `docs/AZURE_SWA_SETUP.md`, deployment workflow `.github/workflows/deploy-docs-swa.yml`

### Voice Architecture Constraints (2026-03-14)
Foundational WebRTC + Azure OpenAI design rules:
- **Audio Path:** Never transits backend — WebRTC connects browser → Azure OpenAI directly; backend only relays tool-call results via `/api/realtime/ws`
- **Token Security:** Ephemeral token TTL ≤ 60s (single-use, non-renewable) — hard constitutional constraint
- **Session Context:** `session_id` shared between text chat and voice — voice attaches to existing `Session` entity; modality switching preserves context

### session.update via Data Channel (2026-03-14)
Added `dc.onopen` handler in `useVoice.ts` to send `session.update` event via WebRTC data channel enabling `input_audio_transcription` (whisper-1). Belt-and-suspenders with backend: frontend ensures transcription active before listening.

### Demo Pages Split (2026-03-20)
Split combined DemoPage into RunbookPage (presenter-only cheat sheet with questions table) + LivePage (full-screen dark-theme audience viewer).
- **RunbookPage:** Runbook, phone number, 9 demo questions, presenter tips
- **LivePage:** Full-screen dark theme (`bg-slate-950`), agent cyan-on-dark, caller slate-on-dark, tool badges animate-pulse, large text for back-of-room, smooth auto-scroll
- **Exit:** Escape key or arrow button returns to runbook

### URL-Based Routing (2026-04-09)
Added `window.location.pathname` reading at module load for direct URL navigation.
- **Routes:** `/live` = audience mode (no header/exit), `/runbook` = presenter mode, `/` = default chat
- **Implementation:** No react-router — simple `getInitialView()` function, `isDirectLiveRoute` flag controls exit prop
- **Design:** Direct `/live` URL removes exit controls for audience; tab navigation includes exit

---

## Team Updates

### 2026-04-09T04:52Z — Direct URL Routing for /live and /runbook

Switch added URL routing for direct access to /live and /runbook pages in `frontend/src/App.tsx`:
- **Commit:** dc90d44
- **Build:** 721 modules, 231.85 kB JS (66.55 kB gzipped)

**Cross-agent note:** Tank simultaneously fixed event name mismatch in media_ws.py (commit 297e7f7, all 461 tests passed). Both changes deployed without blocking issues.

---

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-19 — Workshop Companion Site Build (Archived to Core Context)

**Architecture decisions:**
- Built standalone React + TypeScript + Tailwind CSS site at `workshop-site/` as executive briefing tool for "Trustworthy Agentic AI in Higher Education" workshop
- Microsoft Fluent 2 visual language: generous whitespace, calm typography, restrained color palette
- Primary colors: Microsoft blue (#0078D4), neutral gray (#F3F2F1), dark text (#323130)
- IU crimson (#990000) used SPARINGLY for callout borders — accent color, not primary
- 10 tab-based sections covering full 47 Doors narrative: Problem → Architecture → Trust → Voice → Demo → Governance

**Component architecture:**
- Tab navigation with keyboard accessibility (arrow keys, Tab/Shift+Tab, Enter/Space)
- Reusable components: TabNavigation, CollapsibleNotes, CalloutCard, DiagramSVG
- Each tab is standalone React component in `src/tabs/` — deep-linkable design
- SVG diagrams with semantic markup (figure/figcaption, aria-labels, title/desc elements)
- No external component libraries — lightweight, Heroicons only

**Key file paths:**
- Site root: `workshop-site/`
- Main app: `workshop-site/src/App.tsx` (tab state management)
- Tab components: `workshop-site/src/tabs/*.tsx` (10 total: Overview, TheProblem, ChatbotsToAgents, TrustBoundaries, Architecture, VoiceAccessibility, DemoWalkthrough, ResponsibleAI, ReuseAcrossCampus, YourFirstAgent)
- Reusable UI: `workshop-site/src/components/*.tsx`
- README: `workshop-site/README.md` (install/run instructions)

**User preferences observed:**
- Calm, academic tone — NO flashy marketing energy
- Text-light, visually rich — icons, diagrams, callout cards over dense paragraphs
- Speaker notes as collapsible sections (preserve presentation context without cluttering UI)
- Interactive "Your First Agent" exercise (client-side only, no backend) with live-updating agent card
- High contrast text (WCAG AA 4.5:1 minimum), semantic HTML, keyboard navigation
- Design principle: "This should feel like a confident executive briefing, not a product pitch"

**Content patterns:**
- Each tab has: headline, visual elements (diagrams/cards), callout cards for key insights, collapsible presenter notes
- Diagrams use inline SVG with DiagramSVG wrapper for accessibility
- "What to Notice" callouts highlight architectural insights
- Demo walkthrough uses numbered step cards with visual labels and notes
- "Your First Agent" tab uses controlled inputs with example chips for quick selection

**Build verification:**
- TypeScript typechecks clean (`npm run typecheck` passes)
- Production build succeeds: 222.94 kB JS (63.50 kB gzipped), 16.28 kB CSS (3.58 kB gzipped)
- 371 modules transformed, built in 2.15s
- Local dev: `npm run dev` (Vite dev server on port 5173)

### 2026-03-14 — Azure Static Web Apps Auth Migration (docs runbook)

**Architecture decisions:**
- Runbook site migrated from GitHub Pages → Azure Static Web Apps for built-in authentication.
- Auth provider: Azure AD (Microsoft Entra ID) only — GitHub/Twitter providers explicitly blocked with 404.
- `staticwebapp.config.json` route rules: `/.auth/login/aad` + `/.auth/logout` are `anonymous`; all other routes require `authenticated` role; 401 redirects to AAD login.
- Auth bar integrated into existing sticky nav (right-aligned `.nav-auth` div) — uses `/.auth/me` fetch to show username; hidden on local dev when endpoint unavailable (silent catch).

**Key file paths:**
- SWA config: `docs/staticwebapp.config.json`
- Setup guide: `docs/AZURE_SWA_SETUP.md`
- GitHub Actions workflow: `.github/workflows/deploy-docs-swa.yml`
- Deployment secret expected: `AZURE_STATIC_WEB_APPS_API_TOKEN` (user adds after SWA resource creation)

**User preferences observed:**
- Auth UI must be minimal — user said "don't distract from runbook content"
- Dark theme, purple accent, Inter font — all auth elements use existing CSS variables
- Setup docs use bash (not PowerShell) with emojis for readability
- Local dev graceful degradation is a hard requirement (auth bar hides if `/.auth/me` unavailable)

**Architecture decisions:**
- Audio never transits the backend — WebRTC connects browser → Azure OpenAI directly. Backend only relays tool call results via `/api/realtime/ws`.
- Ephemeral token TTL ≤ 60 s is a hard constitutional constraint (Voice Channel Security); tokens are single-use and non-renewable.
- `session_id` is shared between text chat and voice sessions — voice attaches to the existing `Session` entity so modality switching preserves context.

**Key file paths:**
- OpenAPI contract: `specs/002-voice-interaction/contracts/voice-api.yaml`
- Quickstart guide: `specs/002-voice-interaction/quickstart.md`
- Planned backend router: `backend/app/api/realtime.py` (not yet created)
- Planned frontend hook: `frontend/src/hooks/useVoice.ts` (not yet created)
- Existing router pattern: `backend/app/api/routes.py` (FastAPI `APIRouter`, mounted at `settings.api_prefix` = `/api`)
- Vite proxy config: `frontend/vite.config.ts` — `/api` → `http://127.0.0.1:8000`; WebSocket proxy is handled automatically.
- Env example: `backend/.env.example` — `MODE=mock` is the default; voice adds `AZURE_OPENAI_REALTIME_DEPLOYMENT`.

**Patterns to follow:**
- Router uses `APIRouter()` with full `responses={}` dicts for all non-200 status codes.
- All response models use Pydantic v2 schemas defined in `backend/app/models/`.
- Health check pattern: always returns HTTP 200; use field values (`realtime_available`) for capability detection, not HTTP status.
- WebSocket close code conventions: 4001 = invalid token, 4002 = session expired (custom range above 4000 for app-level errors).

### 2026-03-14 — session.update via Data Channel for Transcription

**What:** Added `dc.onopen` handler in `useVoice.ts` that sends a `session.update` event through the WebRTC data channel to enable `input_audio_transcription` (whisper-1 model). Without this, the Azure OpenAI Realtime API never emits `conversation.item.input_audio_transcription.completed` events — meaning user speech is never transcribed.

**Why belt-and-suspenders:** The backend (Tank) is also being updated to include `input_audio_transcription` in the initial session config. The frontend `session.update` is a safety net — if the backend config is ever missing or the API ignores the initial config, the data-channel message ensures transcription is active before we start listening.

**Side benefit:** Moved the `LISTENING` dispatch into `dc.onopen` instead of relying on `pc.onconnectionstatechange`. The data channel being open is the actual prerequisite for sending/receiving events — more semantically correct than peer connection state alone.

**Key files:**
- `frontend/src/hooks/useVoice.ts` — added `dc.onopen` handler (lines 106–116)

**Team Coordination:** Coordinated with Tank's parallel backend session config changes (spawn 2026-03-15T01:53). Both changes are idempotent and reinforce each other. Frontend ensures transcription is active; backend ensures system prompt is sent.

**Verification:** TypeScript compiles clean. Code review passed (Morpheus).

**Orchestration Log:** `.squad/orchestration-log/2026-03-15T01-53-switch.md`

### 2026-03-20 — Demo Runbook Page with Live Transcript Viewer

**What was built:**
- New `demo` view added to the app's view switcher (alongside chat, tickets, admin)
- Two-section page: Demo Runbook (phone number + 9 demo questions table) + Live Phone Conversation (SSE transcript viewer)
- SSE hook (`useTranscriptStream`) connects to `/api/phone/transcripts/stream` and renders real-time call events
- Chat-bubble UI for caller vs AI agent speech, info badges for tool calls, status indicators for call state

**Key file paths:**
- `frontend/src/types/demo.ts` — SSE event types (CallStarted, UserSpeech, AgentSpeech, ToolCall, CallEnded)
- `frontend/src/hooks/useTranscriptStream.ts` — EventSource hook with useReducer state machine
- `frontend/src/components/DemoPage.tsx` — Full page component (Runbook + LiveConversation)
- `frontend/src/App.tsx` — View type extended with 'demo', DemoPage wired in
- `frontend/src/components/Header.tsx` — Demo tab added with PresentationChartBarIcon

**Patterns used:**
- View switcher pattern matches existing chat/tickets/admin pattern exactly
- Header tab style matches existing tabs (border-b-2 active indicator, Heroicons)
- Message bubbles follow same visual pattern as MessageBubble.tsx (primary-600 for user, white border for agent)
- `aria-live="polite"` on transcript area for screen reader support
- Auto-scroll via useEffect + scrollRef on event changes
- EventSource auto-reconnection (built-in browser behavior)

**API contract (backend dependency on Tank):**
- SSE endpoint: `GET /api/phone/transcripts/stream`
- Event types: call_started, user_speech, agent_speech, tool_call, call_ended
- Frontend is ready; backend SSE endpoint must be implemented by Tank

**Build verification:**
- TypeScript + Vite build passes clean: 720 modules, 226.28 kB JS (65.23 kB gzip), built in 2.54s

### 2026-03-20 — Split Demo Page into Runbook + Live Pages

**What was built:**
- Split the combined DemoPage into two separate pages for live demo workflow
- `RunbookPage.tsx` — Sean's private cheat sheet: phone number, 9 demo questions table, presenter tips section
- `LivePage.tsx` — audience-facing full-screen dark theme transcript viewer for projector display
- Live view hides the app header entirely for clean projection (Escape key or back arrow to exit)

**Key file paths:**
- `frontend/src/components/RunbookPage.tsx` — Presenter-only runbook page
- `frontend/src/components/LivePage.tsx` — Full-screen audience transcript viewer
- `frontend/src/components/DemoPage.tsx` — Original combined page (still exists, no longer routed)
- `frontend/src/App.tsx` — View type extended with 'runbook' | 'live', replaces 'demo'
- `frontend/src/components/Header.tsx` — Runbook (ClipboardDocumentListIcon) + Live (TvIcon) tabs replace Demo tab

**Design decisions for LivePage:**
- `fixed inset-0` overlay with `bg-slate-950` — full viewport dark theme
- Agent speech: cyan-on-dark (`bg-cyan-900/50`, `text-cyan-50`), caller: slate-on-dark (`bg-slate-700/80`, `text-slate-100`)
- Tool calls: pulsing cyan badges (`animate-pulse`) for visual feedback
- Large text (`text-lg` on messages, `text-2xl` on empty state) for back-of-room readability
- Smooth auto-scroll with `scrollTo({ behavior: 'smooth' })`
- Escape key handler + floating ArrowLeftIcon button for exit
- Subtle "47 Doors" branding in top bar with phone number

**Patterns used:**
- Reuses existing `useTranscriptStream` SSE hook — no new data layer needed
- Header hidden via conditional rendering when `currentView === 'live'`
- `onExit` callback prop returns to Runbook view
- Same View type union pattern as existing chat/tickets/admin

**Build verification:**
- TypeScript + Vite build passes clean: 721 modules, 231.67 kB JS (66.49 kB gzip), built in 4.49s
- Deployed to Azure Container Apps successfully

### 2026-04-09 — Exercise Content Alignment with Voice/Phone Features

**Exercise Updates (via Anvil):**
- All 8 labs (00-06 + Exercise 05x) updated to reference voice and phone capabilities
- Coach guide (4 files) updated with voice/telephony facilitation guidance
- Workshop site: new "Telephony" tab added to navigation
- Participant guide, quick reference, README, CHANGELOG all updated to reflect integrated voice/phone features

**Connection to Switch's work:**
- RunbookPage/LivePage split (commit 830a09a) is now explicitly featured in exercise walkthroughs as the demo interface pattern
- Participants see how Switch's UI/UX decisions enable live presenter control of what the audience sees
- Exercise content makes clear that voice transcript streaming is a key feature for live demonstrations

**Context for facilitators:**
- Coach guide now points facilitators to the RunbookPage for preparation and LivePage for projection
- Demo questions explicitly mention phone call capability (via Tank's transcript fix)
- Presentation notes explain the architectural rationale for the split-page design

**Orchestration Log:** `.squad/orchestration-log/2026-04-09T03-01-38Z-anvil.md`

### 2026-04-09 — URL-Based Routing for /live and /runbook Direct Access

**What was built:**
- Added `window.location.pathname` reading at app initialization to support direct URL navigation
- `/live` → fullscreen audience mode (no header, no exit button) — clean projector view
- `/runbook` → presenter runbook page with normal header/tabs
- `/` or any other path → default chat view with full header navigation

**Key design decisions:**
- No react-router dependency — simple `getInitialView()` function reads pathname once at module load
- `isDirectLiveRoute` flag (module-level constant) controls whether LivePage gets an `onExit` prop
- Direct `/live` URL = audience mode: no back arrow, no escape key handler, no way to accidentally leave
- Tab-navigated `/live` = presenter mode: back arrow returns to runbook, escape key works
- nginx `try_files $uri $uri/ /index.html` already handled SPA fallback — no server config changes needed

**Files modified:**
- `frontend/src/App.tsx` — added `getInitialView()`, `isDirectLiveRoute`, conditional `onExit` prop

**Build verification:**
- TypeScript + Vite build passes clean: 721 modules, 231.85 kB JS (66.55 kB gzip)
- Deployed to Azure Container Apps successfully
- Commit: `dc90d44` on main

### 2026-04-21T17:30Z - Voice Schema Clarification (Phone Bridge vs WebRTC)

**Cross-agent note from Tank/Anvil diagnosis:**
- Phone bridge caller transcripts returned empty parameter errors due to nested session.audio being incompatible with direct-WS Azure OpenAI endpoint
- CLARIFICATION FOR SWITCH: The WebRTC endpoint used by browser useVoice.ts DOES accept nested audio.input / audio.output schema
- Do NOT change browser voice implementation - the nested schema is the correct one for the WebRTC path
- The regression was specific to the phone bridge (direct-WS) endpoint, which requires flat top-level fields
- No changes needed to Switch's frontend voice code; it remains production-correct

**Impact:** Frontend voice feature unaffected. Commit 234c2ec applies only to backend phone bridge path.

### 2026-04-21T19:15Z - Runbook Website Phone Documentation Update

**What was verified:**
- All workshop-site runbook tabs already updated in commit 599cc8e (by Anvil/msftsean) to reflect production phone bridge
- Telephony.tsx: Production callout added for April 21, 2026 verification + technical note on Realtime API schema asymmetry
- VoiceAccessibility.tsx: "What's Next" changed to "Phone Integration Is Live" with production date
- DemoWalkthrough.tsx: Phone demo section updated to reflect production-ready status (+1-913-217-1946)
- PresenterScript.tsx: No phone-specific content, no changes needed
- Architecture.tsx, Overview.tsx, App.tsx: No phone content, correctly unchanged

**Copy patterns standardized:**
- Production callouts use "production-verified" language with specific date (April 21, 2026) and revision (azd-1776792457)
- Phone number consistently shown as +1-913-217-1946 in all contexts
- "Same 3-agent pipeline" messaging emphasized across all tabs
- Technical details (Realtime API schema) placed in amber-bordered callouts for presenter context
- Tone remains factual, academic, presenter-facing (no marketing fluff)

**Tabs updated in commit 599cc8e:**
- Telephony.tsx - Production callout + Realtime API technical note
- VoiceAccessibility.tsx - Live phone integration callout
- DemoWalkthrough.tsx - Production-ready phone demo section

**Verification:**
- TypeScript type-check passed clean (npx tsc --noEmit)
- No new commits needed — documentation already current on main branch

**Key learning:**
Workshop-site documentation was already updated in parallel commit stream. Cross-agent coordination via commit log inspection confirmed all requested changes already present.

