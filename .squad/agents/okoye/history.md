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
