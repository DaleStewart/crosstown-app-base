# Okoye — Agent History (Active)

Okoye — Operations / DevOps. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/okoye-history-2026-05-12-to-2026-05-15.md for archival. This file tracks current work.

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
