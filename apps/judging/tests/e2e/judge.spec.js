// @ts-check
const { test, expect } = require('@playwright/test');
const { stubAuth, sampleTeams, jsonRoute } = require('./_fixtures');

test.describe('judge page', function () {
  test.beforeEach(async function ({ page }) {
    await stubAuth(page, 'judge');
    await page.route('**/api/teams**', function (route) {
      if (route.request().method() === 'GET') {
        return jsonRoute(sampleTeams())(route);
      }
      return route.fallback();
    });
    await page.route('**/api/myscores**', jsonRoute([]));
  });

  test('team picker loads when no team selected', async function ({ page }) {
    await page.goto('/judge.html?track=azure');

    const grid = page.locator('#team-grid');
    await expect(grid).toBeVisible();
    await expect(page.locator('#team-grid .team-card')).toHaveCount(3);
    await expect(grid).toContainText('Team Aurora');
    await expect(grid).toContainText('Team Borealis');
    await expect(grid).toContainText('Team Cosmos');
  });

  test('submit enables when all 5 criteria scored, posts /api/score, returns to picker', async function ({ page }) {
    /** @type {any} */
    let posted = null;
    await page.route('**/api/score', function (route) {
      if (route.request().method() === 'POST') {
        try { posted = JSON.parse(route.request().postData() || '{}'); } catch (_) { posted = {}; }
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ ok: true })
        });
      }
      return route.fallback();
    });

    await page.goto('/judge.html?track=azure&team=t1');

    const submit = page.locator('#submit-btn');
    await expect(submit).toBeDisabled();

    const criteriaIds = ['alignment', 'architecture', 'reliability', 'ux', 'demo'];
    for (const cid of criteriaIds) {
      await page.locator('#btn-' + cid + '-5').click();
    }

    await expect(submit).toBeEnabled();
    await submit.click();

    // After a successful POST judge.html redirects back to the picker.
    await page.waitForURL(/\/judge\.html\?track=azure$/, { timeout: 5000 });
    await expect(page.locator('#picker-view')).toBeVisible();

    expect(posted).not.toBeNull();
    expect(posted.teamId).toBe('t1');
    expect(posted.track).toBe('azure');
    expect(posted.criteria).toEqual({
      alignment: 5,
      architecture: 5,
      reliability: 5,
      ux: 5,
      demo: 5
    });
  });

  test('locked track shows banner when /api/score returns 423', async function ({ page }) {
    await page.route('**/api/score', function (route) {
      if (route.request().method() === 'POST') {
        return route.fulfill({
          status: 423,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'locked' })
        });
      }
      return route.fallback();
    });

    await page.goto('/judge.html?track=azure&team=t1');

    for (const cid of ['alignment', 'architecture', 'reliability', 'ux', 'demo']) {
      await page.locator('#btn-' + cid + '-5').click();
    }
    await page.locator('#submit-btn').click();

    const banner = page.locator('#lock-banner');
    await expect(banner).toBeVisible();
    await expect(banner).toContainText(/Scoring is locked/i);
  });
});
