# Scorpius Enterprise Platform - Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Plugin Development](#plugin-development)
4. [API Documentation](#api-documentation)
5. [Security Guidelines](#security-guidelines)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Guide](#deployment-guide)
8. [Monitoring & Observability](#monitoring--observability)
9. [Troubleshooting](#troubleshooting)
10. [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### System Architecture

The Scorpius Enterprise Platform follows a microservices architecture with a unified orchestrator (API Gateway) at its core:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Load Balancer   │    │   Monitoring    │
│   Dashboard     │◄──►│     (Nginx)      │◄──►│  (Prometheus)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Unified Orchestrator                        │
│                     (API Gateway)                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────────────┐ │
│  │ Plugin Manager│ │ Auth & RBAC   │ │ Rate Limiting & Proxy │ │
│  └───────────────┘ └───────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Scanner Service │ │ Bridge Service  │ │ Mempool Service │
│                 │ │                 │ │                 │
│ • Vulnerability │ │ • Cross-chain   │ │ • Transaction   │
│   Detection     │ │   Transfers     │ │   Analysis      │
│ • Smart Contract│ │ • Liquidity     │ │ • Gas Tracking  │
│   Analysis      │ │   Management    │ │ • MEV Detection │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Honeypot Service│ │   MEV Service   │ │   Database      │
│                 │ │                 │ │   (PostgreSQL)  │
│ • Threat        │ │ • Arbitrage     │ │                 │
│   Detection     │ │ • Sandwich      │ │ • Redis Cache   │
│ • Fraud Analysis│ │   Attacks       │ │ • Event Store   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Core Components

#### 1. Unified Orchestrator (API Gateway)

- **Location**: `services/api-gateway/enhanced_gateway.py`
- **Purpose**: Central control plane for all microservices
- **Features**:
  - Plugin management and lifecycle
  - JWT authentication with refresh tokens
  - Role-based access control (RBAC)
  - Rate limiting with Redis backend
  - Intelligent reverse proxy routing
  - WebSocket support for real-time updates
  - Prometheus metrics and structured logging
  - Health checks and service discovery

#### 2. Plugin System

- **Location**: `packages/core/orchestrator.py`
- **Purpose**: Dynamic microservice management
- **Features**:
  - Hot-pluggable microservices
  - Dependency resolution
  - Health monitoring
  - Event-driven communication

#### 3. Security Layer

- **Location**: `config/security.yaml`
- **Purpose**: Enterprise-grade security
- **Features**:
  - Multi-factor authentication
  - API key management
  - Input validation and sanitization
  - Security headers and CORS
  - Audit logging and compliance
  - Circuit breaker
  - Retry patterns
  - OpenTelemetry
  - OpenCost
  - Chaos engineering

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Git
- Redis 6+
- PostgreSQL 14+
- VS Code with Dev Container extension

### Using Dev Container

1. **Open VS Code**:

   ```bash
   code .
   ```

2. **Open in Container**:
   - Click the green "Dev Containers" button in the bottom left
   - Select "Reopen in Container"

3. **Dev Container Features**:
   - Pre-configured Python development environment
   - Docker-in-Docker support
   - Git and GitHub CLI
   - Code formatting and linting tools
   - Integrated testing tools
   - VS Code extensions:
     - Python development tools
     - Pylance for type checking
     - Black formatter
     - Isort
     - Flake8
     - Mypy
     - Debugpy
     - Test adapters and explorers

### Local Development

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd enterprise-platform
   ```

2. **Setup Python environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r config/config/requirements-dev.txt
   ```

3. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start infrastructure services**:

   ```bash
   make dev-setup
   # Or manually:
   docker-compose -f docker/docker-compose.dev.yml up -d postgres redis
   ```

5. **Run database migrations**:

   ```bash
   make migrate
   ```

6. **Start the development server**:

   ```bash
   make dev
   # This starts the orchestrator and all microservices
   ```

7. **Access the application**:
   - API Gateway: <http://localhost:8000>
   - Health Check: <http://localhost:8000/healthz>
   - Metrics: <http://localhost:8000/metrics>
   - API Docs: <http://localhost:8000/docs>

### Quick Start

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd enterprise-platform
   ```

2. **Setup Python environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r config/config/requirements-dev.txt
   ```

3. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start infrastructure services**:

   ```bash
   make dev-setup
   # Or manually:
   docker-compose -f docker/docker-compose.dev.yml up -d postgres redis
   ```

5. **Run database migrations**:

   ```bash
   make migrate
   ```

6. **Start the development server**:

   ```bash
   make dev
   # This starts the orchestrator and all microservices
   ```

7. **Access the application**:
   - API Gateway: <http://localhost:8000>
   - Health Check: <http://localhost:8000/healthz>
   - Metrics: <http://localhost:8000/metrics>
   - API Docs: <http://localhost:8000/docs>

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://scorpius:password@localhost:5432/scorpius
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
TRUSTED_HOSTS=localhost,127.0.0.1

# API Configuration
API_RATE_LIMIT=1000
MAX_REQUEST_SIZE=10485760

# Monitoring
PROMETHEUS_METRICS=true
STRUCTURED_LOGGING=true

# External Services
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
```

### Development Commands

```bash
# Development shortcuts
make dev          # Start development environment
make test         # Run all tests
make lint         # Run code quality checks
make format       # Format code with black and isort
make security     # Run security scans
make docs         # Generate documentation

# Infrastructure management
make docker-build # Build all Docker images
make docker-up    # Start all services
make docker-down  # Stop all services
make docker-logs  # View service logs

# Database operations
make migrate      # Run database migrations
make reset-db     # Reset database (development only)
make backup-db    # Create database backup

# Production deployment
make deploy-staging  # Deploy to staging
make deploy-prod     # Deploy to production
make rollback        # Rollback last deployment
```

## Plugin Development

### Creating a New Plugin

1. **Plugin Structure**:

   ```
   backend/your-service/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── models.py
   │   ├── routes.py
   │   └── config.py
   ├── tests/
   │   ├── __init__.py
   │   └── test_main.py
   ├── Dockerfile
   ├── config/config/requirements-dev.txt
   └── plugin.yaml
   ```

2. **Plugin Configuration** (`plugin.yaml`):

   ```yaml
   name: "your-service"
   version: "1.0.0"
   description: "Your service description"
   
   # Plugin metadata
   metadata:
     author: "Your Name"
     category: "analysis"
     tags: ["blockchain", "security"]
   
   # Service configuration
   service:
     port: 8010
     health_endpoint: "/health"
     metrics_endpoint: "/metrics"
     
   # Dependencies
   dependencies:
     - "database-service"
     - "redis-service"
   
   # Routes to expose through API Gateway
   routes:
     - path: "/api/your-service"
       methods: ["GET", "POST"]
       auth_required: true
       rate_limit: 100
   
   # Environment variables
   environment:
     - name: "SERVICE_CONFIG"
       required: true
   ```

3. **FastAPI Service** (`app/main.py`):

   ```python
   from fastapi import FastAPI, Depends
   from prometheus_client import Counter, Histogram, generate_latest
   import structlog
   from backend.utils.retry import resilient_rpc
   
   # Configure logging
   logger = structlog.get_logger(__name__)
   
   # Metrics
   REQUEST_COUNT = Counter('your_service_requests_total', 'Total requests')
   REQUEST_DURATION = Histogram('your_service_request_duration_seconds', 'Request duration')
   
   app = FastAPI(
       title="Your Service",
       description="Service description",
       version="1.0.0"
   )
   
   @app.get("/health")
   async def health_check():
       """Health check endpoint."""
       return {"status": "healthy", "service": "your-service"}
   
   @app.get("/metrics")
   async def metrics():
       """Prometheus metrics endpoint."""
       return Response(generate_latest(), media_type="text/plain")
   
   @app.get("/api/your-service/endpoint")
   @resilient_rpc(
       max_attempts=3,
       initial_wait=1.0,
       max_wait=30.0,
       failure_threshold=3,
       reset_timeout=60
   )
   async def your_endpoint():
       """Your business logic endpoint with resilience patterns."""
       REQUEST_COUNT.inc()
       with REQUEST_DURATION.time():
           logger.info("Processing request")
           # Your business logic here
           return {"result": "success"}
   ```

### Resilience Patterns

1. **Retry Pattern**:
   - Automatic retries with exponential backoff
   - Configurable retry attempts and wait times
   - Built-in circuit breaker
   - Example usage:

   ```python
   from backend.utils.retry import resilient_rpc
   
   @resilient_rpc(
       max_attempts=3,
       initial_wait=1.0,
       max_wait=30.0,
       failure_threshold=3,
       reset_timeout=60
   )
   async def process_data():
       # Your code here
       pass
   ```

2. **Circuit Breaker**:
   - Automatic circuit breaking on failures
   - Configurable failure thresholds
   - Automatic recovery
   - Example usage:

   ```python
   from backend.utils.retry import create_circuit_breaker
   
   breaker = create_circuit_breaker(
       failure_threshold=3,
       reset_timeout=60
   )
   
   @breaker
   async def critical_operation():
       # Your critical operation here
       pass
   ```

3. **Best Practices**:
   - Always use retry patterns for external service calls
   - Implement circuit breakers for critical operations
   - Monitor circuit breaker state
   - Log failures and circuit breaker state changes
   - Configure appropriate timeouts and thresholds

4. **Register Plugin**:

   ```python
   # In orchestrator
   from packages.core.orchestrator import PluginManager
   
   plugin_manager = PluginManager()
   await plugin_manager.register_plugin("your-service", "/path/to/plugin.yaml")
   await plugin_manager.activate_plugin("your-service")
   ```

### Plugin Best Practices

1. **Health Checks**: Always implement `/health`

## Monitoring & Observability

1. **Metrics Collection**:
   - Prometheus metrics
   - OpenTelemetry integration
   - Custom metrics
   - Request tracking
   - Error monitoring
   - Resource utilization
   - Cost metrics

2. **Logging**:
   - Structured logging
   - Log aggregation
   - Error tracking
   - Audit logging
   - Security events
   - Cost events

3. **Tracing**:
   - OpenTelemetry integration
   - Request tracing
   - Performance monitoring
   - Error correlation
   - Cost tracing

4. **Monitoring Tools**:
   - Prometheus
   - Grafana
   - OpenTelemetry Collector
   - OpenCost
   - ELK Stack
   - New Relic

5. **Dashboards**:
   - Service health
   - Performance metrics
   - Error rates
   - Resource usage
   - Cost distribution
   - Cost by namespace
   - Cost by pod

6. **Alerting**:
   - Service availability
   - Performance thresholds
   - Error rates
   - Resource usage
   - Cost anomalies
   - Security events

7. **Best Practices**:
   - Monitor all services
   - Set up alerts
   - Regular monitoring
   - Performance optimization
   - Cost optimization
   - Security monitoring
   - Incident response

8. **Implementation Example**:

   ```python
   from opentelemetry import trace
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
   import structlog
   
   # Configure OpenTelemetry
   trace.set_tracer_provider(TracerProvider())
   otel_exporter = OTLPSpanExporter(
       endpoint="http://otel-collector:4317",
       insecure=True
   )
   span_processor = BatchSpanProcessor(otel_exporter)
   trace.get_tracer_provider().add_span_processor(span_processor)
   
   # Configure logging
   logger = structlog.get_logger()
   
   def process_request():
       tracer = trace.get_tracer(__name__)
       with tracer.start_as_current_span("process_request"):
           try:
               logger.info("Processing request")
               # Your business logic here
               return "success"
           except Exception as e:
               logger.error("Request failed", error=str(e))
               raise
   ```

9. **Cost Monitoring**:
   - OpenCost integration
   - Cost distribution analysis
   - Resource utilization monitoring
   - Cost anomaly detection
   - Cost optimization recommendations
   - Cost alerts and notifications

10. **Security Monitoring**:
    - Security events tracking
    - Threat detection
    - Incident response monitoring
    - Compliance monitoring
    - Security metrics
    - Security alerts

11. **Performance Optimization**:
    - Performance metrics collection
    - Performance analysis
    - Performance testing
    - Performance optimization
    - Resource optimization
    - Cost optimization

12. **Incident Response**:
    - Incident detection
    - Incident response procedures
    - Incident tracking
    - Incident reporting
    - Post-incident analysis
    - Incident prevention

## API Documentation

### Authentication

All API endpoints require JWT authentication unless specified otherwise.

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password",
  "tenant_id": "optional_tenant_id"
}
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Using JWT Token

```http
GET /api/protected-endpoint
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
X-Tenant-ID: your_tenant_id
```

### Core Endpoints

#### Health Checks

```http
GET /healthz           # Simple health check
GET /readyz            # Readiness check
GET /health            # Detailed health information
```

#### Plugin Management (Admin Only)

```http
GET /admin/plugins                    # List all plugins
POST /admin/plugins/{name}/activate   # Activate plugin
POST /admin/plugins/{name}/deactivate # Deactivate plugin
GET /admin/plugins/{name}/status      # Get plugin status
```

#### Scanner Service

```http
POST /api/scanner/scan
{
  "contract_address": "0x...",
  "scan_type": "comprehensive",
  "include_bytecode": true
}

GET /api/scanner/scan/{scan_id}/status
GET /api/scanner/scans?limit=50&offset=0
```

#### Bridge Service

```http
GET /api/bridge/chains                # Supported chains
POST /api/bridge/simulate             # Simulate transfer
GET /api/bridge/transfers             # Transfer history
```

### Rate Limiting

API endpoints are rate-limited based on:

- IP address
- User authentication
- Endpoint-specific limits

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Error Handling

Standard HTTP status codes are used:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "contract_address",
      "issue": "Invalid Ethereum address format"
    },
    "request_id": "req_1234567890"
  }
}
```

## Security Guidelines

- Monitor security events
- Track authentication attempts
- Monitor permission changes
- Track security policy violations
- Monitor cost anomalies
- Monitor resource anomalies

2. **Response**:
   - Isolate affected systems
   - Block malicious IP addresses
   - Revoke compromised tokens
   - Implement circuit breakers
   - Enforce cost controls
   - Limit resource usage

3. **Recovery**:
   - Restore from backups
   - Reset affected systems
   - Reissue tokens
   - Reset permissions
   - Reset cost controls
   - Reset resource limits

4. **Post-Incident**:
   - Analyze security events
   - Review authentication logs
   - Review permission changes
   - Review security policies
   - Review cost controls
   - Review resource limits
1. **Request Validation**:

   ```python
   from pydantic import BaseModel, validator
   from typing import Optional
   
   class ScanRequest(BaseModel):
       contract_address: str
       scan_type: str = "quick"
       
       @validator('contract_address')
       def validate_address(cls, v):
           if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
               raise ValueError('Invalid Ethereum address')
           return v.lower()
   ```

2. **SQL Injection Prevention**:
   - Use parameterized queries
   - Employ ORM (SQLAlchemy) for database operations
   - Validate and sanitize all inputs

3. **XSS Prevention**:
   - Escape output data
   - Use Content Security Policy headers
   - Validate and sanitize user inputs

### Secrets Management

1. **Environment Variables**:

   ```python
   from pydantic import BaseSettings
   
   class Settings(BaseSettings):
       jwt_secret: str
       database_url: str
       redis_url: str
       
       class Config:
           env_file = ".env"
   ```

2. **AWS Secrets Manager** (Production):

   ```python
   import boto3
   
   def get_secret(secret_name):
       client = boto3.client('secretsmanager')
       response = client.get_secret_value(SecretId=secret_name)
       return json.loads(response['SecretString'])
   ```

### Security Headers

Ensure these headers are set:

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

## Testing Strategy

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_auth.py
│   ├── test_scanner.py
│   └── test_bridge.py
├── integration/          # Integration tests
│   ├── test_api.py
│   └── test_plugins.py
├── performance/          # Performance tests
│   └── locustfile.py
├── security/            # Security tests
│   └── security_tests.py
└── fixtures/            # Test data and fixtures
    └── sample_data.py
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v --asyncio-mode=auto

# All tests with coverage
pytest --cov=app --cov-report=html

# Performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Security tests
python tests/security/security_tests.py
```

### Test Examples

#### Unit Test

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_scan_contract():
    # Mock dependencies
    with patch('app.scanner.analyze_contract') as mock_analyze:
        mock_analyze.return_value = {"vulnerabilities": []}
        
        response = client.post("/api/scanner/scan", json={
            "contract_address": "0x1234567890123456789012345678901234567890"
        })
        
        assert response.status_code == 202
        assert "scan_id" in response.json()
```

#### Integration Test

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_scan_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Authenticate
        login_response = await client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start scan
        scan_response = await client.post("/api/scanner/scan", 
                                        json={"contract_address": "0x..."}, 
                                        headers=headers)
        scan_id = scan_response.json()["scan_id"]
        
        # Check status
        status_response = await client.get(f"/api/scanner/scan/{scan_id}/status",
                                         headers=headers)
        assert status_response.status_code == 200
```

## Deployment Guide

### Development Deployment

```bash
# Start all services
make dev

# Or with Docker Compose
docker-compose -f docker/docker-compose.dev.yml up -d

# Or with Dev Container
code .
```

### Staging Deployment

```bash
# Deploy to Kubernetes staging
make deploy-staging

# Or manually with Skaffold
skaffold run --profile=staging

# Run chaos tests
make chaos-test

# Verify resilience
make verify-resilience
```

### Production Deployment

1. **Infrastructure Setup** (Terraform):

   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan -var-file="prod.tfvars"
   terraform apply
   ```

2. **Security Setup**:

   ```bash
   # Configure secrets
   make configure-secrets
   
   # Setup security policies
   make setup-security
   
   # Verify security
   make verify-security
   ```

3. **Cost Optimization**:

   ```bash
   # Configure cost controls
   make configure-cost
   
   # Verify cost optimization
   make verify-cost
   ```

4. **Application Deployment**:

   ```bash
   # Deploy to production
   make deploy-prod
   
   # Monitor deployment
   kubectl rollout status deployment/api-gateway -n scorpius
   
   # Verify OpenTelemetry
   make verify-opentelemetry
   
   # Verify OpenCost
   make verify-opencost
   ```

5. **Post-deployment Verification**:

   ```bash
   # Run smoke tests
   make smoke-tests
   
   # Check health
   curl https://api.scorpius.com/healthz
   
   # Verify security
   make verify-security
   
   # Verify cost
   make verify-cost
   
   # Verify resilience
   make verify-resilience
   ```

### Disaster Recovery

1. **Backup**:

   ```bash
   # Backup all data
   make backup
   
   # Verify backup
   make verify-backup
   ```

2. **Failover**:

   ```bash
   # Failover to DR environment
   make failover
   
   # Verify failover
   make verify-failover
   ```

3. **Restore**:

   ```bash
   # Restore from backup
   make restore
   
   # Verify restore
   make verify-restore
   ```

### Security Verification

1. **Code Security**:

   ```bash
   # Run security scans
   make security-scan
   
   # Verify dependencies
   make verify-dependencies
   ```

2. **Infrastructure Security**:

   ```bash
   # Verify Terraform security
   make verify-terraform
   
   # Verify Helm security
   make verify-helm
   ```

3. **Runtime Security**:

   ```bash
   # Verify Kubernetes security
   make verify-k8s
   
   # Verify network policies
   make verify-network
   ```

### Cost Optimization

1. **Resource Optimization**:

   ```bash
   # Optimize resources
   make optimize-resources
   
   # Verify optimization
   make verify-optimization
   ```

2. **Cost Monitoring**:

   ```bash
   # Check cost distribution
   make check-cost
   
   # Verify cost controls
   make verify-cost-controls
   ```

3. **Cost Alerts**:

   ```bash
   # Configure cost alerts
   make configure-cost-alerts
   
   # Verify alerts
   make verify-cost-alerts
   ```

### Resilience Testing

1. **Chaos Testing**:

   ```bash
   # Run chaos tests
   make chaos-test
   
   # Verify resilience
   make verify-resilience
   ```

2. **Performance Testing**:

   ```bash
   # Run performance tests
   make performance-test
   
   # Verify performance
   make verify-performance
   ```

3. **Disaster Recovery Testing**:

   ```bash
   # Run disaster recovery tests
   make disaster-recovery-test
   
   # Verify recovery
   make verify-recovery
   ```

### Common Commands

```bash
# Full deployment
make deploy-all

# Full verification
make verify-all

# Full recovery
make recovery-all

# Full security check
make security-check-all

# Full cost optimization
make optimize-all
```

### Monitoring Deployment

After deployment, verify:

- All services are healthy
- Metrics are being collected
- Logs are being aggregated
- Alerts are configured

## Monitoring & Observability

### Metrics (Prometheus)

Default metrics exposed:

- HTTP request counts and durations
- Active WebSocket connections
- Plugin status and health
- Database connection pool metrics
- Redis cache hit/miss ratios
- Custom business metrics
- Circuit breaker state
- Resource utilization
- Cost metrics
- Security events

### Logging (Structured)

```python
import structlog

logger = structlog.get_logger(__name__)

# Example logging
logger.info("Processing scan request",
           user_id=user.id,
           contract_address=request.contract_address,
           scan_type=request.scan_type,
           request_id=request_id,
           cost=scan_cost,
           security_check=security_result)
```

### Tracing (OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_scan(contract_address: str):
    with tracer.start_as_current_span("process_scan") as span:
        span.set_attribute("contract.address", contract_address)
        span.set_attribute("scan.duration", duration)
        span.set_attribute("cost", scan_cost)
        span.set_attribute("security.result", security_result)
```

### Cost Monitoring (OpenCost)

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# Track cost metrics
meter.create_counter(
    "scan_cost",
    unit="USD",
    description="Cost of scan operations"
)
```

### Security Monitoring

1. **Authentication Events**:
   - Login attempts
   - Token usage
   - Permission changes
   - Failed authentications

2. **Authorization Events**:
   - Role changes
   - Permission grants
   - Access denials
   - Policy violations

3. **Security Events**:
   - Failed security checks
   - Suspicious activities
   - Policy violations
   - Security alerts

### Alerting

Key alerts configured:

- Service down
- High error rate (>5%)
- High response time (>2s)
- Database connection issues
- Rate limit violations
- Security events
- Cost anomalies
- Resource utilization
- Circuit breaker state

### Dashboards

1. **Service Health**:
   - Request rates
   - Error rates
   - Response times
   - Resource usage

2. **Cost Metrics**:
   - Cost distribution
   - Resource utilization
   - Cost anomalies
   - Optimization opportunities

3. **Security Metrics**:
   - Authentication events
   - Authorization events
   - Security events
   - Policy violations

4. **Resilience Metrics**:
   - Circuit breaker state
   - Retry attempts
   - Success rates
   - Error patterns

### Common Commands

```bash
# Check metrics
make check-metrics

# Check traces
make check-traces

# Check cost
make check-cost

# Check security
make check-security

# Check resilience
make check-resilience

# Check all monitoring
make check-monitoring
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**:

   ```bash
   # Check logs
   docker-compose logs api-gateway
   
   # Check configuration
   make validate-config
   
   # Verify dependencies
   docker-compose ps
   ```

2. **Database Connection Issues**:

   ```bash
   # Test connection
   psql -h localhost -U scorpius -d scorpius
   
   # Check migrations
   alembic current
   alembic upgrade head
   ```

3. **Redis Connection Issues**:

   ```bash
   # Test Redis
   redis-cli ping
   
   # Check configuration
   echo $REDIS_URL
   ```

4. **Authentication Issues**:

   ```bash
   # Verify JWT secret
   echo $JWT_SECRET
   
   # Test token generation
   curl -X POST http://localhost:8000/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}'
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
export ENVIRONMENT=development
```

### Performance Issues

1. **Check metrics**: Visit `/metrics` endpoint
2. **Profile with APM**: Use performance profilers
3. **Database queries**: Enable SQL query logging
4. **Memory usage**: Monitor container memory limits

## Contributing Guidelines

### Code Standards

1. **Python Style**:
   - Follow PEP 8
   - Use Black for formatting
   - Use isort for import sorting
   - Maximum line length: 88 characters
   - Use async/await for I/O operations
   - Use resilience patterns for RPC calls

2. **Type Hints**:

   ```python
   from typing import List, Optional, Dict, Any
   from backend.decorators.rpc import resilient_rpc
   
   @resilient_rpc(
       max_attempts=3,
       initial_wait=1.0,
       max_wait=30.0,
       failure_threshold=3,
       reset_timeout=60
   )
   async def external_call():
       # Implementation
       pass
   ```

3. **Documentation**:

   ```python
   def analyze_contract(address: str, scan_type: str = "quick") -> ScanResult:
       """
       Analyze a smart contract for vulnerabilities.
       
       Args:
           address: Ethereum contract address (0x...)
           scan_type: Type of scan to perform (quick, deep, comprehensive)
           
       Returns:
           ScanResult containing vulnerability analysis
           
       Raises:
           InvalidAddressError: If address format is invalid
           ScanTimeoutError: If scan takes too long
           CircuitBreakerError: If circuit breaker is open
           CostExceededError: If operation exceeds cost limits
       """
       pass
   ```

4. **Security Practices**:

   ```python
   from fastapi import Depends
   from app.auth import require_role, require_mfa
   from app.security import validate_security
   
   @router.post("/secure-endpoint")
   async def secure_endpoint():
       validate_security("endpoint")
       # Implementation
       pass
   ```

5. **Cost Controls**:

   ```python
   from opentelemetry import metrics
   from app.cost import validate_cost
   
   meter = metrics.get_meter(__name__)
   cost_tracker = CostTracker()
   
   @router.post("/analyze")
   async def analyze_contract(
       address: str,
       scan_type: str = "quick"
   ) -> ScanResult:
       with cost_tracker.track_operation(scan_type):
           # Implementation
           pass
   ```

### Commit Guidelines

Use conventional commits with security and cost tags:

```
type(scope): description

feat(scanner): add new vulnerability detection algorithm
fix(auth): resolve JWT token expiration issue
docs(api): update authentication endpoints documentation
test(bridge): add integration tests for cross-chain transfers
sec(scanner): add security validation for contract analysis
cost(api): implement cost tracking for API operations
```

### Pull Request Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run full test suite
4. Run security scans
5. Run cost analysis
6. Update documentation
7. Submit PR with detailed description
8. Address review feedback
9. Pass security review
10. Pass cost review
11. Merge after approval

### Development Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Make changes
# ...

# Test changes
make test
make lint
## Security Commands

### Security Scan
```bash
# Run security scan
make security-scan

# Validate security configuration
make security-validate

# Run security audit
make security-audit

# Generate security report
make security-report
```

### Cost Analysis

```bash
# Run cost analysis
make cost-analysis

# Validate cost controls
make cost-validate

# Generate cost report
make cost-report
```

### Chaos Testing

```bash
# Run chaos tests
make chaos-test

# Run specific chaos scenarios
make chaos-network-failure
make chaos-database-failure
make chaos-cpu-stress
```

### Performance Testing

```bash
# Run performance tests
make performance-test

# Run load testing
make load-test

# Run stress testing
make stress-test
```

### Security Compliance

```bash
# Run compliance checks
make compliance-check

# Generate compliance report
make compliance-report

# Validate security policies
make policy-validate
```

### Security Monitoring

```bash
# Start security monitoring
make security-monitor

# View security metrics
make security-metrics

# Generate alert report
make alert-report
```

### Security Documentation

```bash
# Generate security documentation
make security-docs

# Update security policies
make update-policies

# Generate threat model
make threat-model
```

## Security Best Practices

### 1. Security Development

```bash
# Run security linting
make security-lint

# Run security unit tests
make security-test

# Run security integration tests
make security-integration-test
```

### Security Testing Framework

#### 1. Test Categories

##### 1.1 Authentication Testing

```yaml
# Authentication test configuration
authentication_tests:
  scenarios:
    - login_success
    - login_failure
    - token_expiration
    - mfa_required
    - rate_limiting

  validation:
    - jwt_signature
    - token_expiry
    - session_management
    - password_policy
```

##### 1.2 Authorization Testing

```yaml
# Authorization test configuration
authorization_tests:
  scenarios:
    - role_based_access
    - permission_validation
    - resource_access
    - privilege_escalation

  validation:
    - rbac_enforcement
    - policy_evaluation
    - access_control
    - audit_trail
```

#### 2. Test Commands

##### 2.1 Unit Testing

```bash
# Run security unit tests
make security-unit-test

# Test specific components
make test-authentication
make test-encryption
make test-validation
```

##### 2.2 Integration Testing

```bash
# Run security integration tests
make security-integration-test

# Test specific flows
make test-auth-flow
make test-data-protection
make test-api-security
```

##### 2.3 Cost Testing

```bash
# Run cost validation tests
make cost-test

# Validate cost controls
make cost-validate

# Test cost optimization
make test-cost-optimization
```

##### 2.4 Chaos Testing

```bash
# Run chaos tests
make chaos-test

# Test specific scenarios
make test-network-failure
make test-database-failure
make test-resource-exhaustion
```

#### 3. Test Validation

##### 3.1 Security Validation

```yaml
# Security validation requirements
validation:
  authentication:
    success_rate: 99.9%
    response_time: <1s
    error_rate: <0.1%

  authorization:
    policy_coverage: 100%
    access_control: strict
    audit_trail: enabled

  encryption:
    key_rotation: 90d
    algorithm_strength: aes-256
    compliance: required
```

##### 3.2 Cost Validation

```yaml
# Cost validation requirements
cost_validation:
  thresholds:
    cpu: 80%
    memory: 90%
    storage: 95%
    network: 95%

  optimization:
    required: true
    frequency: daily
    validation: automated
```

#### 4. Test Documentation

- [Test Scenarios](./testing/scenarios)
- [Validation Requirements](./testing/validation)
- [Cost Optimization](./testing/cost)
- [Chaos Testing](./testing/chaos)
- [Security Validation](./testing/security)

#### 5. Test Updates

- **Last Updated**: 2024-06-27
- **Next Review**: 2024-09-27
- **Version**: 2.0.0
- **Status**: Active

#### 6. Test Resources

- [Test Templates](./testing/templates)
- [Validation Scripts](./testing/scripts)
- [Cost Optimization Tools](./testing/cost-tools)
- [Security Testing Tools](./testing/security-tools)
- [Chaos Testing Framework](./testing/chaos-framework)

### 2. Security Deployment

```bash
# Validate security configuration
make security-validate-config

# Run security deployment checks
make security-deploy-check

# Generate deployment security report
make deploy-security-report
```

### 3. Security Maintenance

```bash
# Run security updates
make security-update

# Run security patches
make security-patch

# Run security audit trail
make security-audit-trail
```

## Security Response

### 1. Incident Response

```bash
# Run incident detection
make incident-detect

# Generate incident report
make incident-report

# Run containment procedures
make incident-contain
```

### 2. Recovery Procedures

```bash
# Run recovery procedures
make recovery-procedure

# Generate recovery report
make recovery-report

# Run post-mortem analysis
make post-mortem
```

## Security Training

### 1. Security Awareness

```bash
# Run security training
make security-training

# Generate training materials
make training-materials

# Run security drills
make security-drill
```

### 2. Security Validation

```bash
# Validate training completion
make training-validate

# Generate training report
make training-report

# Run security assessment
make security-assessment
```

## Security Documentation

- [Security Best Practices](./security/best-practices.md)
- [Security Architecture](./security/architecture.md)
- [Security Hardening](./security/hardening.md)
- [Security Compliance](./security/compliance.md)
- [Security Monitoring](./security/monitoring.md)
- [Security Incident Response](./security/incident-response.md)
- [Security Testing](./security/testing.md)
- [Security Training](./security/training.md)

# Commit changes

git add .
git commit -m "feat(scope): description"

# Push and create PR

git push origin feature/new-feature

```

---

## Additional Resources

- [API Reference](./API_REFERENCE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Best Practices](./SECURITY.md)
- [Performance Tuning](./PERFORMANCE.md)
- [Plugin Development](./PLUGIN_DEVELOPMENT.md)

For questions or support, please open an issue or contact the development team.
