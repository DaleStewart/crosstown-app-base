# 47doors vs Our App — Architecture & Process Delta

> **Purpose:** Strategic analysis for the MTA hackathon team. Research only, no code changes.  
> **Written:** 2026-05-16 | **Author:** Anvil  
> **Audience:** Sean + whoever makes the Tuesday demo call

---

## 1. Architecture Comparison

| Dimension | 47doors (reference) | Our app |
|---|---|---|
| **Backend services** | 1 monolith (`backend/`) | 3 microservices: `orchestrator` + `log_analyst` + `service_advisor` |
| **Agent pattern** | 3-agent pipeline _inside_ one process: `QueryAgent → RouterAgent → ActionAgent` | ToolRegistry across 2 external specialist URLs; orchestrator dispatches HTTP |
| **Voice endpoint** | `POST /api/realtime/session` (ephemeral token) + `WS /api/realtime/ws` (relay) | `WS /ws/voice` (direct streaming relay to Foundry Realtime) |
| **Text endpoint** | Implicit (same chat path) | `POST /api/turn` (eval/redteam surface, same tool path as voice) |
| **Infra resources** | OpenAI, AI Search, Cosmos, ACA (2 apps), ACR | OpenAI (Foundry), AI Search, Cosmos, ACA (4 apps), ACR, Speech, Key Vault, Foundry Hub/Project, App Insights, UAMI, Postgres (idle) |
| **Auth model** | `ManagedIdentityCredential` (API key auth disabled by Azure policy — they document this) | `DefaultAzureCredential` → single UAMI; keyless throughout |
| **Tool dispatch** | `if/elif` on tool name in one `execute_tool()` function in `realtime.py` | Table-driven `ToolRegistry`: `name → specialist URL`, loaded from each specialist's `GET /tools` at startup |
| **Name collision** | N/A (single service, no conflicts possible) | Later registration wins; _silent_ (a bug waiting to happen) |
| **Citation contract** | None. Tool results are plain JSON strings via `ToolCallResponse` | `ToolResponse.finalize()` auto-tags `warnings:["uncited"]`; CI fails at >5% uncited |
| **Deploy topology** | ACA env + 2 apps (backend, frontend) | ACA env + 4 apps (log-analyst, service-advisor, orchestrator, frontend) |
| **Local dev** | `docker-compose.yml` with `MOCK_MODE=true`; full stack up with one command | No docker-compose; individual `uvicorn` + `npm run dev` |
| **Mock mode** | `MockRealtimeService` (no Azure creds needed); documented and tested | `VOICE_PROVIDER` env selects implementation; not as prominently documented |

**Effectively identical:** Stack (Python 3.11 FastAPI + React + Vite + Bicep + azd), auth philosophy (keyless), ACA hosting, AI Search + Cosmos as backing stores, cadence of `azd up`.

**Actually different:** 47doors is a monolith optimised for workshop teachability. We are a microservice mesh optimised for independent scaling and specialist isolation. Both are valid for different goals — ours is harder to operate and debug, but more realistic as a production pattern.

---

## 2. Frontend Comparison

### Component structure

| Component | 47doors | Our app |
|---|---|---|
| **Chat input** | `ChatInput.tsx` — textarea, auto-resize, Enter/Shift+Enter, disabled-during-load | No separate `ChatInput.tsx` on `main` — text input was `POST /api/turn` wired directly; PR #23 added stateless component with callback props |
| **Mic button** | `VoiceMicButton.tsx` — 6-state toggle (idle/connecting/listening/processing/speaking/error) | `PushToTalkButton.tsx` — callback props (`onStart`, `onStop`, `recording`, `disabled`), mouse/touch/spacebar |
| **Transcript** | `VoiceTranscript.tsx` — role-separated, `role="log"` for a11y | `Transcript` component — similar separation |
| **Tool panel** | `TicketDashboard.tsx` + `AdminDashboard.tsx` — ticket management UI | `ToolCallPanel.tsx` — shows tool calls inline; `DisruptionBanner`, `AlternateRouteCard` for service-advisor results |
| **Map / visualization** | ❌ No map component. `LivePage.tsx` is a scrolling transcript for phone-call audiences | ❌ No map component (route_graph.json data exists, no visual) |
| **Status indicators** | `VoiceStatusIndicator.tsx` — explicit component | Inline in `PushToTalkButton` + loading state in parent |
| **Error/loading UX** | Explicit error alerts, loading spinners, empty states in every data-fetching component | `DisruptionBanner` + button disabled state; loading path thinner overall |

