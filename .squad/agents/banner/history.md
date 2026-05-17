# Bruce Banner — Agent History (Active)

Bruce Banner — Tester / Data Science & Evaluation. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/banner-history-2026-05-13-to-2026-05-15.md for archival. This file tracks current work.

---

## 2026-05-17 — Live-deploy Playwright happy-path gate

**Task:** Add `e2e/happy-path.spec.ts` (5 scenarios against live ACA deploy) + wire into CI via `playwright-live.yml`. Intentionally red until PRs #21, #22, #23 merge.

**Status:** Complete. PR opened as draft.

**Key learnings:**
- The existing `mic-button.spec.ts` was never wired into CI — confirmed that Playwright config had no `projects:` block (defaulted to all browsers). Added explicit `projects: [chromium]` and `retries`.
- `playwright test --list` is a fast config-validity check that doesn't require network access.
- `workflow_run:` trigger needs an `if:` guard to avoid running when the upstream workflow fails.
- The app title at deploy time is "MTA Hackathon — Voice Demo" (from `index.html`), not "Crosstown". Test checks for `MTA|Hackathon` regex match and rejects any `Vite + React` generic title.
- Citation locator strategy: fan out across `data-testid*="citation"`, class pattern, `L-\d{4,}` text pattern — resilient to whichever shape the open PRs ship.
- `.squad/decisions/inbox/` is gitignored (runtime state); decision file exists locally only.

**Decision filed:** `.squad/decisions/inbox/banner-playwright-live-gate.md` (local only)

---

## 2026-05-16 — Phase 1 Batch Intake (Scribe)

**Task:** Phase 1 scribe intake for deploy-hygiene batch (Decisions D-020, D-021, D-025, D-027 from Banner authored; merged + archived).

**Status:** Complete. Batch cleared by Anvil.

**Decisions merged:**
- D-020: Orchestrator aiohttp dep (Banner)
- D-021: Bug #6 fixed, Bug #7 escalated (Banner)
- D-025: Bug #10 shipped (Banner)
- D-027: Bug #12 — no-bug (Banner)

**Batch outcome:** Anvil PR #29 review PASS. Smoke test validated; eval gate 11/11 pass on cassettes; all orchestrator+log-analyst contracts verified.

**Decision:** Merged into archive.
