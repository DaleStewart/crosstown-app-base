# Implementation Plan: Crosstown Transit AI — Tuesday Customer Demo

**Branch**: `002-tuesday-demo` (spec authored on `anvil/47doors-comparison`) | **Date**: 2026-05-16 | **Demo**: 2026-05-19 (T-62h) | **Spec**: [spec.md](spec.md)

**Input**: Spec at `specs/002-tuesday-demo/spec.md` (8 stories, FR-001..FR-018, SC-001..SC-010). Quality evidence: [checklists/requirements.md](checklists/requirements.md). Adoptable patterns: [docs/47doors-comparison.md](../../docs/47doors-comparison.md) §8.1–8.3.

## Summary

Ship a demo-stable build of the existing voice + text + specialist stack by (a) landing deploy hygiene first (FR-009/010/011/014), (b) draining 11 open PRs **plus the in-flight `feat/route-map` PR from Session B** in a fixed dependency order with a smoke-test gate between each (FR-015), (c) pinning deploys to `main` only with one-pusher-at-a-time coordination (FR-013, US6), (d) rehearsing the 6-prompt script 3× on demo morning (SC-002). The risk is regressions during the merge train, not missing features.

> **Scope update (T-60h)**: RouteMap (originally spec P3-droppable / v2) is **promoted to in-scope** because Session B has already started shipping it on `feat/route-map`. Their plan: `C:\Users\segayle\.copilot\session-state\5f5c4e40-73e3-4aa8-b591-d2091461cc17\plan.md` (read in full before editing `App.tsx`). See §3 (merge order), §4.1 (cross-session coordination), §7 R10/R11.

## Technical Context

