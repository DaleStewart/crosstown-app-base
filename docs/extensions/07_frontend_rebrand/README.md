# Extension 07 — Frontend Rebrand

**Time:** ~45 min · **Use cases:** #7 (on-prem UI mod) · **Difficulty:** Medium

## What

The skeleton's React frontend (`apps/frontend/`) uses default styling and has no incident-detail
view. This extension has your team:

1. **Apply a custom theme** — update the design token file (or Tailwind config) with fictional
   "RailOps" brand colours and typography.
2. **Build an `IncidentDetailView` component** — a new React component that renders a single
   incident's details (id, line, description, status, and a citations list) received as props.
3. **Integrate the component** into the main app so it is reachable at a route such as
   `/incidents/:id`.

No backend changes are needed — the component can use mock data.

## Why

Use case #7 imagines on-premises operators who need a purpose-built UI rather than a generic
chat interface. This extension shows how a small set of brand/UX changes transforms the
skeleton into something that feels domain-specific — and how GitHub Copilot can accelerate
React work even for developers who don't normally write frontend code.

## Try this

1. **Locate the theme file.**
   Look in `apps/frontend/src/` for a file named `theme.ts`, `tokens.ts`, `tailwind.config.js`,
   or similar. If none exists, create `apps/frontend/src/theme.ts`.
2. **Add brand tokens.**
   At minimum define: `brandPrimary`, `brandSecondary`, `brandBackground` (colour strings).
   Example values: `"#1a3c5e"`, `"#f5a623"`, `"#f0f4f8"`.
3. **Create the IncidentDetailView component.**
   Create `apps/frontend/src/components/IncidentDetailView.tsx` with a default export that
   accepts props: `{ id: number; line: string; description: string; status: string; citations: string[] }`.
4. **Register the route.**
   In `apps/frontend/src/App.tsx` (or the router file) add a route `/incidents/:id` that
   renders `<IncidentDetailView>` with mock data.
5. **Run the frontend tests.**
   ```bash
   npm test --prefix apps/frontend -- --run
   ```

## Prompt Copilot like this

```
1. "In apps/frontend/src/, create a file called theme.ts that exports a const called
   brandTokens with at least three colour fields: brandPrimary ('#1a3c5e'),
   brandSecondary ('#f5a623'), and brandBackground ('#f0f4f8'). Add a brief JSDoc comment
   explaining what each token is for."

2. "Create a React functional component at apps/frontend/src/components/IncidentDetailView.tsx.
   It should accept props: id (number), line (string), description (string), status (string),
   citations (string[]). Render each field in a labelled div and map citations to a <ul>.
   Use TypeScript. Do not add any styling framework — plain className strings are fine."

3. "In apps/frontend/src/App.tsx, add a React Router route at /incidents/:id that renders
   <IncidentDetailView> with hardcoded mock props for now. Import IncidentDetailView from
   './components/IncidentDetailView'."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
npm test --prefix apps/frontend -- --run docs/extensions/07_frontend_rebrand
```

Or, if the frontend test runner is vitest:

```bash
npx vitest run docs/extensions/07_frontend_rebrand/tests/
```

All tests **fail** until the theme and component are created.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [06 — Enable Modernize PR](../06_enable_modernize_pr/README.md) · Next: [08 — Custom Evals](../08_custom_evals/README.md)
