# MevGuardian Enterprise Security Platform

**Transform MEV bots from predatory extraction to defensive protection**

MevGuardian is an enterprise-grade blockchain security platform that uses MEV techniques for threat detection, simulation, and protection rather than profit extraction.

## 🛡️ Core Mission

Transform traditional MEV bot architecture from predatory extraction to defensive protection, providing:
- Real-time threat detection and early warning systems
- Safe attack simulation in forked environments  
- Comprehensive mempool surveillance across multiple chains
- Advanced honeypot and scam detection
- Forensic analysis and attack pattern recognition

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MevGuardian Platform                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Dashboard (React/Vite)                           │
│  ├── Attack Dashboard (Traditional MEV)                    │
│  └── Defense Dashboard (Guardian Mode)                     │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (FastAPI)                                     │
│  ├── REST Endpoints                                        │
│  ├── WebSocket Streaming                                   │
│  └── GraphQL (Optional)                                    │
├─────────────────────────────────────────────────────────────┤
│  Core Guardian Engine                                       │
│  ├── Threat Simulation Engine                              │
│  ├── Mempool Surveillance System                           │
│  ├── Honeypot Detection Matrix                             │
│  ├── Economic Exploit Discovery                            │
│  └── Forensic Time Machine                                 │
├─────────────────────────────────────────────────────────────┤
│  Traditional MEV Engine                                     │
│  ├── Flash Loan Arbitrage                                  │
│  ├── Sandwich Attacks                                      │
│  ├── Liquidation Bot                                       │
│  ├── Cross-Chain Arbitrage                                 │
│  └── Oracle Manipulation                                   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── Multi-Chain Scanner (3k+ tx/s)                        │
│  ├── Database (PostgreSQL + Redis)                         │
│  ├── Message Queue (Redis Streams)                         │
│  └── Monitoring & Metrics                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone and Setup**
```bash
git clone <repository>
cd mev_bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Docker Deployment**
```bash
# Full stack with databases
docker-compose up -d

# Development mode (external DBs)
docker-compose -f docker-compose.dev.yml up -d
```

4. **Database Setup**
```bash
# Run migrations
python scripts/setup_database.py

# Seed with test data
python scripts/seed_data.py
```

## 📡 API Endpoints

### Guardian Mode (Defense)
```
GET     /api/v1/guardian/status              # Guardian system status
GET     /api/v1/guardian/threats             # Recent threats detected
GET     /api/v1/guardian/simulations         # Attack simulations
POST    /api/v1/guardian/simulate            # Run threat simulation
GET     /api/v1/guardian/honeypots           # Honeypot detections
GET     /api/v1/guardian/forensics           # Forensic analysis results
WebSocket /ws/guardian/live                  # Real-time threat feed
```

### Attack Mode (Traditional MEV)
```
GET     /api/v1/mev/status                   # MEV bot status
GET     /api/v1/mev/strategies               # Active strategies
POST    /api/v1/mev/strategies/{id}/toggle   # Enable/disable strategy
GET     /api/v1/mev/opportunities            # Recent opportunities
GET     /api/v1/mev/executions               # Execution history
WebSocket /ws/mev/live                       # Real-time MEV feed
```

### System Management
```
GET     /api/v1/system/health                # Health check
GET     /api/v1/system/metrics               # Performance metrics
POST    /api/v1/system/mode                  # Switch between modes
GET     /api/v1/system/config                # Configuration
```

## 🛡️ Guardian Mode Features

### 1. Threat Simulation Engine
- **Safe Testing Environment**: Fork mainnet for risk-free attack simulation
- **Attack Vector Testing**: Sandwich attacks, oracle manipulation, flash loan exploits
- **Protocol Stress Testing**: Evaluate resilience under adversarial conditions
- **Economic Threshold Analysis**: Determine protocol breaking points

### 2. Real-Time Mempool Surveillance
- **Multi-Chain Monitoring**: Ethereum, Arbitrum, Polygon, BSC
- **Bot Swarm Detection**: Identify coordinated attack patterns
- **Whale Movement Tracking**: Monitor large transactions and liquidations
- **Gas Price Anomalies**: Detect unusual network congestion patterns

### 3. Honeypot & Scam Detection
- **Transaction Pattern Analysis**: Detect revert patterns and gas griefing
- **Token Risk Scoring**: Dynamic risk assessment for new tokens
- **Rugpull Detection**: Identify suspicious liquidity patterns
- **Smart Contract Analysis**: Static analysis for malicious code patterns

### 4. Economic Exploit Discovery
- **Oracle Lag Exploitation**: Detect arbitrage windows from price delays
- **Liquidity Pool Analysis**: Identify mispriced pools and drainage vectors
- **Bridge Vulnerability Scanning**: Cross-chain inconsistency monitoring
- **DeFi Protocol Monitoring**: Track parameter changes and exploits

### 5. Forensic Time Machine
- **Attack Reconstruction**: Replay historical attacks with precise ordering
- **Pattern Database**: Machine learning training from past exploits
- **Reverse Engineering**: Analyze attacker strategies and optimizations
- **Impact Assessment**: Calculate maximum extractable value for incidents

## ⚔️ Attack Mode Features

### Traditional MEV Strategies
- **Flash Loan Arbitrage**: Real-time DEX price difference exploitation
- **Sandwich Attacks**: Front/back-running vulnerable transactions
- **Liquidation Bot**: Monitor undercollateralized positions
- **Cross-Chain Arbitrage**: Exploit price differences across chains
- **Oracle Manipulation**: Leverage price feed delays and inconsistencies

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
MODE=guardian                    # 'guardian' or 'attack' or 'hybrid'
DEBUG=false
LOG_LEVEL=INFO

# Blockchain Configuration
RPC_URL_ETHEREUM=https://...
RPC_URL_POLYGON=https://...
RPC_URL_ARBITRUM=https://...
PRIVATE_KEY=0x...               # Only for attack mode

# Database Configuration
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# External Services
FLASHBOTS_RELAY=https://relay.flashbots.net
TENDERLY_ACCESS_KEY=...
ALCHEMY_API_KEY=...

# Guardian Specific
THREAT_DETECTION_THRESHOLD=0.8
SIMULATION_FORK_BLOCKS=100
HONEYPOT_SCAN_INTERVAL=30

# Attack Specific (if enabled)
MEV_PROFIT_THRESHOLD=0.01
MAX_GAS_PRICE_GWEI=100
FLASHLOAN_PROVIDERS=aave,maker,dydx
```

