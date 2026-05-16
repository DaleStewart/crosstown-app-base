# Lab Dry-Run Runbook — Full Sweep

**Date:** 2026-05-15 (updated 2026-05-15 — customer handoff scope)
**Author:** Stark (Architect)
**Purpose:** Walk the entire hackathon lab end-to-end before the Hackathon Accelerator customer handoff on **Tuesday 2026-05-19**. Everything must be customer-crisp.
**Strategy:** `azd up` once, verify deployed stack, run full eval/test gates live, then validate all 9 exercise scaffolds. Implement EX-01 as a full smoke test; for EX-02–EX-09, verify failing tests fail for the right reason. Any exercise where failing tests aren't cleanly reachable is a **P0 fix before Tuesday**.

---

## Phase 0 — Pre-flight (~5 min, parallel with Okoye)

### 0.1 Subscription & identity

```powershell
az account show --query "{sub:name, id:id, tenant:tenantId}" -o table
azd auth login          # interactive browser flow, one-time
```

- Confirm the subscription has **no spending cap** and is Pay-As-You-Go or Enterprise.
- Confirm your user has **Owner** or **Contributor + User Access Administrator** on the target RG (azd creates it).

### 0.2 Region recommendation

**Use `eastus2`** (the Bicep default). Rationale:

| Service | eastus2 GA? | Notes |
|---|---|---|
| gpt-4.1 (Standard, 10K TPM) | ✅ | D-006 |
| gpt-realtime-1.5 (GlobalStandard, 10K TPM) | ✅ | D-009; `GlobalStandard` routes globally, region is billing anchor only |
| Azure AI Search (Basic + Semantic free tier) | ✅ | |
| Cosmos DB Serverless | ✅ | |
| Azure Speech S0 | ✅ | |
| Container Apps | ✅ | |
| PostgreSQL Flexible Server (B1ms) | ✅ | |

**⚠️ Fallback region:** If `eastus2` quota is exhausted for `gpt-realtime-1.5`, try `eastus` or `swedencentral`. Change via `azd env set AZURE_LOCATION <region>`.

### 0.3 Environment name

```powershell
azd env new mtalab
azd env set AZURE_LOCATION eastus2
```

Pick a short name (≤10 chars) — it feeds into resource names with length limits (KV max 24, ACR max 50).

### 0.4 Pre-flight acceptance

- [ ] `az account show` returns the correct subscription
- [ ] `azd env list` shows `mtalab` as default
- [ ] `azd env get-values` shows `AZURE_LOCATION=eastus2`
- [ ] No `.env` files with stale secrets exist in the repo (keyless auth only, per D-008)

---

## Phase 1 — Provision (~30–40 min, blocking)

### 1.1 Invoke azd up

```powershell
azd up --no-prompt
```

This runs, in order:
1. **`azd provision`** — deploys `infra/main.bicep` (targetScope: resourceGroup)
2. **`azd deploy`** — builds & pushes 3 Docker images (log-analyst, orchestrator, frontend) to ACR, deploys to ACA
3. **`postprovision` hook** — runs `scripts/load_search_index.ps1` → `scripts/load_search_index.py`

### 1.2 Expected resource list (13 resources + role assignments)

| # | Resource | Type | Key config |
|---|---|---|---|
| 1 | Log Analytics workspace | `operationalInsights/workspaces` | Telemetry sink |
| 2 | Application Insights | `insights/components` | Workspace-based |
| 3 | User-Assigned Managed Identity | `managedIdentity/userAssignedIdentities` | Shared by all 3 apps |
| 4 | Key Vault (RBAC mode) | `keyVault/vaults` | Stores AI conn string |
| 5 | Container Registry (Basic) | `containerRegistry/registries` | Admin disabled, AcrPull via UAMI |
| 6 | Container Apps Environment | `app/managedEnvironments` | Single env |
| 7 | AI Foundry Hub | `machineLearningServices/workspaces` (kind=Hub) | |
| 8 | AI Foundry Project | `machineLearningServices/workspaces` (kind=Project) | |
| 9 | Azure OpenAI account | `cognitiveServices/accounts` (kind=OpenAI) | gpt-4.1 + gpt-realtime-1.5 |
| 10 | AI Search (Basic) | `search/searchServices` | Semantic free tier |
| 11 | Cosmos DB Serverless | `documentDB/databaseAccounts` | DB: `mta`, containers: `incidents`, `conversations` |
| 12 | PostgreSQL Flexible Server | `dbForPostgreSQL/flexibleServers` | B1ms, idle, Entra-only auth |
| 13 | Speech Services (S0) | `cognitiveServices/accounts` | Voice fallback |
| + | 3× Container Apps | `app/containerApps` | log-analyst (internal:8001), orchestrator (external:8000), frontend (external:80) |
| + | Role Assignments | Various RBAC | UAMI → Cosmos, Search, KV, ACR, AOAI, Speech, AppInsights; User → same |

### 1.3 Post-provision hook verification

