# Frontend E2E tests

This directory is **Playwright territory**, not Vitest.

- Specs here use `@playwright/test` (`test.describe`, `test(...)`, `expect` from Playwright).
- They are intentionally excluded from Vitest collection via `vite.config.ts` (`test.exclude` includes `**/e2e/**`). If Vitest tries to collect a Playwright spec it errors with: _"Playwright Test did not expect test.describe() to be called here."_
- Run E2E suites separately:

```bash
npx playwright test                # all e2e specs
npx playwright test e2e/mic-button.spec.ts   # single file
```

Unit / component tests live under `tests/` and run via `npm test -- --run`.
