# Stark — agent history

Tony Stark / Iron Man — Architect. Bench-to-active for the MTA AI Hackathon judging app.

## 2026-05-13 — Judging API + infra v0.1

**Task:** Stand up Azure infra (Bicep) and SWA managed Functions backend for the hackathon judging scorecard. Sibling to (not entangled with) the existing Container Apps stack at the repo root.

**Decisions:**
- Scoped the entire workload to `apps/judging/` to avoid colliding with the unrelated root `azure.yaml` / `infra/main.bicep` / `apps/log_analyst|orchestrator|frontend` stack.
- Single source of truth for scoring criteria: `apps/judging/shared/criteria.js`. CommonJS-and-globals dual export so the same file can be `require`d by Functions and `<script>`-tagged by the frontend without a build step.
- Cosmos DB **serverless**, single region East US 2, partition key `/track` on every container (`teams`, `scores`, `events`). Keeps query plans simple and lets us scope reads by partition for free.
- Score doc id = `${judgeEmail}|${teamId}` so a judge submitting again just upserts — no duplicate score docs.
- Lock state is a **special event doc** at id `lock-status-${track}` (upsert). Avoids adding a fourth container just for one flag, while still preserving the audit trail (a second random-UUID event row is appended on every toggle).
- `score-submit` is authoritative on totals — computes server-side via `computeTotal` and rejects unknown criteria keys (defense against payload tampering).
- SWA auth is enforced at the platform via `staticwebapp.config.json`; Functions are `authLevel: anonymous` and read `x-ms-client-principal`. Admin = SWA `admin` role **OR** email in `ADMIN_EMAILS` env. Two-path admin lets us bootstrap before the SWA role grants are wired.
- Same route, different methods (`GET /api/teams` and `POST /api/teams`) sit in **two separate function folders** with disjoint `methods` arrays — SWA managed Functions allow this. Fallback documented in README in case the deploy surface rejects it.

**Open issues handed to Okoye (DevOps):**
- Tenant GUID placeholder in `staticwebapp.config.json` (`{{TODO_TENANT_GUID}}`).
- AAD app registration + `AAD_CLIENT_ID`/`AAD_CLIENT_SECRET` SWA settings.
- Choice of azd flow: nested `azure.yaml` under `apps/judging/` would conflict if azd is run from repo root, so recommended a dedicated GH Actions workflow that targets `apps/judging/infra/main.bicep` directly.

