const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');

const NetworkManager = require('../managers/network-manager');
const ContractManager = require('../managers/contract-manager');
const SessionManager = require('../managers/session-manager');
const ResourceManager = require('../managers/resource-manager');
const Logger = require('../../utils/helpers/logger');

class SandboxEngine extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = config;
    this.logger = new Logger('SandboxEngine');
    
    this.networkManager = new NetworkManager(config);
    this.contractManager = new ContractManager(config);
    this.sessionManager = new SessionManager(config);
    this.resourceManager = new ResourceManager(config);
    
    this.sandboxes = new Map();
    this.isInitialized = false;
    this.maxConcurrentSandboxes = config.maxConcurrentSandboxes || 10;
  }

  async initialize() {
    try {
      this.logger.info('Initializing Sandbox Engine...');
      
      await this.networkManager.initialize();
      await this.contractManager.initialize();
      await this.sessionManager.initialize();
      await this.resourceManager.initialize();
      
      this.isInitialized = true;
      this.logger.info('Sandbox Engine initialized successfully');
      
      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Sandbox Engine:', error);
      throw error;
    }
  }

  async createSandbox(options = {}) {
    if (!this.isInitialized) {
      throw new Error('Sandbox Engine not initialized');
    }

    if (this.sandboxes.size >= this.maxConcurrentSandboxes) {
      throw new Error('Maximum concurrent sandboxes reached');
    }

    const sessionId = uuidv4();
    const sandbox = new SandboxInstance(sessionId, options, {
      networkManager: this.networkManager,
      contractManager: this.contractManager,
      resourceManager: this.resourceManager,
      logger: this.logger
    });

    try {
      await sandbox.initialize();
      this.sandboxes.set(sessionId, sandbox);
      
      this.logger.info(`Sandbox created: ${sessionId}`);
      this.emit('sandboxCreated', { sessionId, sandbox });
      
      return sandbox;
    } catch (error) {
      this.logger.error(`Failed to create sandbox ${sessionId}:`, error);
      throw error;
    }
  }

  async destroySandbox(sessionId) {
    const sandbox = this.sandboxes.get(sessionId);
    if (!sandbox) {
      throw new Error(`Sandbox not found: ${sessionId}`);
    }

    try {
      await sandbox.destroy();
      this.sandboxes.delete(sessionId);
      
      this.logger.info(`Sandbox destroyed: ${sessionId}`);
      this.emit('sandboxDestroyed', { sessionId });
    } catch (error) {
      this.logger.error(`Failed to destroy sandbox ${sessionId}:`, error);
      throw error;
    }
  }

  getSandbox(sessionId) {
    return this.sandboxes.get(sessionId);
  }

  listSandboxes() {
    return Array.from(this.sandboxes.keys());
  }

  async getMetrics() {
    return {
      activeSandboxes: this.sandboxes.size,
      maxConcurrent: this.maxConcurrentSandboxes,
      resourceUsage: await this.resourceManager.getMetrics(),
      networkStatus: await this.networkManager.getStatus()
    };
  }

  async isHealthy() {
    if (!this.isInitialized) return false;
    
    try {
      const networkHealthy = await this.networkManager.isHealthy();
      const resourcesHealthy = await this.resourceManager.isHealthy();
      
      return networkHealthy && resourcesHealthy;
    } catch (error) {
      this.logger.error('Health check failed:', error);
      return false;
    }
  }

  async shutdown() {
    this.logger.info('Shutting down Sandbox Engine...');
    
    // Destroy all active sandboxes
    const destroyPromises = Array.from(this.sandboxes.keys()).map(
      sessionId => this.destroySandbox(sessionId).catch(err => 
        this.logger.error(`Failed to destroy sandbox ${sessionId}:`, err)
      )
    );
    
    await Promise.allSettled(destroyPromises);
    
    // Shutdown managers
    await this.resourceManager.shutdown();
    await this.networkManager.shutdown();
    await this.contractManager.shutdown();
    await this.sessionManager.shutdown();
    
    this.isInitialized = false;
    this.logger.info('Sandbox Engine shutdown complete');
    
    this.emit('shutdown');
  }
}

class SandboxInstance {
  constructor(sessionId, options, dependencies) {
    this.sessionId = sessionId;
    this.options = options;
    this.networkManager = dependencies.networkManager;
    this.contractManager = dependencies.contractManager;
    this.resourceManager = dependencies.resourceManager;
    this.logger = dependencies.logger.child({ sessionId });
    
    this.network = null;
    this.deployedContracts = new Map();
    this.isActive = false;
    this.createdAt = new Date();
    this.lastActivity = new Date();
  }

  async initialize() {
    try {
      this.logger.info('Initializing sandbox instance...');
      
      // Create isolated network
      this.network = await this.networkManager.createNetwork({
        sessionId: this.sessionId,
        forkFrom: this.options.forkFrom,
        blockNumber: this.options.blockNumber
      });
      
      // Allocate resources
      await this.resourceManager.allocateResources(this.sessionId, {
        cpu: this.options.cpuLimit || '1000m',
        memory: this.options.memoryLimit || '2Gi',
        timeout: this.options.timeout || 3600
      });
      
      this.isActive = true;
      this.logger.info('Sandbox instance initialized');
    } catch (error) {
      this.logger.error('Failed to initialize sandbox instance:', error);
      throw error;
    }
  }

  async deployContract(contractCode, constructorArgs = [], options = {}) {
    if (!this.isActive) {
      throw new Error('Sandbox is not active');
    }

    try {
      const deployment = await this.contractManager.deploy({
        code: contractCode,
        args: constructorArgs,
        network: this.network,
        ...options
      });

      this.deployedContracts.set(deployment.address, deployment);
      this.updateActivity();
      
      this.logger.info(`Contract deployed: ${deployment.address}`);
      return deployment;
    } catch (error) {
      this.logger.error('Failed to deploy contract:', error);
      throw error;
    }
  }

  async executeTransaction(transaction) {
    if (!this.isActive) {
      throw new Error('Sandbox is not active');
    }

    try {
      const result = await this.network.sendTransaction(transaction);
      this.updateActivity();
      return result;
    } catch (error) {
      this.logger.error('Failed to execute transaction:', error);
      throw error;
    }
  }

  async getState() {
    return {
      sessionId: this.sessionId,
      isActive: this.isActive,
      createdAt: this.createdAt,
      lastActivity: this.lastActivity,
      deployedContracts: Array.from(this.deployedContracts.keys()),
      networkInfo: await this.network.getInfo()
    };
  }

  updateActivity() {
    this.lastActivity = new Date();
  }

  async destroy() {
    try {
      this.logger.info('Destroying sandbox instance...');
      
      this.isActive = false;
      
      // Clean up deployed contracts
      this.deployedContracts.clear();
      
      // Destroy network
      if (this.network) {
        await this.network.destroy();
      }
      
      // Release resources
      await this.resourceManager.releaseResources(this.sessionId);
      
      this.logger.info('Sandbox instance destroyed');
    } catch (error) {
      this.logger.error('Failed to destroy sandbox instance:', error);
      throw error;
    }
  }
}

module.exports = SandboxEngine; 