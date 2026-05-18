# UAT readiness — 2026-05-17 (T-2 to hackathon)
**Assessor:** T'Challa (Lead)  ·  **Verdict:** 🟡 ship with caveats

## TL;DR (≤4 sentences for Sean)
The app IS deployed and live — text input works end-to-end right now. Voice loop has a known gap: `stopTalking()` never sends the commit boundary, so the orchestrator won't finalize transcription on mic release (PR #26 fixes this but has conflicts). The biggest risk is log-analyst returning 400 on tool calls — possibly a schema mismatch between what the model sends and what the tool expects. Fix the OIDC credential (5 min portal change), rebase PR #26, and you have a demoable app.

## Deployment state
- Live URL: https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/
- Orchestrator URL: https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/
- Last successful deploy: `d0abd0a` via `azure-dev.yml` — 2026-05-17T18:35 UTC (PR #27 merge)
- Current deploy blocker: `deploy.yml` broken (OIDC `environment:dev` federated credential missing — Wanda's diagnosis). **However**, `azure-dev.yml` works and IS deploying on every push to main.
- Frontend served: ✅ HTTP 200
- /api/health: ✅ HTTP 200 `{"status":"ok","voice_provider":"foundry_realtime","tools_loaded":true}`

## UAT loops
| Loop | On main? | Works? | Evidence |
|---|---|---|---|
| A Frontend loads | ✅ | ✅ | `curl` returns 200; nginx serves SPA at live URL |
| B Voice → response | ✅ (partial) | ❌ | `stopTalking()` at `useVoiceSession.ts:287` doesn't send `{type:"stop"}` — orchestrator never gets commit boundary. PR #26 fixes this (not merged). Server VAD + audio commit landed (f9e6576, PR #20). |
| C Text → response | ✅ | ✅ (degraded) | `TextInput.tsx` → `POST /api/turn` → orchestrator dispatches `search_logs` tool call. Tool routing works. **But** log-analyst returns HTTP 400 on `search_logs` — likely argument schema mismatch (model sends `time_range:"today"`, tool may not accept that). Response gracefully degrades to "I couldn't retrieve…" |
| D Transcripts render | ✅ | ✅ | PR #21 merged (c7c3a5e) + PR #22 merged (2051e25). `protocol.ts:57` defines `UserTranscript`, `useVoiceSession.ts:183` handles it, `Transcript.tsx` renders user/assistant bubbles. |

## Top 3 risks for the live demo
1. **Voice loop broken — no commit boundary on mic release.** PR #26 has the fix but is CONFLICTING. Without it, holding spacebar records audio but the orchestrator never transcribes. **Mitigation:** Rebase PR #26 (small — audio.ts + useVoiceSession.ts changes). Fallback: demo via text input only.
2. **Log-analyst 400 on tool calls.** Live test shows `search_logs` gets a 400 from log-analyst. The model sends `{"query":"...","time_range":"today"}` but the tool may reject `time_range` or the search index isn't loaded. **Mitigation:** Check log-analyst container logs (`az containerapp logs show`); verify AI Search index was populated by `postprovision` hook; test tool endpoint directly.
3. **OIDC deploy.yml still broken.** Not blocking (azure-dev.yml works), but if you need branch-protection or environment approvals on deploy day, you'll hit this. **Mitigation:** Add federated credential for `environment:dev` in Entra portal (5 min).

## Outstanding code that gates UAT
- **PR #26** (`fix-spacebar-audio-health`): Spacebar PTT focus guard, `AudioContext.resume()`, stop-frame on mic release, `/api/health` nginx rewrite. Status: CONFLICTING. Owner: Sean to rebase. **This is the P0 — without it, voice demo fails.**
- **PR #30** (`test/playwright-happy-path`): Draft Playwright smoke against live deploy. Nice-to-have, not blocking.
- **PR #27** (Service Disruption Advisor): ✅ MERGED to main (41946c9). Second specialist is live.

## Recommended next 60 minutes for Sean

1. **Rebase PR #26** — it's the only thing blocking voice:
   ```powershell
   cd C:\Users\segayle\repos\mta-ai-hackathon
   git fetch origin
   git checkout anvil/fix-spacebar-audio-health
   git rebase origin/main
   # Resolve conflicts (likely in useVoiceSession.ts and/or audio.ts)
   git push --force-with-lease
   # Merge via GH UI or: gh pr merge 26 --squash
   ```

2. **Diagnose log-analyst 400** — check what arguments `search_logs` actually expects:
   ```powershell
   # Directly test the tool endpoint:
   curl -X POST "https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/api/turn" -H "Content-Type: application/json" -d '{"text":"summarize the most recent incident"}'
   # Check log-analyst container logs:
   az containerapp logs show -n log-analyst -g <rg> --type console --tail 50
   ```

3. **Add OIDC federated credential** (nice-to-have, 5 min):
   - Azure portal → App registration `b2451691-200c-4d8d-b50f-a60396ddb606`
   - Certificates & secrets → Federated credentials → Add
   - Entity: Environment, Name: `dev`
   - This unbreaks `deploy.yml` but `azure-dev.yml` is already deploying.

4. **Verify search index loaded** — the `postprovision` hook runs `load_search_index.ps1`. If the AI Search index is empty, all tool calls will 400/404:
   ```powershell
   az search query-key list --service-name <search-svc> --resource-group <rg>
   # or check via Azure portal → AI Search → Indexes → document count
   ```

## Verdict justification

🟡 Ship with caveats. The app is live, deployed, and the text-input path demonstrates the full orchestrator → specialist → cited-response chain (modulo the 400 on log-analyst which needs a quick schema/index check). Voice is broken on main because `stopTalking()` never sends the commit boundary — but this is a single-PR fix (PR #26) that Sean can rebase in 15 minutes. The deploy pipeline works via `azure-dev.yml` (green on every push). This is not a 🔴 because the demo has a working fallback (text input) and the voice fix is authored and tested — it just needs a conflict resolution. It's not a 🟢 because voice — the headline feature — doesn't work without merging PR #26, and log-analyst tool calls are returning 400 in production.

---

## 2026-05-18 02:18 ET — End of day status

**Assessor:** McManus  ·  **PRs shipped today:** 15+ (see `TOMORROW.md`)

### Live deployment state
- **Frontend:** https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ — ✅ 200 OK
- **Orchestrator:** https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ — ✅ reachable
- **Latest deploy:** commit `ed4136e` via `26010848121` (2026-05-18 ~00:00 ET)
- **Bundle:** `index-JNX-cGYF.js` (or newer — run `Invoke-WebRequest https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/` to verify)

### What's working (post-15-PR avalanche)
- ✅ **Text input** → orchestrator → log-analyst → response with citations (since PR #36, "null-safe specialist responses")
- ✅ **User-turn bubbles** in chat UI (PR #37)
- ✅ **Thinking dots** while assistant thinks (PR #37)
- ✅ **Stop button** visible during streaming (PR #45, "Stop button + auto-interrupt")
- ✅ **Tool-mediated dedupe** — `TextInput` streaming flip + tool result dedup (PR #46–47)
- ✅ **Foundry error frame surfacing** if voice fails (PR #47, "Foundry error frame surfacing")
- ✅ **Language=en pinned** + voice logging telemetry (PR #42)

### What's uncertain (voice loop)
- 🟡 **Voice (mic) transcription:** Transcripts reach the browser (PR #40, "Forward Foundry user transcript") BUT Whisper guesses **Korean instead of English** despite `language=en` pin. Diagnostic telemetry now in place (PR #47). Requires fresh English turn + container logs to diagnose root cause.
- 🟡 **Voice → response:** `stopTalking()` commit boundary landed in PR #45; user partial dedupe landed in PR #47. Still requires real-world test.

### Judging app (separate stack)
- ✅ **GitHub OAuth** live and working (PRs #39–41 pivot from AAD complete)
- ✅ **ADMIN_USERS** env var honored (GitHub usernames, lowercase)
- ✅ **Auto-deploy workflow** in place (`.github/workflows/deploy-judging.yml` on push to main touching `apps/judging/**`)
- 🟡 **First signed-in request to `/api/teams` → 500** — PR #44 added `err.code + detail` to response body; **awaiting error JSON from Sean's next browser DevTools check**

### Recommendation for Tuesday morning
1. **☕ Fresh eyes.** Do NOT iterate on voice tonight.
2. **One English voice turn** against the live frontend → check DevTools WebSocket frames + orchestrator container logs for Whisper issue
3. **Decision:** If voice clearly works → continue voice polish. If Whisper still guesses Korean → **demo text-only** (which is fully functional).
4. **Demo primary modality:** Text input (fully working, no blockers).
5. **Demo stretch:** Working voice if the Korean transcription is solved tomorrow AM.

See `TOMORROW.md` for the full decision tree and rollback nuke option.
