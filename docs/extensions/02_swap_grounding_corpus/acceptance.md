# Acceptance — Extension 02

You're done when **ALL** of the following are true.

- [ ] `data/mock_logs/README.md` exists and contains at least one paragraph describing your team's synthetic domain.
- [ ] `data/mock_logs/` contains at least 5 new `.jsonl` files authored by your team (files added by the skeleton don't count toward the 5).
- [ ] Each `.jsonl` file has at least 5 lines; each line is valid JSON with keys `timestamp`, `line`, `system`, `message`, `severity`.
- [ ] `scripts/load_search_index.py` has a bumped `# corpus-version:` comment (value > 1).
- [ ] `python scripts/load_search_index.py --dry-run` exits with code 0 and prints a document count ≥ 25.
- [ ] `pytest evals/ -v` passes (no regressions from the eval suite).
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Open `data/mock_logs/` in the terminal and run `ls -lh` (or `dir`) to show the new files.
2. Run:
   ```bash
   python scripts/load_search_index.py --dry-run
   ```
   Show the printed document count.
3. Run:
   ```bash
   pytest evals/ docs/extensions/02_swap_grounding_corpus/tests/ -v
   ```
   Show all tests green.
4. Ask the coach: _"What happened on the L3 line last month?"_ and show a log entry from your
   new corpus appearing in the citations.


## 📚 Acceptance criteria

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
