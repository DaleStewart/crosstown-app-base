# Bug #4 Status — AI Search keyless RBAC auth — 2026-05-15

**Author:** Okoye
**Status:** ✅ **FIXED.** Awaiting Banner's PR + final orchestrator redeploy + `/api/turn` smoke test before Phase 2.5 GO.
**Time:** 2026-05-15 PM (Brady AFK; executed under autopilot per his explicit Step A–C plan)

## What was done

1. **PR #9 opened** — https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/9
   - Branch: `squad/fix-search-rbac-auth` (stacked on PR #8)
   - **Auth-mode option chosen: Option 1** (`disableLocalAuth: true` + no `authOptions`) — Brady's preferred, matches the keyless mandate.
   - 1-line addition to `infra/modules/search.bicep` properties block.
   - Role assignments: **no changes needed**. `infra/modules/roleAssignments.bicep` already covers UAMI (Search Index Data Contributor lines 121–129 + Search Service Contributor lines 131–139) and the deploying user (Search Index Data Contributor lines 205–213). The bug was purely the auth-mode flag.

2. **Branch collision recovery** — Banner created `squad/fix-orchestrator-aiohttp-dep` between my `git commit` and my `git push`, capturing my new commit on Banner's branch ref. Recovered by `git branch -f squad/fix-search-rbac-auth 0095a3e` + `--force-with-lease` push. Banner's branch was independently advanced afterwards (Banner's own commit `6d99f2d` is now in place; Banner's branch is unaffected by my fix).

3. **`azd provision` (attempt 4) — happy path.** ARM accepted the in-place auth-options change in **1.6 s** for the Search service; total provision wall-clock **3 min 5 s**. **No Search delete needed.** Customer dry-run on Tuesday will see the same fast in-place path on a fresh `azd up`.

4. **Verified post-fix state:**
   ```json
   { "name":"srch-crosstown-dryrun-may15-yycemmso7sk7q",
     "disableLocalAuth": true,
     "authOptions": null,
     "publicNetworkAccess": "Enabled" }
   ```
   Direct AAD-bearer probe to `/indexes?api-version=2024-07-01` → **HTTP 200** (was 403).

5. **`azd hooks run postprovision` — Search portion fully green:**
   - `mta-logs` index upserted ✅
   - `mta-logs` populated → **5,000 log docs** (verified via AAD `$count` probe)
   - `mta-runbooks` populated → **10 runbook docs** (verified via AAD `$count` probe)

## Caveat carried forward — NOT Okoye's domain

The same hook **also** runs `seed_incidents()` against Cosmos DB. That step now fails with:

```
azure.cosmos.exceptions.CosmosHttpResponseError: (BadRequest)
Message: {"Errors":["One of the specified inputs is invalid"]}
```

This is **not** the Search auth bug recurring — Search loaded fully. It's a script-level / data-shape problem in `scripts/load_search_index.py:128–138` (`seed_incidents`). Likely candidates: missing or mismatched `id`/`incidentId` partition-key field on the seed payload, or a shape mismatch with the Cosmos container created by Bicep (partition path `/incidentId` per architecture contract #6).

This is **outside the Bug #4 scope** and outside Okoye's Bicep / infra-ops remit. **Escalate to whoever owns `scripts/`** (Banner / Maximoff — TBD) for a script-level fix. The Cosmos container, RBAC, and Cosmos endpoint are all healthy (`AZURE_COSMOS_ENDPOINT` reachable, UAMI + user have data-plane SQL roles per `roleAssignments.bicep:173–181, 226–234`).

**Phase 2.5 impact:** `summarize_incident` tool calls will return uncited until incidents are seeded. `search_logs` and `detect_pattern` work now (5000 logs available).

## Awaiting

- **Banner's aiohttp PR** for orchestrator (Bug #5). Banner has committed `6d99f2d` on `squad/fix-orchestrator-aiohttp-dep` — PR may already be open.
- **Squad-coordinated `azd deploy orchestrator`** to pick up Banner's dep change. **Okoye is NOT running `azd deploy` per Brady's Step D — coordinating instead.**
- **Brady's review/merge** of PRs #7, #8, **#9** (and Banner's, when it lands).
- **Cosmos seed script fix** (separate bug, separate owner — see "Caveat carried forward" above).

After all four bullets close, Squad triggers final `azd deploy` + `/api/turn` smoke test → GREEN-light Phase 2.5.

## References

- PR #9: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/9
- PR body: `.squad/files/pr-body-search-rbac.md`
- Provision log: `.squad/files/azd-provision-stdout-2026-05-15-attempt4.log`
- Postprovision hook log: `.squad/files/azd-hook-postprovision-final.log`
- Updated final result: `.squad/files/azd-up-result-2026-05-15.md` (next pass)
- Architecture contract (keyless mandate): `.github/copilot-instructions.md` § Architectural contracts → #5
