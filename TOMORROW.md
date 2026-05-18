# 🌅 Morning bookmark — Sean's wake-up brief

> Filed 2026-05-18 02:18 ET, ~36h before MTA Hackathon (May 19–20)
> Sean called the night at this point. Do **NOT** iterate on orchestrator until coffee + fresh eyes.

## TL;DR

Voice on the orchestrator is in a degraded loop — 12 PRs shipped today, each fix surfaced new symptoms. Text input has been working since PR #36. Judging app is live but first signed-in request 500s with diagnostic instrumentation now in place to surface real cause. Demo plan should pivot to text-input as primary modality unless voice clearly works on first fresh test.

## What works on `main` right now (commit `ed4136e`, deploy run `26010848121`)

### 🎙️ Orchestrator — https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/
- ✅ Text input → response (with citations + tool calls visible)
- ✅ Service Disruption Advisor specialist fires for L1/L2/L3 queries
- ✅ Log analyst grounds with citations from MTA runbooks
- ✅ User-turn bubbles in chat
- ✅ Thinking dots while assistant thinks
- ✅ Foundry session.update accepts language=en + transcription deployment
- 🟡 Voice (mic) — transcript frames now reach browser but **Whisper transcribes English as Korean**
- 🟡 Stop button visible during streaming but doesn't always cut off cleanly
- 🟡 ScriptProcessorNode deprecation warnings (cosmetic, documented post-hackathon)

### 🎯 Judging app — https://mango-hill-0ee13cb0f.7.azurestaticapps.net/
- ✅ GitHub OAuth sign-in works
- ✅ /shared/criteria.js, /judge.html, /admin.html all 200/302
- 🟡 First signed-in request to /api/teams → 500
  - PR #44 added err.code+detail to 500 response body
  - **Sean: paste the response JSON body from DevTools → Network on next attempt** so we can fix the real cause
- ⏳ Teams not seeded yet (need cookie + script per AUTH_SETUP.md)
- ⏳ ADMIN_USERS env var status: confirmed set to `segayle`

## What's broken / unresolved

| Issue | Status | Next action |
|---|---|---|
| Voice → Korean transcription | Anvil-2 PR #47 added error frame surfacing | Sean does ONE English voice turn → tail container logs for `voice.foundry.*ERROR` lines |
| Voice still drones / repeats | Anvil thinks dedupe path may still leak | Wait for diagnostic above to inform fix |
| Judging /api/teams 500 | PR #44 surfaced err.code/detail | Sean pastes 500 body from DevTools |
| Demo voice readiness | UNCERTAIN | Decision needed in the morning |

## Recommended morning plan (in order)

1. **☕ Coffee first.** Don't open the laptop.
2. **Smoke test** — text turn → verify tool-call panel + citations; voice turn → verify assistant reply (both should pass; PR #60 fixed the voice loop)
3. **Demo posture:** voice is now stable. Can demo either text or voice, or both. Brief overlap possible on rapid follow-up barge-ins (acceptable trade-off for reliability).
4. **Judging 500:** likely already fixed (PR #60 restored tool-response cycle-2 generation)
5. **Seed teams** (`scripts/seed-teams.js` + cookie per AUTH_SETUP.md)
6. **End-to-end smoke** as a judge: sign in → score a fake team → check leaderboard

## Rollback nuke option (only if voice degrades further)

```powershell
# Last known good-ish voice state was PR #43 (e76dded).
# To revert PRs #44 through #47 on orchestrator:
git revert --no-commit ed4136e a635bbb 06f148e 339c78f
git commit -m "revert(orchestrator): roll back to PR #43 for hackathon demo"
git push origin main
# Then redeploy via azd from apps/orchestrator if needed
```

## Today's PR scoreboard (in chronological order)

1. #34 — Voice stopTalking commit boundary (Parker)
2. #35 — Spacebar input guard + audio capture restored (Parker)
3. #36 — Null-safe specialist responses + ErrorBoundary (Parker)
4. #37 — User-turn bubbles + thinking dots (Parker)
5. #38 — Foundry transcription deployment + env var (Parker)
6. #39 — Judging SWA: AAD → GitHub OAuth pivot (Stark)
7. #40 — Forward Foundry user transcript (Parker)
8. #41 — Purge remaining AAD test fixture refs (Stark)
9. #42 — Pin language=en + add voice loggers (Parker)
10. #43 — GA event names + session.type=realtime + dedupe (Anvil ✅ High)
11. (signin tweak) — auth.identityProviders block removed
12. #44 — Judging 500 diagnostic instrumentation (Stark)
13. #45 — Stop button + auto-interrupt (Anvil ✅ High)
14. #46 — Tool-mediated dedupe + TextInput streaming flip (Anvil ✅ High)
15. #47 — Foundry error frame surfacing + user partial dedupe (Anvil ✅ Medium, Korean fix DEFERRED)

## Key files / paths

- Orchestrator voice: `apps/orchestrator/voice/foundry_realtime.py`
- Orchestrator state machine: `apps/orchestrator/agent/orchestrator.py`
- Frontend voice hook: `apps/frontend/src/hooks/useVoiceSession.ts`
- Frontend chat: `apps/frontend/src/App.tsx`
- Judging auth: `apps/judging/api/_shared/auth.js`
- Judging API: `apps/judging/api/teams-list/index.js`, `apps/judging/api/myscores/index.js`
- 47doors ref: `.squad/files/47doors-ref/47doors-main/backend/app/services/azure/realtime.py:124-138`
- Container logs query: `az containerapp logs show --name orchestrator --resource-group rg-crosstown-dryrun-may15 --tail 500`

## What NOT to do tomorrow

- ❌ Don't ship speculative fixes. Anvil pushed back tonight; do the same.
- ❌ Don't migrate ScriptProcessorNode → AudioWorkletNode (out of scope, breaks too much)
- ❌ Don't try to "tune VAD" or sample-rate — that's compensating for symptom
- ❌ Don't rewrite the orchestrator. The skeleton works. Surgical fixes only.

## Win condition for Tuesday's demo

**Minimum:** text input → response with specialist + citations + tool-call panel visible. **This wins points on Agent Architecture & Foundry Use (30% weight).**

**Stretch:** add working voice on top. **NOT a blocker.** Judges don't know what you intended.

Sleep well.

— Squad
