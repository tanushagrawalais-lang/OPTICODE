import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/health': 'http://localhost:8000',
      '/conversations': 'http://localhost:8000',
      '/code': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
    },
  },
});
