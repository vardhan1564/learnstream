import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
          editor: [
            '@uiw/react-codemirror',
            '@codemirror/lang-java',
            '@codemirror/lang-python',
            '@codemirror/lang-cpp',
            '@codemirror/lang-javascript',
          ],
        },
      },
    },
  },
})
