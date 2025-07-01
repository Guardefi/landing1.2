# Scorpius Enterprise Quick Reference

## 🚀 Quick Start

### Development Setup
```bash
# Install dependencies
pip install -r config/config/requirements-dev.txt

# Start development environment
docker-compose -f docker/docker/docker-compose.dev.yml up -d

# Run tests
pytest tests/

# Start the application
python scripts/start.py
```

### Production Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Or use Helm
helm install scorpius deploy/helm/
```

## 📁 Directory Quick Reference

### Core Application
| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `backend/` | Microservices | 12+ services (audit_trail, auth_proxy, etc.) |
| `frontend/` | Web application | React/Next.js app |
| `reporting/` | Reporting service | API, templates, webhooks |

### Infrastructure & Deployment
| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `infrastructure/` | IaC configurations | Terraform, K8s, Helm |
| `deploy/` | Deployment strategies | EKS, airgap, kustomize |
| `docker/` | Container configurations | docker-compose files |
| `monitoring/` | Observability | Prometheus, Grafana, alerts |

### Configuration & Scripts
| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `config/` | Configuration files | config/pyproject.toml, config/requirements-dev.txt |
| `scripts/` | Automation scripts | deploy.py, backup.py, security_scan.py |
| `tools/` | Development tools | build.ps1, quick-start.ps1 |

### Documentation & Testing
| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `docs/` | Documentation | API, architecture, deployment guides |
| `tests/` | Test suites | Unit, integration, e2e, security tests |
| `artifacts/` | Build outputs | Logs, reports, test results |

## 🔧 Common Tasks

### Adding a New Service
1. Create service directory in `backend/`
2. Add service definition in `services/`
3. Update `docker/docker/docker-compose.yml`
4. Add tests in `tests/`
5. Update documentation in `docs/`

### Configuration Management
```bash
# Environment-specific config
config/environments/config.template.toml

# Secrets (never commit actual values)
config/secrets/secrets.template.toml

# Global configuration
config/pyproject.toml
config/requirements-dev.txt
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/security/

# Run with coverage
pytest --cov=backend tests/
```

### Deployment
```bash
# Development
docker-compose -f docker/docker/docker-compose.dev.yml up -d

# Production (Kubernetes)
kubectl apply -f infrastructure/kubernetes/

# Production (Helm)
helm install scorpius deploy/helm/
```

## 📊 Monitoring & Observability

### Dashboards
- **Grafana**: `monitoring/dashboards/`
- **Prometheus**: `monitoring/prometheus/`
- **Alerts**: `monitoring/rules/`

### Logs
- **Application logs**: `artifacts/logs/`
- **Monitoring logs**: `monitoring/logs/`

### Metrics
- **Cost monitoring**: `monitoring/opencost/`
- **Security monitoring**: `monitoring/falco/`

## 🔒 Security

### Secrets Management
- **Template**: `config/secrets/secrets.template.toml`
- **Actual secrets**: Never committed to git
- **Git ignore**: `config/secrets/.gitignore`

### Security Tools
- **Security scripts**: `scripts/security/`
- **Security tests**: `tests/security/`
- **Security tools**: `tools/security/`

### Compliance
- **Documentation**: `docs/compliance/`
- **Security docs**: `docs/security/`

## 🚀 CI/CD Pipeline

### GitHub Actions
- **Workflows**: `.github/workflows/`
- **Issue templates**: `.github/ISSUE_TEMPLATE/`
- **PR templates**: `.github/PULL_REQUEST_TEMPLATE/`

### Build Process
```bash
# Build Docker images
docker build -f docker/Dockerfile .

# Run security scan
python scripts/security_scan.py

# Generate documentation
python scripts/generate_docs.py
```

## 📚 Documentation

### Key Documents
- **Architecture**: `docs/architecture/`
- **API Reference**: `docs/api/`
- **Deployment**: `docs/deployment/`
- **Getting Started**: `docs/getting-started/`

### Enterprise Docs
- **Project Structure**: `docs/enterprise/PROJECT_STRUCTURE.md`
- **Cleanup Summary**: `docs/enterprise/CLEANUP_SUMMARY.md`
- **Quick Reference**: `docs/enterprise/QUICK_REFERENCE.md`

## 🛠️ Troubleshooting

### Common Issues

#### Import Errors
```bash
# Update Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install dependencies
pip install -r config/config/requirements-dev.txt
```

#### Docker Issues
```bash
# Clean up containers
docker-compose -f docker/docker/docker-compose.dev.yml down

# Rebuild images
docker-compose -f docker/docker/docker-compose.dev.yml build --no-cache
```

#### Test Failures
```bash
# Run tests with verbose output
pytest -v tests/

# Run specific failing test
pytest tests/path/to/failing_test.py -v
```

### Getting Help
1. Check `docs/` for relevant documentation
2. Review `scripts/` for automation tools
3. Check `monitoring/` for system health
4. Contact team via GitHub issues

## 📈 Performance

### Monitoring
- **Application metrics**: Prometheus + Grafana
- **Cost tracking**: OpenCost
- **Security events**: Falco

### Optimization
- **Performance tests**: `tests/performance/`
- **Load testing**: Use tools in `tools/operations/`

## 🔄 Maintenance

### Regular Tasks
- **Backup**: `python scripts/backup.py`
- **Security scan**: `python scripts/security_scan.py`
- **Documentation**: `python scripts/generate_docs.py`
- **Service registration**: `python scripts/register_services.py`

### Updates
- **Dependencies**: Update `config/requirements-dev.txt`
- **Configuration**: Update `config/environments/`
- **Documentation**: Update relevant files in `docs/`

## 🎯 Best Practices

### Code Organization
- Keep related files together
- Use consistent naming conventions
- Document any deviations from structure
- Regular cleanup of temporary files

### Security
- Never commit secrets to git
- Use security scanning tools
- Follow principle of least privilege
- Regular security audits

### Testing
- Write tests for new features
- Maintain good test coverage
- Run security tests regularly
- Use different test types appropriately

### Documentation
- Keep documentation up to date
- Use clear, concise language
- Include examples where helpful
- Regular documentation reviews 