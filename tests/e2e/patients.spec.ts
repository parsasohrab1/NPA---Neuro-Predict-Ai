import { test, expect } from '@playwright/test';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel('Username').fill('admin');
  await page.getByLabel('Password').fill('admin123');
  await page.getByRole('button', { name: /sign in/i }).click();
  await page.waitForURL(/\/(?!login)/, { timeout: 15_000 });
}

test.describe('Patient Management', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('should navigate to patients page', async ({ page }) => {
    await page.getByRole('link', { name: /patients/i }).click();
    await expect(page).toHaveURL(/patients/);
  });

  test('should render patients list or empty state', async ({ page }) => {
    await page.goto('/patients');
    await expect(
      page.getByRole('heading', { name: /patients/i }).or(page.getByText(/no patients|patient list/i))
    ).toBeVisible({ timeout: 10_000 });
  });
});
