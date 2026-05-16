## Summary

Live `azd up` smoke test of `POST /api/turn` returned **HTTP 500** with:

```
ImportError: aiohttp package is not installed
```

…raised inside `azure.identity.aio._credentials.app_service`. The orchestrator uses the **async** `DefaultAzureCredential` flow:

- `apps/orchestrator/storage/cosmos.py:69` → `from azure.identity.aio import DefaultAzureCredential`
- `apps/orchestrator/voice/foundry_realtime.py:9` → `from azure.identity.aio import DefaultAzureCredential`

…but `apps/orchestrator/pyproject.toml` didn't pin the aiohttp transport, so the production container resolved without it. Local dev happened to have `aiohttp` from another transitive dep, masking the bug.

## Fix

Add `aiohttp>=3.9` as a direct top-level dep in `apps/orchestrator/pyproject.toml`.

> **Note on `[aio]` extras:** Tried `azure-identity[aio]>=1.15` first (cleaner intent), but `pip` warned: `azure-identity 1.17.1 does not provide the extra 'aio'`. That extras group isn't published — adding `aiohttp` directly is the supported form per Azure SDK docs.

## Local verification

```
python -c "from azure.identity.aio import DefaultAzureCredential; import aiohttp; print('OK')"
→ OK aiohttp 3.13.5

python -m ruff check .          → All checks passed!
python -m mypy --strict .       → Success: no issues found in 19 source files
python -m pytest -q             → 11 passed in 0.97s
```

## Context

- **Bug #5** in the Tuesday 2026-05-19 customer-handoff dry-run, Phase 2 (live smoke verify).
- Discovered after Okoye's PRs #5 / #7 / #8 unblocked `azd up`. See `.squad/files/azd-up-result-2026-05-15.md`.
- **Stack order:** #5 (merged) → #7 → #8 → #9 (search RBAC, Okoye, in flight) → **this PR**.
- Independent of Okoye's RBAC fix (different file).

## Follow-up (do NOT auto-deploy)

The orchestrator container needs a fresh `azd deploy` (or full `azd up`) to pick up the new dep. **Coordinate with Squad before triggering** — Okoye's PR #9 should land first so we don't double-deploy.

## Autopilot disclosure

Branch + PR opened in autopilot without per-step approval. Change is non-destructive (single-line dep addition in `pyproject.toml`), reviewable, and gated by CI.
