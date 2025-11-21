import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Patient Management
 */
test.describe('Patient Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/i, { timeout: 10000 });
  });

  test('should navigate to patients page', async ({ page }) => {
    await page.click('a:has-text("Patients"), button:has-text("Patients")');
    await page.waitForURL(/patients/i);
    await expect(page).toHaveURL(/patients/i);
  });

  test('should create a new patient', async ({ page }) => {
    await page.goto('/patients');
    
    // Click add patient button
    await page.click('button:has-text("Add"), button:has-text("New"), button:has-text("Create")');
    
    // Fill patient form
    await page.fill('input[name="first_name"], input[placeholder*="first" i]', 'John');
    await page.fill('input[name="last_name"], input[placeholder*="last" i]', 'Doe');
    await page.fill('input[type="date"], input[name*="birth" i]', '1980-01-15');
    
    // Select gender if dropdown exists
    const genderSelect = page.locator('select[name="gender"], select:has-text("Gender")').first();
    if (await genderSelect.isVisible()) {
      await genderSelect.selectOption('male');
    }
    
    // Submit form
    await page.click('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    
    // Verify patient was created
    await expect(page.locator('text=/john.*doe|doe.*john/i')).toBeVisible({ timeout: 10000 });
  });

  test('should search for patients', async ({ page }) => {
    await page.goto('/patients');
    
    // Search for patient
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await searchInput.press('Enter');
      
      // Wait for search results
      await page.waitForTimeout(1000);
    }
  });

  test('should view patient details', async ({ page }) => {
    await page.goto('/patients');
    
    // Click on first patient in list
    const patientLink = page.locator('a, button').filter({ hasText: /patient|pt-/i }).first();
    if (await patientLink.isVisible()) {
      await patientLink.click();
      await page.waitForURL(/patients\/\d+/i, { timeout: 5000 });
      
      // Verify patient details are displayed
      await expect(page.locator('text=/patient|details|information/i')).toBeVisible();
    }
  });
});