**Stack unchanged**: Python 3.11 FastAPI (orchestrator, log_analyst, service_advisor), Vite/React/Tailwind (frontend), Bicep, ACA in `swedencentral`, Foundry `gpt-realtime-1.5`.
**New artifacts only**: `scripts/smoke-test.{sh,ps1}`, `azure.yaml` `postdeploy` hook, 4× Dockerfile `HEALTHCHECK`, nginx `/api/health` proxy rule, `service-advisor` block in `azure.yaml::services` (delivered by PR #27).
**Constraints**: 62h hard cap. No calibration tweaks (FR-018). Mock data only (FR-007 / Const. II). Keyless auth unchanged (Const. IV).

## Constitution Check

| Principle | Status |
|---|---|
| I. Citations load-bearing | ✅ FR-006 ⊆ Const I; no tool-layer code changes here |
| II. Mock data only | ✅ FR-007 / SC-010 explicit |
| III. Hermetic by default | ✅ Smoke test runs against live URL, eval gates stay cassette-based (FR-018) |
| IV. Keyless auth | ✅ No env-var/secret changes |
| V. One voice abstraction | ✅ Foundry Realtime only on stage; Speech path untouched |
| VI. Extensions are exercises | ✅ No extension code touched |

No violations. Complexity tracking N/A.

---

## 1. Architecture overview (only what changes)

```
                 ┌───────── azd deploy (main only, FR-013) ─────────┐
                 │                                                  │
GitHub Actions ──┤ build & push 4 images ──> ACA revisions ──> postdeploy hook
   (deploy.yml)  │                                                  │
                 └──────────────────────> scripts/smoke-test ──> /api/health (frontend)
                                                  │                  │
                                                  │                  ├─ orchestrator /healthz (via nginx /api/health proxy)
                                                  │                  ├─ log-analyst /healthz (internal)
                                                  │                  └─ service-advisor /healthz (internal, NEW in azure.yaml)
                                                  │
                                                  └── exit ≠0 ─> deploy FAILED (visible in 60s, SC-004)

Each container image: Dockerfile HEALTHCHECK --interval=30s curl localhost/healthz
                      → ACA stops routing on unhealthy revision.
```

Only the **deploy pipeline** changes structurally. Runtime architecture is whatever lands from the PR train (US1/US2). Service-advisor exists in ACA today but is invisible to `azd deploy` until PR #27 adds it to `azure.yaml::services` (FR-012).

## 2. Deploy pipeline design (load-bearing)

Owner: **Okoye**. Verification: **Anvil (Large — 3 reviewers)**. Sized: M.

### 2.1 `scripts/smoke-test.sh` (and `.ps1` mirror) — FR-009

```
Usage: scripts/smoke-test.sh <frontend-url>          # exits ≠0 on first failure, <30s total
Checks (in order, each prints PASS/FAIL with timing):
  1. GET <url>/                 → 200, body contains '<div id="root"' (no Hello World)
  2. GET <url>/api/health       → 200, JSON body parses, "status" in {"ok","degraded"}
  3. GET <url>/api/health       → JSON.services lists orchestrator + log-analyst + service-advisor
  4. POST <url>/api/turn '{"text":"ping"}' → 200, JSON has `citations` key (proves /api/turn wired)
  5. (optional, --full) re-run 4 with each of the 6 rehearsed prompts → assert tool fired & citations≥1
Outputs: one-line summary "smoke OK in 7.4s" or "smoke FAIL at check 2: expected 200 got 404"
Negative test: point at https://k8sequickstart…default.azurecontainerapps.io → must FAIL at check 1
```

### 2.2 `azure.yaml` `postdeploy` hook — FR-010

```yaml
hooks:
  postdeploy:
    posix: { shell: sh,   run: scripts/smoke-test.sh  $env:SERVICE_FRONTEND_URI }
    windows:{ shell: pwsh, run: scripts/smoke-test.ps1 $env:SERVICE_FRONTEND_URI }
    # NO continueOnError — failure must fail the deploy.
```

Resolves `SERVICE_FRONTEND_URI` from azd env (already set by ACA module outputs). If absent, exit ≠0.

### 2.3 Dockerfile `HEALTHCHECK` — FR-011

Add to each of:
- `apps/orchestrator/Dockerfile` → `HEALTHCHECK --interval=30s --timeout=5s --start-period=20s CMD curl -fsS http://localhost:8000/healthz || exit 1`
- `apps/log_analyst/Dockerfile` → same on `:8001/healthz`
- `apps/service_advisor/Dockerfile` → same on `:8002/healthz`
- `apps/frontend/Dockerfile` (nginx stage) → `HEALTHCHECK ... CMD curl -fsS http://localhost:80/api/health || exit 1`

Each service must already expose `/healthz` (verify; if missing, add a 6-line FastAPI route returning `{"status":"ok","service":<name>}`). Frontend `/api/health` is the proxied passthrough — see §2.4.

### 2.4 nginx `/api/health` rewrite — FR-014 (per PR #25 fix)

`apps/frontend/nginx.conf` must contain an **explicit** location for `/api/health` ahead of the catch-all `/api/` proxy, rewriting to `/healthz` on the orchestrator upstream:

```nginx
location = /api/health {
  proxy_pass http://orchestrator/healthz;   # rewrites path, not just prefix-strips
  proxy_read_timeout 5s;
}
location /api/ {
  proxy_pass http://orchestrator;            # existing
}
```

`/api/health` response shape (orchestrator-side):
```json
{ "status": "ok|degraded", "service": "orchestrator", "deps": {"cosmos":"ok","search":"ok","service_advisor":"ok|unreachable"} }
```
Degraded = 200 + non-empty unreachable list (per spec edge case). Smoke check 2 accepts both `ok` and `degraded`; check 3 asserts service-advisor present in `deps`.

---

## 3. PR merge schedule (the train)

Branch protection note: every merge below is `Squash & merge` on `main`, smoke-test against the live frontend URL, **before** the next merge starts (FR-015 / US5).

| Order | PR | Chain | Owner of conflict resolution | Sized | Smoke after = |
|---|---|---|---|---|---|
| **0** | **NEW: `chore/deploy-hygiene`** (#29 hypothetical) | infra | Okoye | M | baseline; must pass against current main |
| 1 | #28 (47doors comparison doc) | docs | Scribe | S | unchanged |
| 2 | #19 fix(frontend): stop frame on mic release | frontend | Parker | S | frontend boots, /api/health 200 |
| 3 | #20 fix(orchestrator): server VAD + audio commit | orch | Wanda | M | voice turn completes locally |
| 4 | #21 feat(frontend): render user-turn transcripts | frontend | Parker (rebase on #19) | S | UI shows user turns |
| 5 | #22 fix(orchestrator): emit user-turn transcripts | orch | Wanda (rebase on #20) | M | end-to-end user transcript |
| 6 | #23 feat(frontend): text input | frontend | Parker (rebase on #21) | M | /api/turn works from UI |
| 7 | #24 fix(orchestrator): safe transcription default + GA nested | orch | Wanda (rebase on #22) | M | no WS close storm |
| 8 | #25 fix(frontend): spacebar PTT + audio capture + nginx /api/health | frontend | Parker (rebase on #23) | M | spacebar works, /api/health 200 via proxy |
| 9 | #26 fix(frontend): restore spacebar + /api/health (Anvil's variant) | frontend | Parker — **resolve overlap with #25**, prefer #25's nginx rule, keep #26's audio fix delta | M | re-run §2.1 full |
| 10 | **#27 feat: Service Disruption Advisor** | infra+orch | Okoye (rebase on #24, updates `azure.yaml::services`) | **L** | smoke `--full` (all 6 prompts), DisruptionBanner + AlternateRouteCard render |
| **11** | **`feat/route-map` (Session B, draft → ready)** | frontend | Parker (Session B) — **rebase on #27** | M | smoke `--full` + manual: RouteMap renders all 10 stations, L1 turns red when prompt 4 fires, dashed shuttle overlay appears when prompt 6 fires |

Rationale per merge:
- **Step 0 first** so every subsequent smoke run uses the real gate; otherwise the train is racing without brakes (R5 mitigation).
- **#28 second** because it's docs-only and burns down the open count cheaply.
- **Frontend and orchestrator chains interleave** in numerical order — they touch different files, but #21 needs #20's WS shape, #22 needs #20 alive, #25 needs #23's text input present in DOM, etc. Numerical order ≈ topological order here.
- **#26 conflicts with #25** intentionally (both touch nginx + spacebar). Conflict owner = #26 (later in sequence, per FR-016 rule 5). Resolution rule: keep #25's nginx `/api/health` block verbatim (it's the contract surface in §2.4); take audio-capture delta from #26 only where it doesn't undo #25.
- **#27 last** so `azure.yaml::services` reflects the full mesh in one deploy; verifies FR-012.
- **`feat/route-map` after #27** because RouteMap reads `apps/service_advisor/data/route_graph.json`; if #27 reshapes that file, RouteMap breaks. Also after #23 because both edit `App.tsx` — see §4.1 hot-zone rule. PR stays **draft** until #27 lands, then Session B rebases on main, flips to ready, and Anvil Large-reviews before merge.

Stop conditions between merges:
- Smoke FAIL → halt train, fix on the failing PR's branch, re-merge. Do **not** stack the next PR on a broken main.
- Conflict ambiguity → escalate to Anvil (Large gate, §9) before resolving.

---

## 4. Branch & worktree strategy

- **Main-only deploys** (FR-013). `deploy.yml` adds first step: `if: github.ref == 'refs/heads/main'` — else fail with `"refusing to deploy from $GITHUB_REF; only main may deploy"`. Workflow_dispatch override requires `confirm_non_main: true` input and prints a loud `::warning::`.
- **Rebase before merge** (US6 rule 3). Every PR in §3 is rebased on `main` immediately before merge — not just at open. `gh pr checkout N && git rebase main && git push --force-with-lease` then merge.
- **One pusher at a time** (US6 rule 2). Pushing session appends to `.squad/decisions.md`:
  ```
  ## 2026-05-17 14:32 — claim main push slot
  Session: copilot-A (this one)
  PRs in flight: #19, #20
  ETA release: 30 min
  Smoke status: pending
  ```
  Other session **must not** push to main while a claim is open. Releases by appending `released 15:01, smoke OK`.
- **Two-session split (recommended)**:
  - **Session A (this one)**: deploy hygiene (step 0), orchestrator chain (#20, #22, #24), #27, demo rehearsals. Owns: `infra/`, `apps/orchestrator/`, `apps/log_analyst/`, `apps/service_advisor/`, `azure.yaml`, `scripts/`, `deploy.yml`.
  - **Session B (parallel, RouteMap)**: frontend chain (#19, #21, #23, #25, #26), docs (#28), AND `feat/route-map`. Owns: `apps/frontend/`. Their plan is at `C:\Users\segayle\.copilot\session-state\5f5c4e40-73e3-4aa8-b591-d2091461cc17\plan.md`.
  - Sessions trade the push-slot at chain boundaries; both must rebase between trades.
- **Worktrees**: one worktree per chain to avoid uncommitted-WIP collisions (`git worktree add ../mta-ai-frontend squad/frontend-train`). Optional, recommended given Sean's exhaustion.

### 4.1 Cross-session coordination (the App.tsx hot zone)

Two Copilot sessions are live. Session B (RouteMap) and the frontend PR chain (#21, #23) all edit `apps/frontend/src/App.tsx`. This is the single highest collision risk in the train.

**File-overlap map**:

| File | #21 | #23 | #25/#26 | `feat/route-map` | Conflict severity |
|---|---|---|---|---|---|
| `apps/frontend/src/App.tsx` | edits | edits | maybe | edits (1 import + 1 JSX line above `<DisruptionBanner>`) | **🔴 HOT** |
| `apps/frontend/src/components/RouteMap.tsx` | — | — | — | NEW | none |
| `apps/frontend/src/components/RouteMap.test.tsx` | — | — | — | NEW | none |
| `apps/frontend/vite.config.ts`, `tsconfig.json` | — | — | — | maybe (`@data` alias) | low |
| `apps/frontend/tailwind.config.js` | — | — | — | maybe (line color tokens) | low |
| `apps/service_advisor/data/route_graph.json` | — | — | — | reads | conflicts with #27 if schema moves — see R10 |
| `apps/frontend/nginx.conf` | — | — | #25 (canonical), #26 (conflicts) | — | covered §3 step 9 rule |

**Branch protection per Session B's stated rules**:
- Session B will **NOT** touch `anvil/*` or `squad/*` branches. Session A reciprocates: **does not** touch `feat/route-map`.
- Session B opens its PR as **draft** with a hold note (`"Hold merge until #27 lands"`); cannot flip to ready until step 10 of §3 smoke-passes.
- Session B documents every autonomous decision (their D1/D2/D3 + any new ones) in PR body — Sean is AFK, this is the audit trail.

**Push-slot handoff dance**:
1. Session A lands hygiene (step 0) → releases slot.
2. Session B lands frontend chain #19–#26 in order → releases slot.
3. Session A lands orchestrator chain #20→#22→#24, then #27 → releases slot.
4. Session B rebases `feat/route-map` on main (now has #23 + #27), runs `npm run lint && typecheck && build && vitest run`, re-runs §2.1 `--full` smoke, then flips PR to ready.
5. Anvil Large-reviews `feat/route-map`, Session A or B merges, smoke `--full` again.

**Handoff log entry template** (`.squad/decisions.md`):
```
## 2026-05-17 HH:MM — handoff
From: session-{A|B}
To: session-{A|B}
Just landed: <PR# or branch>, smoke <OK|FAIL>
In flight: <branch/PR>
Next session picks up: <PR# or task>
App.tsx last touched by: <PR#>  ← critical for rebase order
```

**Hard rule on App.tsx**: any session about to touch `App.tsx` must check the most recent handoff entry for `App.tsx last touched by` and rebase on that PR first. No exceptions.

---

## 5. Smoke test & monitoring matrix

| Service | `/healthz` returns | Dockerfile HEALTHCHECK probes | postdeploy verifies | Escalate to human if |
|---|---|---|---|---|
| frontend (nginx) | n/a — serves SPA + proxies `/api/health` → orchestrator/healthz | `curl localhost:80/api/health` every 30s | check 1 (root has `<div id="root"`) + check 2 (200 + JSON) | check 1 or 2 fails |
| orchestrator | `{status, service:"orchestrator", deps:{cosmos,search,service_advisor}}` | `curl localhost:8000/healthz` | check 3 confirms all 3 deps listed; check 4 POSTs `/api/turn` | `status:"degraded"` 2 runs in a row, OR `service_advisor:"unreachable"` |
| log-analyst | `{status, service:"log_analyst"}` | `curl localhost:8001/healthz` every 30s | indirect: orchestrator deps check + `--full` smoke prompts 1–3 | prompts 1–3 fail to cite |
| service-advisor | `{status, service:"service_advisor"}` | `curl localhost:8002/healthz` every 30s | indirect: orchestrator deps check + `--full` smoke prompts 4–6 | prompts 4–6 fail to render banner/card |

Cadence: full smoke (`--full`, all 6 prompts) at end of merge train + 3× on demo morning (SC-002). Quick smoke (checks 1–4 only) between each merge in §3.

---

## 6. Demo rehearsal protocol

Owner: **Sean + Banner (Bruce)**. Anvil-verified pass criteria.

| When | What | Pass = | Fail action |
|---|---|---|---|
| Mon EOD (T-16h) | Full smoke + 6-prompt walkthrough on live URL. Record video. | All 6 cite, banner+card render, no console errors, voice round-trip <10s | Triage on the spot, decide cut-list (§8) |
| Tue 07:00 (T-3h) | Dry run #1 — voice only, 6 prompts, fresh browser | Same as above | Patch only if blocker; otherwise note for #2 |
| Tue 08:00 (T-2h) | Dry run #2 — text fallback, 6 prompts | All 6 cite via /api/turn | If voice fails here, swap demo to text-only mode (R3 mitigation) |
| Tue 09:00 (T-1h) | Dry run #3 — full voice + text mix, presenter PoV | 3-for-3 success rate (SC-002) | If <3/3, freeze build, no more merges, escalate to Anvil |
| Tue 10:00 | Demo | n/a | n/a |

Hard rule: **no merges to main after Tue 07:00** unless a P0 demo-blocker is found in dry run #1 and Anvil signs off. After dry run #3 the build is frozen.

---

## 7. Risk register

| ID | Risk (from spec) | Mitigation | Owner |
|---|---|---|---|
| R1 | 11-PR merge surface unknown | §3 fixed order + smoke gate; §8 cut-list triggers at T-24h / T-12h / T-6h | Okoye |
| R2 | service-advisor infra gaps | Step 10 includes Bicep verify from clean azd env in `swedencentral` before merging #27 | Stark |
| R3 | Voice provider outage demo day | Dry run #2 (text-only) qualifies fallback; presenter script has text path memorized | Sean |
| R4 | Session 2 doesn't see this spec | Sean confirms in `.squad/decisions.md` *before* first session-2 push; PR template adds `Read specs/002-tuesday-demo/spec.md? [y/n]` | Sean |
| R5 | Sean exhaustion | Step 0 first → Sean removed from per-merge verify; postdeploy is the gate | Anvil |
| **R6 (new)** | nginx `/api/health` rewrite is fragile (#25 vs #26 overlap) | §2.4 pinned canonical config; #26 conflict resolution rule §3 | Parker |
| **R7 (new)** | ACA revision pinning — postdeploy might check the *previous* revision URL during rollout | smoke-test sleeps 15s after deploy, then polls /api/health up to 6×5s before declaring fail | Okoye |
| **R8 (new)** | Demo browser blocks mic on fresh profile | Pre-grant mic via Chromium policy on demo laptop; document in §6 Mon EOD check | Sean |
| **R9 (new)** | Cassettes drift if anyone touches scenario YAMLs mid-train | Freeze `evals/scenarios/` + `evals/cassettes/` after step 0; any change requires Anvil Large gate | Banner |
| **R10 (new)** | PR #27 reshapes `route_graph.json` while `feat/route-map` reads it | #27 merges *before* `feat/route-map` (§3 step 10 → 11); Session B rebases after #27, schema-validates the file in their vitest spec, flags any field rename in PR body | Stark + Parker |
| **R11 (new)** | App.tsx three-way collision (#21, #23, `feat/route-map`) | §4.1 hot-zone rule: handoff log records `App.tsx last touched by`, Session B rebases `feat/route-map` after #23 has landed; merge order in §3 makes #23 strictly precede `feat/route-map` | Parker (both sessions) |

---

## 8. Cut-list (ordered; drop top-down as time slips)

Trigger thresholds: **T-24h** = drop tier 1; **T-12h** = drop tier 2; **T-6h** = drop tier 3 and freeze.

| Tier | When dropped | Item | Cost to demo |
|---|---|---|---|
| 1 | T-24h slip | US7 spacebar PTT (P3) | none — mic button works |
| 1 | T-24h slip | US8 user-side transcription (P3) | mild — assistant still cites |
| 1 | T-24h slip | ~~RouteMap~~ — **NO LONGER DROPPABLE at T-24h** (Session B has it in flight on `feat/route-map`, promoted to in-scope per Sean's SWOT decision); cut only if its PR isn't ready by **T-12h**, in which case keep the branch open as draft and demo without it | none — App.tsx import + JSX line revert is mechanical |
| 2 | T-12h slip | smoke-test `--full` mode (keep checks 1–4 only) | lose per-prompt regression detection; mitigate with manual rehearsal |
| 2 | T-12h slip | Dockerfile HEALTHCHECKs on internal services (keep frontend + orchestrator only) | ACA still routes; weaker readiness signal |
| 2 | T-12h slip | PR #28 (docs) | postpone — docs |
| 2 | T-12h slip | Demo prompts 5 & 6 (alternate route, shuttle bridging) | shrink script to 4 prompts; still demonstrates both specialists if prompt 4 lands |
| 3 | T-6h slip | service-advisor entirely → revert PR #27, demo log-analyst only (prompts 1–3) | major UX downgrade but demo still runs |
| 3 | T-6h slip | Voice on stage → text-only via /api/turn (R3 path) | reframe as "text-first preview" |
| 3 | T-6h slip | postdeploy hook (keep manual smoke) | regression risk back on Sean; only if hook itself is broken |

**Hard floors that never get cut**: §2.1 smoke-test script existence, FR-013 main-only deploys, FR-018 eval gates green, FR-007/SC-010 mock-data discipline.

---

## 9. Anvil verification gates

| Work item | Size | Anvil tier | Criterion to escalate to Large |
|---|---|---|---|
| `scripts/smoke-test.{sh,ps1}` | M | **Large (3 reviewers)** | Always Large — load-bearing gate |
| `azure.yaml` postdeploy hook | S | Medium (1) | Escalate if shell-quoting platform differences surface |
| Dockerfile HEALTHCHECKs ×4 | S | Medium (1) | n/a — mechanical |
| nginx `/api/health` rewrite (§2.4) | S | **Large** | Always Large — owner of FR-014; PR #25/#26 overlap proved it's a footgun |
| PR #19, #21, #23 (frontend small fixes) | S | Medium | Escalate if any change touches nginx.conf |
| PR #20, #22, #24 (orchestrator) | M | Medium | Escalate if WebSocket frame shape changes |
| **PR #25** | M | **Large** | Always Large — nginx + audio + health all in one PR |
| **PR #26** | M | **Large** | Always Large — conflict resolution with #25 |
| **PR #27** | L | **Large** | Always Large — adds service to azure.yaml, infra surface |
| **`feat/route-map` (Session B)** | M | **Large (3 reviewers: Parker, Banner, T'Challa per Session B plan)** | Always Large — touches App.tsx (hot zone, R11) AND reads `route_graph.json` (R10). Escalation already baked in: Session B named Parker + Banner + T'Challa; Anvil acts as 4th adversarial reviewer for the merge. |
| `deploy.yml` main-only guard | S | **Large** | Always Large — FR-013 enforcement |
| `.squad/decisions.md` handoff entries | XS | None (process artifact) | n/a |
| Demo rehearsal sign-off | n/a | **Large** | Final go/no-go (T-1h) |

**Escalation rule (general)**: any change touching deploy pipeline, nginx config, Bicep, `azure.yaml`, or `evals/calibration*` → Large. Anything else defaults to Medium.

---

## 10. Open questions for `/speckit.tasks`

1. **Who is Session B?** Plan assumes one parallel Copilot session exists; if Sean is solo, collapse §4 split and serialize everything onto Session A (adds ~6h to train).
2. **`/healthz` endpoint presence per service** — confirmed for orchestrator (PR #25 path), unverified for log-analyst and service-advisor. Task should `grep -r "/healthz\|/health" apps/` and add stub if missing before §2.3 lands.
3. **PR #26 vs #25 overlap exact diff** — plan picks the resolution rule but tasks should diff the two branches and explicitly list which hunks to keep/drop.
4. **service-advisor port** — assumed `:8002` in §2.3; tasks must read `apps/service_advisor/` Dockerfile and `infra/modules/serviceAdvisor.bicep` (if exists) to confirm.
5. **`SERVICE_FRONTEND_URI` env var name** — assumed by azd convention; tasks should verify with `azd env get-values` against the live env and adjust §2.2 if it's something else (e.g. `AZURE_FRONTEND_URL`).
6. **Cassette additions for service-advisor prompts (4–6)** — FR-018 says eval gates must be green; do prompts 4–6 have cassettes yet, or does the task list need to author them? If yes → adds ~2h, falls under R9.
7. **Demo laptop / browser profile** — Chromium mic permission seeding (R8); tasks should produce a one-page checklist Sean runs Monday EOD.
8. **`route_graph.json` schema stability under #27** — Session B's RouteMap depends on the current shape (10 stations, `shuttle_bridges[DSR_ID]` entries). Tasks must diff #27's branch against main on `apps/service_advisor/data/route_graph.json`; if any field renames, file an inline fix-up commit on `feat/route-map` before flipping to ready.
9. **`@data` alias decision (Session B D1)** — relative import vs. Vite alias. If Session B adopts the alias, tasks need to confirm `tsconfig.json` and `vite.config.ts` edits don't collide with anything in PRs #19–#26 (currently they don't, per file-overlap map §4.1).
10. **Demo script update** — does RouteMap get its own beat in the 6-prompt walkthrough, or does it ride along passively under prompts 4 & 5? Recommend passive (no new prompt); tasks should confirm with Sean and update rehearsal protocol §6 if so.

---

## Phase 0 / Phase 1 artifacts

This feature is operational (deploy + merge orchestration), not a data/contract design. Therefore:

- **research.md**: not generated — all unknowns are listed in §10 as concrete task inputs, not open research threads.
- **data-model.md**: not generated — no new entities beyond the spec's Key Entities (Demo Build, Demo Prompt, Open PR, Health Endpoint), which are operational rather than persisted.
- **contracts/**: not generated — `/api/health` JSON shape is pinned in §2.4 and smoke-test contract in §2.1; both are inline.
- **quickstart.md**: not generated — `scripts/smoke-test.sh <url>` *is* the quickstart for this feature; rehearsal protocol §6 is the human runbook.

If `/speckit.tasks` insists on these files, generate them as one-paragraph stubs pointing back to the relevant section of this plan.

---

## Rollback

Per item:
- Smoke-test script / postdeploy hook → revert the chore PR; deploy continues without gate.
- Any merged PR → `git revert <sha>` on main, re-run smoke. Merge train is designed so each PR is independently revertable.
- #27 (service-advisor) → revert restores azure.yaml without it; orchestrator handles missing specialist via cited "service unavailable" (spec edge case).
- Catastrophic: redeploy `main@bc53e11` (yesterday's PR #17 HEAD) — known-recovered baseline.
