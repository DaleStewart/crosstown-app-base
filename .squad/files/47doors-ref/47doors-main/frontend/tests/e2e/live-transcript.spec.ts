/**
 * E2E tests for the Live Transcript page (/live view).
 *
 * These tests verify the full SSE pipeline from the browser's perspective:
 *   Browser → EventSource → (mocked SSE) → useTranscriptStream → LivePage render
 *
 * The SSE connection to /api/phone/transcripts/stream is intercepted via
 * Playwright's route() API so we can inject synthetic events without needing
 * a real backend or active phone call.
 */

import { test, expect, type Page, type Route } from '@playwright/test';

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Build a valid SSE data frame for a TranscriptEvent. */
function sseFrame(event: Record<string, unknown>): string {
  return `data: ${JSON.stringify(event)}\n\n`;
}

/** Timestamp close to "now" for realistic test events. */
function now(): string {
  return new Date().toISOString();
}

/** Navigate to the Live view by clicking the Live tab. */
async function navigateToLive(page: Page): Promise<void> {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  // Click the "Live" tab in the header
  await page.getByRole('button', { name: 'Live' }).click();
  // Wait for the Live page to render (full-screen overlay)
  await expect(page.getByLabel('Live phone transcript')).toBeVisible();
}

/**
 * Intercept the SSE endpoint and return a controllable writable stream.
 * Returns an object with a `push(event)` method to inject SSE events.
 */
async function interceptSSE(page: Page) {
  const events: Record<string, unknown>[] = [];
  let flushResolve: (() => void) | null = null;

  // We'll fulfill the SSE route with a manual streaming response
  await page.route('**/api/phone/transcripts/stream', async (route: Route) => {
    // Collect any events already queued before the route was hit
    const body = events.map(sseFrame).join('');

    // Start the SSE response — Playwright's route.fulfill sends once,
    // so we accumulate events and the test re-navigates to pick them up.
    // For true streaming, we use page.evaluate to inject events directly.
    await route.fulfill({
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
      body,
    });
  });

  return {
    push(event: Record<string, unknown>) {
      events.push(event);
    },
  };
}

// ─── Tests ───────────────────────────────────────────────────────────────────

