# Scorpius Contract Sandbox

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)
![Security](https://img.shields.io/badge/security-A+-green.svg)

**Enterprise Smart Contract Security Testing and Exploit Simulation Platform**

Scorpius Contract Sandbox is a comprehensive, enterprise-grade platform designed for smart contract security testing, vulnerability analysis, and exploit simulation. Built for security researchers, auditors, and blockchain developers who need a robust environment to test smart contract security scenarios.

## 🚀 Features

### Core Capabilities
- **Isolated Sandbox Environment**: Create secure, isolated blockchain environments for testing
- **Multi-Network Support**: Ethereum, Polygon, Arbitrum, Optimism, and custom networks
- **Exploit Simulation**: Built-in exploit patterns including flash loans, reentrancy, oracle manipulation
- **Advanced Analytics**: Static, dynamic, and formal verification tools integration
- **Real-time Monitoring**: Comprehensive monitoring and alerting system

### Security Features
- **Multi-Factor Authentication**: JWT, OAuth, LDAP integration
- **Role-Based Access Control**: Granular permission system
- **Audit Logging**: Comprehensive audit trail for compliance
- **Data Encryption**: End-to-end encryption for sensitive data
- **Security Scanning**: Automated vulnerability scanning

### Enterprise Ready
- **Kubernetes Deployment**: Full Kubernetes support with Helm charts
- **Microservices Architecture**: Scalable, maintainable design
- **CI/CD Integration**: Complete GitHub Actions workflows
- **Monitoring Stack**: Prometheus, Grafana, AlertManager integration
- **High Availability**: Multi-region deployment support

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Development](#development)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## ⚡ Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Docker and Docker Compose
- Git
- PostgreSQL 14+ (or use Docker)
- Redis 6+ (or use Docker)

### Installation

```bash
# Clone the repository
git clone https://github.com/scorpius-security/contract-sandbox.git
cd scorpius-contract-sandbox

# Install dependencies
npm install

# Setup environment
cp .env.example .env.development
# Edit .env.development with your configuration

# Initialize database
npm run setup

# Start development server
npm run dev
```

### Docker Quick Start

```bash
# Start all services with Docker Compose
npm run docker:run

# Or build and run custom image
npm run docker:build
docker run -p 3000:3000 scorpius-sandbox
```

The application will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

Create a `.env.development` file:

```env
# Application
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scorpius_sandbox
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-32-character-encryption-key

# Blockchain Networks
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
ARBITRUM_RPC_URL=https://arbitrum-mainnet.infura.io/v3/YOUR_PROJECT_ID

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Network Configuration

Configure blockchain networks in `config/networks/`:

```javascript
// config/networks/ethereum.json
{
  "name": "ethereum",
  "chainId": 1,
  "rpcUrl": "${ETHEREUM_RPC_URL}",
  "blockExplorer": "https://etherscan.io",
  "nativeCurrency": {
    "name": "Ether",
    "symbol": "ETH",
    "decimals": 18
  }
}
```

## 📚 API Documentation

### Authentication

```bash
# Login
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123",
    "username": "admin",
    "role": "admin"
  }
}
```

### Sandbox Management

```bash
# Create sandbox
curl -X POST http://localhost:3000/api/v1/sandbox \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Sandbox",
    "network": "ethereum",
    "forkFrom": "latest"
  }'

# Deploy contract
curl -X POST http://localhost:3000/api/v1/sandbox/SESSION_ID/contracts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "pragma solidity ^0.8.0; contract Test { ... }",
    "constructorArgs": []
  }'
```

### Exploit Simulation

```bash
# Run flash loan exploit
curl -X POST http://localhost:3000/api/v1/exploits/flash-loan \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "0x1234567890123456789012345678901234567890",
    "amount": "1000000000000000000000",
    "strategy": "arbitrage"
  }'
