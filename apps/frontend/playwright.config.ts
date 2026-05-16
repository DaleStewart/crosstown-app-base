import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: {
    headless: true,
    baseURL: "https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io",
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
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
});
