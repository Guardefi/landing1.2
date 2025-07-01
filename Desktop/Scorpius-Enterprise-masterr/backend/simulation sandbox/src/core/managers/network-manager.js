const { ethers } = require('ethers');
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const EventEmitter = require('events');
const Logger = require('../../utils/helpers/logger');

class NetworkManager extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = config;
    this.logger = new Logger('NetworkManager');
    
    this.networks = new Map();
    this.providers = new Map();
    this.isInitialized = false;
    
    // Network configurations
    this.networkConfigs = {
      ethereum: {
        name: 'Ethereum Mainnet',
        chainId: 1,
        rpcUrl: process.env.ETHEREUM_RPC_URL,
        blockExplorer: 'https://etherscan.io'
      },
      polygon: {
        name: 'Polygon Mainnet',
        chainId: 137,
        rpcUrl: process.env.POLYGON_RPC_URL,
        blockExplorer: 'https://polygonscan.com'
      },
      arbitrum: {
        name: 'Arbitrum One',
        chainId: 42161,
        rpcUrl: process.env.ARBITRUM_RPC_URL,
        blockExplorer: 'https://arbiscan.io'
      },
      optimism: {
        name: 'Optimism',
        chainId: 10,
        rpcUrl: process.env.OPTIMISM_RPC_URL,
        blockExplorer: 'https://optimistic.etherscan.io'
      }
    };
  }

  async initialize() {
    try {
      this.logger.info('Initializing Network Manager...');
      
      // Initialize providers for each network
      for (const [networkName, config] of Object.entries(this.networkConfigs)) {
        if (config.rpcUrl) {
          const provider = new ethers.providers.JsonRpcProvider(config.rpcUrl);
          this.providers.set(networkName, provider);
          this.logger.info(`Provider initialized for ${networkName}`);
        }
      }
      
      this.isInitialized = true;
      this.logger.info('Network Manager initialized successfully');
      
      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Network Manager:', error);
      throw error;
    }
  }

  async createNetwork(options = {}) {
    if (!this.isInitialized) {
      throw new Error('Network Manager not initialized');
    }

    const networkId = uuidv4();
    const network = new NetworkInstance(networkId, options, {
      providers: this.providers,
      configs: this.networkConfigs,
      logger: this.logger
    });

    try {
      await network.initialize();
      this.networks.set(networkId, network);
      
      this.logger.info(`Network created: ${networkId}`);
      this.emit('networkCreated', { networkId, network });
      
      return network;
    } catch (error) {
      this.logger.error(`Failed to create network ${networkId}:`, error);
      throw error;
    }
  }

  async destroyNetwork(networkId) {
    const network = this.networks.get(networkId);
    if (!network) {
      throw new Error(`Network not found: ${networkId}`);
    }

    try {
      await network.destroy();
      this.networks.delete(networkId);
      
      this.logger.info(`Network destroyed: ${networkId}`);
      this.emit('networkDestroyed', { networkId });
    } catch (error) {
      this.logger.error(`Failed to destroy network ${networkId}:`, error);
      throw error;
    }
  }

  getNetwork(networkId) {
    return this.networks.get(networkId);
  }

  async getStatus() {
    const status = {
      initialized: this.isInitialized,
      activeNetworks: this.networks.size,
      availableProviders: this.providers.size,
      providers: {}
    };

    for (const [name, provider] of this.providers) {
      try {
        const blockNumber = await provider.getBlockNumber();
        status.providers[name] = {
          connected: true,
          blockNumber,
          chainId: this.networkConfigs[name].chainId
        };
      } catch (error) {
        status.providers[name] = {
          connected: false,
          error: error.message
        };
      }
    }

    return status;
  }

  async isHealthy() {
    if (!this.isInitialized) return false;
    
    try {
      // Check if at least one provider is healthy
      for (const provider of this.providers.values()) {
        await provider.getBlockNumber();
        return true;
      }
      return false;
    } catch (error) {
      this.logger.error('Health check failed:', error);
      return false;
    }
  }

  async shutdown() {
    this.logger.info('Shutting down Network Manager...');
    
    // Destroy all active networks
    const destroyPromises = Array.from(this.networks.keys()).map(
      networkId => this.destroyNetwork(networkId).catch(err => 
        this.logger.error(`Failed to destroy network ${networkId}:`, err)
      )
    );
    
    await Promise.allSettled(destroyPromises);
    
    // Clear providers
    this.providers.clear();
    
    this.isInitialized = false;
    this.logger.info('Network Manager shutdown complete');
    
    this.emit('shutdown');
  }
}

