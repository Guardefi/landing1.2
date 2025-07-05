import js from "@eslint/js";
import typescript from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import jsxA11y from "eslint-plugin-jsx-a11y";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        ecmaVersion: "latest",
        sourceType: "module",
      },
      globals: {
        window: "readonly",
        document: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        setInterval: "readonly",
        clearTimeout: "readonly",
        clearInterval: "readonly",
        fetch: "readonly",
        navigator: "readonly",
        location: "readonly",
        history: "readonly",
        process: "readonly",
        File: "readonly",
        FormData: "readonly",
        NodeJS: "readonly",
        require: "readonly",
        HTMLTextAreaElement: "readonly",
        HTMLInputElement: "readonly",
        HTMLButtonElement: "readonly",
        HTMLSelectElement: "readonly",
        HTMLTableRowElement: "readonly",
        HTMLTableCellElement: "readonly",
        HTMLTableCaptionElement: "readonly",
        HTMLTableElement: "readonly",
        HTMLTableSectionElement: "readonly",
        HTMLDivElement: "readonly",
        HTMLUListElement: "readonly",
        HTMLLIElement: "readonly",
        HTMLCanvasElement: "readonly",
        HTMLAnchorElement: "readonly",
        KeyboardEvent: "readonly",
        requestAnimationFrame: "readonly",
        cancelAnimationFrame: "readonly",
        URLSearchParams: "readonly",
        HTMLIFrameElement: "readonly",
        React: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": typescript,
      react,
      "react-hooks": reactHooks,
      "jsx-a11y": jsxA11y,
    },
    rules: {
      ...typescript.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "no-console": "warn",
      "prefer-const": "error",
      "no-var": "error",
      "no-self-assign": "warn",
      "jsx-a11y/iframe-has-title": "warn",
      "react/no-unknown-property": "warn",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
  {
    ignores: [
      "dist/**",
      "build/**",
      "node_modules/**",
      "*.config.js",
      "*.config.ts",
    ],
  },
];
