import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      // Margin intentionally uses effects to synchronize local UI state with
      // settings, workspace changes, and remote data. The React 19 plugin's
      // blanket rule rejects those existing synchronization effects even when
      // they are guarded or initiate async work.
      'react-hooks/set-state-in-effect': 'off',
    },
  },
])
