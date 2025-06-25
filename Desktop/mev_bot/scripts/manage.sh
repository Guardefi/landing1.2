#!/bin/bash

# MevGuardian Management Script
# Provides common management operations for the MevGuardian system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "MevGuardian Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show logs (add service name for specific service)"
    echo "  update      Update and restart services"
    echo "  backup      Backup database"
    echo "  restore     Restore database from backup"
    echo "  mode        Switch bot mode (attack/guardian)"
    echo "  health      Check system health"
    echo "  clean       Clean up Docker resources"
    echo "  help        Show this help message"
}

# Function to check if Docker Compose is available
check_docker() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not found${NC}"
        exit 1
    fi
}

# Function to start services
start_services() {
    echo -e "${BLUE}🚀 Starting MevGuardian services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Services started${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${BLUE}⏹️  Stopping MevGuardian services...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Function to restart services
restart_services() {
    echo -e "${BLUE}🔄 Restarting MevGuardian services...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Services restarted${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    docker-compose ps
}

# Function to show logs
show_logs() {
    if [ -n "$2" ]; then
        echo -e "${BLUE}📋 Showing logs for $2:${NC}"
        docker-compose logs -f "$2"
    else
        echo -e "${BLUE}📋 Showing all logs:${NC}"
        docker-compose logs -f
    fi
}

# Function to update services
update_services() {
    echo -e "${BLUE}🔄 Updating MevGuardian...${NC}"
    docker-compose pull
    docker-compose build
    docker-compose up -d
    echo -e "${GREEN}✅ Update completed${NC}"
}

# Function to backup database
backup_database() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${timestamp}.sql"
    
    echo -e "${BLUE}💾 Creating database backup...${NC}"
    docker-compose exec postgres pg_dump -U mevuser mevguardian > "$backup_file"
    echo -e "${GREEN}✅ Backup created: $backup_file${NC}"
}

# Function to restore database
restore_database() {
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Please specify backup file${NC}"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    echo -e "${BLUE}📥 Restoring database from $2...${NC}"
    docker-compose exec -T postgres psql -U mevuser mevguardian < "$2"
    echo -e "${GREEN}✅ Database restored${NC}"
}

# Function to switch mode
switch_mode() {
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Please specify mode (attack/guardian)${NC}"
        echo "Usage: $0 mode <attack|guardian>"
        exit 1
    fi
    
    echo -e "${BLUE}🔄 Switching to $2 mode...${NC}"
    
    # Update environment variable
    sed -i "s/MEV_MODE=.*/MEV_MODE=$2/" .env
    
    # Restart the main service
    docker-compose restart mev-guardian
    echo -e "${GREEN}✅ Switched to $2 mode${NC}"
}

# Function to check health
check_health() {
    echo -e "${BLUE}🏥 Checking system health...${NC}"
    
    # Check API health
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ API is healthy${NC}"
    else
        echo -e "${RED}❌ API is not responding${NC}"
    fi
    
    # Check database
    if docker-compose exec postgres pg_isready -U mevuser &> /dev/null; then
        echo -e "${GREEN}✅ Database is healthy${NC}"
    else
        echo -e "${RED}❌ Database is not responding${NC}"
    fi
    
    # Check Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis is healthy${NC}"
    else
        echo -e "${RED}❌ Redis is not responding${NC}"
    fi
}

# Function to clean up
clean_up() {
    echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main script logic
check_docker

case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    update)
        update_services
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$@"
        ;;
    mode)
        switch_mode "$@"
        ;;
    health)
        check_health
        ;;
    clean)
        clean_up
        ;;
    help|*)
        usage
        ;;
esac
