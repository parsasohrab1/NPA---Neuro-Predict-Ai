import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Authentication Flow
 */
test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page.locator('h1, h2')).toContainText(/login|sign in/i);
  });

  test('should login with valid credentials', async ({ page }) => {
    // Navigate to login
    const loginButton = page.locator('text=/login|sign in/i').first();
    if (await loginButton.isVisible()) {
      await loginButton.click();
    }

    // Fill login form
    await page.fill('input[name="username"], input[type="text"]', 'admin');
    await page.fill('input[name="password"], input[type="password"]', 'admin123');
    
    // Submit form
    await page.click('button[type="submit"], button:has-text("Login")');
    
    // Wait for redirect to dashboard
    await page.waitForURL(/dashboard|home|patients/i, { timeout: 10000 });
    
    // Verify successful login
    await expect(page).toHaveURL(/dashboard|home|patients/i);
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"], input[type="text"]', 'invalid');
    await page.fill('input[name="password"], input[type="password"]', 'wrong');
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('text=/incorrect|invalid|error/i')).toBeVisible({ timeout: 5000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/i, { timeout: 10000 });

    // Logout
    await page.click('button:has-text("Logout"), a:has-text("Logout")');
    
    // Should redirect to login
    await page.waitForURL(/login|sign in/i, { timeout: 5000 });
    await expect(page).toHaveURL(/login|sign in/i);
  });
});

