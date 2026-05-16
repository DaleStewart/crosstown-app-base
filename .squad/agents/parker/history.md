## 2026-05-15 — Post-merge frontend gates (Parker)

Ran all four CI gates on `apps/frontend` post-realtime-swap merge (D-009 + D-011):

**Outcomes:**
- **lint:** ✅ PASS (0 eslint errors)
- **typecheck:** ✅ PASS (0 tsc errors with `--noEmit`)
- **test:** ✅ PASS (6 tests passed in 3.92s; 1 warning about React act() in App.test.tsx is pre-existing)
- **build:** ❌ FAIL — vite.config.ts line 15: TypeScript error `No overload matches this call. Object literal may only specify known properties, and 'test' does not exist in type 'UserConfigExport'.`

**Analysis:** The build failure is a **pre-existing vite.config.ts configuration error**, not caused by the realtime swap (which only touched `apps/orchestrator/`). The `test` property in `defineConfig()` requires importing from `vitest/config` rather than plain `vite`. This is a known issue in the vite+vitest setup and predates the session.

**Realtime swap scope:** D-009 modified only `apps/orchestrator/` (voice/foundry_realtime.py, settings.py, infra/) + docs. No frontend code touched.

**Verdict:** Frontend lint/typecheck/test gates are all green. Build gate is red, but pre-existing (not a regression).

**Team update (18:11Z):** Re-verify pass complete; PR #3 shipped from Parker for vite.config.ts (shipped, all gates now green).

## Learnings

2026-05-15 — Post-merge frontend gates. lint (pass), typecheck (pass), test (6 passed in 3.92s), build (fail: pre-existing vite.config.ts TypeScript error). No bundle size (build never completed). Frontend scope unaffected by realtime swap.

## 2026-05-13 — Frontend v1 (Parker)

Built the vanilla HTML/CSS/JS judging frontend at `apps/judging/src/` (index, judge, admin) plus `styles.css`, `auth.js`, `toast.js`, `criteria-ui.js`.

Notable decisions:

- **Did not overwrite `apps/judging/shared/criteria.js`.** Stark had already landed a spine with different criterion ids for the Azure track (`alignment / architecture / reliability / ux / demo`) instead of the reference scorecard's (`problem / agent / tech / innovation / demo`). Backend owns that spine, so I layered UI metadata (icon, desc, 1-5 anchors) in a sibling `criteria-ui.js` keyed by `track + criterion id`. `MTAHackCriteriaUI.augment(track)` merges the two for the scorecard renderer.
- Reused the reference scorecard's exact design tokens (navy `#1A3A6B` etc., Barlow + Barlow Condensed, Tabler icons, light/dark via `prefers-color-scheme`). New components (team cards, tabs, leaderboard table, switch) were added in the same idiom.
- `MTAAuth.getUser()` caches a single `/.auth/me` promise; `mountTopbar()` renders the user chip + sign-out everywhere.
- `judge.html` accepts `?track=&team=`; picker shows a green check pill + total for already-scored teams. Submit is gated on all 5 criteria; handles 423 (locked) by disabling the form and showing a banner.
- `admin.html` does an optional `GET /api/lock?track=…` to seed the toggle state. Stark — if you don't expose that, the toggle will just default to "Open" until the user flips it; `POST /api/lock` is the source of truth.
- No build step, no npm, three self-contained HTML pages + shared CSS/JS. Tabler icons + Google Fonts loaded from CDN.

Open follow-ups:

- Per-criterion bar chart on the leaderboard (nice-to-have) was intentionally skipped.
- If Stark's `/api/myscores` returns `criteria` as an array rather than an `{id: 1-5}` map, the scorecard pre-fill will be empty — wire a small adapter when the shape lands.

## 2026-05-13 — Frontend v2 design upgrade (Parker)

Folded in Sean's editorial / transit-system brief. Did not rewrite — surgical upgrades on top of v1.

Changes:

