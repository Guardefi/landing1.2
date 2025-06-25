# 🔥 Scorpius Enterprise Vulnerability Scanner

<div align="center">

![Scorpius Logo](https://img.shields.io/badge/Scorpius-Enterprise-red?style=for-the-badge&logo=security&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-Enterprise-green?style=for-the-badge)

**Enterprise-grade smart contract vulnerability scanner with AI-powered analysis and containerized plugin architecture**

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🔧 Configuration](#configuration) • [🐳 Docker](#docker-deployment)

</div>

---

## 🌟 Features

### 🔍 Advanced Security Analysis
- **Multi-Engine Detection**: Slither, Mythril, Manticore, MythX integration
- **AI-Powered Analysis**: Claude AI integration for advanced pattern recognition
- **Custom Strategies**: Reentrancy, flash loan, access control, arithmetic overflow detection
- **Simulation Testing**: Hardhat-based exploit simulation and testing

### 🏗️ Enterprise Architecture
- **Containerized Plugins**: Isolated Docker containers prevent dependency conflicts
- **Parallel Processing**: Multi-threaded analysis for faster results
- **Scalable Design**: Microservices architecture with Redis and PostgreSQL
- **RESTful API**: Full API access with OpenAPI/Swagger documentation

### 📊 Monitoring & Analytics
- **Real-time Dashboards**: Grafana integration for vulnerability metrics
- **Log Management**: ELK stack for centralized logging
- **Performance Monitoring**: Prometheus metrics and alerting
- **Report Generation**: Comprehensive HTML and PDF reports

### 🛡️ Security & Compliance
- **Role-based Access**: Enterprise authentication and authorization
- **Audit Trails**: Complete activity logging and compliance reporting
- **Data Encryption**: Encrypted storage and transmission
- **Secure Deployment**: Production-ready security configurations

---

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (Latest version)
- **Docker Compose** v2.0+
- **PowerShell** 7.0+ (Windows) or **Bash** (Linux/macOS)
- **Git** for repository management

### 1. Clone Repository
```bash
git clone https://github.com/your-org/scorpius-vulnerability-scanner.git
cd scorpius-vulnerability-scanner
```

### 2. Enterprise Deployment
```powershell
# Full enterprise deployment with all features
./deploy-enterprise.ps1 -CleanInstall -DeploymentProfile full

# Minimal deployment (core services only)
./deploy-enterprise.ps1 -DeploymentProfile minimal

# With security plugins only
./deploy-enterprise.ps1 -DeploymentProfile plugins
```

### 3. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# View service logs
docker-compose logs -f scorpius-main

# Test the API
curl http://localhost:8080/health
```

---

## 📊 Service Architecture

```mermaid
graph TB
    subgraph "🌐 Frontend Layer"
        WEB[Web Interface]
        API[REST API]
        DOCS[API Documentation]
    end
    
    subgraph "🔧 Core Services"
        MAIN[Scorpius Main]
        DB[(PostgreSQL)]
        CACHE[(Redis)]
    end
    
    subgraph "🔍 Security Plugins"
        SLITHER[Slither Container]
        MYTHRIL[Mythril Container]
        MANTICORE[Manticore Container]
        MYTHX[MythX Container]
    end
    
    subgraph "📊 Monitoring Stack"
        GRAFANA[Grafana]
        ELASTIC[Elasticsearch]
        KIBANA[Kibana]
        PROMETHEUS[Prometheus]
    end
    
    subgraph "🧪 Simulation"
        HARDHAT[Hardhat Engine]
        ANVIL[Anvil Fork]
    end
    
    WEB --> API
    API --> MAIN
    MAIN --> DB
    MAIN --> CACHE
    MAIN --> SLITHER
    MAIN --> MYTHRIL
    MAIN --> MANTICORE
    MAIN --> MYTHX
    MAIN --> HARDHAT
    MAIN --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    MAIN --> ELASTIC
    ELASTIC --> KIBANA
```

---

## 🌐 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| 🚀 **Main API** | http://localhost:8080 | Core vulnerability scanning API |
| 📚 **API Docs** | http://localhost:8080/docs | Interactive API documentation |
| 📊 **Grafana** | http://localhost:3000 | Metrics and dashboards |
| 🔍 **Kibana** | http://localhost:5601 | Log analysis and search |
| 💾 **PostgreSQL** | localhost:5432 | Database (internal) |
| 🚀 **Redis** | localhost:6379 | Cache and message queue |

---

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
SCORPIUS_ENV=production
POSTGRES_DB=scorpius
POSTGRES_USER=scorpius
POSTGRES_PASSWORD=your_secure_password

# API Keys (Optional)
ANTHROPIC_API_KEY=your_claude_api_key
MYTHX_API_KEY=your_mythx_api_key
MAINNET_FORK_URL=your_ethereum_rpc_url

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

### Deployment Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| **minimal** | Core API, DB, Cache | Development, testing |
| **plugins** | + Security scanners | Production scanning |
| **monitoring** | + Grafana, ELK stack | Enterprise monitoring |
| **simulation** | + Hardhat, Anvil | Advanced testing |
| **full** | All services | Complete enterprise setup |

---

## 🐳 Docker Deployment

### Container Architecture
- **scorpius-main**: Core application and API
- **scorpius/slither**: Static analysis container
- **scorpius/mythril**: Symbolic execution container
- **scorpius/manticore**: Dynamic analysis container
- **scorpius/mythx**: Professional analysis container

### Build Custom Images
```bash
# Build main application
docker build -t scorpius-enterprise -f docker/scorpius/Dockerfile .

# Build security plugins
docker build -t scorpius/slither docker/slither/
docker build -t scorpius/mythril docker/mythril/
docker build -t scorpius/manticore docker/manticore/
```

### Volume Management
```bash
# Persistent data volumes
./contracts/     # Smart contract sources
./reports/       # Scan reports and results
./logs/          # Application logs
./data/          # Database and cache data
```

---

## 🧪 Testing & Validation

### Run Integration Tests
```bash
# Test enhanced vulnerability detection
python tests/integration/test_enhanced_scanner.py

# Test Docker plugin system
python test_docker_plugins.py

# Test individual strategies
pytest tests/ -v --tb=short
```

### Plugin System Validation
```bash
# Test individual plugins
docker run --rm -v $(pwd)/contracts:/workspace/contracts scorpius/slither
docker run --rm -v $(pwd)/contracts:/workspace/contracts scorpius/mythril
docker run --rm -v $(pwd)/contracts:/workspace/contracts scorpius/manticore
```

---

## 📈 Monitoring & Observability

### Grafana Dashboards
- **Vulnerability Metrics**: Real-time scanning statistics
- **System Performance**: Container resource usage
- **Security Trends**: Historical vulnerability data
- **API Analytics**: Request/response metrics

### Log Analysis (Kibana)
- **Structured Logging**: JSON-formatted application logs
- **Error Tracking**: Centralized error monitoring
- **Audit Trails**: Security event logging
- **Performance Metrics**: Response time analysis

### Alerting (Prometheus)
- **Critical Vulnerabilities**: High-severity findings
- **System Health**: Service availability monitoring
- **Resource Usage**: Memory/CPU threshold alerts
- **API Errors**: Failed request notifications

---

## 🔐 Security Features

### Authentication & Authorization
- JWT-based API authentication
- Role-based access control (RBAC)
- API key management
- Session management with Redis

### Data Protection
- Encryption at rest (database)
- TLS/SSL for data in transit
- Secure environment variable handling
- Container security best practices

### Compliance & Auditing
- Complete audit trail logging
- GDPR compliance features
- SOC 2 compliance preparation
- Regular security assessments

---

## 🛠️ Management Commands

```bash
# Deployment Management
./deploy-enterprise.ps1 -CleanInstall          # Fresh installation
./deploy-enterprise.ps1 -SkipBuild            # Skip image building
./deploy-enterprise.ps1 -DeploymentProfile minimal  # Minimal deployment

# Container Management
docker-compose up -d                    # Start all services
docker-compose down                     # Stop all services
docker-compose restart                  # Restart services
docker-compose logs -f                  # Follow logs

# Database Management
docker-compose exec postgres psql -U scorpius scorpius  # Access database
docker-compose exec redis redis-cli                     # Access cache

# Monitoring
docker-compose exec scorpius-main python -m api.health  # Health check
docker stats                                            # Resource usage
```

---

## 🆘 Troubleshooting

### Common Issues

#### Container Build Failures
```bash
# Clear Docker cache and rebuild
docker system prune -a
./deploy-enterprise.ps1 -CleanInstall
```

#### Port Conflicts
```bash
# Check for port conflicts
netstat -an | findstr :8080
# Kill conflicting processes or change ports in docker-compose.yml
```

#### Plugin Execution Issues
```bash
# Test individual plugin containers
docker run --rm scorpius/slither slither --version
docker run --rm scorpius/mythril myth version
```

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec scorpius-main python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://scorpius:password@postgres:5432/scorpius')
print('Database connection:', engine.execute('SELECT 1').scalar())
"
```

### Performance Optimization

#### Memory Usage
- Increase Docker Desktop memory allocation (8GB+ recommended)
- Adjust container memory limits in docker-compose.yml
- Monitor with `docker stats` command

#### Scanning Performance
- Enable parallel processing: `PARALLEL_EXECUTION=true`
- Adjust worker thread counts: `MAX_WORKERS=4`
- Use SSD storage for contract files

---

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Scan Contract
```http
POST /api/v1/scan
Content-Type: application/json

{
  "contract_address": "0x...",
  "source_code": "pragma solidity ^0.8.0; contract Test { ... }",
  "strategies": ["reentrancy", "access_control"]
}
```

#### Get Scan Results
```http
GET /api/v1/scans/{scan_id}
```

#### List Vulnerabilities
```http
GET /api/v1/vulnerabilities?severity=high&limit=10
```

### WebSocket Events
```javascript
// Real-time scan progress
const ws = new WebSocket('ws://localhost:8080/ws/scan/{scan_id}');
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Scan progress:', update.progress);
};
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/scorpius-vulnerability-scanner.git
cd scorpius-vulnerability-scanner

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Code formatting
black . && isort .

# Linting
flake8 . && mypy .
```

---

## 📄 License

This project is licensed under the Enterprise License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- 📧 **Email**: support@scorpius-security.com
- 💬 **Discord**: [Scorpius Community](https://discord.gg/scorpius)
- 📚 **Documentation**: [docs.scorpius-security.com](https://docs.scorpius-security.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/scorpius-vulnerability-scanner/issues)

---

<div align="center">

**Built with ❤️ by the Scorpius Security Team**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)

</div>
