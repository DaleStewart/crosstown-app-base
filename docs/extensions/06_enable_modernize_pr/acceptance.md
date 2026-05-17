# Acceptance — Extension 06

You're done when **ALL** of the following are true.

- [ ] `.github/workflows/modernize-pr.yml` exists (the `.disabled` version is gone or renamed).
- [ ] The workflow has an `on:` block that includes at least `workflow_dispatch`.
- [ ] There is no `if: false` guard at the workflow or job level.
- [ ] The workflow has at least one job defined.
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Show the file in the editor: `cat .github/workflows/modernize-pr.yml`
2. Point out the `on:` block and the absence of `if: false`.
3. Run `pytest docs/extensions/06_enable_modernize_pr/tests/ -v` and show all green.
4. _(Optional if time permits)_ Navigate to the repo's Actions tab on GitHub and trigger
   `workflow_dispatch` manually — show the workflow run appearing.


## 🤖 Acceptance criteria

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Edge cases listed | [██████████] 100% |
| Pass/fail thresholds | [██████████] 100% |
| Reviewer assigned | Banner (Tester) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Banner (Tester) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When acceptance criteria are revisited or team completes extension |
