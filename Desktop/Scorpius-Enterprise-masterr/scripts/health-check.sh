#!/bin/bash
# Health check script for Scorpius Enterprise services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Scorpius Enterprise Health Check...${NC}"

# Check if we're in a container
if [ -f /.dockerenv ]; then
    echo -e "${GREEN}✓ Running in Docker container${NC}"
else
    echo -e "${YELLOW}⚠ Not running in Docker container${NC}"
fi

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local service_name=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $service_name is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ $service_name is not responding${NC}"
        return 1
    fi
}

# Function to check Redis
check_redis() {
    if command -v redis-cli > /dev/null 2>&1; then
        if redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} -a ${REDIS_PASSWORD:-scorpius_prod_2024} ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is healthy${NC}"
            return 0
        else
            echo -e "${RED}✗ Redis is not responding${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Redis CLI not available, skipping Redis check${NC}"
        return 0
    fi
}

# Function to check PostgreSQL
check_postgres() {
    if command -v pg_isready > /dev/null 2>&1; then
        if pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-scorpius} > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
            return 0
        else
            echo -e "${RED}✗ PostgreSQL is not responding${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ pg_isready not available, skipping PostgreSQL check${NC}"
        return 0
    fi
}

# Main health checks
health_status=0

# Check basic Python environment
if python --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Python is available${NC}"
else
    echo -e "${RED}✗ Python is not available${NC}"
    health_status=1
fi

# Check if main application directories exist
for dir in "/app/backend" "/app/services" "/app/packages"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ Directory $dir exists${NC}"
    else
        echo -e "${RED}✗ Directory $dir is missing${NC}"
        health_status=1
    fi
done

# Check log directory is writable
if [ -w "/app/logs" ]; then
    echo -e "${GREEN}✓ Log directory is writable${NC}"
else
    echo -e "${RED}✗ Log directory is not writable${NC}"
    health_status=1
fi

# Check Redis (if available)
check_redis || health_status=1

# Check PostgreSQL (if available)
check_postgres || health_status=1

# Check specific service endpoints based on SERVICE_NAME
case "${SERVICE_NAME:-api-gateway}" in
    "api-gateway")
        check_http "http://localhost:8000/health" "API Gateway" || health_status=1
        ;;
    "scanner")
        check_http "http://localhost:8000/health" "Scanner Service" || health_status=1
        ;;
    "honeypot")
        check_http "http://localhost:8000/health" "Honeypot Service" || health_status=1
        ;;
    "mempool")
        check_http "http://localhost:8000/health" "Mempool Service" || health_status=1
        ;;
    "bridge")
        check_http "http://localhost:8000/health" "Bridge Service" || health_status=1
        ;;
    "quantum")
        check_http "http://localhost:8000/health" "Quantum Service" || health_status=1
        ;;
    "reporting")
        check_http "http://localhost:8000/health" "Reporting Service" || health_status=1
        ;;
    "monitoring")
        check_http "http://localhost:9090/health" "Monitoring Service" || health_status=1
        ;;
    "websocket")
        check_http "http://localhost:8080/health" "WebSocket Service" || health_status=1
        ;;
    *)
        echo -e "${YELLOW}⚠ Unknown service type, performing basic checks only${NC}"
        ;;
esac

# Final status
if [ $health_status -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All health checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some health checks failed!${NC}"
    exit 1
fi
