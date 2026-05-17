# SQUAD Decisions Log

Track: $track | Cohort: $cohort | Fiscal Year: $fiscal_year | Season: $season

Decisions are grouped by session (D-XXX) and tagged by agent + decision type.

---

## D-010 — Session 2026-05-17 (T'Challa, Okoye, Stark, Maximoff)

### D-010.1 — PR Triage + Merge Batch (T'Challa / Stark)
**Status:** Partial completion.

**Merge-ready count:** 3 (#26 UAT, #31 docs, #32 docs).  
**Status:** #26 held (conflicts); #31, #32 closed (already merged via #28/#33).  
**Action:** Closed #19, #25 (superseded by #26). Held #26 for author rebase.

**Next:** (#26 unblocked → P0 for Tuesday 5/19 UAT demo).

---

### D-010.2 — Judging App Deploy (Okoye)
**Status:** ✅ Complete.

**Live URL:** https://mango-hill-0ee13cb0f.7.azurestaticapps.net/ (HTTP 200).  
**Provision time:** 3m04s.  
**Fix applied:** Added minimal \pps/judging/src/package.json\ (no-op) to unblock SWA packager npm walk.  
**Bootstrap admin:** segayle@microsoft.com (SWA app setting).

**Blockers (Sean's lane):** AAD tenant restriction + CLIENT_ID/SECRET setup.

---

### D-010.3 — Deploy Workflow Diagnosis (Maximoff)
**Status:** ✅ Diagnosed.

**Root cause:** PR #29 added \nvironment: dev\ to deploy workflow; Entra app b2451691-200c-4d8d-b50f-a60396ddb606 has no federated credential for subject \epo:DevPost-Test-Hackathon/crosstown-app:environment:dev\ (AADSTS700213).

**Fix:** Azure portal only — add federated credential (Entity=Environment, name=\dev\).  
**File:** \pps/orchestrator/DEPLOY_DIAGNOSIS_2026-05-17.md\ (historical record).

---

### D-010.4 — PR #28 R3 Review (Anvil)
**Status:** ✅ Approve with nits.

**47doors-comparison.md:** All R2 rejects fixed. Nit (pre-existing): line 169 Dockerfile HEALTHCHECK row should read \✅ Yes\ (PR #29 already merged HEALTHCHECK before Banner's commit).

**Approval:** Comment posted (GitHub CLI self-approval blocked). Sean to click Approve in UI before squash-merge.

---

### D-010.5 — PR #20 Shipped (Okoye)
**Status:** ✅ Merged.

**Commit:** f9e6576 (server VAD + explicit audio commit).  
**Conflict:** Trivial rebase in foundry_realtime.py (session_error guard + transcription update — kept both).  
**CI:** All green. CD: https://github.com/DevPost-Test-Hackathon/crosstown-app/actions/runs/25994066482 ✅.

**Anvil verdict:** Approve with nits (commit_audio untested, session_error path untested — pre-existing risks, no regression).

---

### D-010.6 — PR #22 Shipped (Okoye)
**Status:** ✅ Merged.

**Commit:** 2051e25 (user-turn transcripts — orchestrator backend).  
**Conflicts:** 2 in settings.py + foundry_realtime.py (kept safe defaults + both comment blocks).  
**Functional diff:** Only 2 comment lines after resolution; 13+ tests + handlers already on main.

**CI:** All green (foundry-evaluators skipped — no AZURE_OPENAI_ENDPOINT var).  
**CD:** ✅ 2m40s success.

**Next:** #21 (frontend render transcripts) + #19 (stop-frame).

---

**Session lead:** T'Challa | **Archive:** decisions-2026-05-17.md (64.8 KB)

