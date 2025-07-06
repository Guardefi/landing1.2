# 🐳 Scorpius Enterprise Docker Setup Guide

## 🎯 Overview

This guide will help you set up the complete Scorpius Enterprise environment with all scanner plugins (Slither, Mythril, MythX, Manticore) running in isolated Docker containers to avoid dependency conflicts.

## 🚀 Quick Start

### 1. Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **PowerShell** (Windows) or **Bash** (Linux/Mac)
- **Git** (for cloning the repository)

### 2. Environment Setup

```powershell
# Copy the enterprise environment configuration
Copy-Item config/env.enterprise .env

# Edit the .env file with your specific settings
notepad .env
```

### 3. Start the Enterprise Environment

```powershell
# Start all services (recommended for first run)
.\scripts\docker-enterprise.ps1 start

# Or start development environment only
.\scripts\docker-enterprise.ps1 dev

# Or start only scanner plugins
.\scripts\docker-enterprise.ps1 dev-scanners
```

## 🏗️ Architecture

### Core Services
- **API Gateway** (Port 8000) - Central orchestrator
- **Bridge Service** - Blockchain bridge functionality
- **Bytecode Service** - Smart contract analysis
- **Honeypot Service** - Honeypot detection
- **Mempool Service** - Transaction monitoring
- **Quantum Service** - Quantum computing integration
- **Time Machine Service** - Historical data analysis

### Scanner Plugins (Isolated Containers)
- **Slither Scanner** (Port 8002) - Static analysis
- **Mythril Scanner** (Port 8003) - Symbolic execution
- **MythX Scanner** (Port 8004) - Cloud-based analysis
- **Manticore Scanner** (Port 8005) - Advanced symbolic execution

### Infrastructure
- **PostgreSQL** (Port 5432) - Primary database
- **Redis** (Port 6379) - Caching and queues
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3001) - Monitoring dashboards

### Development Tools
- **PgAdmin** (Port 5050) - Database administration
- **Redis Commander** (Port 8081) - Redis administration
- **Dev Tools Container** - Development environment

## 🔧 Development Workflow

### Starting Development Environment

```powershell
# Start core services for development
.\scripts\docker-enterprise.ps1 dev-core

# Start frontend with hot reload
.\scripts\docker-enterprise.ps1 dev-frontend

# Start scanner plugins
.\scripts\docker-enterprise.ps1 dev-scanners
```

### Building Images

```powershell
# Build all images
.\scripts\docker-enterprise.ps1 build

# Build only scanner plugins
.\scripts\docker-enterprise.ps1 build-scanners

# Build only core services
.\scripts\docker-enterprise.ps1 build-core
```

### Monitoring and Logs

```powershell
# View all logs
.\scripts\docker-enterprise.ps1 logs

# View API gateway logs
.\scripts\docker-enterprise.ps1 logs-api

# View scanner logs
.\scripts\docker-enterprise.ps1 logs-scanners

# Open monitoring dashboards
.\scripts\docker-enterprise.ps1 monitor
```

## 🔍 Scanner Plugin Management

### Individual Scanner Control

```powershell
# View Slither scanner logs
.\scripts\docker-enterprise.ps1 scanner-slither

# View Mythril scanner logs
.\scripts\docker-enterprise.ps1 scanner-mythril

# View MythX scanner logs
.\scripts\docker-enterprise.ps1 scanner-mythx

# View Manticore scanner logs
.\scripts\docker-enterprise.ps1 scanner-manticore
```

### Testing Scanner Health

```powershell
# Test all scanner plugins
.\scripts\docker-enterprise.ps1 test-scanners
```

### Scanner Configuration

Each scanner plugin can be configured independently:

- **Slither**: Static analysis with configurable rules
- **Mythril**: Symbolic execution with timeout settings
- **MythX**: Cloud-based analysis (requires API key)
- **Manticore**: Advanced symbolic execution with resource limits

## 📊 Monitoring and Health Checks

### Service Health

```powershell
# Check service health
.\scripts\docker-enterprise.ps1 health

# Show service status
.\scripts\docker-enterprise.ps1 status

# Show port mappings
.\scripts\docker-enterprise.ps1 ports
```