```

For complete API documentation, visit `/api/docs` when running the application.

## ��️ Architecture

### Enterprise-Grade Components

**Scorpius Contract Sandbox** is built with enterprise scalability and security in mind, integrating proven patterns from the Scorpius Enterprise ecosystem:

#### Core Engines
- **Simulation Engine**: Advanced exploit simulation with AI-assisted analysis
- **Vulnerability Analyzer**: Multi-approach security analysis (static, dynamic, AI-guided)
- **Contract Manager**: Enterprise contract compilation, deployment, and management
- **Sandbox Engine**: Isolated execution environment with resource management
- **Network Manager**: Multi-blockchain network abstraction and management

#### Security & Compliance
- **JWT-based Authentication**: Role-based access control with permissions
- **Rate Limiting**: Redis-backed distributed rate limiting
- **Input Validation**: Comprehensive request validation with express-validator
- **Security Headers**: Helmet.js security middleware
- **Audit Logging**: Comprehensive audit trail with Winston

#### Scalability Features
- **Microservices Ready**: Modular architecture for easy scaling
- **Event-Driven**: EventEmitter-based component communication
- **Resource Management**: Configurable resource limits and isolation
- **Caching**: Redis-based caching for performance optimization
- **Queue Management**: Bull queue integration for background processing

### Integration with Scorpius Enterprise

This Node.js implementation seamlessly integrates with the existing Scorpius Enterprise ecosystem:

- **Compatible Data Models**: Shared enums and structures with Python backend
- **Unified API Patterns**: Consistent response formats and error handling
- **Enterprise Configuration**: Environment-based configuration management
- **Monitoring Integration**: Prometheus metrics and health check endpoints
- **AI Analysis Compatibility**: Compatible with existing AI analysis pipelines

## 📊 Simulation Types

The platform supports multiple simulation approaches:

### 🎯 Proof of Concept
- Quick vulnerability validation
- Basic exploit feasibility testing
- Minimal resource usage

### 🚀 Full Exploit
- Complete attack simulation
- Real-world exploit scenarios
- Comprehensive impact assessment

### 📈 Impact Assessment
- Risk quantification analysis
- Business impact evaluation
- Compliance reporting

### 🔗 Attack Chain
- Multi-step attack scenarios
- Complex exploit combinations
- Advanced persistent threat simulation

### 🛡️ Mitigation Testing
- Security control validation
- Defense mechanism testing
- Remediation verification

### 🤖 AI-Guided Exploit
- Machine learning-assisted discovery
- Novel attack pattern identification
- Adaptive simulation strategies

## 🔍 Vulnerability Analysis

### Analysis Types

- **Static Analysis**: Code pattern matching and AST analysis
- **Dynamic Analysis**: Runtime behavior monitoring
- **Symbolic Execution**: Path exploration and constraint solving
- **Formal Verification**: Mathematical proof techniques
- **AI-Assisted**: Machine learning-powered vulnerability detection
- **Hybrid**: Combined approach for comprehensive coverage

### Security Patterns Detected

- **Reentrancy Vulnerabilities**: Cross-function and cross-contract reentrancy
- **Integer Overflow/Underflow**: Arithmetic operation vulnerabilities
- **Access Control Issues**: Authorization bypass and privilege escalation
- **Unsafe External Calls**: Unchecked external contract interactions
- **Timestamp Dependence**: Block timestamp manipulation vulnerabilities
- **Transaction Origin Usage**: tx.origin authentication issues
- **Unchecked Return Values**: Failed external call handling

## 🌐 API Endpoints

### Simulation Management
```
POST   /api/v1/simulations              # Create new simulation
GET    /api/v1/simulations/:id/status   # Get simulation status
POST   /api/v1/simulations/:id/abort    # Abort running simulation
GET    /api/v1/simulations/:id/report   # Get detailed report
GET    /api/v1/simulations/metrics      # Get system metrics
```

### Contract Analysis
```
POST   /api/v1/simulations/analyze      # Analyze contract vulnerabilities
POST   /api/v1/simulations/deploy       # Deploy contract for testing
```

### System Health
```
GET    /health                          # System health check
GET    /api/v1/simulations/health       # Service-specific health
```

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+**
- **PostgreSQL 13+** (optional, for persistent storage)
- **Redis 6+** (optional, for caching and rate limiting)
- **Docker & Docker Compose** (for full stack deployment)

### Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd scorpius-contract-sandbox
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Dependencies** (optional)
   ```bash
   docker-compose up -d postgres redis anvil
   ```

4. **Run the Application**
   ```bash
   npm start
   ```

### Development Mode

```bash
npm run dev        # Start with nodemon
npm run test       # Run test suite
npm run lint       # Check code style
npm run lint:fix   # Fix linting issues
```

## 🔧 Configuration

### Environment Variables

#### Core Application
```env
PORT=3000
NODE_ENV=development
```

#### Database Configuration
```env
DATABASE_URL=postgresql://localhost:5432/scorpius_sandbox
DATABASE_SSL=false
DATABASE_MAX_CONNECTIONS=20
```

#### Security Settings
```env
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=24h
BCRYPT_ROUNDS=12
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### Blockchain Configuration
```env
DEFAULT_NETWORK=localhost
ANVIL_RPC_URL=http://localhost:8545
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
GAS_LIMIT=8000000
```