- Added Barlow Semi Condensed to the Google Fonts request (used for eyebrows, table labels, small caps metadata, kickers). Italic 700 Barlow Condensed added for ranks + track numerals.
- Body now has a fixed `::before` atmosphere: faint 135° diagonal subway-rule pattern (~4-6% navy) + soft top radial in navy-light. `color-mix()` keeps it themed automatically.
- Dark mode bg pushed to near-black `#0A1428` with `--bg-2` `#07101F` so the navy palette pops forward.
- Card shadow recipe replaced with `0 1px 0 rgba(26,58,107,0.08), 0 12px 32px -16px rgba(26,58,107,0.25)` plus an `--inset-top` highlight on cards / sections / .track-card.
- Staggered reveal animation via `.reveal` parent: 80ms increments on direct children, `cubic-bezier(0.2,0.7,0.2,1)`, respects `prefers-reduced-motion`.
- **index.html** — asymmetric 1.15fr / 0.85fr grid with two `.track-card`s. Each has a giant italic Barlow Condensed `01` / `02` numeral clipped at the bottom-right corner (color `--navy-light`, animates on hover). Secondary card is offset `margin-top: 32px`. Admin pathway is now a narrow `.admin-strip` with a key icon — not a third equal card.
- **judge.html team picker** — new `.picker-mast` with a 48px Barlow Condensed count (e.g. `08` + "Teams in this track" small caps caption). Team cards: 4px left rail (`--navy-mid` on hover, `--navy` when scored), top-eyebrow with `Team · 01` + status, big uppercase Barlow Condensed team name, uppercase letter-spaced metadata, and a top-right `.total-pill` showing the judge's submitted total instead of a generic checkmark.
- **judge.html scorecard** — total score animates with a count-up (cubic ease, ~380ms). When the tier class changes, the total briefly scales (`.flash`). Score buttons get a `scale(0.96)` press + a soft same-color glow when active. Criterion card's left border rail fills via a small keyframe when scored.
- **admin.html** — wire-service leaderboard: `Rank` in 32px italic Barlow Condensed (top-3 in navy gradient), `Team` in 20px Barlow Condensed uppercase, `Avg total` huge 28px navy tabular-num. Tabs got `01` / `02` italic numerals. Hover over a row reveals a `.lb-mini` per-criterion bar chart strip beneath. Lock toggle triggers a full-screen `.lock-flash` (96px navy/amber icon, 600ms fade) and applies `.locked` on the table wrap — a 45° amber stripe overlay across the leaderboard signals "consequence".

Followed the bans: no purple gradients, no glassmorphism, no Inter, no centered-hero-with-three-columns, no welcome-wave greeting. Tabler icons stay mono in navy/amber. Tier colors stay as pills, never as flooded backgrounds.

What I'd add next pass if there were time: a CSS-only `ti-train` glyph drifting horizontally across the masthead rule line as a transit easter-egg; per-row sparkline of judge-by-judge totals on the admin leaderboard.

## 2026-05-13 — MTA brand rebrand (Parker)

Folded Sean's MTA brand brief into the design layer. No restart.

What changed:

- **Typography:** dropped Google Fonts entirely. Body / display all on the Helvetica family stack `'Helvetica Neue', Helvetica, Arial, sans-serif`. Did a sed replace across the whole stylesheet so no Barlow references remain.
- **Color tokens repointed to MTA NYCT line palette:**
  - `--navy` is now MTA Blue `#0039A6` (A C E). `--navy-mid` `#1A4EBF` for hover, `--navy-light` `#E5EDFB` for soft tints.
  - `--red` `#EE352E` (1 2 3), `--green` `#00933C` (4 5 6), `--amber` `#FF6319` (B D F M, used for "developing" tier).
  - Added `--mta-yellow` `#FCCC0A` (N Q R W) for accents / caution.
  - `--text` `#2D2D2D` MTA dark slate, `--text-3` `#A7A9AC` MTA light slate. Background white.
  - Dark mode bg `#0A0A0A`; MTA Blue brightens to `#4D7EE8` so it still pops.
