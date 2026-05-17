# Bruce Banner — Agent History (Active)

Bruce Banner — Tester / Data Science & Evaluation. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/banner-history-2026-05-13-to-2026-05-15.md for archival. This file tracks current work.

---

## 2026-05-17 — PR #28 Round 2 doc fix + purpose reframe

**Task:** Fix 4 Anvil-flagged stale references in `docs/47doors-comparison.md` (smoke-test/postdeploy contradictions). Scribe locked out after R2 reject; Banner took R2 authorship. Mid-task, Sean issued a reframe directive: doc is a **learning reference, not a parity audit**.

**Status:** Complete. Commit `1a78877` force-pushed; PR #28 commented; decision filed.

**Reframe changes (Sean directive):**
- Purpose block: "Strategic analysis" → explicit learning-reference framing
- §8 heading + framing note: distinguishes adopted vs optional patterns
- §6: neutral language for smoke-test.sh description
- §10: "Ordered fix sequence" → "Demo prep checklist"

**Stale-ref fixes (4 required + 2 bonus):**
1. Line 83: "we don't have an equivalent" → "we now have an equivalent"
2. Line 151 (bonus): "Ours doesn't" → accurate description of our stronger hook
3. Line 161: "We have no equivalent" → "We now have an equivalent"
4. Lines 167–168: ❌ No → ✅ Yes; row descriptions updated
5. Lines 347–349: items 3+4 marked ✅ DONE
6. Lines 362+364 (bonus): stale adoption language removed

**Key learnings:**
- Always full-doc grep after targeted fixes — found 2 more stale hits Anvil hadn't listed.
- Mid-task purpose reframes can fold into same commit via `git commit --amend`.
- `gh pr comment --body` with heavy markdown can hang — keep body short.
- Stash before `gh pr checkout` when in-progress work exists on the current branch.
- Branch-awareness is critical when using `git commit --amend` — verify `git branch --show-current` before amending.

**Decision filed:** `.squad/decisions/inbox/banner-pr28-r2-fix.md` (local only — inbox is gitignored)

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
