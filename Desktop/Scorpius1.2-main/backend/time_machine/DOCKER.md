# Docker Deployment Guide

This guide explains how to run the Time Machine application using Docker.

## Quick Start

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 4GB RAM available
- At least 10GB disk space

### Development Setup

1. **Build and run with Docker Compose:**
   ```bash
   # Windows
   .\docker-run.bat
   
   # Linux/Mac
   ./docker-run.sh
   ```

2. **Or manually:**
   ```bash
   # Build the image
   docker build -t time-machine:latest .
   
   # Run with docker-compose
   docker-compose up -d
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Blockchain Node (Anvil): http://localhost:8545

### Development Mode

For development with live reload:

```bash
docker-compose -f docker/docker-compose.dev.yml up -d
```

This mounts your local code directory for hot reloading.

## Services

The Docker Compose setup includes:

### Core Services

1. **time-machine** (port 8000)
   - Main application with FastAPI backend and React UI
   - Includes WebSocket support for real-time updates

2. **anvil** (port 8545)
   - Local Ethereum node for testing
   - Pre-funded with 10 accounts, each with 10,000 ETH

### Optional Services

3. **redis** (port 6379)
   - For caching and job queues
   - Persistent data storage

4. **postgres** (port 5432)
   - For metadata and forensic session storage
   - Database: `timemachine`
   - User: `timemachine`
   - Password: `timemachine_password`

## Configuration

### Environment Variables

- `PYTHONPATH`: Python module path (default: `/app`)
- `TM_CONFIG_PATH`: Configuration file path (default: `/app/config/time_machine.yaml`)
- `TM_DATA_DIR`: Data directory for snapshots (default: `/app/store`)
- `TM_LOG_LEVEL`: Logging level (default: `INFO`)

### Configuration File

The application uses `config/time_machine.yaml` for configuration:

```yaml
engine:
  max_concurrent_jobs: 5
  snapshot_retention_days: 30
  cleanup_interval_hours: 24

vm_adapters:
  anvil:
    enabled: true
    default_port: 8545
    default_chain_id: 31337
  
  hardhat:
    enabled: true
    default_port: 8545
    
  geth:
    enabled: false

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]

logging:
  level: "INFO"
  format: "json"
```

## Data Persistence

### Volumes

The Docker setup uses the following volumes:

- `./store:/app/store` - Snapshots and bundles
- `./logs:/app/logs` - Application logs
- `./config:/app/config` - Configuration files
- `redis-data` - Redis persistence
- `postgres-data` - PostgreSQL data

### Backup Data

To backup your Time Machine data:

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup store data
docker cp time-machine_time-machine_1:/app/store ./backups/$(date +%Y%m%d)/store

# Backup database (if using PostgreSQL)
docker exec time-machine_postgres_1 pg_dump -U timemachine timemachine > ./backups/$(date +%Y%m%d)/database.sql
```

## Monitoring and Debugging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f time-machine

# Real-time logs
docker-compose logs -f --tail=50 time-machine
```

### Health Checks

The application includes health checks:

```bash
# Check application health
curl http://localhost:8000/health

# Check all container health
docker-compose ps
```

### Debug Mode

To run in debug mode with more verbose logging:

1. Update `docker/docker-compose.yml`:
   ```yaml
   environment:
     - TM_LOG_LEVEL=DEBUG
   ```

2. Restart:
   ```bash
   docker-compose restart time-machine
   ```

## Performance Tuning

### Resource Limits

For production, consider adding resource limits:

```yaml
services:
  time-machine:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Scaling

To run multiple Time Machine instances:

```bash
docker-compose up -d --scale time-machine=3
```

Note: You'll need a load balancer for multiple instances.

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Change ports in `docker/docker-compose.yml` if 8000/8545 are in use

2. **Permission issues:**
   - Ensure Docker has access to the project directory
   - Check volume mount permissions

3. **Memory issues:**
   - Increase Docker memory limit in Docker Desktop
   - Reduce `max_concurrent_jobs` in configuration

4. **Build failures:**
   - Clear Docker cache: `docker system prune -a`
   - Check internet connectivity for package downloads

### Debug Commands

```bash
# Enter container shell
docker exec -it time-machine_time-machine_1 /bin/bash

# Check Python environment
docker exec time-machine_time-machine_1 python --version

# Test API directly
docker exec time-machine_time-machine_1 curl http://localhost:8000/health

# Check disk usage
docker exec time-machine_time-machine_1 df -h
```

## Production Deployment

### Security Considerations

1. **Change default passwords:**
   - Update PostgreSQL credentials
   - Use environment variables for secrets

2. **Network security:**
   - Remove external port mappings for internal services
   - Use Docker secrets for sensitive data

3. **SSL/TLS:**
   - Add reverse proxy (nginx/traefik) for HTTPS
   - Generate proper SSL certificates

### Example Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  time-machine:
    image: ghcr.io/your-org/time-machine:latest
    environment:
      - TM_LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://user:pass@postgres:5432/timemachine
    networks:
      - internal
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    networks:
      - internal
    restart: always

networks:
  internal:
    driver: bridge
```

## CI/CD Integration

The project includes GitHub Actions for:

- Automated testing
- Docker image building
- Security scanning
- Deployment to container registry

See `.github/workflows/ci-cd.yml` for the complete pipeline.
