# 🛡️ Scorpius Enterprise Platform

**Enterprise-grade cybersecurity platform for blockchain security, smart contract analysis, and threat detection.**

[![Build Status](https://github.com/scorpius/enterprise-platform/workflows/CI/badge.svg)](https://github.com/scorpius/enterprise-platform/actions)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=scorpius_enterprise&metric=security_rating)](https://sonarcloud.io/dashboard?id=scorpius_enterprise)
[![Coverage](https://codecov.io/gh/scorpius/enterprise-platform/branch/main/graph/badge.svg)](https://codecov.io/gh/scorpius/enterprise-platform)
[![License](https://img.shields.io/badge/license-Enterprise-blue.svg)](LICENSE)

## 🚀 Quick Start

```bash
# Development Environment
git clone https://github.com/scorpius/enterprise-platform.git
cd enterprise-platform
cp .env.example .env
docker-compose -f docker/docker/docker-compose.dev.yml up

# Production Deployment  
docker-compose -f docker/docker-compose.prod.yml up -d
```

**🌐 Access Points:**
- **API Gateway**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000  
- **Monitoring**: http://localhost:3001
- **Documentation**: http://localhost:8080

## 📋 Overview

Scorpius is a comprehensive enterprise cybersecurity platform specializing in:

- **🔍 Smart Contract Security**: Advanced vulnerability scanning and analysis
- **⚡ MEV Protection**: Frontrunning detection and mitigation
- **🕸️ Cross-Chain Security**: Multi-blockchain threat monitoring
- **🤖 AI-Powered Analysis**: Machine learning threat detection
- **📊 Real-time Monitoring**: Live security dashboards and alerting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│  API Gateway     │────│ Microservices   │
│   (React)       │    │  (FastAPI)       │    │ (Python)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Orchestrator    │────│   Databases     │
                       │  (Core Engine)   │    │ (PostgreSQL)    │
                       └──────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

**Backend:** Python 3.11, FastAPI, SQLAlchemy, Celery, Redis  
**Frontend:** React 18, TypeScript, Tailwind CSS, Vite  
**Infrastructure:** Docker, Kubernetes, Terraform, AWS  
**Monitoring:** Prometheus, Grafana, OpenTelemetry  
**Security:** JWT, OAuth2, Vault, Cosign, SAST/DAST

## 📁 Project Structure

```
enterprise-platform/
├── 📂 services/           # Microservices
│   ├── api-gateway/       # Central API gateway
│   ├── bridge-service/    # Cross-chain bridge
│   └── frontend/          # React frontend
├── 📂 packages/           # Shared libraries
│   └── core/             # Core orchestrator
├── 📂 backend/           # Specialized services
│   ├── mev_bot/          # MEV protection
│   ├── scanner/          # Vulnerability scanner
│   └── quantum/          # Quantum security
├── 📂 infrastructure/    # IaC and deployment
├── 📂 monitoring/        # Observability stack
├── 📂 docs/             # Documentation
├── 📂 docker/           # Container configs
└── 📂 config/           # Configuration files
```

## 🚦 Getting Started

### Prerequisites

- **Docker & Docker Compose** (v20.10+)
- **Node.js** (v20+) - for frontend development
- **Python** (3.11+) - for backend development
- **Git** (v2.30+)

### 1. Development Setup

```bash
# Clone repository
git clone https://github.com/scorpius/enterprise-platform.git
cd enterprise-platform

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Start development environment
docker-compose -f docker/docker/docker-compose.dev.yml up --build

# Verify services
curl http://localhost:8000/healthz
curl http://localhost:3000
```

### 2. Production Deployment

```bash
# Production environment
cp config/.env.secure .env.production
# Configure production secrets

# Deploy with scaling
docker-compose -f docker/docker-compose.prod.yml up -d
docker-compose -f docker/docker-compose.prod.yml scale api-gateway=3

# Verify deployment
curl http://localhost:8000/healthz
docker-compose logs -f api-gateway
```

### 3. Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f infrastructure/k8s/

# Verify deployment
kubectl get pods -n scorpius
kubectl port-forward svc/api-gateway 8000:8000
```

## 🔧 Development

### Local Development

```bash
# Backend development
cd packages/core
poetry install
poetry run python -m uvicorn main:app --reload

# Frontend development  
cd services/frontend
npm install
npm run dev

# Testing
make test              # Run all tests
make test-backend      # Backend tests only
make test-frontend     # Frontend tests only
make test-integration  # Integration tests
```

### Code Quality

```bash
make lint              # Run linting
make format            # Format code
make security-scan     # Security analysis
make type-check        # Type checking
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Service health
curl http://localhost:8000/healthz    # Liveness probe
curl http://localhost:8000/readyz     # Readiness probe
curl http://localhost:8000/health     # Detailed health

# Metrics
curl http://localhost:8000/metrics    # Prometheus metrics
```

### Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger Tracing**: http://localhost:16686

## 🔐 Security

### Enterprise Security Features

- **🔐 Authentication**: JWT-based with refresh tokens
- **🛡️ Authorization**: Role-based access control (RBAC)  
- **🔒 Encryption**: TLS 1.3, AES-256, secret management
- **🚫 Input Validation**: Comprehensive input sanitization
- **📊 Audit Logging**: Complete audit trail
- **🔍 Vulnerability Scanning**: Automated security scanning

### Security Scanning

```bash
# Run security scans
make security-scan     # SAST analysis
make container-scan    # Container vulnerability scan
make dependency-scan   # Dependency vulnerability check
```

## 📚 Documentation

- **📖 [API Documentation](docs/API.md)** - Complete API reference
- **🏗️ [Architecture Guide](docs/ARCHITECTURE.md)** - System architecture
- **🚀 [Deployment Guide](docs/DEPLOY_PRIVATE.md)** - Production deployment
- **🔐 [Security Guide](docs/SECURITY.md)** - Security best practices
- **📊 [Runbook](docs/RUNBOOK.md)** - Operations and troubleshooting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development workflow
git checkout -b feature/your-feature
make pre-commit-install
# Make your changes
make test
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

## 📄 License

This project is licensed under the Enterprise License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **📧 Email**: support@scorpius.io
- **💬 Discord**: [Scorpius Community](https://discord.gg/scorpius)
- **📖 Docs**: [Documentation Portal](https://docs.scorpius.io)
- **🐛 Issues**: [GitHub Issues](https://github.com/scorpius/enterprise-platform/issues)

## 🏆 Status

**✅ Production Ready** - Enterprise-grade platform with zero manual deployment required.

---

**Made with ❤️ by the Scorpius Team** | [Website](https://scorpius.io) | [Documentation](https://docs.scorpius.io)
