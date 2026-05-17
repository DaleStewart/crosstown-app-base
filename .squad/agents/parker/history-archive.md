# Peter Parker — Archive (Phase 0)

## Summary (2026-05-13 through 2026-05-16)

**Phase 0 (2026-05-13 through 2026-05-15):**

- **Frontend v1 (2026-05-13):** Vanilla HTML/CSS/JS judging UI (index, judge, admin). Key decision: did not overwrite `criteria.js` (Stark's spine). Layered `criteria-ui.js` keyed by track + criterion id. Design reused reference scorecard tokens (Barlow + Barlow Condensed, Tabler icons, light/dark). Judge page: team picker with checkmarks, scorecard with all-criteria gate, tier feedback. Admin: lock toggle + leaderboard. No build step, no npm, CDN fonts.

- **Frontend v2 MTA rebrand (2026-05-13):** Dropped Google Fonts (Helvetica stack). Color palette: MTA Blue #0039A6, red #EE352E, green #00933C, amber #FF6319, yellow #FCCC0A. Right-angle discipline (radius 0 except bullets/pills/knob). Route bullet primitives (sm/md/lg/xl/xxl). Hackathon roundel (navy AI). Tier ladder: ≥90 green, ≥70 blue, ≥50 orange, <50 red. Staggered reveal animation. Per-criterion bar charts. Lock activation: 45° yellow/black caution stripe. Final bundle: 1524 modules, 177.28 kB JS / 11.87 kB CSS.

- **Post-merge vite.config.ts fix (2026-05-15):** PR #3 — one-line change: `import { defineConfig } from "vitest/config"` (not "vite"). Reason: vitest/config exports widened defineConfig type that knows about `test` block. Final gates: lint ✅, typecheck ✅, test 6/6 ✅, build ✅.

- **P0 mic button fix (2026-05-16):** PR #17 — nginx missing SNI + Host headers on HTTPS proxy to ACA. Added `proxy_set_header Host $ORCHESTRATOR_HOST`, `proxy_ssl_server_name on`, `proxy_ssl_name $ORCHESTRATOR_HOST` to /api/ and /ws/ blocks. Orchestrator was innocent. ACA front door routes by SNI/Host. Deployed via ACR fallback (Docker Desktop not running). Playwright verify: WS opens, start frame sent, PCM frames flow, 0 errors.

- **Bug fixes summary:** Issue 1 — spacebar PTT regression: added guard `if (target.tagName === "INPUT" || "TEXTAREA") return;` to keydown/keyup. Issue 2 — audio not recording: `ctx.resume()` after AudioContext, `send({type:"stop"})` on release. Issue 3 — /api/health 404: nginx rewrite (separate task T106).

**Phase 1 (2026-05-16):** T106 nginx /api/health rewrite shipped on chore/deploy-hygiene branch.

Archive entry date: 2026-05-16
