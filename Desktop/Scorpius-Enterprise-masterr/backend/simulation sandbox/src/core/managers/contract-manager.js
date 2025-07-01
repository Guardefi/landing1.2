const { ethers } = require('ethers');
const solc = require('solc');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const Logger = require('../../utils/helpers/logger');

/**
 * Contract deployment status
 */
const DeploymentStatus = {
  PENDING: 'pending',
  COMPILING: 'compiling',
  DEPLOYING: 'deploying',
  DEPLOYED: 'deployed',
  FAILED: 'failed',
  VERIFIED: 'verified'
};

/**
 * Contract deployment result
 */
class DeploymentResult {
  constructor({
    deploymentId,
    contractName,
    address,
    transactionHash,
    blockNumber,
    gasUsed,
    deploymentCost,
    abi,
    bytecode,
    sourceCode,
    constructorArgs = [],
    metadata = {},
    status = DeploymentStatus.DEPLOYED
  }) {
    this.deploymentId = deploymentId;
    this.contractName = contractName;
    this.address = address;
    this.transactionHash = transactionHash;
    this.blockNumber = blockNumber;
    this.gasUsed = gasUsed;
    this.deploymentCost = deploymentCost;
    this.abi = abi;
    this.bytecode = bytecode;
    this.sourceCode = sourceCode;
    this.constructorArgs = constructorArgs;
    this.metadata = metadata;
    this.status = status;
    this.deployedAt = new Date();
  }

  toDict() {
    return {
      deploymentId: this.deploymentId,
      contractName: this.contractName,
      address: this.address,
      transactionHash: this.transactionHash,
      blockNumber: this.blockNumber,
      gasUsed: this.gasUsed,
      deploymentCost: this.deploymentCost,
      abi: this.abi,
      bytecode: this.bytecode,
      sourceCode: this.sourceCode,
      constructorArgs: this.constructorArgs,
      metadata: this.metadata,
      status: this.status,
      deployedAt: this.deployedAt
    };
  }
}

/**
 * Enterprise Contract Manager
 * 
 * Handles compilation, deployment, and management of smart contracts
 * in isolated sandbox environments with comprehensive error handling
 * and security features.
 */
