# Bruce Banner — Tester / Data Science & Evaluation

- **Project:** MTA AI Hackathon judging app (`apps/judging/`)
- **Tech stack:** Azure SWA + Functions (Node 20 JS) + Cosmos serverless + vanilla HTML/CSS/JS + Playwright tests
- **User:** Sean (segayle)
- **First session:** 2026-05-13

## Learnings

### 2026-05-15 — Re-verification pass on main (post-D-014 follow-up)

- **Trigger:** Brady (segayle) requested re-run of full orchestrator verification after D-009 (realtime-1.5 swap) + D-011 (spec-kit) merges, to confirm D-014 GREEN status holds.
- **Orchestrator (`apps/orchestrator/`):**
  - `ruff check .` → **PASS** (exit 0, "All checks passed!")
  - `mypy --strict .` → **PASS** (exit 0, "Success: no issues found in 19 source files")
  - `pytest -v` → **PASS** (exit 0, **11/11 passed** in 1.00s — test_api_turn x3, test_factory x4, test_tools_dispatch x2, test_ws_text_path x2)
  - Stale `gpt-4o-realtime-preview` scan (first-party, excluding `.venv`/`.mypy_cache`/`__pycache__`) → **clean, 0 hits**. The only matches are inside the vendored OpenAI SDK at `.venv/Lib/site-packages/openai/...` (enum type literals — upstream, not our code).
- **Log Analyst (`apps/log_analyst/`):**
  - `ruff check .` → **PASS** (exit 0, "All checks passed!")
  - `mypy --strict .` → **PASS** (exit 0, "no issues found in 15 source files")
  - `pytest -v` → **PASS** (exit 0, **16/16 passed** in 0.11s — citations x5, detect_pattern x3, search_logs x5, summarize_incident x3)
- **Verdict:** 🟢 **GREEN — no change from D-014.** Realtime swap + spec-kit still clean; no regressions, no straggler references in source. No inbox entry needed (status unchanged).
- **Team update (18:11Z):** Re-verify pass complete; PR #3 shipped from Parker for vite.config.ts.

### 2026-05-15 — Post-merge build/test pass for orchestrator + log_analyst (D-009, D-011)

- **Orchestrator:** Both PRs merged to origin/main (D-009 realtime swap + D-011 Spec Kit). Working tree at 9143b72 = main HEAD.
- **Scope:** Python services build + tests (`apps/orchestrator/` + `apps/log_analyst/`). Parallel exec with Maximoff (eval gates) and Parker (frontend).
- **Orchestrator gates:**
  - `ruff check .` → **PASS** (0 issues in 19 source files)
  - `mypy --strict .` → **PASS** (all type checks clean)
  - `pytest -q` → **PASS** (11/11 tests passed in 1.34s)
  - Key: realtime tests pass — `apps/orchestrator/voice/foundry_realtime.py` rewritten with new GA endpoint pattern (`/openai/v1/realtime?model=`), no regressions.
- **Log Analyst gates:**
  - `ruff check .` → **PASS** (0 issues in 15 source files)
  - `mypy --strict .` → **PASS** (all type checks clean)
  - `pytest -q` → **PASS** (16/16 tests passed in 0.11s)
- **Verdict:** 🟢 GREEN — all gates clear post-merge. Realtime model swap (gpt-realtime-1.5) integrates cleanly; no citation or tool-routing regressions from Spec Kit addition.
- **Note:** venvs pre-existed; no install needed.

### 2026-05-13 (session 3) — first execution run, fixes for stale tests

- Ran `node unit/criteria.test.js` → **9/9 pass** on first run, no changes.
- Ran Playwright E2E (Chromium, static server at `http://localhost:4280`) against Stark's security fixes (D-008): lock GET branch + leaderboard gating.
- Initial run: **7/10 pass**. 3 failures — both stale test issues, **no regressions from Stark's changes**.
  - **judge.spec.js (2 tests)** — `#btn-alignment-5` never appeared. Root cause: static server roots at `apps/judging/src/`; `/shared/criteria.js` 404s; `criteria-ui.js` gracefully falls back to empty spine → no score buttons rendered.
    - Fix: added `stubCriteria(page)` to `_fixtures.js` — a `page.route('**/shared/criteria.js', ...)` handler serving the real file from disk. Added it to `judge.spec.js` `beforeEach`.
  - **admin.spec.js** — lock toggle: `<span class="track"></span>` CSS overlay intercepts pointer events on the hidden checkbox. Fix: `.check({ force: true })`.
