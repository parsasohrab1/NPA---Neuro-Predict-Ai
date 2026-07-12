import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const apiProxyTarget = process.env.VITE_PROXY_TARGET ?? 'http://127.0.0.1:8001'

export default defineConfig({
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
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // Local npm dev: 3001 (admin uses 3000). Docker maps host 3000 -> container 3000.
    port: Number(process.env.VITE_DEV_PORT) || 3001,
    host: true,
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
      },
      '/health': {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
  plugins: [
    react(),
    {
      name: 'favicon-fallback',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url === '/favicon.ico') {
            res.writeHead(302, { Location: '/brain-icon.svg' });
            res.end();
            return;
          }
          next();
        });
      },
    },
  ],
})

