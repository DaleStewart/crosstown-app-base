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

## Learnings

- 2026-05-13 — Shipped API-surface security fixes from Strange's review (C1 CSV formula injection, H4 100KB request body cap in host.json, M1 leaderboard gated to admin OR locked track, M2 lock route GET handler for status reads). No shared `isTrackLocked` helper existed — inlined the same pattern from `score-submit/index.js` into leaderboard and lock to stay surgical; worth promoting to `_shared/` next time the lock doc is touched. Tenant GUID placeholder (C2) and `staticwebapp.config.json` / `infra/main.bicep` items remain Okoye's lane. Commit `7f6b670` on `main`.

- 2026-05-15 — Noted Bicep pattern deployed for **Foundry Realtime GA endpoint** (Decision D-009). Deployment resource `gpt-realtime-1.5` (version `gpt-realtime-1.5-2026-02-23`) targets new GA `/openai/v1/realtime?model={deployment}` endpoint (no api-version param, unlike preview). Orchestrator WebSocket client updated. Pattern documented in `infra/modules/foundry.bicep`. See D-009 for full details.

- 2026-05-15 — **Spec Kit v0.8.10 artifacts authored.** Layout: `.specify/memory/constitution.md` (v1.0.0) + `specs/001-realtime-1-5-upgrade/{spec,plan,tasks}.md`. `create-new-feature.ps1` works but creates a git branch — scaffolded by hand to stay on `main`. Constitution has 6 principles: Citations (NON-NEG), Mock Data (NON-NEG), Hermetic Tests, Keyless Auth, Voice Abstraction, Extensions-as-Exercises. Pitfall: the `.github/prompts/speckit.*.prompt.md` files are agent frontmatter stubs, not workflow docs — the real structure is in `.specify/templates/`.