The hook runs `scripts/load_search_index.py` which:
- Creates search index `mta-logs` (fields: log_id, timestamp, line, station, severity, event_type, etc.)
- Creates search index `mta-runbooks`
- Loads documents from `data/` using `DefaultAzureCredential`
- Seeds Cosmos DB `mta` database with incident documents

```powershell
# Verify indices exist
azd env get-values | Select-String "AZURE_SEARCH_ENDPOINT"
# Then:
az search index list --service-name <search-name> --resource-group <rg> -o table
```

### 1.4 Phase 1 acceptance

- [ ] `azd up` exits 0
- [ ] All resources visible in Azure Portal under the RG
- [ ] `az search index list` shows `mta-logs` and `mta-runbooks`
- [ ] Container Apps all show "Running" revision status
- [ ] Post-provision hook log shows document count > 0

---

## Phase 2 — Smoke verify deployed stack (~10 min)

### 2.1 Capture endpoints

```powershell
$env:ORCH_URL = (azd env get-values | Select-String "ORCHESTRATOR_URL" | ForEach-Object { $_.ToString().Split('=',2)[1].Trim('"') })
$env:FE_URL = (azd env get-values | Select-String "FRONTEND_URL" | ForEach-Object { $_.ToString().Split('=',2)[1].Trim('"') })
Write-Output "Orchestrator: $env:ORCH_URL"
Write-Output "Frontend:     $env:FE_URL"
```

### 2.2 Health endpoints

```powershell
curl -s "$env:ORCH_URL/health" | ConvertFrom-Json
# Expected: {"status": "ok"} or similar 200 response

curl -s "$env:FE_URL" -o $null -w "%{http_code}"
# Expected: 200 (HTML page)
```

### 2.3 One happy-path turn (live Foundry call)

