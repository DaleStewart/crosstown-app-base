# Evals — quality gates for the Log Analyst + Orchestrator

The accelerator ships **four** CI quality gates. This folder owns three of them; red team owns the fourth.

| # | Gate | Runner | Default threshold | Where |
|---|---|---|---|---|
| 1 | **Citation** — every tool turn carries citations of the right type (+ pinned IDs where deterministic) | `python -m runner` | ≤5% uncited turns | `evals/scenarios/*` + `evals/cassettes/*` |
| 2 | **Orchestrator** — user-visible reply contains required substrings, a citation token, and the orchestrator picked the expected tools | `python -m orchestrator_runner` | 0% scenario failures | `evals/orch_scenarios/*` + `evals/orch_cassettes/*` |
| 3 | **Foundry evaluators** *(optional)* — `groundedness` / `relevance` / `coherence` / `retrieval` LLM-judge scores | `python -m runner --with-foundry` | each score ≥3.0/5 | `evals/foundry_evaluators.py` |
| 4 | **Red team** — eight adversarial families (jailbreak, prompt/indirect injection, off-domain, PII, citation skip, hallucination, token bomb) | `python -m redteam.runner` (sibling folder) | 0 high/critical, ≤10% overall | `redteam/` |

All thresholds and the recalibration protocol live in [`calibration.md`](calibration.md) / [`calibration.json`](calibration.json). Every runner prints the observed-vs-threshold delta + noise budget at the end of each run.

## Run locally

```bash
cd evals
pip install -r requirements.txt

# Gate 1 (offline, hermetic)
python -m runner --max-uncited-pct 5

# Gate 2 (offline, hermetic) - includes tool-routing assertions
python -m orchestrator_runner --max-fail-pct 0

# Gate 3 (requires Azure OpenAI endpoint + SDK)
pip install "azure-ai-evaluation>=1.0.0"
AZURE_OPENAI_ENDPOINT=https://... AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o \
  python -m runner --max-uncited-pct 5 --with-foundry
```

## Live mode

```bash
# Citation gate hits the Log Analyst directly
EVAL_MODE=live LOG_ANALYST_URL=https://log-analyst.<env>.azurecontainerapps.io \
  python -m runner

# Orchestrator gate hits the orchestrator's /api/turn
EVAL_MODE=live ORCHESTRATOR_URL=https://orchestrator.<env>.azurecontainerapps.io \
  python -m orchestrator_runner
```

The orchestrator ships `POST /api/turn` out of the box (see `apps/orchestrator/README.md`).

## Scenario shapes

### Citation gate (`scenarios/SC-*.yaml`)

```yaml
id: SC-002
title: "Pattern detection: cascading doors-then-dwell"
prompt: "Look at log L-001234 and tell me if it's part of a known pattern."
expected_tools:
  - name: detect_pattern
    args_contains: {log_id: "L-001234"}
must_cite:
  - type: log
  - type: runbook
must_cite_ids:                  # OPTIONAL — pins specific IDs
  - "L-001234"
  - "RB-01-doors-held"
max_turns: 2
```

### Orchestrator gate (`orch_scenarios/OS-*.yaml`)

```yaml
id: OS-001
title: "Doors-held on L2 — composed reply with citation"
prompt: "What's the recent door-held activity on L2?"
expected_substrings: ["door", "L2"]
expect_citations: true            # response text must contain L-/INC-/RB- token
expected_tools:                   # tool-routing assertion
  - search_logs
```

## Adding scenarios

1. Drop a YAML in `scenarios/` (citation) or `orch_scenarios/` (orchestrator) with a unique `id`.
2. For offline runs, add a matching cassette in `cassettes/<id>.json` or `orch_cassettes/<id>.json`.
3. Re-run the relevant runner until the new scenario behaves.

See [Extension 08](../docs/extensions/08_custom_evals/) for the team exercise.

## Reports

Each run writes JSON to `.report/` (gitignored): `eval-report.json` and `orchestrator-eval-report.json`. CI uploads them as workflow artifacts.

