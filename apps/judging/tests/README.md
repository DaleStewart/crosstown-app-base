# Judging app — tests

Two layers:

1. **Unit smoke** (`unit/criteria.test.js`) — pure Node, no browser. Asserts the scoring math in `apps/judging/shared/criteria.js`.
2. **E2E** (`e2e/*.spec.js`) — Playwright against the SWA CLI dev server with intercepted API responses (no live Cosmos, no live AAD).

## Setup

```bash
cd apps/judging/tests
npm install
npm run install:browsers
```

## Run the dev server (in a separate terminal)

```bash
cd apps/judging
swa start ./src --api-location ./api
```

The app is now on http://localhost:4280. The SWA CLI auth simulator lives at http://localhost:4280/.auth/me — you can hit it in a browser to manually inject a fake `clientPrincipal` (e.g. roles `authenticated`, `admin`).

For automated tests we don't use the simulator UI. Instead Playwright intercepts `/.auth/me` with `page.route()` and returns a stubbed `clientPrincipal`, so each test pins its own identity (anonymous / judge / admin) deterministically.

## Run tests

```bash
# unit smoke (no browser, no server needed)
npm run test:unit

# full E2E suite (needs swa start running)
npm test

# Playwright UI mode
npm run test:ui
```

## Test data

E2E tests do **not** depend on real Cosmos data. They intercept the JSON API surface (`/api/teams`, `/api/myscores`, `/api/score`, `/api/leaderboard`, `/api/lock`) and return inline fixtures. If you ever want to exercise the real API end-to-end, seed teams with `apps/judging/scripts/seed-teams.js` against a dev Cosmos account.
