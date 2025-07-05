// Time Machine - ESLint Configuration
module.exports = {
  root: true,
  env: {
    browser: true,
    es6: true,
    node: true,
  },
  extends: [
    'react-app',
    'react-app/jest',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // General
    'no-console': 'warn',
    'no-debugger': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
    
    // Code style
    'semi': ['error', 'always'],
    'quotes': ['warn', 'single'],
    'comma-dangle': ['warn', 'always-multiline'],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
