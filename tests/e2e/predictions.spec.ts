import { test, expect } from '@playwright/test';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel('Username').fill('admin');
  await page.getByLabel('Password').fill('admin123');
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL(/\/(?!login)/, { timeout: 15_000 });
}

test.describe('Predictions', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should open new prediction flow', async ({ page }) => {
    await page.goto('/predictions/new');
    await expect(page.getByText(/prediction|patient|disease/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test('should reach dashboard after login', async ({ page }) => {
    await expect(page.getByText(/dashboard|patients|neuropredict/i).first()).toBeVisible({
      timeout: 10_000,
    });
  });
});
