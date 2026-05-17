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


## 🎨 Test coverage health

| Metric | Status |
|--------|--------|
| Failing tests in place | [██████████] 100% |
| Test fixture coverage | [██████████] 100% |
| Citation contract checked | [██████████] 100% |
| Deterministic runs | [██████████] 100% (no flakes) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Banner (Tester) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When test assertions are updated or new fixtures added |
