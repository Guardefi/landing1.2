const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const bodyParser = require('body-parser');
const { VM } = require('vm2');
const winston = require('winston');
const rateLimit = require('express-rate-limit');

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'simulation-sandbox.log' })
  ]
});

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ['http://localhost:8000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use(limiter);

// Body parser middleware
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'simulation-sandbox'
  });
});

// Code execution endpoint
app.post('/execute', async (req, res) => {
  try {
    const { code, context = {}, timeout = 5000 } = req.body;

    if (!code) {
      return res.status(400).json({
        success: false,
        error: 'Code is required'
      });
    }

    // Create VM with restricted environment
    const vm = new VM({
      timeout: timeout,
      sandbox: {
        ...context,
        console: {
          log: (...args) => logger.info('VM Console:', ...args),
          error: (...args) => logger.error('VM Console:', ...args),
          warn: (...args) => logger.warn('VM Console:', ...args)
        },
        Math,
        Date,
        JSON,
        parseInt,
        parseFloat,
        isNaN,
        isFinite,
        // Blockchain simulation utilities
        SimulationUtils: {
          generateRandomHash: () => {
            return Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
          },
          calculateGasUsed: (operations) => {
            return operations * 21000; // Simple gas calculation
          },
          validateTransaction: (tx) => {
            return tx && tx.from && tx.to && tx.value >= 0;
          }
        }
      },
      eval: false,
      wasm: false
    });

    // Execute code in VM
    const result = vm.run(code);
    
    logger.info('Code executed successfully', {
      codeLength: code.length,
      resultType: typeof result
    });

    res.json({
      success: true,
      result: result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Code execution error:', error);
    
    res.status(400).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Simulation scenario execution endpoint
app.post('/simulate', async (req, res) => {
  try {
    const { 
      scenario, 
      parameters = {}, 
      iterations = 1,
      timeout = 10000 
    } = req.body;

    if (!scenario) {
      return res.status(400).json({
        success: false,
        error: 'Scenario is required'
      });
    }

    const results = [];
    
    for (let i = 0; i < Math.min(iterations, 100); i++) {
      const vm = new VM({
        timeout: timeout,
        sandbox: {
          ...parameters,
          iteration: i,
          console: {
            log: (...args) => logger.info(`Simulation ${i}:`, ...args)
          },
          Math,
          Date,
          JSON,
          // Simulation helpers
          Simulation: {
            random: () => Math.random(),
            randomInt: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,
            generateAddress: () => '0x' + Array.from({length: 40}, () => Math.floor(Math.random() * 16).toString(16)).join(''),
            calculateReward: (stake, duration) => stake * 0.05 * (duration / 365), // 5% annual
            gasPrice: () => Math.floor(Math.random() * 100) + 20 // 20-120 gwei
          }
        }
      });

      const result = vm.run(scenario);
      results.push({
        iteration: i,
        result: result,
        timestamp: new Date().toISOString()
      });
    }

    logger.info('Simulation completed', {
      iterations: results.length,
      scenarioLength: scenario.length
    });

    res.json({
      success: true,
      results: results,
      summary: {
        iterations: results.length,
        completedAt: new Date().toISOString()
      }
    });

  } catch (error) {
    logger.error('Simulation error:', error);
    
    res.status(400).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  logger.info(`Simulation sandbox server started on port ${PORT}`);
  logger.info('Environment:', {
    nodeVersion: process.version,
    platform: process.platform,
    memory: process.memoryUsage()
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');  
  process.exit(0);
});

module.exports = app;
