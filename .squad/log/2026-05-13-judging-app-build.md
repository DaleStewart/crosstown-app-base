# Session Log · 2026-05-13 · Judging App Build

**Date:** 2026-05-13
**Session ID:** judging-app-build
**Lead:** T'Challa (via Scribe Shuri)
**Duration:** Parallel batch (Stark/Parker/Okoye) + parallel batch (Banner/Maximoff/Scribe logging)

## Parallel Batch 1: Judging App Scaffold

### Stark (Architect) — Infrastructure & API

Built `apps/judging/` as a self-contained SWA + Functions + Cosmos workload:
- 7 Functions (teams-list, teams-create, myscores, score-submit, leaderboard, lock, export) all Node.js, all passed syntax check
- Cosmos partition key `/track` ensures O(scores-in-track) queries on serverless pricing
- SWA managed Functions (no separate Function App resource)
- Decision **D-002** logged and adopted

**Output:** `apps/judging/infra/main.bicep`, `apps/judging/api/{7 functions}`, `apps/judging/shared/criteria.js`

### Parker (Frontend) — Design & UI

Built `apps/judging/src/` with full MTA brand alignment (v1 → v2 editorial → v3 brand override):
- 3 HTML pages (index, judge, admin)
- 4 support modules (auth.js, toast.js, criteria-ui.js, styles.css)
- **Brand v3:** Helvetica Neue (no web fonts), MTA route palette (navy `#0039A6`, red `#EE352E`, green `#00933C`, orange `#FF6319`, yellow `#FCCC0A`), sharp corners (2px buttons, 0px cards), route-bullet primitives
- Tier ladder: Exceptional (≥90, green), Strong (≥70, navy), Developing (≥50, orange), Needs work (<50, red)
- Decision **D-003** logged and adopted

**Output:** `apps/judging/src/{3 HTML, 4 JS/CSS}`

### Okoye (Operations) — Deployment & DevOps

Built operations scaffold:
- `apps/judging/azure.yaml` (azd manifest, separate from root)
- `scripts/seed-teams.js` + `scripts/teams.csv` (test data)
- `apps/judging/README.md` (deployment walkthrough, local setup)
- `.gitignore` updates for secrets & build artifacts
- Decision **D-004** logged and adopted

**Output:** `apps/judging/azure.yaml`, `scripts/seed-teams.js`, `scripts/teams.csv`, `README.md`, `.gitignore` updates

## Parallel Batch 2: Testing & Model Sweep

### Banner (Tester) — Playwright Test Suite

Built comprehensive test coverage under `apps/judging/tests/`:
- Auth tests (AAD login, token refresh, logout, expiry)
- Judge interface (team picker, criterion scoring, tier feedback)
- Leaderboard (rank order, tie-breaking, tier labels, locked state)
- Admin console (lock/unlock tracks, CSV export)
- Edge cases (concurrent submissions, session timeout, offline recovery)
- Accessibility (keyboard nav, ARIA labels, contrast)

**Output:** `apps/judging/tests/{test files}` (Playwright framework, mocked Cosmos/Graph)

### Maximoff (Anomaly/QA) — Model Migration

Swept gpt-4o → gpt-4.1 across root project:
- Updated `.github/workflows/*.yml` (model refs in CI/CD)
- Updated `azure.yaml` (orchestrator/analyzer model param)
- Updated root `*.md` documentation
- Updated env templates
- Scope exclusion: `apps/judging/` untouched, `.squad/` untouched

**Output:** Root project ready for gpt-4.1 inference

## Major Design Pivots

1. **Frontend v1 → v2:** Editorial pass added Barlow Semi Condensed typography, diagonal subway-rule atmosphere, motion (stagger reveal, tier flash, score button press), dark mode
2. **Frontend v2 → v3:** Brand override to MTA Helvetica + NYCT route palette; sharp corners everywhere; removed web fonts; added route-bullet primitives (`.bullet.sm/.md/.lg/.xl/.xxl`)

## Decisions Logged & Adopted

- **D-002:** Judging app layout at `apps/judging/` (isolation, single source of truth for criteria, SWA managed Functions)
- **D-003:** Frontend design v3 (MTA Helvetica + route palette, sharp corners, brand compliance)
- **D-004:** Separate `azure.yaml` inside `apps/judging/` (lifecycle isolation, different service topology, team parallelism)

## Casting

Five agents hired from bench this session:
1. **Stark** (Tony Stark / Iron Man) — Architect
2. **Parker** (Peter Parker / Spider-Man) — Frontend
3. **Okoye** — Operations
4. **Banner** (Bruce Banner / Hulk) — Tester
5. **Maximoff** (Wanda Maximoff / Scarlet Witch) — Anomaly/QA

All added to `.squad/casting/registry.json` with `legacy_named: false`, `status: 'active'`, `created_at: 2026-05-13`. History snapshot recorded in `.squad/casting/history.json`.

## Next Steps

1. **Stark (Infra):** Finalize azd integration vs. standalone GH Actions workflow; replace `{{TODO_TENANT_GUID}}`; document admin-role grant path
2. **Banner (QA):** Integrate Playwright into CI/CD; set up `npm run test:unit` (fast) and `npm run test:e2e` (optional emulator)
3. **Maximoff (QA):** Verify gpt-4.1 availability in target Azure subscription; test orchestrator/analyzer with new model

---

**Logged by:** Scribe (Shuri)
**Session type:** Resumption post-reboot (Stark/Parker/Okoye completed, Banner/Maximoff/Scribe concurrent)
