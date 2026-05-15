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
