# Docker and Containerization Test Commands
# These commands test Docker builds, container functionality, and deployment

Write-Host "=== DOCKER AND CONTAINERIZATION COMMANDS ===" -ForegroundColor Green

# Docker Build Commands
Write-Host "`n1. Docker Build Commands..." -ForegroundColor Yellow

# Build development image
Write-Host "   - Build development image..." -ForegroundColor Cyan
docker build -t scorpius:dev .

# Build production image
Write-Host "   - Build production image..." -ForegroundColor Cyan
docker build -f Dockerfile.production -t scorpius:prod .

# Build with no cache
Write-Host "   - Build without cache..." -ForegroundColor Cyan
docker build --no-cache -t scorpius:latest .

# Build with specific target stage
Write-Host "   - Build specific stage..." -ForegroundColor Cyan
docker build --target production -f Dockerfile.production -t scorpius:prod .

# Docker Run Commands
Write-Host "`n2. Docker Run Commands..." -ForegroundColor Yellow

# Run development container
Write-Host "   - Run development container..." -ForegroundColor Cyan
docker run -d -p 8000:8000 --name scorpius-dev scorpius:dev

# Run production container
Write-Host "   - Run production container..." -ForegroundColor Cyan
docker run -d -p 8000:8000 --name scorpius-prod scorpius:prod

# Run with environment file
Write-Host "   - Run with environment file..." -ForegroundColor Cyan
docker run -d -p 8000:8000 --env-file .env.production --name scorpius-env scorpius:prod

# Run interactively for debugging
Write-Host "   - Run interactively..." -ForegroundColor Cyan
docker run -it --rm scorpius:dev /bin/bash

# Docker Compose Commands
Write-Host "`n3. Docker Compose Commands..." -ForegroundColor Yellow

# Start all services
Write-Host "   - Start all services..." -ForegroundColor Cyan
docker-compose up -d

# Start specific service
Write-Host "   - Start specific service..." -ForegroundColor Cyan
docker-compose up -d backend

# View logs
Write-Host "   - View service logs..." -ForegroundColor Cyan
docker-compose logs -f backend

# Stop all services
Write-Host "   - Stop all services..." -ForegroundColor Cyan
docker-compose down

# Rebuild and restart
Write-Host "   - Rebuild and restart..." -ForegroundColor Cyan
docker-compose up -d --build

# Container Health Checks
Write-Host "`n4. Container Health Checks..." -ForegroundColor Yellow

# Check container health
Write-Host "   - Check container health..." -ForegroundColor Cyan
docker ps --filter "name=scorpius"

# Inspect container health
Write-Host "   - Inspect health status..." -ForegroundColor Cyan
docker inspect scorpius-prod --format='{{.State.Health.Status}}'

# View health check logs
Write-Host "   - Health check logs..." -ForegroundColor Cyan
docker inspect scorpius-prod --format='{{range .State.Health.Log}}{{.Output}}{{end}}'

# Test container endpoints
Write-Host "   - Test health endpoint..." -ForegroundColor Cyan
curl http://localhost:8000/healthz

# Container Resource Usage
Write-Host "`n5. Container Resource Monitoring..." -ForegroundColor Yellow

# View container stats
Write-Host "   - Container stats..." -ForegroundColor Cyan
docker stats scorpius-prod

# Container resource usage
Write-Host "   - Resource usage..." -ForegroundColor Cyan
docker exec scorpius-prod ps aux

# Container logs
Write-Host "   - View container logs..." -ForegroundColor Cyan
docker logs scorpius-prod

# Follow logs
Write-Host "   - Follow logs..." -ForegroundColor Cyan
docker logs -f scorpius-prod

# Image Analysis
Write-Host "`n6. Docker Image Analysis..." -ForegroundColor Yellow

# List images
Write-Host "   - List images..." -ForegroundColor Cyan
docker images | grep scorpius

# Image size analysis
Write-Host "   - Image size..." -ForegroundColor Cyan
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep scorpius

