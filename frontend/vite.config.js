import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import pkg from './package.json'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  base: command === 'serve' ? '/' : './',
  plugins: [
    vue(),
    tailwindcss(),
  ],
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
}))
