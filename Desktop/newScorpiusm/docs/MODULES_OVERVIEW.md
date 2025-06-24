# Scorpius Dashboard - Modules Overview

This document provides a comprehensive overview of all modules available in the Scorpius blockchain security dashboard.

## 🏠 Dashboard Module

**Location**: `src/pages/DashboardPage.tsx`
**API Endpoint**: `/api/dashboard/*`
**Status**: ✅ Active

### Features

- **System Overview**: Real-time system health and status
- **Quick Stats**: Key metrics from all modules at a glance
- **Module Navigation**: Quick access to all security tools
- **Activity Summary**: Recent alerts, scans, and activities

### Key Metrics Displayed

- Total vulnerabilities detected
- Active MEV strategies
- Guardian alerts count
- System uptime and health

---

## 🔍 Scanner Module

**Location**: `src/pages/ScannerPage.tsx`
**API Endpoint**: `/api/scanner/*`
**Status**: ✅ Active

### Features

- **Smart Contract Analysis**: Deep vulnerability scanning
- **Multiple Scan Types**: Quick scan, deep analysis, custom parameters
- **Real-time Results**: Live scanning progress and results
- **Vulnerability Database**: Known vulnerabilities and exploits
- **Risk Assessment**: Severity scoring and impact analysis

### Supported Vulnerabilities

- Reentrancy attacks
- Integer overflow/underflow
- Access control issues
- Gas limit problems
- Logic bugs and more

---

## 📊 Mempool Monitor

**Location**: `src/pages/MempoolPage.tsx`
**API Endpoint**: `/api/mempool/*`
**Status**: ✅ Active

### Features

- **Live Transaction Monitoring**: Real-time mempool analysis
- **MEV Opportunity Detection**: Automated MEV detection
- **Gas Price Tracking**: Current and historical gas prices
- **Transaction Analysis**: Detailed transaction breakdown
- **Network Statistics**: Blockchain network health metrics

### Key Capabilities

- Front-running detection
- Sandwich attack identification
- Arbitrage opportunities
- Liquidation monitoring

---

## 🧬 Bytecode Analyzer

**Location**: `src/pages/BytecodePage.tsx`
**API Endpoint**: `/api/bytecode/*`
**Status**: ✅ Active

### Features

- **Bytecode Decompilation**: Convert bytecode to readable format
- **Control Flow Analysis**: Function flow and logic analysis
- **Pattern Recognition**: Known attack pattern detection
- **Assembly View**: Low-level bytecode inspection
- **Comparative Analysis**: Compare multiple contracts

### Analysis Types

- Static analysis
- Dynamic analysis
- Symbolic execution
- Pattern matching

---

## ⏰ Time Machine

**Location**: `src/pages/TimeMachinePage.tsx`
**API Endpoint**: `/api/time-machine/*`
**Status**: ✅ Active

### Features

- **Historical Replay**: Replay past blockchain states
- **Transaction Tracing**: Trace transaction execution
- **State Analysis**: Analyze contract states at specific blocks
- **Fork Simulation**: Create and analyze blockchain forks
- **Debug Mode**: Step-through debugging capabilities

### Use Cases

- Incident investigation
- Attack vector analysis
- State corruption debugging
- Performance analysis

---

## 🧪 Simulation Engine

**Location**: `src/pages/SimulationPage.tsx`
**API Endpoint**: `/api/simulation/*`
**Status**: ✅ **Recently Enabled**

### Features

- **Exploit Simulation**: Simulate various attack scenarios
- **Environment Management**: Create isolated test environments
- **AI-Powered Analysis**: Machine learning-based exploit detection
- **Scenario Testing**: Custom attack scenario creation
- **Impact Assessment**: Quantify potential damage

### Simulation Types

- Flash loan attacks
- Governance attacks
- Oracle manipulation
- MEV extraction scenarios

---

## ⚡ MEV Operations

**Location**: `src/pages/MevOpsPage.tsx`
**API Endpoint**: `/api/mev-ops/*`
**Status**: ✅ **Recently Enabled**