### Voice flow — push-to-talk / session lifecycle

**47doors:** WebRTC stack — `RTCPeerConnection` + `oai-events` data channel + SDP offer/answer to `/openai/v1/realtime/calls`. Session token fetched first (`POST /api/realtime/session`). `session.update` sent on `dc.onopen` in the GA nested format (`session.audio.input.transcription`, `session.audio.output.voice`). Cleanup: close peer connection, clear audio srcObject.

**Ours:** Raw WebSocket to `/ws/voice` (PCM streaming). No WebRTC layer. Mic captured via `getUserMedia`, PCM piped into the socket. `session.update` sent by the orchestrator backend after WS open, not from the frontend.

**Bug #14 connection:** 47doors' `session.update` is single-phase, GA-nested format — this is exactly what we adopted in the orchestrator fix (flat fields on the direct-WS path caused `unknown_parameter: session.audio`). Their CHANGELOG documents this exact pitfall: _"the nested `session.audio` block used by the WebRTC endpoint is rejected with `unknown_parameter: session.audio`"_. We learned this the hard way; they already wrote it down.

**Implication:** 47doors' WebRTC approach never faces the input_audio_buffer PCM-framing bugs we hit, because the browser's WebRTC stack handles framing natively. Our raw-PCM-over-WebSocket path is lower-level and more fragile at the audio commit boundary.

### Chat input — PR #23 alignment

PR #23 (`ChatInput` stateless component with callback props) explicitly adopted the same pattern as 47doors' `ChatInput.tsx`. The pattern is correct. The regression is not architectural — it's that `fe-202605161807` was built from `anvil/feat-service-advisor` (based on `main` which was missing PRs #19, #21, #23, #25) and deployed, rolling back those fixes. The fix already exists in those PRs. This is a deploy choreography problem, not a frontend architecture problem.

### Map / visualization

Neither app has a map component. 47doors has `LivePage.tsx` (scrolling phone-call transcript for audience display). We have `route_graph.json` data but no renderer. If Tuesday's demo needs a route visualization, this is a build-from-scratch item — 47doors offers no head start.

### nginx / SPA proxy / `/api/health` pattern

**47doors `nginx.conf`:**
```
location /api/phone/transcripts/stream  → SSE, no buffering
location /api/realtime/ws               → WebSocket upgrade (explicit)
location /api/                          → proxy_pass BACKEND_URL
location /                              → try_files $uri /index.html (SPA fallback)
```
Plus security headers. Also has `HEALTHCHECK` in Dockerfile: `curl -f http://localhost:8000/api/health`.

**Our `nginx.conf`:**
```
location /api/   → proxy_pass ORCHESTRATOR_URL (with SNI + Host headers for ACA TLS)
location /ws/    → WebSocket upgrade
location /       → try_files $uri /index.html
```
No Dockerfile HEALTHCHECK. No explicit `/api/health` proxy rule (falls through to `/api/`).

**The 404 / Hello World pitfall:** Our regressions weren't nginx bugs — they were ACA serving the placeholder image (`mcr.microsoft.com/k8se/quickstart:latest`) instead of our container. nginx never ran. Neither 47doors nor we have a guard in the deploy pipeline that verifies `GET /api/health` returns 200 before marking a deploy successful. **47doors' smoke-test.sh does this locally — we don't have an equivalent.**

---

## 3. Backend Comparison

### Tool dispatch

