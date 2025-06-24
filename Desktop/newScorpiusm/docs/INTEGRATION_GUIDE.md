# 🔌 Scorpius Integration & Testing Guide

## Overview

This guide covers the complete integration testing process for the Scorpius Security Platform, including backend API testing, WebSocket connections, and frontend integration verification.

## 🧪 Integration Testing

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx websockets

# Ensure all services are running
startupscorpius --backend-only
```

### Running Integration Tests

```bash
# Run comprehensive integration tests
python test_integration.py

# Run specific test modules
pytest tests/test_scanner.py -v
pytest tests/test_enterprise.py -v
pytest tests/test_simulation.py -v
pytest tests/test_websocket.py -v
```

### Test Coverage

#### 🔐 Authentication & Authorization Tests

- JWT token generation and validation
- Role-based access control (RBAC)
- License tier validation
- Session management
- Multi-factor authentication (MFA)

#### 🛡️ Security Analysis Plugin Tests

- Slither static analysis integration
- Manticore symbolic execution
- MythX cloud analysis
- Custom heuristics engine
- Reentrancy detection
- Honeypot detection

#### 📡 API Endpoint Tests

- **127 REST Endpoints** across 9 modules
- Request/response validation
- Error handling and status codes
- Rate limiting enforcement
- Input sanitization

#### 🔌 WebSocket Connection Tests

- **34 WebSocket Connections** for real-time updates
- Connection establishment and teardown
- Message broadcasting and subscription
- Reconnection handling
- Authentication over WebSocket

#### 🎮 Simulation & Analysis Tests

- Contract sandboxing with Foundry/Anvil
- MEV simulation without mainnet risk
- Historical exploit replay
- AI-powered vulnerability analysis
- Report generation and export

## 🔧 Environment Setup

### Development Environment

```bash
# Clone repositories
git clone https://github.com/Louiiegee/newScorp.git
git clone https://github.com/Louiiegee/new-dash.git

# Setup backend
cd newScorp/backend/backend/SCANNER-main/SCANNER-main
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-security.txt

# Setup frontend
cd ../../../../new-dash
npm install
```

### Environment Variables

#### Backend (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://scorpius:password@localhost:5432/scorpius
REDIS_URL=redis://localhost:6379

# Security Analysis Tools
MYTHX_API_KEY=your-mythx-api-key
SLITHER_PATH=/usr/local/bin/slither
MANTICORE_TIMEOUT=300

# Blockchain RPC Endpoints
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your-key
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/your-key
BSC_RPC_URL=https://bsc-dataseed.binance.org/

# Authentication & Security
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
BCRYPT_ROUNDS=12

# Foundry/Anvil Configuration
FOUNDRY_PATH=/usr/local/bin/foundry
ANVIL_PORT=8545
ANVIL_ACCOUNTS=10

# OpenTelemetry & Monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
PROMETHEUS_PORT=9090
```

#### Frontend (.env)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_API_TIMEOUT=30000

# Authentication
VITE_JWT_SECRET=your-secret-key
VITE_JWT_EXPIRES_IN=24h

# Blockchain RPC (for frontend direct calls)
VITE_ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your-key
VITE_POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/your-key

# External Services
VITE_FLASHLOAN_PROVIDER_API=your-api-key
VITE_MEV_RELAY_URL=https://relay.flashbots.net
```

## 🐳 Docker Integration Testing

### Docker Compose Setup

```bash
# Start all services with Docker
docker-compose -f docker-compose.security.yml up -d

# Run integration tests against Docker environment
DOCKER_ENV=true python test_integration.py

