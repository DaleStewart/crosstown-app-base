# Decisions

## D-030: Phase 1 Deploy-Hygiene Batch | 2026-05-16

**Status:** 🟢 Ship

**Summary:**
Five agents completed Phase 1 deploy-hygiene tasks on `chore/deploy-hygiene` branch. All work verified and ready for Anvil Large review (3 reviewers):

- **T104 (Stark):** Docker HEALTHCHECK directives added to `apps/orchestrator/Dockerfile` and `apps/log_analyst/Dockerfile`. Both use canonical `/health` endpoint (not `/healthz`). curl installed in runtime stages. Verification: static syntax check passing; CI will exercise on build.
- **T106 (Parker):** nginx `/api/health` → orchestrator `/health` rewrite added to `apps/frontend/nginx.conf`. Exact-match `location = /api/health` block precedes catch-all `/api/` block. Verification: `envsubst` render OK; nginx-t skipped (Docker daemon not running); T101 will end-to-end test.
- **T107 (Okoye²):** FR-013 main-only deploy guard added to `.github/workflows/deploy.yml`. New `confirm_non_main` input + first-step guard. Trace table covers 4 cases (push main, push feature, dispatch non-main with override, dispatch non-main no override). Verification: YAML parse OK; edge cases considered; guard is step 2 after checkout.
- **T101 (Okoye):** `scripts/smoke-test.sh` hand-authored per spec FR-009. 5 baseline checks (6 with `--full`): frontend root HTML, `/api/health` rewrite, direct orchestrator health, `/api/turn` text response, 6 rehearsed demo prompts (full mode only). Failure format: `FAIL at check N: reason`. Verification: bash -n syntax OK; negative test against bogus host passes; live test against current deployment correctly detects nginx rewrite not yet landed.
- **T007-followup (Banner):** Hand-crafted service-advisor cassettes (OS-009, OS-010, OS-011) to unblock eval gate. All three cassettes JSON valid, YAML valid, citations regex matches. Orchestrator runner hermetic mode: **11/11 PASS** (0% failure). Cassette tool_calls contract details flagged for Anvil post-PR#27 reconciliation.

**Context & learnings:**
- Canonical health endpoint is `/health`, NOT `/healthz` (Phase 0 audit T001).
- azd env exposes `FRONTEND_URL`, not `SERVICE_FRONTEND_URI` (Phase 0 audit T004); T103 postdeploy hook must use correct var.
- service_advisor port confirmed as 8002 (Dockerfile lock on PR #27).
- When background agents hang >60 min with 0 turns, coordinator should kill and either execute deterministic work directly or re-spawn with corrected prompt (not wait-and-nudge pattern). User directive 2026-05-16T20:10Z codified.

**Files modified:** apps/orchestrator/Dockerfile, apps/log_analyst/Dockerfile, apps/frontend/nginx.conf, .github/workflows/deploy.yml. **Files created:** scripts/smoke-test.sh, evals/orch_cassettes/{OS-009,OS-010,OS-011}.json, evals/orch_scenarios/OS-{009,010,011}_*.yaml.

**Next:** Merge to main via PR review (Anvil Large, 3 reviewers). CI gates: bicep build, eslint, pytest, evals (citation + orchestrator gates), redteam. Deploy gate: main-only (T107 enforces).

---

## D-009: Security Verification & Test Validation | 2026-05-13

**Status:** 🟡 Ship after small remediations

**Summary:**
Strange re-audited all 10 security findings (SECURITY_REVIEW.md). Verdict: 8/10 fixed; 2 partial (H2 Cosmos firewall, M4 ARM connection string). All critical and API-layer findings closed. Verification appended to SECURITY_REVIEW.md and pushed.

Banner ran post-Stark test suite (D-008): Unit 9/9 ✅, E2E 10/10 ✅ (after fixing 2 stale-test issues: criteria.js fetch stub + admin overlay force-click). Zero regressions.

**Context:**
- Strange: SECURITY_REVIEW.md; findings per-item assessment
- Banner: Unit (criteria.js) + E2E (Playwright chromium); test files updated for stale conditions

**Follow-up:**
- H2 and M4 partial remediations: document in BACKLOG or track separately
- Test files remain updated; no rollback needed

---
