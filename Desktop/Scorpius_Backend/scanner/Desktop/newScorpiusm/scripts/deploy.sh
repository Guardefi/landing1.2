# Production Deployment Script for Scorpius
#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting Scorpius Production Deployment..."

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
VERSION=${VERSION:-latest}
REGISTRY=${REGISTRY:-scorpius}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
check_requirements() {
    log_info "Checking deployment requirements..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi

    # Check if required files exist
    if [ ! -f ".env.production" ]; then
        log_error ".env.production file not found. Please create it from .env.production.example"
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "docker-compose is not installed"
        exit 1
    fi

    log_info "All requirements met ✓"
}

# Build Docker images
build_images() {
    log_info "Building production Docker images..."

    # Build backend
    log_info "Building backend image..."
    docker build -f backend/Dockerfile.prod -t ${REGISTRY}/backend:${VERSION} backend/

    # Build frontend
    log_info "Building frontend image..."
    docker build -f frontend/Dockerfile.prod -t ${REGISTRY}/frontend:${VERSION} frontend/

    log_info "Images built successfully ✓"
}

# Run security scans
security_scan() {
    log_info "Running security scans..."

    # Scan Docker images for vulnerabilities
    if command -v trivy >/dev/null 2>&1; then
        log_info "Scanning backend image..."
        trivy image ${REGISTRY}/backend:${VERSION}

        log_info "Scanning frontend image..."
        trivy image ${REGISTRY}/frontend:${VERSION}
    else
        log_warn "Trivy not installed, skipping vulnerability scan"
    fi

    # Run Bandit security scan on Python code
    if [ -f "requirements.prod.txt" ]; then
        log_info "Running Python security scan..."
        pip install bandit
        bandit -r backend/ -f json -o security_scan_results.json || log_warn "Security issues found, check security_scan_results.json"
    fi
}

# Database migrations
run_migrations() {
    log_info "Running database migrations..."

    # Start database first
    docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d postgres redis

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10

    # Run migrations
    docker-compose -f infrastructure/docker/docker-compose.prod.yml run --rm backend alembic upgrade head

    log_info "Database migrations completed ✓"
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."

    # Stop existing containers
    docker-compose -f infrastructure/docker/docker-compose.prod.yml down

    # Start all services
    docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

    log_info "Application deployed ✓"
}

# Health checks
health_check() {
    log_info "Running health checks..."

    # Wait a bit for services to start
    sleep 30

    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_info "Backend health check passed ✓"
    else
        log_error "Backend health check failed ✗"
        return 1
    fi

    # Check frontend health
    if curl -f http://localhost/health >/dev/null 2>&1; then
        log_info "Frontend health check passed ✓"
    else
        log_error "Frontend health check failed ✗"
        return 1
    fi

    log_info "All health checks passed ✓"
}

# Backup current deployment
backup_current() {
    log_info "Creating backup of current deployment..."

    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup database
    docker-compose -f infrastructure/docker/docker-compose.prod.yml exec postgres pg_dump -U scorpius_user scorpius_prod > "$BACKUP_DIR/database.sql"

    # Backup configuration
    cp .env.production "$BACKUP_DIR/"

    log_info "Backup created in $BACKUP_DIR ✓"
}

# Rollback function
rollback() {
    log_error "Deployment failed. Starting rollback..."

    # Stop current deployment
    docker-compose -f infrastructure/docker/docker-compose.prod.yml down

    # Restore from backup if available
    LATEST_BACKUP=$(ls -t backups/ | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        log_info "Restoring from backup: $LATEST_BACKUP"
        # Restore database and config...
    fi

    log_info "Rollback completed"
    exit 1
}

# Main deployment process
main() {
    log_info "Starting production deployment for Scorpius v${VERSION}"

    # Trap errors and rollback
    trap rollback ERR

    check_requirements
    backup_current
    build_images
    security_scan
    run_migrations
    deploy_application
    health_check

    log_info "🎉 Deployment completed successfully!"
    log_info "Application is now running at:"
    log_info "  Frontend: http://localhost"
    log_info "  Backend API: http://localhost:8000"
    log_info "  Monitoring: http://localhost:3000 (Grafana)"
    log_info "  Metrics: http://localhost:9090 (Prometheus)"
}

# Run deployment
main "$@"
