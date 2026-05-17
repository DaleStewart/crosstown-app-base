# Acceptance — Extension 07

You're done when **ALL** of the following are true.

- [ ] `apps/frontend/src/theme.ts` (or equivalent) exports an object with at least `brandPrimary`, `brandSecondary`, and `brandBackground` colour tokens.
- [ ] `apps/frontend/src/components/IncidentDetailView.tsx` exists and exports a React component as its default export.
- [ ] `IncidentDetailView` accepts and renders props: `id`, `line`, `description`, `status`, `citations`.
- [ ] A route `/incidents/:id` is registered in the frontend router and renders `IncidentDetailView`.
- [ ] `npm run build --prefix apps/frontend` (or `vite build`) exits with code 0 (no TypeScript errors).
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Start the frontend: `npm run dev --prefix apps/frontend`
2. Open `http://localhost:5173/incidents/1` in a browser.
3. Show the rendered `IncidentDetailView` with fictional incident data for line L1.
4. Open DevTools → Network, show there are no 500 errors.
5. Run the tests:
   ```bash
   npx vitest run docs/extensions/07_frontend_rebrand/tests/
   ```
   Show all green.


## 🎨 Acceptance criteria

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Edge cases listed | [██████████] 100% |
| Pass/fail thresholds | [██████████] 100% |
| Reviewer assigned | Parker (Frontend) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Parker (Frontend) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When acceptance criteria are revisited or team completes extension |
