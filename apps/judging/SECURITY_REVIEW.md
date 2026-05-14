# Security Review — MTA Hackathon Judging App
**Reviewer:** Strange  |  **Date:** 2026-05-13  |  **Scope:** apps/judging/

## Verdict
🟡 Ship after must-fix items

---

## Critical (must fix before shipping)

### C1 — CSV Export: Formula Injection
- **File:** `api/export/index.js:6-9`
- **Impact:** When team names, judge emails, or notes contain `=`, `+`, `-`, `@`, a malicious value (e.g., `=cmd|'/C calc'!A0`) will be executed by Excel when the admin opens the CSV. Attacker only needs to convince an admin to create a team with a crafted name, or a judge can inject via notes.
- **Fix:** Prefix any cell starting with `=`, `+`, `-`, `@`, `\t`, `\r` with a single-quote (`'`) inside `csvEscape()`:
  ```js
  function csvEscape(v) {
    if (v === null || v === undefined) return '';
    let s = String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    if (/[",\r\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
    return s;
  }
  ```

### C2 — `{{TODO_TENANT_GUID}}` Placeholder Still in Config
- **File:** `staticwebapp.config.json:6`
- **Impact:** If deployed as-is, the AAD `openIdIssuer` URL is invalid. SWA behavior with an invalid issuer is **undefined** — it could fail open (allow any tenant) or fail closed (block all). Neither is acceptable for production.
- **Fix:** Replace `{{TODO_TENANT_GUID}}` with the real Microsoft tenant GUID (`72f988bf-86f1-41af-91ab-2d7cd011db47`) before deploy, or wire it dynamically via the Bicep `AAD_TENANT_ID` setting that already exists.

---

## High (fix before shipping if possible)

### H1 — Missing Security Response Headers
- **File:** `staticwebapp.config.json:27-29`
- **Impact:** No `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, or `Referrer-Policy` headers. The app is frameable (clickjacking) and has no CSP to mitigate XSS.
- **Fix:** Add to `globalHeaders`:
  ```json
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy": "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; font-src https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
  ```

### H2 — Cosmos DB Public Network Access Enabled, No Firewall
- **File:** `infra/main.bicep:52` (`publicNetworkAccess: 'Enabled'`)
- **Impact:** The Cosmos account is reachable from the public internet. If the connection string leaks (ARM deployment history, env vars), anyone can read/write all data.
- **Fix:** Add `ipRules` limiting to Azure Static Web App outbound IPs or use a managed-identity RBAC approach with `disableLocalAuth: true`. At minimum, set `publicNetworkAccess: 'SecuredByPerimeter'` or add `ipRules`.

### H3 — `allowConfigFileUpdates: true` on SWA
- **File:** `infra/main.bicep:102`
- **Impact:** A compromised deployment pipeline or branch could push a new `staticwebapp.config.json` that removes all auth routes, opening the app to unauthenticated access.
- **Fix:** Set `allowConfigFileUpdates: false` in production and manage config exclusively via Bicep/ARM.

### H4 — No JSON Body Size Limit
- **File:** `api/host.json` (no `extensions.http.maxRequestBodySize` set)
- **Impact:** Default Azure Functions limit is 100 MB. A malicious judge could POST a massive body to any endpoint, exhausting memory on the serverless worker and driving up costs.
- **Fix:** Add to `host.json`:
  ```json
  "extensions": { "http": { "maxRequestBodySize": 102400 } }
  ```
  (100 KB is more than sufficient for score payloads.)

---

## Medium (fix soon)

### M1 — Leaderboard Exposes All Scores Before Lock
- **File:** `api/leaderboard/index.js:19-22`
- **Impact:** Any authenticated judge can call `/api/leaderboard?track=azure` at any time and see aggregated rankings + judge counts. This could bias subsequent judges. The route has no lock-gate.
- **Fix:** Consider restricting `/api/leaderboard` to admin-only, or at least gate it behind track-locked state (only show after scoring closes).

### M2 — Lock Route Also Needs GET Handler for Status Check
- **File:** `api/lock/function.json:3` (only POST method)
- **Impact:** The admin UI calls `GET /api/lock?track=...` (admin.html:193) but the function.json only allows POST. This is a functional bug (the GET silently fails), but also means the frontend lock state may be unreliable.
- **Fix:** Add `"GET"` to the methods array in `api/lock/function.json` and add a GET branch in `index.js` that reads lock status.

### M3 — `.gitignore` Only Covers `api/local.settings.json`
- **File:** `.gitignore:2`
- **Impact:** Common sensitive files like `.env`, `.azure/`, `node_modules/`, and `*.env.local` are not ignored. If a developer drops a `.env` in `apps/judging/` it could be committed.
- **Fix:** Expand `.gitignore` to include `.env*`, `.azure/`, `node_modules/`, `*.pem`, etc.

### M4 — Cosmos Connection String Visible in ARM Deployment History
- **File:** `infra/main.bicep:112`
- **Impact:** `cosmos.listConnectionStrings()` is called inline in the Bicep template. While app settings are encrypted at rest, the ARM deployment history retains the evaluated template, making the connection string visible to anyone with `Microsoft.Resources/deployments/read` on the resource group.
- **Fix:** Use a Key Vault reference or set the app setting via a deployment script with `@secure()` parameter piping.

---

## Low / informational

### L1 — `innerHTML` Usage Is Properly Escaped
- **Files:** `src/judge.html`, `src/admin.html`
- **Impact:** All user-supplied data (team names, member names, notes, criterion labels) is passed through `esc()` → `MTAAuth.escapeHtml()` before insertion into `innerHTML`. **No XSS found.** The `esc` function covers `& < > " '`.
- **Status:** ✅ Acceptable.

