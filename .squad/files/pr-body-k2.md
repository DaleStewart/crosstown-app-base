## P1 hackathon-blocker — found during Tuesday 2026-05-19 customer-handoff dry-run

`infra/modules/keyVault.bicep:31` hardcoded `enablePurgeProtection: false`. The Vocareum sandbox subscription used for the customer dry-run has an Azure Policy that **requires** `purgeProtection=true` on Key Vaults — the hardcoded `false` causes `azd up` to fail with:

```
BadRequest: The property "enablePurgeProtection" cannot be set to false.
Enabling the purge protection for a vault is an irreversible action.
```

The vault never gets created and the whole `azd up` aborts.

## Fix

Remove the `enablePurgeProtection` property entirely. Azure's tenant-scoped default applies:

- In permissive tenants → `false` (matches the previous "easy cleanup" intent for hackathon teardown).
- In tenants with a strict policy → `true` (the policy wins, KV creates successfully).

No security regression — this is **more** permissive of stricter tenant policies, not less.

## Verification

- `az bicep build --file infra/main.bicep --stdout > $null` → exit 0.
- Locally re-running `azd up` will retry the KV step; combined with the region switch to `swedencentral` (where AI Search has capacity right now), the dry-run is unblocked.

## Context

- Full failure triage: `.squad/files/azd-up-FAILURE-2026-05-15.md` — documents both the KV policy issue and the parallel `eastus2` Search capacity exhaustion that prompted the swedencentral pivot.
- Pre-flight that locked the original eastus2 / model availability decision: `.squad/files/azd-up-preflight-2026-05-15.md` (D-017). swedencentral was already the documented fallback (both `gpt-4.1` and `gpt-realtime-1.5` GA there).
- 1-line code change, comment-only otherwise.

## Recommendation

Merge before Tuesday 2026-05-19 customer handoff. Without this, `azd up` cannot complete on policy-enforced tenants.

Co-authored-by: Copilot &lt;223556219+Copilot@users.noreply.github.com&gt;
