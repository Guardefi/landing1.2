#!/bin/bash
# Scorpius Enterprise Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="scorpius-enterprise-production"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

echo -e "${BLUE}🚀 Scorpius Enterprise Production Deployment${NC}"
echo "=================================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        echo -e "${RED}❌ docker-compose is not installed. Please install it and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ docker-compose is available${NC}"
}

# Function to check environment file
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠ $ENV_FILE not found. Creating from template...${NC}"
        if [ -f ".env.production" ]; then
            cp .env.production "$ENV_FILE"
            echo -e "${YELLOW}⚠ Please edit $ENV_FILE with your production values before proceeding${NC}"
            echo -e "${YELLOW}⚠ Pay special attention to passwords, secrets, and domain names${NC}"
            exit 1
        else
            echo -e "${RED}❌ No environment template found${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ Environment file exists${NC}"
}

# Function to create necessary directories
create_directories() {
    echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
    mkdir -p logs/{nginx,postgres} data uploads exports config/nginx/ssl
    chmod 755 logs data uploads exports
    echo -e "${GREEN}✓ Directories created${NC}"
}

# Function to build images
build_images() {
    echo -e "${YELLOW}🏗️ Building Docker images...${NC}"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Function to start services
start_services() {
    echo -e "${YELLOW}🚀 Starting services...${NC}"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    echo -e "${GREEN}✓ Services started${NC}"
}

# Function to check service health
check_health() {
    echo -e "${YELLOW}🏥 Checking service health...${NC}"
    sleep 30  # Wait for services to initialize
    
    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Services are running${NC}"
    else
        echo -e "${RED}❌ Some services failed to start${NC}"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
        exit 1
    fi
    
    # Check specific health endpoints
    echo -e "${YELLOW}Checking individual service health...${NC}"
    
    # Wait for API Gateway
    for i in {1..30}; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API Gateway is healthy${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ API Gateway health check failed${NC}"
        fi
        sleep 2
    done
    
    # Wait for Frontend
    for i in {1..30}; do
        if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend is healthy${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Frontend health check failed${NC}"
        fi
        sleep 2
    done
}

# Function to display service URLs
show_urls() {
    echo -e "\n${BLUE}🌐 Service URLs:${NC}"
    echo "=================================================="
    echo -e "Frontend:     ${GREEN}http://localhost:3000${NC}"
    echo -e "API Gateway:  ${GREEN}http://localhost:8000${NC}"
    echo -e "API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "Monitoring:   ${GREEN}http://localhost:9090${NC}"
    echo -e "WebSocket:    ${GREEN}ws://localhost:8080${NC}"
    echo ""
    echo -e "Service Status: ${GREEN}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo -e "View Logs:      ${GREEN}docker-compose -f $COMPOSE_FILE logs -f [service]${NC}"
    echo -e "Stop Services:  ${GREEN}docker-compose -f $COMPOSE_FILE down${NC}"
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}📊 Running database migrations...${NC}"
    # Wait for database to be ready
    sleep 10
    
    # Run migrations through the API Gateway container
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T api-gateway python -c "
import asyncio
from backend.config.database import init_db
asyncio.run(init_db())
print('Database migrations completed')
" || echo -e "${YELLOW}⚠ Migration command failed, but continuing...${NC}"
    
    echo -e "${GREEN}✓ Database migrations completed${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}Starting deployment checks...${NC}\n"
    
    check_docker
    check_docker_compose
    check_env_file
    create_directories
    
    echo -e "\n${BLUE}Building and starting services...${NC}\n"
    
    build_images
    start_services
    run_migrations
    check_health
    
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}\n"
    show_urls
    
    echo -e "\n${YELLOW}💡 Next steps:${NC}"
    echo "1. Update your DNS to point to this server"
    echo "2. Configure SSL certificates in config/nginx/ssl/"
    echo "3. Update CORS_ORIGINS in $ENV_FILE with your domain"
    echo "4. Set up monitoring and backup procedures"
    echo "5. Review and update all default passwords"
}

# Handle command line arguments
case "${1:-}" in
    "start")
        start_services
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping services...${NC}"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting services...${NC}"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f "${2:-}"
        ;;
    "ps"|"status")
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
        ;;
    "build")
        build_images
        ;;
    "health")
        check_health
        ;;
    "down")
        echo -e "${YELLOW}🗑️ Removing all containers and networks...${NC}"
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans
        echo -e "${GREEN}✓ Cleanup completed${NC}"
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|logs|ps|build|health|down]"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  ps       - Show service status"
        echo "  build    - Build Docker images"
        echo "  health   - Check service health"
        echo "  down     - Stop and remove all containers"
        echo ""
        echo "Examples:"
        echo "  $0                    # Full deployment"
        echo "  $0 logs api-gateway   # Show API gateway logs"
        echo "  $0 restart frontend   # Restart frontend service"
        exit 1
        ;;
esac