### L2 — Toast Uses `textContent`
- **File:** `src/toast.js:26`
- **Status:** ✅ Safe — `textContent` never parses HTML.

### L3 — Seed Script Has No Dev Bypass
- **File:** `scripts/seed-teams.js`
- **Status:** ✅ The script requires explicit `--url` and `--token` flags. It authenticates through the same AAD route as the browser. No backdoor.

### L4 — Dependencies Are Minimal
- **File:** `api/package.json`
- **Status:** Only one runtime dependency (`@azure/cosmos ^4.0.0`). Attack surface is very small. Run `npm audit` before deploy to confirm.

### L5 — Audit Trail Is Server-Side Only
- **File:** `api/_shared/audit.js`
- **Status:** ✅ `logEvent` is only called from server functions. The `events` container has no client-facing write route; only the `lock` function writes the lock-status doc, and it requires admin auth (`requireAdmin`). A judge cannot tamper with the audit trail.

### L6 — Score ID Uses Authenticated Email
- **File:** `api/score-submit/index.js:81`
- **Status:** ✅ The score document `id` is `${user.email}|${teamId}` where `user.email` comes from the decoded `x-ms-client-principal` header (server-side, line 10 of `auth.js`). A judge cannot overwrite another judge's score.

### L7 — Parameterized Cosmos Queries (No SQL Injection)
- **Files:** `api/myscores/index.js:18`, `api/leaderboard/index.js:19`, `api/teams-list/index.js:17`, `api/export/index.js:25`
- **Status:** ✅ All queries use `@param` placeholders. No string interpolation into query text.

### L8 — Score Range Validated Server-Side
- **File:** `api/score-submit/index.js:41`
- **Status:** ✅ `!Number.isInteger(v) || v < 1 || v > 5` rejects out-of-range scores.

### L9 — Lock Enforcement on Score Submit
- **File:** `api/score-submit/index.js:52`
- **Status:** ✅ Even if a judge bypasses the frontend lock UI, the server checks `isTrackLocked(track)` before writing.

---

## What looks good

- **Server-side auth on every endpoint** — all 7 functions call `requireAuth` or `requireAdmin` as their first action. The `x-ms-client-principal` header is decoded server-side; no client-supplied identity is trusted.
- **Admin enforcement is dual-layer** — both SWA route rules AND server `requireAdmin()` guard admin endpoints.
- **HTML escaping** is consistent and correct across all frontend rendering.
- **Cosmos queries are fully parameterized** — zero injection risk.
- **Score identity integrity** — the score `id` derives from the authenticated email, preventing cross-judge overwrites.
- **Lock enforcement is server-side** — judges can't bypass the lock by calling the API directly.
- **Audit logging** is non-blocking but comprehensive; failures don't break user flow.
- **Minimal dependency surface** — one npm package in production.
- **Notes are truncated server-side** (2000 chars) — limits storage abuse.

---

## Deploy-time checklist for Sean

- [ ] Replace `{{TODO_TENANT_GUID}}` in `staticwebapp.config.json` with `72f988bf-86f1-41af-91ab-2d7cd011db47` (Microsoft tenant)
- [ ] Set `ADMIN_EMAILS` env var in azd/Bicep params with actual admin email addresses
- [ ] Run `cd apps/judging/api && npm audit` — confirm no critical vulnerabilities
- [ ] Add security headers (H1) to `staticwebapp.config.json` before deploy
- [ ] Apply CSV formula injection fix (C1) to `api/export/index.js`
- [ ] Consider restricting Cosmos public network access (H2)
- [ ] Set `allowConfigFileUpdates: false` in Bicep for production (H3)
- [ ] Add `maxRequestBodySize` to `host.json` (H4)
- [ ] Verify AAD app registration `redirect_uris` only include the SWA hostname
- [ ] Confirm the `admin` role is assigned via Azure Portal → SWA → Role Management (not auto-granted)
- [ ] Expand `.gitignore` (M3) before any dev onboards