| Concern | 47doors | Our app |
|---|---|---|
| **Tool registration** | Hardcoded `if/elif` in `execute_tool()` | `ToolRegistry` loads from each specialist's `GET /tools`; `name → url` map |
| **Adding a tool** | Edit `realtime.py`, add `elif` branch | Create `tools/<name>.py`, `register()` in `tools/__init__.py`, restart specialist |
| **Multi-specialist** | Not applicable (single process) | Yes — log-analyst and service-advisor both register tools at orchestrator startup |
| **Name conflicts** | Impossible | Last-registration-wins (silent; could silently shadow a log-analyst tool if service-advisor reuses a name) |
| **Failure isolation** | Single `try/except` around all tools; one failure returns error string, doesn't crash session | Same — `ToolResponse` always returned; specialist HTTP errors are caught and wrapped |
| **Unknown tool** | Returns `ToolCallResponse(error="Unknown tool: ...")` | Falls back to first URL if name not in registry (probably wrong behavior) |

**Opinion:** Our table-driven pattern is more extensible but the silent name-conflict resolution is a real bug. If service-advisor ever defines a tool named `search_logs` by accident, log-analyst's version silently disappears. This needs a startup assertion or an error on conflict.

### Citation contract

47doors has **no citation contract**. Tool results are plain JSON strings. No `warnings`, no `finalize()`, no CI gate. This means a hallucinated answer looks identical to a cited one in the API response — the consumer has no signal.

Our citation contract (`ToolResponse.finalize()`, `warnings:["uncited"]`, 5% CI gate) is a genuine differentiator. It's not over-engineering — it's the thing that makes our eval harness meaningful. See Section 9.

### System prompt structure

**47doors:** Concise, in `realtime.py` as a constant. 6 rules: no markdown, spell ticket IDs, don't repeat PII, ask clarifying questions, summarize top KB result, acknowledge concern first.

**Ours** (`system_prompt.py`): Lists all 8 tools by name (4 log-analyst + 4 service-advisor), explicit rule to surface cited IDs verbatim, fictional-rail-only constraint (L1/L2/L3).

47doors' prompt is tighter and more testable. Ours is longer because we have more tools, but it could be more explicit about failure modes (what to say when no tool returns results).

### Voice session lifecycle

| Event | 47doors (`media_ws.py`) | Our app (`foundry_realtime.py`) |
|---|---|---|
| `session.created` | Sends `session.update` (flat fields for direct-WS path) | Opens WS, sends `session.update` (GA nested format) |
| `session.updated` | Logs confirmation | Awaits confirmation before starting event pump |
| `input_audio_buffer.speech_stopped` | Commits buffer | Not in our pipeline (raw PCM, no VAD boundary) |
| `response.function_call_arguments.done` | `execute_tool()` → `conversation.item.create` → `response.create` | `ToolCall` event dispatched to specialist, result returned as `conversation.item.create` |
| `response.done` | Session stays open | `Final` event with accumulated citations |

Key delta: 47doors explicitly handles `input_audio_buffer.speech_stopped` and `input_audio_buffer.committed` for VAD-based turn management. Our PCM streaming path does not — we rely on the Realtime API's built-in VAD without explicit commit acknowledgement, which has been a source of the voice loop bug (#14).

---

## 4. Deploy Choreography

### The placeholder image problem

**Both repos use the same pattern:**
```bicep
var placeholderImage = 'mcr.microsoft.com/k8se/quickstart:latest'
// ...
image: placeholderImage  // azd replaces this with real built image after azd build
```

`azd provision` always resets container images to the placeholder — this is by design in azd's model. `azd deploy` (or `azd up`) then builds and pushes the real image. **This pattern is identical in both repos. Neither has a guard.**

### How 47doors' hooks compare to ours

| Hook | 47doors | Our app |
|---|---|---|
| `preprovision` | `echo "Preparing..."` (no-op) | Not defined |
| `postprovision` | `echo "Run azd deploy"` (no-op) | Runs `load_search_index.ps1/.sh` to seed AI Search |
| `postdeploy` | Echoes AZURE_FRONTEND_URL and **`$AZURE_CONTAINERAPP_URL/api/health`** | Not defined |

