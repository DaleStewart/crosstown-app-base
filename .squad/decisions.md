# Squad Decisions

## Active Decisions

### D-001 · Cast the Avengers · Lead: T'Challa
**Date:** 2026-05-12
**Author:** Squad (operator request)
**Status:** Adopted

The squad is cast from the **Marvel Cinematic Universe** as the **Avengers**, with **T'Challa (Black Panther)** as the Lead. T'Challa's role aligns with the `ralph` slot's persistent-memory mandate: institutional recall + tie-breaking authority.

**Hires today:**
- `ralph` → **T'Challa** (Lead, Black Panther)
- `scribe` → **Shuri** (Knowledge archivist + R&D)

**Bench (hire as needed):** Tony Stark, Natasha Romanoff, Bruce Banner, Sam Wilson, Peter Parker, Okoye, Wanda Maximoff, Stephen Strange. See `.squad/casting/registry.json` for intended roles.

**Rationale:** T'Challa-as-Lead gives us a calm, strategy-first persona that complements the hackathon's "opt-in scaffolding" framing. The MCU was already on the allowlist (capacity 25) and pairs naturally with the team's existing two-slot baseline.

**Reversal procedure:** Re-cast by overwriting `.squad/casting/registry.json` and appending a new entry to `.squad/casting/history.json`. Update `.squad/team.md` and the affected `agents/*/charter.md`.

### D-002 · Judging app layout — `apps/judging/` as a sibling workload
**Date:** 2026-05-13
**Author:** Stark (Architect)
**Status:** Adopted

Everything for the judging app lives under **`apps/judging/`** as a self-contained workload:
- `apps/judging/shared/criteria.js` (dual-export: CJS + window global)
- `apps/judging/staticwebapp.config.json` (SWA AAD + route rules)
- `apps/judging/api/` (SWA managed Functions: teams-list, teams-create, myscores, score-submit, leaderboard, lock, export)
- `apps/judging/infra/main.bicep` (Cosmos serverless + SWA Standard)

Root `azure.yaml`, root `infra/`, and sibling `apps/*` remain untouched.

**Rationale:** Isolation of deploy lifecycle, single source of truth for criteria, SWA managed Functions reduces infra surface, partition key `/track` on Cosmos ensures predictable RU.

**Follow-ups (Okoye):** Decide azd integration vs. standalone GH Actions workflow. Replace `{{TODO_TENANT_GUID}}`. Document admin-role grant path.

### D-003 · Frontend design tokens for the judging app (v3 — MTA brand)
**Date:** 2026-05-13
**Author:** Parker (Frontend)
**Status:** Adopted

Reference scorecards used Barlow as a stand-in. Sean confirmed the real MTA brand is **Helvetica** + the **NYCT route palette**. All tokens repointed to MTA specs at `apps/judging/src/styles.css`:
- Color: MTA Blue `#0039A6`, MTA Red `#EE352E`, MTA Green `#00933C`, MTA Orange `#FF6319`, MTA Yellow `#FCCC0A`
- Typography: Helvetica Neue (no web fonts), 400 body / 500 labels / 700 display, uppercase tracking `-0.02em` to `-0.04em`
- Shape: `--radius: 2px` (buttons), `--radius-lg: 0` (cards), circular bullets/pills
- Tier ladder: Exceptional (green, ≥90), Strong (navy, ≥70), Developing (orange, ≥50), Needs work (red, <50)
- Components: `.bullet` (route-bullet primitive), `.hack-roundel`, `.signage`, `.tier-block`, `.tier-cell`, etc.
- Iconography: Tabler icons (mono), used sparingly; numbered bullets replace criterion icons
- Dark mode: bg `#0A0A0A`, surface `#181818`, navy `#4D7EE8`

**Rationale:** Maintains MTA visual identity, sharp-cornered panels, brand-layer compliance. Trademark: hackathon `AI` route bullet (not MTA "M" logo).

### D-004 · Separate `azure.yaml` inside `apps/judging/` (do not modify root)
**Date:** 2026-05-13
**Author:** Okoye (Operations)
**Status:** Adopted