**Things I'd revisit:**
- Switch Cosmos to AAD/`disableLocalAuth: true` with a managed identity once we know how SWA Functions will be granted RBAC (currently SWA managed Functions can't easily use a user-assigned MI for Cosmos data-plane).
- Add a `judges` container if we ever need per-judge metadata beyond the principal claims.
- Tie-breaker logic is single-criterion; if rules evolve to multi-criterion tie-breakers, generalize `tieBreakerId` → list.

## 2026-05-13 — Security Review (Strange)

Strange completed a security review of the judging app and authored `apps/judging/SECURITY_REVIEW.md`. Verdict: 🟡 Ship after must-fix items. 2 critical findings (CSV formula injection in export, unfilled tenant GUID placeholder) and 4 high findings. Core auth/authz model is solid. See decision D-007 and the full report for details and remediation paths.

## 2026-05-15 — Lab Dry-Run Runbook

**Task:** Produce a phased runbook for Brady to walk all 9 hackathon exercises end-to-end before the customer handoff on **Tuesday 2026-05-19**.

**Deliverable:** `.squad/files/lab-dry-run-runbook.md` — 5-phase runbook (Pre-flight → Provision → Smoke verify → Full eval/test gates LIVE → Walk exercises) plus teardown guidance, customer-handoff acceptance checklist, and 11 identified risks.

**Key decisions:**
- Region `eastus2` (all services GA there; `gpt-realtime-1.5` uses `GlobalStandard` so region is billing anchor only).

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up
- EX-01 (Add Health Analyst) selected as the one exercise to fully implement — simplest standalone service, validates the create-service → register-tool → test loop.
- EX-02–EX-09 verified in scaffolding mode only: tests should fail with clear assertion messages, not import errors or infra crashes.
- EX-05 depends on EX-04; all others are independent.
- **Phase 2.5 added:** Full live eval gates (citation, orchestrator, Foundry evaluators, red team) against deployed ACA stack. Any yellow blocks handoff.
- **P0 rule:** Any exercise where failing tests aren't cleanly reachable (ERROR instead of FAILED/SKIPPED) is a P0 fix before Tuesday.
- Idle cost ~$10–18/day; keep running through hackathon (~$75–90 total), teardown after 2026-05-20.
- Customer-handoff acceptance checklist covers: exercise scaffolding, codebase hygiene (no stale model refs), PR state, docs accuracy, cost documentation, and live verification.

**Risks flagged (11):** gpt-realtime-1.5 quota, RBAC propagation delay, ACR latency, vite.config.ts (fixed via PR #3), EX-07 vitest JSX, import path assumptions, Python path, corpus-version comment, P0 unreachable tests, pyyaml dependency for EX-06/08, and AOAI token quota for live evals.

## Learnings

- 2026-05-13 — Shipped API-surface security fixes from Strange's review (C1 CSV formula injection, H4 100KB request body cap in host.json, M1 leaderboard gated to admin OR locked track, M2 lock route GET handler for status reads). No shared `isTrackLocked` helper existed — inlined the same pattern from `score-submit/index.js` into leaderboard and lock to stay surgical; worth promoting to `_shared/` next time the lock doc is touched. Tenant GUID placeholder (C2) and `staticwebapp.config.json` / `infra/main.bicep` items remain Okoye's lane. Commit `7f6b670` on `main`.

- 2026-05-15 — Noted Bicep pattern deployed for **Foundry Realtime GA endpoint** (Decision D-009). Deployment resource `gpt-realtime-1.5` (version `gpt-realtime-1.5-2026-02-23`) targets new GA `/openai/v1/realtime?model={deployment}` endpoint (no api-version param, unlike preview). Orchestrator WebSocket client updated. Pattern documented in `infra/modules/foundry.bicep`. See D-009 for full details.

- 2026-05-15 — **Spec Kit v0.8.10 artifacts authored.** Layout: `.specify/memory/constitution.md` (v1.0.0) + `specs/001-realtime-1-5-upgrade/{spec,plan,tasks}.md`. `create-new-feature.ps1` works but creates a git branch — scaffolded by hand to stay on `main`. Constitution has 6 principles: Citations (NON-NEG), Mock Data (NON-NEG), Hermetic Tests, Keyless Auth, Voice Abstraction, Extensions-as-Exercises. Pitfall: the `.github/prompts/speckit.*.prompt.md` files are agent frontmatter stubs, not workflow docs — the real structure is in `.specify/templates/`.

## 2026-05-16 — T104 HEALTHCHECK directives shipped (Phase 1 deploy-hygiene batch)

**Task:** T104 (Medium) — Add `HEALTHCHECK` directives to `apps/orchestrator/Dockerfile` and `apps/log_analyst/Dockerfile` per FR-012.

**Status:** ✅ Complete. Branch: `chore/deploy-hygiene` (not committed; file-only).

**Deliverable:**
- **apps/orchestrator/Dockerfile:** curl installed in runtime stage; HEALTHCHECK probes `http://localhost:8000/health` (canonical per audit T001, not `/healthz`). Every 30s, 5s timeout, 20s start period, 3 retries.
- **apps/log_analyst/Dockerfile:** Replaced pre-existing python-urllib HEALTHCHECK with curl-based directive; same params except start period 20s (was 10s). Port 8001; ENV PORT=8001.

Both use `${PORT:-<default>}` shell expansion. curl adds ~3–5 MB to each image (acceptable for demo).

**Verification:** Static syntax check passing. Docker daemon not running locally (Docker Desktop not on Windows environment), so build verification deferred to CI deploy.yml + ACA container probes at runtime.

**Notes:**
- service_advisor HEALTHCHECK: intentionally out of scope per audit T003. Will be checkpoint on PR #27.
- No git operations performed per task constraints.

**Decision:** D-030.
