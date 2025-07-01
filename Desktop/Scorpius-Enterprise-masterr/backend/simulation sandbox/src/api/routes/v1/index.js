const express = require('express');
const router = express.Router();

// Import route modules
const simulationRoutes = require('./simulation.routes');
// const exploitRoutes = require('./exploits.routes');
// const analysisRoutes = require('./analysis.routes');
// const authRoutes = require('./auth.routes');

// Mount routes
router.use('/simulations', simulationRoutes);
// router.use('/exploits', exploitRoutes);
// router.use('/analysis', analysisRoutes);
// router.use('/auth', authRoutes);

// API Info endpoint
router.get('/', (req, res) => {
  res.json({
    name: 'Scorpius Contract Sandbox API',
    version: 'v1',
    description: 'Smart Contract Security Testing and Exploit Simulation Platform',
    endpoints: {
      simulations: '/api/v1/simulations'
      // auth: '/api/v1/auth',
      // exploits: '/api/v1/exploits', 
      // analysis: '/api/v1/analysis'
    },
    documentation: '/api/docs',
    health: '/health',
    metrics: '/metrics'
  });
});

module.exports = router; 