# Image history (layers)
Write-Host "   - Image history..." -ForegroundColor Cyan
docker history scorpius:prod

# Image vulnerability scan (if Docker Scout available)
Write-Host "   - Security scan..." -ForegroundColor Cyan
Write-Host "     docker scout cves scorpius:prod" -ForegroundColor Gray

# Container Security Tests
Write-Host "`n7. Container Security Tests..." -ForegroundColor Yellow

# Check running processes in container
Write-Host "   - Running processes..." -ForegroundColor Cyan
docker exec scorpius-prod ps aux

# Check user context
Write-Host "   - User context..." -ForegroundColor Cyan
docker exec scorpius-prod whoami

# Check file permissions
Write-Host "   - File permissions..." -ForegroundColor Cyan
docker exec scorpius-prod ls -la /app

# Network connectivity tests
Write-Host "   - Network tests..." -ForegroundColor Cyan
docker exec scorpius-prod ping -c 3 google.com

# Docker Cleanup Commands
Write-Host "`n8. Docker Cleanup Commands..." -ForegroundColor Yellow

# Remove stopped containers
Write-Host "   - Remove stopped containers..." -ForegroundColor Cyan
docker container prune -f

# Remove unused images
Write-Host "   - Remove unused images..." -ForegroundColor Cyan
docker image prune -f

# Remove all unused resources
Write-Host "   - Remove all unused..." -ForegroundColor Cyan
docker system prune -f

# Remove specific containers
Write-Host "   - Remove specific containers..." -ForegroundColor Cyan
docker rm -f scorpius-dev scorpius-prod

# Production Deployment Tests
Write-Host "`n9. Production Deployment Tests..." -ForegroundColor Yellow

# Test with production environment
Write-Host "   - Production environment test..." -ForegroundColor Cyan
Write-Host "     docker run -d -p 8000:8000 --env ENVIRONMENT=production scorpius:prod" -ForegroundColor Gray

# Test with external database
Write-Host "   - External database test..." -ForegroundColor Cyan
Write-Host "     docker run -d -p 8000:8000 --env DB_HOST=external-db scorpius:prod" -ForegroundColor Gray

# Test with load balancer
Write-Host "   - Load balancer test..." -ForegroundColor Cyan
Write-Host "     docker run -d -p 8001:8000 --name scorpius-1 scorpius:prod" -ForegroundColor Gray
Write-Host "     docker run -d -p 8002:8000 --name scorpius-2 scorpius:prod" -ForegroundColor Gray

# Kubernetes Deployment Tests
Write-Host "`n10. Kubernetes Deployment Tests..." -ForegroundColor Yellow

# Apply Kubernetes manifests
Write-Host "   - Apply manifests..." -ForegroundColor Cyan
kubectl apply -f infrastructure/kubernetes/

# Check pod status
Write-Host "   - Check pod status..." -ForegroundColor Cyan
kubectl get pods -n scorpius-prod

# Check service status
Write-Host "   - Check services..." -ForegroundColor Cyan
kubectl get services -n scorpius-prod

# View pod logs
Write-Host "   - View pod logs..." -ForegroundColor Cyan
kubectl logs -l app=scorpius-backend -n scorpius-prod

# Expected successful output
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "Docker build: Successfully tagged scorpius:prod
Docker run: Container started, health check passing
Health endpoint: HTTP 200 {'status': 'healthy'}
Resource usage: CPU < 50%, Memory < 512MB
Security: Non-root user, no critical vulnerabilities" -ForegroundColor Gray

Write-Host "`n=== TROUBLESHOOTING ===" -ForegroundColor Red
Write-Host "Common Docker issues:"
Write-Host "1. Build failures: Check Dockerfile syntax and dependencies"
Write-Host "2. Port conflicts: Use different ports or stop conflicting services"
Write-Host "3. Permission errors: Check file ownership and container user"
Write-Host "4. Health check failures: Verify application startup and endpoints"
Write-Host "5. Resource limits: Check available memory and CPU"
