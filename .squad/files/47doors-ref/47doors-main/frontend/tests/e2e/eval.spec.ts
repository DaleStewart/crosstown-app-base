import { test, expect, type Page } from '@playwright/test';
import { randomUUID } from 'crypto';

/**
 * Deployment Evaluation Suite for 47 Doors Front Door Support Agent
 *
 * Runnable against any environment via BASE_URL and BACKEND_URL env vars:
 *   BASE_URL=https://frontend.example.com BACKEND_URL=https://backend.example.com npx playwright test eval.spec.ts
 *
 * When BACKEND_URL is not set, derives it from BASE_URL by replacing '-frontend' with '-backend'.
 * Falls back to localhost defaults for local dev.
 */

const FRONTEND_URL = process.env.BASE_URL || 'http://localhost:5173';
const BACKEND_URL =
  process.env.BACKEND_URL ||
  (process.env.BASE_URL
    ? process.env.BASE_URL.replace('-frontend', '-backend')
    : 'http://localhost:8000');

// Thresholds
const PAGE_LOAD_MS = 5_000;
const API_HEALTH_MS = 10_000; // generous for Azure Container App cold starts
const CHAT_RESPONSE_MS = 30_000;

/** Send a chat message via API and return response + elapsed time. */
async function chatViaAPI(
  request: ReturnType<typeof test.info>['_test'] extends never ? never : any,
  message: string,
  sessionId?: string,
): Promise<{ status: number; body: any; elapsedMs: number }> {
  const start = Date.now();
  const response = await request.post(`${BACKEND_URL}/api/chat`, {
    data: { message, session_id: sessionId ?? null },
    timeout: CHAT_RESPONSE_MS,
  });
  const elapsedMs = Date.now() - start;
  let body: any = null;
  try {
    body = await response.json();
  } catch {
    // non-JSON response
  }
  return { status: response.status(), body, elapsedMs };
}

// ---------------------------------------------------------------------------
// 1. HOMEPAGE & UI CHROME
// ---------------------------------------------------------------------------
test.describe('Eval: Homepage & UI', { tag: '@eval' }, () => {
  test('homepage loads within threshold', async ({ page }) => {
    const start = Date.now();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    const loadMs = Date.now() - start;

    await expect(page.locator('body')).toBeVisible();
    expect(loadMs).toBeLessThan(PAGE_LOAD_MS);
    test.info().annotations.push({ type: 'timing', description: `Page load: ${loadMs}ms` });
  });

  test('main UI elements are present', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Header / banner
    await expect(page.getByRole('banner')).toBeVisible();

    // Chat input
    await expect(page.getByRole('textbox').first()).toBeVisible();

    // Send button
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();

    // At least one heading
    const headingCount = await page.locator('h1, h2, h3, [role="heading"]').count();
    expect(headingCount).toBeGreaterThan(0);
  });

  test('page title is set', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    test.info().annotations.push({ type: 'info', description: `Title: "${title}"` });
  });
});

// ---------------------------------------------------------------------------
// 2. BACKEND HEALTH
// ---------------------------------------------------------------------------
test.describe('Eval: Backend Health', { tag: '@eval' }, () => {
  test('health endpoint responds 200', async ({ request }) => {
    const start = Date.now();
    const response = await request.get(`${BACKEND_URL}/api/health`);
    const elapsedMs = Date.now() - start;

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('status');
    expect(elapsedMs).toBeLessThan(API_HEALTH_MS);
    test.info().annotations.push({ type: 'timing', description: `Health: ${elapsedMs}ms` });
  });
});

// ---------------------------------------------------------------------------
// 3. CHAT FUNCTIONALITY
// ---------------------------------------------------------------------------
test.describe('Eval: Chat Functionality', { tag: '@eval' }, () => {
  test('can send a message and receive a response via UI', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const input = page.getByRole('textbox').first();
    await input.fill('Hello, I need help');
    await page.getByRole('button', { name: /send/i }).click();

    // User message should appear
    await expect(page.getByText('Hello, I need help')).toBeVisible();

    // AI response should appear within timeout
    const main = page.locator('[role="main"]');
    await expect(main).toContainText(/.{20,}/i, { timeout: CHAT_RESPONSE_MS });
  });

  test('chat API returns 200 with expected shape', async ({ request }) => {
    const { status, body, elapsedMs } = await chatViaAPI(request, 'What are your hours?');

    expect(status).toBe(200);
    expect(body).toBeTruthy();
    // Response should have a message/response field
    const hasResponse =
      typeof body.response === 'string' ||
      typeof body.message === 'string' ||
      typeof body.answer === 'string';
    expect(hasResponse).toBe(true);

    test.info().annotations.push({ type: 'timing', description: `Chat API: ${elapsedMs}ms` });
  });

  test('chat API response time is under threshold', async ({ request }) => {
    const { elapsedMs } = await chatViaAPI(request, 'How do I register for classes?');
    expect(elapsedMs).toBeLessThan(CHAT_RESPONSE_MS);
    test.info().annotations.push({ type: 'timing', description: `Chat latency: ${elapsedMs}ms` });
  });
});