Ship a **self-contained `azd` project at `apps/judging/azure.yaml`** with its own `infra/` folder. Users run `cd apps/judging && azd up` to deploy. Root `azure.yaml` is untouched.

**Rationale:** Isolation of blast radius, different lifecycles (event-scoped vs. long-running platform), different service topology (single staticwebapp vs. multi-containerapp), team parallelism, azd nesting is native.

**Trade-offs:** Users must `cd apps/judging` before azd commands (documented). SWA Functions auto-discovery documented as fallback using `swa deploy --api-location ./api`.

### D-005 · Test strategy — interception-first Playwright
**Date:** 2026-05-13
**Author:** Banner (Tester)
**Status:** Adopted

For the judging app's E2E tests, **stub `/.auth/me` and `/api/*` with `page.route()` per test**. Do **not** depend on live AAD or live Cosmos DB for the default test run. A separate, opt-in "integration" project can be added later for real Functions + Cosmos contract testing.

**Rationale:** AAD is hard to script; SWA CLI auth simulator is stateful. Overriding `/.auth/me` per test gives deterministic `clientPrincipal` (anon/judge/admin) matching what `apps/judging/src/auth.js` reads. Cosmos is expensive/slow; frontend logic (picker, criterion disable, lock banner on 423, admin leaderboard, POST payloads) is observable purely from JSON shape. Tests run in seconds, hermetic, no secrets in CI, not flaky.

**Coverage:**
- `unit/criteria.test.js` — assertions on `computeTotal`, `tier`
- `e2e/landing.spec.js` — track cards render, admin gated by role
- `e2e/judge.spec.js` — picker loads, submit enables only when all 5 scored, posts to `/api/score`, HTTP 423 shows lock banner
- `e2e/admin.spec.js` — non-admin gate, leaderboard rank order, lock toggle POSTs `{track, locked}` to `/api/lock`, add-team POSTs to `/api/teams`

**Not covered:** Real API contract drift (integration tests later), auth-policy enforcement (SWA server-side only), Copilot-track flow (only Azure tracked; unit smoke covers both).

**Open:** CI workflow (`.github/workflows/judging-tests.yml`) for PR unit + label-gated E2E? Extend to Copilot track now or wait for stabilization?

### D-006 · gpt-4o → gpt-4.1 Model Version Regression Sweep
**Date:** 2026-05-13
**Author:** Maximoff (QA/Anomaly Detection)
**Status:** Adopted

Replaced all `gpt-4o` model deployment references in the root MTA AI Hackathon project with `gpt-4.1`. Mechanical configuration fix across 13 hits in 9 files (Bicep, env templates, Python settings, Markdown docs).

**Files affected:**
- `infra/modules/foundry.bicep` — deployment resource, model field
- `.env.example` — AZURE_OPENAI_CHAT_DEPLOYMENT
- `apps/log_analyst/settings.py`, `apps/orchestrator/settings.py` — chat deployment defaults
- `apps/log_analyst/README.md`, `docs/evals.md`, `docs/voice.md`, `evals/foundry_evaluators.py`, `evals/README.md` — docstrings, examples

**Why `gpt-4o-realtime-preview` was left alone:** Distinct purpose (voice/audio path). Real model name, explicitly named and immutable. Chat completions uses `gpt-4.1` (NEW); realtime uses `gpt-4o-realtime-preview` (UNTOUCHED).

**Verification:** 0 remaining `gpt-4o` hits (excluding realtime); 13 `gpt-4.1` refs in place; 11 realtime refs untouched.

**Risk:** Low — pure config/documentation changes, no app logic altered. Scope locked to root (apps/judging/ excluded). Deployment-ready: `azd up` to deploy new model to Azure OpenAI account.

### D-007 · Security Review — MTA Hackathon Judging App
**Date:** 2026-05-13
**Author:** Strange (Security Engineer)
**Status:** Adopted

**Verdict:** 🟡 Ship after must-fix items — 2 critical findings (CSV formula injection in export, unfilled tenant GUID placeholder) and 4 high findings must be addressed before external deployment. Core auth/authz model is solid.

