# Okoye — Archive (Phase 0)

## Summary (2026-05-13 through 2026-05-15)

**Phase 0 (2026-05-13 through 2026-05-15):**

- **Judging app manifests (2026-05-13):** Nested `apps/judging/azure.yaml` + seed script + README. Lessons: root .gitignore duplication, azd + SWA API discovery flakiness, CSV parser must handle quoted fields, Cosmos networkAclBypass + publicNetworkAccess pattern for SWA managed Functions.
- **Realtime model swap (2026-05-15):** Branch `squad/swap-realtime-to-gpt-realtime-1.5`, commit d79a8d2. Files staged explicitly (7 total, no globs). Lessons: explicit `git add -- <path>` critical, branch naming `squad/tool-version`, HTTPS + gh auth more reliable on Windows.
- **Org import & dual PR batch (2026-05-15):** Resolved PAT + SSO authorization. Pushed both `squad/swap-realtime-to-gpt-realtime-1.5` (#1) and `squad/add-spec-kit-v0.8.10` (#2). Lessons: SSO mandatory even with correct scopes, HTTPS + `gh auth setup-git` reliable, decision log decouples architecture from PR narrative.
- **azd up pre-flight reconnaissance (2026-05-15):** Target sub 47156f11-.../tenant 9b7cbd77-... identified. P0 blocker: gpt-4.1 version pin outdated (2024-11-20 does not exist; should be 2025-04-14, fixed in PR #5). Quota: gpt-realtime-1.5 = 0/10 (tight), other services green. Learnings: confirm auth context (az account show) before recon, cross-tenant subs invisible until `az login --tenant`, lock sub + tenant + region + env name as tuple.

**Phase 1 (2026-05-16):** Deploy-hygiene batch.
- T101 smoke-test.sh: 5 baseline + 6 full checks, `FRONTEND_URL` (not SERVICE_FRONTEND_URI per audit T004)
- T107 deploy.yml guard: FR-013 main-only, workflow_dispatch override, 4-case trace table
- Support on T104/T106 via audit findings (canonical `/health` endpoint per audit T001)

Archive entry date: 2026-05-16