class NetworkInstance {
  constructor(networkId, options, dependencies) {
    this.networkId = networkId;
    this.options = options;
    this.providers = dependencies.providers;
    this.configs = dependencies.configs;
    this.logger = dependencies.logger.child({ networkId });
    
    this.provider = null;
    this.anvilProcess = null;
    this.isActive = false;
    this.createdAt = new Date();
    this.port = null;
  }

  async initialize() {
    try {
      this.logger.info('Initializing network instance...');
      
      if (this.options.type === 'local' || this.options.forkFrom) {
        // Create local network with Anvil
        await this.createLocalNetwork();
      } else {
        // Use existing network provider
        const networkName = this.options.network || 'ethereum';
        this.provider = this.providers.get(networkName);
        
        if (!this.provider) {
          throw new Error(`Provider not found for network: ${networkName}`);
        }
      }
      
      this.isActive = true;
      this.logger.info('Network instance initialized');
    } catch (error) {
      this.logger.error('Failed to initialize network instance:', error);
      throw error;
    }
  }

  async createLocalNetwork() {
    const port = await this.findAvailablePort();
    this.port = port;
    
    const args = [
      '--port', port.toString(),
      '--chain-id', '31337',
      '--accounts', '10',
      '--balance', '10000'
    ];

    // Add fork configuration if specified
    if (this.options.forkFrom) {
      const baseProvider = this.providers.get(this.options.forkFrom);
      if (baseProvider) {
        args.push('--fork-url', baseProvider.connection.url);
        
        if (this.options.blockNumber) {
          args.push('--fork-block-number', this.options.blockNumber.toString());
        }
      }
    }

    this.anvilProcess = spawn('anvil', args, {
      stdio: ['ignore', 'pipe', 'pipe']
    });

    return new Promise((resolve, reject) => {
      let output = '';
      
      this.anvilProcess.stdout.on('data', (data) => {
        output += data.toString();
        if (output.includes('Listening on')) {
          this.provider = new ethers.providers.JsonRpcProvider(`http://localhost:${port}`);
          resolve();
        }
      });

      this.anvilProcess.stderr.on('data', (data) => {
        this.logger.error('Anvil error:', data.toString());
      });

      this.anvilProcess.on('error', (error) => {
        reject(new Error(`Failed to start Anvil: ${error.message}`));
      });

      this.anvilProcess.on('exit', (code) => {
        if (code !== 0) {
          reject(new Error(`Anvil exited with code ${code}`));
        }
      });

      // Timeout after 30 seconds
      setTimeout(() => {
        reject(new Error('Timeout waiting for Anvil to start'));
      }, 30000);
    });
  }

  async findAvailablePort() {
    const net = require('net');
    
    return new Promise((resolve) => {
      const server = net.createServer();
      server.listen(0, () => {
        const port = server.address().port;
        server.close(() => resolve(port));
      });
    });
  }

  async sendTransaction(transaction) {
    if (!this.isActive || !this.provider) {
      throw new Error('Network is not active');
    }

    try {
      const result = await this.provider.sendTransaction(transaction);
      return result;
    } catch (error) {
      this.logger.error('Failed to send transaction:', error);
      throw error;
    }
  }

  async getBlockNumber() {
    if (!this.provider) {
      throw new Error('Provider not available');
    }
    
    return await this.provider.getBlockNumber();
  }

  async getBalance(address) {
    if (!this.provider) {
      throw new Error('Provider not available');
    }
    
    return await this.provider.getBalance(address);
  }

  async getInfo() {
    if (!this.provider) {
      return { status: 'inactive' };
    }

    try {
      const blockNumber = await this.provider.getBlockNumber();
      const network = await this.provider.getNetwork();
      
      return {
        networkId: this.networkId,
        chainId: network.chainId,
        blockNumber,
        isActive: this.isActive,
        createdAt: this.createdAt,
        port: this.port,
        type: this.options.type || 'remote'
      };
    } catch (error) {
      return {
        networkId: this.networkId,
        isActive: false,
        error: error.message
      };
    }
  }

  async destroy() {
    try {
      this.logger.info('Destroying network instance...');
      
      this.isActive = false;
      
      // Kill Anvil process if running
      if (this.anvilProcess) {
        this.anvilProcess.kill('SIGTERM');
        
        // Force kill after 5 seconds
        setTimeout(() => {
          if (this.anvilProcess && !this.anvilProcess.killed) {
            this.anvilProcess.kill('SIGKILL');
          }
        }, 5000);
      }
      
      this.provider = null;
      
      this.logger.info('Network instance destroyed');
    } catch (error) {
      this.logger.error('Failed to destroy network instance:', error);
      throw error;
    }
  }
}

module.exports = NetworkManager; 