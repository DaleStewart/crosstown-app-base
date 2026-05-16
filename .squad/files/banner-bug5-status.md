# Banner — Bug #5 status (orchestrator aiohttp dep)

**Date:** 2026-05-15
**Author:** Banner (Tester / Quality)
**PR:** [#10 — fix(orchestrator): aiohttp dep for async DefaultAzureCredential](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/10)
**Branch:** `squad/fix-orchestrator-aiohttp-dep` → base `squad/fix-foundry-hub-name-length`
**Stack:** #5 (merged) → #7 → #8 → #9 (Okoye, in flight) → **#10 (this)**

## Bug confirmation

Found in source:
- `apps/orchestrator/storage/cosmos.py:69` → `from azure.identity.aio import DefaultAzureCredential`
- `apps/orchestrator/voice/foundry_realtime.py:9` → `from azure.identity.aio import DefaultAzureCredential`

Found in `apps/orchestrator/pyproject.toml`:
- PEP 621 style `[project] dependencies`
- Line 13 had `"azure-identity>=1.15"` (no aiohttp transport)
- No `aiohttp` anywhere in deps or extras

→ Production container resolved without `aiohttp`, causing `ImportError` deep in `azure.identity.aio._credentials.app_service` whenever `/api/turn` tried to authenticate. **Bug confirmed real.**

## Fix applied

Form: **direct top-level dep** (alternative form), not `[aio]` extras.

Reason: tried `azure-identity[aio]>=1.15` first; pip warned `azure-identity 1.17.1 does not provide the extra 'aio'` — that extras group is not published. Direct `aiohttp>=3.9` is the supported form per Azure SDK docs.

Diff (apps/orchestrator/pyproject.toml):
```diff
     "azure-identity>=1.15",
+    "aiohttp>=3.9",
     "azure-cosmos>=4.6",
```

No lock file in repo (no poetry.lock, no requirements.txt) — nothing else to update.

## Local validation

| Gate | Result |
|---|---|
| `pip install -e ".[dev]"` | ✓ resolved aiohttp 3.13.5 |
| Import smoke (`from azure.identity.aio import DefaultAzureCredential; import aiohttp`) | ✓ OK |
| `python -m ruff check .` | ✓ All checks passed |
| `python -m mypy --strict .` | ✓ Success — no issues, 19 source files |
| `python -m pytest -q` | ✓ 11 passed in 0.97s |

No regressions.

## Next step — needs Squad coordination

The orchestrator container in ACA still has the broken image. To unblock `/api/turn` live:

1. Land PR #9 (Okoye, search RBAC) first.
2. Land PR #10 (this).
3. Run `azd deploy orchestrator` (or full `azd up`) to push a new container image with the corrected dep.

⚠️ **Do not auto-deploy.** Coordinate with Squad — overlapping deploys with Okoye's RBAC fix would double-deploy. Wait for #9 + #10 both merged, then single `azd deploy`.

## Autopilot disclosure

PR opened without per-step live approval (non-destructive code change, single-line dep addition, reviewable, gated by CI).