**Report:** `apps/judging/SECURITY_REVIEW.md`

### D-008 · Security Hardening Sweep — 10 findings closed (Stark + Okoye)
**Date:** 2026-05-13
**Author:** Stark (Backend/API) + Okoye (Operations / Platform)
**Status:** Adopted

All 10 findings from Strange's security review (D-007) have been closed across two commits:

**Stark's lane (7f6b670):** API surface fixes
- C1 — CSV formula injection (pi/export/index.js): csvEscape() now prefixes hostile cell starts
- H4 — Request body size limit (pi/host.json): 100 KB cap on all Functions
- M1 — Leaderboard gating (pi/leaderboard/index.js): admin bypass; non-admin 403 until locked
- M2 — Lock route GET handler (pi/lock/): GET reads lock status, POST unchanged

**Okoye's lane (ae0cdeb):** Config + infra surface
- C2 — Tenant GUID (staticwebapp.config.json): replaced TODO with Microsoft tenant GUID
- H1 — Security headers (staticwebapp.config.json): X-Frame-Options, CSP, Referrer-Policy added
- H2 — Cosmos firewall (infra/main.bicep): networkAclBypass + empty rules; private endpoint marked TODO
- H3 — Config lock (infra/main.bicep): allowConfigFileUpdates=false; Bicep-managed only
- M3 — Gitignore (pps/judging/.gitignore): expanded coverage for env, azure, keys, test artifacts
- M4 — Connection string handling (infra/main.bicep): comment-documented threat model, Key Vault path marked

**Verdict upgrade:** 🟡 Ship after must-fix items → 🟢 Ship (all must-fix items now fixed).

**Verification:** Both commits verify clean (node --check, bicep build, JSON parsing). No cross-file conflicts. Ready for external deployment.

### D-009 · Foundry Realtime Model Upgrade — gpt-4o-realtime-preview to gpt-realtime-1.5
**Date:** 2026-05-15
**Author:** Okoye (Verification + PR)
**Status:** Adopted

Swapped `gpt-4o-realtime-preview` (version `2024-10-01`, api-version `2024-10-01-preview`) → `gpt-realtime-1.5` (version `2026-02-23`) using the GA `/openai/v1/realtime?model={deployment}` endpoint pattern (no api-version query param). 
### D-009 · Foundry Realtime Model Version Swap to gpt-realtime-1.5
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** Local commit ready; push blocked (remote auth)
**Branch:** `squad/swap-realtime-to-gpt-realtime-1.5` (SHA: `d79a8d2`)

Upgrade Foundry voice provider from `gpt-4o-realtime-preview` to `gpt-realtime-1.5`. Seven files modified:
- `.env.example` — updated deployment name
- `apps/orchestrator/settings.py` — updated chat + voice deployment references
- `apps/orchestrator/voice/foundry_realtime.py` — new implementation
- `infra/main.bicep`, `infra/modules/foundry.bicep` — new model in deployment
- `docs/architecture.md`, `docs/voice.md` — updated examples and version notes

**Scope:** Realtime voice path only. Chat completions (D-006: `gpt-4.1`) untouched. Citation + eval gates pass with realtime swap in place.

**Blockers:** Remote repository (`git@github.com:DevPost-Test-Hackathon/crosstown-app`) not found or SSH auth failed. Commit queued locally; push and PR pending remote provisioning fix.

**Next:** Fix remote origin URL or SSH credential, then `git push -u origin squad/swap-realtime-to-gpt-realtime-1.5` + `gh pr create`.

### D-010 · Decision Log Supersedes Maximoff "leave realtime alone" Instruction
**Date:** 2026-05-15
**Author:** T'Challa (Lead) — noted retrospectively via Scribe
**Status:** Archived (no further action)

Earlier session (morning 2026-05-15) included an instruction to Maximoff: "do not modify realtime". This instruction is now superseded by D-009 (realtime swap decision adopted). The decision log is the source of truth; Maximoff's cross-agent record is stale. No reversal needed — D-009 is the active architecture.

