import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🔧 Setting up global test environment...');
  
  // Ensure artifacts directory exists
  const fs = require('fs');
  const path = require('path');
  
  const artifactsDir = path.join(__dirname, '..', '..', 'artifacts', 'tests');
  if (!fs.existsSync(artifactsDir)) {
    fs.mkdirSync(artifactsDir, { recursive: true });
    console.log('📁 Created artifacts/tests directory');
  }
  
  // You can add any other global setup here
  // like starting database connections, setting up test data, etc.
  
  console.log('✅ Global setup completed');
}

export default globalSetup;
