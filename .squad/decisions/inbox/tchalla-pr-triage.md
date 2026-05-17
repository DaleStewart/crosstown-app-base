# PR Triage Decision — 2026-05-17

**Author:** 🏗️ T'Challa (Lead)
**Status:** Awaiting Sean authorization to merge/close

## Counts
- 🟢 Merge-ready: **3** (#26, #31, #32 — #32 after #31)
- 🟡 Needs review: **2** (#21 rebase-then-merge, #27 hold for CI + review)
- 🔵 Draft: **1** (#30)
- 🔴 Stale/superseded: **2** (#19, #25 — both close, superseded by #26)

## Merge order (top → bottom)
1. **#26** — P0 UAT (spacebar/audio/health). Merge first. All CI green. Demo Tue 5/19.
2. **Close #25** — superseded by #26.
3. **Close #19** — superseded by #26 (stop-frame put in correct call site).
4. **#21** — rebase onto post-#26 main (fixes the playwright-dup CI bug) → merge. P0 conversation parity (D-032).
5. **#31** — docs polish, all green.
6. **#32** — rebase after #31 (shared `.squad/decisions.md` conflict) → merge.
7. **#27** — HOLD. Wait for Anvil's CI fix, then full review by Stark (orchestrator wiring) + Banner (eval/red-team). Largest risk surface — do not co-merge with UAT fixes.
8. **#30** — SKIP (draft).

## Top priority
**#26** — only thing standing between UAT and Tuesday's demo.

## Cleanup actions queued (await authorization)
- Close #19, #25 with link to #26.
- After #26 lands: ping Parker to rebase #21, ping Ralph to rebase #32.
- After #27 CI green: assign Stark + Banner reviewers.

Full per-PR detail in `.squad/log/2026-05-17-pr-triage.md`.
