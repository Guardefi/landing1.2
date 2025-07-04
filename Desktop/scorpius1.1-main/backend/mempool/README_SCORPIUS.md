# SCORPIUS MEMPOOL MONITORING - Elite System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Guardefi/SCORPIUS-MEMPOOL-MONITORING)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)

## 🎯 Overview

The **SCORPIUS Elite Mempool Monitoring System** is an enterprise-grade, real-time blockchain mempool monitoring and MEV detection platform built for institutional use.

### 🚀 Key Features

- **Real-time Mempool Monitoring**: Monitor pending transactions across multiple blockchain networks
- **MEV Detection & Analysis**: Detect arbitrage, sandwich attacks, and liquidation opportunities
- **Multi-chain Support**: Ethereum, Polygon, BSC, Arbitrum, and more
- **Enterprise APIs**: RESTful APIs with WebSocket real-time feeds
- **Advanced Analytics**: Transaction pattern analysis and profitability calculations
- **Production Ready**: Docker containerization with horizontal scaling support

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web3 Nodes    │    │  FastAPI Server │    │   PostgreSQL    │
│  (Multi-chain)  │────│   (REST/WS)     │────│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Monitoring    │
                       │    (Cache)      │    │  (Prometheus)   │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 15+ with Redis caching
- **Blockchain**: Web3.py with multi-provider support
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest with async support

## 📦 Installation

### Quick Start with Docker

```bash
# Clone the repository
git clone git@github.com:Guardefi/SCORPIUS-MEMPOOL-MONITORING.git
cd SCORPIUS-MEMPOOL-MONITORING

# Copy environment configuration
cp .env.example .env
# Edit .env with your RPC URLs and configuration

# Start the full stack
docker-compose up -d

# Check system health
curl http://localhost:8000/health
```

### Local Development

```bash
# Install dependencies
pip install -r config/config/requirements-dev.txt

# Set up database
docker-compose up -d postgres redis

# Start the API server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Configuration

### Environment Variables

```env
# Blockchain RPC URLs
ETHEREUM_RPC_URL=wss://mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID
POLYGON_RPC_URL=wss://polygon-mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5433/elite_mempool
REDIS_URL=redis://localhost:6380

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
JWT_SECRET=your-super-secret-jwt-key

# MEV Configuration
FLASHBOTS_RPC_URL=https://rpc.flashbots.net
BOT_PRIVATE_KEY=your_bot_private_key_here
```

## 📚 API Documentation

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health

### Transaction Monitoring
- `GET /api/v1/transactions` - List pending transactions
- `GET /api/v1/transactions/{hash}` - Get transaction details
- `POST /api/v1/transactions/filter` - Filter transactions by criteria

### MEV Analysis
- `GET /api/v1/mev/opportunities` - List MEV opportunities
- `GET /api/v1/mev/patterns` - Detected MEV patterns
- `POST /api/v1/mev/analyze` - Analyze transaction for MEV

### Real-time WebSocket
- `WS /ws/transactions` - Live transaction feed
- `WS /ws/mev` - Live MEV opportunity feed

### Interactive API Documentation
Visit `http://localhost:8000/docs` for full Swagger/OpenAPI documentation.

## 🔍 Core Features

### 1. Real-time Mempool Monitoring

```python
from core.enhanced_mempool_monitor import EnhancedMempoolMonitor

# Initialize monitor
monitor = EnhancedMempoolMonitor()

# Start monitoring
await monitor.start_monitoring()

# Set filters
monitor.set_min_value_filter(1.0)  # 1 ETH minimum
monitor.add_contract_filter("0x...")  # Specific contract
```

### 2. MEV Detection

```python
from mev_analysis.mev_detector import detect_mev_patterns

# Detect MEV opportunities
opportunities = await detect_mev_patterns(pending_transactions)

for opportunity in opportunities:
    print(f"Type: {opportunity.strategy_type}")
    print(f"Profit: ${opportunity.estimated_profit_usd}")
    print(f"Confidence: {opportunity.confidence_score}")
```

### 3. WebSocket Real-time Feeds

```javascript
// Connect to transaction feed
const ws = new WebSocket('ws://localhost:8000/ws/transactions');

ws.onmessage = function(event) {
    const transaction = JSON.parse(event.data);
    console.log('New transaction:', transaction);
};
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 🚀 Deployment

### Production Docker Deployment

```bash
# Build production image
docker build -t scorpius-mempool-monitoring .

# Run with production configuration
docker run -d \
  --name mempool-monitor \
  -p 8000:8000 \
  --env-file .env.production \
  scorpius-mempool-monitoring
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mempool-monitor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mempool-monitor
  template:
    metadata:
      labels:
        app: mempool-monitor
    spec:
      containers:
      - name: api
        image: scorpius-mempool-monitoring:latest
        ports:
        - containerPort: 8000
```

## 📊 Monitoring & Observability

### Metrics
- Transaction processing rate
- MEV opportunity detection rate
- API response times
- Database connection health

### Grafana Dashboards
- Real-time transaction volume
- MEV opportunity trends
- System performance metrics
- Alert management

## 🔐 Security

- **API Authentication**: JWT-based authentication
- **Rate Limiting**: Request rate limiting per user
- **Input Validation**: Comprehensive request validation
- **Security Headers**: CORS, CSRF protection
- **Container Security**: Non-root user, minimal attack surface

## 📈 Performance

- **High Throughput**: Process 1000+ transactions/second
- **Low Latency**: Sub-100ms API response times
- **Horizontal Scaling**: Redis clustering support
- **Efficient Storage**: Optimized PostgreSQL schema

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/Guardefi/SCORPIUS-MEMPOOL-MONITORING/wiki)
- **Issues**: [GitHub Issues](https://github.com/Guardefi/SCORPIUS-MEMPOOL-MONITORING/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Guardefi/SCORPIUS-MEMPOOL-MONITORING/discussions)

---

**Built with ❤️ by the Guardefi Team**

[![Guardefi](https://img.shields.io/badge/Guardefi-blockchain--security-blue)](https://guardefi.com)
