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

---

## 2026-05-18 ~11:15 ET — Audio regression diagnosis: "Brooklyn → Ozone on the surface"

**Investigator:** Wanda (Maximoff)
**Report time:** 2026-05-18T11:14-11:15 ET (Sean, live orchestrator)
**Symptom:** Sean said "Brooklyn" → transcription received as "Ozone on the surface"

### Root cause classification: **B — Wrong/insufficient audio reached Foundry**

The orchestrator relay layer is committing audio buffers to Foundry prematurely or without adequate audio content. Two buffers were committed in the ~11:15 ET window. The second commit was **completely empty (0.00ms)**. The first commit had some audio but likely a very short/fragmented payload (Whisper hallucinated "Ozone on the surface" rather than "Brooklyn" — a classic short-audio hallucination pattern). This is not a Foundry/Whisper quality issue in isolation; the bad transcription is a downstream symptom of the relay sending insufficient audio.

### Direct log evidence

```
# Timestamp: 2026-05-18T15:15:14.878 UTC (= 11:15:14 ET)
{"TimeStamp": "2026-05-18T15:15:14.8786617+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=input_audio_buffer.committed"}
{"TimeStamp": "2026-05-18T15:15:14.8790645+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=conversation.item.added"}
{"TimeStamp": "2026-05-18T15:15:14.8790808+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=conversation.item.done"}
{"TimeStamp": "2026-05-18T15:15:14.8807241+00:00", "Log": "15:15:14,880 voice.foundry INFO foundry.recv DROP type=response.created"}

# Response completes in <200ms — suspiciously fast, consistent with near-empty audio
{"TimeStamp": "2026-05-18T15:15:15.0601463+00:00", "Log": "15:15:15,059 voice.foundry INFO foundry.recv EMIT type=response.done -> Final"}

# Transcription deltas arrive (Foundry IS processing some audio from the first commit)
{"TimeStamp": "2026-05-18T15:15:15.3110530+00:00", "Log": "15:15:15,310 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.delta -> TranscriptDelta"}
# [5 more delta events through 15:15:15.328]

# *** SMOKING GUN ***
{"TimeStamp": "2026-05-18T15:15:15.434144+00:00", "Log": "15:15:15,433 voice.foundry ERROR foundry.recv ERROR event_id=event_DgtyVSvJslOzlEzUhcsVp code=input_audio_buffer_commit_empty type=invalid_request_error param=None message=Error committing input audio buffer: buffer too small. Expected at least 100ms of audio, but buffer only has 0.00ms of audio."}

# Transcription for the first (short) buffer completes — this is the "Ozone on the surface" result
{"TimeStamp": "2026-05-18T15:15:15.5710672+00:00", "Log": "15:15:15,570 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.completed -> TranscriptDelta"}
```

### Interpretation

| Fact | Implication |
|------|------------|
| `input_audio_buffer.committed` at 15:15:14 → transcription deltas fire | First buffer had SOME audio — mic is live and audio path is not completely broken |
| Second buffer committed at 15:15:15.434 with **0.00ms** | Relay called `input_audio_buffer.commit` on an empty buffer — no audio chunks were accumulated before commit |
| `response.done → Final` in <200ms after first commit | Response was trivially short; server-side VAD likely triggered on a very short audio segment |
| Wildly wrong transcription ("Ozone on the surface") | Whisper hallucination caused by receiving a very short, possibly near-silence audio clip — known Whisper behavior on <1s clips |

The relay layer is either: (a) committing the buffer too early (before mic audio accumulates), or (b) sending a `commit` without waiting for the frontend to stream sufficient `input_audio_buffer.append` chunks. The 0.00ms error confirms the orchestrator's relay called commit on an empty Foundry-side buffer at least once in this session.

### Recommended fix

**Stark:** In the orchestrator relay, add a minimum-audio-duration guard before committing the input audio buffer — do not call `input_audio_buffer.commit` unless the buffer holds ≥ 100ms of audio (matching Foundry's own enforced minimum). If the client sends a stop/commit signal with an empty buffer, drop the commit rather than forwarding it.

### Confidence: High

- The 0.00ms error is unambiguous and timestamped exactly in Sean's reported window (11:15 ET).
- No `voice.foundry ERROR` or relay errors on the audio path prior to this window → not a pre-existing crash.
- Transcription infrastructure (`gpt-4o-mini-transcribe`) is not at fault; it produced an output for the audio it received — the audio itself was the problem.
- Frontend microphone is live (audio DID reach the first buffer), so this is not Cause C (frontend capture broken).

---

## Risk if left unfixed
- **No code can reach the live Azure environment.** Every push to `main` fails before `azd provision` and `azd deploy` even start. Voice stack (`apps/orchestrator`, `apps/log_analyst`, `apps/frontend`) is frozen at whatever was last deployed — which, given there is **no successful run on record**, may mean nothing has *ever* deployed via this workflow and the live ACA apps are still on placeholder/quickstart images.
- **Hackathon impact (Track 2):** the Tuesday demo (specs/002-tuesday-demo) depends on the deploy lane producing a working `FRONTEND_URL` for the smoke test (`scripts/smoke-test.*` + `azure.yaml` postdeploy hook). With OIDC broken, the demo URL cannot be refreshed with current PR #21 / PR #22 / PR #27 changes (user-turn transcripts, VAD fix, service-advisor feature). Judges will hit stale or broken endpoints.
- **Eval/red-team live mode** (`EVAL_MODE=live ORCHESTRATOR_URL=…`) cannot be exercised against the deployed stack until this clears, so we lose live-path coverage on top of hermetic cassettes.
- **Time cost:** ~5 min Azure portal change once a Contributor on the app registration is available. Every hour of delay is an hour the Track 2 stack ships on stale bits.
