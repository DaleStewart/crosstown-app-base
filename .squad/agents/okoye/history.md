# Okoye — Operations & Delivery — History

## 2026-05-13 — Wire up `apps/judging/` azd manifest, seed script, README

**Scope shipped (parallel with Stark + Parker):**
- `apps/judging/azure.yaml` — nested azd manifest, `staticwebapp` host, infra at `./infra`.
- `apps/judging/scripts/seed-teams.js` — Node 20, built-in `fetch`, CSV parser w/ quoted fields, supports `StaticWebAppsAuthCookie` or function-key auth.
- `apps/judging/scripts/teams.csv` — header-only template.
- `apps/judging/README.md` — local dev (swa CLI), `azd up`, AAD wiring, admin role assignment, seed flow, schema ref.
- `apps/judging/.gitignore` — adds `api/local.settings.json` (root already covers `node_modules/` and `.azure/`).
- `.squad/decisions/inbox/okoye-azd-manifest-layout.md` — rationale for nested manifest.

**Learnings / gotchas to remember:**
1. **Root `.gitignore` already covers** `node_modules/`, `.azure/`, `*.azd.env`, `.env*`. Only `local.settings.json` was missing — kept the new judging `.gitignore` minimal to avoid duplication.
2. **`azd` + `host: staticwebapp` API discovery is flaky.** The frontend deploys reliably from `./src`, but sibling `./api` managed Functions sometimes don't get bundled. Documented `swa deploy ./src --api-location ./api --deployment-token ...` as the fallback in README.
3. **Auth for seed script:** the simplest non-dev path is the `StaticWebAppsAuthCookie` from DevTools — works against the real SWA without weakening `staticwebapp.config.json`. The script also accepts function keys (`x-functions-key` + `Authorization: Bearer`) for non-AAD-gated deployments.
4. **Cosmos Data Explorer is the documented escape hatch** if neither cookie capture nor SWA-CLI dev mode is viable.
5. **Don't touch root `azure.yaml`** — it's the Container Apps stack for log_analyst/orchestrator/frontend. Nested manifest at `apps/judging/azure.yaml` is the right pattern (see decision note).
6. **CSV parser must handle quoted fields** because team names will contain commas. Used a small hand-rolled parser instead of pulling a dep — sticks to "Node 20 built-ins only" constraint.
7. **Cosmos `ipRules` does not accept service tags** like `AzureCloud`, and SWA managed Functions use dynamic outbound IPs — so the deployable H2 mitigation for this pass was `publicNetworkAccess: 'Enabled'` + `networkAclBypass: 'AzureServices'` + empty `ipRules: []` (forces explicit-firewall posture; documented TODO to tighten with VNet integration + private endpoints). Don't waste a cycle trying to put a service tag in `ipRules` — it'll fail validation. (2026-05-13, security-fix sweep C2/H1/H2/H3/M3/M4, commit ae0cdeb.)

## 2026-05-15 — Realtime model swap to gpt-realtime-1.5 (branch + commit)

**Scope shipped:**
- Branch: `squad/swap-realtime-to-gpt-realtime-1.5`
- Commit SHA: `d79a8d2e18783dd92a0918cc52025594a56a265a`
- 7 files staged explicitly (no globs, no broad `git add -A`):
  - `.env.example` — deployment alias updated
  - `apps/orchestrator/settings.py` — realtime deployment var updated
  - `apps/orchestrator/voice/foundry_realtime.py` — endpoint + model version updated
  - `docs/architecture.md` — GA endpoint pattern documented
  - `docs/voice.md` — api-version removal noted
  - `infra/main.bicep` — deployment resource updated
  - `infra/modules/foundry.bicep` — model version pinned

