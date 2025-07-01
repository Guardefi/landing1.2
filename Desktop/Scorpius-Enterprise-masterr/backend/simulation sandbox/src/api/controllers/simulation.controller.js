const { SimulationEngine, SimulationType, SimulationConfig } = require('../../exploits/simulation/simulation-engine');
const { VulnerabilityAnalyzer } = require('../../security/audit/vulnerability-analyzer');
const { ContractManager } = require('../../core/managers/contract-manager');
const Logger = require('../../utils/helpers/logger');
const { body, param, query, validationResult } = require('express-validator');

class SimulationController {
  constructor() {
    this.logger = new Logger('SimulationController');
    this.simulationEngine = null;
    this.vulnerabilityAnalyzer = null;
    this.contractManager = null;
  }

  async initialize(config = {}) {
    try {
      this.simulationEngine = new SimulationEngine(config.simulation);
      this.vulnerabilityAnalyzer = new VulnerabilityAnalyzer(config.analysis);
      this.contractManager = new ContractManager(config.contracts);
      
      await Promise.all([
        this.simulationEngine.initialize(),
        this.vulnerabilityAnalyzer.initialize(),
        this.contractManager.initialize()
      ]);
      
      this.logger.info('Simulation Controller initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Simulation Controller:', error);
      throw error;
    }
  }

  /**
   * Validation middleware for simulation creation
   */
  static validateCreateSimulation() {
    return [
      body('type')
        .isIn(Object.values(SimulationType))
        .withMessage('Invalid simulation type'),
      body('target.contractCode')
        .notEmpty()
        .withMessage('Contract code is required'),
      body('target.contractName')
        .optional()
        .isString()
        .withMessage('Contract name must be a string'),
      body('exploitParams')
        .optional()
        .isObject()
        .withMessage('Exploit parameters must be an object'),
      body('config.timeout')
        .optional()
        .isInt({ min: 1000, max: 600000 })
        .withMessage('Timeout must be between 1 second and 10 minutes'),
      body('config.maxGasLimit')
        .optional()
        .isInt({ min: 21000, max: 30000000 })
        .withMessage('Gas limit must be between 21,000 and 30,000,000')
    ];
  }

