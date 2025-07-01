console.log('🔄 Starting simplified Scorpius application...');

try {
  const express = require('express');
  const cors = require('cors');
  const helmet = require('helmet');
  console.log('✅ Basic middleware imported');
  
  // Try importing our custom components one by one
  console.log('⏳ Importing Logger...');
  const Logger = require('./src/utils/helpers/logger');
  console.log('✅ Logger imported');
  
  console.log('⏳ Creating application...');
  const app = express();
  const logger = new Logger('SimpleApp');
  
  console.log('⏳ Setting up middleware...');
  app.use(helmet());
  app.use(cors());
  app.use(express.json());
  
  console.log('⏳ Setting up routes...');
  app.get('/', (req, res) => {
    res.json({
      success: true,
      message: 'Simplified Scorpius Contract Sandbox',
      timestamp: new Date().toISOString()
    });
  });
  
  app.get('/health', (req, res) => {
    res.json({
      success: true,
      status: 'healthy',
      timestamp: new Date().toISOString()
    });
  });
  
  console.log('⏳ Starting server...');
  const port = 3000;
  app.listen(port, () => {
    console.log(`🚀 Simplified Scorpius app running on port ${port}`);
    console.log(`📍 Health check: http://localhost:${port}/health`);
    logger.info('Application started successfully');
  });
  
} catch (error) {
  console.error('❌ Error in simplified application:', error);
  console.error('Stack:', error.stack);
  process.exit(1);
} 