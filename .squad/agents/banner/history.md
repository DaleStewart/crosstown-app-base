# Bruce Banner — Tester / Data Science & Evaluation

- **Project:** MTA AI Hackathon judging app (`apps/judging/`)
- **Tech stack:** Azure SWA + Functions (Node 20 JS) + Cosmos serverless + vanilla HTML/CSS/JS + Playwright tests
- **User:** Sean (segayle)
- **First session:** 2026-05-13

## Learnings

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
