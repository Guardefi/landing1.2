#!/bin/bash
# Scorpius Enterprise Scanner - Startup Script (Linux/Mac)
# Starts all scanner plugins and backend services

echo "🔥 Starting Scorpius Enterprise Vulnerability Scanner..."
echo "================================================"

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Navigate to scanner directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start all services
echo "🔧 Building and starting all services..."
docker-compose up -d --build

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Display service URLs
echo ""
echo "🌐 Service URLs:"
echo "   Main Scanner API:    http://localhost:8090"
echo "   Slither Plugin:      http://localhost:8091"
echo "   Mythril Plugin:      http://localhost:8092"
echo "   Manticore Plugin:    http://localhost:8093"
echo "   MythX Plugin:        http://localhost:8094"
echo "   PostgreSQL DB:       localhost:5433"
echo "   Redis Cache:         localhost:6380"

echo ""
echo "🚀 Scorpius Enterprise Scanner is now running!"
echo "📝 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
