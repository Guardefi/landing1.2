const express = require('express');
const SimulationController = require('../../controllers/simulation.controller');
const authMiddleware = require('../../middleware/auth');
const rateLimitMiddleware = require('../../middleware/rate-limit');
const validationMiddleware = require('../../middleware/validation');

const router = express.Router();
const simulationController = new SimulationController();

// Initialize controller (this would be done at app startup)
// simulationController.initialize(config);

/**
 * @route   POST /api/v1/simulations
 * @desc    Create and run a new exploit simulation
 * @access  Private
 */
router.post('/',
  authMiddleware,
  rateLimitMiddleware({ windowMs: 15 * 60 * 1000, max: 10 }), // 10 requests per 15 minutes
  SimulationController.validateCreateSimulation(),
  validationMiddleware,
  async (req, res) => {
    await simulationController.createSimulation(req, res);
  }
);

/**
 * @route   GET /api/v1/simulations/:simulationId/status
 * @desc    Get simulation execution status
 * @access  Private
 */
router.get('/:simulationId/status',
  authMiddleware,
  async (req, res) => {
    await simulationController.getSimulationStatus(req, res);
  }
);

/**
 * @route   POST /api/v1/simulations/:simulationId/abort
 * @desc    Abort a running simulation
 * @access  Private
 */
router.post('/:simulationId/abort',
  authMiddleware,
  async (req, res) => {
    await simulationController.abortSimulation(req, res);
  }
);

/**
 * @route   GET /api/v1/simulations/:simulationId/report
 * @desc    Get comprehensive simulation report
 * @access  Private
 */
router.get('/:simulationId/report',
  authMiddleware,
  async (req, res) => {
    await simulationController.getSimulationReport(req, res);
  }
);

/**
 * @route   GET /api/v1/simulations/metrics
 * @desc    Get simulation engine metrics and statistics
 * @access  Private
 */
router.get('/metrics',
  authMiddleware,
  async (req, res) => {
    await simulationController.getMetrics(req, res);
  }
);

/**
 * @route   POST /api/v1/simulations/analyze
 * @desc    Analyze contract for vulnerabilities
 * @access  Private
 */
router.post('/analyze',
  authMiddleware,
  rateLimitMiddleware({ windowMs: 15 * 60 * 1000, max: 20 }), // 20 requests per 15 minutes
  SimulationController.validateAnalyzeContract(),
  validationMiddleware,
  async (req, res) => {
    await simulationController.analyzeContract(req, res);
  }
);

/**
 * @route   POST /api/v1/simulations/deploy
 * @desc    Deploy contract for testing
 * @access  Private
 */
router.post('/deploy',
  authMiddleware,
  rateLimitMiddleware({ windowMs: 15 * 60 * 1000, max: 5 }), // 5 deployments per 15 minutes
  SimulationController.validateDeployContract(),
  validationMiddleware,
  async (req, res) => {
    await simulationController.deployContract(req, res);
  }
);

/**
 * @route   GET /api/v1/simulations/health
 * @desc    Health check for simulation services
 * @access  Public
 */
router.get('/health',
  async (req, res) => {
    await simulationController.healthCheck(req, res);
  }
);

module.exports = router; 