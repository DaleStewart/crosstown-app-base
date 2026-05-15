# Feature Specification: Foundry Realtime Model Upgrade (gpt-4o-realtime-preview → gpt-realtime-1.5)

**Feature Branch**: `001-realtime-1-5-upgrade`

**Created**: 2026-05-15

**Status**: Complete

**Input**: Decision D-009 (realtime model swap), session plan for gpt-4o-realtime-preview → gpt-realtime-1.5-2026-02-23.

## User Scenarios & Testing

### User Story 1 — Deployer provisions updated voice model (Priority: P1)

A hackathon team member runs `azd up` against their Devpost-provisioned Azure subscription. The Foundry Realtime deployment provisions as `gpt-realtime-1.5` (model version `gpt-realtime-1.5-2026-02-23`) instead of the deprecated `gpt-4o-realtime-preview`. No manual intervention or additional env-var changes are needed — `.env.example` already shows the new default.

**Why this priority**: Without the updated deployment, the voice path targets a GA-deprecated preview model. This is the load-bearing change.

**Independent Test**: Run `az bicep build --file infra/main.bicep` — must pass. Inspect the Bicep deployment resource and confirm `model.name` = `gpt-realtime-1.5` and `model.version` = `gpt-realtime-1.5-2026-02-23`.

**Acceptance Scenarios**:

1. **Given** a fresh Azure subscription, **When** the deployer runs `azd up`, **Then** the Foundry account contains a deployment named `gpt-realtime-1.5` with model version `gpt-realtime-1.5-2026-02-23`.
2. **Given** the Bicep files, **When** `az bicep build --file infra/main.bicep` is run, **Then** it exits 0 with no errors.

---

### User Story 2 — Dispatcher uses voice with no visible change (Priority: P1)

An end user (MTA dispatcher) presses the push-to-talk button and speaks. The voice path works identically to before: audio streams over WebSocket, transcripts appear, tool calls fire, cited replies return. The citation contract, endpoint URLs, and env-var names are unchanged.

**Why this priority**: The voice path is the hero flow. If the model swap breaks it, the accelerator is dead.

**Independent Test**: All four CI gates pass (`ci.yml`, `eval.yml`, `redteam.yml` hermetic). `ruff check .` + `mypy --strict .` + `pytest -q` green for the orchestrator.

**Acceptance Scenarios**:

1. **Given** the orchestrator configured with `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5`, **When** a voice turn is processed, **Then** the WebSocket connects to the GA `/openai/v1/realtime?model={deployment}` endpoint and returns transcripts + cited replies.
2. **Given** the updated codebase, **When** `ruff check . && mypy --strict . && pytest -q` is run in `apps/orchestrator/`, **Then** all checks pass with zero failures.

---

### User Story 3 — Documentation reflects current state (Priority: P2)

A hackathon team member reads `docs/voice.md` or `docs/architecture.md` to understand the voice path. All model references say `gpt-realtime-1.5`, not the deprecated preview name. Troubleshooting guidance and region recommendations are accurate for the GA model.

**Why this priority**: Stale docs cause debugging confusion during a two-day hackathon.

**Independent Test**: `grep -ri "gpt-4o-realtime" docs/ .env.example apps/ infra/` returns zero hits.

**Acceptance Scenarios**:

1. **Given** the documentation files, **When** searched for `gpt-4o-realtime-preview`, **Then** zero matches are found in active code/doc paths.

---

### Edge Cases

- What happens if the deployer's subscription region doesn't support `gpt-realtime-1.5-2026-02-23`? → Existing troubleshooting row in `docs/voice.md` covers this ("WS connects then drops in <1s" → check Foundry deployments; consider East US 2 or Sweden Central).
- What if the new GA endpoint uses a different WebSocket frame schema? → Verified during implementation; the frame types (`input_audio_buffer.append`, `session.update`, `response.create`) are supported. Symptom would be immediate WS drop, caught by existing troubleshooting table.

## Requirements

### Functional Requirements

- **FR-001**: Bicep MUST provision a Foundry deployment named `gpt-realtime-1.5` with `model.version` = `gpt-realtime-1.5-2026-02-23` and SKU `GlobalStandard`.
- **FR-002**: Orchestrator MUST default `AZURE_OPENAI_REALTIME_DEPLOYMENT` to `gpt-realtime-1.5` when no env override is set.
- **FR-003**: Orchestrator MUST connect to the GA Realtime endpoint pattern (`/openai/v1/realtime?model={deployment}`) — no `api-version` query parameter.
- **FR-004**: `.env.example` MUST show `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5`.
- **FR-005**: Documentation MUST reference `gpt-realtime-1.5` wherever the realtime model is named.

### Non-Goals

- Do NOT add `gpt-realtime-mini` as a second deployment.
- Do NOT add `gpt-realtime-translate` or `gpt-4o-transcribe-diarize`.
- Do NOT modify the Speech Services fallback path.
- Do NOT rename the `gpt4oRealtimeDeployment` Bicep symbol or the `AZURE_OPENAI_REALTIME_DEPLOYMENT` env-var name (API stability).

### Key Entities

- **Bicep deployment resource** (`infra/modules/foundry.bicep`): the `gpt4oRealtimeDeployment` resource — name, model.name, model.version fields.
- **Orchestrator settings** (`apps/orchestrator/settings.py`): `azure_openai_realtime_deployment` default value.
- **WebSocket URL builder** (`apps/orchestrator/voice/foundry_realtime.py`): endpoint pattern + api-version.

## Success Criteria

### Measurable Outcomes

- **SC-001**: `az bicep build --file infra/main.bicep` exits 0.
- **SC-002**: `ruff check . && mypy --strict . && pytest -q` green for `apps/orchestrator`.
- **SC-003**: `grep -ri "gpt-4o-realtime" apps/ infra/ docs/ .env.example` returns zero hits (excluding `.squad/` historical notes).
- **SC-004**: All four CI gate thresholds maintained (citation ≤5%, orchestrator 0%, foundry ≥3.0, redteam 0 high/critical).

## Assumptions

- `gpt-realtime-1.5-2026-02-23` is available in East US 2 (the default `AZURE_LOCATION`).
- The GA Realtime endpoint at `/openai/v1/realtime?model={deployment}` supports the frame types used by the orchestrator (`input_audio_buffer.append`, `session.update`, `response.create`).
- The `GlobalStandard` SKU with capacity 10 is valid for the new model.
- The Speech Services fallback path is unaffected and requires no changes.

## Risks

- **Api-version frame-schema drift**: If the GA endpoint rejects a frame type the orchestrator sends, the WS drops on first frame. Mitigation: verified frame schema during implementation.
- **Regional availability**: `gpt-realtime-1.5-2026-02-23` may not be available in all regions. Mitigation: East US 2 is the default; troubleshooting table updated.
- **Capacity-unit semantics**: If the new model expects different SKU capacity units, Bicep surfaces a validation error at provision time.
