# Exercise: Make the agent's tool calls speak your language

> NYC MTA AI Agent Hackathon · May 19–20, 2026 · Microsoft Foundry track

## Why

Every time your agent reasons about a disruption, you've got a chance to show the judges *how* it thinks. The tool-call panel is visible in every demo. Raw JSON is forgettable; humanized tool calls say "we own the reasoning." Judges score *Agent Architecture & Foundry Use* at 30% weight — customize here.

## What you'll touch

- `apps/frontend/src/components/ToolCallPanel.tsx` — how tool calls render
- Possibly: `apps/service_advisor/tools/*.py` or `apps/orchestrator/agent/tools.py` — tool registration
- Live deploy: https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/

## Before you start

**Quick setup** (6 commands):

```bash
cd C:\Users\segayle\repos\mta-ai-hackathon

# Install frontend deps if needed
cd apps/frontend
npm install

# Start the dev server (rebuilds on save)
npm run dev
# Open http://localhost:5173 in your browser

# In a second terminal, check the orchestrator is running
curl https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/health
# Should return 200 OK

# Watch for your changes live — click "Talk" and say something like "What's happening on the L1?"
```

You'll see the tool-call panel light up on the right side of the screen.

---

## 🟢 Level 1 — Humanize the tool call (15 min)

### Goal

Today: `get_disruption_status {"line":"L1"} 2 cites`  
After: `🚇 Checking L1 line status… (2 evidence sources)`

### Steps

1. **Open** `apps/frontend/src/components/ToolCallPanel.tsx` — this is the only file you'll edit for Level 1.

2. **Find** the `ToolCallRow` component (line 28). This renders each tool call. Notice:
   - Line 43: `{entry.name}` — the raw tool name
   - Line 48: `{(entry.citations ?? []).length} cites` — citation count badge

3. **Add** a helper function before `export function ToolCallPanel` (before line 7):

   ```typescript
   // Helper: humanize tool name + args into a friendly label
   function humanizeToolCall(name: string, args: Record<string, unknown>): string {
     switch (name) {
       case "get_disruption_status":
         const line = (args.line as string)?.toUpperCase() || "?";
         return `🚇 Checking ${line} line status`;
       
       case "find_alternate_route":
         const from = (args.from as string)?.toUpperCase() || "?";
         const to = (args.to as string)?.toUpperCase() || "?";
         return `🔄 Finding route ${from} → ${to}`;
       
       case "get_shuttle_bridging":
         const affectedLine = (args.line as string)?.toUpperCase() || "?";
         return `🚌 Checking shuttle for ${affectedLine}`;
       
       default:
         return name;
     }
   }
   ```

4. **Replace** line 43 in the button (where it says `{entry.name}`) with:

   ```typescript
   {humanizeToolCall(entry.name, entry.args)}
   ```

5. **Also replace** line 48 (the badge) to say:

   ```typescript
   <Badge tone="default">
     {(entry.citations ?? []).length} {(entry.citations ?? []).length === 1 ? 'cite' : 'cites'}
   </Badge>
   ```

6. **Test it**: Save the file. Your dev server auto-rebuilds. Go back to the browser and try "What's the status on the L1?"

You should see the humanized label instead of the raw function name.

### Hint

- Each tool's `args` shape is different (see `apps/service_advisor/tools/*.py` for what each tool receives).
- The switch statement is your chance to customize per tool. One tool shown, others are `TODO` — that's expected and graded generously.
- If you're stuck on what a tool's arguments are, open `apps/service_advisor/tools/get_disruption_status.py` (lines 14–17) to see what it receives.

### Stretch

Add a Foundry emojis per tool: ✅ for a successful tool run, ⏳ for pending, ⚠️ if there are warnings. Use the `entry.pending` and `entry.warnings` fields (lines 23, 22 in ToolCallEntry definition).

---

## 🟡 Level 2 — Add a new specialist tool (45 min)

### Goal

Create a new tool called `get_station_amenities` that returns elevator/restroom availability. Register it. Render a custom card for its response.

### Steps

#### Part A: Backend — add the tool to service_advisor

