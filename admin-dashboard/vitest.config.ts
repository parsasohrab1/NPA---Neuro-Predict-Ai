import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

/**
 * Standalone Vitest config (does not extend vite.config.ts) so test runs
 * stay fast and free from dev-server side effects (proxy, websocket, etc.)
 * and don't require PostCSS plugins (tailwind/autoprefixer) at test time.
 */
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: false,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        'src/test/**',
        '**/*.config.{ts,js}',
        '**/*.d.ts',
      ],
    },
  },
})
