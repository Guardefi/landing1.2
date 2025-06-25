# Scorpius Bridge Network Architecture

## Overview

The Scorpius Bridge Network is an enterprise-grade cross-chain interoperability system built with Domain-Driven Design (DDD) principles and Clean Architecture patterns. It provides secure, efficient, and scalable bridge transfers between multiple blockchain networks.

## Architecture Layers

### 1. Domain Layer (`domain/`)
Pure business logic without external dependencies:
- **Models**: Core entities (BridgeTransaction, ValidatorNode, LiquidityPool)
- **Events**: Domain events for event-driven architecture
- **Policies**: Business rules and invariants
- **Errors**: Custom domain exceptions

### 2. Application Layer (`application/`)
Use-case orchestration and CQRS implementation:
- **Commands**: Write operations that change state
- **Queries**: Read operations that return data
- **Services**: Thin orchestrators that coordinate domain objects

### 3. Infrastructure Layer (`infrastructure/`)
External integrations and technical implementations:
- **Blockchain**: Chain-specific RPC clients
- **Persistence**: Repository pattern with SQLModel/SQLAlchemy
- **Messaging**: Event publishing with Kafka/Redis
- **Caching**: Redis caching layer
- **Tasks**: Background job processing

### 4. API Layer (`api/`)
Transport adapters for external communication:
- **HTTP**: FastAPI routers with versioning
- **WebSocket**: Real-time event streaming
- **gRPC**: High-performance service communication

### 5. Adapters Layer (`adapters/`)
Integration with existing systems:
- Existing atomic swap engines
- Liquidity pool managers
- Validator network components

## Key Features

### Security
- Multi-signature validation with configurable thresholds
- Hardware Security Module (HSM) integration ready
- Role-based access control (RBAC)
- Rate limiting and DDoS protection
- Comprehensive audit logging

### Scalability
- Async/await throughout for high concurrency
- Redis caching for frequently accessed data
- Event-driven architecture with Kafka
- Database connection pooling
- Horizontal scaling support

### Observability
- Structured JSON logging
- Prometheus metrics collection
- OpenTelemetry distributed tracing
- Health check endpoints
- Grafana dashboards

### Development Experience
- Type safety with Pydantic and mypy
- Comprehensive test suite (unit/integration/contract)
- Docker containerization
- CI/CD pipeline ready
- API documentation with OpenAPI/Swagger

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework with automatic API docs
- **Pydantic**: Data validation and settings management
- **SQLModel**: SQL databases with Python type annotations
- **Alembic**: Database migrations

### Databases & Caching
- **PostgreSQL**: Primary data store with async support
- **Redis**: Caching and session storage
- **SQLAlchemy**: ORM with async support

### Blockchain Integration
- **Web3.py**: Ethereum and EVM-compatible chains
- **Solana.py**: Solana blockchain integration
- **Custom clients**: Extensible blockchain client architecture

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Structlog**: Structured logging
- **OpenTelemetry**: Distributed tracing

### Development Tools
- **pytest**: Testing framework with async support
- **Black**: Code formatting
- **mypy**: Static type checking
- **Docker**: Containerization

## Getting Started

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone and setup environment**:
```bash
git clone <repository>
cd scorpius_bridge
cp .env.example .env
# Edit .env with your configuration
```

2. **Start infrastructure services**:
```bash
docker-compose up -d postgres redis kafka
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run database migrations**:
```bash
alembic upgrade head
```

5. **Start the API server**:
```bash
uvicorn scorpius_bridge.main:app --reload
```

6. **Access the API**:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Production Deployment

1. **Build Docker image**:
```bash
docker build -t scorpius-bridge:latest .
```

2. **Deploy with docker-compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Or deploy to Kubernetes** (coming soon)

## API Examples

### Initiate Bridge Transfer
```bash
curl -X POST "http://localhost:8000/api/v2/bridge/transfer" \
  -H "Content-Type: application/json" \
  -d '{
    "source_chain": "ethereum",
    "destination_chain": "polygon", 
    "token_address": "0x...",
    "amount": "100.0",
    "sender_address": "0x...",
    "recipient_address": "0x...",
    "security_level": "high"
  }'
```

### Get Transfer Status
```bash
curl "http://localhost:8000/api/v2/bridge/transfer/{transfer_id}"
```

### Add Liquidity
```bash
curl -X POST "http://localhost:8000/api/v2/liquidity/pools/{pool_id}/add" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1000.0",
    "token_address": "0x..."
  }'
```

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Run All Tests with Coverage
```bash
pytest --cov=scorpius_bridge tests/
```

## Configuration

Configuration is managed through environment variables with the `BRIDGE_` prefix. Key configurations include:

- **Database**: `BRIDGE_DATABASE_URL`
- **Redis**: `BRIDGE_REDIS_URL`
- **Blockchain RPCs**: `BRIDGE_ETHEREUM_RPC`, etc.
- **Security**: `BRIDGE_JWT_SECRET`, `BRIDGE_PRIVATE_KEY`
- **Operational**: `BRIDGE_MIN_VALIDATORS`, `BRIDGE_CONSENSUS_THRESHOLD`

See `.env.example` for a complete list of configuration options.

## Security Considerations

### Production Checklist
- [ ] Use Hardware Security Modules (HSM) for key management
- [ ] Enable TLS/SSL for all endpoints
- [ ] Configure proper CORS policies
- [ ] Set up rate limiting and DDoS protection
- [ ] Enable audit logging
- [ ] Regularly rotate JWT secrets
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable database encryption at rest
- [ ] Configure network security groups/firewalls

### Validator Security
- [ ] Multi-signature schemes for high-value transfers
- [ ] Slashing mechanisms for malicious behavior
- [ ] Reputation scoring system
- [ ] Geographic distribution requirements
- [ ] Stake requirements and bonding periods

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[License information here]

## Support

For technical support and questions:
- Documentation: [Link to docs]
- Issues: [Link to GitHub issues]
- Discord: [Link to Discord]
- Email: support@scorpius-bridge.com