### Features

- **Strategy Management**: Create and manage MEV strategies
- **Live Opportunities**: Real-time MEV opportunity detection
- **Execution Engine**: Automated MEV execution
- **Profit Tracking**: Track MEV profits and performance
- **Risk Management**: Position sizing and risk controls

### Strategy Types

- Arbitrage
- Liquidation
- Sandwich attacks
- Front-running
- Back-running

### Configuration Options

- Auto-execution settings
- Profit thresholds
- Gas price limits
- Slippage tolerance
- Wallet management

---

## 🛡️ MEV Guardians

**Location**: `src/pages/MevGuardiansPage.tsx`
**API Endpoint**: `/api/mev-guardians/*`
**Status**: ✅ **Recently Enabled**

### Features

- **Real-time Protection**: Active MEV attack protection
- **Guardian Nodes**: Distributed protection network
- **Alert System**: Instant threat notifications
- **Protection Strategies**: Configurable defense mechanisms
- **Threat Intelligence**: Community-driven threat data

### Protection Types

- Front-running protection
- Sandwich attack mitigation
- MEV extraction prevention
- Transaction ordering protection

### Alert Categories

- Critical threats
- Warning indicators
- Informational notices
- System status updates

---

## 🍯 Honeypot Detector

**Location**: `src/pages/HoneypotPage.tsx`
**API Endpoint**: `/api/honeypot/*`
**Status**: ✅ Active

### Features

- **Smart Contract Analysis**: Detect honeypot contracts
- **Token Verification**: Verify token contract legitimacy
- **Risk Assessment**: Comprehensive risk scoring
- **Pattern Recognition**: Known honeypot patterns
- **Community Database**: Crowdsourced honeypot reports

### Detection Methods

- Static code analysis
- Dynamic behavior analysis
- Community reports
- Machine learning models

---

## 📋 Reports Module

**Location**: `src/pages/ReportsPage.tsx`
**API Endpoint**: `/api/reports/*`
**Status**: ✅ Active

### Features

- **Automated Reports**: Scheduled security reports
- **Custom Reports**: User-defined report templates
- **Multi-format Export**: PDF, JSON, CSV export options
- **Historical Data**: Long-term trend analysis
- **Compliance Reports**: Regulatory compliance documentation

### Report Types

- Security assessments
- MEV analysis reports
- Vulnerability summaries
- Performance analytics
- Incident reports

---

## ⚙️ Settings Module

**Location**: `src/pages/SettingsPage.tsx`
**API Endpoint**: `/api/settings/*`
**Status**: ✅ Active

### Features

- **General Settings**: Application preferences
- **Notification Settings**: Alert and notification preferences
- **API Configuration**: External API integrations
- **Security Settings**: Authentication and security options
- **Appearance**: Theme and UI customization

### Configuration Categories

- System preferences
- Alert thresholds
- API endpoints
- User preferences
- Module settings

---

## 🔧 Technical Architecture

### Frontend Stack

- **React 18** with TypeScript
- **Vite** for building and development
- **Tailwind CSS** for styling
- **Radix UI** for components
- **React Router** for navigation
- **TanStack Query** for data fetching

### Backend Stack

- **FastAPI** (Python) for API server
- **Uvicorn** ASGI server
- **WebSocket** support for real-time updates
- **RESTful API** design
- **CORS** enabled for frontend integration

### Real-time Features

- WebSocket connections for live updates
- Real-time transaction monitoring
- Live alert notifications
- Dynamic data refreshing

### Security Features

- Input validation
- CORS protection
- Rate limiting ready
- Error handling
- Secure API design

---

## 🚀 Getting Started

1. **Start Backend**: `cd backend/backend && python main.py`
2. **Start Frontend**: `npm run dev`
3. **Access Dashboard**: http://localhost:3000
4. **API Documentation**: http://localhost:8000/docs

All modules are now **fully integrated** with live backend data and ready for use!
