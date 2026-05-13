# Evals — Log Analyst golden scenarios

This is the **deploy gate**. The eval workflow (`.github/workflows/eval.yml`) runs the eight YAML scenarios under `scenarios/` and fails the build when more than 5% of turns produce uncited claims.

## Run locally

```bash
cd evals
pip install -r requirements.txt
python -m runner --max-uncited-pct 5
```

By default the runner uses **offline mode**: each scenario ships with a cassette (`cassettes/<id>.json`) of recorded tool responses, so the suite is hermetic.

Switch to live mode to hit a deployed env:

```bash
EVAL_MODE=live \
  LOG_ANALYST_URL=https://log-analyst.<env>.azurecontainerapps.io \
  python -m runner --max-uncited-pct 5
```

## Scenario shape (`scenarios/*.yaml`)

```yaml
id: SC-001
title: "L2 doors-held cluster around Beacon"
prompt: "Show me door-held events on L2 near Beacon in the last hour."
expected_tools:
  - name: search_logs
    args_contains: {query: "doors held", time_range: any}
must_cite:
  - type: log    # at least one
  - type: runbook
max_turns: 3
```

## Adding new scenarios

Drop `.yaml` files into `scenarios/`. Each new scenario also needs a cassette in `cassettes/` (record once with `--record` against a live env).

See [Extension 08](../docs/extensions/08_custom_evals/) for the team exercise.
