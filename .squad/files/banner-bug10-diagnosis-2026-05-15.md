# Bug #10 Diagnosis — `detect_pattern` 400 from log-analyst

**Date:** 2026-05-15
**Owner:** Banner
**Severity:** P0 (blocks Phase 2.5 live eval gate — 1/3 tool paths broken)
**Confidence:** HIGH

## Verbatim repro

Live POST to deployed orchestrator (`rg-crosstown-dryrun-may15`, swedencentral, revision
post-PR-#15):

```
POST https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/api/turn
{"text": "Look at log L-001234 and tell me if it's part of a known pattern."}
```

Response (truncated):

```json
{
  "text": "...",
  "citations": [],
  "tool_calls": [
    {
      "name": "detect_pattern",
      "arguments": {"seed_log_id": "L-001234"},
      "call_id": "call_uzklXIWYDBcHwqIB"
    }
  ],
  "warnings": [
    "Client error '400 Bad Request' for url 'http://log-analyst.internal.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/tools/detect_pattern'",
    "uncited"
  ]
}
```

A previous repro with the prompt `"Was there a cascading_doors_then_dwell pattern on line L1 today?"`
produced `arguments: {"pattern": "cascading_doors_then_dwell", "window_minutes": 1440}` — also
without `log_id`, also 400. **The model is inventing argument names because it has no schema.**

## What log-analyst expects

`apps/log_analyst/tools/detect_pattern.py`:

```python
async def handle_detect_pattern(body: dict[str, Any], trace_id: str) -> ToolResponse:
    log_id = body.get("log_id")
    if not isinstance(log_id, str) or not log_id.strip():
        raise HTTPException(status_code=400, detail="log_id must be a non-empty string")
    window_minutes = body.get("window_minutes", 60)
    ...
```

Tool descriptor (`apps/log_analyst/tools/__init__.py`):

```python
register(ToolDescriptor(
    name="detect_pattern",
    description="...",
    input_schema={
        "type": "object",
        "properties": {
            "log_id": {"type": "string"},
            "window_minutes": {"type": "integer", "minimum": 1, "default": 60},
        },
        "required": ["log_id"],
    },
), handle_detect_pattern)
```

Required: `log_id` (non-empty string). The Pydantic `ToolDescriptor` (`citations.py`) serializes
field as `input_schema`.

## What orchestrator actually sent

The orchestrator dispatches whatever args the Realtime model produced. The model produced
`{"seed_log_id": "L-001234"}` — not the required `log_id`. log-analyst correctly rejects with
`400 "log_id must be a non-empty string"`.

## Root cause (the orchestrator schema-passthrough bug)

`apps/orchestrator/agent/tools.py:24-53` — `ToolRegistry.load()` reads `/tools` from log-analyst
and builds `ToolSpec`s that go into `session.update`'s tool registration with the Realtime model.
At line 45:

```python
parameters=dict(t.get("parameters", {})) or {"type": "object", "properties": {}},
```

It reads field `parameters`. log-analyst returns `input_schema` (per `ToolDescriptor.input_schema`
in `apps/log_analyst/citations.py:36-39`). **`t.get("parameters", {})` is always `{}` →
falsy → falls through to the empty default.**

**Effect:** the Realtime model is told all three tools exist with empty parameter schemas. It
guesses arg names from the tool name/description. For `search_logs` (`query` is obvious) and
`summarize_incident` (`incident_id` is obvious) it guesses correctly — those paths work. For
`detect_pattern` it has no way to know the seed field is named `log_id`, so it invents
`seed_log_id` (in this run) or omits it entirely (`pattern`/`window_minutes` only, prior run)
and log-analyst 400s.

This bug has been latent since the orchestrator+log_analyst registry contract was first wired;
it surfaced only because Bug #9 (tool dispatch race) was hiding it. With Bug #9 fixed, the model
now actually dispatches detect_pattern — and the missing schema is exposed.

## Diff (expected vs actual payload)

| Field | Sent by orchestrator | Expected by log-analyst |
|---|---|---|
| `log_id` | ❌ missing (model sent `seed_log_id`) | ✅ required, non-empty string |
| `window_minutes` | optional, default 60 | optional, default 60 |

## Fix (1 file, 1 line)

`apps/orchestrator/agent/tools.py:45` — accept both `input_schema` (real log-analyst format) and
`parameters` (existing test-mock format):

```python
parameters=dict(t.get("input_schema") or t.get("parameters") or {}) or {
    "type": "object",
    "properties": {},
},
```

Backwards compatible with existing `test_tools_dispatch.py::test_registry_load` (which mocks
`parameters`). After fix, the Realtime model sees the real JSON Schema for every tool, including
`log_id` as required for `detect_pattern`, and will dispatch with the correct field name.

## Confidence

**HIGH.** Verified end-to-end:
- Read log-analyst handler — confirmed `log_id` is the required field.
- Read log-analyst registration — confirmed descriptor exposes `input_schema`.
- Read `ToolDescriptor` Pydantic model — confirmed field name is `input_schema` on the wire.
- Read orchestrator loader — confirmed it reads `parameters`, never `input_schema`.
- Live repro 2× — model invents arg names (`pattern`+`window_minutes`, then `seed_log_id`).
- The same bug applies to all 3 tools, but only `detect_pattern` is observable because its
  required arg name (`log_id`) is not obvious from name/description; `search_logs.query` and
  `summarize_incident.incident_id` are obvious enough that the model still guesses correctly.

## Ship/escalate

**SHIP.** ≤10 lines in 1 file, clear schema bug, no contract change (just plumbing the schema
that was already there). Branch: `squad/fix-log-analyst-detect-pattern-400` (stacked on
PR #15).