- **Tier ladder** is now bullet-style: ≥90 green, ≥70 blue, ≥50 orange, &lt;50 red. Updated both `tierClass()` functions and added `.pill.blue` / `.pill.orange` rules.
- **Right-angle discipline:** `--radius-lg: 0`, `--radius: 2px`. `border-radius: 0 !important` on every card / panel / button / input via a single brand-layer rule. Bullets, pills, and the switch knob stay round.
- **Route bullet primitive:** new `.bullet` component (sm / md / lg / xl / xxl). Renders a solid circle in Helvetica Bold (`A`, `C`, `01`, `78`, …) — the building block for everything brand-relevant.
- **Hackathon roundel:** small navy circle with white `AI` next to a `MTA AI / Hackathon · 2026` wordmark. Top-left of every page (replaces the previous `ti-train` crumb).
- **index.html:** flat MTA-blue `.signage` panel bleeds past the body padding with massive white Helvetica Bold heading, yellow station rule beneath. Track cards lost the clipped italic numerals — now they each carry a giant `.bullet.xxl` (`A` MTA-blue for Azure, `C` MTA-red for Copilot). On hover the panel inverts to the track color; the bullet inverts to white.
- **judge.html topbar:** roundel + a small `A` / `C` track bullet acting as the breadcrumb. Team picker cards are now a 2-col grid (`56px bullet` + content). Cards for unscored teams show the team number in the track color; scored cards show the rounded total inside a tier-colored bullet — looks like a station callout.
- **judge.html scorecard:** criterion cards lose the `ti-` icon and gain a 32px MTA-blue numbered `.bullet` (`01..05`). Total renders 80px Helvetica Bold (kept the count-up animation + tier-change flash). Below it a new `.tier-block` reads `● STRONG` style, with the dot in tier color.
- **admin.html:** tabs ditched the italic `01`/`02` for actual `A`/`C` route bullets. Leaderboard rank cell renders the rank in a tier-colored `.bullet.md`; tier column became `● STRONG` style. `th` cells are now solid black with white Helvetica Bold (signage band). Lock activation:
  - Full-screen `.lock-flash` overlay is now a 45° MTA yellow / black caution stripe — out-of-service vibe.
  - Table wrap gets `.locked` (red border + animated caution-stripe sweep).
  - A persistent red `.locked-banner` with a yellow left accent rail mounts above the table, reading `Judging Locked — &lt;track&gt; track`.

What did not change:
- The criterion-card / 1-5 button / anchor-list / textarea structure still mirrors the reference scorecards. Same DOM, same per-criterion bar chart. The fonts/colors swap, but the scoring artifact is intact.
- `criteria.js` (Stark's spine) and `criteria-ui.js` (anchors + icons) are unchanged. The card icons are now visually hidden via `.card-icon { display: none; }` since the numbered bullet replaces them.
- Page-load staggered `.reveal`, `prefers-reduced-motion` guard, light/dark.

Notes / follow-ups:
- The signage panel bleeds with `margin: -2rem -1rem 0;` to overrun the body's 2rem/1rem padding. If the team ever wraps the page in a different container or changes body padding, that bleed will read as a misalignment.
- Helvetica is system-available on macOS/iOS. Windows/Linux fall back to Arial (intentional — Arial is on-brand for MTA). If we ever want pixel-perfect parity on Linux, we'd need to license Helvetica Neue webfonts.
- I did NOT use the actual MTA "M" logo — only a hackathon-specific `AI` roundel — to sidestep trademark risk.

## 2026-05-13 — Security Review (Strange)

Strange completed a security review of the judging app and authored `apps/judging/SECURITY_REVIEW.md`. Verdict: 🟡 Ship after must-fix items. 2 critical findings (CSV formula injection in export, unfilled tenant GUID placeholder) and 4 high findings. Core auth/authz model is solid. See decision D-007 and the full report for details and remediation paths.


## 2026-05-15 — Re-verification + vite.config.ts fix shipped (Parker)

Re-ran all four CI gates on `apps/frontend` after D-014's note that the build failure was pre-existing.

**Gate results (before fix):**
- `npm run lint`      → exit 0 ✅
- `npm run typecheck` → exit 0 ✅
- `npx vitest run`    → exit 0 ✅ (3 files, 6 tests passed in 2.95s; same pre-existing React act() warning on Header)
- `npm run build`     → exit 2 ❌ `vite.config.ts(15,3): error TS2769: No overload matches this call. Object literal may only specify known properties, and 'test' does not exist in type 'UserConfigExport'.`

**Fix shipped:** one-line change in `apps/frontend/vite.config.ts`:

``diff
-import { defineConfig } from "vite";
+import { defineConfig } from "vitest/config";
``

`vitest/config` re-exports a widened `defineConfig` whose type knows about the `test` block; `vite`'s does not. After the fix, `npm run build` → exit 0 (tsc -b clean, vite build → 1524 modules, 177.28 kB JS / 11.87 kB CSS, 2.40s).

**Branch / PR:** committed on `squad/fix-vite-config-defineConfig` (off origin/main), opened PR #3 in DevPost-Test-Hackathon/crosstown-app.

**Final status — all four gates green:** lint ✅, typecheck ✅, test ✅ (6/6), build ✅.

## 2026-05-16 — Mic button P0 fixed (Bug #13) (Parker)

Sean reported UAT mic button dead. Diagnosed end-to-end and shipped PR #17.

**🤖 Autopilot disclosure:** acted in autopilot for this task per the system prompt directive. No human gates between diagnosis and shipping.

**Symptom:** Live UAT frontend rendered fine; clicking the mic button did nothing.

**Diagnostic path:**
1. Installed `@playwright/test` + chromium in `apps/frontend`, wrote `e2e/mic-button.spec.ts` to capture WS events, console errors, network failures against the live URL with `--use-fake-ui-for-media-stream` so `getUserMedia` doesn't gate the click.
2. Pre-fix run (`.squad/files/playwright-mic-button-2026-05-16.log`): click handler fires, browser opens `wss://frontend.../ws/voice`, gets **HTTP 502** on the WS upgrade.
3. Verified orchestrator is healthy: direct `websockets.connect` to `wss://orchestrator.blackriver-.../ws/voice` succeeds (`.squad/files/probe_ws.py`).
4. Frontend container nginx error logs (`az containerapp logs show --name frontend`): `peer closed connection in SSL handshake (104: Connection reset by peer) while SSL handshaking to upstream, upstream: "https://100.100.244.199:443/ws/voice", host: "frontend.blackriver-..."`.

**Root cause:** nginx's `proxy_pass https://...` to ACA was missing **SNI** (`proxy_ssl_server_name on;` + `proxy_ssl_name`) and was forwarding the wrong **Host header** (inbound `frontend.blackriver-...` instead of the orchestrator's hostname). ACA front door routes by SNI/Host and resets handshakes that lack them.

