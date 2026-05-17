# Feature Specification: Crosstown Transit AI Assistant — Tuesday Customer Demo

**Feature Branch**: `002-tuesday-demo`
**Created**: 2026-05-16
**Demo Date**: 2026-05-19 (Tuesday)
**Owner**: Sean (msftsean / segayle)
**Status**: Draft
**Input**: 62-hour stabilization push to deliver a customer-facing voice+text demo of the Crosstown (fictional MTA) rider assistant. Driven by burnout-inducing regression cycle across ~28 PRs / ~17 bugs over the last 48 hours, and by Anvil's `docs/47doors-comparison.md` analysis identifying three deploy-hygiene gaps (`smoke-test.sh`, `postdeploy` health gate, Dockerfile `HEALTHCHECK`) that would have prevented this entire bug class.

---

## Context and Problem Statement

The repo has a working voice → orchestrator → specialist → cited-reply architecture (Hour-1 skeleton plus the service-advisor specialist landed in PR #27). It also has 11 open PRs that each fix a real bug, but they step on each other on `main` and during deploy. Symptoms experienced repeatedly in the last 48 hours:

- "Hello World" ACA quickstart placeholder served instead of our frontend image.
- `/api/health` returning 404 on the live deploy.
- Text input regressing three times (PRs #19/#21/#23/#25 chain dropped on a feature-branch deploy).
- `service-advisor` not registered in `azure.yaml` on `main`, so its tools fail to route.
- New fixes shipped from a feature branch silently roll back earlier merges.

Sean's bandwidth is the bottleneck. The customer demo is 62 hours out. The risk is **not** "we can't build the features" — they are built. The risk is "we can't ship the features that already exist, with confidence, without something regressing between now and Tuesday."

This spec defines what "demo-ready" means, what is in/out of scope for Tuesday, and the non-negotiable deploy-hygiene gates that must be in place before any further work.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Customer opens the live URL and asks one voice question (Priority: P1)

A customer visits the deployed frontend URL. The chat interface loads (no Hello World placeholder, no console errors visible to a non-developer). They hold the mic button (or spacebar), speak one of the rehearsed demo prompts, release, and see their transcribed turn plus a cited assistant response within a few seconds.

**Why this priority**: This is the headline moment. If this single flow does not work, the demo has failed regardless of everything else. It exercises every architectural seam: frontend bundle, nginx proxy, orchestrator WebSocket, voice provider, tool dispatch, specialist call, citation, render.

**Independent Test**: From a clean browser session, navigate to the deployed frontend URL. Confirm the chat interface (not Hello World) renders. Hold spacebar, say "Show me the most recent door-fault logs from station Atlantic," release. Within 10 seconds, observe (a) user turn rendered with the spoken text, (b) assistant turn rendered with response text, (c) at least one citation (log ID, runbook ID, or incident ID) visible in the response or in the ToolCallPanel, (d) no red console errors in DevTools.

**Acceptance Scenarios**:

1. **Given** the deployed frontend URL, **When** a customer loads the page in a fresh browser, **Then** the chat interface renders, `/api/health` returns 200, and no Hello World placeholder appears.
2. **Given** the chat interface is loaded, **When** the customer holds the mic (button or spacebar) and says "Show me the most recent door-fault logs from station Atlantic," **Then** within 10 seconds the user's transcribed turn and a cited assistant response are both visible, and the `search_logs` tool call is recorded.
3. **Given** the same loaded page, **When** the customer instead types "Is the L1 line running right now?" and submits, **Then** the assistant responds with a cited disruption status and the `DisruptionBanner` renders an L1 red-pill indicator.

---

### User Story 2 — Customer walks through the full rehearsed demo script (Priority: P1)

The customer (or Sean presenting to the customer) runs through six rehearsed prompts that exercise both specialists end-to-end. Every prompt produces a cited response and triggers the expected tool. The two service-advisor UI components (`DisruptionBanner`, `AlternateRouteCard`) render when their backing tools fire.

**Why this priority**: A single working turn proves the architecture, but a customer demo requires a coherent multi-turn narrative. This story is what Sean will actually walk a customer through on Tuesday. It also proves that both specialists are reachable and that the multi-specialist tool registry is functional.

**Independent Test**: Run the six prompts below in order against the deployed URL. Every response must contain ≥1 citation. The expected tool must fire for each. The DisruptionBanner must show L1 red after prompt 4. The AlternateRouteCard must render after prompt 5.

**Demo prompts and expected behavior:**

| # | Prompt | Expected tool | Expected UI |
|---|---|---|---|
| 1 | "Show me the most recent door-fault logs from station Atlantic" | `search_logs` | ToolCallPanel shows tool call; ≥1 log citation |
| 2 | "Look at log L-001234 — is it part of a known pattern?" | `detect_pattern` | ToolCallPanel; citation includes log ID |
| 3 | "Summarize incident INC-1001" | `summarize_incident` | ToolCallPanel; incident citation |
| 4 | "Is the L1 line running right now?" | `get_disruption_status` | DisruptionBanner (red pill on L1) |
| 5 | "S-Penn to S-East with the L1 disruption" | `find_alternate_route` | AlternateRouteCard |
| 6 | "Are there shuttle buses for L1?" | `get_shuttle_bridging` | ToolCallPanel; shuttle details cited |

**Acceptance Scenarios**:

1. **Given** the deployed app, **When** all six prompts are submitted in order, **Then** all six produce cited responses, all six correct tools fire, and the DisruptionBanner and AlternateRouteCard render at prompts 4 and 5 respectively.
2. **Given** any single prompt from the table, **When** it is submitted, **Then** the response contains at least one citation token (log/runbook/incident ID) and the `warnings` field does not contain `"uncited"`.

---

### User Story 3 — Sean (or anyone) re-deploys from `main` and the deploy fails loud, not silent, on regressions (Priority: P1)

Sean (or CI on a push to `main`) runs `azd deploy`. After the containers are pushed, an automated post-deploy step curls `/api/health` on the live frontend URL. If it returns anything other than 200, the deploy step exits non-zero and the regression is visible immediately — not 20 minutes later when someone tries to use the app. The same check can be run locally before declaring a deploy good.

**Why this priority**: This is the single highest-leverage change identified by the 47doors comparison. It eliminates the entire class of regressions (Hello World placeholder, frontend rollback, missing route) that have consumed the last 48 hours. Without it, even a perfect demo build can silently break between merge and demo time.

**Independent Test**: Run `scripts/smoke-test.sh <frontend-url>` from a developer laptop. With a healthy deploy it exits 0 and prints a success line. With a broken deploy (simulate by pointing at a Hello World ACA app) it exits non-zero with a clear error message naming the failing check. Trigger a CI deploy; observe that the `postdeploy` hook runs and fails the workflow visibly on a non-200 `/api/health`.

**Acceptance Scenarios**:

1. **Given** a healthy deploy, **When** `scripts/smoke-test.sh <url>` is run, **Then** it exits 0 within 30 seconds and prints which checks passed.
2. **Given** a deploy where the frontend container is serving the Hello World placeholder, **When** the `azure.yaml` `postdeploy` hook runs, **Then** it exits non-zero and the deploy is marked failed.
3. **Given** any service container (orchestrator, log-analyst, service-advisor, frontend), **When** the container starts but its `/api/health` (or equivalent) does not return 200, **Then** the Dockerfile `HEALTHCHECK` marks the container unhealthy and ACA does not route traffic to it.

---

### User Story 4 — Sean (or CI) deploys ONLY from `main`, never from a feature branch (Priority: P1)

Every container image deployed to the customer-facing environment is built from the `main` branch at a tagged commit. Feature branches may run CI and may be deployed to ephemeral preview environments, but the customer URL only ever serves an image built from `main`. The deploy workflow refuses (or visibly warns) when invoked from a non-`main` ref.

**Why this priority**: The frontend rollback regression (PRs #19/#21/#23/#25 disappearing) was caused by an image built from a feature branch that did not include those merges. The fix is procedural and tool-enforced, not architectural. Until this is in place, every deploy is a fresh opportunity to lose work.

**Independent Test**: Attempt to trigger the production deploy workflow from a non-`main` branch. The workflow must refuse to run or must produce a loud warning that the deploy is not from `main`. Inspect the most recent customer-facing deploy: the image tag must trace back to a commit that exists on `main`.

**Acceptance Scenarios**:

1. **Given** the production deploy workflow, **When** it is invoked from any ref other than `main`, **Then** it either refuses to deploy or requires an explicit override flag and logs a warning.
2. **Given** any image running in the customer-facing environment, **When** its source commit is looked up, **Then** that commit is reachable from `main`.

---

### User Story 5 — The PR backlog is merged in a defined order before any new feature work (Priority: P1)

The 11 open PRs are resolved in dependency order onto `main`, with conflicts handled deliberately, before any new feature work is started. The merge order is sequenced so that frontend-chain PRs (#19, #21, #23, #25, #26) land in order, orchestrator-chain PRs (#20, #22, #24) land in order, and service-advisor (#27) lands last so `azure.yaml` reflects the full service mesh. After every merge, the smoke test from Story 3 runs.

**Why this priority**: The bugs that need to ship are already coded. The risk is in how they land. A defined sequence with smoke-test gates between merges is what converts existing work into a stable demo build.

**Independent Test**: At the end of the merge sequence, `git log main` shows all 11 PRs merged in the planned order. After each merge, the smoke test exit code is 0. No new commits were made to `main` outside of these PRs during the sequence.

**Acceptance Scenarios**:

1. **Given** the 11 open PRs, **When** they are merged following the documented sequence, **Then** each merge is followed by a passing smoke test before the next merge starts.
2. **Given** a merge conflict during the sequence, **When** it is encountered, **Then** the conflict is resolved by the agent that owns the later PR in the sequence (not the earlier), and the resolution is reviewed by Anvil before commit.

---

### User Story 6 — Both Copilot sessions working the repo coordinate via explicit branch rules (Priority: P2)

Sean is running two Copilot sessions (this one and a parallel session that has been working on RouteMap and the service-advisor feature drop). Both sessions follow explicit branch-coordination rules so they do not produce the kind of conflict that just happened: one session deploys from a branch missing the other's merges. Rules are documented in this spec and referenced by the plan.

**Why this priority**: Multi-agent / multi-session coordination is a known failure mode in this repo's recent history. Without explicit rules, a second well-meaning session can re-introduce a regression in minutes.

**Independent Test**: Inspect the branch-coordination section of this spec; confirm it states (a) only one session at a time may push to `main`, (b) feature branches must be rebased on `main` before merge, (c) any session that deploys must verify the deploy is from `main`, (d) handoff between sessions is logged in `.squad/decisions.md` or equivalent.

**Acceptance Scenarios**:

1. **Given** two active Copilot sessions, **When** either session opens a PR, **Then** the PR description references the branch-coordination rules and confirms the branch is rebased on `main`.
2. **Given** a handoff between sessions, **When** one session finishes a unit of work, **Then** the handoff is recorded with what was done, what is in flight, and what the next session should pick up.

---

### User Story 7 — Push-to-talk works via spacebar AND mic button (Priority: P3, stretch)

In addition to clicking the mic button, the customer can press and hold the spacebar to start speaking, and release to stop. Both input methods drive the same voice session lifecycle.

**Why this priority**: Stretch. Mic-button-only is sufficient for the demo. Spacebar is a nice presenter affordance.

**Independent Test**: With the chat interface focused (not a text input), press and hold spacebar — the mic activates and audio streams. Release — the voice turn completes. Repeat with the mic button — same behavior.

**Acceptance Scenarios**:

1. **Given** the chat interface is loaded and no text input is focused, **When** spacebar is held down, **Then** mic capture starts and visually indicates recording.
2. **Given** spacebar is being held, **When** it is released, **Then** mic capture stops and the voice turn is submitted.

---

### User Story 8 — User-side speech transcription is rendered alongside assistant turns (Priority: P3, stretch)

When a customer speaks, their transcribed words appear in the transcript as a user turn before the assistant response arrives, so the customer can confirm what was heard.

**Why this priority**: Stretch. Improves customer perception of the demo and is small if it works for free from the voice provider; non-trivial if it requires plumbing.

**Independent Test**: Speak a voice turn. Confirm a user-role turn appears in the transcript with the transcribed text within ~2 seconds of releasing the mic, and before the assistant response renders.

**Acceptance Scenarios**:

1. **Given** a voice turn in flight, **When** the voice provider returns the user transcript, **Then** a user-role turn is rendered with that text before or alongside the assistant turn.

---

### Edge Cases

- **Voice provider returns no transcript** (silence, mic permission denied, network drop mid-utterance) → frontend shows a non-confusing message ("Didn't catch that — try again") and the session remains usable. Not an unhandled exception.
- **A tool call returns zero results** (e.g., `search_logs` with no matching station) → assistant responds with a cited "no results found" message; `warnings` does not contain `"uncited"` because the empty-result message is itself cited to the query.
- **`/api/health` is reachable but a backing service (Cosmos, AI Search) is down** → `/api/health` returns degraded status (still 200, but with a JSON body indicating which dependencies are down). Customer-visible behavior: assistant says it cannot reach the data right now, with no stack trace.
- **Customer asks an off-domain question** ("What's the weather?") → orchestrator declines gracefully per existing system prompt; redteam off-domain family covers this.
- **Customer asks about a real MTA line** ("Is the 4 train running?") → assistant redirects to the fictional L1/L2/L3 lines used in the demo; mock-data constitution principle remains intact.
- **Deploy succeeds but `service-advisor` is unreachable** (e.g., container failed to start) → orchestrator tool registry startup logs the missing specialist; service-advisor prompts (4–6 in the demo script) fail with a cited "service temporarily unavailable" message rather than silently producing wrong answers. Caught by smoke test before customer sees it.
- **Both Copilot sessions push to `main` near-simultaneously** → second push fails on non-fast-forward; the losing session rebases and re-runs smoke test before retrying.

---

## Requirements *(mandatory)*

### Functional Requirements — Demo capability

- **FR-001**: System MUST serve a working chat interface at the customer-facing frontend URL with no Hello World placeholder, no missing-image errors, and no red console errors visible to a non-developer.
- **FR-002**: Users MUST be able to submit a query either by holding the mic button (mouse, touch) OR by typing in a text input and submitting. Both paths MUST drive the same orchestrator tool-routing and citation contract.
- **FR-003**: System MUST render each turn (user input + assistant reply) in the transcript in arrival order. Assistant turns MUST display the response text and the citations.
- **FR-004**: System MUST route to all three log-analyst tools (`search_logs`, `detect_pattern`, `summarize_incident`) and all four service-advisor tools (`get_disruption_status`, `find_alternate_route`, `get_shuttle_bridging`, `recommend_commute_action`) from the orchestrator's unified tool registry.
- **FR-005**: System MUST render `DisruptionBanner` when `get_disruption_status` returns a non-clear status, and `AlternateRouteCard` when `find_alternate_route` returns a route.
- **FR-006**: Every assistant response surfaced to the customer MUST include at least one citation (log, runbook, or incident ID), and the orchestrator response MUST NOT carry `warnings: ["uncited"]` for any of the six rehearsed demo prompts.
- **FR-007**: System MUST keep all rail-line references fictional (L1, L2, L3). No real MTA lines, stations, employees, or telemetry may appear in any demo output.
- **FR-008**: System MUST respond to each of the six rehearsed demo prompts (User Story 2 table) by firing the listed tool and rendering the listed UI element.

### Functional Requirements — Deploy hygiene (the 47doors lessons)

- **FR-009**: Repo MUST contain `scripts/smoke-test.sh` (and an equivalent `.ps1` for Windows developers) that, at minimum, accepts a base URL argument and exits 0 only if `GET <url>/api/health` returns 200. The script MUST exit non-zero with a human-readable error on any failure and MUST complete within 30 seconds.
- **FR-010**: `azure.yaml` MUST define a `postdeploy` hook that runs the smoke test against the deployed frontend URL and fails the deploy step on non-zero exit.
- **FR-011**: Every service Dockerfile (`orchestrator`, `log_analyst`, `service_advisor`, `frontend`) MUST declare a `HEALTHCHECK` that curls its local health endpoint and exits non-zero on failure.
- **FR-012**: `azure.yaml` `services` block MUST include `service-advisor` so that `azd deploy` provisions and updates the service-advisor container app. (Currently missing on `main`; PR #27 lands this.)
- **FR-013**: The production deploy workflow MUST only build and deploy images from the `main` branch. Invocations from other refs MUST be refused or require an explicit override flag plus a loud warning.
- **FR-014**: `/api/health` MUST return 200 with a JSON body indicating service status, and MUST be reachable through the frontend nginx proxy at the same path on the public URL.

### Functional Requirements — Process

- **FR-015**: The 11 open PRs MUST be merged in a defined sequence documented in the plan (`/speckit.plan` output), with the smoke test from FR-009 passing after each merge before the next merge proceeds.
- **FR-016**: Branch-coordination rules between the two active Copilot sessions MUST be documented in this spec (see section "Branch coordination rules") and referenced in every PR description during the demo push.
- **FR-017**: Every code change merged between now and demo time MUST pass Anvil's verification + adversarial review before commit, with no exceptions.
- **FR-018**: All hermetic eval gates MUST be green on the demo build: citation gate ≤5% uncited, orchestrator gate 0% fail, redteam 0 high/critical.

### Non-Goals (out of scope for Tuesday)

- Do NOT add `RouteMap` UI component (move to v2).
- Do NOT add new specialists beyond log-analyst and service-advisor.
- Do NOT integrate any real MTA data sources.
- Do NOT add features beyond what is already in PRs #19–#27.
- Do NOT add `docker-compose.yml` for local full-stack dev (post-demo improvement).
- Do NOT write a `.squad/skills/azure-realtime-api-schema/SKILL.md` for the session.update bug (post-demo improvement).
- Do NOT tweak any calibration thresholds in `evals/calibration.json` to make a gate green — follow the recalibration protocol or do not merge.

### Key Entities

- **Demo Build**: The single tagged commit on `main` that the customer-facing URL is serving at demo time. Attributes: commit SHA, image tags per service, deploy timestamp, smoke-test result.
- **Demo Prompt**: One of the six rehearsed prompts (User Story 2). Attributes: prompt text, expected tool, expected UI element, last-known-good behavior.
- **Open PR**: One of the 11 PRs in the merge backlog. Attributes: PR number, chain (frontend / orchestrator / service-advisor), dependency on other PRs, merge order, last smoke-test result on its branch.
- **Health Endpoint**: `/api/health` on each service plus the proxy passthrough. Attributes: returns 200 + status JSON, exercised by smoke test and Dockerfile HEALTHCHECK.

---

## Branch coordination rules *(applies to both Copilot sessions and any human contributor)*

1. **`main` is the only deploy source.** No image deployed to the customer URL between now and demo may originate from a non-`main` ref.
2. **One pusher at a time.** Before pushing to `main`, the pushing session announces it in `.squad/decisions.md` (or the agreed coordination channel). Other sessions wait until the push lands and smoke test passes.
3. **Feature branches must be rebased on latest `main`** immediately before opening a PR. If main moved during the PR's review, rebase again before merge.
4. **Smoke test after every merge.** After any merge to `main`, run `scripts/smoke-test.sh <staging-or-prod-url>` and confirm exit 0 before the next merge starts.
5. **Conflicts are owned by the later PR.** When two PRs in the backlog conflict, the later one in the merge sequence (see plan) does the resolution, and Anvil reviews it.
6. **Handoffs are logged.** When a session finishes a unit of work or hands off to another session, an entry goes into `.squad/decisions.md` stating: what was done, what is in flight (branch + PR number), what to pick up next, what the smoke-test status is.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On demo day, a customer loading the deployed frontend URL sees the chat interface (not the Hello World placeholder) within 5 seconds of page load, with `/api/health` returning 200.
- **SC-002**: All six rehearsed demo prompts (User Story 2 table) produce cited responses on the live deploy with 100% success across three back-to-back rehearsal runs the morning of the demo.
- **SC-003**: 0 uncited customer-visible turns during the demo (citation contract holds end-to-end on the live build).
- **SC-004**: From the moment a regression is introduced into a deploy, it is detected automatically within 60 seconds (post-deploy smoke test exit code) — not 20+ minutes later by a human noticing Hello World.
- **SC-005**: At the start of demo day, the count of regressions caused by deploying from a non-`main` branch since this spec was ratified is 0.
- **SC-006**: A new developer (or Sean from a clean machine) can clone the repo from `main` and run `azd up` end-to-end to a working, smoke-test-passing deploy in ≤45 minutes (cold start).
- **SC-007**: All hermetic eval gates on the demo build are green: citation gate ≤5% uncited, orchestrator gate 0% fail, redteam 0 high / 0 critical.
- **SC-008**: Between spec ratification and demo time, every PR merged to `main` has Anvil verification + adversarial review recorded in its description.
- **SC-009**: All 11 open PRs (#19–#27 inclusive) are either merged to `main` in the documented sequence or explicitly closed with a written reason before demo time.
- **SC-010**: Zero references to real MTA lines, stations, employees, or telemetry exist in any demo output (mock-data constitution principle holds).

---

## Assumptions

- The hardware Sean will demo from has a working microphone, modern Chromium-based browser, and reliable network at the demo location.
- The customer-facing URL is the existing ACA-hosted frontend (no new hostname or DNS work in scope).
- The Azure subscription, Foundry deployment (`gpt-realtime-1.5`), AI Search index, and Cosmos containers provisioned by `azd up` are intact and within quota for demo day.
- The voice provider remains `foundry_realtime` for the demo; Speech Services fallback is not exercised on stage.
- The 11 open PRs as a set, once merged, contain all the code-level changes needed for the six rehearsed demo prompts to work — no additional code-level features need to be authored.
- Anvil remains available as a verification + adversarial review gate throughout the 62-hour window.
- Both Copilot sessions can read this spec and the eventual plan/tasks; coordination is via shared repo state (`.squad/decisions.md`, PR descriptions), not real-time chat.
- "Hello World placeholder" specifically refers to the `mcr.microsoft.com/k8se/quickstart:latest` image; if a different placeholder surfaces, the smoke test still catches it via `/api/health` non-200.

---

## Out of Scope (explicit, for the avoidance of doubt)

- RouteMap UI component (and any new visualization of `route_graph.json`) — defer to v2.
- Any new specialist beyond log-analyst and service-advisor.
- Any real MTA data integration; lines stay `L1/L2/L3`, data stays under `data/`.
- Mobile-specific UX work; demo is desktop browser only.
- Multi-region / DR; demo is single-region.
- Authentication / multi-tenant; demo is anonymous customer view.
- Cost optimization, autoscaling beyond defaults, Postgres activation.
- Backfilling tests for code that already shipped without them (unless required by a CI gate).
- Adopting 47doors' `docker-compose.yml`, demo runbook component, or skill files — log as post-demo follow-ups.

---

## Dependencies

- **PR #27** (service-advisor) must land for FR-012 and demo prompts 4–6 to work.
- **PRs #19, #21, #23, #25, #26** (frontend chain) must land for FR-001/FR-002/FR-003 to hold on the live build.
- **PRs #20, #22, #24** (orchestrator chain) must land for FR-004/FR-006 to hold across both specialists.
- **`scripts/smoke-test.sh`** (FR-009) must land before FR-010 and FR-015 can be enforced.
- **`azure.yaml` `postdeploy` hook** (FR-010) depends on FR-009.
- **Dockerfile HEALTHCHECKs** (FR-011) are independent of the above and can land in parallel.
- **Anvil verification gate** (FR-017) depends on Anvil being available for every merge.

---

## Risks (acknowledged, not solved here — solve in plan)

- **R1**: The 11-PR merge sequence has unknown conflict surface. Estimated time may blow the 62-hour budget. — Plan must include a "what to cut" decision tree if conflicts compound.
- **R2**: `service-advisor` may have additional infra requirements not yet in Bicep. — Plan must verify `azd up` from a clean subscription before demo morning.
- **R3**: Voice provider availability on demo day is outside our control. — Plan must include a tested text-only fallback rehearsal.
- **R4**: A second Copilot session may not see this spec before pushing. — Sean to confirm session 2 has read this spec before any further `main` activity.
- **R5**: Sean is exhausted; further bug whack-a-mole will degrade decision quality. — Plan must front-load deploy hygiene (Stories 3+4) so subsequent merges are gated automatically and Sean is removed from the per-merge verification loop.
