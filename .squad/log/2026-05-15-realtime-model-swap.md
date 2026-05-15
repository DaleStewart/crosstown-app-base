# 2026-05-15 — Foundry Realtime Model Upgrade
**Session Lead:** Okoye (Operations)  
**Scribe:** Shuri  
**Dates:** 2026-05-13 to 2026-05-15

---

## Session Summary

Upgrade Foundry Realtime voice provider from `gpt-4o-realtime-preview` (2024-10-01 preview) to `gpt-realtime-1.5` (2026-02-23 GA). Swapped endpoint from preview `/openai/v1/realtime?api-version=2024-10-01-preview` to GA `/openai/v1/realtime?model={deployment}` (no api-version param).

**Session milestone:** D-009 (model upgrade decision) adopted.

---

## What Happened

1. **Verification (Batch 1):** Okoye verified all integration points across 7 files. Gates: Bicep build, ruff, mypy --strict (19 files), pytest (11/11), frame schemas, grep clean. All pass → GO.

2. **Commit + PR (Batch 2):** Okoye staged 7 files, created branch `squad/swap-realtime-to-gpt-realtime-1.5`, committed, pushed, opened PR.

3. **Scribe log (this session):** Updated `.squad/decisions.md` (D-009, D-010), orchestration log, cross-agent history, identity/now.md.

---

## Files Modified

### Realtime Upgrade (Okoye, Batch 2)
- `infra/modules/foundry.bicep` — deployment resource, model
- `infra/main.bicep` — stack output reference
- `.env.example` — AZURE_OPENAI_REALTIME_DEPLOYMENT
- `apps/orchestrator/settings.py` — realtime config
- `apps/orchestrator/voice/foundry_realtime.py` — WebSocket endpoint
- `docs/architecture.md` — deployment diagram
- `docs/voice.md` — realtime + Speech Services docs

### Squad Records (Shuri, this session)
- `.squad/decisions.md` — D-009 (model upgrade), D-010 (Maximoff instruction superseded)
- `.squad/orchestration-log/2026-05-15T134814Z-okoye.md` — verification + PR batches
- `.squad/agents/maximoff/history.md` — cross-agent update (D-009 link)
- `.squad/agents/stark/history.md` — cross-agent update (GA realtime endpoint in Bicep)
- `.squad/identity/now.md` — focus area refresh
- `.squad/log/2026-05-15-realtime-model-swap.md` — this file

---

## PR Status

Branch: `squad/swap-realtime-to-gpt-realtime-1.5`  
Expected: Awaiting CI + partner review.

**Next steps for partner:**
1. `azd up` against test subscription to confirm regional availability of `gpt-realtime-1.5-2026-02-23` deployment
2. Live WS frame shapes may differ; `evals/` cassettes may need refresh if live mode differs from offline
3. Optional: Test orchestrator realtime end-to-end with new model

---

## Decisions Logged

- **D-009:** Foundry Realtime Model Upgrade (adopted)
- **D-010:** Maximoff "leave realtime alone" instruction superseded (adopted)

## Verification

✅ All gates passed before PR opened  
✅ Frame schemas valid for GA endpoint  
✅ No breaking changes to auth/settings  
✅ Speech Services fallback unchanged
