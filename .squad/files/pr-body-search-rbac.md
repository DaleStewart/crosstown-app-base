## P1 hackathon-blocker — found post-provision during Tuesday 2026-05-19 customer-handoff dry-run

`infra/modules/search.bicep` did not set `authOptions` or `disableLocalAuth`. Azure's default for new Search services is **`authOptions: { apiKeyOnly: {} }`** — bearer tokens are rejected entirely, regardless of any RBAC role assignments.

Result: the post-provision search-index loader (`scripts/load_search_index.py`) and any runtime client using `DefaultAzureCredential` (orchestrator, log_analyst) get **HTTP 403 Forbidden** when calling Search admin or data-plane APIs. Verified via direct REST probe to `https://srch-…/indexes` with a fresh AAD bearer token — confirmed 403 even with `Search Index Data Contributor` and `Search Service Contributor` already assigned to the principal.

This violates architectural contract #5 in `.github/copilot-instructions.md`:

> **Auth is keyless.** All Azure SDK clients use `DefaultAzureCredential` against a single user-assigned managed identity ... Never add API-key auth or secrets to env files; secrets flow through Key Vault.

## Fix

Set `disableLocalAuth: true` on the Search service (Option 1 from Brady's two-option spec — the cleanest match for the keyless mandate).

```bicep
properties: {
  replicaCount: 1
  partitionCount: 1
  publicNetworkAccess: 'enabled'
  semanticSearch: 'free'
  // Keyless auth — RBAC only. Bearer tokens via DefaultAzureCredential.
  disableLocalAuth: true
}
```

Setting `disableLocalAuth: true` forces Azure to flip `authOptions` away from the default `apiKeyOnly` mode. After this lands and `azd provision` runs, the existing UAMI role assignments (`Search Index Data Contributor`, `Search Service Contributor` — already in `infra/modules/roleAssignments.bicep:121–139`) and the user role assignment (`Search Index Data Contributor`, line 205–213) will work as intended.

If Azure's resource provider rejects an in-place change of this property on a service that was created in `apiKeyOnly` mode, the recovery is `az search service delete` then re-provision. **Either path is fine — Brady authorized the deletion fallback.** Will note in the dry-run report which path was taken.

## Role assignment audit (no changes needed)

`infra/modules/roleAssignments.bicep` already covers everything required for keyless Search access:

| Principal | Role | Lines |
|---|---|---|
| UAMI | Search Index Data Contributor | 121–129 |
| UAMI | Search Service Contributor | 131–139 |
| Deploying user | Search Index Data Contributor | 205–213 |

No role assignment additions in this PR — the bug is purely the auth-mode flag.

## Verification

- `az bicep build --file infra/main.bicep --stdout > $null` → exit 0.
- After merge + re-provision, expected:
  - `az search service show -n <name> -g <rg> --query disableLocalAuth` → `true`
  - `Invoke-RestMethod -Uri "$searchUrl/indexes?api-version=2024-07-01" -Headers @{Authorization="Bearer <aad-token>"}` → 200 (was 403)
  - `azd hooks run postprovision` → loader populates `mta-logs` + `mta-runbooks` indexes (was 403 Forbidden)

## PR stack

This stacks on top of **#8** (`fix(infra): cap Foundry Hub & Project names at 32 chars`), which itself stacks on **#7** (`fix(infra): omit Key Vault purgeProtection`). Recommended merge order:

1. **#5** (already merged before this session — gpt-4.1 version pin)
2. **#7** (KV purge protection)
3. **#8** (Foundry name length)
4. **#9** (this PR — Search keyless RBAC)

All four are required for `azd up` + post-provision to complete cleanly on the Vocareum tenant in swedencentral. Together they unblock Phase 2.5 (live eval gate) for the Tuesday 2026-05-19 customer demo, paired with Banner's separate `aiohttp` dep PR for the orchestrator (Bug #5, in flight in parallel).

## Context

- Full triage + state inventory: `.squad/files/azd-up-result-2026-05-15.md` — covers all four bugs (gpt-4.1 version, KV policy, Foundry naming, Search auth) and the swedencentral region pivot.
- Architecture contract: `.github/copilot-instructions.md` § Architectural contracts → #5 (Auth is keyless).
- Pre-flight: `.squad/files/azd-up-preflight-2026-05-15.md` (D-017).

Co-authored-by: Copilot &lt;223556219+Copilot@users.noreply.github.com&gt;