```powershell
$body = '{"message": "What happened on line L1 last month?"}'
curl -s -X POST "$env:ORCH_URL/api/turn" `
  -H "Content-Type: application/json" `
  -d $body | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

**Expected response shape:**
```json
{
  "text": "...",
  "citations": [ { "type": "log", ... } ],
  "tool_calls": [ { "name": "search_logs", ... } ],
  "warnings": []
}
```

### 2.4 WebSocket connectivity (quick check)

```powershell
# Use wscat or a browser — open $env:FE_URL, click push-to-talk, confirm WS handshake in DevTools
# Alternatively:
npx -y wscat -c "wss://$($env:ORCH_URL -replace 'https://','')'/ws/voice" --no-check
# Should connect (then close — voice requires audio frames)
```

### 2.5 Phase 2 acceptance

- [ ] Orchestrator `/health` returns 200
- [ ] Frontend loads in browser (HTML, no 5xx)
- [ ] `/api/turn` returns a response with `citations` array (at least 1 citation)
- [ ] `tool_calls` array contains `search_logs` entry
- [ ] `warnings` does NOT contain `"uncited"`
- [ ] WebSocket connection established (even if no audio sent)

---

## Phase 2.5 — Full eval + test gate (~20–30 min, blocking)

> **Gate rule:** ALL green. Any yellow blocks the Tuesday 2026-05-19 customer handoff.

### 2.5.1 Banner gate — local lint/type/test for all services

Run from the repo root. Every command must exit 0.

**Orchestrator:**
```powershell
cd apps/orchestrator
pip install -e ".[dev]" --quiet
ruff check .
mypy --strict .
pytest -v
cd ../..
```

**Log Analyst:**
```powershell
cd apps/log_analyst
pip install -e ".[dev]" --quiet
ruff check .
mypy --strict .
pytest -v
cd ../..
```

**Frontend:**
```powershell
cd apps/frontend
npm ci --silent
npm run lint
npm run typecheck
npm test -- --run
npm run build
cd ../..
```

**Bicep sanity:**
```powershell
az bicep build --file infra/main.bicep --stdout > $null
```

### 2.5.2 Maximoff gate — live eval gates against deployed orchestrator

All eval gates run in **live mode** against the ACA-deployed orchestrator — NOT cassettes. This proves the actual Foundry models, AI Search index, and Cosmos data are wired correctly.

```powershell
# Set live-mode env vars (ORCH_URL captured in Phase 2.1)
$env:EVAL_MODE = "live"
$env:ORCHESTRATOR_URL = $env:ORCH_URL
$env:AZURE_OPENAI_ENDPOINT = (azd env get-values | Select-String "AZURE_OPENAI_ENDPOINT" | ForEach-Object { $_.ToString().Split('=',2)[1].Trim('"') })
```

**Citation gate (threshold ≤5% uncited):**
```powershell
cd evals
pip install -r requirements.txt --quiet
python -m runner --max-uncited-pct 5
```

**Orchestrator gate (threshold 0% fail):**
```powershell
python -m orchestrator_runner --max-fail-pct 0
```

**Foundry evaluators (each score ≥3.0):**
```powershell
python -m runner --with-foundry
```

**Red team (0 high/critical, ≤10% overall):**
```powershell
cd ../redteam
pip install -r requirements.txt --quiet
python -m runner --max-fail-pct 10
cd ..
```

### 2.5.3 Phase 2.5 acceptance

- [ ] `ruff check` exits 0 for both Python services
- [ ] `mypy --strict` exits 0 for both Python services
- [ ] `pytest -v` all green for both Python services
- [ ] Frontend: `lint` + `typecheck` + `test` + `build` all exit 0
- [ ] `az bicep build` exits 0
- [ ] Citation gate LIVE: ≤5% uncited (expect 0%)
- [ ] Orchestrator gate LIVE: 0% failures
- [ ] Foundry evaluators LIVE: all scores ≥3.0
- [ ] Red team LIVE: 0 high/critical findings, ≤10% overall failure rate

**🚨 If any gate fails:** Stop. Diagnose and fix before proceeding to Phase 3. A failing gate means the skeleton itself is broken — that's a P0 for customer handoff.

---

## Phase 3 — Walk the 9 exercises

### Strategy

- **EX-01 (Add Health Analyst):** Full implementation smoke test — build it, make all tests pass. This validates the entire create-service → register-tool → run-tests loop.
- **EX-02 through EX-09:** Verify scaffolding only — run tests, confirm they fail with the expected error (missing module / missing file / missing function), NOT with infrastructure errors or import crashes.

---

### EX-01 · Add Health Analyst Agent ⭐ FULL IMPLEMENTATION

| Field | Value |
|---|---|
| **ID** | EX-01 |
| **What it adds** | New FastAPI service `apps/health_analyst/` with 3 tools: `pull_health_report`, `find_hidden_issues`, `open_ticket`. Orchestrator routing update. |
| **Dependencies** | None (standalone) |
| **Test file** | `docs/extensions/01_add_health_analyst/tests/test_health_analyst.py` |
| **Tests (6)** | `test_health_endpoint`, `test_pull_health_report_returns_200_with_citations`, `test_find_hidden_issues_returns_issues_list`, `test_open_ticket_returns_ticket_number`, `test_orchestrator_routes_health_query_to_health_analyst`, `test_health_analyst_tool_registry_completeness` |
| **Validation** | `pytest docs/extensions/01_add_health_analyst/tests/ -v` → all 6 pass |
| **Estimated time** | 30–45 min (with Copilot assistance) |
| **Pass criteria** | All 6 tests green. Existing `pytest apps/orchestrator/ -q` and `pytest apps/log_analyst/ -q` still pass (no regressions). |

**Implementation steps:**

1. Copy `apps/log_analyst/` → `apps/health_analyst/` as starting skeleton
2. Replace tools with `pull_health_report`, `find_hidden_issues`, `open_ticket`
3. Ensure all tool responses include `citations` key (citation contract)
4. Create `apps/orchestrator/routing.py` with `select_agent()` function that routes SCADA/health/bridge/ticket queries to `health_analyst`
5. Ensure `apps/health_analyst/tools.py` exports all 3 tool names
6. Run: `pytest docs/extensions/01_add_health_analyst/tests/ -v`
7. Run: `pytest apps/orchestrator/ -q && pytest apps/log_analyst/ -q` (regression check)

**Pre-implementation baseline:**
```powershell
pytest docs/extensions/01_add_health_analyst/tests/ -v 2>&1 | Select-Object -First 20
# Expected: all 6 SKIPPED (importorskip: "apps/health_analyst not yet implemented")
```

---

### EX-02 · Swap Grounding Corpus

| Field | Value |
|---|---|
| **ID** | EX-02 |
| **What it adds** | New JSONL files in `data/mock_logs/`, corpus README, bumped version in load script |
| **Dependencies** | None |
| **Test file** | `docs/extensions/02_swap_grounding_corpus/tests/test_corpus.py` |
| **Tests (4)** | `test_corpus_readme_exists`, `test_corpus_has_team_jsonl_files`, `test_jsonl_entries_are_valid`, `test_load_script_version_bumped` |
| **Expected failure** | `test_corpus_readme_exists` → `AssertionError: Create data/mock_logs/README.md`; `test_corpus_has_team_jsonl_files` → `Found <N> .jsonl file(s)... Add at least 5`; `test_load_script_version_bumped` → `corpus-version is still 1` or `Could not find a '# corpus-version'` |
| **Validation command** | `pytest docs/extensions/02_swap_grounding_corpus/tests/ -v` |
| **Estimated time** | 2 min (verify only) |
| **Pass criteria** | Tests fail with descriptive assertion messages (not import errors or tracebacks). The failure tells the team exactly what to create. |

```powershell
pytest docs/extensions/02_swap_grounding_corpus/tests/ -v 2>&1 | Select-Object -Last 20
# Expect: 3-4 FAILED with clear assertion messages, 0 ERROR
```

---

### EX-03 · Add Tool (correlate_lines)

| Field | Value |
|---|---|
| **ID** | EX-03 |
| **What it adds** | `correlate_lines(line_a, line_b, window_min)` function + endpoint on log analyst; tool registry entry on orchestrator |
| **Dependencies** | None |
| **Test file** | `docs/extensions/03_add_tool/tests/test_add_tool.py` |
| **Tests (4)** | `test_correlate_lines_exists_in_tools_module`, `test_correlate_lines_returns_required_keys`, `test_correlate_lines_endpoint_returns_200`, `test_tool_registry_includes_correlate_lines` |
| **Expected failure** | `test_correlate_lines_exists_in_tools_module` → `AssertionError: Add 'correlate_lines' to apps/log_analyst/tools.py`; `test_tool_registry_includes_correlate_lines` → `apps/orchestrator/tool_registry not found` |
| **Validation command** | `pytest docs/extensions/03_add_tool/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | Tests fail on missing function/registry, not on import errors for existing modules (`apps.log_analyst.main` and `apps.log_analyst.tools` must import successfully). |

