# API Gateway Service

FastAPI-based central orchestrator for the Scorpius microservices platform.

## Features

- **Request Routing**: Intelligent routing to appropriate microservices
- **WebSocket Hub**: Real-time communication with frontend
- **Authentication**: JWT-based authentication and authorization
- **Rate Limiting**: Protection against abuse
- **Circuit Breakers**: Resilience against service failures
- **Health Checks**: Continuous monitoring of service health
- **Metrics**: Prometheus-compatible metrics collection
- **Load Balancing**: Distribution of requests across service instances

## Quick Start

```bash
# Install dependencies
pip install -r config/config/requirements-dev.txt

# Start the gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Core
- `GET /` - Gateway information
- `GET /health` - System health status
- `GET /metrics` - Prometheus metrics

### Services
- `GET /api/v1/services` - List available services
- `POST /api/v1/execute` - Execute service request
- `GET /api/v1/{service}/health` - Service health
- `{METHOD} /api/v1/{service}/{path}` - Proxy to service

### WebSocket
- `WS /ws` - General WebSocket connection
- `WS /ws/{service}` - Service-specific WebSocket

## Configuration

Environment variables:
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - JWT signing secret
- `LOG_LEVEL` - Logging level
- `CORS_ORIGINS` - Allowed CORS origins

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Format code
black main.py
isort main.py
```