# View logs
docker-compose logs -f scorpius-backend
docker-compose logs -f scorpius-frontend
```

### Docker Environment Variables

```yaml
# docker-compose.security.yml
version: '3.8'
services:
  scorpius-backend:
    build:
      context: .
      dockerfile: Dockerfile.security
    environment:
      - DATABASE_URL=postgresql://scorpius:password@postgres:5432/scorpius
      - REDIS_URL=redis://redis:6379
      - MYTHX_API_KEY=${MYTHX_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    ports:
      - '8000:8000'
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=scorpius
      - POSTGRES_USER=scorpius
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 📊 API Testing

### REST API Testing

```python
import httpx
import pytest

class TestScannerAPI:
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000")

    @pytest.fixture
    def auth_headers(self):
        # Get JWT token from login
        response = httpx.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    async def test_scanner_endpoints(self, client, auth_headers):
        # Test scanner configuration
        response = await client.get("/api/scanner/config", headers=auth_headers)
        assert response.status_code == 200

        # Test plugin management
        response = await client.get("/api/scanner/plugins", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) > 0

        # Test scan initiation
        response = await client.post("/api/scanner/scan",
            headers=auth_headers,
            json={
                "contract_address": "0x1234567890123456789012345678901234567890",
                "plugins": ["slither", "manticore"]
            }
        )
        assert response.status_code == 201
        scan_id = response.json()["scan_id"]

        # Test scan status
        response = await client.get(f"/api/scanner/scans/{scan_id}", headers=auth_headers)
        assert response.status_code == 200
```

### WebSocket Testing

```python
import asyncio
import websockets
import json

async def test_websocket_connections():
    # Test scanner progress WebSocket
    uri = "ws://localhost:8000/ws/scanner/progress"
    async with websockets.connect(uri) as websocket:
        # Send authentication
        await websocket.send(json.dumps({
            "type": "auth",
            "token": "your-jwt-token"
        }))

        # Wait for authentication confirmation
        response = await websocket.recv()
        auth_data = json.loads(response)
        assert auth_data["type"] == "auth_success"

        # Subscribe to scan progress
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channel": "scan_progress",
            "scan_id": "test-scan-id"
        }))

        # Receive progress updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data["type"] == "scan_complete":
                break
```

## 🔒 Security Testing

### Authentication Flow Testing

```python
def test_authentication_flow():
    # Test user registration
    response = httpx.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepassword123",
        "name": "Test User"
    })
    assert response.status_code == 201

    # Test login
    response = httpx.post("/api/auth/login", json={
        "email": "newuser@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    tokens = response.json()

    # Test protected endpoint access
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = httpx.get("/api/auth/profile", headers=headers)
    assert response.status_code == 200

    # Test token refresh
    response = httpx.post("/api/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 200
```

### License Validation Testing

```python
def test_license_validation():
    # Test community tier access
    headers = {"Authorization": f"Bearer {community_token}"}
    response = httpx.get("/api/scanner/config", headers=headers)
    assert response.status_code == 200

    # Test enterprise feature access (should fail for community)
    response = httpx.get("/api/enterprise/organization", headers=headers)
    assert response.status_code == 403

    # Test enterprise tier access
    headers = {"Authorization": f"Bearer {enterprise_token}"}
    response = httpx.get("/api/enterprise/organization", headers=headers)
    assert response.status_code == 200
```

## 🎯 Performance Testing

### Load Testing

```python
import asyncio
import aiohttp
import time

async def load_test_api():
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()

        # Create 100 concurrent requests
        for i in range(100):
            task = session.get("http://localhost:8000/api/scanner/config")
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        success_count = sum(1 for r in responses if r.status == 200)
        print(f"Completed {success_count}/100 requests in {end_time - start_time:.2f}s")
```

### WebSocket Connection Limits

```python
async def test_websocket_limits():
    connections = []
    try:
        # Test maximum concurrent connections
        for i in range(50):  # Adjust based on your limits
            ws = await websockets.connect("ws://localhost:8000/ws/system/metrics")
            connections.append(ws)

        print(f"Successfully established {len(connections)} WebSocket connections")

    finally:
        # Clean up connections
        for ws in connections:
            await ws.close()
```

## 📈 Monitoring & Observability

### Health Check Testing

```python
def test_health_endpoints():
    # Basic health check
    response = httpx.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Detailed health check
    response = httpx.get("http://localhost:8000/health/detailed")
    assert response.status_code == 200
    health_data = response.json()

    # Verify all components are healthy
    assert health_data["database"]["status"] == "healthy"
    assert health_data["redis"]["status"] == "healthy"
    assert health_data["plugins"]["slither"]["status"] == "available"
```

### Metrics Testing

```python
def test_prometheus_metrics():
    response = httpx.get("http://localhost:8000/metrics")
    assert response.status_code == 200

    metrics_text = response.text
    assert "scorpius_api_requests_total" in metrics_text
    assert "scorpius_scan_duration_seconds" in metrics_text
    assert "scorpius_websocket_connections" in metrics_text
```

## 🚀 Deployment Testing

### Production Readiness Checklist

- [ ] All 127 REST endpoints respond correctly
- [ ] All 34 WebSocket connections establish successfully
- [ ] Authentication and authorization work properly
- [ ] License validation enforces tier restrictions
- [ ] Database migrations run successfully
- [ ] Redis caching functions correctly
- [ ] Security analysis plugins are available
- [ ] Foundry/Anvil simulation works
- [ ] SSL/TLS certificates are valid
- [ ] Environment variables are properly configured
- [ ] Logging and monitoring are functional
- [ ] Error handling works as expected
- [ ] Rate limiting is enforced
- [ ] CORS is properly configured
- [ ] Docker containers build and run successfully

### Smoke Tests

```bash
#!/bin/bash
# smoke-test.sh

echo "Running Scorpius smoke tests..."

# Test backend health
curl -f http://localhost:8000/health || exit 1

# Test authentication
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}' | \
  jq -r '.access_token')

# Test protected endpoint
curl -f -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/scanner/config || exit 1

# Test WebSocket connection
node -e "
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8000/ws/system/metrics');
ws.on('open', () => { console.log('WebSocket connected'); ws.close(); });
ws.on('error', (err) => { console.error('WebSocket failed:', err); process.exit(1); });
"

echo "All smoke tests passed!"
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U scorpius -d scorpius -c "SELECT 1;"
```

#### Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping
```

#### Plugin Installation Issues

```bash
# Install Slither
pip install slither-analyzer

# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

#### WebSocket Connection Issues

```bash
# Check if WebSocket port is open
netstat -tlnp | grep :8000

# Test WebSocket connection
wscat -c ws://localhost:8000/ws/system/metrics
```

### Debug Mode

```bash
# Run backend in debug mode
DEBUG=true uvicorn scorpius_scanner.api.server:app --reload --log-level debug

# Enable verbose logging
export LOG_LEVEL=DEBUG
export PYTHONPATH=/path/to/scorpius_scanner
```

---

**For additional support, please refer to the main README.md or create an issue in the repository.**