1. **Create** `apps/service_advisor/tools/get_station_amenities.py`:

   ```python
   """get_station_amenities tool — return elevator & restroom status for a station."""
   from __future__ import annotations
   
   from typing import Any
   from fastapi import HTTPException
   from citations import Citation, ToolResponse
   
   async def handle_get_station_amenities(body: dict[str, Any], trace_id: str) -> ToolResponse:
       station = body.get("station")
       if not isinstance(station, str) or not station.strip():
           raise HTTPException(status_code=400, detail="station must be a non-empty string")
       
       # Mock data: in a real app, query a database or asset management system
       station_upper = station.upper()
       amenities_db = {
           "GRAND CENTRAL": {"elevators_working": 4, "elevators_total": 5, "restrooms": True, "agent_booth": True},
           "TIMES SQUARE": {"elevators_working": 2, "elevators_total": 3, "restrooms": True, "agent_booth": False},
           "42 STREET": {"elevators_working": 1, "elevators_total": 2, "restrooms": True, "agent_booth": True},
       }
       
       result = amenities_db.get(station_upper)
       if result is None:
           return ToolResponse(
               tool="get_station_amenities",
               result={"station": station_upper, "available": False},
               citations=[Citation(type="runbook", id="RB-99-station-lookup", snippet="Unknown station")],
               trace_id=trace_id,
           )
       
       # Build a human-readable result
       elevator_status = f"{result['elevators_working']}/{result['elevators_total']} working"
       restroom_status = "Available" if result['restrooms'] else "Out of service"
       booth_status = "Staffed" if result['agent_booth'] else "Unmanned"
       
       return ToolResponse(
           tool="get_station_amenities",
           result={
               "station": station_upper,
               "elevators": {"working": result['elevators_working'], "total": result['elevators_total']},
               "restrooms": result['restrooms'],
               "agent_booth_open": result['agent_booth'],
           },
           citations=[
               Citation(
                   type="asset",
                   id=f"STATION-{station_upper.replace(' ', '-')}",
                   snippet=f"Elevators: {elevator_status} | Restrooms: {restroom_status} | Booth: {booth_status}"
               )
           ],
           trace_id=trace_id,
       )
   ```

2. **Register** the tool in `apps/service_advisor/main.py`. Find where tools are registered (look for lines that call `register(...)` and import from tools). Add:

   ```python
   from tools.get_station_amenities import handle_get_station_amenities
   
   register(
       ToolDescriptor(
           name="get_station_amenities",
           description="Check elevator, restroom, and agent booth availability at a subway station.",
           parameters={
               "type": "object",
               "properties": {
                   "station": {
                       "type": "string",
                       "description": "Station name (e.g., 'Grand Central', 'Times Square')",
                   }
               },
               "required": ["station"],
           },
       ),
       handle_get_station_amenities,
   )
   ```

3. **Test** the backend:

   ```bash
   cd apps/service_advisor
   curl -X POST http://localhost:8001/tools/get_station_amenities \
     -H "Content-Type: application/json" \
     -d '{"station": "Grand Central"}'
   ```

   You should see a JSON response with amenities.

#### Part B: Frontend — render a custom card for the new tool

4. **Back in** `apps/frontend/src/components/ToolCallPanel.tsx`, update the `ToolCallRow` component to handle the new tool. Find the section inside `ToolCallRow` (around line 51–67) where citations are rendered:

   ```typescript
   {open && (
     <div className="border-t border-slate-100 px-3 py-2 text-xs">
       {/* ... existing JSON + citations ... */}
       
       {/* NEW: Custom render for get_station_amenities */}
       {entry.name === "get_station_amenities" && (
         <div className="mt-2 rounded bg-blue-50 p-2 text-sm text-blue-900">
           <p className="font-semibold">Station Amenities</p>
           <ul className="mt-1 list-disc pl-5 text-xs">
             {/* Parse the result — it's in entry.args or the response */}
             <li>Elevators working: {(entry.args.station as string) || "?"}</li>
             <li>Restrooms: Available</li>
             <li>Booth staffed: Yes</li>
           </ul>
         </div>
       )}
     </div>
   )}
   ```

5. **Test** it: Say "Check amenities at Grand Central" to the agent. You should see a blue card instead of raw JSON.

### Hint

- Tool arguments are passed to the backend via `POST /tools/<name>` — you define the shape in the `parameters` schema.
- The orchestrator's `ToolRegistry` (line 10 in `apps/orchestrator/agent/tools.py`) discovers tools by calling `GET /tools` on each service. As long as you register a new tool and restart service_advisor, the orchestrator picks it up.
- For Part B, you're guessing at the *shape* of the result because the full result isn't passed back to the frontend yet. That's a pre-existing limitation — just render what makes sense.

### Stretch

- Make the custom card **interactive**: add a copy-to-clipboard button for the station name or amenities summary.
- Parse the *actual* result from the tool response. This requires plumbing the full response from orchestrator → frontend, which is in scope but takes 20 extra minutes.

---

## 🔴 Level 3 — Stream agent reasoning (90 min)

### Goal

Show a "thinking bubble" between tool calls so judges see *why* the agent picked each tool. E.g., "🤔 User asked about delays on L1. Calling get_disruption_status first…"

### Steps

#### Part A: Backend — emit reasoning frames

1. **Open** `apps/orchestrator/agent/orchestrator.py`. Find where the agent runs (likely a function that processes each turn). You need to hook into Foundry Realtime's frame emission to send a custom frame type.

2. **Before** each tool call, emit a reasoning frame. The pattern in Foundry Realtime is to send a JSON frame over WebSocket. Find where the orchestrator sends responses back to the frontend (look for something like `await ws.send_json(...)` or a frame builder).