```powershell
pytest docs/extensions/03_add_tool/tests/ -v 2>&1 | Select-Object -Last 20
# tests 1-2: FAILED (hasattr check), test 3: FAILED (missing route), test 4: SKIPPED (tool_registry not found)
```

---

### EX-04 · Legacy Modernization (ASP.NET → FastAPI)

| Field | Value |
|---|---|
| **ID** | EX-04 |
| **What it adds** | `legacy/SampleController.cs` (pasted), `apps/legacy_service/main.py` (FastAPI port) |
| **Dependencies** | None |
| **Test file** | `docs/extensions/04_legacy_modernization/tests/test_legacy_service.py` |
| **Tests (7)** | `test_legacy_cs_file_exists`, `test_legacy_cs_contains_incidents_route`, `test_legacy_service_module_importable`, `test_health_route`, `test_get_all_incidents`, `test_get_incident_by_id`, `test_get_incident_invalid_id`, `test_create_incident`, `test_create_incident_empty_body` |
| **Expected failure** | `test_legacy_cs_file_exists` → `AssertionError: Paste the SampleController.cs snippet`; `test_legacy_service_module_importable` → SKIPPED (`apps/legacy_service not implemented`) |
| **Validation command** | `pytest docs/extensions/04_legacy_modernization/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | First 2 tests FAIL (file missing), remaining tests SKIPPED or FAIL on import — no infrastructure errors. |

---

### EX-05 · Wire Legacy to Agent

| Field | Value |
|---|---|
| **ID** | EX-05 |
| **What it adds** | `query_incidents` tool on log analyst, routing hint in orchestrator |
| **Dependencies** | **EX-04** (needs `apps/legacy_service/` to exist for the tool to call) |
| **Test file** | `docs/extensions/05_wire_legacy_to_agent/tests/test_wire_legacy.py` |
| **Tests (5)** | `test_query_incidents_exists`, `test_query_incidents_no_id_returns_list`, `test_query_incidents_with_id_returns_single`, `test_query_incidents_endpoint_returns_200`, `test_routing_hint_mentions_query_incidents` |
| **Expected failure** | `test_query_incidents_exists` → `AssertionError: Add 'query_incidents' to apps/log_analyst/tools.py` |
| **Validation command** | `pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | Tests fail on missing `query_incidents` attribute, not on broken imports. Tests use `unittest.mock.patch("httpx.get")` so no live legacy service needed. |

---

### EX-06 · Enable Modernize-PR Workflow

