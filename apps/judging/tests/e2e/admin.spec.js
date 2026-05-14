// @ts-check
const { test, expect } = require('@playwright/test');
const { stubAuth, sampleLeaderboard, jsonRoute } = require('./_fixtures');

test.describe('admin page', function () {
  test('non-admin sees auth gate, not admin body', async function ({ page }) {
    await stubAuth(page, 'judge');
    await page.goto('/admin.html');

    await expect(page.locator('#auth-gate')).toBeVisible();
    await expect(page.locator('#admin-body')).toBeHidden();
    await expect(page.locator('#lb-table')).toBeHidden();
  });

  test.describe('with admin role', function () {
    test.beforeEach(async function ({ page }) {
      await stubAuth(page, 'admin');
      await page.route('**/api/leaderboard**', jsonRoute(sampleLeaderboard()));
      await page.route('**/api/lock**', function (route) {
        if (route.request().method() === 'GET') {
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ track: 'azure', locked: false })
          });
        }
        return route.fallback();
      });
    });

    test('leaderboard renders sorted teams', async function ({ page }) {
      await page.goto('/admin.html');
      await expect(page.locator('#admin-body')).toBeVisible();

      const rows = page.locator('#lb-body tr[data-idx]');
      await expect(rows).toHaveCount(3);

      const first = rows.nth(0);
      await expect(first.locator('.rank')).toContainText('1');
      await expect(first.locator('.team')).toContainText('Team Aurora');

      await expect(rows.nth(1).locator('.team')).toContainText('Team Borealis');
      await expect(rows.nth(2).locator('.team')).toContainText('Team Cosmos');
    });

    test('lock toggle posts /api/lock with track + locked=true', async function ({ page }) {
      /** @type {any} */
      let posted = null;
      await page.route('**/api/lock', function (route) {
        const method = route.request().method();
        if (method === 'POST') {
          try { posted = JSON.parse(route.request().postData() || '{}'); } catch (_) { posted = {}; }
          return route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ track: posted.track, locked: !!posted.locked })
          });
        }
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ track: 'azure', locked: false })
        });
      });

      page.on('dialog', function (d) { d.accept(); });

      await page.goto('/admin.html');
      await expect(page.locator('#admin-body')).toBeVisible();
      await page.locator('#lb-body tr[data-idx]').first().waitFor();

      await page.locator('#lock-toggle').check();

      await expect.poll(function () { return posted; }, { timeout: 5000 }).not.toBeNull();
      expect(posted).toEqual({ track: 'azure', locked: true });
    });

    test('add team form posts /api/teams with form values', async function ({ page }) {
      /** @type {any} */
      let posted = null;
      await page.route('**/api/teams', function (route) {
        const method = route.request().method();
        if (method === 'POST') {
          try { posted = JSON.parse(route.request().postData() || '{}'); } catch (_) { posted = {}; }
          return route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({ id: 'new-team', ok: true })
          });
        }
        return route.fallback();
      });

      await page.goto('/admin.html');
      await expect(page.locator('#admin-body')).toBeVisible();

      // <details> wrapper must be open before the form is interactive.
      await page.locator('details.add-team summary').click();

      await page.locator('#add-name').fill('Team Delta');
      await page.locator('#add-room').fill('Room 9');
      await page.locator('#add-slot').fill('3:15 PM');
      await page.locator('#add-members').fill('Marie Curie\nNikola Tesla');

      await page.locator('#add-team-form button[type="submit"]').click();

      await expect.poll(function () { return posted; }, { timeout: 5000 }).not.toBeNull();
      expect(posted.name).toBe('Team Delta');
      expect(posted.track).toBe('azure');
      expect(posted.room).toBe('Room 9');
      expect(posted.slot).toBe('3:15 PM');
      expect(posted.members).toEqual(['Marie Curie', 'Nikola Tesla']);
    });
  });
});