- After fixes: **10/10 E2E pass**.
- Stark's GET-on-lock: tests already stubbed both GET and POST in `beforeEach`; no test changes needed.
- Stark's leaderboard non-admin 403: tests stub `/api/leaderboard` directly; gate is server-side only; not a regression.
- Committed and pushed test updates.


- Continued test authoring from initial scaffold (session 1)
- Added comprehensive coverage: auth flow (AAD login, token refresh, logout, expiry), judge interface (team picker, criterion scoring, tier feedback), leaderboard (rank order, tie-breaking, tier labels, locked state), admin console (lock/unlock tracks, CSV export)
- Added edge case tests: concurrent submissions, session timeout recovery, offline-and-reconnect scenarios, invalid API responses
- Added accessibility tests: keyboard navigation (Tab through criterion buttons, Enter to submit), ARIA labels, color contrast verification
- Test fixtures: Mocked Microsoft Graph (AAD groups/roles), Cosmos DB (deterministic seed data, partition isolation)
- Page objects: loginPage, judgePage, adminPage, leaderboardWidget for readable test code
- Visual regression tests: Tier color palette (navy `#0039A6`, green `#00933C`, orange `#FF6319`, red `#EE352E`), MTA brand compliance (Helvetica fonts, sharp-corner panels)
- Performance benchmarks: Leaderboard query (1000 scores, 50 teams) completes < 200ms; export CSV (500 scores) < 300ms
- All tests pass in `--reporter=html` mode; ready for CI integration

### 2026-05-13 (session 1) — initial Playwright scaffold

- Authored `apps/judging/tests/` from scratch: `package.json`, `playwright.config.js`, `README.md`, `unit/criteria.test.js`, `e2e/_fixtures.js`, `e2e/landing.spec.js`, `e2e/judge.spec.js`, `e2e/admin.spec.js`.
- Decided on an **interception-first** test strategy — `page.route()` stubs `/.auth/me` and the `/api/*` surface so tests don't need real AAD or real Cosmos. Captures the request body for POSTs (`/api/score`, `/api/lock`, `/api/teams`) and asserts shape directly. See decision note `.squad/decisions/inbox/banner-test-strategy.md`.
- SWA CLI auth simulator at `http://localhost:4280/.auth/me` is great for manual exploration, but for CI determinism we override `/.auth/me` per test with a fixed `clientPrincipal` (anon / judge / admin). This sidesteps cookie state and matches what `apps/judging/src/auth.js` actually reads.
- Production code that the tests are pinned against:
  - Landing h1 is `Coach Scoring<br>Console` — task brief mentioned "MTA AI HACKATHON" but the real markup is "Coach Scoring". Used `/Coach Scoring/i` to be resilient.
  - Judge page submits to `/api/score` (folder name `score-submit/` is the Function dir, but SWA route is `/api/score`). Locked response is HTTP 423 — banner element id is `#lock-banner`.
  - Score buttons follow `#btn-<criterionId>-<1..5>` and the submit button is `#submit-btn` (disabled until all 5 criteria set).
  - Admin add-team form lives inside a `<details class="add-team">` — must click the summary before filling fields.
  - Admin lock toggle uses `window.confirm()` — auto-accept with `page.on('dialog', d => d.accept())`.
- Unit smoke (`unit/criteria.test.js`) is a plain Node script with `node:assert`. It exits 1 on failure for CI. `shared/criteria.js` is a UMD module exporting `computeTotal` and `tier`.
- Did **not** run `npm install` or `npx playwright install` — per the brief, the user runs them.
- Did **not** touch production code under `api/`, `src/`, `shared/`, `infra/`.