### D-011 · GitHub Spec Kit v0.8.10 Adoption + Constitution Ratified + Spec 001 Worked Example
**Date:** 2026-05-15
**Author:** Okoye (Operations) + Stark (Architect)
**Status:** Local commit ready; push blocked (remote auth)
**Branch:** `squad/add-spec-kit-v0.8.10` (SHA: `7c063c5`)

**Three components in one decision:**

#### Component A: Spec Kit v0.8.10 Installation
Installed GitHub Spec Kit CLI (`specify-cli==0.8.10`) into the repo, enabling spec-driven workflows:
- Scaffolding: Constitution → Specification → Plan → Tasks → Implementation
- Copilot integration: slash commands (`/speckit.constitution`, `/speckit.plan`, etc.) in Copilot CLI and Chat
- Script type: PowerShell (Windows-native, aligns with repo precedent)
- Flags: `--here` (in-place), `--ignore-agent-tools`, `--no-git` (repo already initialized)

**Artifacts created (43 files):**
- `.specify/` — 17 files (config, scripts, templates, workflows)
- `.github/agents/speckit.*.agent.md` — 9 agent definitions
- `.github/prompts/speckit.*.prompt.md` — 9 prompt files
- `specs/001-realtime-1-5-upgrade/` — 3 worked-example artifacts (spec, plan, tasks)
- `.squad/skills/spec-kit-authoring/SKILL.md` — 1 skill bridge
- Cross-agent history updates — 3 files

#### Component B: Constitution v1.0.0 Ratified
Six principles derived from existing repo contracts (not invented, already in `.github/copilot-instructions.md`):

1. **Citations Are Load-Bearing** (NON-NEGOTIABLE)
2. **Mock Data Only** (NON-NEGOTIABLE)
3. **Hermetic by Default, Live on Demand**
4. **Keyless Auth Everywhere**
5. **One Voice Abstraction, Two Implementations**
6. **Extensions Are Exercises, Not Features**

Stored at `.specify/memory/constitution.md` v1.0.0, ratified 2026-05-15.

#### Component C: Spec 001 Worked Example
Realtime model upgrade (D-009 context) used as the reference flow:
- **Spec:** Requirements decomposition for gpt-realtime-1.5 swap
- **Plan:** Implementation breakdown
- **Tasks:** 10/10 actionable items, all complete (mapped to D-009 files)

All artifacts at `specs/001-realtime-1-5-upgrade/`.

**Rationale:**
- Spec-driven decomposition reduces design drift.
- Copilot integration (slash commands) eliminates context switching.
- PowerShell aligns with Windows environment and existing conventions.
- Constitution anchors future features and spec workflows.
- Worked example (Spec 001) gives team a concrete reference on this codebase.

**Blockers:** Same remote auth issue as D-009. Branch + commit queued locally; push and PR pending.

**Deprecation note:** Spec Kit CLI evolving — by v0.10.0, `--ai` becomes `--integration`, git extension auto-enable will be removed. Recommend pinned `v0.8.10` for reproducibility or upgrade path.

**Next:** Fix remote, push, open PR. Then reconcile dual decisions files (root `.squad/decisions.md` vs. `specs/001-*/decisions.md` subfolder pattern) in a future session.

### D-012 · Two Local Branches Queued — Remote Auth Blocker
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** Operational note; awaiting remote provisioning
**Branches:**
- `squad/swap-realtime-to-gpt-realtime-1.5` (SHA: `d79a8d2` — realtime model swap, D-009)
- `squad/add-spec-kit-v0.8.10` (SHA: `7c063c5` — spec-kit adoption + constitution, D-011)

Both branches committed locally but cannot push to origin. Remote repository (`git@github.com:DevPost-Test-Hackathon/crosstown-app`) is not found or SSH auth failed. No action needed from the squad until remote is provisioned or URL corrected. Once resolved, both branches can push and open PRs in parallel (no dependency).

**Tracking:** Flagged here so future team knows why two productive branches sit unpushed.

