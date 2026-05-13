# Extension 06 — Enable the Modernize-PR GitHub Actions Workflow

**Time:** ~15 min · **Use cases:** #6 (.NET 4.8→10), #8 (GH Actions pipeline) · **Difficulty:** Easy

## What

The skeleton ships a GitHub Actions workflow file at
`.github/workflows/modernize-pr.yml.disabled`. It is intentionally disabled (wrong extension,
no active trigger). Your team **renames it** to `.github/workflows/modernize-pr.yml`,
**sets a real trigger** (`on: workflow_dispatch` at minimum), and **removes any `if: false`
guard** that would prevent it from running. The workflow uses Copilot CLI / AI-assisted checks
to comment on PRs that touch `legacy/`.

## Why

Use case #6 requires an automated gate that catches .NET 4.8 patterns before they're merged.
Use case #8 requires a working CI pipeline the team can demo. Enabling this workflow in 15 minutes
shows how a dormant automation asset can be activated with minimal effort — and how teams can
verify workflow integrity with tests.

## Try this

1. **Rename the file.**
   ```bash
   mv .github/workflows/modernize-pr.yml.disabled .github/workflows/modernize-pr.yml
   ```
2. **Open the file** and verify the `on:` block. Add `workflow_dispatch:` if it's missing.
   Remove any line like `if: false` at the job or workflow level.
3. **Commit and push** (or just confirm locally that the tests pass — no push required for the
   hackathon demo).
4. **Run the tests** to confirm the workflow file is structurally correct.

## Prompt Copilot like this

```
1. "I have a file at .github/workflows/modernize-pr.yml. Open it and tell me: does it have an
   'on:' trigger defined? Is there an 'if: false' guard anywhere? What changes do I need to
   make so it runs when I dispatch it manually?"

2. "Add a workflow_dispatch trigger to .github/workflows/modernize-pr.yml if one is not already
   present. Show me only the diff."

3. "Write a Python test using pyyaml that asserts modernize-pr.yml has workflow_dispatch in its
   on: block and does not have 'if: false' anywhere in the file."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/06_enable_modernize_pr/tests/ -v
```

All tests **fail** until the workflow file is renamed and corrected.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [05 — Wire Legacy to Agent](../05_wire_legacy_to_agent/README.md) · Next: [07 — Frontend Rebrand](../07_frontend_rebrand/README.md)