**Fix shipped (`squad/fix-frontend-mic-button` → PR #17, stacked on `squad/fix-log-analyst-detect-pattern-400`):**
- `apps/frontend/docker-entrypoint.sh` — derive `ORCHESTRATOR_HOST` from `ORCHESTRATOR_URL` (sed-strip scheme/path/port); export both for envsubst.
- `apps/frontend/nginx.conf` — on both `/api/` and `/ws/`: add `proxy_set_header Host $ORCHESTRATOR_HOST;`, `proxy_ssl_server_name on;`, `proxy_ssl_name $ORCHESTRATOR_HOST;`. Existing WS `Upgrade`/`Connection` headers preserved.
- Did **not** touch any React/TS code. `useVoiceSession`'s same-origin `wss://` URL construction is correct by design — the nginx hop is the intended data path. Frontend was innocent.

**Build/lint/test (local):** lint ✅, typecheck ✅, build ✅ (1524 modules / 177.28 kB JS — bundle unchanged, config-only fix).

**Deploy:** `azd deploy frontend` aborted with "Docker service not running" on the operator box. Fell back to Okoye's ACR-push fallback per Day-5 ops pattern:
- `az acr build --registry crcrosstowndryrunmay15yycemmso7sk7q --image mta-ai-hackathon/frontend-crosstown-dryrun-may15:mic-fix-20260516094226 -f Dockerfile .` (build ran in ACR; CLI log streaming threw a Windows `cp1252` encoding error on the build's check-mark glyph but the build itself completed — image confirmed via `az acr repository show-tags`).
- `az containerapp update --name frontend --image ...mic-fix-20260516094226` rolled revision `frontend--0000002` to 100% traffic, `healthState: Healthy`.

**Post-deploy verification (Playwright re-run, `.squad/files/playwright-mic-button-postfix-2026-05-16.log`):**
- `[opened] wss://frontend.../ws/voice` — no more 502
- `[sent] {"type":"start","conversationId":null,"mode":"push_to_talk"}` — start frame went out
- 14 follow-on binary PCM frames sent (fake media stream audio)
- **0 WS errors, 0 closes, 0 network failures** in the 7 s observation window
- Lingering cosmetic `404` on `/api/health` (orchestrator only serves `/health`, not `/api/health`) — pre-existing, unrelated.

**Verdict:** Sean can UAT the push-to-talk button — it now opens a real WebSocket session to the orchestrator. Full voice loop (audio response back from Foundry Realtime) still depends on Bug #8 (orchestrator-side WS handshake 404), which remains with Brady; that's independent of this fix.

**Followups:**
- The `/api/health` 404 on every page load — frontend should either probe `/api/health` (and orchestrator add a route) or use `/health` directly. Cosmetic but visible in console. Not in scope for this P0.
- Playwright `test:e2e` script added but **not** wired into default CI — it points at the live UAT URL by design (diagnostic). If we want it in CI it should target a hermetic dev server.

## Learnings

2026-05-16 — nginx → ACA HTTPS upstream **always** needs `proxy_ssl_server_name on;` + `proxy_ssl_name $host;` + `proxy_set_header Host $host;`. The default behavior (no SNI, inbound Host forwarded) silently produces 502s with the diagnostic `peer closed connection in SSL handshake` line in error logs. Worth baking into any future ACA-fronted nginx template.

