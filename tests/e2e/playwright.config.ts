import { defineConfig, devices } from '@playwright/test';

/**
 * E2E Tests Configuration for NeuroPredict-AI
 * Run from tests/e2e: npx playwright test
 */
export default defineConfig({
  // Config lives in tests/e2e/ — specs are siblings, not nested under tests/e2e/tests/e2e
  testDir: '.',
  testMatch: /.*\.spec\.ts/,
  /* Maximum time one test can run for. */
  timeout: 30 * 1000,
  expect: {
    /* Maximum time expect() should wait for the condition to be met. */
    timeout: 5000
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI
    ? [['list'], ['github']]
    : [
        ['html'],
        ['json', { outputFile: 'test-results/results.json' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
      ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
    actionTimeout: 0,
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3001',
    /* API base URL */
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  /* Local only: spin up servers. CI config-validation job skips webServer via --list. */
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : [
        {
          command: 'cd ../backend && python -m uvicorn app.main:app --port 8001',
          url: 'http://localhost:8001/health',
          reuseExistingServer: !process.env.CI,
          timeout: 120 * 1000,
          env: {
            SECRET_KEY: 'test-secret-key-for-e2e-tests-only-min-32-characters-long',
            ENVIRONMENT: 'test',
            DATABASE_URL: 'sqlite+aiosqlite:///:memory:',
          },
        },
        {
          command: 'cd ../frontend && npm run dev',
          url: 'http://localhost:3001',
          reuseExistingServer: !process.env.CI,
          timeout: 120 * 1000,
        },
      ],
});
