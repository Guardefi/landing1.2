const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const cookieParser = require('cookie-parser');
const { body, validationResult } = require('express-validator');

// Import utilities and middleware
const Logger = require('./utils/helpers/logger');
const { rateLimiters } = require('./api/middleware/rate-limit');

// Import routes
const v1Routes = require('./api/routes/v1');

// Import core managers
const { NetworkManager } = require('./core/managers/network-manager');
const { SandboxEngine } = require('./core/engines/sandbox-engine');
const { SimulationEngine } = require('./exploits/simulation/simulation-engine');  
const { VulnerabilityAnalyzer } = require('./security/audit/vulnerability-analyzer');
const { ContractManager } = require('./core/managers/contract-manager');
const SimulationController = require('./api/controllers/simulation.controller');

class ScorpiusApplication {
  constructor() {
    this.app = express();
    this.logger = new Logger('ScorpiusApplication');
    this.server = null;
    
    // Core components
    this.networkManager = null;
    this.sandboxEngine = null;
    this.simulationEngine = null;
    this.vulnerabilityAnalyzer = null;
    this.contractManager = null;
    this.simulationController = null;
    
    this.isInitialized = false;
  }

  async initialize() {
    try {
      this.logger.info('Initializing Scorpius Contract Sandbox...');
      
      // Load configuration
      await this.loadConfiguration();
      
      // Setup middleware
      this.setupMiddleware();
      
      // Initialize core components
      await this.initializeComponents();
      
      // Setup routes
      this.setupRoutes();
      
      // Setup error handling
      this.setupErrorHandling();
      
      this.isInitialized = true;
      this.logger.info('Scorpius Contract Sandbox initialized successfully');
      
    } catch (error) {
      this.logger.error('Failed to initialize application:', error);
      throw error;
    }
  }

  async loadConfiguration() {
    // Load environment variables with defaults
    this.config = {
      port: process.env.PORT || 3000,
      nodeEnv: process.env.NODE_ENV || 'development',
      
      // Database configuration
      database: {
        url: process.env.DATABASE_URL || 'postgresql://localhost:5432/scorpius_sandbox',
        ssl: process.env.DATABASE_SSL === 'true',
        maxConnections: parseInt(process.env.DATABASE_MAX_CONNECTIONS) || 20
      },
      
      // Redis configuration
      redis: {
        url: process.env.REDIS_URL || 'redis://localhost:6379',
        keyPrefix: process.env.REDIS_KEY_PREFIX || 'scorpius:'
      },
      
      // Security configuration
      security: {
        jwtSecret: process.env.JWT_SECRET || 'scorpius-sandbox-secret-key',
        jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
        bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 12,
        corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000']
      },
      
      // Blockchain configuration
      blockchain: {
        defaultNetwork: process.env.DEFAULT_NETWORK || 'localhost',
        anvilRpcUrl: process.env.ANVIL_RPC_URL || 'http://localhost:8545',
        privateKey: process.env.PRIVATE_KEY || '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
        gasLimit: parseInt(process.env.GAS_LIMIT) || 8000000
      },
      
      // Simulation configuration
      simulation: {
        maxConcurrentSimulations: parseInt(process.env.MAX_CONCURRENT_SIMULATIONS) || 5,
        defaultTimeout: parseInt(process.env.SIMULATION_TIMEOUT) || 300000,
        enableAiAnalysis: process.env.ENABLE_AI_ANALYSIS !== 'false',
        enableDynamicAnalysis: process.env.ENABLE_DYNAMIC_ANALYSIS !== 'false'
      },
      
      // Analysis configuration
      analysis: {
        enableAiAnalysis: process.env.ENABLE_AI_ANALYSIS !== 'false',
        maxConcurrentAnalyses: parseInt(process.env.MAX_CONCURRENT_ANALYSES) || 3,
        analysisTimeout: parseInt(process.env.ANALYSIS_TIMEOUT) || 300000
      },
      
      // Contract configuration
      contracts: {
        solidityVersion: process.env.SOLIDITY_VERSION || '0.8.21',
        optimizerEnabled: process.env.OPTIMIZER_ENABLED !== 'false',
        optimizerRuns: parseInt(process.env.OPTIMIZER_RUNS) || 200,
        maxContractSize: parseInt(process.env.MAX_CONTRACT_SIZE) || 24576
      }
    };
    
    this.logger.info('Configuration loaded successfully');
  }

