import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    fs: {
      // Allow serving files from the project root
      // This fixes the 403 error when the project path contains spaces
      strict: false,
      allow: [
        // Project root
        path.resolve(__dirname),
        // Parent directories (for workspace with spaces in path)
        'D:/3rd year',
        'D:/3rd year/mlops final project',
        'D:/3rd year/mlops final project/focusflow_new',
        'D:/3rd year/mlops final project/focusflow_new/focusflow',
        'D:/3rd year/mlops final project/focusflow_new/focusflow/focusflow',
      ],
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
