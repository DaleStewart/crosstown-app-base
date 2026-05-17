---
description: "Atomic, agent-spawnable task list for the Tuesday 2026-05-19 customer demo merge train."
---

# Tasks: Crosstown Transit AI — Tuesday Customer Demo

**Feature**: `002-tuesday-demo` · **Demo**: 2026-05-19 10:00 (T-60h at task generation) · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Delta analysis**: [docs/47doors-comparison.md](../../docs/47doors-comparison.md)

---

## Preamble — autonomous decisions made while generating this list

Per the `/speckit.tasks` prompt, the following decisions were made without round-tripping to Sean. They are reversible — flag any objection and the affected tasks will be re-sequenced.

1. **Task atomicity > plan §3 row granularity.** The plan packs each merge-train row as a single "PR" entity. This list explodes each PR into the same 4-beat cluster — `Rebase → Local verify → Anvil review → Merge + smoke` — so any one agent can complete one task in one spawn. Where a PR has unusual surface (e.g. #25 nginx + audio + health, #26 conflict resolution, #27 service-advisor infra), extra beats are inserted.
2. **Cast assignment follows plan §3 "Owner of conflict resolution" column** with Banner picking up all `--full` smoke runs (he's the tester) and Anvil acting as the verification gate on every Large item rather than as a task owner.
3. **Anvil tier mirrors plan §9** verbatim. Any task that touches deploy pipeline / nginx / Bicep / `azure.yaml` / `evals/calibration*` is Large by default. Mechanical tasks (Dockerfile HEALTHCHECKs, doc PRs, smoke runs) are Small. Everything else is Medium.
4. **Step 0 (`chore/deploy-hygiene`) is decomposed into 7 sibling tasks** (T101–T107) so Okoye/Stark/Parker can parallelize the smoke script, postdeploy hook, four HEALTHCHECKs, nginx rewrite, and main-only deploy guard. They all converge at T108 (Anvil Large review of the bundle) before T109 merges them as one squash commit (plan §3 row 0 is one PR but its contents are intrinsically parallel).
5. **`feat/route-map` is treated as Session B-owned and read-only for Session A.** Session A tasks for it (T501, T503, T505) are *checkpoints, rebase guidance, and merge-orchestration only* — they never edit code on that branch. The actual implementation tasks would live in Session B's task list; they are referenced here as `[SESSION-B]` placeholders so Session A knows what handoff to expect.
6. **App.tsx hot-zone checkpoints (T401, T501, T504)** are net-new tasks the plan implies but doesn't enumerate. Each one is a 5-minute read of `.squad/decisions.md` + `git log -- apps/frontend/src/App.tsx` before any agent is allowed to touch `App.tsx`.
7. **Smoke-test-between-merges is a first-class task (T2xxS, T3xxS, T4xxS suffix).** Plan §3 says "smoke after each merge"; here that's a dedicated atomic task with its own verification command and pass criterion. They are P0 and non-skippable.
8. **Demo dry runs are 4 separate tasks (T601–T604)** per SC-002 + plan §6: Mon EOD, Tue 07:00, Tue 08:00 (text fallback), Tue 09:00 (mixed). T604 is the freeze gate — no merges may follow.
9. **Cut-list tasks (T7xx) are pre-scheduled but conditional.** They have explicit trigger conditions (T-24h / T-12h / T-6h) and are marked `P3` so they don't run unless their trigger fires.
10. **Test tasks are not generated** — the spec is operational (deploy + merge orchestration) and explicitly says "no backfilling tests for code that already shipped" (Out of Scope §). Existing CI (`ci.yml`, `eval.yml`, `redteam.yml`) covers per-PR validation; smoke tests cover deploy validation; demo dry runs cover system validation. Adding unit-test tasks would be scope creep.

### Tag legend

Every task carries these sub-bullet attributes:

- **Cast**: which `.squad/team.md` member spawns this task (or `Session B` for cross-session items, or `Anvil` for verification gates).
- **Tier**: Anvil verification tier — **S**(mall, 0–1 reviewer, advisory), **M**(edium, 1 reviewer, baseline check), **L**(arge, 3 reviewers + SQL ledger + evidence bundle).
- **Priority**: **P0** (critical path, blocks demo), **P1** (high value, demo degrades without), **P3** (droppable per cut-list §8).
- **Deps**: other task IDs that must be `done` before this can start.
- **Wall-clock**: realistic estimate for one agent in one spawn (not parallelized).
- **Inputs**: file paths the agent must read.
- **Outputs**: file paths the agent must write/modify.
- **Verify**: command(s) whose successful exit (or pass output) closes the task.

### Format note

Tasks follow the strict checklist format the `/speckit.tasks` command requires (`- [ ] T### [P?] [Story?] description with path`). The `[P]` marker means "parallelizable with siblings in the same phase". The `[USn]` story tag maps to the spec's user stories (US1–US8) where applicable; deploy-hygiene tasks carry the story they unblock.

---

## Phase 0: Pre-train baseline (must run before slot 0)

**Purpose**: Establish a known-good baseline against which the first smoke-test invocation can be compared, and resolve plan §10 open questions that gate code authorship.

- [ ] T001 [P] [US3] Confirm `/healthz` endpoint presence in every Python service by running `Select-String -Path apps/orchestrator,apps/log_analyst,apps/service_advisor -Pattern '/healthz|/health' -Recurse` and recording results in `.squad/decisions.md`
  - Cast: Stark · Tier: S · Priority: P0 · Deps: — · Wall-clock: 15 min
  - Inputs: `apps/orchestrator/`, `apps/log_analyst/`, `apps/service_advisor/`
  - Outputs: `.squad/decisions.md` (new entry: `## 2026-05-16 — healthz audit`)
  - Verify: `.squad/decisions.md` contains one of {present, stub-added} for each of orchestrator / log_analyst / service_advisor; resolves plan §10 Q2

- [ ] T002 [P] [US3] Add 6-line `GET /healthz` route to any service flagged as missing in T001 (must return `{"status":"ok","service":"<name>"}`); commit to `chore/deploy-hygiene` branch
  - Cast: Stark · Tier: M · Priority: P0 · Deps: T001 · Wall-clock: 20 min (skip if T001 finds all three present)
  - Inputs: T001 output, each service's `main.py` or `app.py`
  - Outputs: up to 3 files under `apps/*/`
  - Verify: `cd apps/<svc> && python -m pytest -q tests/` stays green; manual `uvicorn` curl returns 200

- [ ] T003 [P] [US3] Confirm `service-advisor` listens on `:8002` (or update plan §2.3 + T105 with actual port) by reading `apps/service_advisor/Dockerfile` and `infra/modules/serviceAdvisor.bicep` (if present)
  - Cast: Okoye · Tier: S · Priority: P0 · Deps: — · Wall-clock: 10 min
  - Inputs: `apps/service_advisor/Dockerfile`, `infra/modules/serviceAdvisor.bicep`
  - Outputs: `.squad/decisions.md` (new entry: `## 2026-05-16 — service_advisor port confirmed`)
  - Verify: `.squad/decisions.md` records the confirmed port; resolves plan §10 Q4

- [ ] T004 [P] [US3] Confirm azd env exposes frontend URL as `SERVICE_FRONTEND_URI` (or update plan §2.2 + T103 with actual var name) by running `azd env get-values | Select-String -Pattern 'FRONTEND|URI|URL'`
  - Cast: Okoye · Tier: S · Priority: P0 · Deps: — · Wall-clock: 5 min
  - Inputs: live azd env
  - Outputs: `.squad/decisions.md` (entry: confirmed env var name)
  - Verify: var name written to decisions log; resolves plan §10 Q5

- [ ] T005 [P] [US2] Diff `apps/service_advisor/data/route_graph.json` between `main` and `pr/27` heads; record schema delta (if any) in `.squad/decisions.md` and flag Session B if any field renames
  - Cast: Stark · Tier: S · Priority: P0 · Deps: — · Wall-clock: 15 min
  - Inputs: `git fetch origin pull/27/head:pr-27`, `apps/service_advisor/data/route_graph.json` on both refs
  - Outputs: `.squad/decisions.md` (entry: route_graph.json schema diff)
  - Verify: `git diff main pr-27 -- apps/service_advisor/data/route_graph.json` output captured; resolves plan §10 Q8 + R10

- [ ] T006 [P] [US6] Confirm Session B has read `specs/002-tuesday-demo/spec.md` + plan §4.1 by checking `.squad/decisions.md` for an explicit acknowledgement entry from Session B; if absent, post a request and wait
  - Cast: T'Challa · Tier: S · Priority: P0 · Deps: — · Wall-clock: 5 min (sync) + indefinite (async wait)
  - Inputs: `.squad/decisions.md`, `.squad/team.md`
  - Outputs: `.squad/decisions.md` (entry: session B ack confirmed or pending)
  - Verify: presence of `## 2026-05-16 ... — Session B spec ack` entry; resolves spec R4

- [ ] T007 [US2] Confirm cassettes exist for service-advisor demo prompts 4–6 (`get_disruption_status`, `find_alternate_route`, `get_shuttle_bridging`); if missing, author them on `chore/deploy-hygiene` so `eval.yml` stays green
  - Cast: Banner · Tier: M (L if new cassettes added — touches `evals/`) · Priority: P0 · Deps: — · Wall-clock: 30–120 min
  - Inputs: `evals/scenarios/`, `evals/cassettes/`, `evals/orchestrator_runner.py`
  - Outputs: up to 3 new files under `evals/cassettes/` + matching YAMLs under `evals/scenarios/`
  - Verify: `cd evals && python -m orchestrator_runner --max-fail-pct 0` passes; resolves plan §10 Q6

**Checkpoint C-PRE**: T001–T007 done. `.squad/decisions.md` reflects all plan §10 answers needed before code is authored. Step 0 may begin.

---

## Phase 1 — Slot 0: `chore/deploy-hygiene` (NEW; load-bearing)

**Purpose**: Land smoke gate, postdeploy hook, healthchecks, nginx rewrite, and main-only deploy guard as one squash commit, **before** any feature PR is merged, so every subsequent smoke run uses the real gate (plan §3 rationale; spec R5).

- [ ] T101 [P] [US3] Author `scripts/smoke-test.sh` implementing plan §2.1 checks 1–4 + optional `--full` (checks 5: 6 rehearsed prompts); exits non-zero on first failure; completes <30s; prints one-line summary
  - Cast: Okoye · Tier: **L** (always Large per plan §9) · Priority: P0 · Deps: T001..T005 · Wall-clock: 90 min
  - Inputs: plan §2.1, `docs/47doors-comparison.md` §8.1 (reference implementation), spec FR-009
  - Outputs: `scripts/smoke-test.sh` (executable, +x)
  - Verify: `bash scripts/smoke-test.sh https://k8sequickstart-default.someplace.azurecontainerapps.io` exits non-zero with "FAIL at check 1"; `bash scripts/smoke-test.sh <healthy-staging-url>` exits 0 in <30s

- [ ] T102 [P] [US3] Mirror T101 logic in `scripts/smoke-test.ps1` (Windows parity for FR-009)
  - Cast: Okoye · Tier: **L** · Priority: P0 · Deps: T101 (cherry-pick logic) · Wall-clock: 60 min
  - Inputs: `scripts/smoke-test.sh` (canonical)
  - Outputs: `scripts/smoke-test.ps1`
  - Verify: `pwsh scripts/smoke-test.ps1 <staging-url>` matches sh exit codes and timing on the same target

- [ ] T103 [P] [US3] Add `azure.yaml` `postdeploy` hook per plan §2.2 (posix → sh, windows → pwsh, no `continueOnError`), using env var name confirmed in T004
  - Cast: Okoye · Tier: M (escalate to L if shell-quoting differences surface) · Priority: P0 · Deps: T101, T102, T004 · Wall-clock: 20 min
  - Inputs: `azure.yaml`, T004 output
  - Outputs: `azure.yaml` (new `hooks.postdeploy` block)
  - Verify: `azd hooks run postdeploy --service frontend` in dry-run completes; YAML parses (`azd env list` doesn't error)

- [ ] T104 [P] [US3] Add `HEALTHCHECK` directive to `apps/orchestrator/Dockerfile`, `apps/log_analyst/Dockerfile`, `apps/service_advisor/Dockerfile` per plan §2.3 (port from T003 for service_advisor)
  - Cast: Stark · Tier: M (mechanical) · Priority: P0 · Deps: T002, T003 · Wall-clock: 20 min
  - Inputs: three Dockerfiles, T003 port confirmation
  - Outputs: three Dockerfiles modified
  - Verify: `docker build apps/<svc> -t test:hc` then `docker inspect --format='{{.Config.Healthcheck}}' test:hc` shows the directive; container started locally transitions to `healthy` within 60s

- [ ] T105 [P] [US3] Add `HEALTHCHECK` to `apps/frontend/Dockerfile` (nginx stage) probing `localhost:80/api/health`
  - Cast: Parker · Tier: M · Priority: P0 · Deps: T106 (nginx rewrite must be in same commit) · Wall-clock: 15 min
  - Inputs: `apps/frontend/Dockerfile`
  - Outputs: `apps/frontend/Dockerfile`
  - Verify: same as T104

- [ ] T106 [P] [US1] Add explicit `location = /api/health` rewrite to `apps/frontend/nginx.conf` per plan §2.4 (must precede catch-all `/api/`)
  - Cast: Parker · Tier: **L** (always Large per plan §9 — FR-014 owner) · Priority: P0 · Deps: T001 (orchestrator /healthz confirmed) · Wall-clock: 30 min
  - Inputs: `apps/frontend/nginx.conf`, plan §2.4
  - Outputs: `apps/frontend/nginx.conf`
  - Verify: locally `docker compose up frontend orchestrator` (or equivalent), `curl http://localhost/api/health` returns 200 + JSON with `status` in {`ok`,`degraded`} and `service: "orchestrator"`

- [ ] T107 [P] [US4] Add main-only guard to `.github/workflows/deploy.yml`: first step `if: github.ref == 'refs/heads/main'` else fail with named error; add `workflow_dispatch` input `confirm_non_main: bool` with `::warning::` echo
  - Cast: Okoye · Tier: **L** (always Large per plan §9 — FR-013 enforcement) · Priority: P0 · Deps: — · Wall-clock: 30 min
  - Inputs: `.github/workflows/deploy.yml`
  - Outputs: same file
  - Verify: push a no-op commit to a feature branch and trigger the workflow → run exits non-zero with the expected message; trigger on `main` → proceeds normally

- [ ] T108 [US3] Anvil Large review of the bundled `chore/deploy-hygiene` PR (T101..T107): 3 reviewers (Anvil + Stark + Banner), baseline check, SQL ledger entry, evidence bundle (smoke-test transcript on healthy + on Hello World target)
  - Cast: Anvil · Tier: **L** · Priority: P0 · Deps: T101..T107 · Wall-clock: 45 min
  - Inputs: PR diff, T101 verify transcripts, T107 verify transcripts
  - Outputs: Anvil verdict comment on PR; SQL ledger row
  - Verify: PR has "Anvil: APPROVED (Large, 3/3)" comment

- [ ] T109 [US3] Squash-merge `chore/deploy-hygiene` to `main`; claim the push slot in `.squad/decisions.md` before, release after
  - Cast: Okoye · Tier: M (process) · Priority: P0 · Deps: T108 · Wall-clock: 10 min
  - Inputs: `.squad/decisions.md`
  - Outputs: `main` advanced by one commit; `.squad/decisions.md` claim+release entries
  - Verify: `git log main -1 --oneline` shows the merge; CI `deploy.yml` triggered

- [ ] T110 [US3] **SMOKE GATE** — baseline run of `scripts/smoke-test.sh <prod-url>` against post-T109 deploy; must exit 0; this is the reference smoke that every subsequent merge is compared against
  - Cast: Banner · Tier: M · Priority: P0 · Deps: T109 + completed `deploy.yml` run · Wall-clock: 5 min
  - Inputs: deployed frontend URL
  - Outputs: smoke transcript pasted into `.squad/decisions.md`
  - Verify: exit 0; "smoke OK in <Ns>" recorded

**Checkpoint C-0**: Slot 0 done. Deploy gate is live. Train may proceed. Session A releases push slot; Session B can begin frontend chain.

---

## Phase 2 — Slot 1: PR #28 (47doors docs)

- [ ] T201 [US5] Rebase PR #28 on `main` (now contains T109)
  - Cast: Scribe · Tier: S · Priority: P1 · Deps: T110 · Wall-clock: 10 min
  - Inputs: `pr/28` branch
  - Outputs: rebased branch + force-push
  - Verify: `gh pr view 28 --json mergeable` returns `MERGEABLE`

- [ ] T202 [US5] Anvil Medium review of PR #28 (docs-only, low risk)
  - Cast: Anvil · Tier: M · Priority: P1 · Deps: T201 · Wall-clock: 15 min
  - Verify: PR has Anvil approval

- [ ] T203 [US5] Squash-merge PR #28 to `main`
  - Cast: Scribe · Tier: S · Priority: P1 · Deps: T202 · Wall-clock: 5 min
  - Verify: `gh pr view 28` shows MERGED

- [ ] T204S [US5] **SMOKE GATE** between merges — `scripts/smoke-test.sh <prod-url>` exit 0
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T203 + `deploy.yml` run · Wall-clock: 5 min
  - Verify: exit 0; record in `.squad/decisions.md`

---

## Phase 3 — Frontend + orchestrator merge train (slots 2–9)

> **Cross-session note**: Per plan §4.1, Session B owns the frontend PRs (#19, #21, #23, #25, #26). Session A owns the orchestrator PRs (#20, #22, #24). The slots interleave because some frontend changes need orchestrator changes already live. Each PR cluster follows the same 4-beat pattern: **Rebase → Local verify → Anvil review → Merge + smoke gate**.

### Slot 2: PR #19 — `fix(frontend): stop frame on mic release`

- [ ] T301 [P] [US1] Rebase PR #19 on `main`
  - Cast: Parker (Session B) · Tier: S · Priority: P0 · Deps: T204S · Wall-clock: 10 min
  - Verify: `gh pr view 19 --json mergeable` MERGEABLE
- [ ] T302 [US1] Local verify: `cd apps/frontend && npm ci && npm run lint && npm run typecheck && npm test -- --run && npm run build`
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T301 · Wall-clock: 10 min
  - Verify: all four commands exit 0
- [ ] T303 [US1] Anvil Medium review of PR #19
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T302 · Wall-clock: 15 min
- [ ] T304 [US1] Squash-merge PR #19
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T303 · Wall-clock: 5 min
- [ ] T305S [US5] **SMOKE GATE** — frontend boots, `/api/health` 200
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T304 + deploy · Wall-clock: 5 min

### Slot 3: PR #20 — `fix(orchestrator): server VAD + audio commit`

- [ ] T311 [US1] Rebase PR #20 on `main`
  - Cast: Wanda (Session A) · Tier: S · Priority: P0 · Deps: T305S · Wall-clock: 10 min
- [ ] T312 [US1] Local verify orchestrator: `cd apps/orchestrator && ruff check . && mypy --strict . && pytest -q`
  - Cast: Wanda · Tier: M · Priority: P0 · Deps: T311 · Wall-clock: 15 min
  - Verify: all three exit 0 (mypy stays strict-clean per repo invariant)
- [ ] T313 [US1] Anvil Medium review of PR #20 (escalate to L if WS frame shape changes)
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T312 · Wall-clock: 20 min
- [ ] T314 [US1] Squash-merge PR #20
  - Cast: Wanda · Tier: S · Priority: P0 · Deps: T313 · Wall-clock: 5 min
- [ ] T315S [US5] **SMOKE GATE** — voice turn completes locally (manual curl /api/turn + /ws/voice handshake)
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T314 + deploy · Wall-clock: 10 min

### Slot 4: PR #21 — `feat(frontend): render user-turn transcripts`

- [ ] T321 [US1] Rebase PR #21 on `main` (now has #19); confirms `App.tsx` last-touch in `.squad/decisions.md`
  - Cast: Parker (Session B) · Tier: S · Priority: P0 · Deps: T315S · Wall-clock: 15 min
  - Verify: handoff entry written with `App.tsx last touched by: #19 → about to be #21`
- [ ] T322 [US1] Local verify frontend (lint/typecheck/test/build as T302)
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T321 · Wall-clock: 10 min
- [ ] T323 [US1] Anvil Medium review of PR #21
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T322 · Wall-clock: 15 min
- [ ] T324 [US1] Squash-merge PR #21; update `App.tsx last touched by` in `.squad/decisions.md`
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T323 · Wall-clock: 10 min
- [ ] T325S [US5] **SMOKE GATE** — UI shows user turns
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T324 + deploy · Wall-clock: 5 min

### Slot 5: PR #22 — `fix(orchestrator): emit user-turn transcripts`

- [ ] T331 [US1] Rebase PR #22 on `main`
  - Cast: Wanda · Tier: S · Priority: P0 · Deps: T325S · Wall-clock: 10 min
- [ ] T332 [US1] Local verify orchestrator (T312 pattern)
  - Cast: Wanda · Tier: M · Priority: P0 · Deps: T331 · Wall-clock: 15 min
- [ ] T333 [US1] Anvil Medium review of PR #22
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T332 · Wall-clock: 20 min
- [ ] T334 [US1] Squash-merge PR #22
  - Cast: Wanda · Tier: S · Priority: P0 · Deps: T333 · Wall-clock: 5 min
- [ ] T335S [US5] **SMOKE GATE** — end-to-end user transcript visible after a voice turn
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T334 + deploy · Wall-clock: 10 min

### Slot 6: PR #23 — `feat(frontend): text input`

- [ ] T341 [US1] Rebase PR #23 on `main` (now has #21); record App.tsx touch
  - Cast: Parker (Session B) · Tier: S · Priority: P0 · Deps: T335S · Wall-clock: 15 min
- [ ] T342 [US1] Local verify frontend
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T341 · Wall-clock: 10 min
- [ ] T343 [US1] Anvil Medium review of PR #23
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T342 · Wall-clock: 15 min
- [ ] T344 [US1] Squash-merge PR #23; update `App.tsx last touched by` to `#23`
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T343 · Wall-clock: 10 min
- [ ] T345S [US5] **SMOKE GATE** — `/api/turn` works from UI (text → cited reply)
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T344 + deploy · Wall-clock: 5 min

### Slot 7: PR #24 — `fix(orchestrator): safe transcription default + GA nested`

- [ ] T351 [US1] Rebase PR #24 on `main`
  - Cast: Wanda · Tier: S · Priority: P0 · Deps: T345S · Wall-clock: 10 min
- [ ] T352 [US1] Local verify orchestrator
  - Cast: Wanda · Tier: M · Priority: P0 · Deps: T351 · Wall-clock: 15 min
- [ ] T353 [US1] Anvil Medium review of PR #24
  - Cast: Anvil · Tier: M · Priority: P0 · Deps: T352 · Wall-clock: 20 min
- [ ] T354 [US1] Squash-merge PR #24
  - Cast: Wanda · Tier: S · Priority: P0 · Deps: T353 · Wall-clock: 5 min
- [ ] T355S [US5] **SMOKE GATE** — no WebSocket close storm; run smoke + spot-check orchestrator logs for clean shutdown
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T354 + deploy · Wall-clock: 10 min

### Slot 8: PR #25 — `fix(frontend): spacebar PTT + audio capture + nginx /api/health`

- [ ] T361 [US1] Rebase PR #25 on `main` (now has #23); verify nginx rewrite matches plan §2.4 (should already, since T106 landed it)
  - Cast: Parker (Session B) · Tier: M · Priority: P0 · Deps: T355S · Wall-clock: 20 min
  - Verify: `diff apps/frontend/nginx.conf` (PR vs main) shows no regression of the `location = /api/health` block
- [ ] T362 [US1] Local verify frontend + manual spacebar test in browser against staging
  - Cast: Parker · Tier: M · Priority: P0 · Deps: T361 · Wall-clock: 20 min
- [ ] T363 [US1] Anvil **Large** review of PR #25 (always L per plan §9 — nginx + audio + health in one PR)
  - Cast: Anvil · Tier: **L** · Priority: P0 · Deps: T362 · Wall-clock: 45 min
- [ ] T364 [US1] Squash-merge PR #25
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T363 · Wall-clock: 10 min
- [ ] T365S [US5] **SMOKE GATE** — spacebar PTT functional, `/api/health` via proxy returns 200
  - Cast: Banner · Tier: S · Priority: P0 · Deps: T364 + deploy · Wall-clock: 10 min

### Slot 9: PR #26 — `fix(frontend): restore spacebar + /api/health (Anvil variant)`

- [ ] T371 [US1] Rebase PR #26 on `main` (now has #25); explicitly resolve overlap per plan §3 step 9 rule — keep #25's nginx rule verbatim, take #26's audio-fix delta only where it doesn't undo #25
  - Cast: Parker (Session B) · Tier: **L** (always Large per plan §9 — conflict resolution with #25) · Priority: P0 · Deps: T365S · Wall-clock: 60 min
  - Inputs: `pr/26` diff, current `main`, plan §3 step 9 rule
  - Outputs: resolved branch + PR comment documenting which hunks were kept/dropped
  - Verify: `git diff main pr-26 -- apps/frontend/nginx.conf` shows zero changes to the `/api/health` block; `npm run build` passes
- [ ] T372 [US1] Local verify frontend (full lint/typecheck/test/build) + manual spacebar regression
  - Cast: Parker · Tier: M · Priority: P0 · Deps: T371 · Wall-clock: 20 min
- [ ] T373 [US1] Anvil **Large** review of PR #26 (conflict resolution audit)
  - Cast: Anvil · Tier: **L** · Priority: P0 · Deps: T372 · Wall-clock: 45 min
- [ ] T374 [US1] Squash-merge PR #26
  - Cast: Parker · Tier: S · Priority: P0 · Deps: T373 · Wall-clock: 10 min
- [ ] T375S [US5] **SMOKE GATE — full** — `scripts/smoke-test.sh --full <prod-url>` (re-runs all 6 prompts; first time `--full` is invoked in the train)
  - Cast: Banner · Tier: M · Priority: P0 · Deps: T374 + deploy · Wall-clock: 15 min
  - Verify: all 6 prompts cite; tool routing correct for prompts 1–3 (4–6 will still fail until #27 lands — record this expected failure explicitly)

**Checkpoint C-FE**: Frontend chain complete. Session B releases push slot. Session A picks up #27.

---

## Phase 4 — Slot 10: PR #27 (service-advisor) — Large gate

- [ ] T401 [US6] **Cross-session checkpoint** — read `.squad/decisions.md` for latest `App.tsx last touched by` (expected: `#23` or possibly `#25`); confirm Session B has released push slot; confirm `feat/route-map` is still draft and has NOT been rebased on main yet (Session B waits for #27)
  - Cast: T'Challa (Session A) · Tier: S · Priority: P0 · Deps: T375S · Wall-clock: 10 min
  - Inputs: `.squad/decisions.md`, `gh pr list --state open --label session-b`
  - Outputs: handoff entry in `.squad/decisions.md`: `## ... — Session A claims push slot for #27`
  - Verify: no open Session B push claim; `gh pr view feat/route-map` shows `isDraft: true`

- [ ] T402 [P] [US2] Verify `azd up` from a clean `swedencentral` env reaches a healthy state with PR #27 branch checked out — proves spec R2 (service-advisor infra not yet in Bicep would surface here)
  - Cast: Stark · Tier: **L** · Priority: P0 · Deps: T401 · Wall-clock: 60 min
  - Inputs: `pr/27` branch, fresh azd env (or `azd env new test-pr27`)
  - Outputs: `.squad/decisions.md` entry: `azd up clean: PASS|FAIL` + Bicep gap list if any
  - Verify: `azd up` exits 0; all 4 ACA apps `Running`; smoke against ephemeral URL exits 0

- [ ] T403 [US2] Rebase PR #27 on `main`
  - Cast: Okoye · Tier: S · Priority: P0 · Deps: T401 · Wall-clock: 15 min

- [ ] T404 [US2] Local verify: orchestrator + service_advisor strict mypy + pytest; frontend build; `az bicep build --file infra/main.bicep --stdout > $null`
  - Cast: Stark · Tier: M · Priority: P0 · Deps: T403 · Wall-clock: 25 min

- [ ] T405 [US2] Diff `apps/service_advisor/data/route_graph.json` vs T005 baseline; if schema changed, write inline fix-up commit on `feat/route-map` notes for Session B to pick up
  - Cast: Stark · Tier: M · Priority: P0 · Deps: T404 · Wall-clock: 15 min
  - Outputs: `.squad/decisions.md` entry covering R10

- [ ] T406 [US2] Confirm `azure.yaml::services` block includes `service-advisor` (FR-012)
  - Cast: Okoye · Tier: S · Priority: P0 · Deps: T403 · Wall-clock: 5 min
  - Verify: `Select-String -Path azure.yaml -Pattern 'service-advisor'` returns match in `services:` block

- [ ] T407 [US2] Anvil **Large** review of PR #27 (3 reviewers, baseline check, SQL ledger, evidence bundle: T402 + T404 + T406 outputs)
  - Cast: Anvil · Tier: **L** · Priority: P0 · Deps: T402, T404, T405, T406 · Wall-clock: 60 min

- [ ] T408 [US2] Squash-merge PR #27
  - Cast: Okoye · Tier: S · Priority: P0 · Deps: T407 · Wall-clock: 10 min

- [ ] T409S [US5] **SMOKE GATE — full** — `scripts/smoke-test.sh --full <prod-url>`; all 6 prompts must now cite + correct tools fire; `DisruptionBanner` + `AlternateRouteCard` must render on prompts 4 + 5 (manual visual check)
  - Cast: Banner · Tier: M · Priority: P0 · Deps: T408 + deploy · Wall-clock: 20 min
  - Verify: smoke exits 0; screenshot/video evidence of both UI components rendering attached to `.squad/decisions.md`

**Checkpoint C-SA**: Service advisor live. Session A releases push slot. Session B may now rebase `feat/route-map` on `main`.

---

## Phase 5 — Slot 11: `feat/route-map` (Session B owns)

> **Hands-off rule**: Session A does not edit any file on `feat/route-map`. These tasks are *coordination + verification* only.

- [ ] T501 [US6] **Cross-session checkpoint (pre)** — post handoff to Session B in `.squad/decisions.md`: "PR #27 merged at <sha>; main now contains everything `feat/route-map` depends on; push slot released; please rebase, flip to ready, request review"
  - Cast: T'Challa (Session A) · Tier: S · Priority: P1 · Deps: T409S · Wall-clock: 5 min
  - Inputs: `.squad/decisions.md`
  - Outputs: handoff entry per plan §4.1 template

- [ ] T502 [US6] **[SESSION B]** Rebase `feat/route-map` on `main`; resolve App.tsx conflict (1 import + 1 JSX line above `<DisruptionBanner>`); run `npm run lint && npm run typecheck && npm test -- --run apps/frontend/src/components/RouteMap.test.tsx && npm run build`; flip PR from draft to ready
  - Cast: Session B (Parker, in their session) · Tier: **L** · Priority: P1 · Deps: T501 · Wall-clock: 60–90 min (estimated; Session A does not block on this)
  - Inputs: `feat/route-map`, current `main`
  - Outputs: rebased + ready PR
  - Verify: PR `isDraft: false`; CI green

- [ ] T503 [US6] **Cross-session checkpoint (mid)** — when Session B signals "ready for review" in `.squad/decisions.md`, Session A confirms `App.tsx last touched by: #23` (or whatever the post-#23 state is) is the rebase target Session B used; if not, request re-rebase
  - Cast: T'Challa (Session A) · Tier: M · Priority: P1 · Deps: T502 · Wall-clock: 10 min

- [ ] T504 [US6] Anvil **Large** review of `feat/route-map` (3 reviewers per Session B's plan: Parker + Banner + T'Challa; Anvil acts as 4th adversarial reviewer); evidence bundle includes RouteMap renders all 10 stations, L1 red on prompt 4, dashed shuttle overlay on prompt 6
  - Cast: Anvil · Tier: **L** · Priority: P1 · Deps: T502, T503 · Wall-clock: 60 min

- [ ] T505 [US6] Squash-merge `feat/route-map` (either session may merge once Anvil approves; coordinate via push-slot claim)
  - Cast: Okoye or Session B · Tier: S · Priority: P1 · Deps: T504 · Wall-clock: 10 min

- [ ] T506S [US5] **SMOKE GATE — full + manual** — `scripts/smoke-test.sh --full <prod-url>` exit 0 + manual: RouteMap renders all 10 stations, L1 turns red when prompt 4 fires, dashed shuttle overlay appears when prompt 6 fires
  - Cast: Banner · Tier: M · Priority: P1 · Deps: T505 + deploy · Wall-clock: 20 min

**Checkpoint C-RM**: RouteMap live. Merge train complete. Build is now demo-candidate.

---

## Phase 6 — Demo rehearsal (plan §6, spec SC-002)

- [ ] T601 [US2] **Dry run Mon EOD (T-16h)** — full smoke + 6-prompt walkthrough on live URL; record video
  - Cast: Sean + Banner · Tier: M · Priority: P0 · Deps: T506S (or T409S if RouteMap dropped per cut-list) · Wall-clock: 45 min
  - Pass: all 6 cite, banner+card render, no console errors, voice round-trip <10s
  - Fail action: triage on the spot, decide cut-list (Phase 7); document in `.squad/decisions.md`

- [ ] T602 [US2] **Dry run #1 Tue 07:00 (T-3h)** — voice only, 6 prompts, fresh Chromium profile with mic pre-granted (spec R8)
  - Cast: Sean + Banner · Tier: M · Priority: P0 · Deps: T601 · Wall-clock: 30 min
  - Fail action: patch only if blocker, otherwise note for dry run #2

- [ ] T603 [US2] **Dry run #2 Tue 08:00 (T-2h)** — text fallback path (R3 mitigation), 6 prompts via `/api/turn`
  - Cast: Sean + Banner · Tier: M · Priority: P0 · Deps: T602 · Wall-clock: 30 min
  - Fail action: if voice fails today, demo goes text-only (cut-list tier 3)

- [ ] T604 [US2] **Dry run #3 Tue 09:00 (T-1h)** — full voice + text mix from presenter PoV; 3-for-3 success rate (SC-002)
  - Cast: Sean + Banner + T'Challa (final go/no-go) · Tier: **L** (final Anvil sign-off per plan §9) · Priority: P0 · Deps: T603 · Wall-clock: 30 min
  - Pass: 3/3 across the three dry runs in aggregate → **BUILD FROZEN** at T604 close
  - Fail: <3/3 → no more merges; escalate to Anvil; consider tier-3 cuts

---

## Phase 7 — Cut-list (conditional, triggered by elapsed time, plan §8)

> Each task here has a trigger condition. Do NOT execute unless the trigger fires. All are `P3` because they are remediation, not deliverables.

### Tier 1 — fires at T-24h slip

- [ ] T701 [P3] [US7] Revert/skip US7 spacebar PTT (mark PR delta as out-of-scope; mic button only)
  - Cast: Parker · Tier: S · Priority: P3 · Trigger: T-24h with merge train not past slot 9 · Wall-clock: 10 min
- [ ] T702 [P3] [US8] Revert/skip US8 user-side transcription
  - Cast: Wanda · Tier: S · Priority: P3 · Trigger: same as T701 · Wall-clock: 10 min
- [ ] T703 [P3] [US6] (RouteMap stays in unless T-12h fires — see T705)

### Tier 2 — fires at T-12h slip

- [ ] T704 [P3] [US5] Drop `--full` smoke (keep checks 1–4 only); update plan §5 cadence note
  - Cast: Okoye · Tier: S · Priority: P3 · Trigger: T-12h with merge train incomplete · Wall-clock: 10 min
- [ ] T705 [P3] [US6] Cut RouteMap — leave `feat/route-map` open as draft; demo without it; revert any App.tsx import/JSX hunk if already merged
  - Cast: Parker + T'Challa · Tier: M · Priority: P3 · Trigger: T-12h AND T505 incomplete · Wall-clock: 20 min
- [ ] T706 [P3] [US3] Drop Dockerfile HEALTHCHECKs on internal services (keep frontend + orchestrator)
  - Cast: Stark · Tier: S · Priority: P3 · Trigger: T-12h with hygiene PR conflicts · Wall-clock: 10 min
- [ ] T707 [P3] [US2] Shrink demo script to 4 prompts (drop 5 & 6: alternate route, shuttle bridging); update T601–T604 expected pass criteria
  - Cast: Sean · Tier: S · Priority: P3 · Trigger: T-12h AND #27 unstable · Wall-clock: 5 min

### Tier 3 — fires at T-6h slip (also: build freeze)

- [ ] T708 [P3] [US2] Revert PR #27 entirely; demo log-analyst only (prompts 1–3)
  - Cast: Okoye · Tier: **L** (revert touches azure.yaml) · Priority: P3 · Trigger: T-6h with prompts 4–6 still failing · Wall-clock: 30 min
- [ ] T709 [P3] [US2] Switch demo to text-only via `/api/turn` (voice off-stage)
  - Cast: Sean · Tier: S · Priority: P3 · Trigger: T-6h with voice unreliable · Wall-clock: 5 min (presenter script change)
- [ ] T710 [P3] [US3] Disable `postdeploy` hook (keep manual smoke as fallback) — only if the hook itself is broken
  - Cast: Okoye · Tier: M · Priority: P3 · Trigger: T-6h with postdeploy itself flaking · Wall-clock: 10 min

**Hard floors (cannot be cut, per plan §8)**: `scripts/smoke-test` existence (T101/T102), main-only deploy guard (T107), eval gates green (FR-018), mock-data discipline (FR-007/SC-010).

---

## Dependencies (high-level graph)

```
Phase 0 (T001..T007)         [pre-train, parallelizable]
        │
        ▼
Phase 1 (T101..T110)         [slot 0: hygiene]   ← C-PRE checkpoint
        │
        ▼
Phase 2 (T201..T204S)        [slot 1: #28 docs]
        │
        ▼
Phase 3 slots 2..9           [interleaved chains, strictly serial per slot]
  T301..T305S  → T311..T315S → T321..T325S → T331..T335S
   → T341..T345S → T351..T355S → T361..T365S → T371..T375S
        │
        ▼                       ← C-FE checkpoint, Session B releases slot
Phase 4 (T401..T409S)        [slot 10: #27 service-advisor]
        │
        ▼                       ← C-SA checkpoint, Session A releases slot
Phase 5 (T501..T506S)        [slot 11: feat/route-map, Session B owns]
        │
        ▼                       ← C-RM checkpoint
Phase 6 (T601..T604)         [dry runs Mon EOD + 3× Tue morning]
        │
        ▼
Phase 7 (T7xx)               [conditional cut-list, triggered]
```

Cross-session checkpoints (T401, T501, T503) sit on the critical path and serialize the two sessions at chain boundaries.

---

## Parallel execution opportunities

**Within Phase 0** (all parallelizable, no inter-deps except T002 ← T001): T001 ‖ T003 ‖ T004 ‖ T005 ‖ T006 ‖ T007 — 6 agents could finish Phase 0 in ~30 min wall-clock instead of ~3.5h serial.

**Within Phase 1 slot 0**: T101 ‖ T102 ‖ T104 ‖ T105 ‖ T106 ‖ T107 (T103 depends on T101+T102+T004). 5 agents could collapse slot 0 from ~5h to ~1.5h wall-clock.

**Across Phase 3 slots**: Slots cannot parallelize across the boundary (each smoke gate is a hard barrier per FR-015). However, *within* a slot, rebase (T3x1) + local verify (T3x2) can overlap by ~5 min if rebase is clean. Anvil review (T3x3) is always serial.

**Across Phase 4 ‖ Phase 3 final**: T402 (clean `azd up` for #27) can start the moment T375S smoke passes — it doesn't need #27 merged, just the branch checked out in an ephemeral env. This buys ~60 min of clock back if Sean has a spare azd env quota.

**Phase 5 ‖ Phase 6 prep**: While Session B works T502, Session A can stage the rehearsal environment for T601 (pre-grant mic per R8, capture baseline `/api/health` JSON, prep video recording).

---

## Ambiguities flagged for Sean (not blocking, but please review)

1. **Session B identity / responsiveness.** T006 assumes Session B exists and reads `.squad/decisions.md`. If Session B is silent for >2h on a handoff (T501), Session A should escalate to Sean rather than block the train. T'Challa decides escalation threshold.
2. **Cassette authorship effort (T007).** If service-advisor prompts 4–6 lack cassettes today, T007 jumps from 30 min to ~2h and may push Phase 1 past T-48h. If that happens, recommend running `eval.yml` with a temporary skip on prompts 4–6 (Banner sign-off required) and authoring cassettes in parallel with Phase 3.
3. **`azd up` clean test (T402) needs an ephemeral env.** Plan §7 R2 calls for it; if quota or time forbids, drop T402 and accept the risk that #27's Bicep gaps surface only at merge time. Marked P0 here; downgrade to P1 if necessary.
4. **`workflow_dispatch` override on T107** — the plan says "require an explicit override flag." This list interprets that as an input `confirm_non_main: bool` plus `::warning::`. If Sean wants stricter (e.g. only Sean's GH login can trigger override), flag it and T107 becomes Medium effort.
5. **Demo prompt 6 cassette + tool wiring** — plan implicitly assumes `get_shuttle_bridging` is registered; verify in T312 / T352 or earlier. If missing, add to T007 scope.
6. **Smoke `--full` test data** — the 6 rehearsed prompts must produce deterministic citations for `--full` smoke to be useful. If responses vary (LLM nondeterminism), `--full` becomes flaky; consider lowering `--full` to "tool fires, ≥1 citation" rather than "exact output match." T101 should code defensively.
7. **RouteMap demo beat** — plan §10 Q10 asks whether RouteMap gets its own prompt; tasks assume passive (no new prompt, rides under 4+5). If Sean wants a dedicated beat, add T605 to extend dry-run scripts.

---

## Readiness for Squad dispatch

- ✅ Every task has a single named cast member (no "team owns").
- ✅ Every task has an Anvil tier consistent with plan §9.
- ✅ Every task has explicit deps by Task ID — Squad can topological-sort and dispatch.
- ✅ Smoke gates are first-class tasks (T110, T204S, T305S, T315S, T325S, T335S, T345S, T355S, T365S, T375S, T409S, T506S) — Squad routing can enforce them as required gates between merges.
- ✅ Cross-session checkpoints (T401, T501, T503) are explicit and reference `.squad/decisions.md` as the coordination surface.
- ✅ Cut-list tasks are pre-loaded with trigger conditions — Squad can fire them automatically on time-based events (T-24h, T-12h, T-6h) if hooked up to the deadline timer.
- ⚠ Session B tasks (T502) live outside Squad's dispatch surface; Session A escalates if Session B misses a handoff window.
- ⚠ T007 and T402 may need scope adjustment after Phase 0 reveals true effort — re-estimate at C-PRE checkpoint.

**Total task count**: 90
**Breakdown by priority**: P0 = 71 · P1 = 9 · P3 = 10
**Breakdown by tier**: Large = 14 · Medium = 31 · Small = 45
**Breakdown by phase**: Phase 0 = 7 · Phase 1 = 10 · Phase 2 = 4 · Phase 3 = 40 (8 slots × 5 beats) · Phase 4 = 9 · Phase 5 = 6 · Phase 6 = 4 · Phase 7 = 10
