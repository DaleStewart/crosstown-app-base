# Calibrated Thresholds

> **Source of truth:** [`evals/calibration.json`](calibration.json) — machine-readable record updated whenever a gate is re-calibrated.

The accelerator runs four CI gates. Each has a numeric threshold. Pre-2026-05-12 those numbers were hand-picked; this doc captures the calibration that pinned them.

## The math

For every gate we look at three numbers:

| Number | Meaning |
|---|---|
| **observed** | What the offline gate actually produced on the current cassette suite. |
| **threshold** | The number CI fails above. |
| **noise budget** | `threshold − observed`, expressed as "scenarios you could lose to genuine noise before CI flips red." |

For percentage gates: `noise budget (turns) = floor(threshold_pct/100 × N)`.

## Per-gate calibration

### Citation gate · `evals/runner.py`
- **N**: 8 turns (one per scenario today; pinned-IDs add no turns).
- **Observed uncited**: 0 / 8 = 0.0%.
- **Threshold**: 5.0%.
- **Noise budget today**: `floor(0.05 × 8) = 0` — i.e. *any* uncited turn fails the gate at N=8.
- **Scaling**: at 20 turns the same 5% threshold tolerates 1 noise turn (`floor(0.05 × 20) = 1`). The threshold scales **automatically** with suite size — that's the whole reason it's a percent, not a count.
- **Why not 0%?** A 0% gate becomes brittle the moment a single scenario hits a known-flaky live infra path. 5% preserves the spirit (deterministic now) while giving the suite room to grow without a re-tuning round-trip.
- **Re-calibrate when**: observed climbs above 2% in steady-state, or N grows past 50 (drop threshold to 2%).

### Orchestrator gate · `evals/orchestrator_runner.py`
- **N**: 8 scenarios (4 capability + 4 tool-routing).
- **Observed failures**: 0 / 8 = 0.0%.
- **Threshold**: 0.0%.
- **Noise budget**: 0 — any failure is a real regression. Each scenario is a deterministic substring/routing check against a cassette or a controlled live env. There is no legitimate flakiness budget at the orchestrator layer.
- **Re-calibrate when**: a non-regression flake actually appears in live mode three runs in a row. Then bump to `ceil(1/N × 100)` = 12.5% (allows exactly 1 flaky scenario), and log the reason in `.squad/decisions.md`.

### Red-team gate · `redteam/runner.py`
- **N**: 8 adversarial scenarios.
- **Observed**: 0 / 8 fail, 0 high/critical.
- **Thresholds**: 10% overall **AND** 0 high/critical.
- **Noise budget today**: `floor(0.10 × 8) = 0` — same shape as the citation gate. At N=10, one failure becomes tolerable; high/critical stays at zero forever.
- **Why two thresholds?** A jailbreak success is categorically different from an off-domain refusal failing a wording check. The overall-percent gate catches drift; the hard zero on high/critical catches the failures that actually matter.
- **Re-calibrate when**: never loosen high/critical. Overall threshold can scale with N like the citation gate.

### Foundry evaluators · `evals/foundry_evaluators.py`
- **Pass bar**: 3.0 on the 1..5 scale.
- **Evaluators**: `groundedness`, `relevance`, `coherence`, `retrieval`.
- **Why 3.0?** Foundry's docs use 3.0 as the default "acceptable" threshold for LLM-judge evaluators. Lower → noise; higher → would require human-labeled ground truth we don't have.
- **Status**: optional CI job; only runs when `AZURE_OPENAI_ENDPOINT` is configured. Observed-baseline data will be added the first time the live job runs.

### Tool-routing assertion · part of `orchestrator_runner.py`
- **N**: 4 routing-focused scenarios (OS-005..008) + 3 capability scenarios with `expected_tools` pinned (OS-001..003).
- **Observed misroute**: 0 / 7 = 0.0%.
- **Threshold**: 0.0% — same logic as the orchestrator gate. Routing is deterministic; any miss is a real regression.

## Recalibration protocol

The protocol is in [`calibration.json#recalibration_protocol`](calibration.json). One-liner: **fix the regression first, loosen the threshold last.** Any threshold change goes through `.squad/decisions.md`.

## Running calibration locally

```bash
cd evals
python -m runner --max-uncited-pct 5
python -m orchestrator_runner --max-fail-pct 0
cd ../redteam
python -m runner --max-fail-pct 10
```

Each runner prints `Observed X.X% / Gate <= Y.Y%` so you can spot trend movement before the gate flips.
