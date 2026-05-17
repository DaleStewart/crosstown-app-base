# Bruce Banner — Archive (Phase 0)

## Summary (2026-05-13 through 2026-05-15)

**Phase 0:** Comprehensive test authoring for MTA AI Hackathon judging app. Authored Playwright E2E + unit test suite covering auth (AAD), judge scorecard, leaderboard (rank order, tie-breaking, tier feedback), admin console (lock/unlock, CSV export), edge cases (timeout recovery, offline), accessibility (keyboard nav, ARIA), and visual regression (MTA brand compliance).

Key decisions:
- Interception-first test strategy (`page.route()` stubs for /.auth/me + /api/*, deterministic fixtures)
- SWA CLI auth simulator override (fixed clientPrincipal per test vs. cookie state)
- Unit smoke via plain Node.js (criteria.js UMD export test)
- 10/10 E2E pass after fixing stale test issues (fetch stub, CSS overlay force-click)

Key learnings:
- Production code pinning: landing h1 "Coach Scoring<br>Console", /api/score route, #btn-* button ids, lock toggle uses window.confirm()
- Playwright best practice: mock SWA auth at test level rather than relying on `.auth/me` cookie capture
- Function names in SWA (/api/score) differ from folder names (score-submit/); use runtime routes, not folder structure

**Phase 1 (2026-05-15 through 2026-05-16):** Post-merge verification (Realtime + Spec Kit → no regressions). Bug diagnostics and fixes:
- Bug #10 (PR #16): orchestrator/agent/tools.py schema passthrough; detect_pattern now receives proper input_schema from log-analyst
- Bug #12 resolution (no code): 422 was correct validation; client payload used `message` instead of `text`
- Bug #7 escalated (out of scope)
- T007-followup: hand-crafted service-advisor cassettes (OS-009/010/011) — eval gate unblocked, 11/11 PASS

Archive entry date: 2026-05-16
