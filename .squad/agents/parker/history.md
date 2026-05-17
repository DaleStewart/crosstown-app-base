# Parker — Agent History (Active)

Peter Parker / Spider-Man — Frontend developer. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/parker-history-2026-05-13-to-2026-05-15.md for archival. This file tracks current work.

---

## 2026-05-16 — T105 Phase 1 Batch Intake

**Task:** T105 (Medium) — Frontend Dockerfile HEALTHCHECK config (Phase 1 deploy-hygiene batch).

**Status:** ✅ Complete. Branch: chore/deploy-hygiene.

**Deliverable:**
- **apps/frontend/Dockerfile:** curl-based HEALTHCHECK probes http://localhost:3000/api/health (proxied by nginx to orchestrator /health). Every 30s, 5s timeout, 20s start period, 3 retries. curl adds ~2–3 MB to production image (acceptable).

**Verification:** Static syntax check passing. Docker daemon deferred (Windows environment).

**Batch outcome:** Anvil PR #29 review — **PASS ✅**. Six high-value checks all pass. Frontend HEALTHCHECK couples locally to orchestrator (soft concern; ACA Bicep probes override).

**Decision:** D-030 (merged into D-028).

## 2026-05-16 — Smoke-test retry for ACA revision-flip window

**Task:** Add bounded retry loop to smoke check 2 (and check 3 shape audit) in `scripts/smoke-test.sh` and `scripts/smoke-test.ps1`.

**Status:** ✅ Complete. Committed to main.

**Deliverable:**
- Check 2 (`GET /api/health → service:orchestrator`) now retries with exponential backoff (5s → 10s → 15s cap) for up to `SMOKE_RETRY_SECONDS` (default 90s) before hard-failing with the original grader-compatible message.
- Check 3 (direct orchestrator /health) only asserts HTTP 200, not the service field — no revision-flip exposure, no retry needed.
- PowerShell parity: same envelope in `smoke-test.ps1`, same `$env:SMOKE_RETRY_SECONDS` override.

## Learnings

- **ACA revision flips take 1–30 s to route traffic to the new revision.** Smoke gates that run immediately after `azd deploy` returns can hit the old revision and see stale JSON (e.g., `service=""`). The fix is a deadline-based retry loop (not a fixed sleep) so fast deploys stay fast and slow flips don't false-fail.