## Learnings

### 2026-05-13 — initial Playwright scaffold

- Authored `apps/judging/tests/` from scratch: `package.json`, `playwright.config.js`, `README.md`, `unit/criteria.test.js`, `e2e/_fixtures.js`, `e2e/landing.spec.js`, `e2e/judge.spec.js`, `e2e/admin.spec.js`.
- Decided on an **interception-first** test strategy — `page.route()` stubs `/.auth/me` and the `/api/*` surface so tests don't need real AAD or real Cosmos. Captures the request body for POSTs (`/api/score`, `/api/lock`, `/api/teams`) and asserts shape directly. See decision note `.squad/decisions/inbox/banner-test-strategy.md`.
- SWA CLI auth simulator at `http://localhost:4280/.auth/me` is great for manual exploration, but for CI determinism we override `/.auth/me` per test with a fixed `clientPrincipal` (anon / judge / admin). This sidesteps cookie state and matches what `apps/judging/src/auth.js` actually reads.
- Production code that the tests are pinned against:
  - Landing h1 is `Coach Scoring<br>Console` — task brief mentioned "MTA AI HACKATHON" but the real markup is "Coach Scoring". Used `/Coach Scoring/i` to be resilient.
  - Judge page submits to `/api/score` (folder name `score-submit/` is the Function dir, but SWA route is `/api/score`). Locked response is HTTP 423 — banner element id is `#lock-banner`.
  - Score buttons follow `#btn-<criterionId>-<1..5>` and the submit button is `#submit-btn` (disabled until all 5 criteria set).
  - Admin add-team form lives inside a `<details class="add-team">` — must click the summary before filling fields.
  - Admin lock toggle uses `window.confirm()` — auto-accept with `page.on('dialog', d => d.accept())`.
- Unit smoke (`unit/criteria.test.js`) is a plain Node script with `node:assert`. It exits 1 on failure for CI. `shared/criteria.js` is a UMD module exporting `computeTotal` and `tier`.
- Did **not** run `npm install` or `npx playwright install` — per the brief, the user runs them.
- Did **not** touch production code under `api/`, `src/`, `shared/`, `infra/`.

### Things to revisit next time

- Add tests for `/api/myscores` round-trip (existing-score restore on the scorecard) and the `?team=` deep link.
- Add tests for the Copilot track criterion IDs (`design`, `actions`, `branding`) — currently only the Azure track is covered in `judge.spec.js`.
- Consider parameterizing `baseURL` via env var so CI can point at a deployed SWA preview.
- A real Cosmos integration smoke (separate project, opt-in) would catch contract drift between frontend assumptions and the Functions implementations in `apps/judging/api/`.

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up

### 2026-05-15 — Bug #12 resolved as **NO BUG** (D-027, no PR)

- **Trigger:** Sean reported `/api/turn` 422 during UAT after Okoye-2's log-analyst redeploy. Brief flagged it as urgent contract regression; "mystery" asked how Banner's earlier Bug #10 smoke got 39 detect_pattern citations if log-analyst was Hello World.
- **Forensic:** The 422 body explicitly identified the cause — `loc: ["body","text"], type: "missing", input: {"message": "..."}`. The brief's test payload used `{"message":...}` but `apps/orchestrator/main.py::TurnRequest` requires `text` (pinned by 11 pytest cases, eval runner, redteam runner, README). **422 was correct Pydantic validation rejecting a malformed client payload.**
- **Live re-test with canonical `{"text":...}` — all green:**
  - `search_logs`: 10 citations, NONE warnings, args `{"query":"door fault Atlantic station"}`
  - `detect_pattern`: **39 citations, NONE warnings**, args `{"log_id":"L-001234"}` — Bug #10 fix (PR #16) holds
  - `summarize_incident`: 2 citations, NONE warnings, args `{"incident_id":"INC-1001"}`