#### Simulation Settings
```env
MAX_CONCURRENT_SIMULATIONS=5
SIMULATION_TIMEOUT=300000
ENABLE_AI_ANALYSIS=true
ENABLE_DYNAMIC_ANALYSIS=true
```

### Advanced Configuration

The application supports extensive configuration through environment variables and config files:

- **Network Management**: Multiple blockchain network support
- **Resource Limits**: Configurable memory, CPU, and disk limits
- **Security Policies**: Customizable security rules and patterns
- **Analysis Engines**: Configurable analysis parameters and thresholds
- **Monitoring**: Metrics collection and alerting configuration

## 🐳 Docker Deployment

### Production Stack

```bash
docker-compose -f docker-compose.prod.yml up -d
```

This starts:
- **Application Server** (Node.js)
- **PostgreSQL Database**
- **Redis Cache**
- **Anvil Blockchain Node**
- **Prometheus Monitoring**
- **Grafana Dashboard**

### Development Stack

```bash
docker-compose up -d
```

Includes additional development tools:
- **Hot Reload** enabled
- **Debug Ports** exposed
- **Development Dependencies** included

## 📈 Monitoring & Observability

### Health Checks
- **Application Health**: `/health`
- **Service Health**: `/api/v1/simulations/health`
- **Component Status**: Individual service health reporting

### Metrics Collection
- **Prometheus Integration**: Automated metrics collection
- **Custom Metrics**: Business-specific KPIs
- **Performance Monitoring**: Response times and throughput

### Logging
- **Structured Logging**: JSON-formatted logs with Winston
- **Log Rotation**: Daily log rotation with compression
- **Audit Trails**: Security and compliance logging

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Role-Based Access**: Granular permission system
- **Session Management**: Secure session handling

### API Security
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: Comprehensive request validation
- **Security Headers**: OWASP-recommended security headers
- **CORS Configuration**: Flexible cross-origin policies

### Sandbox Security
- **Network Isolation**: Isolated blockchain networks
- **Resource Limits**: Configurable execution limits
- **Safe Code Execution**: Sandboxed smart contract execution
- **Audit Logging**: Complete action audit trails

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `npm test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards

- Follow ESLint configuration
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenZeppelin](https://openzeppelin.com/) for smart contract security standards
- [Hardhat](https://hardhat.org/) for development framework
- [Foundry](https://getfoundry.sh/) for testing tools
- The blockchain security community for continuous innovation

## 📞 Support

- **Documentation**: [docs.scorpius.io](https://docs.scorpius.io)
- **Community**: [Discord](https://discord.gg/scorpius)
- **Issues**: [GitHub Issues](https://github.com/scorpius-security/contract-sandbox/issues)
- **Email**: support@scorpius.io

---

**Made with ❤️ by the Scorpius Security Team** 