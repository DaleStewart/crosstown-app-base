# Decision Note — Anvil PR #28 Round 3 Review

**Agent:** Anvil (adversarial code review)  
**Date:** 2026-05-17T10:18:00-04:00  
**PR:** #28 (`anvil/47doors-comparison`)  
**Branch:** `anvil/47doors-comparison`  
**Commit reviewed:** `1a78877` (Banner)

## Verdict: APPROVE WITH NITS ✅

---

## Thing 1 — R2 Reject Items

All 4 required items fixed. 2 bonus items also fixed.

| Item | Location | Fixed? |
|---|---|---|
| nginx paragraph: "no equivalent" | Line 83 | ✅ |
| Root-cause paragraph: "We have no equivalent" | Line 161 | ✅ |
| Prevention table smoke-test row | Line 167 | ✅ |
| Prevention table postdeploy row | Line 168 | ✅ |
| Action items 3+4 as open TODOs | Lines 351+353 | ✅ |
| §10 closing stale ref | Line 366 | ✅ |

**grep verification:** `git grep -n -i "smoke-test\|postdeploy\|smoke test" docs/47doors-comparison.md` → 13 hits, all consistent and positive. Zero contradictions.

---

## Thing 2 — Purpose Reframe

| Requirement | Result |
|---|---|
| Explicit 'Purpose' intro | ✅ Line 3 blockquote: "This is a learning reference, not a parity target." |
| Prescriptive language softened | ✅ No "should match" language anywhere |
| §8 reframed away from "what to adopt" | ✅ Heading: "Patterns From 47doors — What We've Borrowed and What Remains Optional"; note: "optional improvements…not parity requirements" |
| §10 reframed to demo-prep checklist | ✅ "Demo prep checklist (by risk, not alphabetical)"; items 3+4 ✅ DONE; items 1+2 Crosstown-specific gaps |

Doc reads as a diagnostic reference / learning document throughout. Purpose reframe is materially present and executed correctly.

---

## Nit (Non-Blocking, Pre-Existing)

**Line 169 — Dockerfile HEALTHCHECK table row:** Shows `❌ No` for our app, but PR #29 (merged 2026-05-17T00:23:23Z) added HEALTHCHECK to all three Dockerfiles before Banner's commit `1a78877` was authored. This was not in the R2 reject list; Banner inherited it and missed it. The row should read `✅ Yes`.

Not blocking. Should be corrected before squash-merge or in a follow-up.

---

## No New Factual Errors

The Dockerfile HEALTHCHECK row (line 169) is a pre-existing oversight, not introduced by Banner's R3 changes. No other factual regressions found in Banner's commit.

---

## Process Notes

- GitHub CLI raised "Cannot approve your own pull request" — the CLI account is the PR author. Review was posted as a comment (comment #4470961555 on PR #28).
- Sean must manually click Approve in the GitHub UI (or a human reviewer account must do it) before squash-merge.
- Scribe is locked out of this PR. Banner is locked out after this round. No further agent reviews needed — verdict is APPROVE.

## Next Action

Sean can squash-merge PR #28 after clicking Approve in the GitHub UI. One optional cleanup: fix line 169 Dockerfile HEALTHCHECK cell to `✅ Yes` either before merge or in a follow-up commit.
