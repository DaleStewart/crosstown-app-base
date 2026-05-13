# Participant Tailoring — 3 thirty-minute recipes

> **For forking teams only.** If you're greenfielding in your Devpost sandbox, treat these as architectural references — lift what's useful, ignore the rest.

These three recipes are the fastest paths from the Hour-1 demo to a demo that looks like *your* submitted use case. Pick one; finish it before lunch on Day 1.

---

## Recipe 1 — Swap the Specialty (30 min)

**Goal:** Replace what the Log Analyst is good at without touching the orchestrator or frontend.

**Best for:** use cases #1 (log analyzer), #2 (SCADA monitoring), #3 (DB health reports).

**Steps**
1. Open `apps/log_analyst/agent.py`. Find the `SYSTEM_PROMPT` constant.
2. Rewrite it in 5–10 sentences in your domain's voice: "You are a SCADA health analyst. You answer in three sections: signal, evidence, next action…"
3. Open `apps/log_analyst/tools/`. Each tool is a single file. Rename `summarize_incident.py` → `summarize_<your_thing>.py` and update its body. Keep the function signature `def tool(...) -> dict` and **always include `citations` in the return**.
4. Update the tool registry in `apps/log_analyst/tool_router.py` to expose the new tool name.
5. Run `evals/runner.py --service log_analyst --update-cassettes` to refresh the golden cassettes (your scenarios will fail until you also do Extension 08).
6. Demo: the voice flow is unchanged; the agent now answers in your domain.

**Prompt Copilot like this:**
```
Open apps/log_analyst/agent.py. Rewrite SYSTEM_PROMPT for a SCADA distributed-system
health analyst at a metro rail authority. Keep the same three-section answer shape
(signal / evidence / next action) and the requirement to cite every claim by
log_id or runbook_id.
```

---

## Recipe 2 — Swap the Legacy App (30 min)

**Goal:** Drop your team's legacy slice in front of Copilot and ship a modernized API.

**Best for:** use cases #4 (PCICS), #5 (.NET 4.8 → .NET 10), #7 (on-prem web/desktop), #10 (UI modernization).

**Steps**
1. Drop your legacy controller (a single file is plenty for a demo) into `legacy/`. The repo ships with `legacy/README.md` explaining the format.
2. Follow the Copilot prompts in `docs/extensions/04_legacy_modernization/README.md`.
3. Once you have a working `apps/<your_service>/main.py`, add it as a service in `azure.yaml`.
4. Register it as a tool on the Log Analyst via `apps/log_analyst/tool_router.py` (see Extension 05).
5. Demo: ask the voice agent something that requires the modernized service; watch the tool-call panel light up.

**Prompt Copilot like this:**
```
Here is legacy/SampleController.cs (.NET Framework 4.8 MVC, on-prem SQL).
Generate an equivalent FastAPI service under apps/sample/ using SQLAlchemy
async + asyncpg. Preserve the route paths and JSON shapes. Add a Dockerfile
based on apps/log_analyst/Dockerfile. Add a pytest for each route.
```

---

## Recipe 3 — Swap the Data Source (30 min)

**Goal:** Ground the agent on your team's mock dataset instead of the shipped train-control logs.

**Best for:** use cases #4 (data warehouse), #6 (ELT modernization), #11 (data + reports).

**Steps**
1. Generate or paste your mock data into `data/<your_corpus>/` (JSONL preferred). **Headerline must say `# MOCK DATA — NOT FROM <ORG>`**.
2. Edit `scripts/load_search_index.py` — add an index definition and a loader function for your corpus.
3. Re-run the loader: `python scripts/load_search_index.py`.
4. Update `apps/log_analyst/tools/search_logs.py` (or copy it to `search_<your_thing>.py`) and point at the new index name.
5. Demo: ask the agent something that lives only in your dataset.

**Prompt Copilot like this:**
```
Read scripts/load_search_index.py. Add a build_<your>_index() function and a
load_<your>() function that indexes data/<your_corpus>/*.jsonl. Use the same
DefaultAzureCredential pattern. Wire it into main().
```

---

## After you finish a recipe

You're set up for the extensions. The 9 [extension folders](extensions/) layer on top of these recipes — pick the ones that map to your use case in [use-case-map.md](use-case-map.md).

If you completed Recipe 1 → try Extension 01 (add a second specialist) or Extension 03 (add a fourth tool).
If you completed Recipe 2 → try Extension 05 (wire the modernized API as a tool) or Extension 06 (enable the modernize-PR workflow).
If you completed Recipe 3 → try Extension 02 (swap grounding corpus — formalized) or Extension 08 (custom evals for your domain).