  /**
   * Create and run a new simulation
   */
  async createSimulation(req, res) {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: 'Validation failed',
          details: errors.array()
        });
      }

      const { type, target, exploitParams = {}, config = {} } = req.body;
      
      this.logger.info(`Creating ${type} simulation for contract ${target.contractName || 'Unnamed'}`);

      // Create simulation configuration
      const simulationConfig = new SimulationConfig(config);

      // Pre-analysis of contract (optional)
      let preAnalysis = null;
      if (config.runPreAnalysis) {
        this.logger.debug('Running pre-analysis...');
        preAnalysis = await this.vulnerabilityAnalyzer.analyze(
          target.contractCode,
          target.contractName || 'TargetContract',
          { analysisType: 'static' }
        );
      }

      // Run simulation
      const result = await this.simulationEngine.runSimulation(
        type,
        target,
        exploitParams,
        simulationConfig
      );

      // Enhanced response with pre-analysis data
      const response = {
        success: true,
        data: {
          simulation: result.toDict(),
          preAnalysis: preAnalysis ? {
            vulnerabilityCount: preAnalysis.vulnerabilities.length,
            securityScore: preAnalysis.securityScore,
            riskLevel: preAnalysis.getRiskLevel(),
            criticalIssues: preAnalysis.vulnerabilities.filter(v => v.severity === 'critical').length
          } : null,
          metadata: {
            executionTime: result.executionTime,
            timestamp: new Date().toISOString(),
            version: '1.0.0'
          }
        }
      };

      res.status(201).json(response);

    } catch (error) {
      this.logger.error('Failed to create simulation:', error);
      
      res.status(500).json({
        success: false,
        error: 'Simulation creation failed',
        message: error.message,
        ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
      });
    }
  }

  /**
   * Get simulation status
   */
  async getSimulationStatus(req, res) {
    try {
      const { simulationId } = req.params;
      
      const status = this.simulationEngine.getSimulationStatus(simulationId);
      
      if (status === null) {
        return res.status(404).json({
          success: false,
          error: 'Simulation not found'
        });
      }

      const response = {
        success: true,
        data: {
          simulationId,
          status,
          timestamp: new Date().toISOString()
        }
      };

      res.json(response);

    } catch (error) {
      this.logger.error('Failed to get simulation status:', error);
      
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve simulation status',
        message: error.message
      });
    }
  }

  /**
   * Abort a running simulation
   */
  async abortSimulation(req, res) {
    try {
      const { simulationId } = req.params;
      const { reason = 'manual' } = req.body;
      
      const result = await this.simulationEngine.abortSimulation(simulationId, reason);
      
      const response = {
        success: true,
        data: {
          simulationId,
          result: result.toDict(),
          message: 'Simulation aborted successfully'
        }
      };

      res.json(response);

    } catch (error) {
      this.logger.error('Failed to abort simulation:', error);
      
      if (error.message.includes('not found')) {
        res.status(404).json({
          success: false,
          error: 'Simulation not found'
        });
      } else {
        res.status(500).json({
          success: false,
          error: 'Failed to abort simulation',
          message: error.message
        });
      }
    }
  }

  /**
   * Get simulation metrics and statistics
   */
  async getMetrics(req, res) {
    try {
      const metrics = this.simulationEngine.getMetrics();
      
      const response = {
        success: true,
        data: {
          metrics,
          timestamp: new Date().toISOString()
        }
      };

      res.json(response);

    } catch (error) {
      this.logger.error('Failed to get metrics:', error);
      
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve metrics',
        message: error.message
      });
    }
  }

  /**
   * Run contract analysis
   */
  async analyzeContract(req, res) {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: 'Validation failed',
          details: errors.array()
        });
      }

      const { contractCode, contractName = 'Contract', analysisType = 'hybrid' } = req.body;
      
      this.logger.info(`Analyzing contract ${contractName} with ${analysisType} analysis`);

      const result = await this.vulnerabilityAnalyzer.analyze(
        contractCode,
        contractName,
        { analysisType }
      );

      const response = {
        success: true,
        data: {
          analysis: {
            analysisId: result.analysisId,
            contractName: result.contractName,
            analysisType: result.analysisType,
            securityScore: result.securityScore,
            riskLevel: result.getRiskLevel(),
            vulnerabilities: result.vulnerabilities.map(v => ({
              id: v.id,
              type: v.type,
              severity: v.severity,
              title: v.title,
              description: v.description,
              location: v.location,
              recommendation: v.recommendation,
              confidence: v.confidence
            })),
            severityCount: result.getSeverityCount(),
            gasOptimizations: result.gasOptimizations,
            recommendations: result.recommendations,
            aiInsights: result.aiInsights,
            executionTime: result.executionTime
          },
          metadata: {
            analyzedAt: result.analyzedAt,
            version: '1.0.0'
          }
        }
      };

      res.status(201).json(response);

    } catch (error) {
      this.logger.error('Failed to analyze contract:', error);
      
      res.status(500).json({
        success: false,
        error: 'Contract analysis failed',
        message: error.message
      });
    }
  }

  /**
   * Validation middleware for contract analysis
   */
  static validateAnalyzeContract() {
    return [
      body('contractCode')
        .notEmpty()
        .withMessage('Contract code is required'),
      body('contractName')
        .optional()
        .isString()
        .withMessage('Contract name must be a string'),
      body('analysisType')
        .optional()
        .isIn(['static', 'dynamic', 'symbolic', 'formal_verification', 'ai_assisted', 'hybrid'])
        .withMessage('Invalid analysis type')
    ];
  }

  /**
   * Deploy contract for testing
   */
  async deployContract(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: 'Validation failed',
          details: errors.array()
        });
      }

      const { contractCode, contractName, constructorArgs = [], network = 'localhost' } = req.body;
      
      this.logger.info(`Deploying contract ${contractName} to ${network}`);

      // Get network configuration (simplified for this example)
      const networkConfig = {
        networkId: 1337,
        provider: null // Would be initialized with actual provider
      };

      const deployment = await this.contractManager.deploy({
        code: contractCode,
        args: constructorArgs,
        network: networkConfig,
        contractName
      });

      const response = {
        success: true,
        data: {
          deployment: {
            deploymentId: deployment.deploymentId,
            contractName: deployment.contractName,
            address: deployment.address,
            transactionHash: deployment.transactionHash,
            blockNumber: deployment.blockNumber,
            gasUsed: deployment.gasUsed,
            deploymentCost: deployment.deploymentCost,
            status: deployment.status
          },
          metadata: {
            deployedAt: deployment.deployedAt,
            network: network
          }
        }
      };

      res.status(201).json(response);

    } catch (error) {
      this.logger.error('Failed to deploy contract:', error);
      
      res.status(500).json({
        success: false,
        error: 'Contract deployment failed',
        message: error.message
      });
    }
  }

  /**
   * Validation middleware for contract deployment
   */
  static validateDeployContract() {
    return [
      body('contractCode')
        .notEmpty()
        .withMessage('Contract code is required'),
      body('contractName')
        .notEmpty()
        .withMessage('Contract name is required'),
      body('constructorArgs')
        .optional()
        .isArray()
        .withMessage('Constructor arguments must be an array'),
      body('network')
        .optional()
        .isString()
        .withMessage('Network must be a string')
    ];
  }

  /**
   * Get comprehensive simulation report
   */
  async getSimulationReport(req, res) {
    try {
      const { simulationId } = req.params;
      
      // This would generate a comprehensive report
      // combining simulation results, analysis data, and recommendations
      
      const report = {
        simulationId,
        generatedAt: new Date().toISOString(),
        summary: {
          status: 'completed',
          riskLevel: 'HIGH',
          vulnerabilitiesFound: 5,
          exploitSuccess: true,
          fundsAtRisk: '10 ETH'
        },
        detailedFindings: [
          // Would be populated with actual findings
        ],
        recommendations: [
          // Would be populated with actual recommendations
        ],
        nextSteps: [
          'Implement recommended security controls',
          'Conduct additional testing',
          'Review access control mechanisms'
        ]
      };

      const response = {
        success: true,
        data: { report }
      };

      res.json(response);

    } catch (error) {
      this.logger.error('Failed to generate simulation report:', error);
      
      res.status(500).json({
        success: false,
        error: 'Failed to generate report',
        message: error.message
      });
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(req, res) {
    try {
      const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          simulationEngine: this.simulationEngine?.isInitialized || false,
          vulnerabilityAnalyzer: this.vulnerabilityAnalyzer?.isInitialized || false,
          contractManager: this.contractManager?.isInitialized || false
        },
        metrics: this.simulationEngine?.getMetrics() || {}
      };

      res.json({
        success: true,
        data: health
      });

    } catch (error) {
      this.logger.error('Health check failed:', error);
      
      res.status(503).json({
        success: false,
        error: 'Service unhealthy',
        message: error.message
      });
    }
  }
}

module.exports = SimulationController; 