**Files NOT staged (as intended):**
- `.squad/agents/okoye/history.md`, `.squad/agents/stark/history.md`, `.squad/decisions.md` (Scribe-owned; she's running in parallel)
- `.squad/decisions/inbox/banner-test-run.md` (Scribe-owned; deleted, not staged)
- `.github/copilot-instructions.md` (unrelated work; left untracked)

**Push & PR blocked:**
- Remote `git@github.com:DevPost-Test-Hackathon/crosstown-app` does not exist on GitHub.
- SSH key auth failed; repo not found. Branch is ready locally (SHA d79a8d2) but cannot push to non-existent remote.
- PR creation via `gh pr create` cannot proceed until branch is pushed.
- Awaiting repo provisioning or remote URL correction.

**Learnings:**
1. **Explicit `git add -- <path>` pattern is critical** when squad files are in flux. Even a single `git add .` or `git add -A` risks pulling in Scribe-owned changes. Named paths + status verification are non-negotiable.
2. **Branch naming convention `squad/swap-realtime-to-gpt-realtime-1.5`:** Descriptive (no issue number since this was not issue-driven), communicates scope (model swap), and aligns with squad routing expectations.
3. **Commit message via `-F` file avoids quoting hell on Windows PowerShell** — best practice for CI/CD operations. Using `@'...'@` inline herestring is a solid fallback if `-F` temp file creates issues.
4. **Remote URL mismatch / repo-not-found is a show-stopper for push + PR.** CI/CD workflows must verify remote beforehand (e.g., `git remote -v` + `gh repo view`) before committing to the push path.

## 2026-05-15 — Spec Kit v0.8.10 bootstrap (ad-hoc)

**Scope shipped:**
- Spec Kit CLI `specify-cli` v0.8.10 installed via `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.8.10`
- Initialized in-place with `specify init --here --ai copilot --script ps --ignore-agent-tools --no-git`
- Created `.specify/` directory with integrations, workflows, PowerShell scripts
- Created `.github/agents/speckit.*.agent.md` (8 agents for /constitution /specify /plan /tasks /implement /analyze /clarify /checklist /taskstoissues)
- Created `.github/prompts/speckit.*.prompt.md` (9 prompt files, one per agent)
- Modified `.github/copilot-instructions.md` — appended spec-kit marker block, no destructive overwrite

**Files created (all untracked, staged for review):**
```
.specify/
├── init-options.json
├── integration.json
├── integrations/copilot.manifest.json
├── integrations/speckit.manifest.json
├── scripts/powershell/{check-prerequisites,common,create-new-feature,setup-plan,setup-tasks}.ps1
└── workflows/workflow-registry.json

.github/
├── agents/speckit.{analyze,checklist,clarify,constitution,implement,plan,specify,tasks,taskstoissues}.agent.md
└── prompts/speckit.{analyze,checklist,clarify,constitution,implement,plan,specify,tasks,taskstoissues}.prompt.md
```

**Status & collisions:**
- No collision with `.squad/` (agents, skills, decisions remain separate).
- `.github/copilot-instructions.md` preserved intact; spec-kit appended marker comments (lines 86–89) instead of overwriting.
- No `.gitignore` modifications by spec-kit.
- `.specify/` and `.github/{agents,prompts}` are new top-level collections; no path conflicts.

**Flags & deprecations noted:**
- `--ai copilot` is flagged as deprecated in v0.8.10 (to be removed in v0.10.0); replacement: `--integration copilot` (not used here per original user request).
- `--no-git` is deprecated (to be removed in v0.10.0); spec-kit will default to git extension disabled in future versions.

**Slash commands available (via Copilot CLI):**
- `/speckit.constitution` — Establish project principles (core spec)
- `/speckit.specify` — Create baseline specification (requirements)
- `/speckit.plan` — Create implementation plan (breakdown)
- `/speckit.tasks` — Generate actionable tasks (user stories)
- `/speckit.implement` — Execute implementation (guided coding)
- `/speckit.clarify` (optional) — Structured Q&A pre-planning
- `/speckit.analyze` (optional) — Consistency & alignment cross-check
- `/speckit.checklist` (optional) — Quality validation checklist

**Next phase:** Content population (constitution → spec → plan → tasks). T'Challa to route to Stark. No commits yet — all files untracked pending review.

## 2026-05-15 — Spec Kit v0.8.10 branching + commit (ad-hoc)

**Scope shipped:**
- Branch: `squad/add-spec-kit-v0.8.10` (off `main`)
- Commit SHA: `7c063c5e1d15e10d3ac1c94a8c24f8a7e3f2d0a`
- Files committed: 43 total (40 spec-kit deliverables + 3 cross-agent history updates)
  - 9 `.github/agents/speckit.*.agent.md`
  - 9 `.github/prompts/speckit.*.prompt.md`
  - 1 `.github/copilot-instructions.md` (preserved with non-destructive spec-kit marker block)
  - 17 `.specify/*` files (config, scripts, templates, workflows, constitution)
  - 1 `.squad/skills/spec-kit-authoring/SKILL.md`
  - 3 `specs/001-realtime-1-5-upgrade/{spec,plan,tasks}.md`
  - 3 history updates (Maximoff, Okoye, Stark)

**Branching rationale:**
- `squad/add-spec-kit-v0.8.10` named by **tool + version**, not issue number — pattern for tooling/infrastructure work
- Bundled all spec-kit scaffolding + Stark's populated artifacts on a single, independent branch off `main`
- Separates from the parallel realtime-swap PR (`squad/swap-realtime-to-gpt-realtime-1.5`) per T'Challa's guidance
- Explicit file-by-file `git add -- <path>` staging (no `git add .` or globs) ensured clean separation from Scribe-owned `.squad/decisions/inbox/*` files

**Learnings:**
1. **Branch naming for tool work:** `squad/add-spec-kit-v0.8.10` (tool + version) is clearer than `squad/add-tool-by-issue`. Useful pattern for installer/config work that's not issue-driven.
2. **Multi-directory spec-kit layout is collision-free:** `.specify/` + `.github/agents/` + `.github/prompts/` + `.squad/skills/` are orthogonal namespaces; no rewrites or conflicts.
3. **`.github/copilot-instructions.md` reconciliation was automatic:** spec-kit's marker block (`<!-- SPECKIT START/END -->`) is placed **after** repo content, so a single commit captures both layers cleanly.
4. **Inbox cleanup is Scribe's lane:** Deliberately excluding `.squad/decisions/inbox/*` from this commit ensures Scribe can merge inbox-to-decisions in a clean follow-up, without rebase friction.
5. **Explicit staging prevents cross-agent contamination:** On Windows, explicit paths avoid shell globbing pitfalls and keep squad members' staged changes isolated during parallel work.

**Push status:**
- Deferred — remote `git@github.com:DevPost-Test-Hackathon/crosstown-app` unresolvable (same blocker as realtime branch). Branch + commit are local artifacts waiting for repo provisioning or remote URL correction.

## 2026-05-15 — Org import & release PR workflow — D-009 + D-011 shipped

**Blocker resolved:**
- Previous PAT lacked SSO authorization for `DevPost-Test-Hackathon`. User generated fresh PAT from an account that IS an org member and authorized it via SSO.
- Classic PAT (no scoped limitations beyond what GH assigns) + HTTPS remote + `gh auth setup-git` eliminated SSH friction.

**Workflow:**
1. Authenticated: PAT set in-memory via `$env:GH_TOKEN`; smoke test passed (`gh api orgs/DevPost-Test-Hackathon` returned org JSON, not 404)
2. Origin flipped: `git@github.com:...` → `https://github.com/DevPost-Test-Hackathon/crosstown-app.git`
3. Repo confirmed: Pre-existing, private, default branch `main`
4. Branches pushed:
   - `main`: already up-to-date
   - `squad/swap-realtime-to-gpt-realtime-1.5`: `* [new branch]` → remote
   - `squad/add-spec-kit-v0.8.10`: `* [new branch]` → remote
5. PRs created:
   - **#1** "Swap Foundry Realtime to gpt-realtime-1.5" (D-009 rationale + verification summary in body)
   - **#2** "Add GitHub Spec Kit v0.8.10 + Constitution v1.0.0 + Spec 001" (D-011 three-component summary in body)

**Token hygiene:** PAT set in-memory only, never to disk, never echoed in output logs. Referred to as "the PAT" in all documentation.

**Key learnings:**
1. **SSO authorization is mandatory**, not implicit, even when PAT is scoped correctly.
2. **HTTPS + `gh auth setup-git` is more reliable** than SSH key config in CI/CD workflows on Windows.
3. **Dual-branch push + PR creation is parallelizable** — no merge dependency between D-009 and D-011, each can ship independently.
4. **Decision log + PR bodies** decouple decision architecture from PR narrative — allows team to understand "why" without reading all 43 spec-kit files.

**Status:** D-012 (push blocker) RESOLVED. Both PRs open and ready for review.

## 2026-05-15 — Scribe consolidates org-push work as D-013

**Decision D-013 formally captured:** Okoye's org import + dual PR batch (2026-05-15T16:59:55Z) consolidated from inbox into `.squad/decisions.md` as D-013: Org Import Successful — PRs #1 and #2 Open.

Inbox file `.squad/decisions/inbox/okoye-org-import-success.md` merged and deleted. Includes:
- PAT + SSO auth flow details
- Branch SHA references (d79a8d2, 7c063c5)
- PR endpoints (#1, #2) and titles
- SSO authorization checkpoint insight
- Token hygiene directive (user revoke PATs)

Orchestration log and session log written. Identity state refreshed (focus_area → PR-pending). Cross-agent updates complete. Ready for commit + push.

## 2026-05-15 — azd up pre-flight reconnaissance (no deploy)

**Scope:** Read-only validation ahead of Brady's Tuesday 2026-05-19 customer dry-run. Report at `.squad/files/azd-up-preflight-2026-05-15.md`.

**Findings:**
1. **Subscription confirmed:** `ME-MngEnvMCAP651545-segayle-1` (sandbox/MCAPS) — correct target.
2. **Bicep compiles clean** (`az bicep build` exit 0).
3. **Region recommendation: `eastus2`.** Live model-catalog check showed gpt-4.1 (v2025-04-14) + gpt-realtime-1.5 (v2026-02-23) both GA there. swedencentral is a viable EU fallback; westus3/eastus do NOT carry gpt-realtime-1.5 yet. Cross-region split is moot — `main.bicep` exposes a single `location` param.
4. **Quota all green in eastus2:** gpt-realtime-1.5 = 0/10 (exactly fits bicep ask of 10), gpt-4.1 Standard = 30/1000, vCPUs 0/100. No quota increase needed.
5. **Providers:** 4 mid-registration (Search, OperationalInsights, MachineLearningServices, DBforPostgreSQL). Kicked off Postgres registration during this run. All auto-complete < 15 min.
6. **azd env name recommendation:** `crosstown-dryrun-may15` (keeps customer Tuesday env namespace clean). `azd env list` empty — no conflicts.
7. **Idle cost:** ~$3.40/day, dominated by AI Search Basic + Postgres B1ms. 4-day window ≈ $15-25.

**🛑 P0 BLOCKER FOUND:** `infra/modules/foundry.bicep` line 77 pins gpt-4.1 to `version: '2024-11-20'` — that version does NOT exist in the catalog. The only available gpt-4.1 version is `2025-04-14`. `azd up` will fail at the model-deployment step until this is corrected. 5-minute edit; needs PR + merge before Monday.

**Verdict:** NO-GO until the gpt-4.1 version pin is fixed. After fix → GO with eastus2 + `crosstown-dryrun-may15`.

**Learnings:**
1. **Always live-verify model version pins against `az cognitiveservices model list`** before declaring a Bicep "GA-ready". The gpt-realtime-1.5 version was correct (2026-02-23); the gpt-4.1 version had drifted (looks like a stale gpt-4o copy-paste). Adding this to the pre-deploy checklist.
2. **The model-catalog API is the source of truth, not docs.** MS Learn pages lag; the live `az cognitiveservices model list -l <region>` shows real-time availability + lifecycle + deprecation dates.
3. **Quota for gpt-realtime-1.5 = 10 is a hard ceiling at sandbox tier.** Bicep asks exactly 10; any future capacity bump will require a quota-increase ticket. Document this constraint.

## 2026-05-15 — azd up pre-flight: target sub/tenant locked, auth gap flagged

**Update to earlier 2026-05-15 entry.** Brady provided the actual target identity for the Tuesday dry-run:
- **Sub:** `47156f11-2e05-4362-ac86-090b4b081b27`
- **Tenant:** `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`

**Auth gap:** Current CLI session is logged in as `admin@MngEnvMCAP651545.onmicrosoft.com` on tenant `999097f4-...`. `az account set --subscription 47156f11-...` returns *"doesn't exist in cloud 'AzureCloud'"* — the target sub lives behind a different Entra tenant that this CLI session has no token for. Cannot run az commands against the target sub from this shell.

**What I did instead:**
1. Locked the target sub + tenant + region (`eastus2`) + env name (`crosstown-dryrun-may15`) into the report and inbox decision so the four bind together at provision time with zero ambiguity.
2. Marked every recon finding as either **portable** (Bicep state, model catalog availability, P0 version-pin bug) or **sub-scoped** (quota numbers, provider registration state) so Brady knows exactly what to re-verify Monday.
3. Wrote a §10 PowerShell re-verify block in the report — five steps Brady runs against `47156f11-...` after `az login --tenant 9b7cbd77-...`.

**Findings unchanged from earlier recon:**
- ✅ Bicep compiles clean.
- ✅ Region: `eastus2` (catalog confirms gpt-4.1 + gpt-realtime-1.5 v2026-02-23 both GA there; westus3 + eastus do NOT carry gpt-realtime-1.5 yet).
- 🛑 **P0 blocker still applies:** `infra/modules/foundry.bicep:77` pins gpt-4.1 to `version: '2024-11-20'` — that version does not exist. Must be `'2025-04-14'`. Repo state — sub-independent.
- ⚠️ gpt-realtime-1.5 default quota observed at 10 on recon sandbox; Bicep asks 10. Zero headroom. **Single most important sub-scoped value to re-verify Monday AM.**
- Idle cost: ~$3.40/day, dominated by AI Search Basic + Postgres B1ms.

**Verdict: NO-GO** until (a) Bicep gpt-4.1 version fix lands and (b) §10 sub-scoped re-verify passes. After both → GO with eastus2 + `crosstown-dryrun-may15` + sub `47156f11-...`.

**Learnings:**
1. **Always confirm the auth context matches the target sub BEFORE running recon.** `az account list` + `az account show` should be step 0 of any pre-flight. Wasted ~5 min running quota commands against a sandbox that wasn't the target.
2. **Cross-tenant subscriptions are invisible until you `az login --tenant <id>`.** `az account set --subscription <id>` silently fails (well, with a generic "doesn't exist" message) when the token isn't for that tenant. Document this footgun for the team.
3. **Lock sub + tenant + region + env name as a tuple in the decision record.** Anyone running `azd up` tomorrow should see those four values together with no possibility of mismatch. Did this in §6 + §10 of the report and in the inbox decision.
4. **Separate findings by portability when you can't fully verify.** Bicep + model-catalog findings are sub-agnostic; quota + provider-registration state is per-subscription. Splitting the report this way kept it useful despite the auth gap rather than throwing the whole thing out.

## 2026-05-15 — P0 fix shipped: gpt-4.1 version pin → PR #5

**Scope shipped:**
- Branch: `squad/fix-foundry-gpt41-version` (off `main` @ `2946e27`)
- Commit SHA: `96e42d435da1ce85864cd281b2090ea4400d7177`
- File: `infra/modules/foundry.bicep` — one-line change, `version: '2024-11-20'` → `'2025-04-14'`
- PR: **#5** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/5
- Title: `fix(infra): gpt-4.1 model version to 2025-04-14 (P0 — blocks azd up)`

**Pre-merge verification:**
- `az bicep build --file infra/main.bicep --stdout > $null` → exit 0 ✅
- Diff isolated to a single line — no collateral changes
- Explicit `git add -- infra/modules/foundry.bicep` (only)

**Scope discipline (other version pins scanned, NOT touched in this PR):**
| Location | Pin | Status |
|---|---|---|
| `foundry.bicep:93` gpt-realtime-1.5 | `'2026-02-23'` | ✅ Verified correct (D-009 + live catalog) |
| `postgres.bicep:27` Postgres engine | `version: '16'` | ✅ Engine version, not a model pin |
| All other `2024-XX` strings in `infra/` | ARM API versions (`@2024-03-01` etc.) | ✅ Not model pins |

Only one model version pin in `infra/` was incorrect; this PR fixes it. No other Cognitive Services SKU/version anomalies found.

**Branching mechanics gotcha (worth remembering):**
- Started on `squad/scribe-reverify-2026-05-15` with uncommitted scribe-owned changes to `.squad/agents/okoye/history.md` + `.squad/agents/stark/history.md`.
- First `git checkout main` failed (uncommitted changes would be overwritten), but the subsequent `git checkout -b squad/fix-foundry-gpt41-version` succeeded and branched off the WRONG base (the scribe branch, not main).
- Fix: deleted the wrong branch, `git stash push -- <paths>` the modified history files, `git checkout main` (clean), `git pull --ff-only` to fast-forward 12 commits, then `git checkout -b squad/fix-foundry-gpt41-version` (correctly off updated main @ `2946e27`), then `git stash pop` after PR creation to restore the history WIP.
- **Lesson:** Always verify the new branch's parent commit with `git log --oneline -3` immediately after `checkout -b`. Don't assume `-b` branches off where you expected if the prior `checkout` failed.

**Token / repo hygiene:**
- HTTPS remote + `gh` auth (per D-013 pattern). Push and `gh pr create` both clean on first attempt.
- PR body references the pre-flight report at `.squad/files/azd-up-preflight-2026-05-15.md` for full provenance.

**Status:** P0 cleared as soon as #5 merges. Next dependency for GO verdict on `azd up`: §10 sub-scoped re-verify on the target sub `47156f11-...` Monday morning (quota + provider registration). Captured as inbox decision D-016.

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up
