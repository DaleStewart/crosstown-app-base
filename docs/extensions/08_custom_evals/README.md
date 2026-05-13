# Extension 08 — Custom Evaluation Scenarios

**Time:** ~30 min · **Use cases:** All use cases · **Difficulty:** Easy

## What

The skeleton ships a small eval harness under `evals/` with a handful of scenarios in
`evals/scenarios/`. This extension has your team **add at least three new evaluation scenarios**
in YAML format under `evals/scenarios/<your_domain>_*.yaml` and verify that the eval gate
passes on all of them. This proves that your agent changes (from any of the other extensions)
haven't regressed the AI's ability to answer domain questions correctly.

## Why

Every extension in this hackathon changes agent behaviour — new tools, new routing rules, a new
grounding corpus. Without automated evals you can only verify correctness by hand. This extension
introduces the habit of writing evals alongside feature work, which is a core practice for
production AI systems serving all of the use cases in the track.

## Try this

1. **Pick a domain for your three scenarios.**
   Good choices: SCADA health (use case #2), incident tracking (use case #5), cross-line
   correlation (use case #1+#2). Use only fictional lines L1, L2, L3.
2. **Create three YAML files.**
   Save each file as `evals/scenarios/<domain>_<slug>.yaml`. For example:
   `evals/scenarios/scada_l2_timeout.yaml`.
3. **Each YAML file must have the following fields:**
   ```yaml
   prompt: "What happened to the L2 SCADA bridge at 03:00 on 2025-11-01?"
   expected_tools:
     - search_logs
   must_cite: true
   ```
   Optional additional fields: `expected_agent`, `min_citations` (int), `tags` (list).
4. **Run the eval gate:**
   ```bash
   pytest evals/test_eval_gate.py -v
   ```
   Fix any failing scenarios by adjusting either the YAML expectations or your agent behaviour.

## Prompt Copilot like this

```
1. "Generate a YAML eval scenario file for the following question: 'What were the top three
   fault events on line L1 in November 2025?' The expected_tools list should include
   search_logs and detect_pattern. must_cite should be true. Save it as
   evals/scenarios/log_l1_top_faults.yaml."

2. "Open evals/test_eval_gate.py and explain the schema it expects for scenario YAML files.
   List all required fields and any optional fields."

3. "I have added three new eval scenarios. Run pytest evals/test_eval_gate.py and tell me
   which ones are failing and why. Then suggest fixes to the YAML — do not change the test
   gate itself."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/08_custom_evals/tests/ -v
```

Then also run the eval gate itself:

```bash
pytest evals/test_eval_gate.py -v
```

All tests **fail** until at least three valid scenario files exist.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [07 — Frontend Rebrand](../07_frontend_rebrand/README.md) · Next: [09 — Postgres Target](../09_postgres_target/README.md)
