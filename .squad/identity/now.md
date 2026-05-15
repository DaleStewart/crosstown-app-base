---
updated_at: 2026-05-15T13:48:14Z
focus_area: Foundry Realtime model upgrade — gpt-realtime-1.5 PR open
active_issues:
  - NONE (PR awaiting CI + review)
---

# Session — 2026-05-15 · Foundry Realtime Model Upgrade

**Okoye verified and submitted PR for gpt-4o-realtime-preview → gpt-realtime-1.5 swap.** All verification gates (Bicep, ruff, mypy --strict, pytest, frame schemas) passed. Branch: `squad/swap-realtime-to-gpt-realtime-1.5`. Decision D-009 adopted; decision D-010 (Maximoff instruction superseded) adopted.

## Next Steps

1. Partner should `azd up` against test subscription to confirm regional availability of `gpt-realtime-1.5-2026-02-23` deployment.
2. Cassettes in `evals/` may need refresh if WS event shape differs in live mode vs. offline.
3. Optional: Test orchestrator realtime end-to-end with new model.
4. Untracked `.github/copilot-instructions.md` pending separate decision (not in scope of this session).

See `.squad/log/2026-05-15-realtime-model-swap.md` for full session summary.

