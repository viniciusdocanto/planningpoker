import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import pkg from './package.json'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // Padrão é '/' em dev, e em prod usa VITE_APP_BASE ou '/'
  // Isso remove o 'planningpoker' forçado e deixa você decidir no .env
  const base = env.VITE_APP_BASE || '/'

  return {
    base: base,
    plugins: [
      vue(),
      tailwindcss(),
    ],
    define: {
      __APP_VERSION__: JSON.stringify(pkg.version),
    },
  }
})
