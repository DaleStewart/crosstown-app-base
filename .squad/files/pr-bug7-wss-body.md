# Bug #7 — `wss://` scheme for Foundry Realtime WebSocket (P0)

D-009 (Realtime model swap to `gpt-realtime-1.5`) updated the endpoint
path correctly (`/openai/v1/realtime?model={deployment}`, no api-version
query param) but missed converting the URL scheme. The Foundry endpoint
env var resolves to `https://swedencentral.api.azureml.ms/...`, but
`websockets.connect` requires `wss://` and raises:

```
InvalidURI: 'https://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5'
isn't a valid URI: scheme isn't ws or wss
```

All three live tool paths (`search_logs`, `detect_pattern`,
`summarize_incident`) currently return HTTP 500 at this same upstream
point in `voice/foundry_realtime.py:160` before tool dispatch is reached.

## Fix

Surgical change in `apps/orchestrator/voice/foundry_realtime.py:155-163`:
build the URL with `wss://` (or `ws://` for local dev) by translating
the scheme of `self._endpoint` once, then pass it to
`websockets.connect`. Bearer auth header preserved; no `api-version`
query param re-added; `?model=gpt-realtime-1.5` deployment alias
preserved.

## Validation

- `ruff check .` — clean
- `mypy --strict .` — 19 files clean
- `pytest -q` — 11/11 pass

## Stack

Stacks on PR #12 (`squad/fix-orchestrator-aiohttp-dockerfile`,
Bug #5b — Dockerfile aiohttp). Discovered during the Tuesday
2026-05-19 customer-handoff dry-run after Bugs #1–#6 had merged.
