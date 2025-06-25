# Scorpius DeFi Security Platform - Architecture

## Introduction

Scorpius is an enterprise-grade DeFi security platform that provides comprehensive smart contract vulnerability scanning, MEV protection, and blockchain forensics. The platform is built as a microservices architecture with async Python backends, React frontend, and specialized Rust workers for high-performance blockchain operations.

## Service Map

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────��───────────┐
│   Frontend (React)  │    │  API Gateway        │    │  Authentication     │
│   - Dashboard       │────│  - FastAPI          │────│  - JWT Auth         │
│   - Analytics       │    │  - Rate Limiting    │    │  - RBAC             │
│   - Reports         │    │  - Load Balancer    │    │  - Session Mgmt     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Core Backend Services                              │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  Scanner Service    │  MEV Protection     │  Blockchain Analytics           │
│  - Slither          │  - Front-run detect │  - Transaction analysis         │
│  - Mythril          │  - Sandwich protect │  - Pattern recognition          │
│  - Custom rules     │  - MEV mitigation   │  - Risk assessment              │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Specialized Workers                                │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  Mempool Scanner    │  Oracle Monitor     │  Liquidation Monitor            │
│  (Rust -> Python)  │  (Rust -> Python)  │  (Rust -> Python)              │
│  - Real-time scan  │  - Price feeds      │  - Position tracking            │
│  - Pattern detect  │  - Deviation alerts │  - Risk calculation             │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Layer                                     │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│  PostgreSQL         │  Redis Cache        │  Time-Series DB                 │
│  - User data        │  - Sessions         │  - Metrics                      │
│  - Scan results     │  - Rate limits      │  - Performance data             │
│  - Audit logs       │  - Temp data        │  - Historical analysis          │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

## Data Flow

### 1. User Request Flow

```
User → Frontend → API Gateway → Authentication → Core Service → Database
  ↓                                                      ↓
Response ← Frontend ← API Gateway ← Authentication ← Core Service ← Database
```

### 2. Real-time Scanning Flow

```
Blockchain → Mempool Scanner (Rust) → Message Queue → Backend Service → Database
                                          ↓
                                    Alert System → WebSocket → Frontend
```

### 3. Analysis Pipeline

```
Smart Contract → Scanner Service → Analysis Engine → Risk Assessment → Report Generation
      ↓                                                      ↓
    Upload           Results stored in DB             PDF/JSON Export
```

## Deployment Topology

### Development Environment

```
┌───────���─────────────────────────────────────────────────────┐
│                    Docker Compose                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Frontend      │   Backend       │   Supporting Services   │
│   - Vite dev    │   - FastAPI     │   - PostgreSQL          │
│   - Hot reload  │   - Auto reload │   - Redis               │
│   - Port 8080   │   - Port 8000   │   - Prometheus          │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Frontend      │   Backend       │   Supporting Services   │
│   - 3 replicas  │   - 5 replicas  │   - PostgreSQL HA       │
│   - Nginx LB    │   - Auto-scale  │   - Redis Cluster       │
│   - CDN         │   - Health chks │   - Monitoring Stack    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Network Architecture

```
Internet → CDN → Load Balancer → API Gateway → Microservices
                      ↓                ↓
                 SSL Termination   Rate Limiting
                      ↓                ↓
                 WAF Protection    Authentication
```

## Core Services Detail

### 1. API Gateway (FastAPI)

- **Path**: `/backend/routes/`
- **Purpose**: Central API entry point with authentication and rate limiting
- **Key Files**:
  - `auth_fastapi.py` - Authentication endpoints
  - `scanner_routes.py` - Vulnerability scanning APIs
  - `mev_fastapi.py` - MEV protection APIs
  - `blockchain_forensics_fastapi.py` - Analysis APIs

### 2. Scanner Service

- **Path**: `/backend/routes/scanner_routes.py`
- **Purpose**: Smart contract vulnerability detection
- **Engines**:
  - Slither (static analysis)
  - Mythril (symbolic execution)
  - Custom rule engine
- **Output**: Vulnerability reports with severity scoring

### 3. MEV Protection Service

- **Path**: `/backend/mev_bot/`
- **Purpose**: Maximum Extractable Value detection and protection
- **Features**:
  - Front-running detection
  - Sandwich attack mitigation
  - MEV-resistant transaction ordering
  - Flashloan attack prevention

### 4. Time Machine Service

- **Path**: `/backend/time_machine/`
- **Purpose**: Historical blockchain analysis and transaction replay
- **Features**:
  - Fork state simulation
  - Transaction replay
  - Attack vector analysis
  - Forensic investigation tools

### 5. Bridge Service

- **Path**: `/backend/scorpius_bridge/`
- **Purpose**: Cross-chain asset bridging with security validation
- **Features**:
  - Multi-chain support
  - Atomic swaps
  - Liquidity pool management
  - Security validation

## Technology Stack

### Backend

- **Framework**: FastAPI (async Python 3.11+)
- **Database**: PostgreSQL with SQLModel/Alembic
- **Caching**: Redis
- **Task Queue**: Celery
- **Package Management**: Poetry
- **Containerization**: Docker

### Frontend

- **Framework**: React 18 with TypeScript
- **State Management**: Zustand
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **UI Components**: Radix UI
- **Testing**: Vitest + React Testing Library

### Workers

- **Language**: Rust (compiled to Python wheels)
- **Services**:
  - Mempool scanner
  - Oracle monitor
  - Liquidation monitor
- **Performance**: High-throughput, low-latency processing

### DevOps

- **CI/CD**: GitHub Actions
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with audit trails
- **Security**: Secret management, vulnerability scanning

## Extensibility Hooks

### 1. Plugin System

```python
# Plugin interface for custom vulnerability detectors
class VulnerabilityDetector:
    def analyze(self, contract: str) -> List[Vulnerability]:
        pass

    def get_severity(self, vuln: Vulnerability) -> Severity:
        pass
