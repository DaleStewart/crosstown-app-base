# 2026-05-16T20:30:00Z — Phase 1 deploy-hygiene batch completion

**Agents shipped:** Stark, Parker, Okoye, Okoye², Banner  
**Branch:** chore/deploy-hygiene  
**Status:** Ready for Anvil Large review  

## What was shipped

Five Phase 1 tasks completed on `chore/deploy-hygiene` branch:

1. **T104 (Stark):** HEALTHCHECK directives in two Dockerfiles.
2. **T106 (Parker):** nginx `/api/health` → `/health` rewrite.
3. **T107 (Okoye²):** deploy.yml main-only guard (FR-013).
4. **T101 (Okoye):** scripts/smoke-test.sh with 5+1 checks.
5. **T007-followup (Banner):** service-advisor cassettes (OS-009/010/011), eval gate unblocked.

## Readiness for Anvil

- **Code changes:** all verified (syntax check, static analysis, mock execution where feasible).
- **Eval gate:** PASS (11/11 scenarios, 0% failure in orchestrator_runner hermetic mode).
- **Files status:** no git commits; all changes on working tree, ready for manual stage + commit by Coordinator.
- **Dependencies:** no blockers. T104/T106/T107/T101 are self-contained. T007-followup cassettes flagged for post-PR#27 reconciliation (Anvil to re-record from live handlers).

## Key learnings

- Canonical health endpoint: `/health` (not `/healthz`, per audit T001).
- azd exposes `FRONTEND_URL` (not `SERVICE_FRONTEND_URI`, per audit T004).
- Service-advisor port confirmed 8002 (per audit T003).
- Background agent hang policy: 60-min hard-stop; don't wait-and-nudge (user directive 2026-05-16T20:10Z).

## CI gates (expected to pass)

- bicep build ✅
- ruff + mypy (no Python changes on this branch)
- eslint + tsc (no frontend source changes)
- pytest (no test changes)
- citation gate (evals): affected only by banner cassettes, all cited ✅
- orchestrator gate (evals): all 11 scenarios pass ✅
- deploy guard (T107): enforces main-only, will pass on push to main ✅

## Next action

Coordinator stages modified files (not .squad/):
- apps/orchestrator/Dockerfile
- apps/log_analyst/Dockerfile
- apps/frontend/nginx.conf
- .github/workflows/deploy.yml
- scripts/smoke-test.sh (new)
- evals/orch_cassettes/OS-{009,010,011}.json (new)
- evals/orch_scenarios/OS-{009,010,011}_*.yaml (new)

Commits to main. Anvil review follows.

---  
**Scribe log:** D-030, orchestration-log/* (5 agents), this session log.
