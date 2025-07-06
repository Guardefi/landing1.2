#!/bin/bash

# Scorpius Enterprise Platform - Quick Start Script
# This script sets up and launches the complete microservices platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PLATFORM_NAME="Scorpius Enterprise Platform"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
print_header() {
    echo -e "\n${BLUE}================================================================${NC}"
    echo -e "${BLUE}🦂 $PLATFORM_NAME${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
}

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_step "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "All requirements met"
}

setup_environment() {
    print_step "Setting up environment..."
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file not found. Creating from example..."
        cp .env.example "$ENV_FILE"
        print_warning "Please edit $ENV_FILE with your configuration before proceeding."
        read -p "Press Enter when you're ready to continue..."
    fi
    
    # Create necessary directories
    mkdir -p logs/{api-gateway,bridge,mempool,honeypot,scanner,mev-bot,bytecode,quantum,time-machine,reporting}
    mkdir -p data/{postgres,redis,grafana,prometheus}
    mkdir -p infrastructure/{nginx,monitoring,ssl}
    
    print_success "Environment setup complete"
}

build_services() {
    print_step "Building all services..."
    
    echo "This may take several minutes on first run..."
    docker-compose -f "$COMPOSE_FILE" build --parallel
    
    print_success "All services built successfully"
}

start_database() {
    print_step "Starting database services..."
    
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis
    
    # Wait for postgres to be ready
    echo "Waiting for PostgreSQL to be ready..."
    until docker-compose -f "$COMPOSE_FILE" exec postgres pg_isready -U scorpius &> /dev/null; do
        echo -n "."
        sleep 1
    done
    
    print_success "Database services started"
}

start_core_services() {
    print_step "Starting core services..."
    
    docker-compose -f "$COMPOSE_FILE" up -d api-gateway
    
    # Wait for API gateway to be ready
    echo "Waiting for API Gateway to be ready..."
    until curl -s http://localhost:8000/health &> /dev/null; do
        echo -n "."
        sleep 1
    done
    
    print_success "API Gateway started"
}

start_microservices() {
    print_step "Starting microservices..."
    
    docker-compose -f "$COMPOSE_FILE" up -d \
        bridge-service \
        mempool-service \
        honeypot-service \
        scanner-service \
        mev-bot-service \
        bytecode-service \
        quantum-service \
        time-machine-service \
        reporting-service
    
    print_success "Microservices started"
}

start_frontend() {
    print_step "Starting frontend dashboard..."
    
    docker-compose -f "$COMPOSE_FILE" up -d frontend
    
    print_success "Frontend dashboard started"
}

start_monitoring() {
    print_step "Starting monitoring services..."
    
    docker-compose -f "$COMPOSE_FILE" up -d prometheus grafana
    
    print_success "Monitoring services started"
}

start_load_balancer() {
    print_step "Starting load balancer..."
    
    docker-compose -f "$COMPOSE_FILE" up -d nginx
    
    print_success "Load balancer started"
}

wait_for_services() {
    print_step "Waiting for all services to be healthy..."
    
    local services=(
        "localhost:8000"   # API Gateway
        "localhost:3000"   # Frontend
        "localhost:9090"   # Prometheus
        "localhost:3001"   # Grafana
    )
    
    for service in "${services[@]}"; do
        echo "Checking $service..."
        until curl -s "http://$service" &> /dev/null; do
            echo -n "."
            sleep 2
        done
        echo " ✓"
    done
    
    print_success "All services are healthy"
}

show_status() {
    print_step "Platform Status"
    
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
}

show_access_info() {
    print_step "Access Information"
    
    echo ""
    echo -e "${GREEN}🌐 Web Interfaces:${NC}"
    echo "  • Dashboard:     http://localhost:3000"
    echo "  • API Gateway:   http://localhost:8000"
    echo "  • API Docs:      http://localhost:8000/docs"
    echo "  • Grafana:       http://localhost:3001 (admin/admin123)"
    echo "  • Prometheus:    http://localhost:9090"
    echo ""
    echo -e "${GREEN}🔌 Service Endpoints:${NC}"
    echo "  • Bridge:        http://localhost:8001"
    echo "  • Mempool:       http://localhost:8002"
    echo "  • Honeypot:      http://localhost:8003"
    echo "  • Scanner:       http://localhost:8004"
    echo "  • MEV Bot:       http://localhost:8005"
    echo "  • Bytecode:      http://localhost:8006"
    echo "  • Quantum:       http://localhost:8007"
    echo "  • Time Machine:  http://localhost:8008"
    echo "  • Reporting:     http://localhost:8009"
    echo ""
    echo -e "${GREEN}📊 Monitoring:${NC}"
    echo "  • Health Check:  curl http://localhost:8000/health"
    echo "  • Metrics:       curl http://localhost:8000/metrics"
    echo "  • Logs:          docker-compose logs -f [service-name]"
    echo ""
}

cleanup_on_error() {
    print_error "An error occurred during startup. Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down
    exit 1
}

# Main execution
main() {
    # Set error handler
    trap cleanup_on_error ERR
    
    print_header
    
    check_requirements
    setup_environment
    build_services
    start_database
    start_core_services
    start_microservices
    start_frontend
    start_monitoring
    start_load_balancer
    wait_for_services
    
    print_header
    print_success "🎉 Scorpius Enterprise Platform started successfully!"
    
    show_status
    show_access_info
    
    echo -e "${BLUE}💡 Useful Commands:${NC}"
    echo "  • View logs:     docker-compose logs -f"
    echo "  • Stop platform: docker-compose down"
    echo "  • Restart:       docker-compose restart [service]"
    echo "  • Update:        git pull && docker-compose build && docker-compose up -d"
    echo ""
    echo -e "${YELLOW}Note: On first run, services may take a few minutes to fully initialize.${NC}"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        print_step "Stopping Scorpius Enterprise Platform..."
        docker-compose -f "$COMPOSE_FILE" down
        print_success "Platform stopped"
        ;;
    "restart")
        print_step "Restarting Scorpius Enterprise Platform..."
        docker-compose -f "$COMPOSE_FILE" restart
        print_success "Platform restarted"
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-}"
        ;;
    "clean")
        print_warning "This will remove all containers, volumes, and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
            docker system prune -af --volumes
            print_success "Platform cleaned"
        fi
        ;;
    *)
        main
        ;;
esac