### Monitoring Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **PgAdmin**: http://localhost:5050 (admin@scorpius.enterprise/admin)
- **Redis Commander**: http://localhost:8081

## 🧹 Maintenance

### Backup and Restore

```powershell
# Backup data volumes
.\scripts\docker-enterprise.ps1 backup

# Clean up Docker resources
.\scripts\docker-enterprise.ps1 clean

# Remove unused resources
.\scripts\docker-enterprise.ps1 prune
```

### Updates

```powershell
# Update all images
.\scripts\docker-enterprise.ps1 update

# Restart all services
.\scripts\docker-enterprise.ps1 restart
```

## 🔧 Advanced Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
DB_PASSWORD=your_secure_password
POSTGRES_DB=scorpius_enterprise

# Redis
REDIS_PASSWORD=your_redis_password

# JWT Security
JWT_SECRET=your_jwt_secret

# Scanner Configuration
MYTHX_API_KEY=your_mythx_api_key
SLITHER_TIMEOUT=300
MYTHRIL_TIMEOUT=600
MANTICORE_TIMEOUT=1800
```

### Resource Limits

Each scanner container has resource limits:

- **Slither**: 1GB RAM, 1 CPU
- **Mythril**: 2GB RAM, 1.5 CPU
- **MythX**: 1GB RAM, 1 CPU
- **Manticore**: 4GB RAM, 2 CPU

### Scaling Services

```powershell
# Scale API gateway to 3 instances
.\scripts\docker-enterprise.ps1 scale api-gateway 3

# Scale bridge service to 2 instances
.\scripts\docker-enterprise.ps1 scale bridge-service 2
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```powershell
   # Check what's using a port
   netstat -ano | findstr :8000
   
   # Stop conflicting services
   .\scripts\docker-enterprise.ps1 stop
   ```

2. **Scanner Not Responding**
   ```powershell
   # Check scanner logs
   .\scripts\docker-enterprise.ps1 logs-scanners
   
   # Test scanner health
   .\scripts\docker-enterprise.ps1 test-scanners
   ```

3. **Database Connection Issues**
   ```powershell
   # Check database logs
   .\scripts\docker-enterprise.ps1 logs postgres
   
   # Restart database
   docker-compose -f docker/docker-compose.enterprise.yml restart postgres
   ```

4. **Memory Issues**
   ```powershell
   # Check container resource usage
   docker stats
   
   # Restart with fresh containers
   .\scripts\docker-enterprise.ps1 restart --force
   ```

### Debug Mode

```powershell
# Open shell in dev-tools container
.\scripts\docker-enterprise.ps1 shell

# Execute command in specific container
.\scripts\docker-enterprise.ps1 exec api-gateway "python -c 'import sys; print(sys.path)'"
```

## 📈 Performance Optimization

### Production Deployment

```powershell
# Deploy to production
.\scripts\docker-enterprise.ps1 deploy

# Scale for high load
.\scripts\docker-enterprise.ps1 scale api-gateway 5
.\scripts\docker-enterprise.ps1 scale bridge-service 3
```

### Monitoring Setup

1. **Prometheus**: Configure scraping targets
2. **Grafana**: Import dashboards for each service
3. **Alerts**: Set up alerting rules for critical metrics

## 🔐 Security Considerations

### Production Security

1. **Change Default Passwords**: Update all default passwords in `.env`
2. **SSL/TLS**: Enable SSL for production deployments
3. **Network Security**: Use Docker networks for service isolation
4. **API Keys**: Secure storage of MythX and other API keys
5. **Access Control**: Implement proper authentication and authorization

### Scanner Security

- Each scanner runs in its own isolated container
- Resource limits prevent DoS attacks
- Timeout settings prevent hanging processes
- API rate limiting on scanner endpoints

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Scorpius Enterprise Architecture](docs/architecture/ARCHITECTURE.md)
- [API Documentation](docs/api/API.md)
- [Scanner Plugin Documentation](backend/scanner/README.md)

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review logs: `.\scripts\docker-enterprise.ps1 logs`
3. Check service health: `.\scripts\docker-enterprise.ps1 health`
4. Open an issue in the project repository

---

**🎉 Congratulations!** You now have a fully containerized Scorpius Enterprise environment with all scanner plugins running smoothly in isolated containers. 