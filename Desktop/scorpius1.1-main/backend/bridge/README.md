# 🌉 Scorpius Bridge Network

**Enterprise-grade cross-chain interoperability system** with real-time WebSocket API and gRPC services, built for Vite + React dashboard integration.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-enabled-orange.svg)]()
[![gRPC](https://img.shields.io/badge/gRPC-ready-purple.svg)]()
[![Docker](https://img.shields.io/badge/Docker-production--ready-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Key Features

### Core Bridge Functionality
- **🌉 Cross-Chain Bridge**: Seamless asset transfers between blockchains
- **⚛️ Atomic Swaps**: Trustless peer-to-peer exchanges
- **✅ Validator Network**: Decentralized validation and consensus
- **💧 Liquidity Pools**: Automated market making and fee optimization

### Real-Time Integration
- **🔄 WebSocket API**: Live events for dashboard integration
- **📡 gRPC Services**: High-performance binary protocol
- **📊 Live Statistics**: Real-time metrics and monitoring
- **🎯 Event Streaming**: Transaction and validator updates

### Enterprise Features  
- **🔒 Security-First**: Multi-signature validation, JWT auth, audit logging
- **⚡ High Performance**: Async/await architecture, Redis caching, event-driven design
- **🔧 Developer Experience**: Type safety, auto-generated API docs, comprehensive testing
- **📊 Observability**: Prometheus metrics, structured logging, distributed tracing
- **🏗️ Production Ready**: Docker deployment, CI/CD pipelines, monitoring dashboards

## 🏛️ Architecture Overview

```
scorpius_bridge/                     # 🚀 Python package root
│
├─ config/                          # ⚙️ 12-factor settings
│   ├─ settings.py                  # Pydantic BaseSettings – env-driven, namespaced
│   ├─ logging.yaml                 # Central log format (JSON-ready)
│   └─ secrets.toml.example         # Redacted template for private keys, DB creds
│
├─ api/                             # 🌐 transport adapters
│   ├─ http/                        # FastAPI routers go here
│   │   ├─ dependencies.py          # auth, rate-limit, DB session injection
│   │   ├─ routers/                 # versioned route groups
│   │   │   ├─ v1.py
│   │   │   └─ v2.py
│   │   └─ schemas/                 # Pydantic request/response DTOs
│   ├─ websocket/                   # Real-time feeds (e.g. order-book, event stream)
│   └─ grpc/                        # gRPC service defs + generated stubs
│
├─ domain/                          # 🧠 pure DDD territory (no frameworks!)
│   ├─ models/                      # core entities & value objects
│   │   ├─ bridge_tx.py
│   │   └─ validator.py
│   ├─ events.py                    # domain events (e.g. LiquidityAdded)
│   ├─ policy.py                    # rules & invariants
│   └─ errors.py                    # custom exceptions
│
├─ application/                     # 🔨 use-case orchestration
│   ├─ commands.py                  # "write" side CQRS commands
│   ├─ queries.py                   # "read" side CQRS queries
│   └─ services/                    # thin orchestrators → domain objects
│       ├─ bridge_service.py
│       └─ liquidity_service.py
│
├─ infrastructure/                  # 🏗️ outer-layer integrations
│   ├─ blockchain/                  # chain-specific RPC clients
│   │   ├─ ethereum.py
│   │   └─ solana.py
│   ├─ persistence/                 # Repo pattern + migrations
│   │   ├─ models_sql.py            # SQLModel / SQLAlchemy tables
│   │   ├─ repository.py            # generic CRUD wrapper
│   │   └─ alembic/                 # DB migrations
│   ├─ messaging/                   # Kafka / NATS / Rabbit adapters
│   ├─ caching/                     # Redis, Memcached, in-proc
│   └─ tasks/                       # Celery/RQ/Arq async jobs
│
├─ adapters/                        # existing code you already have
│   ├─ atomic_swaps/
│   ├─ liquidity_pools/
│   └─ validators/
│
├─ tests/                           # ✅ pytest (unit → integration → contract)
│   ├─ conftest.py
│   ├─ unit/
│   ├─ integration/
│   └─ contract/
│
└─ docs/                            # 📚 MkDocs / Sphinx source
    └─ architecture.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd scorpius_bridge

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Infrastructure
```bash
# Start PostgreSQL, Redis, and Kafka
docker-compose up -d postgres redis kafka
```

### 3. Install Dependencies
```bash
pip install -r config/config/requirements-dev.txt
```

### 4. Database Setup
```bash
# Run migrations
alembic upgrade head
```

### 5. Launch API
```bash
# Development server with auto-reload
uvicorn scorpius_bridge.main:app --reload

# Production server
uvicorn scorpius_bridge.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 📡 API Examples

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

### Add Liquidity to Pool
```bash
curl -X POST "http://localhost:8000/api/v2/liquidity/pools/{pool_id}/add" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1000.0",
    "token_address": "0x..."
  }'
```

### Register Validator
```bash
curl -X POST "http://localhost:8000/api/v2/validators/register" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x...",
    "public_key": "0x...",
    "stake_amount": "10000.0",
    "supported_chains": ["ethereum", "polygon"]
  }'
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=scorpius_bridge tests/

# Generate coverage report
pytest --cov=scorpius_bridge --cov-report=html tests/
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up
```

### Production
```bash
# Build production image
docker build -t scorpius-bridge:latest .

# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

The system includes comprehensive monitoring out of the box:

- **Prometheus**: Metrics collection at `/metrics`
- **Grafana**: Dashboards for visualization (port 3000)
- **Health Checks**: Component status at `/health`
- **Structured Logging**: JSON logs for observability

## 🔐 Security Features

### Multi-Layer Security
- **Cryptographic Signatures**: Multi-signature validation
- **Rate Limiting**: API endpoint protection
- **Authentication**: JWT-based with role validation
- **Audit Logging**: Comprehensive operation tracking
- **Input Validation**: Pydantic schema validation

### Production Security Checklist
- [ ] HSM integration for key management
- [ ] TLS/SSL configuration
- [ ] Secrets management (Vault/AWS Secrets Manager)
- [ ] Network security groups
- [ ] Database encryption at rest
- [ ] Regular security audits

## 🔧 Configuration

Configuration is environment-driven using the `BRIDGE_` prefix:

```bash
# Database
BRIDGE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Blockchain RPCs
BRIDGE_ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_KEY
BRIDGE_POLYGON_RPC=https://polygon-mainnet.infura.io/v3/YOUR_KEY

# Security
BRIDGE_JWT_SECRET=your-secret-key
BRIDGE_MIN_VALIDATORS=5
BRIDGE_CONSENSUS_THRESHOLD=0.67

# Operational
BRIDGE_BASE_BRIDGE_FEE_PERCENTAGE=0.003
BRIDGE_MAX_TRANSFER_AMOUNT=1000000.0
```

See `.env.example` for complete configuration options.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Documentation](http://localhost:8000/docs)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 📈 Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Domain model implementation
- [x] API layer with FastAPI
- [x] Database integration
- [x] Basic security features

### Phase 2: Advanced Features 🚧
- [ ] WebSocket real-time feeds
- [ ] gRPC service implementation
- [ ] Advanced monitoring dashboards
- [ ] Load balancer integration

### Phase 3: Enterprise Features 📋
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] Mobile SDK
- [ ] Governance features

## 🆘 Support

- **Documentation**: [Link to comprehensive docs]
- **Issues**: [GitHub Issues](https://github.com/scorpius-bridge/issues)
- **Discord**: [Community Discord](https://discord.gg/scorpius)
- **Email**: support@scorpius-bridge.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ using:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [SQLModel](https://sqlmodel.tiangolo.com/) - Database ORM
- [Docker](https://www.docker.com/) - Containerization
- [Prometheus](https://prometheus.io/) - Monitoring

---

**Ready to bridge the future of DeFi? Let's build! 🚀**