**47doors' `postdeploy` hook prints the health URL explicitly.** Ours doesn't. If ours did, the "Hello World" regression would at least produce a visible prompt to check `/api/health` immediately after deploy. Not a fix, but a faster feedback loop.

### Why the current regression happened

The frontend rollback (`fe-202605161807` losing text input) was **not** an azd placeholder bug. The sequence:
1. `anvil/feat-service-advisor` was branched off `main`
2. `main` at that time was missing PRs #19, #21, #23, #25 (the frontend fix chain)
3. `fe-202605161807` was built from that branch, producing an image that pre-dates the fixes
4. That image was deployed, rolling back the frontend

**Root cause: no branch protection / build provenance check.** Neither repo enforces "only deploy images built from `main`." 47doors doesn't solve this either. The difference is that 47doors has `scripts/smoke-test.sh` which explicitly checks `/api/health` and could catch "Hello World" within 30 seconds of deploy. We have no equivalent.

### What would have prevented Bug #11 (Hello World) and the frontend rollback

| Guard | 47doors has it? | We have it? | Would it have helped? |
|---|---|---|---|
| `scripts/smoke-test.sh` checks `/api/health` | ✅ Yes | ❌ No | ✅ Bug #11: caught immediately |
| `postdeploy` hook prints health URL | ✅ Yes (echo only) | ❌ No | 🟡 Marginally — prompts manual check |
| Dockerfile HEALTHCHECK | ✅ Yes | ❌ No | 🟡 ACA doesn't use Dockerfile HEALTHCHECK directly, but it signals container readiness |
| "Only deploy from `main`" CI gate | ❌ No | ❌ No | ✅ Frontend rollback: prevented |
| Deploy image pinned from PR SHA | ❌ No | ❌ No | ✅ Frontend rollback: prevented |

### ACA revision strategy

Neither repo uses `targetRevision`, blue-green, or traffic splitting. Both use ACA's default replace-in-place on every `azd deploy`. This means a bad deploy is immediately live with no rollback path except `azd deploy` again from a known-good commit.

### Our azure.yaml is missing `service-advisor`

```yaml
# Current azure.yaml on main (as of this writing):
services:
  log-analyst:    ...
  orchestrator:   ...
  frontend:       ...
  # service-advisor is NOT HERE
```

If `service-advisor` shipped in `anvil/feat-service-advisor` but its entry wasn't merged to `azure.yaml` on `main`, then `azd deploy` will not deploy it. The orchestrator will fail all service-advisor tool calls at runtime. **Verify this before Tuesday.**

---

## 5. Eval + Red Team Comparison

| Dimension | 47doors | Our app |
|---|---|---|
| **Citation gate threshold** | N/A (no citation contract) | 5% uncited; CI-enforced |
| **Orchestrator gate threshold** | N/A | 0% fail; CI-enforced |
| **Redteam threshold** | N/A (no redteam in scope we found) | ≤10% overall, 0 high/critical |
| **Scenario format** | Not found (their eval harness is for GPT-4o intent scoring, not our citation/routing model) | YAML scenarios + JSON cassettes |
| **Hermetic mode** | Live GPT-4o eval (requires `az login`); `DefaultAzureCredential` fallback | Hermetic by default; `EVAL_MODE=live` opt-in |
| **Calibration doc** | Not found | `evals/calibration.json` + `calibration.md` with explicit recalibration protocol |
| **Eval coverage** | 97 GPT-4o tests (intent classification, PII, sentiment, urgency) | Citation gate + tool-routing gate + redteam gate |
| **Live mode pattern** | `az login` → run tests | `EVAL_MODE=live ORCHESTRATOR_URL=...` |

Their eval harness tests the _quality_ of the three-agent pipeline (does it classify intent correctly?). Ours tests _contract compliance_ (are responses cited? are tools routed correctly? do adversarial inputs fail safely?). Different goals, both valid. We have more structural rigor; they have more semantic coverage.

