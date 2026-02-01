import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            if (id.includes('recharts')) {
              return 'recharts';
            }
            if (id.includes('@tanstack/react-query') || id.includes('zustand')) {
              return 'state';
            }
            return 'vendor';
          }
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Proxy /api and /health to backend to avoid CORS. Backend default port is 8001; use 8000 if you run backend there.
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        ws: true,
      },
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})

