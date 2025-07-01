# Enterprise Honeypot Detector

A production-ready, enterprise-grade smart contract honeypot detector combining multiple detection engines (symbolic execution, machine learning, static analysis) to identify malicious smart contracts on EVM-compatible blockchains.

## Features

- **Multi-Engine Detection**: Combines symbolic execution, machine learning, and static analysis for comprehensive detection
- **Multi-Chain Support**: Works with Ethereum, BSC, and other EVM-compatible blockchains
- **Enterprise-Ready Architecture**:
  - Microservices with API and worker components
  - Scalable MongoDB storage
  - Redis-based caching and task queueing
  - Docker containerization
  - Prometheus/Grafana monitoring
- **Comprehensive API**: REST API with FastAPI, input validation, authentication, and rate limiting
- **Advanced Detection Techniques**:
  - Bytecode pattern analysis
  - Transaction history monitoring
  - Machine learning classification
  - Symbolic execution for control flow analysis
  - Source code heuristics
- **Security Features**:
  - API Key authentication
  - Rate limiting
  - Input validation
  - CORS protection

## Architecture

The system is built on a microservices architecture with these components:

1. **API Service**: FastAPI application handling HTTP requests
2. **Worker Service**: Celery workers for background processing of contract analysis
3. **MongoDB**: Scalable storage for analysis results and contract data
4. **Redis**: For caching, task queueing, and distributed rate limiting
5. **Monitoring Stack**: Prometheus and Grafana for observability

## Detection Engines

- **Static Analysis Engine**: Detects honeypot patterns using regular expressions, bytecode analysis, and source code heuristics
- **Machine Learning Engine**: Uses RandomForestClassifier trained on contract features to predict honeypot probability
- **Symbolic Execution Engine**: Performs control flow analysis to detect malicious logic paths in contracts
- **Transaction Analyzer**: Examines transaction patterns to identify suspicious behavior

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- MongoDB 7+
- Redis 7+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/honeypot-detector.git
   cd honeypot-detector
   ```

2. Create and configure the `.env` file (or run the setup script):
   ```bash
   python scripts/setup.py
   ```

3. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the API at `http://localhost:8000`

### Manual Setup (Without Docker)

1. Install dependencies:
   ```bash
   pip install -r config/config/requirements-dev.txt
   ```

2. Run the setup script:
   ```bash
   python scripts/setup.py
   ```

3. Start the API server:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

4. Start the Celery worker:
   ```bash
   celery -A core.worker worker --loglevel=info
   ```

## API Documentation

API documentation is available at `/docs` when running the service with `DEBUG=True`.

### Key Endpoints

- `GET /health/live`: Liveness probe
- `GET /health/ready`: Readiness probe
- `GET /health/status`: Detailed system status
- `POST /api/v1/analysis/contract`: Submit a contract for analysis
- `GET /api/v1/analysis/contract/{address}/{chain_id}`: Get analysis results
- `GET /api/v1/analysis/statistics`: Get system-wide statistics

### Authentication

All API endpoints require an API key, passed in the `X-API-Key` header.

## Configuration

Configuration is managed through environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| API_KEY | API authentication key | Auto-generated |
| ALLOWED_ORIGINS | CORS allowed origins | ["*"] |
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017 |
| DATABASE_NAME | MongoDB database name | honeypot_detector |
| ETHEREUM_RPC_URL | Ethereum RPC URL | https://eth-mainnet.g.alchemy.com/v2/your-key |
| BSC_RPC_URL | BSC RPC URL | https://bsc-dataseed.binance.org/ |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |

## Development

### Project Structure

```
honeypot-detector/
├── api/
│   ├── middleware/         # Authentication and rate limiting
│   └── routes/             # API endpoints
├── blockchain/             # Blockchain integration
├── config/                 # Application configuration
├── core/
│   ├── analyzers/          # Contract analyzers
│   └── engines/            # Detection engines
├── database/
│   └── repositories/       # Data access layer
├── docker/                 # Docker configuration
├── models/                 # ML models and data models
├── scripts/                # Utility scripts
└── tests/                  # Test cases
```

### Running Tests

```bash
pytest
```

## Monitoring

The system includes Prometheus metrics and Grafana dashboards. When running with Docker Compose:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default login: admin/securepassword)

## License

[MIT License](LICENSE)

## Acknowledgments

- [Web3.py](https://github.com/ethereum/web3.py)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Z3 Theorem Prover](https://github.com/Z3Prover/z3)
- [Scikit-learn](https://scikit-learn.org/)
