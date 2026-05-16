# `azd up` Pre-Flight Report — 2026-05-15

**Author:** Okoye (Ops/DevOps)
**Requested by:** Brady (segayle)
**Customer demo:** Tuesday 2026-05-19
**Scope:** Read-only reconnaissance only. **No `azd up` executed.**

---

## 🎯 Target identity (locked per Brady, 2026-05-15)

| Field | Value |
|---|---|
| **Subscription ID** | `47156f11-2e05-4362-ac86-090b4b081b27` |
| **Tenant ID** | `9b7cbd77-6d6b-4879-8aba-63d7dfb18472` |
| **azd env name** | `crosstown-dryrun-may15` |
| **Region** | `eastus2` |

These four values MUST be used together when Brady provisions tomorrow. Bind them up front:

```powershell
az login --tenant 9b7cbd77-6d6b-4879-8aba-63d7dfb18472
az account set --subscription 47156f11-2e05-4362-ac86-090b4b081b27
azd auth login --tenant-id 9b7cbd77-6d6b-4879-8aba-63d7dfb18472
azd env new crosstown-dryrun-may15 `
  --location eastus2 `
  --subscription 47156f11-2e05-4362-ac86-090b4b081b27
```

## ⚠️ Important caveat about this recon

The CLI session available during this pre-flight was authenticated to **a different sandbox** (`ME-MngEnvMCAP651545-segayle-1`, sub `b1ade9aa-...`, tenant `999097f4-...`) — it did **not** have visibility into Brady's target sub `47156f11-...` or tenant `9b7cbd77-...`. Brady must `az login --tenant 9b7cbd77-...` against the correct tenant to re-verify the subscription-scoped checks below.

What's **portable** (verified, applies to any sub):
- ✅ **Bicep compile** — repo state, not sub-specific.
- ✅ **Model regional availability + version strings** — `az cognitiveservices model list` results are catalog-wide, not sub-specific. The eastus2 finding stands.
- ✅ **The P0 Bicep version-pin bug** (§8) — repo state, sub-independent.

What MUST be re-verified on `47156f11-...` before `azd up`:
- 🔁 **Quota** (§4) — `OpenAI.GlobalStandard.gpt-realtime-1.5`, `OpenAI.Standard.gpt-4.1`, vCPU cores. Quotas are per-subscription.
- 🔁 **Provider registration** (§5) — registration state is per-subscription.
- 🔁 **Existing `azd env` collisions** (§6) — `azd env list` is per-machine but env-name uniqueness within the target sub matters when shared.

Recon commands for Brady to re-run after `az login` on the right tenant are in §10.

---

## TL;DR

| Item | Status |
|---|---|
| Target identity locked | ✅ Sub `47156f11-...` / Tenant `9b7cbd77-...` |
| Bicep compile | ✅ Clean (exit 0) |
| Region recommendation | ✅ **`eastus2`** (single region, no split needed) |
| Models available | ✅ `gpt-4.1` and `gpt-realtime-1.5 v2026-02-23` both GA in eastus2 |
| Quota (target sub) | 🔁 **Re-verify on `47156f11-...`** — was clear on the recon sandbox; assumption is fresh sub = empty usage |
| Provider registration (target sub) | 🔁 **Re-verify on `47156f11-...`** — may need 4 providers registered |
| **Bicep model version pin** | 🛑 **P0 BLOCKER — gpt-4.1 pinned to bogus version `2024-11-20`; correct version is `2025-04-14`** |
| **VERDICT** | 🛑 **NO-GO until (a) §8 Bicep fix lands AND (b) §10 sub-scoped re-verify passes** |

---

## 1. Azure context

**Target (per Brady, locked in this report):**
- Sub `47156f11-2e05-4362-ac86-090b4b081b27`
- Tenant `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`

**Recon-time CLI state (different sub, used only for portable catalog/Bicep checks):**
```json
{
  "id":       "b1ade9aa-a8a5-454e-9531-3f8ba1b1a06a",
  "name":     "ME-MngEnvMCAP651545-segayle-1",
  "tenantId": "999097f4-0a95-4a60-b69a-2a50bdf72f6e",
  "user":     "admin@MngEnvMCAP651545.onmicrosoft.com"
}
```

The current CLI login is **not** in the target tenant. `az account set --subscription 47156f11-...` returned *"doesn't exist in cloud 'AzureCloud'"* because that sub lives behind a different Entra tenant. Quota / provider numbers in this report come from the recon sandbox; treat them as a representative baseline, not as authoritative for the target sub.

## 2. Bicep validation

```
az bicep build --file infra/main.bicep --stdout > $null
EXIT=0
```

✅ Bicep compiles clean with no warnings. The repo's single template root `infra/main.bicep` parameterises one `location` (default `eastus2`), so every resource lands in the same region — no cross-region split is supported by the current IaC. *Repo state — portable across subs.*

