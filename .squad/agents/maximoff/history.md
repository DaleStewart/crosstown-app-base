# Wanda Maximoff — Agent History

**Date**: 2026-05-13  
**Role**: Anomaly Detection & Agent QA  
**Requested by**: Sean (segayle)

## Mission: Root Model-Version Regression Sweep

**Project**: MTA AI Hackathon — Multi-tenant Transit Authority Accelerator  
**Architecture**: Root Container Apps stack (`apps/orchestrator`, `apps/log_analyst`) + separate `apps/judging/` judging app  
**Context**: Legacy `gpt-4o` references across infrastructure and configuration needed regression fix to `gpt-4.1`.

### Scope

- **Root project only**: C:\Users\segayle\repos\mta-ai-hackathon (excluded `apps/judging/` per constraints)
- **Mechanical substitution**: 13 hits across 9 files
- **Critical constraint**: Leave `gpt-4o-realtime-preview` untouched (real model name for Foundry audio path)

### Changes Executed

1. **`.env.example` line 14**: Chat deployment default → `gpt-4.1`
2. **`apps/log_analyst/README.md` line 51**: Docstring → `gpt-4.1`
3. **`apps/log_analyst/settings.py` line 28**: Config default → `gpt-4.1`
4. **`apps/orchestrator/settings.py` line 14**: Config default → `gpt-4.1`
5. **`docs/evals.md` line 34**: Command example → `gpt-4.1`
6. **`docs/voice.md` lines 40, 51**: Speech Services path + env var docs → `gpt-4.1`
7. **`evals/foundry_evaluators.py` lines 13, 46**: Docstring + default value → `gpt-4.1`
8. **`evals/README.md` line 28**: Command example → `gpt-4.1`
9. **`infra/modules/foundry.bicep` lines 68, 71, 76**: Comment, deployment name, model name → `gpt-4.1`

### Verification

- ✅ Zero remaining `gpt-4o` references (excluding realtime)
- ✅ All 13 `gpt-4.1` references created
- ✅ `gpt-4o-realtime-preview` preserved in all files

## Technical Notes

- **Deployment name flip** (Bicep line 71): Resource name is now `gpt-4.1`, must align with env config
- **Realtime preserved**: Voice orchestrator still routes to `gpt-4o-realtime-preview` for audio; chat completions use `gpt-4.1`
- **No app logic changed**: This was a pure configuration sweep; no code paths altered
- **Judging app isolated**: `apps/judging/` directory remains independent per task constraints

## Status

✅ Complete — all edits applied, verified, documented.

---

## 2026-05-15 — Realtime Model Upgrade (D-009 Supersedes Earlier Instruction)

The "leave gpt-4o-realtime-preview alone" instruction from D-006 has been **deliberately superseded** by a full model upgrade to `gpt-realtime-1.5` (GA endpoint). This is not a reversion of D-006 — D-006 remains accurate as an audit trail. The historical context was specific to the 2026-05-13 chat-model migration. As of 2026-05-15, D-009 and D-010 execute the deliberate next step: upgrade to the GA realtime model.

**Related:** Decision D-009 (adopted 2026-05-15), Decision D-010 (adopted 2026-05-15).

---

## Learnings

**2026-05-15** — Post-merge eval gates run. Confirmed no regression from realtime model swap (D-009).

- **Citation gate** (`python -m runner --max-uncited-pct 5`): 8 turns, **0 uncited (0.0%)**, threshold 5%, **PASS**, exit code 0
  - All 8 scenarios passed; no missing citations or tool response gaps
  - Noise budget floor: 0 turns (5% of 8 = 0.4, floored to 0)

- **Orchestrator gate** (`python -m orchestrator_runner --max-fail-pct 0`): 8 scenarios, **0 failed (0.0%)**, threshold 0%, **PASS**, exit code 0
  - **Tool-routing assertions: ALL PASS** (critical for Spec 001)
  - Tested vague status → search_logs (OS-005), log ID hint → detect_pattern (OS-006), incident ID → summarize_incident (OS-007), composite ask (OS-008)
  - Realtime endpoint swap did not affect tool dispatch path or citation contract; routing identical to pre-swap baseline

- **Verdict:** 🟢 **GREEN** — No regression. Both PRs merged successfully. Citation contract intact. Orchestrator routing unaffected by gpt-realtime-1.5 swap.


---

## 2026-05-15 (re-run) — Eval Gates Re-Verification (Post D-009 + D-011 Merge)

**Requested by:** Brady (segayle). Second pass on same day to confirm no drift after PRs #1 (D-009 realtime-1.5 swap) and #2 (D-011 spec-kit + constitution + Spec 001) merged into `main`. D-014 baseline (earlier same day) was all GREEN.

### Citation gate — `python -m runner --max-uncited-pct 5`
- Scenarios run: **8** (SC-001..SC-008)
- Turns: 8 - Uncited: **0 (0.0%)** - Threshold: 5.0%
- Noise budget: floor(0.05 * 8) = 0 turns
- Result: **PASS** (exit 0)

### Orchestrator gate — `python -m orchestrator_runner --max-fail-pct 0`
- Scenarios run: **8** (OS-001..OS-008)
- Failed: **0 (0.0%)** - Threshold: 0.0%
- Result: **PASS** (exit 0)

### Tool-routing assertions (subset of orchestrator gate)
- OS-005 vague status -> `search_logs`: **PASS**
- OS-006 log ID hint -> `detect_pattern`: **PASS**
- OS-007 incident ID -> `summarize_incident`: **PASS**
- OS-008 composite ask -> multi-tool route: **PASS**

### Overall: 🟢 GREEN
Identical to D-014 baseline. Realtime model swap (D-009) and spec-kit adoption (D-011) confirmed regression-free on `main`. No status change since last run -> no inbox decision draft required.

**Team update (18:11Z):** Re-verify pass complete; PR #3 shipped from Parker for vite.config.ts.

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up
