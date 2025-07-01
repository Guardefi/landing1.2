import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up global test environment...');
  
  // Add any cleanup logic here
  // like closing database connections, cleaning up test data, etc.
  
  console.log('✅ Global teardown completed');
}

export default globalTeardown;