## 3. Region recommendation — **`eastus2`**

### Model availability (live `az cognitiveservices model list`, catalog-wide)

| Region | gpt-4.1 (v2025-04-14, Standard) | gpt-realtime-1.5 (v2026-02-23, GlobalStandard) | Verdict |
|---|---|---|---|
| **eastus2** | ✅ GA | ✅ GA | **RECOMMENDED** |
| swedencentral | ✅ GA | ✅ GA | Viable fallback (EU residency) |
| westus3 | ✅ GA | ❌ Not listed | ❌ |
| eastus | ✅ GA | ❌ Not listed | ❌ |

### Why eastus2

1. Both required models (gpt-4.1 + gpt-realtime-1.5) co-resident — no cross-region split needed (which `main.bicep` doesn't support without refactor anyway).
2. Matches `main.bicep` default — zero parameter overrides required.
3. Lowest latency from NYC for a US customer demo.
4. AI Search Basic, Cosmos SQL Serverless, ACA, ACR Basic, Speech S0, Key Vault, App Insights, Postgres Flex B1ms all GA in eastus2.

### Cross-region split — not needed, not supported

`main.bicep` exposes a single `location` param. Foundry/AOAI/Speech/Search/Cosmos/ACA all consume it directly. Refactor only required if a future region split becomes a hard requirement. **Not blocking for Tuesday.**

## 4. Quota check (🔁 baseline from recon sandbox — re-verify on target sub)

### AOAI / Cognitive Services — observed on `b1ade9aa-...` / eastus2

| Quota | Bicep ask | Recon-sub current | Recon-sub limit |
|---|---|---|---|
| `OpenAI.GlobalStandard.gpt-realtime-1.5` | 10 | 0 | **10** |
| `OpenAI.Standard.gpt-4.1` | 10 | 30 | 1000 |

> ⚠️ **gpt-realtime-1.5 default tier limit is 10 — exactly equal to Bicep's ask.** If the target sub has the same default ceiling, it fits but with zero headroom. If anything is already deployed in `47156f11-...`, this fails. **This is the single most important value to re-verify** (§10 step 3).

### Compute (ACA consumption profile)

ACA Consumption doesn't pre-allocate VMs; baseline vCPU limits in eastus2 were 100 across all SKU families. Comfortable.

### Postgres

B1ms Burstable in eastus2 — no per-SKU quota gates observed. Standard for any Azure sub.

## 5. Provider registration (🔁 re-verify on target sub)

The 11 providers `main.bicep` needs:

```
Microsoft.CognitiveServices, Microsoft.Search, Microsoft.DocumentDB,
Microsoft.App, Microsoft.ContainerRegistry, Microsoft.KeyVault,
Microsoft.Insights, Microsoft.OperationalInsights,
Microsoft.DBforPostgreSQL, Microsoft.MachineLearningServices,
Microsoft.Storage
```

On the recon sandbox, 7 were already `Registered`; 4 needed registration (`Microsoft.Search`, `Microsoft.OperationalInsights`, `Microsoft.MachineLearningServices`, `Microsoft.DBforPostgreSQL`). Brady's target sub may differ. The §10 one-liner registers any that aren't.

## 6. azd environment

**Recommended name:** `crosstown-dryrun-may15`

Bind it to the exact sub + region at creation time so there's zero ambiguity:

```bash
azd env new crosstown-dryrun-may15 \
  --location eastus2 \
  --subscription 47156f11-2e05-4362-ac86-090b4b081b27
```

Rationale: prefix `crosstown-` matches `DevPost-Test-Hackathon/crosstown-app`; `dryrun` flags non-customer scope; `may15` dates it so Tuesday's customer env can be a separate name (e.g. `crosstown-customer-may19`) without resource-group collisions (`<env>-<token>` pattern).

## 7. Rough cost (idle, eastus2, 24h)

| Resource | SKU | $/day idle |
|---|---|---|
| ACA env + 3 apps (consumption, scale-to-zero) | Consumption | ~$0.10 (KEDA polling) |
| Azure OpenAI gpt-4.1 + gpt-realtime-1.5 | Pay-per-token | $0 idle |
| AI Search | Basic | ~$2.50 |
| Cosmos DB SQL | Serverless | $0 idle |
| ACR Basic | Basic | ~$0.17 |
| Key Vault | Standard | $0 idle |
| App Insights + Log Analytics | PAYG | ~$0.10 (low ingest) |
| Speech Services S0 | Pay-per-call | $0 idle |
| Postgres Flex B1ms | B1ms + 32GB | ~$0.45 |
| Storage (Foundry hub) | LRS Hot | ~$0.05 |
| AI Foundry hub + project | Basic | $0 (infra only) |

**Idle total: ~$3.40/day**, dominated by AI Search Basic + Postgres B1ms. 4-day window (Fri–Mon) + Tuesday demo ≈ **$15–25**. Voice exercises add per-minute realtime token costs on top.

> 💡 `azd down --purge` after the customer demo for a clean teardown.

## 8. 🛑 P0 BLOCKER — Bicep model-version mismatch

`infra/modules/foundry.bicep` line 77 pins:

```bicep
resource gpt4oDeployment '...' = {
  name: 'gpt-4.1'
  sku: { name: 'Standard', capacity: 10 }
  properties: {
    model: {
      name: 'gpt-4.1'
      version: '2024-11-20'   // ❌ DOES NOT EXIST FOR gpt-4.1
    }
  }
}
```

`az cognitiveservices model list -l eastus2` reports the **only available `gpt-4.1` version is `2025-04-14`** (GA, deprecation 2026-10-14). `2024-11-20` is a gpt-4o version that was copy-pasted in. **`azd up` will fail at the model-deployment step.**

This is repo state and sub-independent — the bug exists regardless of which subscription is used.

### Fix (5-minute edit, must land before Tuesday)

```diff
- version: '2024-11-20'
+ version: '2025-04-14'
```

gpt-realtime-1.5 pin `version: '2026-02-23'` (foundry.bicep line 93) is correct — verified live against the model catalog.

## 9. GO / NO-GO

🛑 **NO-GO until BOTH:**
1. §8 Bicep fix is committed and merged to `main`.
2. §10 sub-scoped re-verification passes on `47156f11-...` (quota + provider registration).

After both: ✅ **GO** with:

| Setting | Value |
|---|---|
| Subscription | `47156f11-2e05-4362-ac86-090b4b081b27` |
| Tenant | `9b7cbd77-6d6b-4879-8aba-63d7dfb18472` |
| Region | `eastus2` |
| azd env | `crosstown-dryrun-may15` |

Expected `azd up` runtime: 25–35 min (Foundry hub + project + 2 model deployments are the long poles).

## 10. Monday-morning re-verify checklist (run on the target sub)

```powershell
# 0. Re-auth on the correct tenant
az login --tenant 9b7cbd77-6d6b-4879-8aba-63d7dfb18472
az account set --subscription 47156f11-2e05-4362-ac86-090b4b081b27
az account show --query '{name:name, id:id, tenantId:tenantId}' -o json
# Expect: id == 47156f11-..., tenantId == 9b7cbd77-...

# 1. Bicep still compiles + gpt-4.1 version is correct
az bicep build --file infra/main.bicep --stdout > $null
Select-String -Path infra/modules/foundry.bicep -Pattern "2025-04-14"  # must hit
Select-String -Path infra/modules/foundry.bicep -Pattern "2024-11-20"  # must NOT hit

# 2. All 11 providers registered
@('Microsoft.CognitiveServices','Microsoft.Search','Microsoft.DocumentDB',
  'Microsoft.App','Microsoft.ContainerRegistry','Microsoft.KeyVault',
  'Microsoft.Insights','Microsoft.OperationalInsights',
  'Microsoft.DBforPostgreSQL','Microsoft.MachineLearningServices',
  'Microsoft.Storage') | ForEach-Object {
    $s = az provider show --namespace $_ --query registrationState -o tsv
    if ($s -ne 'Registered') { az provider register --namespace $_ | Out-Null; "$_ : kicked off" }
    else { "$_ : Registered" }
  }

# 3. CRITICAL — quota for the two model deployments
az cognitiveservices usage list --location eastus2 `
  --query "[?contains(name.value, 'gpt-realtime-1.5') || contains(name.value, 'gpt4.1') || contains(name.value, 'gpt-4.1')].{Quota:name.value, Current:currentValue, Limit:limit}" `
  -o table
# Required: GlobalStandard.gpt-realtime-1.5 has (Limit - Current) >= 10
# Required: Standard.gpt4.1            has (Limit - Current) >= 10

# 4. azd env name not already in use locally
azd env list   # must not contain 'crosstown-dryrun-may15'

# 5. Create env bound to target sub + region
azd auth login --tenant-id 9b7cbd77-6d6b-4879-8aba-63d7dfb18472
azd env new crosstown-dryrun-may15 --location eastus2 --subscription 47156f11-2e05-4362-ac86-090b4b081b27
```

If all five steps pass clean → `azd up`. If gpt-realtime-1.5 quota is below 10, file a quota-increase ticket Monday AM (typical turnaround 2–24h) before proceeding.

---

*Tools run live during recon: az CLI 2.6x, az bicep, az cognitiveservices, az provider, azd env list — all against recon sandbox `b1ade9aa-...`. Catalog/Bicep findings are portable; quota + provider state require sub-scoped re-verification per §10.*
