# Okoye — Judging app deploy (mtahack-prod)

**Date:** 2026-05-17
**Outcome:** ✅ Success — `azd up` provisioned + deployed in 3m04s on the first non-prereq pass.

## URL
- Live: https://mango-hill-0ee13cb0f.7.azurestaticapps.net/ (HTTP 200 on smoke test)

## Resources (RG `rg-mtahack-prod`, sub `Devpost-1`, region `eastus2`)
- SWA: `mtahack-swa-5vqz4ojvidqwi`
- Cosmos (serverless): `mtahack-cosmos-5vqz4ojvidqwi`, DB `mtahack`
- azd env: `mtahack-prod`
- Bootstrap admin: `segayle@microsoft.com` (set via `ADMIN_EMAILS` SWA app setting)

## Fix applied during deploy
**Symptom:** First `azd up` failed at packaging:
```
ERROR: step "package-web" failed: ... npm error path C:\Users\segayle\repos\package.json
npm error code ENOENT
```
The `web` service declares `language: js` + `host: staticwebapp` in `azure.yaml`, so azd invokes `npm install` in `./src`. `./src` is vanilla HTML/CSS/JS with no `package.json`, so npm walked up the directory tree until it landed in `C:\Users\segayle\repos\` (no manifest there either) and exploded.

**Fix:** Added a minimal no-op `apps/judging/src/package.json` (private, version 0.1.0, `build` is an echo). This is purely build hygiene — no runtime behavior changes, no dependencies. After this, azd packaged cleanly and the SWA CLI `swa deploy` step succeeded end-to-end.

**Alternative considered:** Drop `language: js` from `azure.yaml`. Rejected — azd's staticwebapp packager still expects a project file when host is `staticwebapp`, and the npm step is what wires up the `swa deploy` toolchain. The package.json is the conventional fix.

## Sean's next actions (not Okoye's lane)
1. AAD identity provider setup on the SWA (Authentication blade → tenant-restrict to microsoft.com).
2. Add `AAD_CLIENT_ID` / `AAD_CLIENT_SECRET` SWA app settings.
3. Replace `{{TODO_TENANT_GUID}}` in `apps/judging/staticwebapp.config.json` and redeploy.
4. (Optional) Deploy the `./api` Functions if azd skipped them — README documents the `swa deploy ./src --api-location ./api ...` escape hatch. Spot-check `/api/leaderboard` from the live URL to confirm whether the API is bundled.
5. Seed teams from `scripts/teams.csv` per README "Seed teams" section.

## Stay-in-lane check
Touched only `apps/judging/` (`src/package.json` added, `README.md` "Live deployment" heading added) and `.squad/decisions/inbox/okoye-judging-deploy.md`. No orchestrator / log_analyst / frontend files modified. T'Challa's root-PR review untouched.