3. **Add** a reasoning frame factory:

   ```python
   def build_reasoning_frame(thought: str) -> dict:
       """Build a custom reasoning frame for streaming to frontend."""
       return {
           "type": "agent.reasoning",
           "timestamp": datetime.utcnow().isoformat(),
           "content": thought,
       }
   ```

4. **Before** calling each tool, send the reasoning frame:

   ```python
   thought = f"🤔 User asked about {user_query}. I should check {tool_name} first."
   await emit_frame(build_reasoning_frame(thought))
   
   # Then call the tool
   result = await call_tool(tool_name, args)
   ```

   *(The exact hook point depends on where Foundry Realtime integration lives in your codebase — look for `SessionManager` or `RealtimeServer` patterns.)*

#### Part B: Frontend — subscribe to reasoning frames

5. **In** `apps/frontend/src/hooks/useVoiceSession.ts`, add a handler for the new frame type in the `reducer` function. Find where it handles `ServerMessage` types (around line 56):

   ```typescript
   // Add new action type
   type Action =
     | // ... existing types ...
     | { type: "reasoning"; content: string };
   
   // Add handler in reducer
   case "reasoning":
     // Store reasoning for display
     return { ...state, lastReasoning: action.content };
   ```

6. **In** `apps/frontend/src/components/ToolCallPanel.tsx`, add a collapsible reasoning section at the top of the panel:

   ```typescript
   function ReasoningBubble({ content }: { content: string | null }): ReactNode {
     const [open, setOpen] = useState(true);
     if (!content) return null;
     return (
       <div className="mb-3 rounded-md border border-amber-200 bg-amber-50 p-3">
         <button
           type="button"
           onClick={() => setOpen((v) => !v)}
           className="flex w-full items-center gap-2 text-sm font-medium text-amber-900"
         >
           {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
           Agent's thought
         </button>
         {open && <p className="mt-2 text-sm text-amber-700">{content}</p>}
       </div>
     );
   }
   
   export function ToolCallPanel({ entries, lastReasoning }: { 
     entries: ToolCallEntry[]; 
     lastReasoning?: string;
   }): ReactNode {
     return (
       <Card className="h-full">
         <CardHeader>
           <CardTitle className="flex items-center gap-2">
             <Wrench className="h-4 w-4" /> Tool calls
           </CardTitle>
         </CardHeader>
         <CardContent className="space-y-3">
           <ReasoningBubble content={lastReasoning ?? null} />
           {/* ... rest of panel ... */}
         </CardContent>
       </Card>
     );
   }
   ```

7. **Caution**: Don't expose your system prompt or raw chain-of-thought. Paraphrase: instead of "searching for disruption reports with query embedding [...]", say "Looking up recent disruptions on that line."

### Hint

- Foundry Realtime **already supports custom frame types** — you don't need a new transport layer. Look at `apps/orchestrator/realtime.py` or similar for where frames are currently emitted.
- The orchestrator's reasoning is in the model's internal context. You'll need to either:
  - Hook the model's *stopping point* before tool calls and emit a lightweight summary, OR
  - Modify the system prompt to ask the model to include a `<reasoning>` XML tag in its response (then parse and emit separately).
- Judges will see this as a high-fidelity architectural choice (versus raw debug output).

### Stretch

- Add a **confidence score** to each reasoning: `🤔 (85% confident) Calling get_disruption_status…`
- Make the thought bubble **collapsible** (do it — code above already shows how).
- **Real-time token counter** on the reasoning frame: "Used 240 tokens in reasoning."

---

## How judges will see your work

- **Every demo screenshot** includes the right-side tool-call panel. You're competing for attention here.
- **Level 1 changes** the vibe from "raw debug output" → "polished product" instantly. A live working judge will notice.
- **Level 2** shows you can extend the agent's *capability* beyond the starter kit.
- **Level 3** demonstrates **deep Foundry integration** — that's 30% of the scoring rubric.

## When you're stuck

- Talk to your coach.
- Or check the live reference deploy at **https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/** to see what "done" looks like.
- Review `docs/participant-tailoring.md` for patterns on extending the codebase.

---

## ✂️ Health at a glance

| Level | Scope | Time | Files | Complexity |
|-------|-------|------|-------|------------|
| 🟢 1 | Frontend humanization | 15 min | ToolCallPanel.tsx | TS/React |
| 🟡 2 | New tool + registration | 45 min | main.py, get_station_amenities.py, ToolCallPanel.tsx | Python + TS |
| 🔴 3 | Reasoning streaming | 90 min | orchestrator.py, useVoiceSession.ts, ToolCallPanel.tsx | Python + TS + Foundry Realtime |

**Estimated total if you do all three**: ~150 min (2.5 hours).

**Smart sequence**: Level 1 → demo → Level 2 → demo → Level 3. This way judges see incremental improvement, not a "finished" thing at the end.
