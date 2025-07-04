# 🚀 Scorpius Enterprise Platform - Quick Start Guide

This guide will get you up and running with the complete Scorpius Enterprise platform in just a few minutes.

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **8GB+ RAM** recommended for full platform
- **PowerShell** (Windows) or **Bash** (Linux/Mac)

## 🎯 One-Command Startup

We've created simple, reliable startup scripts that replace all the complex setup processes:

### Windows (PowerShell)
```powershell
.\start-scorpius.ps1
```

### Linux/Mac (Bash)
```bash
./start-scorpius.sh
```

That's it! The script will:
- ✅ Check Docker availability
- ✅ Set up environment configuration
- ✅ Create necessary directories
- ✅ Start all services in the correct order
- ✅ Show you all the service URLs when ready

## 🌐 Service URLs (after startup)

Once started, you can access:

- **🏠 Main Dashboard**: http://localhost:3000
- **🔌 API Gateway**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔍 Slither Scanner**: http://localhost:8002
- **🔍 Mythril Scanner**: http://localhost:8003
- **🔍 MythX Scanner**: http://localhost:8004
- **🔍 Manticore Scanner**: http://localhost:8005
- **📊 Grafana Monitor**: http://localhost:3001
- **📈 Prometheus**: http://localhost:9090
- **🗄️ Database Admin**: http://localhost:5050
- **🗃️ Redis Admin**: http://localhost:8081

## 🔧 Management Commands

### Start the platform
```bash
# Windows
.\start-scorpius.ps1

# Linux/Mac
./start-scorpius.sh
```

### Stop the platform
```bash
# Windows
.\start-scorpius.ps1 stop

# Linux/Mac
./start-scorpius.sh stop
```

### Restart the platform
```bash
# Windows
.\start-scorpius.ps1 restart

# Linux/Mac
./start-scorpius.sh restart
```

### Clean restart (removes all data)
```bash
# Windows
.\start-scorpius.ps1 restart -Clean

# Linux/Mac
./start-scorpius.sh restart clean
```

### Check status
```bash
# Windows
.\start-scorpius.ps1 status

# Linux/Mac
./start-scorpius.sh status
```

### View logs
```bash
docker-compose -f docker/docker-compose.enterprise.yml logs -f
```

## 🛠️ Configuration

The startup script creates a `.env` file with default settings. You can edit this file to customize:

- Database passwords
- API keys (like MythX)
- JWT secrets
- Log levels

## 🎭 What's Included

The platform includes:

### Core Services
- **API Gateway** - Central orchestration and routing
- **Bridge Service** - Blockchain bridge functionality
- **Bytecode Service** - Smart contract bytecode analysis
- **Honeypot Service** - Honeypot detection capabilities
- **Mempool Service** - Transaction monitoring
- **Quantum Service** - Quantum computing integration
- **Time Machine Service** - Historical blockchain analysis

### Security Scanners
- **Slither** - Static analysis for Solidity
- **Mythril** - Symbolic execution security analysis
- **MythX** - Cloud-based security analysis
- **Manticore** - Advanced symbolic execution

### Infrastructure
- **PostgreSQL** - Primary database
- **Redis** - Caching and message queues
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **Frontend** - React-based web interface

### Admin Tools
- **PgAdmin** - Database management
- **Redis Commander** - Redis management
- **Dev Tools** - Development utilities

## 🚨 Troubleshooting

### Docker Issues
- Make sure Docker Desktop is running
- Check Docker has enough memory allocated (8GB+ recommended)
- Try restarting Docker Desktop

### Port Conflicts
- Make sure no other services are using the ports listed above
- You can modify port mappings in `docker/docker-compose.enterprise.yml`

### Services Not Starting
- Check logs: `docker-compose -f docker/docker-compose.enterprise.yml logs -f`
- Try a clean restart: `./start-scorpius.ps1 restart -Clean`

### Need Help?
- Check the logs for specific error messages
- Ensure all prerequisites are met
- Try stopping and starting again

## 🎉 That's It!

You now have a complete enterprise-grade blockchain security platform running locally. The startup script handles all the complexity for you!

---

*Previous complex startup scripts have been replaced with these simple, reliable scripts that just work.* 