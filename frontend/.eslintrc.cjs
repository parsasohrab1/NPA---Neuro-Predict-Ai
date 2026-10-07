/* ESLint config for the NeuroPredict-AI web app (type safety is enforced by `tsc --noEmit`). */
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module', ecmaFeatures: { jsx: true } },
  plugins: ['@typescript-eslint', 'react'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
  ],
  settings: { react: { version: 'detect' } },
  rules: {
    // The codebase types API payloads loosely; tsc strict mode is the type gate.
    '@typescript-eslint/no-explicit-any': 'off',
    'react/prop-types': 'off',
    'react/no-unescaped-entities': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
  },
  ignorePatterns: ['dist', 'coverage', 'node_modules', '*.cjs'],
}
