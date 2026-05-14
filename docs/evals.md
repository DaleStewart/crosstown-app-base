# Evals — quality gates for the MTA AI Hackathon accelerator

Three gates ship in `.github/workflows/eval.yml`:

| Gate | Runner | Threshold | What it grades |
|---|---|---|---|
| **Citation** | `python -m runner` | `≤5%` uncited turns | Tool-layer responses from the Log Analyst carry citations of the right type and pinned IDs where applicable. |
| **Orchestrator** | `python -m orchestrator_runner` | `0%` failures | The composed user-facing reply contains required substrings, at least one citation token, **and the orchestrator picked the expected tool(s)** (`expected_tools` field). |
| **Foundry** (optional) | `python -m runner --with-foundry` | `score ≥ 3.0` on each evaluator | Groundedness, relevance, coherence, retrieval — Foundry-hosted LLM-judge scores. |

Plus the safety gate in [`docs/redteam.md`](redteam.md).

## When each gate fires

- Citation + Orchestrator: every PR to `main` that touches `apps/**` or `evals/**`.
- Foundry: only when `AZURE_OPENAI_ENDPOINT` is configured as a repo variable (so the SDK has somewhere to call).
- Red team: weekly + on-demand.

## Run locally

```bash
cd evals
pip install -r requirements.txt

# 1. Citation gate (offline, hermetic)
python -m runner --max-uncited-pct 5

# 2. Orchestrator-level gate (offline, hermetic)
python -m orchestrator_runner --max-fail-pct 0

# 3. Foundry evaluators (requires SDK + endpoint)
pip install "azure-ai-evaluation>=1.0.0"
AZURE_OPENAI_ENDPOINT=https://... \
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1 \
  python -m runner --max-uncited-pct 5 --with-foundry
```

## Live mode

Set `EVAL_MODE=live` plus the URL env var:

```bash
EVAL_MODE=live LOG_ANALYST_URL=https://log-analyst.<env>... python -m runner
EVAL_MODE=live ORCHESTRATOR_URL=https://orchestrator.<env>... python -m orchestrator_runner
```

The orchestrator must expose `POST /api/turn` (it does — see `apps/orchestrator/main.py`).

## Scenario shapes

### Citation-gate scenario (`evals/scenarios/SC-*.yaml`)
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
must_cite_ids:                      # OPTIONAL — pins specific IDs
  - "L-001234"
  - "RB-01-doors-held"
max_turns: 2
```

`must_cite_ids` makes the gate stricter: at least one citation in the response must match each pinned ID. This catches "cited *something*, just not the *right* something."

### Orchestrator scenario (`evals/orch_scenarios/OS-*.yaml`)
```yaml
id: OS-001
title: "Doors-held on L2 — composed reply with citation"
prompt: "What's the recent door-held activity on L2?"
expected_substrings: ["door", "L2"]
expect_citations: true              # response text must contain at least one L-/INC-/RB- token
expected_tools:                     # tool-routing assertion (cassettes carry tool_calls)
  - search_logs
```

Tool-routing scenarios (OS-005..008) target the routing question specifically — a vague status question must route to `search_logs`, a raw log ID must route to `detect_pattern`, an incident ID must route to `summarize_incident`, and a composite ask must invoke both.

## Foundry evaluators

Lazy-imported in `evals/foundry_evaluators.py`. Returns a 1..5 score per evaluator with `PASS_BAR=3.0`. Missing SDK or missing endpoint is treated as "skip" (score=None), not "fail" — so the offline path keeps running.

| Evaluator | What it asks the judge |
|---|---|
| `groundedness` | Does the response stay within the cited context? |
| `relevance` | Does the response answer the user's question? |
| `coherence` | Is the response well-formed? |
| `retrieval` | Was the retrieved context useful for answering? |

## Reports

Each run writes JSON to `evals/.report/` (gitignored): `eval-report.json` and `orchestrator-eval-report.json`. The GitHub Actions jobs upload them as artifacts.

## Calibration

All thresholds in this doc are pinned in [`evals/calibration.json`](../evals/calibration.json) with the math in [`evals/calibration.md`](../evals/calibration.md). Each runner prints **observed vs threshold + noise budget** at the end of every run so trend movement is visible before the gate flips. Re-calibration goes through `.squad/decisions.md`.

## Adding scenarios

1. Drop a YAML in `scenarios/` (citation gate) or `orch_scenarios/` (orchestrator gate) with a unique `id`.
2. For offline runs, add a matching cassette in `cassettes/<id>.json` (citation) or `orch_cassettes/<id>.json` (orchestrator).
3. Run the relevant runner until your scenario behaves.
