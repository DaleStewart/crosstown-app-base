// @ts-check
const { defineConfig } = require('@playwright/test');

/**
 * Playwright config for the MTA AI Hackathon judging app.
 *
 * The dev server (SWA CLI) is NOT started by Playwright — run it yourself
 * in another terminal:
 *
 *   cd apps/judging && swa start ./src --api-location ./api
 *
 * Then from apps/judging/tests/: `npm test`.
 */
module.exports = defineConfig({
  testDir: './e2e',
  timeout: 30 * 1000,
  expect: { timeout: 5 * 1000 },
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:4280',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'off',
    trace: 'off'
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' }
    }
  ]
  // webServer: {
  //   command: 'swa start ./src --api-location ./api',
  //   cwd: '..',
  //   url: 'http://localhost:4280',
  //   reuseExistingServer: true,
  //   timeout: 120 * 1000
  // }
});
