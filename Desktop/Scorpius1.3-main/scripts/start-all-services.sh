#!/bin/bash

# Scorpius Backend Services Startup Script
# This script starts all backend services on their designated ports

echo "🚀 Starting Scorpius Backend Services..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}Port $port is available${NC}"
        return 0
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local start_command=$4
    
    echo -e "\n${BLUE}Starting $service_name on port $port...${NC}"
    
    if check_port $port; then
        cd "$service_path" || {
            echo -e "${RED}Failed to navigate to $service_path${NC}"
            return 1
        }
        
        echo "Running: $start_command"
        eval "$start_command" &
        local pid=$!
        echo "PID: $pid"
        
        # Wait a bit and check if process is still running
        sleep 2
        if kill -0 $pid 2>/dev/null; then
            echo -e "${GREEN}✓ $service_name started successfully${NC}"
        else
            echo -e "${RED}✗ $service_name failed to start${NC}"
        fi
    else
        echo -e "${YELLOW}Skipping $service_name (port in use)${NC}"
    fi
}

# Create logs directory
mkdir -p logs

echo -e "${BLUE}Checking Python virtual environment...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
}

echo -e "${GREEN}Virtual environment activated${NC}"

# Start all services
echo -e "\n${BLUE}Starting backend services...${NC}"

# Main API Gateway (Port 8000) - if exists
if [ -d "services/api-gateway" ]; then
    start_service "API Gateway" "services/api-gateway" 8000 "python main.py > ../../logs/api-gateway.log 2>&1"
fi

# Scanner Service (Port 8001)
if [ -d "backend/scanner" ]; then
    start_service "Scanner Service" "backend/scanner" 8001 "python -m api.main > ../../logs/scanner.log 2>&1"
fi

# Honeypot Service (Port 8002)
if [ -d "backend/honeypot" ]; then
    start_service "Honeypot Service" "backend/honeypot" 8002 "python -m api.main > ../../logs/honeypot.log 2>&1"
fi

# Mempool Service (Port 8003)
if [ -d "backend/mempool" ]; then
    start_service "Mempool Service" "backend/mempool" 8003 "python -m api.main > ../../logs/mempool.log 2>&1"
fi

# Bridge Service (Port 8004)
if [ -d "backend/bridge" ]; then
    start_service "Bridge Service" "backend/bridge" 8004 "python main.py > ../../logs/bridge.log 2>&1"
fi

# Bytecode Service (Port 8005)
if [ -d "backend/Bytecode" ]; then
    start_service "Bytecode Service" "backend/Bytecode" 8005 "python -m api.main > ../../logs/bytecode.log 2>&1"
fi

# Wallet Guard Service (Port 8006)
if [ -d "backend/wallet_guard" ]; then
    start_service "Wallet Guard" "backend/wallet_guard" 8006 "python app.py > ../../logs/wallet.log 2>&1"
fi

# Time Machine Service (Port 8007)
if [ -d "backend/time_machine" ]; then
    start_service "Time Machine" "backend/time_machine" 8007 "python app.py > ../../logs/time-machine.log 2>&1"
fi

# Quantum Service (Port 8008)
if [ -d "backend/quantum" ]; then
    start_service "Quantum Service" "backend/quantum" 8008 "python -m scorpius.api.main > ../../logs/quantum.log 2>&1"
fi

echo -e "\n${GREEN}🎉 All services startup completed!${NC}"
echo -e "${BLUE}📋 Service Status:${NC}"
echo "• API Gateway: http://localhost:8000"
echo "• Scanner: http://localhost:8001"
echo "• Honeypot: http://localhost:8002"
echo "• Mempool: http://localhost:8003"
echo "• Bridge: http://localhost:8004"
echo "• Bytecode: http://localhost:8005"
echo "• Wallet Guard: http://localhost:8006"
echo "• Time Machine: http://localhost:8007"
echo "• Quantum: http://localhost:8008"

echo -e "\n${YELLOW}📝 Logs are available in the 'logs/' directory${NC}"
echo -e "${BLUE}🔗 Frontend will be available at: http://localhost:3000${NC}"
echo -e "${YELLOW}⚠️  Some services may take a few seconds to fully initialize${NC}"

echo -e "\n${GREEN}To stop all services, run: ./scripts/stop-all-services.sh${NC}"
