# D-033 — PR #22 Shipped: user-turn transcripts (orchestrator backend)

**Agent:** Okoye (DevOps)  
**Date:** 2026-05-17T11:10:00-04:00  
**PR:** #22 — `fix(orchestrator): emit user-turn transcripts to client (P0 — conversation parity)`  
**Branch:** `squad/fix-voice-user-transcription` (deleted after merge)  
**Merge commit:** `2051e25`

---

## Rebase outcome

Rebased `squad/fix-voice-user-transcription` onto `bac5bdf` (main tip after PR #20 merged at `f9e6576`).

**2 conflicts, 3 hunks — all resolved with both sides preserved:**

### `apps/orchestrator/settings.py`
- **HEAD** default: `azure_openai_transcription_deployment: str = ""` (disabled)
- **PR #22** default: `"whisper-1"` (unsafe for Azure OpenAI — crashes WebSocket)
- **Resolution:** Kept HEAD's safe `""` default. Merged both comment blocks to document that OpenAI accepts "whisper-1" but Azure requires a real deployment name.

### `apps/orchestrator/voice/foundry_realtime.py` (2 hunks)
1. **`commit_audio` docstring:** Kept both sentences from HEAD and PR #22 — they're complementary ("belt-and-suspenders" + "without it the model never processes speech").
2. **Phase 2 comment + JSON format:** Kept HEAD's DANGER comment (Azure closes WebSocket on invalid deployment name — NOT a soft error) and HEAD's GA nested `audio.input.transcription.model` format (validated via 47doors-ref). PR #22's flat `input_audio_transcription` format and "non-fatal/fire-and-forget" framing were overridden.

**Key finding from Anvil:** After conflict resolution, the functional diff vs main is only 2 comment lines. Every substantive change (`_translate` user-transcript handlers, `TranscriptDelta(role="user")`, `_handle_event` routing, all 13+ tests) was already on main from prior work.

---

## Local verify

All green on `apps/orchestrator/`:
- `ruff check .` ✅
- `mypy --strict .` → 20 files, no issues ✅  
- `pytest -q` → 25/25 passed ✅

---

## Anvil verdict

**APPROVE-WITH-NITS** (3 nits, none blocking)

| # | Nit |
|---|-----|
| 1 | `.squad/files/pr-voice-user-transcription-body.md` said default `"whisper-1"` — fixed before merge |
| 2 | `foundry_realtime.py`: `completed` handler missing empty-string guard (unlike `delta` handler) — pre-existing, not introduced by this PR |
| 3 | PR body claimed 14 new tests; file has 13 — documentation inaccuracy only |

Nit #1 fixed in `docs(squad)` commit `57d6525` before merge.

---

## CI (all green before merge)

| Check | Result |
|-------|--------|
| ci/bicep | ✅ |
| ci/frontend | ✅ |
| ci/python (log_analyst) | ✅ |
| ci/python (orchestrator) | ✅ |
| eval/citation-gate | ✅ |
| eval/orchestrator-gate | ✅ |
| eval/foundry-evaluators | skipped (no AZURE_OPENAI_ENDPOINT var) |

---

## CD

**Run:** https://github.com/DevPost-Test-Hackathon/crosstown-app/actions/runs/25994434251  
**Status:** ✅ success (2m40s)  
**Steps:** Provision Infrastructure ✅ → Deploy Application ✅

---

## Text-path regression

```
POST /api/turn {"text":"any delays on the L train?"} → HTTP 200, 10 citations, warnings: []
```
✅ Text path **not** regressed. Same behavior as PR #20 baseline.

Note: First regression curl with `{"text":"L train delays?"}` got `citations:[], uncited` due to model sending an invalid `time_range` param. This is pre-existing model behavior (non-deterministic param choices), not an orchestrator regression. Confirmed with exact #20 baseline text.

---

## Status

**Wave 2 (orchestrator backend) complete. Ready for frontend pair:**
- **#21** — `feat(frontend): render user transcripts in chat` (Parker's PR — renders `transcript_delta` with `role: "user"`)
- **#19** — stop-frame PR (Maximoff's scope)

Both PRs depend on the `transcript_delta` message contract now live on main (`{type, role, text, final}`). Field names are stable and locked.