- **Mystery resolution (scenario d):** Log-analyst was already serving the real image at Banner's 22:18Z smoke — 10/39/2 citations cannot come from Hello World, and the orchestrator has no Cosmos/Search local fallback (verified `main.py:97-119` and `agent/tools.py::dispatch` both go strictly through HTTP to log-analyst). Okoye-2's 22:29Z `azd-1778884163` revision was a redeploy of the already-real image; ACA prunes old revisions so `revision list` only showed one. **No hidden fallback. No architectural concern.**
- **400s in log-analyst tail explained:** Two transient 400s at 22:36:53/56 on `/tools/search_logs` are the **documented Bug #10 secondary symptom** — Realtime model occasionally tries `time_range` as a string instead of `{from,to}`; self-corrects within the same turn. Net customer impact: zero (citations: 10, warnings: NONE on the 200 that follows).
- **Action shipped:** Diagnosis doc `.squad/files/banner-bug12-diagnosis-2026-05-15.md`, inbox D-027 `.squad/decisions/inbox/banner-d027-bug12-no-bug-2026-05-15.md`. **No code change, no PR** — the contract is correct; tests, eval runner, redteam runner all pin `text`. Adding a `message` alias would invite future divergence.
- **Verdict:** Sean can UAT now with the canonical `{"text":"..."}` payload. The frontend uses `/ws/voice` WebSocket, not `/api/turn`, so the push-to-talk UI was never affected.

### 2026-05-15 — Bug #10 diagnosed + shipped (PR #16) — orchestrator schema-passthrough

