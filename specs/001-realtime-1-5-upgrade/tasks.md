# Tasks: Foundry Realtime Model Upgrade

**Input**: Design documents from `specs/001-realtime-1-5-upgrade/`

**Prerequisites**: plan.md (required), spec.md (required)

## Format: `[ID] Description`

All tasks are complete. This is a retrospective record of the work shipped on 2026-05-15.

---

## Phase 1: Infrastructure (Bicep)

**Purpose**: Update Foundry deployment resource to the GA model.

- [x] T001 `bicep-foundry-module` — Update `infra/modules/foundry.bicep`: deployment `name` → `gpt-realtime-1.5`, `model.name` → `gpt-realtime-1.5`, `model.version` → `gpt-realtime-1.5-2026-02-23`. Retain SKU `GlobalStandard` capacity 10. Update inline comment.
- [x] T002 `bicep-main-comment` — Update `infra/main.bicep`: description comment referencing the realtime model.

**Checkpoint**: Bicep resources target the new model. No app or doc changes yet.

---

## Phase 2: Application Config

**Purpose**: Update orchestrator defaults and env example to match the new deployment name.

- [x] T003 `app-settings-default` — Update `apps/orchestrator/settings.py`: default for `azure_openai_realtime_deployment` → `"gpt-realtime-1.5"`.
  - **Depends on**: T001 (deployment name must match Bicep)
- [x] T004 `app-ws-api-version` — Update `apps/orchestrator/voice/foundry_realtime.py`: switch WebSocket URL from preview `api-version` query-param pattern to GA `/openai/v1/realtime?model={deployment}` pattern.
  - **Depends on**: T003
  - **Note**: Discovered mid-flight that the GA endpoint uses a different URL structure than preview. The preview form included `?api-version=...&deployment=...`; the GA form is `/openai/v1/realtime?model={deployment}` with no api-version param. This was not in the original plan and was added as T004 during implementation.
- [x] T005 `env-example` — Update `.env.example`: `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5`.
  - **Depends on**: T001

**Checkpoint**: App config aligned with infra. Orchestrator will connect to the new model on next deploy.

---

## Phase 3: Documentation

**Purpose**: Update docs so hackathon participants see accurate model references.

- [x] T006 [P] `docs-voice` — Update `docs/voice.md`: 5 spots — model name in heading, "How it works" section, "Required Bicep" section, env-var default, troubleshooting table.
  - **Depends on**: T001, T003
- [x] T007 [P] `docs-architecture` — Update `docs/architecture.md`: 2 spots — Azure resources list, Mermaid voice-flow diagram.
  - **Depends on**: T001

**Checkpoint**: Docs reflect the new model. All code + config + docs changes are complete.

---

## Phase 4: Verification

**Purpose**: Confirm all gates pass and no straggler references remain.

- [x] T008 `bicep-build` — Run `az bicep build --file infra/main.bicep --stdout > /dev/null`. Must exit 0.
  - **Depends on**: T001, T002
- [x] T009 `app-tests` — Run `ruff check .`, `mypy --strict .`, `pytest -q` from `apps/orchestrator/`. All must pass.
  - **Depends on**: T003, T004
- [x] T010 `grep-verify` — Run `grep -ri "gpt-4o-realtime" apps/ infra/ docs/ .env.example`. Must return zero hits.
  - **Depends on**: T001–T007

**Checkpoint**: All verification gates green. Work is complete.

---

## Dependencies & Execution Order

### Dependency Graph

```
T001 (bicep-foundry-module)
 ├── T002 (bicep-main-comment) ─────────────────┐
 ├── T003 (app-settings-default)                 │
 │    └── T004 (app-ws-api-version)              │
 ├── T005 (env-example)                          │
 ├── T006 (docs-voice)                           │
 ├── T007 (docs-architecture)                    │
 └────────────────────────────────────────────────┤
      T008 (bicep-build) ← T001, T002            │
      T009 (app-tests) ← T003, T004              │
      T010 (grep-verify) ← T001–T007 ────────────┘
```

### Actual Execution Order

Tasks were executed sequentially in the order listed (T001 → T010). T006 and T007 (docs) could have run in parallel but were done sequentially for simplicity.

---

## Summary

| Metric | Value |
|---|---|
| Total tasks | 10 |
| Completed | 10 |
| Blocked | 0 |
| Files touched | 7 |
| Mid-flight additions | 1 (T004 — WS URL pattern change) |
| Verification gates | 3 (bicep build, ruff+mypy+pytest, straggler grep) |
