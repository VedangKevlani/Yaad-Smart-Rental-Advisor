import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'src': path.resolve(__dirname, 'src')
    }
  },
  preview: {
    // Render serves the built site with `vite preview`; allow its domains
    allowedHosts: ['.onrender.com']
  },
  server: {
    proxy: {
      '^/api*': {
        target: 'http://localhost:5000/'
      }
    }
  }
})
