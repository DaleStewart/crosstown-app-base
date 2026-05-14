// @ts-check
const { test, expect } = require('@playwright/test');
const { stubAuth } = require('./_fixtures');

test.describe('landing page', function () {
  test('renders headline and both track cards', async function ({ page }) {
    await stubAuth(page, 'judge');
    await page.goto('/');

    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    // index.html ships "Coach Scoring\nConsole" as the headline.
    await expect(h1).toContainText(/Coach Scoring/i);

    await expect(page.locator('a.track-card.azure')).toBeVisible();
    await expect(page.locator('a.track-card.copilot')).toBeVisible();
  });

  test('admin link hidden for non-admin', async function ({ page }) {
    await stubAuth(page, 'judge');
    await page.goto('/');
    await page.waitForFunction(function () {
      return !!document.getElementById('admin-card');
    });
    const adminCard = page.locator('#admin-card');
    await expect(adminCard).toBeHidden();
  });

  test('admin link visible for admin', async function ({ page }) {
    await stubAuth(page, 'admin');
    await page.goto('/');
    const adminCard = page.locator('#admin-card');
    await expect(adminCard).toBeVisible();
  });
});