**Calibration discipline:** Our `calibration.md` explicitly prohibits loosening thresholds to make CI green. 47doors has no equivalent discipline documented. This is our advantage — see Section 9.

---

## 6. Workshop / Lab Structure

### Structure comparison

| Dimension | 47doors | Our app |
|---|---|---|
| **Format** | 8 progressive labs (Lab 00–07), each 30–120 min | 9 extension exercises (`docs/extensions/01–09`), each ships failing tests |
| **Sequencing** | Scaffolded: Lab 00 = setup, Lab 01 = concepts, Lab 06 = deploy | Unsequenced: teams pick; no mandatory progression |
| **Smoke test script** | `scripts/smoke-test.sh` — checks Python/Node/backend health/docs/mock mode | ❌ None |
| **Environment validation** | `scripts/validate-lab-00.sh` — versions, venv, deps, CORS, mock mode, ports | ❌ None |
| **Lab 00 (setup)** | 30-min prereq check with explicit `curl /api/health` step; voice env vars; VITE_API_BASE_URL gotcha documented | No equivalent "Day 0" script |
| **Lab 05 (orchestration)** | Teaches QueryAgent → RouterAgent → ActionAgent pipeline explicitly, with tests | Extension 05 (if it maps) teaches the pattern but via failing tests only |
| **Lab 06 (deploy)** | Full azd deployment lab with health checks, common pitfalls, `azd down` cleanup | No dedicated deploy lab; deploy is `azd up` in README |
| **Coach guide** | `FACILITATION.md` (8-hour timeline), `TROUBLESHOOTING.md` (per-lab), `ASSESSMENT_RUBRIC.md`, `TALKING_POINTS.md` | `.squad/` facilitation notes, no per-lab troubleshooting guide |
| **Demo runbook** | Referenced in CHANGELOG; `DemoPage.tsx` component exists | No dedicated demo runbook |
| **Start/solution pattern** | Labs 02/04/05/06/07 have both `start/` and `solution/` code | Extensions ship failing tests only; no solution code |

### The `smoke-test.sh` is the key adoptable artifact

`scripts/smoke-test.sh` (282 lines) does what no one on our team has taken the time to write:
1. Checks Python/Node/npm versions
2. Runs backend unit tests
3. Starts backend if not running
4. `curl /api/health` → exits non-zero if not 200
5. Checks `/docs` (FastAPI schema)
6. Validates mock LLM + KB services

If this had existed for us, Bug #11 (Hello World ACA placeholder) would have been caught in under 30 seconds after deploy. The current frontend rollback would have been caught before anyone tried to demo.

### `validate-lab-00.sh` as "Day 0 checklist"

Checks versions, virtualenv, dependencies, CORS config, mock mode, docs endpoint, open ports. Documents the `VITE_API_BASE_URL must be empty` gotcha that affects local dev proxy routing. We have hit proxy routing issues repeatedly. They documented the fix.

---

## 7. Process / Framework Comparison

### Framework artifacts

| Artifact | 47doors | Our app |
|---|---|---|
| **Squad framework** | ✅ `.squad/` with team.md, routing.md, agent charters | ✅ Same; richer per-agent history (parker, tank, switch, etc.) |
| **SpecKit** | ✅ `.specify/` with constitution.md, spec/plan/tasks templates | ✅ Same |
| **Copilot instructions** | `.github/copilot-instructions.md` = 1 line ("use Azure best practices") | `.github/copilot-instructions.md` = 300+ lines of architectural contracts |
| **CLAUDE.md** | Sparse; auto-generated with broken command syntax (`cd src [ONLY COMMANDS...]`) | N/A (we use copilot-instructions.md) |
| **Constitution** | `.specify/memory/constitution.md` — FERPA, accessibility, escalation, PII rules | Embedded in copilot-instructions.md |
| **Agent charters** | Morpheus (architecture), Tank (Python/Azure), Switch (React), Neo (security), Mouse (testing), Scribe (logging) | Same cast; Anvil is explicit |
| **Skill packs** | `.agent/skills/frontend-design/SKILL.md` | Skills system available |
| **MCP config** | `.copilot/mcp-config.json` (example only) | Not present |
| **Decisions log** | `.squad/decisions*.md` referenced | `.squad/decisions.md` referenced in calibration protocol |

