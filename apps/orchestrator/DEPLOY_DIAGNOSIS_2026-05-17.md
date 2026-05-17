# Deploy workflow diagnosis — 2026-05-17
**Investigator:** Wanda (Maximoff)
**Failing runs:** 25999139361 (18:29 UTC, sha d0abd0a), 25999032995 (18:24 UTC, sha 6e86386)
**Last green deploy:** **none on record** — `gh run list --workflow=deploy --status=success` returns `[]`. The deploy workflow has never succeeded since the `environment: dev` change landed; all five most-recent runs (back to 15:11 UTC) fail identically at the OIDC login step.

## Root cause
🟡 **CONFIG DRIFT — OIDC federated identity credential is missing a subject for `environment:dev`.** The deploy job declares `environment: dev` (deploy.yml line 26), so GitHub mints an OIDC token whose `sub` claim is `repo:DevPost-Test-Hackathon/crosstown-app:environment:dev`. Entra rejects it with **AADSTS700213 — "No matching federated identity record found for presented assertion subject 'repo:DevPost-Test-Hackathon/crosstown-app:environment:dev'"**. The Entra app `b2451691-200c-4d8d-b50f-a60396ddb606` (tenant `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`) does have *some* federated credential — almost certainly the original `ref:refs/heads/main` subject from before the deploy-hygiene refactor — but no credential whose subject pattern matches `environment:dev`. Nothing in the repo's code or Bicep is broken; this is purely an Azure-side identity configuration gap that must be added in the Entra app's "Federated credentials" blade. Job never reaches `azd provision` or `azd deploy`, so no infra/container/test failure is in play. The `apps/judging/` `azure.yaml` is *not* a factor — the workflow dies before any `azd` command that would resolve services.

## Evidence
- `gh run view 25999139361 --log-failed` — step **"Log in (OIDC)"** fails in 13s with:
  - `ERROR: Authentication with Azure failed.`
  - `ClientAssertionCredential authentication failed.`
  - `POST https://login.microsoftonline.com/9b7cbd77-6d6b-4879-8aba-63d7dfb18472/oauth2/v2.0/token` → **`RESPONSE 401: 401 Unauthorized`**
  - `"error": "invalid_client"`, `"error_codes": [700213]`
  - `"error_description": "AADSTS700213: No matching federated identity record found for presented assertion subject 'repo:DevPost-Test-Hackathon/crosstown-app:environment:dev'."`
  - Trace ID `c71e2126-e487-4b03-98cf-51f9fda94400`, Correlation ID `91497e24-da34-461b-8e43-c7f80911ea1e`.
- `.github/workflows/deploy.yml:26` — `environment: dev` (added by PR #29). This is what drives the `environment:dev` subject claim.
- `.github/workflows/deploy.yml:51-59` — login step passes `AZURE_CLIENT_ID=${{ vars.AZURE_CLIENT_ID }}` (`b2451691-200c-4d8d-b50f-a60396ddb606`) and `AZURE_TENANT_ID=${{ vars.AZURE_TENANT_ID }}` — both repo vars resolve, so the failure is not a missing variable; the token is minted and *rejected by Entra*.
- All 5 most-recent failed runs (25999139361, 25999032995, 25998917601, 25998867451, 25994549401) fail at the same step. The earliest failure (15:11 UTC, sha 2276017 — Okoye's PR #22 ship-it commit) is the **first push to main after** the deploy-hygiene merge that introduced `environment: dev`. The pattern is deterministic, not flaky → not 🔵 transient.
- `gh run list --workflow=deploy --status=success` → `[]` (no successful run exists post-`environment:dev`).

## Suspected commit
**`3398440` — "chore(deploy): deploy-hygiene bundle — smoke + healthchecks + nginx + main-only guard + cassettes (#29)"** (merged from `ea17f2a`, Sat May 16 20:23 -0400). `git show 3398440 -- .github/workflows/deploy.yml` shows the additive line `+      environment: dev`. That single line silently changes the OIDC `sub` claim shape and is what the federated credential on the Entra app no longer matches.

## Recommended fix
**Do not revert the workflow.** Pinning the job to a GitHub environment is correct for FR-013 / Phase 1 guardrails — the fix belongs in Azure, not in this repo:

1. In the Azure portal → App registration `b2451691-200c-4d8d-b50f-a60396ddb606` (tenant `9b7cbd77-…`) → **Certificates & secrets → Federated credentials → Add credential**:
   - Issuer: `https://token.actions.githubusercontent.com`
   - Organization: `DevPost-Test-Hackathon`
   - Repository: `crosstown-app`
   - Entity type: **Environment**
   - Environment name: **`dev`**
   - Audience: `api://AzureADTokenExchange`
   - Subject (auto-generated): `repo:DevPost-Test-Hackathon/crosstown-app:environment:dev`
2. Save. No code change required. Retry by re-running run `25999139361` (`gh run rerun 25999139361`) or pushing a no-op commit.

Optional belt-and-suspenders if the environment in GitHub doesn't exist yet: confirm `Settings → Environments → dev` exists on the `DevPost-Test-Hackathon/crosstown-app` repo (the `environment: dev` line in the workflow implicitly requires it; if it's missing GitHub still issues the token but the env-protection rules don't apply — current failure mode rules this out, since the token was issued).

**Out of scope (do not touch):** `apps/judging/azure.yaml`, `infra/**`, any service Dockerfiles. None of them contribute to this failure.

## Risk if left unfixed
- **No code can reach the live Azure environment.** Every push to `main` fails before `azd provision` and `azd deploy` even start. Voice stack (`apps/orchestrator`, `apps/log_analyst`, `apps/frontend`) is frozen at whatever was last deployed — which, given there is **no successful run on record**, may mean nothing has *ever* deployed via this workflow and the live ACA apps are still on placeholder/quickstart images.
- **Hackathon impact (Track 2):** the Tuesday demo (specs/002-tuesday-demo) depends on the deploy lane producing a working `FRONTEND_URL` for the smoke test (`scripts/smoke-test.*` + `azure.yaml` postdeploy hook). With OIDC broken, the demo URL cannot be refreshed with current PR #21 / PR #22 / PR #27 changes (user-turn transcripts, VAD fix, service-advisor feature). Judges will hit stale or broken endpoints.
- **Eval/red-team live mode** (`EVAL_MODE=live ORCHESTRATOR_URL=…`) cannot be exercised against the deployed stack until this clears, so we lose live-path coverage on top of hermetic cassettes.
- **Time cost:** ~5 min Azure portal change once a Contributor on the app registration is available. Every hour of delay is an hour the Track 2 stack ships on stale bits.
