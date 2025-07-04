#!/bin/bash
# Scorpius Enterprise Platform - Simple Startup Script
# This script starts the complete Scorpius Enterprise platform with all services

set -e

# Configuration
ACTION="${1:-start}"
CLEAN="${2:-false}"
COMPOSE_FILE="docker/docker-compose.enterprise.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}🦂 $1${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo ""
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

check_docker() {
    print_step "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker"
        exit 1
    fi
    
    print_success "Docker is available and running"
}

setup_environment() {
    print_step "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs data/{postgres,redis,grafana,prometheus,pgadmin}
    
    # Create basic .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_step "Creating environment configuration..."
        cat > .env << EOF
# Scorpius Enterprise Environment Configuration
DB_PASSWORD=scorpius123
REDIS_PASSWORD=scorpius123
JWT_SECRET=scorpius-enterprise-jwt-secret-key-change-in-production
GRAFANA_PASSWORD=admin
PGADMIN_PASSWORD=admin
MYTHX_API_KEY=your-mythx-api-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
        print_success "Created .env file with default configuration"
        print_warning "Please edit .env file with your specific settings if needed"
    fi
    
    print_success "Environment setup complete"
}

start_infrastructure() {
    print_step "Starting infrastructure services..."
    
    # Start database and cache first
    docker-compose -f $COMPOSE_FILE up -d postgres redis
    
    print_step "Waiting for database to be ready..."
    local attempt=0
    local max_attempts=30
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U scorpius &> /dev/null; then
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -ge $max_attempts ]; then
        print_error "Database failed to start within timeout"
        exit 1
    fi
    
    echo ""
    print_success "Infrastructure services started"
}

start_core_services() {
    print_step "Starting core services..."
    
    # Start API Gateway
    docker-compose -f $COMPOSE_FILE up -d api-gateway
    
    print_step "Waiting for API Gateway to be ready..."
    local attempt=0
    local max_attempts=30
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f http://localhost:8000/health &> /dev/null; then
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo ""
    if [ $attempt -lt $max_attempts ]; then
        print_success "API Gateway is ready"
    else
        print_warning "API Gateway may still be starting up"
    fi
}

start_services() {
    print_step "Starting all remaining services..."
    
    # Start all services
    docker-compose -f $COMPOSE_FILE up -d
    
    print_step "Waiting for services to initialize..."
    sleep 10
    
    print_success "All services started"
}

show_status() {
    print_header "Scorpius Enterprise Platform Status"
    
    # Show running containers
    print_step "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    echo -e "${GREEN}🌐 Service URLs:${NC}"
    echo -e "  • Main Dashboard:     ${WHITE}http://localhost:3000${NC}"
    echo -e "  • API Gateway:        ${WHITE}http://localhost:8000${NC}"
    echo -e "  • API Documentation:  ${WHITE}http://localhost:8000/docs${NC}"
    echo -e "  • Slither Scanner:    ${WHITE}http://localhost:8002${NC}"
    echo -e "  • Mythril Scanner:    ${WHITE}http://localhost:8003${NC}"
    echo -e "  • MythX Scanner:      ${WHITE}http://localhost:8004${NC}"
    echo -e "  • Manticore Scanner:  ${WHITE}http://localhost:8005${NC}"
    echo -e "  • Grafana Monitor:    ${WHITE}http://localhost:3001${NC}"
    echo -e "  • Prometheus:         ${WHITE}http://localhost:9090${NC}"
    echo -e "  • Database Admin:     ${WHITE}http://localhost:5050${NC}"
    echo -e "  • Redis Admin:        ${WHITE}http://localhost:8081${NC}"
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo -e "  • View logs:          ${GRAY}docker-compose -f $COMPOSE_FILE logs -f${NC}"
    echo -e "  • Stop services:      ${GRAY}./start-scorpius.sh stop${NC}"
    echo -e "  • Restart services:   ${GRAY}./start-scorpius.sh restart${NC}"
    echo -e "  • Clean restart:      ${GRAY}./start-scorpius.sh clean${NC}"
}

stop_services() {
    print_header "Stopping Scorpius Enterprise Platform"
    
    print_step "Stopping all services..."
    docker-compose -f $COMPOSE_FILE down
    
    if [ "$CLEAN" = "clean" ]; then
        print_step "Cleaning up containers and volumes..."
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        print_success "Clean shutdown complete"
    else
        print_success "Services stopped"
    fi
}

restart_services() {
    print_header "Restarting Scorpius Enterprise Platform"
    
    stop_services
    sleep 5
    start_all
}

start_all() {
    print_header "Starting Scorpius Enterprise Platform"
    
    check_docker
    setup_environment
    start_infrastructure
    start_core_services
    start_services
    show_status
    
    print_header "🎉 Scorpius Enterprise Platform Started Successfully!"
}

show_help() {
    print_header "Scorpius Enterprise Platform - Startup Script"
    
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${GRAY}./start-scorpius.sh [action] [options]${NC}"
    echo ""
    echo -e "${BLUE}Actions:${NC}"
    echo -e "  ${WHITE}start${NC}      - Start all services (default)"
    echo -e "  ${WHITE}stop${NC}       - Stop all services"
    echo -e "  ${WHITE}restart${NC}    - Restart all services"
    echo -e "  ${WHITE}status${NC}     - Show service status"
    echo -e "  ${WHITE}help${NC}       - Show this help message"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo -e "  ${WHITE}clean${NC}      - Clean shutdown (removes volumes)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ${GRAY}./start-scorpius.sh${NC}"
    echo -e "  ${GRAY}./start-scorpius.sh stop${NC}"
    echo -e "  ${GRAY}./start-scorpius.sh restart clean${NC}"
}

# Main script execution
case "$ACTION" in
    "start")
        start_all
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "help")
        show_help
        ;;
    *)
        print_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac 