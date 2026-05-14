# Session Resume Context — 2026-05-13 21:23 EDT

**Paused by:** Sean (segayle) for machine reboot
**Last session ID:** (this session)

## What we're building

**Azure Static Web App for the NYC MTA AI Agent Hackathon (May 19-20, 2026)** — coaches score teams on weighted /100 scorecards across two tracks (Azure/Foundry and Copilot Studio). Lives entirely in `apps/judging/`.

**⚠️ The repo root is an UNRELATED Container Apps stack — do not touch root `azure.yaml`, root `infra/`, or root `apps/{log_analyst,orchestrator,frontend,modules}`.**

## Where we are in the build

Three specialist agents were cast from the Avengers bench (active universe: MCU) and fanned out in parallel:

### 🏗️ Stark (Architect) — ✅ COMPLETE
Built `apps/judging/{infra,api,shared,staticwebapp.config.json}`:
- Bicep provisions **SWA Standard SKU** + **Cosmos serverless** (db `mtahack`, containers `teams`/`scores`/`events` partition `/track`)
- **Seven Functions** (Node 20 JS, SWA managed):
  - `teams-list` (GET /teams)
  - `teams-create` (POST /teams, admin only) — **may conflict on shared route with teams-list; fallback `teams/create` route documented**
  - `myscores` (GET /myscores)
  - `score-submit` (POST /score, server-authoritative total + returns 423 if locked)
  - `leaderboard` (GET /leaderboard, tie-breaker sort)
  - `lock` (POST /lock, admin only, persists as `lock-status-{track}` event doc)
  - `export` (GET /export, admin only, CSV)
- `shared/criteria.js` — dual-export (CJS for Functions + window global for frontend)
- `staticwebapp.config.json` — AAD identity provider with `{{TODO_TENANT_GUID}}` placeholder, role-gated routes
- All JS passes `node --check`. Criteria math smoke-tested.

### ⚙️ Okoye (Ops/Delivery) — ✅ COMPLETE
Built `apps/judging/{azure.yaml,scripts,README.md,.gitignore}`:
- `azure.yaml` — nested azd manifest, staticwebapp host, infra at `./infra`
- `scripts/seed-teams.js` — Node 20 built-ins (no deps), handles header validation, blank-row skip, cookie-auth and function-key auth paths, non-zero exit on failure
- `scripts/teams.csv` — header-only template (`name,track,members,room,slot`)
- `README.md` — local dev (`swa start`), `azd up`, AAD configuration, admin role assignment, seed flow
- `.gitignore` — `api/local.settings.json`

### ⚛️ Parker (Frontend) — ⏳ IN PROGRESS WHEN PAUSED
Was working on `apps/judging/src/{index,judge,admin}.html` + `styles.css`, `auth.js`, `toast.js`.

**Parker received THREE layered briefs during the run:**