### What their CHANGELOG tells us about lessons learned

The CHANGELOG entry on the voice bug is instructive:
> "Azure OpenAI Realtime API `/openai/realtime` direct-WS endpoint requires flat session-level fields; the nested `session.audio` block used by the WebRTC endpoint is rejected with `unknown_parameter: session.audio`. See `.squad/skills/azure-realtime-api-schema/SKILL.md`."

They documented the session.update format split as a **skill** (`.squad/skills/azure-realtime-api-schema/SKILL.md`). We fixed the same bug but left the knowledge in commit messages and PR descriptions, not in a reusable skill file. Next agent picking up a voice issue won't find it without grepping history.

### Their CLAUDE.md is worse than ours, but for an interesting reason

47doors' CLAUDE.md is auto-generated and broken (`cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]` is literal placeholder text). This tells you the SpecKit templating ran but wasn't curated. **Our copilot-instructions.md is hand-crafted and 10x more useful.** The irony is they have 8 labs teaching AI agent development but their own agent instructions are auto-generated noise.

---

## 8. Top 5 Adoptable Patterns (ranked)

### 1. `scripts/smoke-test.sh` → port as `scripts/smoke-test.ps1` (or sh)
**Effort:** S (2–4 hours). **Risk:** 🟢 additive.  
**What to port:** Check Python/Node versions, run `pip install -e .[dev] && pytest -q` for each service, `curl /api/health`, validate mock mode. Exit non-zero on any failure.  
**Would have prevented:** Bug #11 (Hello World). The current frontend rollback (would have caught it at deploy time, not 20 minutes later). Every future ACA placeholder regression.  
**Do it now.** This is the highest ROI item on this list. Sean should have a single command that tells him if the stack is alive.

### 2. `postdeploy` hook that validates `/api/health`
**Effort:** XS (30 minutes). **Risk:** 🟢 additive.  
**What to port:** Add a `postdeploy` hook to `azure.yaml` that `curl`s the deployed frontend URL and `/api/health` and exits non-zero if either fails.  
```yaml
hooks:
  postdeploy:
    run: |
      echo "Checking health..."
      curl -f ${AZURE_CONTAINERAPP_URL}/api/health || exit 1
      echo "Frontend: ${AZURE_FRONTEND_URL}"
```
**Would have prevented:** Bug #11. Slows down bad deploys, makes regressions visible immediately.

