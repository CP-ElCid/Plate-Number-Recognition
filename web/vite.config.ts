import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Expose to network (use 'localhost' or '127.0.0.1' for local only)
    port: 5173,      // Set a fixed port
  },
})
