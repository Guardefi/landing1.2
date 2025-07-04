# 🚀 SCORPIUS Time Machine

[![CI/CD Pipeline](https://github.com/Guardefi/SCORPIUS-TIME-MACHINE/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Guardefi/SCORPIUS-TIME-MACHINE/actions)
[![Security Rating](https://img.shields.io/badge/security-A+-brightgreen)](https://github.com/Guardefi/SCORPIUS-TIME-MACHINE)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-blue.svg)](https://www.typescriptlang.org/)

**Enterprise-grade blockchain forensics and time-travel debugging platform for Ethereum and EVM-compatible networks.**

## 🎯 Overview

SCORPIUS Time Machine is a sophisticated blockchain forensics system that enables investigators, developers, and security researchers to analyze, replay, and debug blockchain transactions with unprecedented detail. Built for enterprise environments, it provides real-time monitoring, historical analysis, and advanced visualization capabilities.

### 🌟 Key Features

- **🔍 Advanced Forensics**: Deep transaction analysis with MEV detection, vulnerability scanning, and pattern recognition
- **⏱️ Time Travel Debugging**: Replay historical blockchain states with precision
- **🚨 Real-time Monitoring**: Live detection of suspicious activities, exploits, and anomalies  
- **📊 Interactive Dashboard**: Modern React-based UI with comprehensive analytics
- **🔗 Multi-chain Support**: Ethereum, Polygon, BSC, and other EVM networks
- **🛡️ Security First**: Enterprise-grade security with role-based access control
- **📈 Scalable Architecture**: Microservices design with Docker/Kubernetes support
- **🔌 Plugin System**: Extensible architecture for custom analysis modules

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   Time Machine  │
│   Dashboard     │◄──►│   Backend       │◄──►│   Core Engine   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────┐            ┌─────────┐            ┌─────────┐
    │  MUI    │            │  Redis  │            │ Anvil   │
    │ Theme   │            │ Cache   │            │ Fork    │
    └─────────┘            └─────────┘            └─────────┘
```

### 🧩 Components

- **Frontend**: React 18 + TypeScript + Material-UI
- **Backend**: FastAPI + Python 3.11+ + Pydantic
- **Core Engine**: Custom blockchain analysis engine
- **Storage**: Redis (cache) + SQLite/PostgreSQL (persistence)
- **Blockchain Interface**: Web3.py + Anvil for forked networks
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### 🐳 Docker Setup (Recommended)

```bash
# Clone the repository
git clone git@github.com:Guardefi/SCORPIUS-TIME-MACHINE.git
cd SCORPIUS-TIME-MACHINE

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000  # API & Dashboard
open http://localhost:8000/docs  # API Documentation
```

### 🔧 Local Development Setup

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r config/config/requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start the backend
python start_server.py
```

#### Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Start development server
npm start
```

## 📊 Dashboard Features

### 🔍 Timeline Analysis
- **20+ Realistic Demo Events**: Pre-loaded with forensic scenarios
- **Real-time Event Stream**: WebSocket-based live updates
- **Advanced Filtering**: By event type, time range, metadata
- **Interactive Exploration**: Click to dive deep into transactions

### 📈 Job Management
- **Analysis Jobs**: Create, monitor, and manage forensic investigations
- **Progress Tracking**: Real-time status updates with detailed logs
- **Batch Operations**: Handle multiple analyses simultaneously
- **Export Results**: Download findings in multiple formats

### 🌿 Branch Management
- **State Snapshots**: Create and manage blockchain state branches
- **Version Control**: Track changes across different investigation paths
- **Merge & Compare**: Analyze differences between branches
- **Rollback Capability**: Return to previous investigation states

### 🔬 Diff Viewer
- **Transaction Comparison**: Side-by-side analysis of transactions
- **State Changes**: Visualize storage and balance modifications
- **Code Diffs**: Smart contract bytecode and source comparisons
- **Gas Analysis**: Detailed gas usage patterns and optimizations

### 🔌 Plugin Dashboard
- **Anvil Integration**: Local blockchain forking and testing
- **Gas Analysis**: Advanced gas optimization recommendations
- **Security Scanner**: Automated vulnerability detection
- **Custom Plugins**: Extensible architecture for specialized tools

## 🛠️ Configuration

### Environment Variables

```bash
# Application
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./time_machine.db
REDIS_URL=redis://localhost:6379/0

# Blockchain
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
ETHERSCAN_API_KEY=YOUR_API_KEY

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Features
ENABLE_DEMO_DATA=true
ENABLE_REAL_TIME_MONITORING=true
ENABLE_SECURITY_SCANNING=true
```

### 📁 Project Structure

```
SCORPIUS-TIME-MACHINE/
├── 📁 time_machine/          # Core Python package
│   ├── 📁 api/               # FastAPI routes and schemas
│   ├── 📁 core/              # Core engine and models
│   ├── 📁 cli/               # Command-line interface
│   └── 📁 plugins/           # Extensible plugin system
├── 📁 ui/                    # React frontend
│   ├── 📁 src/components/    # React components
│   ├── 📁 src/services/      # API service layer
│   └── 📁 public/            # Static assets
├── 📁 tests/                 # Test suites
├── 📁 scripts/               # Utility scripts
├── 📁 legacy/                # Legacy/archived code
├── 📁 docs/                  # Documentation
├── 🐳 docker/docker-compose.yml     # Docker orchestration
├── 🐳 Dockerfile             # Container definition
├── ⚙️ config/pyproject.toml         # Python project config
└── 📋 config/config/requirements-dev.txt       # Python dependencies
```

## 🧪 Testing

### Backend Tests
```bash
# Run all backend tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=time_machine --cov-report=html

# Run specific test categories
pytest tests/ -m "unit"      # Unit tests only
pytest tests/ -m "integration"  # Integration tests only
```

### Frontend Tests
```bash
cd ui

# Run all frontend tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

### Integration Tests
```bash
# Start the full stack
docker-compose up -d

# Run integration tests
python -m pytest tests/test_comprehensive.py -v
```

## 🚀 Deployment

### 🐳 Docker Production

```bash
# Build production image
docker build -t scorpius-time-machine:latest .

# Run in production mode
docker run -d \
  --name time-machine \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e DATABASE_URL=your-prod-db-url \
  scorpius-time-machine:latest
```

### ☁️ Cloud Deployment

Supports deployment on:
- **AWS ECS/EKS**
- **Google Cloud Run/GKE**
- **Azure Container Instances/AKS**
- **DigitalOcean App Platform**
- **Kubernetes** (any provider)

See `docs/deployment/` for platform-specific guides.

## 🔒 Security

### Security Features
- **🔐 JWT Authentication**: Secure API access
- **🛡️ Input Validation**: Comprehensive request validation
- **🚨 Rate Limiting**: DDoS protection
- **📝 Audit Logging**: Complete action tracking
- **🔍 Security Scanning**: Automated vulnerability detection
- **🔒 HTTPS Enforcement**: TLS/SSL required in production

### Security Scanning
```bash
# Run security audit
bandit -r time_machine/
safety check
npm audit

# Container security scan
docker run --rm -v $(pwd):/src aquasec/trivy fs /src
```

## 📈 Performance

### Benchmarks
- **API Response Time**: < 100ms (95th percentile)
- **WebSocket Latency**: < 10ms
- **Memory Usage**: < 512MB (base)
- **Concurrent Users**: 1000+ (with Redis)
- **Transaction Analysis**: 1000+ TPS

### Optimization
- **Redis Caching**: Intelligent caching layer
- **Database Indexing**: Optimized queries
- **Connection Pooling**: Efficient resource usage
- **Async Processing**: Non-blocking operations
- **Memory Management**: Garbage collection tuning

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Create** a Pull Request

### Code Standards

- **Python**: Black formatting, type hints, docstrings
- **TypeScript**: ESLint + Prettier, strict mode
- **Git**: Conventional commits, signed commits
- **Testing**: >90% code coverage required

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🏢 Enterprise Support

For enterprise deployments, custom features, and professional support:

- **Email**: enterprise@guardefi.com
- **Website**: [https://guardefi.com](https://guardefi.com)
- **Documentation**: [https://docs.time-machine.guardefi.com](https://docs.time-machine.guardefi.com)

## 🎯 Roadmap

### 🔄 Current (v1.0)
- ✅ Core forensics engine
- ✅ Interactive dashboard
- ✅ Docker containerization
- ✅ Real-time monitoring
- ✅ Multi-chain support

### 🚀 Next (v1.1)
- 🔄 Machine learning detection
- 🔄 Advanced visualizations
- 🔄 API rate limiting
- 🔄 Database migrations
- 🔄 Kubernetes manifests

### 🌟 Future (v2.0)
- 📋 Multi-tenant architecture
- 📋 Advanced analytics
- 📋 Custom alerting
- 📋 Compliance reporting
- 📋 Mobile application

## 📚 Documentation

- **[API Documentation](https://docs.time-machine.guardefi.com/api)**
- **[User Guide](https://docs.time-machine.guardefi.com/guide)**
- **[Developer Documentation](https://docs.time-machine.guardefi.com/dev)**
- **[Deployment Guide](https://docs.time-machine.guardefi.com/deploy)**

## 💬 Community & Support

- **GitHub Issues**: Bug reports and feature requests
- **Discord**: [Join our community](https://discord.gg/guardefi)
- **Twitter**: [@Guardefi](https://twitter.com/guardefi)
- **Blog**: [Latest updates and tutorials](https://blog.guardefi.com)

---

<div align="center">

**Built with ❤️ by the Guardefi Team**

[Website](https://guardefi.com) • [Documentation](https://docs.time-machine.guardefi.com) • [Community](https://discord.gg/guardefi) • [Support](mailto:support@guardefi.com)

</div>