1. **Initial spec** — vanilla HTML, no React, scorecard reference visuals
2. **frontend-design skill upgrade** — editorial polish, transit precision aesthetic, banned generic AI tells (no purple gradients, no rounded-2xl cards on white, no Inter/Roboto, no "Welcome back" wave emoji)
3. **🎯 MTA BRAND ALIGNMENT — THIS IS THE AUTHORITATIVE FINAL BRIEF:**

   **Typography:**
   - **Helvetica** (NOT Barlow) — `'Helvetica Neue', Helvetica, Arial, sans-serif`
   - Helvetica Bold for headings, signage, large numerics
   - Helvetica Regular for body
   - Helvetica Medium for labels/eyebrows

   **Colors — official MTA NYCT line palette:**
   - **MTA Blue `#0039A6`** — primary brand (REPLACES the earlier navy `#1A3A6B`)
   - **MTA Yellow `#FCCC0A`** — accent / N Q R W
   - **MTA Red `#EE352E`** — danger / 1 2 3 / "Needs work" tier
   - **MTA Green `#00933C`** — success / 4 5 6 / "Exceptional" tier
   - **MTA Orange `#FF6319`** — B D F M / "Developing" tier
   - **MTA Light Slate `#A7A9AC`** — dividers
   - **MTA Dark Slate `#2D2D2D`** — body text on light bg
   - Background: clean white `#FFFFFF` or `#F5F5F5`
   - Dark mode: `#0A0A0A` with MTA Blue popping forward

   **Tier color ladder:**
   - ≥90 Exceptional → green `#00933C`
   - ≥70 Strong → MTA Blue `#0039A6`
   - ≥50 Developing → orange `#FF6319`
   - <50 Needs work → red `#EE352E`

   **MTA bullet (roundel) motif:**
   - Solid colored circle with bold white letter/number inside (Helvetica Bold)
   - Use as a UI device for rank, tier pills, track tabs, team identifiers
   - Track tabs on admin: "A" bullet (blue) for Azure, "C" bullet (red/orange) for Copilot Studio
   - Rank column in leaderboard: render the rank as a bullet
   - Tier pills: MTA-style bullets, not generic capsule pills

   **Signage system patterns (Vignelli):**
   - Mono-color background panels with massive white Helvetica Bold text (landing page hero as a flat MTA-blue station-sign panel)
   - Strong horizontal rules — black 2px bars beneath section headers
   - Numbered grid — every team/criterion numbered (01, 02, 03)
   - Right-angle layouts, sharp corners (NO rounded corners over ~4px; bullets stay perfectly circular)
   - Generous white space — uncluttered like mta.info

   **Custom logo treatment** (avoid trademark): circle (MTA blue) with white Helvetica Bold "AI" inside, used like a subway line designation. Header of every page.

   **What changed from prior briefs:**
   - Barlow → Helvetica (drop Barlow font loading)
   - Navy `#1A3A6B` → MTA Blue `#0039A6`
   - Tier colors → MTA bullet colors
   - Rounded cards → sharp-cornered panels (bullets stay round)

   **What stayed from prior briefs:**
   - Tabler icons (sparingly, mono, in MTA blue or slate)
   - Light/dark mode support
   - Page-load staggered reveals (~80ms increments)
   - Scorecard component structure (criterion cards, 1-5 buttons, anchor descriptions, notes textarea)
   - The "wow, who built this?" target — editorial polish over feature density

## Backend contract Parker is integrating against

Auth: SWA-managed AAD at `/.auth/me` returns `{clientPrincipal: {userDetails, userRoles, claims}}`. Logout via `/.auth/logout`.

API routes (all auth-required, role gating in `staticwebapp.config.json`):
- `GET  /api/teams?track=azure|copilot` → `[{id,name,track,members[],room,slot}]`
- `GET  /api/myscores?track=...` → `[{teamId, criteria, notes, total, tier, ...}]`
- `POST /api/score` body `{teamId, track, criteria: {id:1-5}, notes: {id:string}}`
- `GET  /api/leaderboard?track=...`
- `POST /api/teams` (admin) body `{name, track, members[], room, slot}`
- `POST /api/lock` (admin) body `{track, locked:bool}`
- `GET  /api/export?track=...` (admin)

Criteria definitions loaded via `<script src="/shared/criteria.js"></script>` → `window.MTAHackCriteria = { CRITERIA, computeTotal, tier }`.

## Open work items (in priority order when resuming)

### 1. Confirm Parker delivered the frontend
Files expected: `apps/judging/src/{index,judge,admin}.html`, `styles.css`, `auth.js`, `toast.js`.

**Verify against the MTA brand brief:**
- Helvetica fonts (NOT Barlow)
- MTA Blue `#0039A6` (NOT navy `#1A3A6B`)
- MTA bullet roundels for ranks/tiers/track tabs
- Sharp corners (not pill-rounded except for bullets)
- Signage-style panels

If Parker is still idle when you resume, send her a follow-up; if she didn't finish, re-spawn with the MTA brand brief as the canonical design.

