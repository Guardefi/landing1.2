module.exports = {
  env: {
    browser: false,
    es2021: true,
    node: true,
    jest: true,
  },
  extends: [
    'airbnb-base',
    'plugin:jest/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: [
    'jest',
  ],
  rules: {
    // General rules
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'prefer-const': 'error',
    'no-var': 'error',
    
    // Import rules
    'import/prefer-default-export': 'off',
    'import/no-dynamic-require': 'off',
    'import/no-unresolved': 'off',
    
    // Function rules
    'function-paren-newline': 'off',
    'object-curly-newline': 'off',
    'max-len': ['error', { 
      code: 120, 
      ignoreUrls: true, 
      ignoreStrings: true, 
      ignoreTemplateLiterals: true 
    }],
    
    // Class rules
    'class-methods-use-this': 'off',
    'no-underscore-dangle': 'off',
    
    // Async/await rules
    'no-await-in-loop': 'off',
    'no-restricted-syntax': 'off',
    
    // Security-related rules
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
    
    // Performance rules
    'no-loop-func': 'error',
    'no-extend-native': 'error',
    
    // Jest specific rules
    'jest/no-disabled-tests': 'warn',
    'jest/no-focused-tests': 'error',
    'jest/no-identical-title': 'error',
    'jest/prefer-to-have-length': 'warn',
    'jest/valid-expect': 'error',
    
    // Blockchain/crypto specific
    'no-bitwise': 'off', // Often needed for crypto operations
    'no-mixed-operators': 'off', // Common in mathematical calculations
    
    // Allow certain patterns common in blockchain development
    'camelcase': ['error', { 
      allow: [
        'block_number',
        'gas_limit',
        'gas_price',
        'max_fee_per_gas',
        'max_priority_fee_per_gas',
        'transaction_hash'
      ] 
    }],
  },
  overrides: [
    {
      files: ['tests/**/*.js', '**/*.test.js', '**/*.spec.js'],
      env: {
        jest: true,
      },
      rules: {
        'no-unused-expressions': 'off',
        'max-len': 'off',
        'import/no-extraneous-dependencies': 'off',
      },
    },
    {
      files: ['scripts/**/*.js'],
      rules: {
        'no-console': 'off',
        'import/no-extraneous-dependencies': 'off',
      },
    },
    {
      files: ['config/**/*.js'],
      rules: {
        'global-require': 'off',
        'import/no-dynamic-require': 'off',
      },
    },
  ],
  globals: {
    // Global variables for blockchain development
    web3: 'readonly',
    ethers: 'readonly',
    artifacts: 'readonly',
    contract: 'readonly',
    assert: 'readonly',
  },
}; 