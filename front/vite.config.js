import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import autoprefixer from 'autoprefixer'

export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    allowedHosts: [
      'dongne-gosgos.store',
      'www.dongne-gosgos.store',
      'localhost',
      'front'
    ],
    // 로컬 개발용 프록시
    proxy: {
      '/sgis-api': {
        target: 'https://sgisapi.kostat.go.kr',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sgis-api/, ''),
        secure: false,
      },
    },
    // host: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    postcss: {
      plugins: [
        autoprefixer,
      ],
    },
  },
})