import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Bind on all interfaces so the app is reachable from outside the sandbox.
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // Allow the sandbox preview hostname (https://{port}-{id}.e2b.app) plus localhost.
    allowedHosts: ['.e2b.app', 'localhost', '127.0.0.1'],
    // The browser only ever talks to this origin; Vite forwards /api to the
    // backend, so no CORS and no hardcoded localhost URLs in the browser.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['.e2b.app', 'localhost', '127.0.0.1'],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