  setupMiddleware() {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"],
        },
      },
      crossOriginEmbedderPolicy: false
    }));
    
    // CORS configuration
    this.app.use(cors({
      origin: this.config.security.corsOrigins,
      credentials: true,
      optionsSuccessStatus: 200
    }));
    
    // Compression
    this.app.use(compression());
    
    // Request parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    this.app.use(cookieParser());
    
    // Logging middleware
    if (this.config.nodeEnv === 'development') {
      this.app.use(morgan('dev'));
    } else {
      this.app.use(morgan('combined', {
        stream: {
          write: (message) => this.logger.info(message.trim())
        }
      }));
    }
    
    // Global rate limiting
    this.app.use('/api', rateLimiters.general);
    
    this.logger.info('Middleware configured successfully');
  }

  async initializeComponents() {
    try {
      this.logger.info('Initializing core components...');
      
      // Initialize Network Manager
      this.networkManager = new NetworkManager(this.config.blockchain);
      await this.networkManager.initialize();
      
      // Initialize Sandbox Engine
      this.sandboxEngine = new SandboxEngine({
        networkManager: this.networkManager,
        ...this.config.simulation
      });
      await this.sandboxEngine.initialize();
      
      // Initialize Simulation Engine
      this.simulationEngine = new SimulationEngine(this.config.simulation);
      await this.simulationEngine.initialize();
      
      // Initialize Vulnerability Analyzer
      this.vulnerabilityAnalyzer = new VulnerabilityAnalyzer(this.config.analysis);
      await this.vulnerabilityAnalyzer.initialize();
      
      // Initialize Contract Manager
      this.contractManager = new ContractManager(this.config.contracts);
      await this.contractManager.initialize();
      
      // Initialize Simulation Controller
      this.simulationController = new SimulationController();
      await this.simulationController.initialize({
        simulation: this.config.simulation,
        analysis: this.config.analysis,
        contracts: this.config.contracts
      });
      
      this.logger.info('All core components initialized successfully');
      
    } catch (error) {
      this.logger.error('Failed to initialize components:', error);
      throw error;
    }
  }

  setupRoutes() {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        success: true,
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        environment: this.config.nodeEnv,
        components: {
          networkManager: this.networkManager?.isInitialized || false,
          sandboxEngine: this.sandboxEngine?.isInitialized || false,
          simulationEngine: this.simulationEngine?.isInitialized || false,
          vulnerabilityAnalyzer: this.vulnerabilityAnalyzer?.isInitialized || false,
          contractManager: this.contractManager?.isInitialized || false
        }
      });
    });
    
    // API routes
    this.app.use('/api/v1', v1Routes);
    
    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        success: true,
        message: 'Scorpius Contract Sandbox API',
        version: '1.0.0',
        documentation: '/api/v1/docs',
        health: '/health'
      });
    });
    
    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        success: false,
        error: 'Not Found',
        message: `Route ${req.method} ${req.originalUrl} not found`
      });
    });
    
    this.logger.info('Routes configured successfully');
  }

  setupErrorHandling() {
    // Global error handler
    this.app.use((error, req, res, next) => {
      this.logger.error('Unhandled error:', {
        error: error.message,
        stack: error.stack,
        path: req.path,
        method: req.method,
        userId: req.user?.id || 'anonymous'
      });
      
      // Don't expose stack traces in production
      const errorResponse = {
        success: false,
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
      };
      
      if (this.config.nodeEnv === 'development') {
        errorResponse.details = {
          message: error.message,
          stack: error.stack
        };
      }
      
      res.status(500).json(errorResponse);
    });
    
    // Handle unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      this.logger.error('Unhandled Promise Rejection:', reason);
      // Optionally exit the process
      // process.exit(1);
    });
    
    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      this.logger.error('Uncaught Exception:', error);
      // Gracefully shutdown
      this.shutdown();
      process.exit(1);
    });
    
    this.logger.info('Error handling configured successfully');
  }

  async start() {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    return new Promise((resolve, reject) => {
      this.server = this.app.listen(this.config.port, (error) => {
        if (error) {
          this.logger.error('Failed to start server:', error);
          reject(error);
        } else {
          this.logger.info(`Scorpius Contract Sandbox started on port ${this.config.port}`);
          this.logger.info(`Environment: ${this.config.nodeEnv}`);
          this.logger.info(`Health check: http://localhost:${this.config.port}/health`);
          this.logger.info(`API documentation: http://localhost:${this.config.port}/api/v1/docs`);
          resolve(this.server);
        }
      });
    });
  }

  async shutdown() {
    this.logger.info('Shutting down Scorpius Contract Sandbox...');
    
    try {
      // Close HTTP server
      if (this.server) {
        await new Promise((resolve) => {
          this.server.close(resolve);
        });
        this.logger.info('HTTP server closed');
      }
      
      // Shutdown core components
      const shutdownPromises = [];
      
      if (this.simulationEngine) {
        shutdownPromises.push(this.simulationEngine.shutdown());
      }
      
      if (this.vulnerabilityAnalyzer) {
        shutdownPromises.push(this.vulnerabilityAnalyzer.shutdown());
      }
      
      if (this.contractManager) {
        shutdownPromises.push(this.contractManager.shutdown());
      }
      
      if (this.sandboxEngine) {
        shutdownPromises.push(this.sandboxEngine.shutdown());
      }
      
      if (this.networkManager) {
        shutdownPromises.push(this.networkManager.shutdown());
      }
      
      await Promise.allSettled(shutdownPromises);
      
      this.logger.info('Scorpius Contract Sandbox shutdown complete');
      
    } catch (error) {
      this.logger.error('Error during shutdown:', error);
    }
  }

  // Getter methods for components (useful for testing)
  getNetworkManager() { return this.networkManager; }
  getSandboxEngine() { return this.sandboxEngine; }
  getSimulationEngine() { return this.simulationEngine; }
  getVulnerabilityAnalyzer() { return this.vulnerabilityAnalyzer; }
  getContractManager() { return this.contractManager; }
}

// Start the application if this file is run directly
if (require.main === module) {
  console.log('🔄 Starting Scorpius Contract Sandbox...');
  
  try {
    const app = new ScorpiusApplication();
    console.log('✅ Application instance created');
    
    app.start().then(() => {
      console.log('🚀 Scorpius Contract Sandbox is running!');
    }).catch((error) => {
      console.error('❌ Failed to start Scorpius Contract Sandbox:', error);
      console.error('Stack trace:', error.stack);
      process.exit(1);
    });
  } catch (error) {
    console.error('❌ Failed to create application instance:', error);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
  
  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('📤 SIGTERM received, shutting down gracefully...');
    app.shutdown().then(() => {
      process.exit(0);
    });
  });
  
  process.on('SIGINT', () => {
    console.log('\n📤 SIGINT received, shutting down gracefully...');
    app.shutdown().then(() => {
      process.exit(0);
    });
  });
}

module.exports = ScorpiusApplication; 