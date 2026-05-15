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

