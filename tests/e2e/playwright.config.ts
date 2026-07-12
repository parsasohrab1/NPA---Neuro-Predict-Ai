import { defineConfig, devices } from '@playwright/test';

const repoRoot = process.cwd();
const backendDir = `${repoRoot}/backend`;
const frontendDir = `${repoRoot}/frontend`;

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  timeout: 60 * 1000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [['github'], ['html', { open: 'never' }]]
    : [['html']],
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: process.env.CI
    ? [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
    : [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
        { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
        { name: 'webkit', use: { ...devices['Desktop Safari'] } },
      ],
  webServer: process.env.CI
    ? undefined
    : [
        {
          command: `cd "${backendDir}" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`,
          url: 'http://127.0.0.1:8001/health',
          reuseExistingServer: true,
          timeout: 120_000,
          env: {
            SECRET_KEY: 'test-secret-key-for-e2e-tests-only-min-32-characters-long',
            ENVIRONMENT: 'test',
            DATABASE_URL: 'sqlite+aiosqlite:///./e2e_test.db',
            DATABASE_URL_SYNC: 'sqlite:///./e2e_test.db',
          },
        },
        {
          command: `cd "${frontendDir}" && npm run dev -- --host 127.0.0.1 --port 3001`,
          url: 'http://127.0.0.1:3001',
          reuseExistingServer: true,
          timeout: 120_000,
        },
      ],
});
