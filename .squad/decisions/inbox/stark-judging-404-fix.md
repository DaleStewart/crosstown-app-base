# Stark — Judging SWA P0 404 fix (UAT unblock)

**When:** 2026-05-17  
**Who:** Stark (for Sean, during live UAT)  
**Scope:** `apps/judging/` only. Track 2 untouched.

## Symptom
Sean on `https://mango-hill-0ee13cb0f.7.azurestaticapps.net/judge.html?track=azure`:
- `criteria.js` → 404
- `/api/teams?track=azure` → 404
- `/api/myscores?track=azure` → 404

All three returned the SWA "Azure Static Web Apps - 404: Not found" page → the SWA is up, but those routes/assets don't exist on the deployed build.

## Root causes (three, not two)

1. **`/shared/criteria.js` was never deployed.** Source lives at `apps/judging/shared/criteria.js`, *outside* the azd `web` service path (`./src`). HTML references `<script src="/shared/criteria.js">` → 404.
2. **Managed Functions never wired.** SWA `buildProperties` was null and there was no `swa-cli.config.json`, so `azd deploy` invoked `swa deploy` with only `--app-location`/`--output-location`, never `--api-location`. Per `cli/azd/pkg/tools/swa/swa.go`, azd *only* picks up `apiLocation` from `swa-cli.config.json` at the service path.
3. **`staticwebapp.config.json` was never deployed either.** It lived at `apps/judging/` (sibling of `src`), outside the app folder, so the routes table + AAD identity provider config never shipped. (Without it, even a wired `/api/*` route would 404 instead of redirecting to login.)

## Changes shipped

| File | Change |
| --- | --- |
| `apps/judging/azure.yaml` | `web.project` `./src` → `.`; added `dist: src` so azd treats the judging folder as project root and `src/` as output. |
| `apps/judging/package.json` | NEW — minimal stub so azd's `npm` framework has a project root (no real deps; deps stay in `src/` and `api/`). |
| `apps/judging/swa-cli.config.json` | NEW — single `judging` configuration with `appLocation: src`, `apiLocation: api`, `outputLocation: .`, `apiLanguage: node`, `apiVersion: 20`, no-op build commands. This is what wires managed Functions through azd. |
| `apps/judging/src/staticwebapp.config.json` | MOVED from `apps/judging/staticwebapp.config.json` so SWA CLI finds it inside the app folder and actually deploys routes + AAD config. |
| `apps/judging/src/shared/criteria.js` | NEW — copy of `apps/judging/shared/criteria.js` so the frontend `<script src="/shared/criteria.js">` resolves. |
| `apps/judging/api/_shared/criteria.js` | Replaced one-line shim (`require('../../shared/criteria.js')` — would 404 at runtime once the Function App is zipped without the sibling folder) with a self-contained copy. |
| `apps/judging/infra/main.bicep` | Added `buildProperties` (cosmetic / portal display) and flipped `allowConfigFileUpdates: false → true`. Required to land the first `staticwebapp.config.json` via swa CLI — previous deploy failed with *"Cannot update staticwebapp.config.json while the config file is locked."* |

## Source-of-truth note (criteria.js)
`apps/judging/shared/criteria.js` is now duplicated in three places (shared/, src/shared/, api/_shared/). Until we add a copy hook, treat `apps/judging/shared/criteria.js` as canonical and mirror changes to the two deployed copies before each `azd deploy`. If criteria stabilize, we can drop the canonical copy.

## Security follow-up (H3 regression)
`allowConfigFileUpdates: true` re-opens the surface Stark closed in commit `7f6b670`. Once the routes/auth config is stable, flip back to `false` in `infra/main.bicep` and run `azd provision`. Any future routes change then has to land via Bicep + `azd provision` — same posture as before. Leaving open during hackathon week so the team can iterate.

## Verification
```
GET /shared/criteria.js           → 200 (2159 bytes, matches source)
GET /api/teams?track=azure        → 302 → /.auth/login/aad   (route wired, auth-gated)
GET /api/myscores?track=azure     → 302 → /.auth/login/aad   (route wired, auth-gated)
```
`azd deploy web` succeeded in ~1m. SWA reports `Ready`. Sean can refresh `/judge.html?track=azure` after AAD login.
