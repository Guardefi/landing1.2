#!/bin/bash

# Scorpius Bridge Build and Deployment Script
# This script handles building, testing, and deploying the Scorpius Bridge system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-development}
COMPOSE_FILE=${COMPOSE_FILE:-docker-compose.yml}
PROJECT_NAME="scorpius-bridge"

echo -e "${BLUE}🌉 Scorpius Bridge Deployment Script${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running ✓"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_status "Docker Compose is available ✓"
}

# Function to setup directories
setup_directories() {
    print_status "Setting up directories..."
    mkdir -p logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p secrets
    mkdir -p nginx
    mkdir -p postgres
    mkdir -p redis
    print_status "Directories created ✓"
}

# Function to generate secrets for production
generate_secrets() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Generating production secrets..."
        
        if [ ! -f secrets/secret_key.txt ]; then
            openssl rand -base64 32 > secrets/secret_key.txt
            print_status "Generated secret_key.txt"
        fi
        
        if [ ! -f secrets/jwt_secret.txt ]; then
            openssl rand -base64 32 > secrets/jwt_secret.txt
            print_status "Generated jwt_secret.txt"
        fi
        
        if [ ! -f secrets/postgres_password.txt ]; then
            openssl rand -base64 24 > secrets/postgres_password.txt
            print_status "Generated postgres_password.txt"
        fi
        
        if [ ! -f secrets/grafana_password.txt ]; then
            openssl rand -base64 16 > secrets/grafana_password.txt
            print_status "Generated grafana_password.txt"
        fi
        
        # Set proper permissions
        chmod 600 secrets/*
        print_status "Secrets generated and secured ✓"
    fi
}

# Function to create basic configurations
create_configs() {
    print_status "Creating configuration files..."
    
    # Prometheus config
    if [ ! -f monitoring/prometheus.yml ]; then
        cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scorpius-bridge'
    static_configs:
      - targets: ['scorpius-bridge:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF
        print_status "Created prometheus.yml"
    fi
    
    # Grafana datasource
    if [ ! -f monitoring/grafana/datasources/prometheus.yml ]; then
        cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
        print_status "Created Grafana datasource config"
    fi
    
    # Basic Nginx config for production
    if [ "$ENVIRONMENT" = "production" ] && [ ! -f nginx/nginx.conf ]; then
        cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server scorpius-bridge:8000;
    }
    
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
        print_status "Created Nginx config"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Build test image
    docker build -t ${PROJECT_NAME}-test --target test .
    
    # Run unit tests
    docker run --rm ${PROJECT_NAME}-test pytest tests/unit/ -v --cov=scorpius_bridge --cov-report=term-missing
    
    # Run integration tests if available
    if [ -d "tests/integration" ]; then
        print_status "Running integration tests..."
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down
    fi
    
    print_status "Tests completed ✓"
}

# Function to build the application
build_app() {
    print_status "Building Scorpius Bridge..."
    
    # Choose the right compose file
    if [ "$ENVIRONMENT" = "production" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    # Build the application
    docker-compose -f $COMPOSE_FILE build --no-cache
    print_status "Build completed ✓"
}

# Function to deploy the application
deploy_app() {
    print_status "Deploying Scorpius Bridge..."
    
    # Stop existing containers
    docker-compose -f $COMPOSE_FILE down
    
    # Start the application
    docker-compose -f $COMPOSE_FILE up -d
    
    # Wait for health checks
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check if main service is running
    if docker-compose -f $COMPOSE_FILE ps scorpius-bridge | grep -q "Up"; then
        print_status "Scorpius Bridge is running ✓"
    else
        print_error "Scorpius Bridge failed to start"
        docker-compose -f $COMPOSE_FILE logs scorpius-bridge
        exit 1
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    print_status "Available Services:"
    echo "  🌐 API: http://localhost:8000"
    echo "  📊 Metrics: http://localhost:9090 (Prometheus)"
    echo "  📈 Dashboards: http://localhost:3000 (Grafana)"
    
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "  🗄️  Database Admin: http://localhost:5050 (pgAdmin)"
        echo "  🔧 WebSocket Test: http://localhost:8000/api/ws/test"
    fi
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  📋 Logs: http://localhost:5601 (Kibana)"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-scorpius-bridge}
    print_status "Showing logs for $service..."
    docker-compose -f $COMPOSE_FILE logs -f $service
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f $COMPOSE_FILE down -v
    docker system prune -f
    print_status "Cleanup completed ✓"
}

# Function to backup data
backup_data() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Creating backup..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_dir="backups/${timestamp}"
        mkdir -p $backup_dir
        
        # Backup database
        docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U scorpius scorpius_bridge > $backup_dir/database.sql
        
        # Backup volumes
        docker run --rm -v scorpius-bridge_postgres_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
        docker run --rm -v scorpius-bridge_redis_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
        
        print_status "Backup created in $backup_dir ✓"
    else
        print_warning "Backup is only available in production environment"
    fi
}

# Main script logic
case "${1:-deploy}" in
    "check")
        check_docker
        check_docker_compose
        ;;
    "setup")
        check_docker
        check_docker_compose
        setup_directories
        generate_secrets
        create_configs
        ;;
    "test")
        check_docker
        run_tests
        ;;
    "build")
        check_docker
        check_docker_compose
        build_app
        ;;
    "deploy")
        check_docker
        check_docker_compose
        setup_directories
        generate_secrets
        create_configs
        build_app
        deploy_app
        show_status
        ;;
    "redeploy")
        deploy_app
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    "stop")
        docker-compose -f $COMPOSE_FILE down
        ;;
    "restart")
        docker-compose -f $COMPOSE_FILE restart
        ;;
    "cleanup")
        cleanup
        ;;
    "backup")
        backup_data
        ;;
    "help"|"--help"|"-h")
        echo "Scorpius Bridge Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  redeploy  - Redeploy without rebuilding"
        echo "  build     - Build only"
        echo "  test      - Run tests"
        echo "  setup     - Setup directories and configs"
        echo "  status    - Show service status"
        echo "  logs      - Show logs [service_name]"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  cleanup   - Clean up containers and volumes"
        echo "  backup    - Backup data (production only)"
        echo "  check     - Check prerequisites"
        echo "  help      - Show this help"
        echo ""
        echo "Environment Variables:"
        echo "  ENVIRONMENT   - deployment environment (development|production)"
        echo "  COMPOSE_FILE  - docker-compose file to use"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
