import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [
    react()
  ],
  resolve: {
    alias: {
      '@comp': path.resolve(__dirname, './src/components'),
      '@img': path.resolve(__dirname, './src/assets/images'),
      '@root': path.resolve(__dirname, './src'),
      '@constants': path.resolve(__dirname, './src/constants'),
      '@util': path.resolve(__dirname, './src/util')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }

})