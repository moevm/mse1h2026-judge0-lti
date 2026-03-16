import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    // Стандартный плагин React (теперь на базе быстрого Oxc)
    react(),

    // Подключение Babel через Rolldown-плагин для компилятора
    babel({
      presets: [
        reactCompilerPreset({
          // Опции для компилятора (например, для React 18)
          target: '18'
        })
      ],
    } as never),
    // Подключаем Tailwind v4
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Настраиваем быстрый доступ к папке src через @
      "@": path.resolve(__dirname, "./src"),
    },
  }
})