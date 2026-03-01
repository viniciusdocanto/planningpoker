import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import pkg from './package.json'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    base: env.VITE_APP_BASE || '/',
    plugins: [
      vue(),
      tailwindcss(),
    ],
    define: {
      __APP_VERSION__: JSON.stringify(pkg.version),
    },
  }
})
