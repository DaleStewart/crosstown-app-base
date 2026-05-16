## P0 — UAT mic button does nothing

**Discovered:** UAT smoke 2026-05-16. Sean clicked mic on the live frontend; nothing happened.

### Root cause

nginx in the frontend container reverse-proxies `/ws/voice` + `/api/*` to the orchestrator ACA app over HTTPS. Both location blocks were missing the two ingredients ACA's front door requires for HTTPS upstreams:

1. **TLS SNI** — without `proxy_ssl_server_name on;` + `proxy_ssl_name`, nginx opens TLS to the upstream IP with no SNI; ACA resets the handshake.
2. **Upstream `Host` header** — was being kept as the inbound `frontend.blackriver-...` host; needs to be the orchestrator's hostname for ACA to route.

Frontend container logs (2026-05-16):

```
[error] peer closed connection in SSL handshake (104: Connection reset by peer)
while SSL handshaking to upstream, ...
upstream: "https://100.100.244.199:443/ws/voice",
host: "frontend.blackriver-0ab9be19...."
```

The mic button click handler itself fires correctly (Playwright confirms a `wss://frontend.../ws/voice` WebSocket attempt; nginx then 502s the upgrade). The frontend JS / React code is fine — `useVoiceSession` deliberately builds a same-origin `wss://` URL so the nginx hop is in the data path. Bug was purely server-side config.

Direct WSS to `wss://orchestrator.blackriver-.../ws/voice` works (verified with `websockets.connect`) — orchestrator + its ingress are healthy.

### Fix

- `apps/frontend/docker-entrypoint.sh`: derive `ORCHESTRATOR_HOST` from `ORCHESTRATOR_URL`.
- `apps/frontend/nginx.conf`: add `proxy_ssl_server_name on;`, `proxy_ssl_name $ORCHESTRATOR_HOST;`, `proxy_set_header Host $ORCHESTRATOR_HOST;` on both `/api/` and `/ws/`. Preserve existing WS upgrade headers.
- `apps/frontend/playwright.config.ts` + `e2e/mic-button.spec.ts`: diagnostic spec captures WS events + console errors against the live URL. Reusable for any future "mic dead" UAT smoke.

### Verification

- Local: `npm run lint` ✅, `npm run typecheck` ✅, `npm run build` ✅ (no bundle change — config only).
- Live (pre-fix Playwright run, `.squad/files/playwright-mic-button-2026-05-16.log`): WS handshake → 502.
- Live (post-deploy): re-run Playwright; expect WS to upgrade + `start` frame to be sent.

### Ship plan

- Branch `squad/fix-frontend-mic-button` stacked on `squad/fix-log-analyst-detect-pattern-400` (top of PR #7-#16 stack).
- PR #17 against that base.
- `azd deploy frontend --no-prompt` after PR push.
- Re-run `e2e/mic-button.spec.ts` for post-deploy verification.

### Files

- `apps/frontend/nginx.conf`
- `apps/frontend/docker-entrypoint.sh`
- `apps/frontend/playwright.config.ts` (new)
- `apps/frontend/e2e/mic-button.spec.ts` (new)
- `apps/frontend/.gitignore` (new — excludes test-results/, playwright-report/, build artifacts)
- `apps/frontend/package.json` + lockfile (`@playwright/test` devDep + `test:e2e` script)
