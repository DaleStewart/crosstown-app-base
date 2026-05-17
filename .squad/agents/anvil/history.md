# Anvil — Code Review Agent

**Role:** Evidence-first code reviewer. Adversarial multi-model review with SQL-tracked verification.  
**Project:** MTA AI Hackathon  
**First session:** 2026-05-16

## 2026-05-16 — T108 Large Review (PR #29 Deploy Hygiene)

**Task:** T108 (Large) — Code review of PR #29 with 3 independent reviewers + consolidated verdict.

**Status:** ✅ Complete. **VERDICT: PASS ✅**

**PR Scope:** Deploy hygiene bundle (6 files, ~150 LOC total):
- `scripts/smoke-test.ps1` — Smoke-test validation script
- `apps/orchestrator/Dockerfile` — HEALTHCHECK directive
- `apps/log_analyst/Dockerfile` — HEALTHCHECK directive  
- `apps/frontend/Dockerfile` — HEALTHCHECK directive
- `azure.yaml` — postdeploy hook structure
- `.github/workflows/deploy.yml` — main-only guard + confirmation gate

**Review Phases:**
1. **Phase A (Stark lens — architecture):** Dockerfiles, nginx config, deploy guard syntax
2. **Phase B (Banner lens — testing):** Smoke modes, cassettes, eval gate, negative tests
3. **Phase C (Anvil lens — adversarial):** Silent failures, over-trust assumptions, regression paths

**Six High-Value Checks (all pass ✅):**
1. `/health` vs `/healthz` route consistency — Routes verified at orchestrator/log_analyst main.py. Plan was wrong; PR correctly uses `/health` everywhere. ✓
2. `FRONTEND_URL` vs `SERVICE_FRONTEND_URI` env var — `azd env get-values` returns `FRONTEND_URL`; no `SERVICE_FRONTEND_URI`. azure.yaml uses correct var. ✓
3. service_advisor HEALTHCHECK absence — Directory not in tracked tree (will be PR #27's job). Correctly out of scope. ✓
4. OS-010 cassette argument keys — Runner grades on tool name only; `from`/`to`/`avoid_disruption` keys invisible to gate. Reconciliation tracked for PR #27. ✓
5. nginx `proxy_pass` URI semantics — Rendered template verified: `/api/health` exact-match rewrite OK, `/api/` prefix forwards URI correctly. ✓
6. deploy.yml env passthrough — Script-injection-safe pattern; traced 4 cases (push main / push feature / dispatch confirm=true/false) — all correct. ✓

**Evidence Bundle:**
- Syntax: bash -n, YAML validity, JSON validity (cassettes)  
- Eval gate: 11/11 orchestrator scenarios PASS (OS-001..011)
- Negative smoke: GET https://example.invalid → exits 1 with FAIL (expected)
- Live smoke: GET https://frontend.blackriver-... → routes verified
- Rendered configs: nginx exact-match block, deploy.yml branch logic traced
- SQL ledger: 19 rows (1 baseline, 15 after-checks, 3 verdicts), all passed=1

**Non-Blocking Soft Concerns:**
1. Frontend Dockerfile HEALTHCHECK couples to orchestrator locally; ACA Bicep probes override (acceptable)
2. OS-010 cassette reconciliation post-PR#27 merge
3. Smoke check 3 (direct orchestrator) silently skips when env unset (acceptable for hackathon)

**Decision:** PASS — Cleared for merge. PR #29 safe to land as step 0 of Tuesday demo merge train.

---

## Learnings

2026-05-16 — Three-reviewer phase pattern (Architecture / Testing / Adversarial) detects different classes of issues. Architecture catches structural mismatches (routes, bindings). Testing catches coverage gaps + gate contracts. Adversarial catches over-trust + silent failures. All three lenses needed for large PRs.
