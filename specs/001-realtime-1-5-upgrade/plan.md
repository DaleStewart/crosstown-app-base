# Implementation Plan: Foundry Realtime Model Upgrade

**Branch**: `001-realtime-1-5-upgrade` | **Date**: 2026-05-15 | **Spec**: [specs/001-realtime-1-5-upgrade/spec.md](spec.md)

**Input**: Feature specification from `specs/001-realtime-1-5-upgrade/spec.md`

## Summary

Swap the single Foundry Realtime deployment from `gpt-4o-realtime-preview` (model version `2024-10-01`) to `gpt-realtime-1.5` (model version `gpt-realtime-1.5-2026-02-23`) — the GA successor. Update the orchestrator's WebSocket URL pattern from the preview `api-version` query-param form to the GA `/openai/v1/realtime?model={deployment}` pattern. Update defaults, env example, and documentation. Verify via the four CI gates.

## Technical Context

**Language/Version**: Python 3.11 (orchestrator), Bicep (infra), Markdown (docs)

**Primary Dependencies**: FastAPI, azure-identity, websockets (orchestrator); Azure Bicep CLI (infra)

**Storage**: N/A (no data migration)

**Testing**: `az bicep build`, `ruff check .`, `mypy --strict .`, `pytest -q`, straggler grep

**Target Platform**: Azure Container Apps (ACA) + Azure AI Foundry

**Project Type**: Configuration + documentation change across an existing multi-service repo

**Constraints**: Zero breaking changes to public surface (env-var names, ACA endpoints, citation contract)

## Constitution Check

| Principle | Status |
|---|---|
| I. Citations Are Load-Bearing | ✅ No citation code touched; eval gates re-verified |
| II. Mock Data Only | ✅ No data changes |
| III. Hermetic by Default | ✅ Tests remain hermetic; no new live dependencies |
| IV. Keyless Auth | ✅ No auth changes; UAMI + DefaultAzureCredential unchanged |
| V. One Voice Abstraction | ✅ Only the Foundry Realtime implementation updated; abstraction intact |
| VI. Extensions Are Exercises | ✅ No extension code touched |

## Files Changed

| # | File | Change |
|---|---|---|
| 1 | `infra/modules/foundry.bicep` | Deployment resource `name` → `gpt-realtime-1.5`, `model.name` → `gpt-realtime-1.5`, `model.version` → `gpt-realtime-1.5-2026-02-23`. SKU `GlobalStandard` capacity 10 retained. Comment updated. |
| 2 | `infra/main.bicep` | Description comment referencing the realtime model updated. |
| 3 | `apps/orchestrator/settings.py` | Default for `azure_openai_realtime_deployment` → `"gpt-realtime-1.5"`. |
| 4 | `apps/orchestrator/voice/foundry_realtime.py` | WebSocket URL switched from preview `api-version` query-param pattern to GA `/openai/v1/realtime?model={deployment}` pattern. (Discovered mid-flight — the GA endpoint uses a different URL structure than preview.) |
| 5 | `.env.example` | `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5` |
| 6 | `docs/voice.md` | 5 spots updated: model name in heading, "How it works" section, "Required Bicep" section, env-var default, troubleshooting table. |
| 7 | `docs/architecture.md` | 2 spots updated: Azure resources list and Mermaid voice-flow diagram. |

## Files Explicitly NOT Changed

| File/Symbol | Reason |
|---|---|
| `gpt4oRealtimeDeployment` (Bicep symbol name) | API stability — renaming would break any downstream references. |
| `AZURE_OPENAI_REALTIME_DEPLOYMENT` (env var name) | API stability — the var name is decoupled from the model it points to. |
| `.squad/**` historical notes | Rewriting audit-trail entries would falsify history. |
| Speech Services fallback (`voice/speech_services.py`) | Out of scope — only the Foundry Realtime path is affected. |
| `evals/`, `redteam/` | No scenario or cassette changes needed — the model swap is transparent to the eval surface. |

## Naming Decision

- **Bicep deployment `name`** = `gpt-realtime-1.5` (short alias, no date suffix — keeps env files clean).
- **`model.version`** in Bicep = `gpt-realtime-1.5-2026-02-23` (the actual versioned identifier).
- Matches existing pattern: deployment `name: 'gpt-4.1'` with `model.version: '2024-11-20'`.

## Verification Gates

| # | Gate | Command | Pass Criteria |
|---|---|---|---|
| 1 | Bicep build | `az bicep build --file infra/main.bicep --stdout > /dev/null` | Exit 0 |
| 2 | Linting | `ruff check .` (from `apps/orchestrator/`) | Exit 0 |
| 3 | Type checking | `mypy --strict .` (from `apps/orchestrator/`) | Exit 0 |
| 4 | Unit tests | `pytest -q` (from `apps/orchestrator/`) | All pass |
| 5 | Straggler grep | `grep -ri "gpt-4o-realtime" apps/ infra/ docs/ .env.example` | Zero hits |
| 6 | Frame-schema sanity | Manual review: confirm `input_audio_buffer.append`, `session.update`, `response.create` are valid for the GA endpoint | Verified |

## Rollback

Single revert commit restores `gpt-4o-realtime-preview` everywhere. No data migration, no breaking config-key changes, no downstream coordination needed.

## Complexity Tracking

No constitution violations. Change is mechanical (7 files, config + docs only, no new dependencies, no architectural shifts).