### Guardian Configuration
```yaml
# guardian_config.yml
guardian:
  mode: "passive"  # passive, active, simulation
  threat_detection:
    confidence_threshold: 0.8
    alert_channels: ["discord", "telegram", "webhook"]
  simulation:
    fork_provider: "tenderly"
    max_concurrent_sims: 5
    cleanup_after_hours: 24
  monitoring:
    chains: [1, 137, 42161, 56]
    protocols: ["uniswap", "aave", "compound", "makerdao"]
```

## 🐳 Docker Support

### Production Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  mev-guardian:
    build: .
    environment:
      - MODE=guardian
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
```

### Development
```bash
# Local development with hot reload
docker-compose -f docker-compose.dev.yml up
```

## 📊 Monitoring & Metrics

### Prometheus Metrics
- `mev_guardian_threats_detected_total`
- `mev_guardian_simulations_executed_total`
- `mev_guardian_honeypots_identified_total`
- `mev_bot_opportunities_found_total`
- `mev_bot_execution_success_rate`

### Health Checks
```bash
curl http://localhost:8000/health
{
  "status": "healthy",
  "mode": "guardian",
  "uptime": 3600,
  "version": "1.0.0"
}
```

## 🔒 Security Considerations

### Guardian Mode
- **No Live Transactions**: All operations are read-only or simulation-based
- **API Rate Limiting**: Prevent abuse of threat detection endpoints
- **Data Encryption**: Sensitive threat intelligence encrypted at rest
- **Access Control**: Role-based access to different threat levels

### Attack Mode
- **Private Key Management**: KMS integration for production
- **Transaction Limits**: Maximum value and gas price protections
- **Emergency Stop**: Immediate shutdown capabilities
- **Audit Logging**: Complete transaction and decision logging

## 🚨 Responsible Disclosure

MevGuardian follows responsible disclosure practices:
- Threats detected are reported to affected protocols
- Critical vulnerabilities shared through secure channels
- Public disclosure only after remediation periods
- Collaboration with security researchers and white hat communities

## 📚 Frontend Integration

### WebSocket Events
```typescript
// Guardian Mode Events
interface GuardianEvent {
  type: 'threat_detected' | 'simulation_complete' | 'honeypot_found';
  timestamp: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  data: any;
}

// Attack Mode Events  
interface MEVEvent {
  type: 'opportunity_found' | 'execution_complete' | 'strategy_status';
  strategy: string;
  profit?: number;
  data: any;
}
```

### REST API Examples
```typescript
// Get threat status
const threats = await fetch('/api/v1/guardian/threats');

// Start simulation
const simulation = await fetch('/api/v1/guardian/simulate', {
  method: 'POST',
  body: JSON.stringify({
    attack_type: 'sandwich',
    target_protocol: 'uniswap_v3',
    simulation_params: {...}
  })
});
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

MevGuardian is designed for security research and protection. The attack mode capabilities are intended for educational purposes and authorized security testing only. Users are responsible for compliance with applicable laws and regulations.

---

**Built with enterprise security in mind** 🛡️
