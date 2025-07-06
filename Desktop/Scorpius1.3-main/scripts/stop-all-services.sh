#!/bin/bash

# Scorpius Backend Services Stop Script
# This script stops all backend services

echo "🛑 Stopping Scorpius Backend Services..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to stop service on a specific port
stop_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${BLUE}Stopping $service_name on port $port...${NC}"
    
    # Find process using the port
    local pid=$(lsof -ti:$port)
    
    if [ -n "$pid" ]; then
        echo "Found PID: $pid"
        kill -TERM $pid 2>/dev/null
        
        # Wait for graceful shutdown
        sleep 2
        
        # Check if still running
        if kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}Force killing $service_name...${NC}"
            kill -KILL $pid 2>/dev/null
        fi
        
        echo -e "${GREEN}✓ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}No process found on port $port${NC}"
    fi
}

# Stop all services by port
stop_port 8000 "API Gateway"
stop_port 8001 "Scanner Service"
stop_port 8002 "Honeypot Service"  
stop_port 8003 "Mempool Service"
stop_port 8004 "Bridge Service"
stop_port 8005 "Bytecode Service"
stop_port 8006 "Wallet Guard"
stop_port 8007 "Time Machine"
stop_port 8008 "Quantum Service"

# Also stop any uvicorn/python processes that might be running our services
echo -e "\n${BLUE}Checking for remaining Python/Uvicorn processes...${NC}"

# Kill any remaining uvicorn processes
pkill -f "uvicorn.*main:app" 2>/dev/null && echo -e "${GREEN}Stopped remaining uvicorn processes${NC}"

# Kill any Python processes running our main files
pkill -f "python.*main.py" 2>/dev/null && echo -e "${GREEN}Stopped remaining Python main processes${NC}"
pkill -f "python.*app.py" 2>/dev/null && echo -e "${GREEN}Stopped remaining Python app processes${NC}"

echo -e "\n${GREEN}🏁 All Scorpius backend services have been stopped!${NC}"

# Check if any ports are still in use
echo -e "\n${BLUE}Verifying all ports are free...${NC}"
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8008; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}⚠️  Port $port is still in use${NC}"
    else
        echo -e "${GREEN}✓ Port $port is free${NC}"
    fi
done

echo -e "\n${YELLOW}💡 To start services again, run: ./scripts/start-all-services.sh${NC}"
