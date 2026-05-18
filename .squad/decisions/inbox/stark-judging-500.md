# stark-judging-500

**When:** 2026-05-17T22:53-04:00
**Owner:** Stark (at Sean's direction)
**Scope:** apps/judging/

## Symptom
After Sean signed in to the judging SWA via GitHub successfully, the first
`/judge.html` load returned 500 on:
- `GET /api/teams?track=azure`
- `GET /api/myscores?track=azure`

## Investigation (evidence-based)

Verified each candidate from Sean's brief:

1. **Auth principal shape** — `apps/judging/api/_shared/auth.js` already
   tolerates GitHub principals: `principal.userDetails || (emailClaim && emailClaim.val) || ''`,
   then `.toLowerCase()`. For GitHub `userDetails = "segayle"` → `user.email = "segayle"`,
   which is truthy, so `requireAuth` passes (does not throw, does not 401).
   `isAdmin` already prefers `ADMIN_USERS` and falls back to `ADMIN_EMAILS`,
   null-guarded via `(process.env.ADMIN_USERS || process.env.ADMIN_EMAILS || '')`.
   **Not the cause.**

2. **Cosmos containers** — verified live:
   `az cosmosdb sql container list -a mtahack-cosmos-5vqz4ojvidqwi -g rg-mtahack-prod -d mtahack`
   returned `teams`, `events`, `scores`. **All exist.**

3. **SWA app settings** — verified live:
   `az staticwebapp appsettings list -n mtahack-swa-5vqz4ojvidqwi -g rg-mtahack-prod`
   returned `COSMOS_CONNECTION_STRING`, `ADMIN_USERS=msftsean,segayle`,
   `ADMIN_EMAILS=segayle@microsoft.com`. **All set.**

4. **Cosmos query roundtrip** — ran the exact teams-list and myscores
   queries locally against prod Cosmos with the live connection string.
   Both returned 0 rows with no error. **The code path works.**

5. **Deploy is current** — `deploy-judging.yml` succeeded at 2026-05-18T02:34:55Z
   on `398f758`, which is the tip of `main` for `apps/judging/`. No drift.

## Diagnosis

The four most-likely root causes from Sean's brief are all *ruled out* by
direct evidence. The 500 is being thrown from somewhere inside the
try/catch but the response body just says `{error: "Failed to list teams"}`,
which hides the actual Cosmos / runtime error code from anyone debugging
from a browser. No App Insights is wired (`az monitor app-insights component show -g rg-mtahack-prod`
returned empty), so SWA-managed Functions stderr is effectively a black hole.

## Fix shipped

Made the catch blocks in `teams-list/index.js` and `myscores/index.js`
surface the actual error `code` and `message` in the JSON response body
(behind the existing auth gate — these endpoints already require
`authenticated` role per `staticwebapp.config.json`, so no anonymous PII
exposure). Also moved `requireAuth` and `CRITERIA` validation *inside*
the try/catch so any synchronous throw there is captured the same way
instead of becoming an unhandled 500.

This is intentionally a diagnostic-forward fix: Sean's next refresh will
show the real error in DevTools → Network → Response, which then lets us
make a *targeted* second fix (rather than guessing).

## Follow-up

Once Sean reports back with the real `code`/`detail`, dial the response
body back down to `{error: "Failed to list teams"}` and address the
underlying cause in a second PR.
