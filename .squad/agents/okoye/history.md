# Okoye — Agent History (Active)

Okoye — Operations / DevOps. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/okoye-history-2026-05-12-to-2026-05-15.md for archival. This file tracks current work.

---

## 2026-05-17 — PR #20 `fix/voice-vad-commit` shipped (Wave 1)

**Task:** Drive PR #20 through rebase → verify → Anvil review → squash-merge → CD + regression smoke.

**Status:** ✅ Complete. Merge commit: `f9e6576`.

**Pipeline:**
- **Rebase:** One trivial conflict in `foundry_realtime.py` — PR #22's transcription block vs PR #20's `session_error` raise. Kept both (semantically independent). All 4 commits rebased clean.
- **Local verify:** ruff ✅ mypy (20 files) ✅ pytest (25/25) ✅
- **Anvil:** APPROVE with NITS — 5 nits, no blockers. Key: `commit_audio()` and `session_error` paths untested; orphaned task on error raise is pre-existing; docstring references dead server_vad scenario.
- **CD:** https://github.com/DevPost-Test-Hackathon/crosstown-app/actions/runs/25994066482 → ✅ success
- **Text regression:** `POST /api/turn {"text":"any delays on the L train?"}` → HTTP 200, 10 citations, warnings: [] ✅
- **Playwright:** `playwright-live.yml` does not exist in repo. Sean dry-runs voice himself.

**Learning:** When rebasing a branch that adds error-propagation code against a branch that adds a conditional config block at the same location, both are usually independently correct — keep both, error check first. Duck-typing via `getattr` is acceptable when the base protocol change would require stub implementations in all providers; document the reason in a comment.

---

## 2026-05-16 — T102, T103 Phase 1 Batch Intake

**Tasks:** T102 (Medium) — scripts/smoke-test.ps1; T103 (Medium) — azure.yaml postdeploy hook. Phase 1 deploy-hygiene batch.

**Status:** ✅ Complete. Branch: chore/deploy-hygiene.

**Deliverables:**
- **scripts/smoke-test.ps1:** PowerShell smoke-test script validating deployment health (three checks: GET / for Crosstown marker, GET /api/health for orchestrator routing, GET /ws/voice for WebSocket live). Early exit on first check failure. Supports live URL or xample.invalid for negative test.
- **azure.yaml postdeploy hook:** Scaffolding ready for postdeploy orchestration (e.g., index loader, seed data). Placeholder structure in place.

**Batch outcome:** Anvil PR #29 review — **PASS ✅**. Smoke test validates nginx rewrite guards correctly; live verification on Tuesday demo.

**Decisions:** D-030 (merged into D-028).

---

## 2026-05-17 — PR #23 Drive-to-Merge (Phase 3 Wave 1)

**Task:** Drive PR #23 (`feat(frontend): text input for typing questions`) through rebase → local verify → Anvil review → squash-merge → CD watch → live smoke.

**Status:** ✅ Complete. Merged at `8eb6e5b`.

**Key findings:**
- Prior CI failure: `vite.config.ts` on branch missing `include`/`exclude` patterns for e2e tests (Playwright specs picked up by vitest). Resolved cleanly by rebase on main (67b4a34) — 0 conflicts.
- Anvil verdict: **APPROVE-WITH-NITS** (3 low-severity nits: `tool_calls` not forwarded to side panel, no AbortController, no component-level TextInput tests). No blockers.
- CD: ✅ green in 2m44s (run 25993677016).
- Live smoke: `POST /api/turn {"text":"is the L train running?"}` → HTTP 200, 10 citations, 11.6s latency.

**Learning:** When a branch is behind main and picks up a vite.config.ts change that adds e2e exclusions, do NOT immediately diagnose the CI failure as a bug in the PR code — it may be a rebase lag. Always run `git diff --stat HEAD origin/main` before diagnosing CI failures on stale branches. Rebase first, diagnose second.
## 2026-05-17 — PR #27 `ci/frontend` rescue (Anvil's branch)

**Context:** Sean lifted the do-not-touch on `anvil/feat-service-advisor` (Anvil not active). PR #27 had 5/6 checks green; `ci/frontend` red.

**Root cause:** `apps/frontend/e2e/mic-button.spec.ts` is a Playwright spec (`test.describe` from `@playwright/test`). Vitest collected it during `npm test -- --run` and threw `Playwright Test did not expect test.describe() to be called here.` Anvil's `vite.config.ts` had no Vitest `exclude` — Vitest's defaults don't cover `e2e/`.

**Fix (commit f80a314 on `anvil/feat-service-advisor`):**
- `apps/frontend/vite.config.ts`: added `include: [""tests/**/*.test.{ts,tsx}""]` and explicit `exclude` block with `**/e2e/**` (mirrors Vitest defaults + e2e). Same pattern is already in place on `squad/feat-frontend-text-input` — convention now codified.
- `apps/frontend/e2e/README.md`: new doc — "e2e/ is Playwright territory, run via `npx playwright test`". Cheap deterrent for the next person.

**Verified:** `npm test -- --run` → 3 files / 6 tests passed, e2e file no longer collected. Pushed direct to `anvil/feat-service-advisor` (no new PR, no force-push). PR comment posted tagging Anvil.

**Test-runner separation pattern:**
- Vitest owns `tests/**` (jsdom, unit/component). Config: `vite.config.ts` `test` block.
- Playwright owns `e2e/**` (real browser). Config: `playwright.config.ts`, runner: `npx playwright test`.
- The two collide if Vitest's `exclude` doesn't mention `e2e/**` — Vitest's built-in defaults (`cypress`, `node_modules`, etc.) do NOT include `e2e`. Every Vitest config in this repo must add it explicitly.

**Recurrence risk:** HIGH. Anyone adding a new Playwright spec under `apps/frontend/e2e/` or scaffolding a fresh `vite.config.ts` without the `exclude` block re-breaks `ci/frontend`. Decision drop filed: `.squad/decisions/inbox/okoye-vitest-e2e-exclude-2026-05-17.md`.

**Secondary issue — merge conflict NOT resolved:** PR #27 still `CONFLICTING` with main. Attempted merge: `.gitattributes` `merge=union` cleanly handled `.squad/` files, but **3 eval cassettes** had add/add conflicts: `evals/orch_cassettes/OS-009.json`, `OS-010.json`, `OS-011.json`. These are test fixtures (code, not append-only) — aborted per Sean's rule and flagged in PR comment for Anvil to resolve.

**CI re-run status:** No new dispatch observed on f80a314 within ~3 min of push (likely GH queue lag or DIRTY merge state gating dispatch). Local verification was clean.
