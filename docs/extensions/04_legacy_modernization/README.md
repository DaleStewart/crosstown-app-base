# Extension 04 — Legacy Modernization (ASP.NET 4.8 → FastAPI)

**Time:** ~60 min · **Use cases:** #5 (PCICS), #6 (.NET 4.8→10), #7 (on-prem) · **Difficulty:** Hard

## What

A fictional legacy ASP.NET 4.8 controller (`legacy/SampleController.cs`) is provided as a
starting snippet below. Your team **pastes it into the repo**, then uses GitHub Copilot to
translate it into a Python FastAPI service at `apps/legacy_service/main.py`. The goal is not
a perfect port — it's to experience Copilot-assisted modernization and understand what changes
(data shapes, auth patterns, error handling) need human review.

## Legacy snippet — paste this into `legacy/SampleController.cs`

```csharp
using System.Web.Http;

namespace Pcics.Controllers
{
    [RoutePrefix("api/incidents")]
    public class SampleController : ApiController
    {
        // GET api/incidents
        [HttpGet, Route("")]
        public IHttpActionResult GetAll()
        {
            // TODO: replace with real DB call
            var incidents = new[]
            {
                new { Id = 1, Line = "L1", Description = "Signal fault at sector 4", Status = "open" },
                new { Id = 2, Line = "L2", Description = "SCADA timeout bridge-7", Status = "resolved" },
            };
            return Ok(incidents);
        }

        // GET api/incidents/{id}
        [HttpGet, Route("{id:int}")]
        public IHttpActionResult GetById(int id)
        {
            if (id <= 0) return BadRequest("id must be a positive integer");
            // TODO: replace with real DB call
            return Ok(new { Id = id, Line = "L3", Description = "Mock incident", Status = "open" });
        }

        // POST api/incidents
        [HttpPost, Route("")]
        public IHttpActionResult Create([FromBody] IncidentDto dto)
        {
            if (dto == null) return BadRequest("body required");
            return Created($"api/incidents/99", new { Id = 99, dto.Line, dto.Description, Status = "open" });
        }
    }

    public class IncidentDto
    {
        public string Line { get; set; }
        public string Description { get; set; }
    }
}
```

## Why

Use cases #5, #6, and #7 all involve bringing legacy on-premises code into the modern
agent-based architecture. Practicing the mechanical steps (paste → prompt → review → test)
with a small, safe snippet builds the muscle memory that teams need for larger real-world ports.

## Try this

1. **Save the snippet.**
   Copy the C# block above and save it to `legacy/SampleController.cs`.
2. **Open GitHub Copilot Chat** and use the prompts below to generate `apps/legacy_service/main.py`.
3. **Review the generated code** — check error handling, response shapes, and that only fictional
   data (L1/L2/L3) is referenced.
4. **Wire up the FastAPI routes** so that `GET /incidents`, `GET /incidents/{id}`, and
   `POST /incidents` all return HTTP 200/201.
5. **Run the tests** to confirm the routes behave equivalently to the C# original.

## Prompt Copilot like this

```
1. "Read legacy/SampleController.cs. Translate it to a Python FastAPI app at
   apps/legacy_service/main.py. Keep the same URL paths (/incidents, /incidents/{id}).
   Use Pydantic models for request/response bodies. Add a /health route that returns
   {\"status\": \"ok\"}. Do not connect to a real database — use an in-memory list."

2. "The generated apps/legacy_service/main.py uses route /api/incidents but the tests expect
   /incidents. Fix the route prefix so it matches the test expectations in
   docs/extensions/04_legacy_modernization/tests/test_legacy_service.py."

3. "Add a Pydantic response model called IncidentResponse with fields id (int), line (str),
   description (str), status (str) to apps/legacy_service/main.py, and annotate all three
   route handlers with it."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/04_legacy_modernization/tests/ -v
```

All tests **fail** until `legacy/SampleController.cs` and `apps/legacy_service/main.py` exist.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [03 — Add Tool](../03_add_tool/README.md) · Next: [05 — Wire Legacy to Agent](../05_wire_legacy_to_agent/README.md)
