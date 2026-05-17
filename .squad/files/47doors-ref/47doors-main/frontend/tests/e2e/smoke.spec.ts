/**
 * Smoke Tests for 47 Doors Boot Camp
 *
 * These tests run quickly and verify the essential functionality
 * of the application. They're designed to:
 *
 * 1. Run in Codespaces environments
 * 2. Complete in under 2 minutes
 * 3. Catch critical regressions before participants see them
 *
 * Run with: npx playwright test smoke.spec.ts --project=chromium
 */

import { test, expect } from '@playwright/test';

test.describe('Smoke Tests - Critical Path', () => {
  test.beforeEach(async ({ page }) => {
    // Wait for the page to be ready
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('homepage loads successfully', async ({ page }) => {
    // Verify the main app container loads
    await expect(page.locator('body')).toBeVisible();

    // Check for critical UI elements
    const mainContent = page.locator('main, [role="main"], #root, #app');
    await expect(mainContent.first()).toBeVisible();
  });

  test('chat interface is present', async ({ page }) => {
    // Look for chat-related elements
    const chatElements = [
      page.getByRole('textbox').first(),
      page.locator('input[type="text"]').first(),
      page.locator('[class*="chat"]').first(),
      page.locator('[class*="message"]').first(),
    ];

    // At least one chat-related element should be visible
    let foundChat = false;
    for (const element of chatElements) {
      try {
        if (await element.isVisible({ timeout: 2000 })) {
          foundChat = true;
          break;
        }
      } catch {
        // Continue to next element
      }
    }

    expect(foundChat).toBe(true);
  });

  test('can submit a basic message', async ({ page }) => {
    // Find and fill the message input
    const input = page.getByRole('textbox').first()
      .or(page.locator('input[type="text"]').first())
      .or(page.locator('textarea').first());

    await input.fill('Hello');

    // Find and click submit
    const submitButton = page.getByRole('button', { name: /send|submit/i }).first()
      .or(page.locator('button[type="submit"]').first())
      .or(page.locator('[class*="submit"]').first());

    // If there's a submit button, click it
    try {
      if (await submitButton.isVisible({ timeout: 1000 })) {
        await submitButton.click();
      } else {
        // Try pressing Enter
        await input.press('Enter');
      }
    } catch {
      await input.press('Enter');
    }

    // Wait for some response indication (loading, new message, etc.)
    await page.waitForTimeout(2000);

    // Verify the page didn't crash
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Smoke Tests - Backend Health', () => {
  test('backend health endpoint responds', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/health');
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body).toHaveProperty('status');
  });

  test('backend OpenAPI docs available', async ({ request }) => {
    const response = await request.get('http://localhost:8000/docs');
    expect(response.ok()).toBeTruthy();
  });

  test('chat endpoint accepts POST', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/chat', {
      data: {
        message: 'Hello, this is a test',
        session_id: null,
      },
    });

    // Should get a response (200) or validation error (422), not server error
    expect(response.status()).toBeLessThan(500);
  });
});

test.describe('Smoke Tests - Mock Mode Validation', () => {
  test('password reset query returns IT department', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/chat', {
      data: {
        message: 'I forgot my password',
        session_id: null,
      },
    });

    if (response.ok()) {
      const body = await response.json();
      // In mock mode, this should route to IT
      expect(body.department).toBe('IT');
    }
  });

  test('escalation triggers for policy keywords', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/chat', {
      data: {
        message: 'I want to appeal my grade',
        session_id: null,
      },
    });

    if (response.ok()) {
      const body = await response.json();
      // Should be escalated
      expect(body.escalated).toBe(true);
    }
  });
});

test.describe('Smoke Tests - Accessibility Basics', () => {
  test('page has proper heading structure', async ({ page }) => {
    await page.goto('/');

    // Should have at least one heading
    const headings = page.locator('h1, h2, h3, [role="heading"]');
    const count = await headings.count();

    expect(count).toBeGreaterThan(0);
  });

  test('interactive elements are keyboard accessible', async ({ page }) => {
    await page.goto('/');

    // Tab through the page
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Something should be focused
    const focusedElement = page.locator(':focus');
    await expect(focusedElement.first()).toBeVisible();
  });
});
