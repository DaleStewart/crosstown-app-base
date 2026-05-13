# Acceptance — Extension 08

You're done when **ALL** of the following are true.

- [ ] At least 3 new `.yaml` files exist under `evals/scenarios/` whose filenames were **not** in the skeleton (i.e., created by your team).
- [ ] Each new YAML file contains at minimum: `prompt` (string), `expected_tools` (list), `must_cite` (boolean).
- [ ] None of the three YAML files reference real MTA systems or real place names — only fictional lines L1, L2, L3.
- [ ] `pytest evals/test_eval_gate.py -v` passes with no failures (including your new scenarios).
- [ ] All tests in `tests/` (this folder) pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Run:
   ```bash
   ls evals/scenarios/
   ```
   Point out your three new files.
2. Run:
   ```bash
   pytest evals/test_eval_gate.py -v
   ```
   Show all green, including the new scenarios.
3. Open one of your YAML files and walk the coach through the `prompt`, `expected_tools`,
   and `must_cite` fields, explaining what each one tests.