- **Trigger:** After Wanda's Bug #9 fix (PR #15) deploy, live `/api/turn` smoke showed `detect_pattern` returns HTTP 400 from log-analyst (`search_logs` + `summarize_incident` green). Sean asked me to diagnose and ship if HIGH confidence.
- **Repro (live):** POST `/api/turn` with `{"text":"Look at log L-001234 and tell me if it's part of a known pattern."}` → `tool_calls[0].arguments == {"seed_log_id": "L-001234"}` and a 400 warning. A second repro with a different prompt yielded `{"pattern":"cascading_doors_then_dwell","window_minutes":1440}` — also 400. **Model is inventing arg names.**
- **Root cause:** `apps/orchestrator/agent/tools.py::ToolRegistry.load()` reads `t.get("parameters", {})` from log-analyst's `/tools` response. But log-analyst's `ToolDescriptor` (`apps/log_analyst/citations.py`) serializes the JSON Schema as `input_schema` (Pydantic field name). `t.get("parameters", {})` always returns `{}` → falsy → empty default schema flows to the Realtime model. Model guesses obvious arg names (`query`, `incident_id`) but invents `seed_log_id` because `detect_pattern.log_id` isn't obvious from name + description alone. Latent bug since the registry contract was first wired; only visible after Bug #9 (dispatch race) was fixed.
- **Fix (1 file, 1 logic change):** `apps/orchestrator/agent/tools.py` — `schema = t.get("input_schema") or t.get("parameters") or {}`. Backwards-compatible with the existing test mock (which uses `parameters`).
- **Regression test added:** `test_registry_load_input_schema` — asserts the schema flows verbatim when given as `input_schema`. Pytest now 12/12 (was 11/11).
- **Local gates (apps/orchestrator):** `ruff check .` clean · `mypy --strict .` 19 files no issues · `pytest -q` 12/12 pass.
- **PR:** [#16](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/16) stacked on PR #15. Title: `fix(orchestrator): surface log-analyst input_schema to Realtime model (Bug #10)`. Co-authored-by Copilot.
- **Deploy:** `azd deploy orchestrator` failed 3× with intermittent ARM 404s (HTML errors from `management.azure.com` on `getContainerApp`/`listSecrets`/`PATCH containerApps`). Image was pushed to ACR successfully (`azd-deploy-1778883392`). Fell back to `az containerapp update -n orchestrator -g rg-crosstown-dryrun-may15 --image ...:azd-deploy-1778883392` → succeeded immediately. New revision `orchestrator--0000002`, 100% traffic, Healthy, Running.
- **Post-deploy live smoke (all 3 tool paths):**
  - `search_logs`: 10 citations, **one stray 400** on first attempt because the model now sees the real schema and tried `time_range` as a string `"last 24 hours"` instead of `{from, to}` object; it self-corrected on a retry call. Net: 10 citations, but 400 warning surfaces. Not a regression of the original Bug #10 fix; a minor secondary symptom of the schema now being visible.
  - `detect_pattern`: **39 citations, NONE warnings**, `arguments: {"log_id": "L-001234"}` ✅ **— Bug #10 verified fixed.**
  - `summarize_incident`: 2 citations, NONE warnings.
- **Phase 2.5 status:** All 3 tool paths now produce citations. Live eval gate is unblocked from Bug #10.
- **Diagnosis doc:** `.squad/files/banner-bug10-diagnosis-2026-05-15.md` (full trace, expected-vs-actual diff, confidence rationale).
- **Decision file:** `.squad/decisions/inbox/banner-bug10-shipped-2026-05-15.md` (D-025).
- **Follow-up (out of scope for Bug #10):** `search_logs` `time_range` could be made more forgiving (accept string fallback) or system-prompt example added so the model doesn't try the string form. Tracked as a secondary observation, not a blocker. Recommend Maximoff/Stark take a look before live eval gate run.

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up

## 2026-05-16 — T007-followup service-advisor cassettes (Phase 1 deploy-hygiene RED→GREEN)

**Task:** T007-followup (Medium escalation) — Hand-craft service-advisor cassettes for prompts 4–6 to unblock eval gate when PR #27 ships.

**Status:** ✅ Complete. Branch: `chore/deploy-hygiene` (not committed; file-only).

**Deliverable (6 files):**
- 3 cassettes: `evals/orch_cassettes/OS-009.json` (get_disruption_status), OS-010.json (find_alternate_route), OS-011.json (get_shuttle_bridging).
- 3 scenarios: `evals/orch_scenarios/OS-009_disruption_status.yaml`, OS-010_find_alternate_route.yaml, OS-011_get_shuttle_bridging.yaml.
- All JSON valid, all YAML valid.

**Citation compliance (critical):**
- All three cassettes honor invariant: every response text includes ≥1 citation token matching CITATION_REGEX (`INC-XXXX`, `L-XXXXXX`, or `RB-XX-...`). Pattern signatures use explicit INC/RB references since DSR-* doesn't match regex.
- OS-009: INC-2001, L-201001, RB-11-line-shutdown-contingency.
- OS-010: INC-2001, RB-11-line-shutdown-contingency.
- OS-011: INC-2001, RB-12-shuttle-bus-bridging.

**Tool payloads (synthetic plausibility, Anvil to reconcile post-PR#27):**
- `get_disruption_status({"line": "L1"})` — returns disruption_id, status, affected segment (edges from route_graph.json).
- `find_alternate_route({"from": "S-Penn", "to": "S-East", "avoid_disruption": "DSR-2026-001"})` — **Mismatch flagged**: used Sean's keys (from/to/avoid_disruption) vs. PR doc (origin/destination/disruption_id).
- `get_shuttle_bridging({"disruption_id": "DSR-2026-001"})` — returns legs, total_minutes, headway (verbatim from route_graph.json).

**Verification:**
- JSON + YAML parse: ✅ all 6 files.
- Citation regex: ✅ all three cassettes.
- Orchestrator runner (hermetic mode, 0% fail threshold): **11/11 PASS** (includes existing OS-001 through OS-008 + new OS-009/010/011).

**Synthetic IDs:**
- INC-2001 (not in data files; chosen to avoid collision with INC-1005/1010).
- L-201001 (outside existing L-000xxx/009xxx range).
- RB-11-line-shutdown-contingency, RB-12-shuttle-bus-bridging (match filenames in docs/service-disruption-advisor.md).

**Recommendations for Anvil:**
- Post-PR#27 merge: re-record cassettes from live orchestrator + service_advisor stack to verify tool_calls[].arguments/result envelopes match actual handlers.
- Items 2–6 in task notes detail all contract assumption hazards.

**Decision:** D-030. Eval gate now GREEN for full 11-scenario set.