### 3. Dockerfile HEALTHCHECK for all services
**Effort:** XS (30 minutes). **Risk:** 🟢 additive.  
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/api/health || exit 1
```
47doors does this. ACA uses it for container readiness. Without it, ACA marks the container healthy as soon as the process starts, even if it's serving "Hello World."

### 4. `docker-compose.yml` for local full-stack dev
**Effort:** M (half day). **Risk:** 🟢 additive.  
47doors has one command to bring up the full stack locally with `MOCK_MODE=true`. We require running 3 FastAPI servers + npm. A compose file with mock env vars would let Sean (or a customer) do a pre-demo sanity check without Azure credentials.

### 5. Skill file for the Realtime API session.update schema
**Effort:** XS (1 hour). **Risk:** 🟢 additive.  
47doors stores the GA-nested vs. flat-field distinction as `.squad/skills/azure-realtime-api-schema/SKILL.md`. We fixed this bug but stored the knowledge nowhere reusable. Next voice regression, the next agent will rediscover it from scratch. Write the skill file.

---

## 9. Top 5 Things We Do Better (or differently for good reasons)

### 1. Citation contract is load-bearing
`ToolResponse.finalize()` + `warnings:["uncited"]` + 5% CI gate means a hallucinated response is structurally distinguishable from a cited one. 47doors has no citation concept. For a transit incident tool that tells riders what train to take, uncited answers are a liability. **Do not remove this, do not loosen the gate.**

### 2. Microservice specialist isolation
Our log-analyst and service-advisor are independently deployable, independently scalable, and independently testable. 47doors' monolith means a bug in the action agent takes down all functionality. Our pattern is more realistic for a production transit system and gives evaluators something concrete to discuss at the demo.

### 3. Hermetic eval discipline + calibration protocol
Our `calibration.json` + `calibration.md` with explicit recalibration protocol ("don't loosen the threshold to make CI green — fix the regression") is more rigorous than anything 47doors has. The `evals/` + `redteam/` dual-gate structure catches both correctness and adversarial robustness. 47doors tests intent classification quality but doesn't test for prompt injection, citation skipping, or hallucination.

### 4. Pluggable voice provider
`VOICE_PROVIDER=foundry_realtime|speech_services` behind `VoiceProvider/VoiceSession` abstractions means we can swap implementations without touching the orchestrator. 47doors hardcodes Azure OpenAI Realtime. For a demo environment where the Realtime endpoint might be unavailable, our fallback capability is real.

### 5. Comprehensive copilot-instructions.md
Our agent instructions document architectural contracts that matter: citation contract, tool registration, auth model, Cosmos partition keys, eval calibration rules. 47doors' equivalent is one line ("use Azure best practices"). Every agent that picks up a ticket in our repo has the full context. This is the reason the Squad framework has been productive despite high agent churn.

---

## 10. Tuesday Demo Gap Analysis

**T-63 hours. Current state:** broken text input (frontend rollback), Hello World risk on re-deploy, `service-advisor` possibly not in `azure.yaml`, 10 open PRs.

### Minimum viable demo path

**What "all features working" requires:**
- ✅ Voice (push-to-talk) functional
- ✅ Text input functional (PR #23 pattern, currently rolled back)
- ✅ Tool calls routing to log-analyst + service-advisor
- ✅ Citations present in response
- ✅ Frontend loads (not Hello World)

**What you actually need to demo confidently:**
- One voice turn that completes with a cited response ← the headline
- One text turn ← proves voice and text share the same path
- One service-advisor tool call visible in ToolCallPanel ← shows multi-specialist
- `/api/health` returns 200 on the deployed URL ← the kill-chain catch

### Ordered fix sequence (by risk, not alphabetical)

1. **Verify `service-advisor` is in `azure.yaml` on `main`.** If not, this is a P0 before any deploy. A tool registry that can't reach service-advisor will produce confusing failures at demo time.

2. **Cherry-pick or re-merge PRs #19, #21, #23, #25 onto `main`.** Do not build another image from anything but `main`. Tag the resulting commit.

3. **Add `smoke-test.sh` (even a 20-line version).** Minimum: `curl /api/health` returning 200. Run it after every deploy.

4. **Add `postdeploy` hook** (30-minute change). Fail the deploy step visibly if `/api/health` is not 200.

5. **Then `azd deploy` from `main` only.** Never from a feature branch.

### What to cut if time runs short

- Map visualization: not in scope, not demoed. Tell evaluators it's extension #10.
- Red team gate: skip for Tuesday, run after demo.
- Multi-region: not in scope.
- Mock mode validation: only matters for CI, not demo.

### If 47doors' demo approach is adoptable

They have a `DemoPage.tsx` component and a referenced demo runbook. Their smoke test (`scripts/smoke-test.sh`) is the right pre-demo checklist. Adopting their smoke test takes 2 hours and immediately gives Sean a go/no-go signal before showing the app to anyone.

**The minimum viable Monday morning action:** Write 30 lines of smoke test, add postdeploy hook, verify `service-advisor` in `azure.yaml`, deploy from `main`. That's 3 hours of work that eliminates the entire class of regressions you've been fighting.

---

*Comparison written against: 47doors `47doors-main` (extracted `.squad/files/47doors-ref/47doors-main/`) vs our app at `main` (bc53e11). 47doors CHANGELOG last entry: 2026-03-01 (359/359 backend tests passing).*
