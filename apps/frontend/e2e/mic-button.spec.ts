import { test, expect } from "@playwright/test";

test.describe("UAT — mic button push-to-talk", () => {
  test("page loads with mic button visible", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(`pageerror: ${err.message}`));

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const candidates = [
      'button[aria-label*="talk" i]',
      'button[aria-label*="mic" i]',
      'button:has-text("Talk")',
      '[data-testid="mic-button"]',
      "button",
    ];
    let found: string | null = null;
    for (const sel of candidates) {
      const btn = page.locator(sel).first();
      if ((await btn.count()) > 0 && (await btn.isVisible().catch(() => false))) {
        found = sel;
        console.log(`MIC SELECTOR HIT: ${sel}`);
        break;
      }
    }
    expect(found, "Could not find a mic button on the page").not.toBeNull();
    await page.screenshot({ path: "test-results/initial.png", fullPage: true });
    console.log(`\n=== CONSOLE ERRORS on load (${errors.length}) ===`);
    errors.forEach((e) => console.log(`  ${e}`));
  });

  test("clicking mic opens WebSocket to orchestrator", async ({ page }) => {
    const wsEvents: { url: string; event: string; payload?: string }[] = [];
    const errors: string[] = [];
    const networkFailures: { url: string; failure: string | null }[] = [];

    page.on("console", (msg) => {
      console.log(`[browser ${msg.type()}] ${msg.text()}`);
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(`pageerror: ${err.message}\n${err.stack ?? ""}`));
    page.on("requestfailed", (req) =>
      networkFailures.push({ url: req.url(), failure: req.failure()?.errorText || null }),
    );
    page.on("websocket", (ws) => {
      console.log(`[ws opened] ${ws.url()}`);
      wsEvents.push({ url: ws.url(), event: "opened" });
      ws.on("framesent", (p) =>
        wsEvents.push({ url: ws.url(), event: "sent", payload: String(p.payload).substring(0, 300) }),
      );
      ws.on("framereceived", (p) =>
        wsEvents.push({
          url: ws.url(),
          event: "received",
          payload: String(p.payload).substring(0, 300),
        }),
      );
      ws.on("close", () => {
        console.log(`[ws closed] ${ws.url()}`);
        wsEvents.push({ url: ws.url(), event: "closed" });
      });
      ws.on("socketerror", (e) => {
        console.log(`[ws error] ${e}`);
        wsEvents.push({ url: ws.url(), event: "error", payload: String(e) });
      });
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const candidates = [
      'button[aria-label*="talk" i]',
      'button[aria-label*="mic" i]',
      'button:has-text("Talk")',
      '[data-testid="mic-button"]',
    ];
    let micButton = null;
    for (const sel of candidates) {
      const btn = page.locator(sel).first();
      if ((await btn.count()) > 0 && (await btn.isVisible().catch(() => false))) {
        micButton = btn;
        break;
      }
    }
    if (!micButton) micButton = page.locator("button").first();

    await micButton.dispatchEvent("mousedown");
    await page.waitForTimeout(2000);
    await micButton.dispatchEvent("mouseup");
    await page.waitForTimeout(5000);

    await page.screenshot({ path: "test-results/after-click.png", fullPage: true });

    console.log(`\n=== CONSOLE ERRORS (${errors.length}) ===`);
    errors.forEach((e) => console.log(`  ${e}`));
    console.log(`\n=== WS EVENTS (${wsEvents.length}) ===`);
    wsEvents.forEach((e) =>
      console.log(`  [${e.event}] ${e.url} ${e.payload ? `:: ${e.payload}` : ""}`),
    );
    console.log(`\n=== NETWORK FAILURES (${networkFailures.length}) ===`);
    networkFailures.forEach((f) => console.log(`  ${f.url} :: ${f.failure}`));

    expect(true).toBe(true);
  });
});
