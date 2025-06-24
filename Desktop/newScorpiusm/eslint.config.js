import antfu from '@antfu/eslint-config';

export default antfu({
  typescript: true,
  react: true,
  formatters: {
    css: true,
    html: true,
    markdown: 'prettier',
  },
  rules: {
    'no-console': 'warn',
    'no-debugger': 'error',
    '@typescript-eslint/no-unused-vars': 'error',
    'react/prop-types': 'off',
    'react/react-in-jsx-scope': 'off',
    'prefer-const': 'error',
    'no-var': 'error',
  },
  ignores: ['dist', 'node_modules', '*.d.ts', 'public', 'build'],
});