```

### 2. Custom Rules Engine

```python
# Rule definition for pattern matching
class SecurityRule:
    pattern: str
    severity: Severity
    description: str
    remediation: str
```

### 3. API Extensions

```python
# Custom API endpoints
@router.post("/custom-analysis")
async def custom_analysis(request: CustomRequest):
    # Implementation
    pass
```

### 4. Worker Extensions

```rust
// Rust worker trait for blockchain monitoring
trait BlockchainWorker {
    fn process_block(&self, block: Block) -> Result<Analysis>;
    fn handle_transaction(&self, tx: Transaction) -> Result<Alert>;
}
```

### 5. Frontend Component System

```typescript
// React component extension interface
interface CustomDashboard {
  render(): JSX.Element;
  handleData(data: any): void;
  getConfig(): DashboardConfig;
}
```

## Security Architecture

### Authentication & Authorization

- **JWT-based authentication** with RS256 signing
- **Role-based access control** (RBAC)
- **API key management** for service accounts
- **Multi-factor authentication** support

### Data Protection

- **Encryption at rest** for sensitive data
- **TLS 1.3** for all communications
- **Key management** with HSM integration
- **Data classification** by sensitivity

### Network Security

- **Private container networks**
- **Rate limiting** and DDoS protection
- **Web Application Firewall** (WAF)
- **Network segmentation**

## Performance Characteristics

### Scalability Targets

- **API Throughput**: >1000 RPS
- **Response Time**: <200ms P95
- **Concurrent Users**: >10,000
- **Data Processing**: >1M transactions/day

### Resource Requirements

- **CPU**: Multi-core for parallel processing
- **Memory**: 16GB+ for large contract analysis
- **Storage**: SSD for database performance
- **Network**: High bandwidth for blockchain sync

## Monitoring & Observability

### Metrics Collection

- **Application metrics**: Response times, error rates
- **Infrastructure metrics**: CPU, memory, disk usage
- **Business metrics**: Scan volume, threat detection
- **Security metrics**: Failed auth, anomalies

### Alerting

- **Critical alerts**: Security incidents, system failures
- **Warning alerts**: Performance degradation, high load
- **Info alerts**: Deployment completion, maintenance

### Logging

- **Structured logging** with JSON format
- **Audit trails** for compliance
- **Error tracking** with stack traces
- **Performance profiling**

## Development Workflow

### Local Development

1. **Setup**: `just dev` (spins up entire stack)
2. **Testing**: `just test` (runs test suite)
3. **Linting**: `just lint` (code quality checks)
4. **Database**: `just reset-db` (reset local DB)

### Code Quality Gates

- **Pre-commit hooks**: Linting, formatting, security
- **CI Pipeline**: Tests, coverage, security scan
- **Code Review**: Required for all changes
- **Deployment**: Automated for main branch

## Disaster Recovery

### Backup Strategy

- **Database**: Daily automated backups
- **Code**: Git repository mirroring
- **Configurations**: Infrastructure as Code
- **Secrets**: Encrypted backup storage

### Recovery Procedures

- **RTO** (Recovery Time Objective): <1 hour
- **RPO** (Recovery Point Objective): <15 minutes
- **Failover**: Automated to secondary region
- **Data Recovery**: Point-in-time restoration

---

## Quick Start Guide

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Setup Commands

```bash
# Clone repository
git clone <repo-url>
cd newScorp

# Start development environment
just dev

# Run tests
just test

# Access applications
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Total setup time: ≤15 minutes**

---

_Architecture diagram: `docs/architecture.drawio` (PNG export included)_
