import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Prediction Flow
 */
test.describe('Predictions', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/i, { timeout: 10000 });
  });

  test('should navigate to predictions page', async ({ page }) => {
    await page.click('a:has-text("Predictions"), button:has-text("Predictions")');
    await page.waitForURL(/predictions/i);
    await expect(page).toHaveURL(/predictions/i);
  });

  test('should create a new prediction', async ({ page }) => {
    await page.goto('/predictions');
    
    // Click create prediction button
    await page.click('button:has-text("New Prediction"), button:has-text("Create")');
    
    // Select patient
    const patientSelect = page.locator('select[name="patient"], select:has-text("Patient")').first();
    if (await patientSelect.isVisible()) {
      await patientSelect.selectOption({ index: 1 }); // Select first option
    }
    
    // Fill medical data
    const mmseInput = page.locator('input[name="mmse"], input[placeholder*="mmse" i]').first();
    if (await mmseInput.isVisible()) {
      await mmseInput.fill('25');
    }
    
    // Submit prediction
    await page.click('button[type="submit"], button:has-text("Predict"), button:has-text("Generate")');
    
    // Wait for prediction results
    await expect(page.locator('text=/risk|prediction|score/i')).toBeVisible({ timeout: 15000 });
  });

  test('should display prediction results', async ({ page }) => {
    await page.goto('/predictions');
    
    // Click on a prediction if exists
    const predictionLink = page.locator('a, button').filter({ hasText: /prediction|view|details/i }).first();
    if (await predictionLink.isVisible()) {
      await predictionLink.click();
      
      // Verify results are displayed
      await expect(page.locator('text=/risk score|confidence|alzheimer|parkinson/i')).toBeVisible({ timeout: 5000 });
    }
  });
});

