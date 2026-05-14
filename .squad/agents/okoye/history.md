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