### 2. Run Scribe (was queued but not yet dispatched)
The session needs to be logged. Decision inbox entries from Stark and Okoye are waiting. Spawn Scribe with the standard prompt — she'll merge decisions, write orchestration log entries, update cross-agent history, and commit `.squad/` files.

### 3. gpt-4o → gpt-4.1 sweep (USER PRE-APPROVED)
User said "yes" to flipping `gpt-4o` to `gpt-4.1` across the **root project** (unrelated to apps/judging/). **Leave `gpt-4o-realtime-preview` alone** (explicit user instruction).

13 hits across 9 files:
- `.env.example:14`
- `apps/log_analyst/README.md:51`
- `apps/log_analyst/settings.py:28` (default value)
- `apps/orchestrator/settings.py:14` (default value)
- `docs/evals.md:34`
- `docs/voice.md:40` (excluding line ~51 which mentions realtime — verify before editing)
- `docs/voice.md:51` (verify — may need to skip if context is realtime)
- `evals/foundry_evaluators.py:13` (docstring) and `:46` (default)
- `evals/README.md:28`
- `infra/modules/foundry.bicep:68,71,76` ← **this is the real Azure deployment swap, not just docs**

Dispatch a separate agent for this — it's root-project work, not judging-app work. Suggest casting Banner from the bench OR using a fast haiku agent since it's mostly mechanical text substitution.

### 4. Playwright smoke tests (USER PRE-APPROVED)
User said "test it all using playwright when appropriate." Once Parker's frontend is verified, dispatch a tester.

Setup: `swa start ./src --api-location ./api` from `apps/judging/`. SWA CLI has an auth simulator at `http://localhost:4280/.auth/me` that lets tests inject `userRoles: ['admin']` for admin flows.

Tests should cover:
- Landing → judge picker → scorecard submit flow
- Admin leaderboard render + lock toggle (with mocked admin role)
- `criteria.js` `computeTotal` math against known inputs (5×5 → 100, mixed → check weights)
- Tier color thresholds (≥90/≥70/≥50/<50)
- Lock state → score submit returns 423 with "locked" banner

Place tests at `apps/judging/tests/`. Add a `playwright.config.js` and a `package.json` if needed for the test runner only (still no build step for the app itself).

Bruce Banner is the natural cast pick from the bench ("Data Science & Evaluation — golden scenarios, eval gates").

### 5. Commit + push
Once everything verifies:
- Stage only files inside `apps/judging/`, `.squad/`, `reference/`
- Commit message: something like `feat: add MTA hackathon judging app (apps/judging/)`
- Push to `origin` → `https://github.com/DevPost-Test-Hackathon/crosstown-app.git`
- **Reminder:** the PAT `ghp_0zDQ…` used earlier in this session was pasted in chat history and should be rotated by the user. Auth is currently cached in git credential manager; pushes will work without re-auth.

## Snapshot when paused

- 37 files written under `apps/judging/` (~0.13 MB)
- 5 untracked dirs: `.squad/agents/{okoye,parker,stark}/`, `apps/judging/`, `reference/`
- Nothing modified — all additive
- Decision inbox files written by Stark + Okoye (Parker possibly pending)
- Stark + Okoye agents are idle (done). Parker's last state was running.

## Roster (Avengers)

Active:
- 🏗️ T'Challa — Lead (pre-existing)
- 📋 Shuri — Scribe (always Scribe)
- 🏗️ Tony Stark — Architect (hired this session)
- ⚛️ Peter Parker — Frontend (hired this session)
- ⚙️ Okoye — Ops & Delivery (hired this session)
- 🔄 Ralph — Work Monitor

Bench (available for hire):
- Natasha Romanoff — Security & red team
- Bruce Banner — Data science & evaluation **← natural pick for Playwright tester**
- Sam Wilson — Observability
- Wanda Maximoff — Anomaly detection
- Stephen Strange — Architectural reviewer
