# Tests — Extension 07

## How to run

```bash
# From the repo root (requires Node.js + vitest in apps/frontend)
npx vitest run docs/extensions/07_frontend_rebrand/tests/

# Or via npm if the frontend package.json has a test script:
npm test --prefix apps/frontend -- --run
```

## Expected state before completing the extension

All tests **fail** — `theme.ts` and `IncidentDetailView.tsx` don't exist yet.

## Expected state after completing the extension

All tests pass.

## Dependencies

These tests use `vitest` and `@testing-library/react`, which are included in the
`apps/frontend` package. Run `npm install --prefix apps/frontend` if you haven't already.