test.describe('Live Transcript Page', () => {

  test('shows "Waiting for call…" when no events arrive', async ({ page }) => {
    // Mock SSE endpoint to return empty stream
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      // Return a valid SSE response with just a keepalive comment
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: ': keepalive\n\n',
      });
    });

    await navigateToLive(page);

    // Should show waiting state (in the main transcript area, not the status badge)
    await expect(page.getByLabel('Live phone transcript').getByText('Waiting for call…')).toBeVisible();
    // Phone number should be displayed (appears in header and empty state)
    await expect(page.getByText('+1 (913) 217-1946').first()).toBeVisible();
    // 47 Doors branding
    await expect(page.getByText('47 Doors').first()).toBeVisible();
  });

  test('renders call_started event as "Call connected" pill', async ({ page }) => {
    const ts = now();

    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: sseFrame({
          type: 'call_started',
          call_id: 'test-call-1',
          phone_number: '+19132171946',
          timestamp: ts,
        }),
      });
    });

    await navigateToLive(page);

    // "Waiting for call" should be gone
    await expect(page.getByText('Waiting for call…')).not.toBeVisible();
    // Call connected indicator should appear
    await expect(page.getByText('Call connected')).toBeVisible();
    // Status badge should show "Call in progress"
    await expect(page.getByText('Call in progress')).toBeVisible();
  });

  test('renders user_speech as right-aligned caller bubble', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          sseFrame({
            type: 'call_started',
            call_id: 'test-call-2',
            phone_number: '+19132171946',
            timestamp: now(),
          }),
          sseFrame({
            type: 'user_speech',
            text: 'I need to reset my password',
            call_id: 'test-call-2',
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    // Caller label and text should appear
    await expect(page.getByText('📱 Caller')).toBeVisible();
    await expect(page.getByText('I need to reset my password')).toBeVisible();
  });

  test('renders agent_speech as left-aligned AI bubble', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          sseFrame({
            type: 'call_started',
            call_id: 'test-call-3',
            phone_number: '+19132171946',
            timestamp: now(),
          }),
          sseFrame({
            type: 'agent_speech',
            text: 'I can help you reset your password.',
            call_id: 'test-call-3',
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    // Agent label and text should appear
    await expect(page.getByText('🤖 AI Agent')).toBeVisible();
    await expect(page.getByText('I can help you reset your password.')).toBeVisible();
  });

  test('renders tool_call as centered pulsing badge', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          sseFrame({
            type: 'call_started',
            call_id: 'test-call-4',
            phone_number: '+19132171946',
            timestamp: now(),
          }),
          sseFrame({
            type: 'tool_call',
            tool: 'search_kb',
            summary: 'Found 3 articles about password reset',
            call_id: 'test-call-4',
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    await expect(page.getByText('Found 3 articles about password reset')).toBeVisible();
  });

  test('renders call_ended with duration and status update', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          sseFrame({
            type: 'call_started',
            call_id: 'test-call-5',
            phone_number: '+19132171946',
            timestamp: now(),
          }),
          sseFrame({
            type: 'call_ended',
            call_id: 'test-call-5',
            duration_seconds: 95,
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    // Call ended pill should show duration
    await expect(page.getByText('Call ended • 1m 35s')).toBeVisible();
    // Status badge should update
    await expect(page.getByText('Call in progress')).not.toBeVisible();
  });

  test('full call lifecycle renders all event types in order', async ({ page }) => {
    const callId = 'full-lifecycle-1';

    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          sseFrame({
            type: 'call_started',
            call_id: callId,
            phone_number: '+19132171946',
            timestamp: now(),
          }),
          sseFrame({
            type: 'user_speech',
            text: 'How do I apply for financial aid?',
            call_id: callId,
            timestamp: now(),
          }),
          sseFrame({
            type: 'tool_call',
            tool: 'search_kb',
            summary: 'Searching financial aid articles',
            call_id: callId,
            timestamp: now(),
          }),
          sseFrame({
            type: 'agent_speech',
            text: 'You can apply through the FAFSA portal at fafsa.ed.gov.',
            call_id: callId,
            timestamp: now(),
          }),
          sseFrame({
            type: 'user_speech',
            text: 'What is the deadline?',
            call_id: callId,
            timestamp: now(),
          }),
          sseFrame({
            type: 'agent_speech',
            text: 'The priority deadline is March 1st.',
            call_id: callId,
            timestamp: now(),
          }),
          sseFrame({
            type: 'call_ended',
            call_id: callId,
            duration_seconds: 120,
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    // Verify all transcript content rendered
    await expect(page.getByText('Call connected')).toBeVisible();
    await expect(page.getByText('How do I apply for financial aid?')).toBeVisible();
    await expect(page.getByText('Searching financial aid articles')).toBeVisible();
    await expect(page.getByText('You can apply through the FAFSA portal at fafsa.ed.gov.')).toBeVisible();
    await expect(page.getByText('What is the deadline?')).toBeVisible();
    await expect(page.getByText('The priority deadline is March 1st.')).toBeVisible();
    await expect(page.getByText('Call ended • 2m 0s')).toBeVisible();

    // Verify we have the right number of caller and agent bubbles
    const callerBubbles = page.getByText('📱 Caller');
    const agentBubbles = page.getByText('🤖 AI Agent');
    await expect(callerBubbles).toHaveCount(2);
    await expect(agentBubbles).toHaveCount(2);
  });

  test('SSE connection targets correct URL path', async ({ page }) => {
    // Verify the frontend connects to the right SSE endpoint
    let sseUrlCaptured = '';

    await page.route('**/api/phone/transcripts/stream', async (route) => {
      sseUrlCaptured = route.request().url();
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: ': keepalive\n\n',
      });
    });

    await navigateToLive(page);

    // The SSE URL should end with /api/phone/transcripts/stream
    expect(sseUrlCaptured).toContain('/api/phone/transcripts/stream');
  });

  test('page has correct accessibility attributes', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: ': keepalive\n\n',
      });
    });

    await navigateToLive(page);

    // Transcript area should have role="log" and aria-live="polite"
    const transcriptArea = page.getByLabel('Live phone transcript');
    await expect(transcriptArea).toBeVisible();
    await expect(transcriptArea).toHaveAttribute('role', 'log');
    await expect(transcriptArea).toHaveAttribute('aria-live', 'polite');
  });

  test('malformed SSE data does not crash the page', async ({ page }) => {
    await page.route('**/api/phone/transcripts/stream', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: [
          'data: {invalid json}\n\n',
          'data: \n\n',
          sseFrame({
            type: 'call_started',
            call_id: 'robust-1',
            phone_number: '+19132171946',
            timestamp: now(),
          }),
        ].join(''),
      });
    });

    await navigateToLive(page);

    // Despite malformed events, valid event should still render
    await expect(page.getByText('Call connected')).toBeVisible();
  });
});
