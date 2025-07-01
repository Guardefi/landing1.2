console.log('🔄 Starting enhanced Scorpius application...');

try {
  const express = require('express');
  const cors = require('cors');
  const helmet = require('helmet');
  const compression = require('compression');
  
  console.log('✅ Basic dependencies imported');
  
  // Import our custom components
  const Logger = require('./src/utils/helpers/logger');
  console.log('✅ Logger imported');
  
  // Create application
  const app = express();
  const logger = new Logger('EnhancedApp');
  
  // Setup middleware
  app.use(helmet());
  app.use(cors());
  app.use(compression());
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true }));
  
  console.log('✅ Middleware configured');
  
  // Basic routes
  app.get('/', (req, res) => {
    res.json({
      success: true,
      message: 'Enhanced Scorpius Contract Sandbox API',
      version: '1.0.0',
      endpoints: {
        health: '/health',
        simulations: '/api/v1/simulations'
      },
      timestamp: new Date().toISOString()
    });
  });
  
  app.get('/health', (req, res) => {
    res.json({
      success: true,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });
  });
  
  // Simple simulation endpoints (without authentication for testing)
  app.post('/api/v1/simulations/test', (req, res) => {
    res.json({
      success: true,
      message: 'Test simulation endpoint working',
      data: {
        simulationId: 'test-123',
        status: 'completed',
        timestamp: new Date().toISOString()
      }
    });
  });
  
  app.get('/api/v1/simulations/health', (req, res) => {
    res.json({
      success: true,
      status: 'simulation services healthy',
      timestamp: new Date().toISOString()
    });
  });
  
  console.log('✅ Routes configured');
  
  // Error handling
  app.use((error, req, res, next) => {
    logger.error('Unhandled error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal Server Error',
      message: error.message
    });
  });
  
  // Start server
  const port = 3000;
  app.listen(port, () => {
    console.log(`🚀 Enhanced Scorpius app running on port ${port}`);
    console.log(`📍 Health check: http://localhost:${port}/health`);
    console.log(`📍 API info: http://localhost:${port}/`);
    console.log(`📍 Test simulation: POST http://localhost:${port}/api/v1/simulations/test`);
    logger.info('Enhanced application started successfully');
  });
  
} catch (error) {
  console.error('❌ Error in enhanced application:', error);
  console.error('Stack:', error.stack);
  process.exit(1);
} 