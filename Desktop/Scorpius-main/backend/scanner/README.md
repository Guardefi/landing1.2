# 🦂 Scorpius Vulnerability Scanner Enterprise

![Scorpius Logo](https://img.shields.io/badge/Scorpius-Enterprise-red?style=for-the-badge&logo=security&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

An enterprise-grade smart contract vulnerability scanner with advanced simulation capabilities, Docker-based plugin architecture, and comprehensive exploit testing framework.

## 🚀 Quick Start

### Easy Startup (Recommended)

**Windows (PowerShell):**
```powershell
# Start all services (backend + all plugins)
.\start-scorpius.ps1

# Stop all services
.\stop-scorpius.ps1
```

**Linux/Mac (Bash):**
```bash
# Make scripts executable (first time only)
chmod +x start-scorpius.sh stop-scorpius.sh

# Start all services (backend + all plugins)
./start-scorpius.sh

# Stop all services
./stop-scorpius.sh
```

### Manual Docker Compose
```bash
# Start all services
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View status
docker-compose ps
```

### Service Endpoints

Once started, the following services will be available:

- **Main Scanner API**: http://localhost:8090
- **Slither Plugin**: http://localhost:8091  
- **Mythril Plugin**: http://localhost:8092
- **Manticore Plugin**: http://localhost:8093
- **MythX Plugin**: http://localhost:8094
- **PostgreSQL Database**: localhost:5433
- **Redis Cache**: localhost:6380

## 🚀 Features

### Core Scanning Capabilities
- **Multi-Plugin Architecture**: Slither, Mythril, Manticore, MythX, and more
- **Static & Dynamic Analysis**: Comprehensive vulnerability detection
- **Symbolic Execution**: Advanced code path exploration
- **Real-time Scanning**: Asynchronous scanning with live progress updates

### Enterprise Simulation Engine
- **Exploit Simulation**: Test vulnerabilities in controlled environments
- **Attack Chain Analysis**: Multi-step attack scenario testing
- **Impact Assessment**: Quantify potential damage from vulnerabilities
- **Proof-of-Concept Generation**: Automatic exploit code generation

### Docker-Based Infrastructure
- **Isolated Plugin Execution**: Each scanner runs in dedicated containers
- **Simulation Environments**: Ethereum and DeFi testing sandboxes
- **Scalable Architecture**: Horizontal scaling with container orchestration
- **Security Hardened**: Network isolation and resource limits

### API & Integration
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Authentication & Authorization**: JWT-based security
- **Webhook Support**: Real-time notifications and integrations
- **Metrics & Monitoring**: Prometheus, Grafana, and ELK stack integration

## 📋 Requirements

### System Requirements
- **OS**: Linux (Ubuntu 20.04+) or macOS (10.15+)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 20GB free space minimum
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Supported Languages
- Solidity (0.6.x - 0.8.x)
- Vyper (experimental)
- Yul (experimental)

## 🏗️ Quick Start

### Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/scorpius-vulnerability-scanner.git
cd scorpius-vulnerability-scanner

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Install Dependencies**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r config/config/requirements-dev.txt
```

2. **Configure Environment**
```bash
# Copy and edit configuration
cp .env.example .env
nano .env
```

3. **Build and Start Services**
```bash
# Build Docker images
docker-compose build

# Start core services
docker-compose up -d

# Initialize plugins
docker-compose --profile plugins up -d

# Start simulation environment
docker-compose --profile simulation up -d
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Core Configuration
SCORPIUS_ENV=production
SCORPIUS_API_KEY=your-secure-api-key
SCORPIUS_SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://scorpius:password@localhost:5432/scorpius

# External Services
MYTHX_API_KEY=your-mythx-api-key
MAINNET_FORK_URL=https://mainnet.infura.io/v3/your-infura-key
```

### Plugin Configuration

Each plugin can be configured in `config/plugins.yaml`:

```yaml
slither:
  enabled: true
  timeout: 300
  memory_limit: "1g"
  
mythril:
  enabled: true
  timeout: 600
  memory_limit: "2g"
  
manticore:
  enabled: true
  timeout: 900
  memory_limit: "4g"
```

## 📖 Usage

### API Usage

#### Start a Scan
```bash
curl -X POST "http://localhost:8080/api/v1/scan" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "file",
    "target_identifier": "/path/to/contract.sol",
    "scan_type": "full",
    "plugins": ["slither", "mythril"]
  }'
```

#### Check Scan Status
```bash
curl -X GET "http://localhost:8080/api/v1/scan/{scan_id}/status" \
  -H "Authorization: Bearer your-api-token"
```

#### Get Scan Results
```bash
curl -X GET "http://localhost:8080/api/v1/scan/{scan_id}/results" \
  -H "Authorization: Bearer your-api-token"
```

#### Start Exploit Simulation
```bash
curl -X POST "http://localhost:8080/api/v1/simulation" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  -d '{
    "vulnerability_id": "vuln_123",
    "simulation_type": "poc",
    "target_identifier": "contract_code_here"
  }'
```

### Command Line Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run a basic scan
python scorpius.py scan --file contract.sol --type full

# Run with specific plugins
python scorpius.py scan --file contract.sol --plugins slither,mythril

# Generate HTML report
python scorpius.py scan --file contract.sol --output-format html

# Run exploit simulation
python scorpius.py simulate --vulnerability-id vuln_123 --type poc
```

## 🐳 Docker Architecture

### Service Overview

