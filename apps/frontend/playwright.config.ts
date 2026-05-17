import { defineConfig, devices } from "@playwright/test";

const DEFAULT_URL =
  "https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    headless: true,
    baseURL: process.env.FRONTEND_URL || DEFAULT_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    launchOptions: {
      args: [
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
      ],
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
});
