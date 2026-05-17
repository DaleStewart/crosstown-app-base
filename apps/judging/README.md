# MTA Hackathon — Coach Scoring App

Azure Static Web App that hackathon coaches use to score teams at the NYC MTA AI Agent Hackathon (May 19–20, 2026). Two tracks (Azure / Foundry and Copilot Studio), live leaderboard, lockable judging.

## Live deployment

- **URL:** https://mango-hill-0ee13cb0f.7.azurestaticapps.net/
- **Resource group:** `rg-mtahack-prod` (subscription `Devpost-1`, region `eastus2`)
- **SWA:** `mtahack-swa-5vqz4ojvidqwi`
- **Cosmos:** `mtahack-cosmos-5vqz4ojvidqwi` (serverless, DB `mtahack`)
- **azd env:** `mtahack-prod`
- **Bootstrap admin:** `segayle` (GitHub username, configured via `ADMIN_USERS` app setting; additional admins can be invited from the SWA Role Management blade)
- **Deployed:** 2026-05-17 via `azd up` (Okoye)

Post-provision follow-ups before judges sign in (see sections below for full detail):

1. Set `ADMIN_USERS` app setting with comma-separated GitHub usernames (e.g., `segayle,otheradmin`).
2. Seed teams from `scripts/teams.csv` (see "Seed teams" below).

## Architecture
- Frontend: vanilla HTML/CSS/JS (no build step) served by Azure Static Web Apps
- API: Azure Functions (Node 20, JS) bundled as SWA managed Functions
- DB: Azure Cosmos DB for NoSQL (serverless, East US 2). Containers: `teams`, `scores`, `events` (partition `/track`)
- Auth: SWA built-in GitHub OAuth (no app registration needed). Admin role gated for `/admin.html` and admin-only API routes.

## Prerequisites
- Node 20+
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- Azure subscription
- (Optional) Azure Static Web Apps CLI for local dev: `npm i -g @azure/static-web-apps-cli`

## Local dev
1. `cd apps/judging`
2. Copy `api/local.settings.json.example` → `api/local.settings.json` and fill in a real Cosmos DB connection string (use the Cosmos Emulator or a dev account).
3. From `apps/judging/`: `swa start ./src --api-location ./api`
4. Open http://localhost:4280

SWA CLI proxies API calls to Functions and emulates auth — use the auth simulator at http://localhost:4280/.auth/me to set fake roles like `admin`.

## Deploy with azd
1. `cd apps/judging`
2. `azd auth login`
3. `azd up`
4. When prompted: pick subscription, region (East US 2 recommended), environment name (e.g., `mtahack-prod`).
5. The output `STATIC_WEB_APP_DEFAULT_HOSTNAME` is your live URL. No further config needed — GitHub OAuth is built-in.

> **Caveat — azd + Static Web Apps:** the `staticwebapp` host in azd deploys the `web` service from `./src` but does not always discover the sibling `./api` folder as managed Functions. If `azd deploy web` skips the API, deploy the API with the SWA CLI instead from `apps/judging/`:
>
> ```bash
> swa deploy ./src --api-location ./api \
>   --deployment-token "$(az staticwebapp secrets list -n <swa-name> --query properties.apiKey -o tsv)" \
>   --env production
> ```

## Configure auth (one-time, post-provision)
1. In the Azure Portal, open the Static Web App → Configuration → Application settings.
2. Add `ADMIN_USERS` = comma-separated list of GitHub usernames (lowercase, e.g., `segayle,alice,bob`).
3. Save. GitHub OAuth is pre-configured in `staticwebapp.config.json` — no further action needed.
4. Test by opening `/judge.html` in incognito — you should be redirected to GitHub login.

## Assign admin role
1. In the Azure Portal, open the Static Web App → Role Management.
2. Invite a user by email, assign role `admin`.
3. They'll get an invite link — once accepted, they can hit `/admin.html`.

Alternatively, the `ADMIN_USERS` app setting is read as a comma-separated allowlist of GitHub usernames that grants admin server-side. Use that to bootstrap before the role-management invite flow.

## Seed teams
1. Fill in `apps/judging/scripts/teams.csv` (header: `name,track,members,room,slot`; `members` semicolon-separated).
2. Make sure you have admin access on the SWA (see above).
3. Capture an auth cookie from a signed-in browser session (DevTools → Application → Cookies → copy `StaticWebAppsAuthCookie`).
4. Run:
   ```bash
   node scripts/seed-teams.js \
     --url https://<your-swa-hostname> \
     --csv ./scripts/teams.csv \
     --token "<StaticWebAppsAuthCookie value>"
   ```

OR: Use the [Cosmos DB Data Explorer](https://learn.microsoft.com/azure/cosmos-db/data-explorer) to insert team docs directly (matches the schema in `infra/main.bicep` / `apps/judging/shared/criteria.js`).

## Schema reference
- `teams`: `{ id, name, track, members: [], room, slot }`
- `scores`: `{ id (= '${judgeEmail}|${teamId}'), judgeEmail, judgeName, teamId, teamName, track, criteria: {id:1-5}, notes: {id:string}, total, tier, submittedAt, locked }`
- `events`: `{ id, ts, actor, action, payload }` + a special `lock-status-{track}` doc reflecting current lock state.

## Files
```
apps/judging/
  azure.yaml
  staticwebapp.config.json
  infra/
    main.bicep
    main.parameters.json
  api/
    host.json
    package.json
    _shared/
    teams-list/  teams-create/  myscores/  score-submit/  leaderboard/  lock/  export/
  shared/criteria.js
  src/
    index.html  judge.html  admin.html
    styles.css  auth.js  toast.js
  scripts/
    seed-teams.js
    teams.csv
```
