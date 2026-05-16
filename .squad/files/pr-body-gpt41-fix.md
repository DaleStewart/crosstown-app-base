## 🛑 P0 — Blocks `azd up` (customer handoff Tuesday 2026-05-19)

### Problem
`infra/modules/foundry.bicep` pinned the `gpt-4.1` model deployment to **`version: '2024-11-20'`**. That version string **does not exist** in the Azure OpenAI model catalog for `gpt-4.1` — it appears to be a stale copy-paste of a `gpt-4o` version.

Live catalog check on the target region:

```
$ az cognitiveservices model list -l eastus2 \
    --query "[?model.name=='gpt-4.1'].{name:model.name, version:model.version, lifecycle:model.lifecycleStatus}" -o table

Name     Version     Lifecycle
-------  ----------  ------------------
gpt-4.1  2025-04-14  GenerallyAvailable
```

The only GA version of `gpt-4.1` is `2025-04-14` (deprecation 2026-10-14). `azd up` would fail at the model-deployment step.

### Fix (single-line change)
```diff
- version: '2024-11-20'
+ version: '2025-04-14'
```

### Scope discipline
This PR fixes **only** the `gpt-4.1` version pin. I also scanned the rest of `infra/` for other potentially-stale Cognitive Services model versions / SKUs:

| Location | Pin | Status |
|---|---|---|
| `foundry.bicep:77` gpt-4.1 | `'2024-11-20'` → `'2025-04-14'` | ✅ **fixed in this PR** |
| `foundry.bicep:93` gpt-realtime-1.5 | `'2026-02-23'` | ✅ Verified correct (matches D-009; live catalog confirms GA in eastus2) |
| `postgres.bicep:27` Postgres engine | `version: '16'` | ✅ Supported engine version, not a model pin |
| All other `2024-XX` strings in `infra/` | ARM API versions (`@2024-03-01`, `@2024-05-15`, `@2024-04-01`, `@2024-08-01`) | ✅ Not model pins — valid resource type API versions |

No other model version pins exist in `infra/`. Speech service uses an SKU only.

### Verification
```
$ az bicep build --file infra/main.bicep --stdout > $null
$ echo $LASTEXITCODE
0
```

Clean compile.

### Provenance
- Bug discovered during pre-flight reconnaissance ahead of the Tuesday customer handoff.
- Full pre-flight report: `.squad/files/azd-up-preflight-2026-05-15.md`
- Target identity locked for provisioning: sub `47156f11-2e05-4362-ac86-090b4b081b27`, tenant `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`, region `eastus2`, env `crosstown-dryrun-may15`.

### Decision
Will be captured as **D-016** — "gpt-4.1 version pin corrected; `azd up` unblocked".

### Labels
`P0` · `blocker` · `infra` · `azd-up`