class ContractManager extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = config;
    this.logger = new Logger('ContractManager');
    
    // State management
    this.deployments = new Map();
    this.compilationCache = new Map();
    this.contractTemplates = new Map();
    
    // Configuration
    this.solidityVersion = config.solidityVersion || '0.8.21';
    this.optimizerEnabled = config.optimizerEnabled !== false;
    this.optimizerRuns = config.optimizerRuns || 200;
    this.evmVersion = config.evmVersion || 'london';
    
    // Security settings
    this.maxContractSize = config.maxContractSize || 24576; // 24KB limit
    this.gasLimit = config.gasLimit || 8000000;
    this.allowUnsafeCode = config.allowUnsafeCode || false;
    
    this.isInitialized = false;
  }

  async initialize() {
    try {
      this.logger.info('Initializing Contract Manager...');
      
      // Load contract templates
      await this.loadContractTemplates();
      
      // Initialize compiler settings
      this.compilerSettings = {
        language: 'Solidity',
        sources: {},
        settings: {
          optimizer: {
            enabled: this.optimizerEnabled,
            runs: this.optimizerRuns
          },
          evmVersion: this.evmVersion,
          outputSelection: {
            '*': {
              '*': ['*']
            }
          }
        }
      };
      
      this.isInitialized = true;
      this.logger.info('Contract Manager initialized successfully');
      
      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Contract Manager:', error);
      throw error;
    }
  }

  /**
   * Compile Solidity source code
   */
  async compile(sourceCode, contractName, options = {}) {
    if (!this.isInitialized) {
      throw new Error('Contract Manager not initialized');
    }

    const cacheKey = this.generateCacheKey(sourceCode, contractName);
    
    // Check compilation cache
    if (this.compilationCache.has(cacheKey) && !options.forceRecompile) {
      this.logger.debug(`Using cached compilation for ${contractName}`);
      return this.compilationCache.get(cacheKey);
    }

    this.logger.info(`Compiling contract: ${contractName}`);
    
    try {
      // Prepare compiler input
      const input = {
        ...this.compilerSettings,
        sources: {
          [`${contractName}.sol`]: {
            content: sourceCode
          }
        }
      };

      // Add imports if specified
      if (options.imports) {
        Object.entries(options.imports).forEach(([importPath, content]) => {
          input.sources[importPath] = { content };
        });
      }

      // Compile with specified Solidity version
      const output = JSON.parse(solc.compile(JSON.stringify(input)));

      // Check for compilation errors
      if (output.errors) {
        const errors = output.errors.filter(error => error.severity === 'error');
        const warnings = output.errors.filter(error => error.severity === 'warning');
        
        if (warnings.length > 0) {
          this.logger.warn(`Compilation warnings for ${contractName}:`, warnings);
        }
        
        if (errors.length > 0) {
          this.logger.error(`Compilation errors for ${contractName}:`, errors);
          throw new Error(`Compilation failed: ${errors.map(e => e.message).join(', ')}`);
        }
      }

      // Extract compilation results
      const contractKey = `${contractName}.sol:${contractName}`;
      const compiledContract = output.contracts[`${contractName}.sol`][contractName];
      
      if (!compiledContract) {
        throw new Error(`Contract ${contractName} not found in compilation output`);
      }

      const result = {
        contractName,
        abi: compiledContract.abi,
        bytecode: compiledContract.evm.bytecode.object,
        deployedBytecode: compiledContract.evm.deployedBytecode.object,
        sourceMap: compiledContract.evm.bytecode.sourceMap,
        deployedSourceMap: compiledContract.evm.deployedBytecode.sourceMap,
        gasEstimates: compiledContract.evm.gasEstimates,
        metadata: compiledContract.metadata,
        userdoc: compiledContract.userdoc,
        devdoc: compiledContract.devdoc
      };

      // Security checks
      await this.performSecurityChecks(result, sourceCode);

      // Cache the result
      this.compilationCache.set(cacheKey, result);
      
      this.logger.info(`Successfully compiled ${contractName}`);
      this.emit('contractCompiled', { contractName, result });
      
      return result;
      
    } catch (error) {
      this.logger.error(`Failed to compile ${contractName}:`, error);
      throw error;
    }
  }

  /**
   * Deploy a compiled contract
   */
  async deploy({ code, args = [], network, gasLimit, gasPrice, value = 0, ...options }) {
    if (!this.isInitialized) {
      throw new Error('Contract Manager not initialized');
    }

    const deploymentId = uuidv4();
    let compilationResult;
    let contractName = options.contractName || 'Contract';

    this.logger.info(`Starting deployment ${deploymentId} for ${contractName}`);

    try {
      // Compile if source code is provided
      if (typeof code === 'string' && code.includes('pragma solidity')) {
        this.logger.debug('Compiling source code for deployment');
        compilationResult = await this.compile(code, contractName, options);
      } else if (typeof code === 'object' && code.abi && code.bytecode) {
        // Pre-compiled contract
        compilationResult = code;
      } else {
        throw new Error('Invalid contract code format');
      }

      // Validate bytecode size
      const bytecodeSize = (compilationResult.bytecode.length - 2) / 2; // Remove 0x prefix and convert to bytes
      if (bytecodeSize > this.maxContractSize) {
        throw new Error(`Contract size ${bytecodeSize} exceeds maximum limit ${this.maxContractSize}`);
      }

      // Get network provider
      const provider = network.provider;
      if (!provider) {
        throw new Error('Network provider not available');
      }

      // Create contract factory
      const contractFactory = new ethers.ContractFactory(
        compilationResult.abi,
        compilationResult.bytecode,
        provider.getSigner ? provider.getSigner() : provider
      );

      // Estimate gas if not provided
      const estimatedGas = gasLimit || await contractFactory.signer.estimateGas(
        contractFactory.getDeployTransaction(...args)
      );

      // Deploy contract
      this.logger.debug(`Deploying contract with gas limit: ${estimatedGas}`);
      const contract = await contractFactory.deploy(...args, {
        gasLimit: estimatedGas,
        gasPrice: gasPrice,
        value: value
      });

      // Wait for deployment
      const deploymentTransaction = await contract.deployTransaction.wait();

      // Create deployment result
      const deployment = new DeploymentResult({
        deploymentId,
        contractName,
        address: contract.address,
        transactionHash: deploymentTransaction.transactionHash,
        blockNumber: deploymentTransaction.blockNumber,
        gasUsed: deploymentTransaction.gasUsed.toString(),
        deploymentCost: deploymentTransaction.gasUsed.mul(deploymentTransaction.effectiveGasPrice || gasPrice || 0).toString(),
        abi: compilationResult.abi,
        bytecode: compilationResult.bytecode,
        sourceCode: typeof code === 'string' ? code : null,
        constructorArgs: args,
        metadata: {
          ...options,
          networkId: network.networkId,
          compilerVersion: this.solidityVersion
        }
      });

      // Store deployment
      this.deployments.set(deploymentId, deployment);
      
      this.logger.info(`Successfully deployed ${contractName} at ${contract.address}`);
      this.emit('contractDeployed', { deploymentId, deployment });
      
      return deployment;
      
    } catch (error) {
      this.logger.error(`Failed to deploy contract ${contractName}:`, error);
      
      const failedDeployment = new DeploymentResult({
        deploymentId,
        contractName,
        address: null,
        transactionHash: null,
        blockNumber: null,
        gasUsed: '0',
        deploymentCost: '0',
        abi: compilationResult?.abi || null,
        bytecode: compilationResult?.bytecode || null,
        sourceCode: typeof code === 'string' ? code : null,
        constructorArgs: args,
        status: DeploymentStatus.FAILED,
        metadata: { error: error.message }
      });
      
      this.emit('deploymentFailed', { deploymentId, error, deployment: failedDeployment });
      throw error;
    }
  }

  /**
   * Get contract instance for interaction
   */
  async getContractInstance(deploymentId, network) {
    const deployment = this.deployments.get(deploymentId);
    if (!deployment) {
      throw new Error(`Deployment ${deploymentId} not found`);
    }

    if (!deployment.address) {
      throw new Error(`Deployment ${deploymentId} has no valid address`);
    }

    const provider = network.provider;
    const signer = provider.getSigner ? provider.getSigner() : provider;
    
    return new ethers.Contract(deployment.address, deployment.abi, signer);
  }

  /**
   * Verify contract on block explorer (simulation)
   */
  async verifyContract(deploymentId, options = {}) {
    const deployment = this.deployments.get(deploymentId);
    if (!deployment) {
      throw new Error(`Deployment ${deploymentId} not found`);
    }

    this.logger.info(`Verifying contract ${deployment.contractName} at ${deployment.address}`);
    
    // Simulate verification process
    await this.sleep(2000);
    
    deployment.status = DeploymentStatus.VERIFIED;
    deployment.metadata.verified = true;
    deployment.metadata.verifiedAt = new Date();
    
    this.logger.info(`Contract ${deployment.contractName} verified successfully`);
    this.emit('contractVerified', { deploymentId, deployment });
    
    return true;
  }

  /**
   * Perform security checks on compiled contract
   */
  async performSecurityChecks(compilationResult, sourceCode) {
    const issues = [];

    // Check for common vulnerabilities
    if (sourceCode.includes('.call(') && !sourceCode.includes('reentrancyGuard')) {
      issues.push({
        type: 'warning',
        message: 'Potential reentrancy vulnerability detected'
      });
    }

    if (sourceCode.includes('tx.origin')) {
      issues.push({
        type: 'warning',
        message: 'Use of tx.origin detected - prefer msg.sender'
      });
    }

    if (sourceCode.includes('block.timestamp') || sourceCode.includes('now')) {
      issues.push({
        type: 'info',
        message: 'Timestamp dependence detected'
      });
    }

    if (sourceCode.includes('selfdestruct') && !this.allowUnsafeCode) {
      issues.push({
        type: 'error',
        message: 'Self-destruct not allowed in sandbox environment'
      });
    }

    // Log issues
    if (issues.length > 0) {
      this.logger.warn('Security check issues found:', issues);
    }

    return issues;
  }

  /**
   * Load contract templates
   */
  async loadContractTemplates() {
    try {
      const templatesDir = path.join(__dirname, '../../../contracts/templates');
      
      // This would load actual template files in a real implementation
      this.contractTemplates.set('vulnerable', {
        name: 'VulnerableContract',
        description: 'A deliberately vulnerable contract for testing',
        category: 'testing'
      });
      
      this.contractTemplates.set('secure', {
        name: 'SecureContract',
        description: 'A secure contract template',
        category: 'template'
      });
      
      this.logger.debug(`Loaded ${this.contractTemplates.size} contract templates`);
    } catch (error) {
      this.logger.warn('Failed to load contract templates:', error);
    }
  }

  /**
   * Generate cache key for compilation
   */
  generateCacheKey(sourceCode, contractName) {
    const crypto = require('crypto');
    const hash = crypto.createHash('sha256');
    hash.update(sourceCode + contractName + this.solidityVersion);
    return hash.digest('hex');
  }

  /**
   * Get deployment by ID
   */
  getDeployment(deploymentId) {
    return this.deployments.get(deploymentId);
  }

  /**
   * List all deployments
   */
  listDeployments(filters = {}) {
    let deployments = Array.from(this.deployments.values());
    
    if (filters.status) {
      deployments = deployments.filter(d => d.status === filters.status);
    }
    
    if (filters.contractName) {
      deployments = deployments.filter(d => d.contractName.includes(filters.contractName));
    }
    
    return deployments;
  }

  /**
   * Get compilation cache statistics
   */
  getCacheStats() {
    return {
      cacheSize: this.compilationCache.size,
      hitRate: this.cacheHitRate || 0
    };
  }

  /**
   * Utility sleep function
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Shutdown the contract manager
   */
  async shutdown() {
    this.logger.info('Shutting down Contract Manager...');
    
    // Clear caches
    this.compilationCache.clear();
    this.deployments.clear();
    this.contractTemplates.clear();
    
    this.isInitialized = false;
    this.logger.info('Contract Manager shutdown complete');
    
    this.emit('shutdown');
  }
}

module.exports = {
  ContractManager,
  DeploymentStatus,
  DeploymentResult
}; 