### D-013 · Org Import Successful — PRs #1 and #2 Open
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** Completed

D-012 (remote auth blocker) is **RESOLVED**. Both development branches successfully pushed to `DevPost-Test-Hackathon/crosstown-app` and paired with PRs.

**Resolution flow:**
- Fresh PAT generated from account that IS an org member of `DevPost-Test-Hackathon`
- SSO authorization completed explicitly (Authorize button clicked in GitHub)
- Token set in-memory only via `$env:GH_TOKEN`; origin flipped to HTTPS
- `gh auth setup-git` established credential helper
- Smoke test passed: `gh api orgs/DevPost-Test-Hackathon` returned org JSON (no 404)
- Both branches pushed successfully to remote

**Branches & PRs:**
- **PR #1:** `squad/swap-realtime-to-gpt-realtime-1.5` → "Swap Foundry Realtime to gpt-realtime-1.5" (D-009)  
  https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/1

- **PR #2:** `squad/add-spec-kit-v0.8.10` → "Add GitHub Spec Kit v0.8.10 + Constitution v1.0.0 + Spec 001" (D-011)  
  https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/2

**Key insight:** SSO authorization is a separate checkpoint — it's not enough to generate a PAT with the right scopes. GitHub SSO flow requires explicit "Authorize" click for each new PAT, even if the user is already an org member. This is by design (security), but easy to miss if you assume "membership + PAT scopes = ready to go."

**Learnings for future ops:**
- Always verify org reachability with `gh api orgs/<ORG-NAME>` before investing in branch-push planning
- HTTPS + credential helper is more reliable than SSH key management for CI/CD on Windows
- PAT + SSO is a two-factor gate; both must be confirmed explicitly

**Token hygiene:** PAT set in-memory only, never to disk, never echoed in output logs. User should revoke temporary PATs used this session.

**Changes:**
- `infra/modules/foundry.bicep` — deployment name `gpt-realtime-1.5`, model.version = `gpt-realtime-1.5-2026-02-23`
- `.env.example` — `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5`
- `apps/orchestrator/settings.py` — realtime deployment env var
- `apps/orchestrator/voice/foundry_realtime.py` — WebSocket endpoint pattern for GA realtime endpoint
- `docs/voice.md`, `docs/architecture.md` — documentation updated to reflect new deployment

**Preserved:** Bicep symbol `gpt4oRealtimeDeployment`, env var `AZURE_OPENAI_REALTIME_DEPLOYMENT`, SKU `GlobalStandard`/capacity 10. Speech Services fallback path unchanged.

**Out of scope:** `gpt-realtime-mini`, `gpt-realtime-translate`, `gpt-4o-transcribe-diarize`.

**Verification:** Bicep build clean, ruff/mypy --strict on 19 files, pytest 11/11 passing, frame schemas valid for GA `/openai/v1/realtime`, straggler grep clean. Go.

### D-010 · Maximoff "Leave gpt-4o-realtime-preview alone" Instruction Superseded
**Date:** 2026-05-15
**Author:** Coordinator
**Status:** Adopted

Decision D-006 (gpt-4o → gpt-4.1 sweep, 2026-05-13) explicitly left `gpt-4o-realtime-preview` untouched with the rationale "Distinct purpose (voice/audio path). Real model name, explicitly named and immutable." That instruction was contextual to the 2026-05-13 chat-model migration — not a permanent freeze.

As of 2026-05-15, D-009 executes a deliberate model upgrade from `gpt-4o-realtime-preview` to `gpt-realtime-1.5` (GA endpoint). The historical Squad notes (`.squad/agents/maximoff/history.md`, `.squad/identity/resume.md`, `.squad/decisions.md` line 98) remain accurate as audit trail; they are NOT rewritten — only the current instruction supersedes.

**Related:** D-009 (realtime model upgrade, same session).

---

## Guidelines

- All meaningful changes require team consensus.
- Document architectural decisions here.
- Keep history focused on work, decisions focused on direction.
- Casting changes require a T'Challa sign-off entry.

