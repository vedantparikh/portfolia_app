import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    base: '/portfolio-ui/',
    server: {
        host: true,
	allowedHosts: [
      'bubbly.tail13e229.ts.net'
    ],
    proxy: {
      // If the request starts with /api/v1...
      '/api/v1': {
        // ...forward it to your local Python server
        target: 'http://localhost:8000',
        changeOrigin: true, // Recommended
      }
    }
    }
})