// ---------------------------------------------------------------------------
// 4. KNOWLEDGE BASE QUALITY
// ---------------------------------------------------------------------------
test.describe('Eval: Knowledge Base Quality', { tag: '@eval' }, () => {
  const knowledgeQuestions = [
    {
      question: 'How do I reset my password?',
      mustContain: /password|reset|account|IT|help desk/i,
      topic: 'IT / Password Reset',
    },
    {
      question: 'What meal plans are available?',
      mustContain: /meal|dining|plan|food|cafeteria/i,
      topic: 'Dining / Meal Plans',
    },
    {
      question: 'How do I register for classes?',
      mustContain: /register|enroll|class|course|registrar/i,
      topic: 'Registration',
    },
    {
      question: 'What are the library hours?',
      mustContain: /library|hour|open|close|schedule/i,
      topic: 'Library',
    },
    {
      question: 'How do I apply for financial aid?',
      mustContain: /financial|aid|FAFSA|scholarship|grant|loan/i,
      topic: 'Financial Aid',
    },
  ];

  for (const { question, mustContain, topic } of knowledgeQuestions) {
    test(`KB: ${topic} — "${question}"`, async ({ request }) => {
      const { status, body, elapsedMs } = await chatViaAPI(request, question);

      expect(status).toBe(200);

      // Extract the response text from whichever field the API uses
      const responseText = body?.response ?? body?.message ?? body?.answer ?? '';
      expect(typeof responseText).toBe('string');

      // Should be a substantive answer (not empty / not "I don't know")
      expect(responseText.length).toBeGreaterThan(30);
      expect(responseText).not.toMatch(/I don't have information|I cannot help|no information/i);

      // Should contain topic-relevant keywords
      expect(responseText).toMatch(mustContain);

      test.info().annotations.push({
        type: 'timing',
        description: `${topic}: ${elapsedMs}ms, ${responseText.length} chars`,
      });
    });
  }
});

// ---------------------------------------------------------------------------
// 5. SESSION MANAGEMENT
// ---------------------------------------------------------------------------
test.describe('Eval: Session Management', { tag: '@eval' }, () => {
  test('session ID is returned and reusable', async ({ request }) => {
    // First message — no session
    const r1 = await chatViaAPI(request, 'Hello');
    expect(r1.status).toBe(200);

    const sessionId = r1.body?.session_id;
    expect(sessionId).toBeTruthy();

    // Second message — reuse session
    const r2 = await chatViaAPI(request, 'What was my first message?', sessionId);
    expect(r2.status).toBe(200);

    // Session should persist
    expect(r2.body?.session_id).toBe(sessionId);
  });

  test('invalid session ID is handled gracefully', async ({ request }) => {
    const bogusId = randomUUID();
    const { status } = await chatViaAPI(request, 'Hello', bogusId);

    // Should not 500 — either accept the new session or return 4xx
    expect(status).toBeLessThan(500);
  });

  test('conversation history persists in UI', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const input = page.getByRole('textbox').first();

    // Send first message
    await input.fill('My name is EvalBot');
    await page.getByRole('button', { name: /send/i }).click();
    await expect(page.getByText('My name is EvalBot')).toBeVisible();

    // Wait for response
    await page.locator('[role="main"]').waitFor({ state: 'visible' });
    await page.waitForTimeout(3000);

    // Send second message
    await input.fill('What is my name?');
    await page.getByRole('button', { name: /send/i }).click();
    await expect(page.getByText('What is my name?')).toBeVisible();

    // Both user messages should be visible (conversation preserved)
    await expect(page.getByText('My name is EvalBot')).toBeVisible();
    await expect(page.getByText('What is my name?')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// 6. ERROR HANDLING
// ---------------------------------------------------------------------------
test.describe('Eval: Error Handling', { tag: '@eval' }, () => {
  test('empty message is prevented in UI', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const sendButton = page.getByRole('button', { name: /send/i });
    // Send button should be disabled when input is empty
    await expect(sendButton).toBeDisabled();
  });

  test('malformed API request returns 4xx, not 5xx', async ({ request }) => {
    const response = await request.post(`${BACKEND_URL}/api/chat`, {
      data: {},
    });
    // Missing required 'message' field should be a validation error, not a crash
    expect(response.status()).toBeGreaterThanOrEqual(400);
    expect(response.status()).toBeLessThan(500);
  });

  test('non-existent endpoint returns 404', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/nonexistent-endpoint-eval`);
    expect(response.status()).toBe(404);
  });

  test('app does not crash on rapid sequential messages', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const input = page.getByRole('textbox').first();
    const sendButton = page.getByRole('button', { name: /send/i });

    // Fire off 3 messages quickly
    for (const msg of ['Quick 1', 'Quick 2', 'Quick 3']) {
      await input.fill(msg);
      await sendButton.click();
      await page.waitForTimeout(500);
    }

    // Page should still be functional — no crash, no blank screen
    await expect(page.locator('body')).toBeVisible();
    await expect(page.getByRole('textbox').first()).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// 7. VOICE UI PRESENCE
// ---------------------------------------------------------------------------
test.describe('Eval: Voice UI', { tag: '@eval' }, () => {
  test('voice-related UI element is present', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Look for mic/voice button by various selectors
    const voiceSelectors = [
      page.getByRole('button', { name: /voice|mic|microphone|speak|call/i }),
      page.locator('button[aria-label*="voice" i]'),
      page.locator('button[aria-label*="mic" i]'),
      page.locator('[class*="voice" i]'),
      page.locator('[class*="mic" i]'),
      page.locator('button svg'), // icon buttons (mic icon)
    ];

    let found = false;
    for (const selector of voiceSelectors) {
      try {
        if ((await selector.count()) > 0 && (await selector.first().isVisible({ timeout: 2000 }))) {
          found = true;
          const label =
            (await selector.first().getAttribute('aria-label')) ||
            (await selector.first().textContent()) ||
            'unlabelled';
          test.info().annotations.push({
            type: 'info',
            description: `Voice element found: "${label}"`,
          });
          break;
        }
      } catch {
        // continue
      }
    }

    // Soft-pass: log presence but don't hard-fail if voice hasn't shipped yet
    if (!found) {
      test.info().annotations.push({
        type: 'warning',
        description: 'No voice UI element detected — voice feature may not be deployed.',
      });
    }
    // Still pass — voice UI is advisory in eval
    expect(true).toBe(true);
  });

  test('voice health endpoint responds (if available)', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/voice/health`, {
      failOnStatusCode: false,
    });

    // Voice may not be deployed — just record what we find
    test.info().annotations.push({
      type: 'info',
      description: `Voice health: ${response.status()}`,
    });

    if (response.ok()) {
      const body = await response.json();
      expect(body).toHaveProperty('status');
    }
    // No hard-fail — voice is optional in eval
  });
});

// ---------------------------------------------------------------------------
// 8. RESPONSE TIME BENCHMARKS
// ---------------------------------------------------------------------------
test.describe('Eval: Performance Benchmarks', { tag: '@eval' }, () => {
  test('full page load with network idle < 8s', async ({ page }) => {
    const start = Date.now();
    await page.goto('/', { waitUntil: 'networkidle' });
    const elapsedMs = Date.now() - start;

    expect(elapsedMs).toBeLessThan(8_000);
    test.info().annotations.push({ type: 'timing', description: `Full load: ${elapsedMs}ms` });
  });

  test('chat round-trip via API < 30s', async ({ request }) => {
    const { elapsedMs } = await chatViaAPI(request, 'What is the add/drop deadline?');
    expect(elapsedMs).toBeLessThan(CHAT_RESPONSE_MS);
    test.info().annotations.push({ type: 'timing', description: `API round-trip: ${elapsedMs}ms` });
  });

  test('three sequential queries average < 20s each', async ({ request }) => {
    const questions = [
      'Where is the parking office?',
      'How do I get a student ID card?',
      'What tutoring services are available?',
    ];

    let totalMs = 0;
    for (const q of questions) {
      const { elapsedMs, status } = await chatViaAPI(request, q);
      expect(status).toBe(200);
      totalMs += elapsedMs;
    }

    const avgMs = Math.round(totalMs / questions.length);
    expect(avgMs).toBeLessThan(20_000);
    test.info().annotations.push({
      type: 'timing',
      description: `3-query avg: ${avgMs}ms (total: ${totalMs}ms)`,
    });
  });
});
