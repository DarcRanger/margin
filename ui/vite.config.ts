import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            {
              name: 'prosemirror',
              test: /node_modules[\\/]prosemirror-/,
              priority: 4,
            },
            {
              name: 'editor',
              test: /node_modules[\\/](?:@tiptap|tiptap-markdown)/,
              priority: 3,
            },
            {
              name: 'react',
              test: /node_modules[\\/](?:react(?:-dom|-router-dom)?|@tanstack|zustand)[\\/]/,
              priority: 2,
            },
            {
              name: 'vendor',
              test: /node_modules[\\/]/,
              priority: 1,
            },
          ],
        },
      },
    },
  },
})
