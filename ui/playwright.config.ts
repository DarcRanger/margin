import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'line',
  use: {
    baseURL: process.env.MARGIN_BROWSER_BASE_URL,
    trace: 'on-first-retry',
    ...devices['Desktop Chrome'],
  },
})