| Field | Value |
|---|---|
| **ID** | EX-06 |
| **What it adds** | Rename `.github/workflows/modernize-pr.yml.disabled` → `.yml`, add `workflow_dispatch` trigger, remove `if: false` |
| **Dependencies** | None |
| **Test file** | `docs/extensions/06_enable_modernize_pr/tests/test_workflow.py` |
| **Tests (6)** | `test_workflow_file_exists`, `test_disabled_file_is_gone`, `test_workflow_is_valid_yaml`, `test_workflow_has_on_trigger`, `test_workflow_dispatch_trigger_defined`, `test_no_if_false_guard`, `test_workflow_has_at_least_one_job` |
| **Expected failure** | `test_workflow_file_exists` → `AssertionError: Rename ... to modernize-pr.yml`; `test_disabled_file_is_gone` passes (trivially, since we check `.disabled` doesn't exist — wait, `.disabled` DOES exist, so this will also fail) |
| **Validation command** | `pytest docs/extensions/06_enable_modernize_pr/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | `test_workflow_file_exists` FAILS (`.yml` doesn't exist); `test_disabled_file_is_gone` FAILS (`.disabled` still exists). Remaining tests FAIL on missing file. All failures are clear assertion messages. |

**⚠️ Pre-req check:** Confirm `.github/workflows/modernize-pr.yml.disabled` exists:
```powershell
Test-Path ".github\workflows\modernize-pr.yml.disabled"
# Expected: True
```

---

### EX-07 · Frontend Rebrand

| Field | Value |
|---|---|
| **ID** | EX-07 |
| **What it adds** | `apps/frontend/src/theme.ts` (brand tokens), `apps/frontend/src/components/IncidentDetailView.tsx`, route at `/incidents/:id` |
| **Dependencies** | None |
| **Test file** | `docs/extensions/07_frontend_rebrand/tests/IncidentDetailView.test.tsx` |
| **Tests (3)** | `theme.ts exports brandTokens with required colour fields`, `IncidentDetailView.tsx has a default export`, `IncidentDetailView renders id, line, description, status, and citations` |
| **Expected failure** | Dynamic `import()` fails → `Error: Failed to resolve ... apps/frontend/src/theme` and `... IncidentDetailView` |
| **Validation command** | `cd apps/frontend && npx vitest run docs/extensions/07_frontend_rebrand/tests/IncidentDetailView.test.tsx` (run from repo root, vitest resolves relative imports) |
| **Estimated time** | 3 min |
| **Pass criteria** | Tests fail on missing module resolution, not on test framework config errors. Vitest itself loads and runs. |

**⚠️ Note:** This test uses JSX (`render(<IncidentDetailView {...mockProps} />)`), so vitest must be configured with React/JSX transform. Verify the frontend's `vitest.config` or `vite.config.ts` handles `.tsx`.

---

### EX-08 · Custom Evals

| Field | Value |
|---|---|
| **ID** | EX-08 |
| **What it adds** | ≥3 new YAML scenario files in `evals/scenarios/` |
| **Dependencies** | None |
| **Test file** | `docs/extensions/08_custom_evals/tests/test_custom_evals.py` |
| **Tests (5)** | `test_scenarios_dir_exists`, `test_at_least_three_new_scenario_files`, `test_scenario_files_have_required_fields`, `test_scenarios_use_only_fictional_lines`, `test_expected_tools_are_strings` |
| **Expected failure** | `test_at_least_three_new_scenario_files` → `Found 0 team-authored scenario file(s)... Create at least 3` |
| **Validation command** | `pytest docs/extensions/08_custom_evals/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | `test_scenarios_dir_exists` PASSES (dir exists from skeleton). `test_at_least_three_new_scenario_files` FAILS with count < 3 message. Remaining tests FAIL on "No team-authored YAML files found yet." |

**⚠️ Gotcha:** The test uses `SKELETON_SCENARIO_FILES: set[str] = set()` — meaning ALL yaml files in the dir count as "team-authored." If the skeleton ships with any scenario yamls, they'll count toward the 3. Verify:
```powershell
Get-ChildItem evals/scenarios/*.yaml, evals/scenarios/*.yml -ErrorAction SilentlyContinue | Select-Object Name
```

---

### EX-09 · Postgres Target

| Field | Value |
|---|---|
| **ID** | EX-09 |
| **What it adds** | `query_legacy_db(sql)` tool on log analyst with SQLite fallback, POST endpoint, env-gated Postgres |
| **Dependencies** | None (SQLite fixture is self-contained; `fixtures/schema.sql` ships with the exercise) |
| **Test file** | `docs/extensions/09_postgres_target/tests/test_postgres_target.py` |
| **Tests (6)** | `test_query_legacy_db_exists`, `test_query_legacy_db_select_returns_rows`, `test_query_legacy_db_rejects_non_select`, `test_query_legacy_db_where_clause`, `test_query_legacy_db_endpoint_returns_200`, `test_schema_fixture_file_exists` |
| **Expected failure** | `test_query_legacy_db_exists` → `AssertionError: Add 'query_legacy_db' to apps/log_analyst/tools.py`; `test_schema_fixture_file_exists` → PASSES (fixture ships with repo) |
| **Validation command** | `pytest docs/extensions/09_postgres_target/tests/ -v` |
| **Estimated time** | 2 min |
| **Pass criteria** | `test_schema_fixture_file_exists` PASSES. `test_query_legacy_db_exists` FAILS on missing attribute. Other tests FAIL on missing function. No import errors for `apps.log_analyst.main` or `apps.log_analyst.tools`. |

**⚠️ Note:** The Postgres Flexible Server provisioned by `azd up` is idle — no schema applied, no data. That's by design. The tests use SQLite via the `patch_query_legacy_db_to_use_sqlite` autouse fixture.

---

### Exercise dependency map

```
EX-01  EX-02  EX-03  EX-04  EX-06  EX-07  EX-08  EX-09
  │      │      │      │       │      │      │      │
  │      │      │      ▼       │      │      │      │
  │      │      │    EX-05     │      │      │      │
  │      │      │              │      │      │      │
  ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
  (independent unless noted: EX-05 requires EX-04)
```

---

## Phase 4 — Teardown decision

### Options

| Option | Command | Cost/day (idle) | When to use |
|---|---|---|---|
| **A. Keep running** | _(no action)_ | ~$15–25/day | Hackathon is ≤48 hrs away; teams need a live endpoint to test against |
| **B. Stop Container Apps (keep infra)** | `az containerapp revision deactivate` for each app | ~$8–12/day | Hackathon is >2 days away; saves ACA compute but keeps data plane intact |
| **C. Full teardown** | `azd down --purge --force` | $0 | Re-provision from scratch before hackathon (adds 30–40 min setup day-of) |

### Cost breakdown (idle estimate)

| Resource | Idle $/day |
|---|---|
| Azure OpenAI (gpt-4.1 + gpt-realtime-1.5, 0 tokens) | $0.00 (pay-per-token) |
| AI Search Basic | ~$3.50 |
| Cosmos DB Serverless (0 RU) | ~$0.00 |
| Container Apps (3 apps, min 0 replicas if scaled to 0) | ~$0–5 (depends on min replicas) |
| PostgreSQL B1ms | ~$4.00 |
| Speech S0 | ~$0.00 (pay-per-use) |
| Key Vault, UAMI, App Insights, Log Analytics | ~$1–3 |
| ACR Basic | ~$1.70 |
| Foundry Hub storage | ~$0.50 |
| **Total idle** | **~$10–18/day** |

### Recommendation

**For Tuesday 2026-05-19 handoff:** Use **Option A** (keep running). The customer needs a live stack to demo. Cost from dry-run day (2026-05-15) through hackathon end (2026-05-20) is ~5 days × $15 = **~$75–90 total**. Budget accordingly.

After the hackathon (2026-05-20 evening): **Option C** (`azd down --purge --force`). No reason to keep idle resources.

---

## Risks & gotchas

### R-01: gpt-realtime-1.5 regional capacity
- **Risk:** `GlobalStandard` deployment may hit subscription-level TPM quota.
- **Mitigation:** Check quota before `azd up`: `az cognitiveservices usage list --location eastus2 -o table`. If blocked, request quota increase or switch to `swedencentral`.

### R-02: Post-provision hook flakiness
- **Risk:** `scripts/load_search_index.py` uses `DefaultAzureCredential`. If the azd principal doesn't have Search Index Data Contributor + Cosmos DB roles yet (ARM propagation delay), the script fails.
- **Mitigation:** Hook has `continueOnError: true` in `azure.yaml`. If it fails, wait 2 min for RBAC propagation, then re-run manually:
  ```powershell
  python scripts/load_search_index.py
  ```

### R-03: ACR image pull latency
- **Risk:** First `azd deploy` builds 3 Docker images and pushes to ACR. On a slow connection, this can take 15+ minutes.
- **Mitigation:** Run on a fast network. If it times out, `azd deploy` again (idempotent).

### R-04: Frontend vite.config.ts
- **Risk:** D-014 identified a pre-existing TS error. D-015 (PR #3) fixed it. **Ensure PR #3 is merged before running the dry run.**
- **Mitigation:** Verify: `cd apps/frontend && npx tsc --noEmit` should exit 0.

### R-05: EX-07 vitest JSX transform
- **Risk:** The EX-07 test file uses JSX (`<IncidentDetailView />`). If vitest isn't configured with the React plugin, the test runner will crash on syntax, not on missing module.
- **Mitigation:** Verify `apps/frontend/vite.config.ts` includes `@vitejs/plugin-react`. If the test runner crashes on JSX parse, that's a scaffolding bug — fix the vitest config, not the exercise.

### R-06: EX-03 and EX-05 import path assumptions
- **Risk:** Tests import `apps.orchestrator.tool_registry` and `apps.orchestrator.routing` respectively. These modules may not exist in the skeleton (they're part of the exercise deliverable). The tests use `pytest.importorskip` so they'll SKIP, not ERROR.
- **Impact:** Low — SKIP is an acceptable "not yet implemented" signal.

### R-07: Python path / editable installs
- **Risk:** Extension tests import `apps.health_analyst.main`, `apps.legacy_service.main`, etc. These are new packages not in the skeleton's `pyproject.toml`. Tests must be run from the repo root with the right `PYTHONPATH` or editable installs.
- **Mitigation:** Before running extension tests:
  ```powershell
  $env:PYTHONPATH = (Get-Location).Path
  ```
  Or run `pip install -e .` from the repo root if a root `pyproject.toml` with package discovery exists.

### R-08: EX-02 corpus-version comment
- **Risk:** `test_load_script_version_bumped` looks for `# corpus-version: <N>` in `scripts/load_search_index.py`. If the skeleton doesn't ship this comment, the test fails with "Could not find" rather than "Bump it" — which is still a clear failure message but slightly confusing.
- **Mitigation:** Verify the comment exists: `Select-String "corpus-version" scripts/load_search_index.py`. If absent, that's expected — the team adds it as part of the exercise.

### R-09: 🚨 P0 — Unreachable failing tests block customer handoff
- **Risk:** Any exercise where the failing test is NOT cleanly reachable — e.g., it depends on infra that wasn't provisioned, imports a module that no longer exists at the expected path, or crashes with a traceback instead of a clean assertion — is a **P0 fix before Tuesday 2026-05-19**. A customer team doing `git clone` + `azd up` + `pytest docs/extensions/NN_*/tests/ -v` must see clean FAILED/SKIPPED with human-readable messages, never ERROR tracebacks.
- **Specific exercises to audit:**
  - **EX-01:** `test_health_analyst.py` uses `pytest.importorskip("apps.health_analyst.main")` → should SKIP cleanly ✅
  - **EX-02:** `test_corpus.py` checks file existence → should FAIL with "Create data/mock_logs/README.md" ✅ (but verify `# corpus-version` comment scenario per R-08)
  - **EX-03:** `test_add_tool.py` uses `importorskip("apps.log_analyst.main")` → should import OK, then FAIL on missing `correlate_lines` ✅; BUT `test_tool_registry_includes_correlate_lines` imports `apps.orchestrator.tool_registry` which may not exist → should SKIP via `importorskip` ✅
  - **EX-04:** `test_legacy_service.py` checks `legacy/SampleController.cs` file existence → should FAIL cleanly ✅
  - **EX-05:** `test_wire_legacy.py` checks `hasattr(tools, "query_incidents")` → should FAIL cleanly ✅; uses `unittest.mock.patch("httpx.get")` so no live service needed ✅
  - **EX-06:** `test_workflow.py` checks `.github/workflows/modernize-pr.yml` file path → should FAIL cleanly ✅; requires `pyyaml` installed ⚠️ (verify it's in dev deps)
  - **EX-07:** `IncidentDetailView.test.tsx` uses dynamic `import()` → should fail on module resolution ✅; BUT needs vitest + React plugin configured correctly (see R-05) ⚠️
  - **EX-08:** `test_custom_evals.py` checks `evals/scenarios/` dir → should PASS on dir existence, FAIL on count ✅; requires `pyyaml` ⚠️
  - **EX-09:** `test_postgres_target.py` uses `importorskip("apps.log_analyst.tools")` → should import OK, then FAIL on missing `query_legacy_db` ✅; `test_schema_fixture_file_exists` should PASS (fixture ships) ✅
- **Action items if any exercise fails with ERROR instead of FAILED/SKIPPED:**
  1. File as P0 bug
  2. Fix the test guard (add `importorskip`, `pytest.mark.skipif`, or file-existence check)
  3. Commit to `main` before Tuesday
- **Mitigation:** Run the full batch in Phase 3, capture stdout, grep for `ERROR` lines. Any `ERROR` (as opposed to `FAILED` or `SKIPPED`) is a P0.

### R-10: pyyaml dependency for EX-06 and EX-08 tests
- **Risk:** `test_workflow.py` (EX-06) and `test_custom_evals.py` (EX-08) import `yaml` (PyYAML). If pyyaml isn't in the dev dependencies of either Python service, these tests crash with `ModuleNotFoundError`.
- **Mitigation:** Verify: `python -c "import yaml"`. If missing, either add pyyaml to a dev-extras group in the root or instruct teams to `pip install pyyaml` before running extension tests. This must work out-of-the-box for the customer — add to requirements if needed.

### R-11: Live eval gates require sufficient AOAI token quota
- **Risk:** Phase 2.5 runs citation gate, orchestrator gate, AND Foundry evaluators all live against the deployed model. That's 8+ scenarios × multiple LLM calls each. If the gpt-4.1 Standard deployment has only 10K TPM, rapid-fire evals may hit rate limits.
- **Mitigation:** Monitor for 429s during eval runs. If throttled, wait 60s between gates or temporarily increase TPM quota in Azure Portal → Azure OpenAI → Deployments → gpt-4.1 → Edit.

---

## Customer-Handoff Acceptance Checklist (Tuesday 2026-05-19)

> Every box must be checked before declaring the accelerator ready for customer delivery.

### Exercise scaffolding
- [ ] **EX-01** tests: `pytest docs/extensions/01_add_health_analyst/tests/ -v` → all 6 SKIPPED (importorskip), 0 ERROR
- [ ] **EX-02** tests: `pytest docs/extensions/02_swap_grounding_corpus/tests/ -v` → 3–4 FAILED with clear messages, 0 ERROR
- [ ] **EX-03** tests: `pytest docs/extensions/03_add_tool/tests/ -v` → 2–3 FAILED + 1 SKIPPED, 0 ERROR
- [ ] **EX-04** tests: `pytest docs/extensions/04_legacy_modernization/tests/ -v` → 2 FAILED + rest SKIPPED, 0 ERROR
- [ ] **EX-05** tests: `pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v` → 4 FAILED + 1 FAILED, 0 ERROR
- [ ] **EX-06** tests: `pytest docs/extensions/06_enable_modernize_pr/tests/ -v` → all 7 FAILED, 0 ERROR
- [ ] **EX-07** tests: `cd apps/frontend && npx vitest run docs/extensions/07_frontend_rebrand/tests/` → FAIL on missing modules, no framework crash
- [ ] **EX-08** tests: `pytest docs/extensions/08_custom_evals/tests/ -v` → 1 PASSED + 4 FAILED, 0 ERROR
- [ ] **EX-09** tests: `pytest docs/extensions/09_postgres_target/tests/ -v` → 1 PASSED (fixture exists) + rest FAILED, 0 ERROR
- [ ] Every exercise reachable by customer via: `git clone` → `azd up` → `pytest docs/extensions/NN_*/tests/ -v`

### Codebase hygiene
- [ ] Zero straggler references to `gpt-4o` (non-realtime) in `.py`, `.bicep`, `.yaml`, `.yml`, `.env*` files — verified via `Select-String -Path apps/**,infra/**,evals/**,redteam/** -Pattern "gpt-4o[^-]" -Recurse`
- [ ] Zero references to removed paths or dead env vars (e.g., old `AZURE_OPENAI_DEPLOYMENT` without the `_CHAT_` or `_REALTIME_` qualifier)
- [ ] No API keys, connection strings, or secrets in tracked files — keyless auth only (D-008)

### PRs & branch state
- [ ] PR #1 (D-009: realtime swap) — merged to main ✅
- [ ] PR #2 (D-011: spec-kit + constitution) — merged to main ✅
- [ ] PR #3 (D-015: vite.config.ts fix) — merged to main ✅
- [ ] PR #4 (scribe re-verify) — merged to main ✅
- [ ] `git log --oneline -5` on `main` includes all 4 PR merge commits
- [ ] No stale/unmerged squad branches that should have been merged

### Documentation
- [ ] `README.md` "Fork → deploy → extend" section is accurate and serves as Day-0 quickstart (lines 60–75)
- [ ] `README.md` extension ladder table (lines 81–91) has correct paths and time estimates for all 9 exercises
- [ ] `docs/architecture.md` reflects current model names (gpt-4.1, gpt-realtime-1.5)
- [ ] `docs/voice.md` reflects GA Foundry Realtime endpoint pattern (no api-version param)
- [ ] `docs/evals.md` and `docs/redteam.md` have correct threshold values matching `evals/calibration.json`
- [ ] `.env.example` has correct deployment names (`gpt-4.1`, `gpt-realtime-1.5`)

### Infrastructure & cost
- [ ] Cost-per-day at idle documented in this runbook (Phase 4): **~$10–18/day**
- [ ] Teardown command documented: `azd down --force --purge`
- [ ] Region recommendation documented: `eastus2` (with fallback guidance)
- [ ] All known gotchas and regional caveats listed in Risks section (R-01 through R-11)

### Live verification (from Phase 2 + 2.5)
- [ ] Orchestrator `/health` returns 200
- [ ] `/api/turn` returns cited response with correct tool routing
- [ ] All eval gates pass LIVE (citation ≤5%, orchestrator 0%, Foundry ≥3.0, red team ≤10%)
- [ ] Frontend loads, no console errors, push-to-talk connects WebSocket

---

## Appendix: Quick-reference commands

```powershell
# Phase 0
azd auth login
azd env new mtalab
azd env set AZURE_LOCATION eastus2

# Phase 1
azd up --no-prompt

# Phase 2
$vals = azd env get-values
# Parse ORCHESTRATOR_URL, FRONTEND_URL from output

# Phase 2.5 — Full eval + test gates (live)
cd apps/orchestrator && ruff check . && mypy --strict . && pytest -v && cd ../..
cd apps/log_analyst && ruff check . && mypy --strict . && pytest -v && cd ../..
cd apps/frontend && npm ci --silent && npm run lint && npm run typecheck && npm test -- --run && npm run build && cd ../..
az bicep build --file infra/main.bicep --stdout > $null
$env:EVAL_MODE = "live"
$env:ORCHESTRATOR_URL = $env:ORCH_URL
$env:AZURE_OPENAI_ENDPOINT = (azd env get-values | Select-String "AZURE_OPENAI_ENDPOINT" | ForEach-Object { $_.ToString().Split('=',2)[1].Trim('"') })
cd evals && python -m runner --max-uncited-pct 5 && python -m orchestrator_runner --max-fail-pct 0 && python -m runner --with-foundry && cd ..
cd redteam && python -m runner --max-fail-pct 10 && cd ..

# Phase 3 — all exercise tests (batch verify)
$env:PYTHONPATH = (Get-Location).Path
pytest docs/extensions/01_add_health_analyst/tests/ -v
pytest docs/extensions/02_swap_grounding_corpus/tests/ -v
pytest docs/extensions/03_add_tool/tests/ -v
pytest docs/extensions/04_legacy_modernization/tests/ -v
pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v
pytest docs/extensions/06_enable_modernize_pr/tests/ -v
cd apps/frontend && npx vitest run docs/extensions/07_frontend_rebrand/tests/ && cd ../..
pytest docs/extensions/08_custom_evals/tests/ -v
pytest docs/extensions/09_postgres_target/tests/ -v

# Phase 3 — P0 check: grep for ERROR lines (any ERROR = fix before Tuesday)
# Re-run all Python extension tests and capture:
pytest docs/extensions/ -v 2>&1 | Select-String "ERROR"
# Expected: zero matches

# Phase 4
azd down --purge --force   # Option C: full teardown
```
