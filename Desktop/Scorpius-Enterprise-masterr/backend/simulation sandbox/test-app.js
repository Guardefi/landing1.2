console.log('🔄 Starting test application...');

try {
  const express = require('express');
  console.log('✅ Express imported');
  
  const app = express();
  console.log('✅ Express app created');
  
  // Test basic route
  app.get('/', (req, res) => {
    res.json({ message: 'Test server is running!' });
  });
  
  app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
  });
  
  const port = 3000;
  app.listen(port, () => {
    console.log(`🚀 Test server running on port ${port}`);
    console.log(`📍 Health check: http://localhost:${port}/health`);
  });
  
} catch (error) {
  console.error('❌ Error in test application:', error);
  console.error('Stack:', error.stack);
} 