```mermaid
graph TB
    A[Scorpius API] --> B[PostgreSQL]
    A --> C[Redis]
    A --> D[Plugin Manager]
    
    D --> E[Slither Container]
    D --> F[Mythril Container]
    D --> G[Manticore Container]
    D --> H[MythX Container]
    
    A --> I[Simulation Engine]
    I --> J[Ethereum Sim]
    I --> K[DeFi Sim]
    
    L[Monitoring Stack] --> M[Prometheus]
    L --> N[Grafana]
    L --> O[ELK Stack]
```

### Available Profiles

- **Core**: Basic scanning functionality
- **Plugins**: All vulnerability scanning plugins
- **Simulation**: Exploit simulation environments
- **Monitoring**: Metrics and logging infrastructure
- **Storage**: Distributed storage (IPFS, MinIO)

### Docker Commands

```bash
# Start specific profiles
docker-compose --profile plugins up -d
docker-compose --profile simulation up -d
docker-compose --profile monitoring up -d

# Scale services
docker-compose up -d --scale scorpius-main=3

# View logs
docker-compose logs -f scorpius-main

# Health checks
docker-compose ps
```

## 🔒 Security Features

### Sandbox Isolation
- **Network Isolation**: Plugins run in isolated networks
- **Resource Limits**: CPU and memory constraints
- **Read-only Filesystems**: Immutable container environments
- **Capability Dropping**: Minimal container privileges

### API Security
- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Cross-origin request control

### Simulation Security
- **Isolated Blockchain**: Sandboxed Ethereum environments
- **Controlled Execution**: Limited gas and time bounds
- **Result Quarantine**: Isolated exploit artifacts
- **Audit Logging**: Comprehensive simulation logs

## 📊 Monitoring & Metrics

### Available Dashboards
- **Grafana**: Real-time metrics visualization
- **Kibana**: Log analysis and search
- **Prometheus**: Metrics collection and alerting

### Key Metrics
- Scan completion rates
- Plugin performance statistics
- Simulation success rates
- Resource utilization
- Error rates and types

### Accessing Dashboards
- Grafana: http://localhost:3000 (admin/admin)
- Kibana: http://localhost:5601
- Prometheus: http://localhost:9090

## 🧪 Simulation Engine

### Simulation Types

1. **Proof of Concept (PoC)**
   - Quick vulnerability verification
   - Basic exploit demonstration
   - Low resource usage

2. **Full Exploit**
   - Complete attack implementation
   - Damage quantification
   - Success probability analysis

3. **Impact Assessment**
   - Financial impact calculation
   - Affected user analysis
   - Mitigation cost estimation

4. **Attack Chain**
   - Multi-step attack scenarios
   - Dependency analysis
   - Timeline reconstruction

### Simulation Results

Each simulation provides:
- Exploit success probability
- Extracted funds calculation
- Gas usage analysis
- Execution trace
- Mitigation recommendations

## 🔌 Plugin Development

### Creating Custom Plugins

1. **Plugin Structure**
```python
from scanners.base import BaseScannerPlugin

class MyPlugin(BaseScannerPlugin):
    NAME = "my_plugin"
    DESCRIPTION = "Custom vulnerability scanner"
    VERSION = "1.0.0"
    
    async def scan(self, target, config):
        # Implementation here
        pass
```

2. **Docker Integration**
```dockerfile
FROM python:3.11-slim
# Install your scanner
RUN pip install my-scanner
# Configure environment
```

3. **Registration**
```python
# Register in plugin manager
plugin_manager.register_plugin("my_plugin", MyPlugin)
```

## 📈 Performance Optimization

### Scaling Strategies
- **Horizontal Scaling**: Multiple API instances
- **Plugin Parallelization**: Concurrent plugin execution
- **Caching**: Redis-based result caching
- **Database Optimization**: Indexed queries and connection pooling

### Resource Management
- **Memory Limits**: Per-plugin memory constraints
- **CPU Quotas**: Fair CPU allocation
- **Disk Quotas**: Storage usage limits
- **Network Throttling**: Bandwidth management

## 🛠️ Troubleshooting

### Common Issues

1. **Docker Permission Denied**
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

2. **Plugin Container Fails**
```bash
# Check logs
docker-compose logs slither

# Rebuild image
docker-compose build slither
```

3. **API Connection Refused**
```bash
# Check service status
docker-compose ps

# Restart services
docker-compose restart scorpius-main
```

4. **Database Connection Error**
```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down
docker volume rm scorpius_postgres_data
docker-compose up -d postgres
```

### Debug Mode

Enable debug logging in `.env`:
```bash
SCORPIUS_LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# API health
curl http://localhost:8080/health

# Database health
docker-compose exec postgres pg_isready

# Plugin health
curl http://localhost:8080/api/v1/plugins
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/scorpius-vulnerability-scanner.git

# Install development dependencies
pip install -r config/requirements-dev.txt

# Run tests
pytest

# Format code
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Slither](https://github.com/crytic/slither) - Static analysis framework
- [Mythril](https://github.com/ConsenSys/mythril) - Security analysis tool
- [Manticore](https://github.com/trailofbits/manticore) - Symbolic execution tool
- [MythX](https://mythx.io/) - Professional security analysis service

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/scorpius-vulnerability-scanner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/scorpius-vulnerability-scanner/discussions)
- **Email**: support@scorpius-scanner.com

---

Made with ❤️ by the Scorpius Security Team
