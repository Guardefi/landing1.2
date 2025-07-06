#!/bin/bash

# Scorpius Enterprise Platform - DevContainer Start Script
# This script runs every time the dev container starts

set -e

echo "🚀 Starting Scorpius Enterprise Platform development environment..."

# Check if required services are running
echo "🔍 Checking service status..."

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo "⚠️  Docker daemon not available"
    exit 1
fi

# Check if development services should be auto-started
if [ "${AUTO_START_SERVICES:-true}" = "true" ]; then
    echo "🏗️  Starting development services..."
    
    # Start core development services
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml up -d postgres redis
        
        # Wait for services to be ready
        echo "⏳ Waiting for services to be ready..."
        sleep 10
        
        # Check PostgreSQL
        until docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U scorpius; do
            echo "Waiting for PostgreSQL..."
            sleep 2
        done
        
        # Check Redis
        until docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping; do
            echo "Waiting for Redis..."
            sleep 2
        done
        
        echo "✅ Core services are ready!"
    fi
fi

# Set up port forwarding for Kubernetes services (if running)
if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
    echo "☸️  Setting up Kubernetes port forwarding..."
    
    # Port forward Prometheus (if running)
    if kubectl get service prometheus-server -n monitoring &> /dev/null; then
        kubectl port-forward -n monitoring service/prometheus-server 9090:80 &
        echo "📊 Prometheus available at http://localhost:9090"
    fi
    
    # Port forward Grafana (if running)
    if kubectl get service grafana -n monitoring &> /dev/null; then
        kubectl port-forward -n monitoring service/grafana 3001:80 &
        echo "📈 Grafana available at http://localhost:3001"
    fi
    
    # Port forward OpenCost (if running)
    if kubectl get service opencost -n opencost &> /dev/null; then
        kubectl port-forward -n opencost service/opencost 9003:9003 &
        echo "💰 OpenCost available at http://localhost:9003"
    fi
fi

# Start monitoring processes
echo "📊 Starting development monitoring..."

# Background process to monitor resource usage
{
    while true; do
        if command -v docker &> /dev/null; then
            echo "$(date): Docker containers: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | tail -n +2 | wc -l)" >> /tmp/dev-monitoring.log
        fi
        sleep 60
    done
} &

# Background process to monitor costs (if OpenCost is available)
{
    while true; do
        if curl -s http://localhost:9003/healthz &> /dev/null; then
            cost_data=$(curl -s "http://localhost:9003/model/allocation?window=1d" | jq -r '.data[0].totalCost // 0' 2>/dev/null || echo "0")
            echo "$(date): Daily cost: $${cost_data}" >> /tmp/cost-monitoring.log
        fi
        sleep 3600  # Check hourly
    done
} &

# Set up development environment variables
echo "⚙️  Setting up environment variables..."
export SCORPIUS_ENV=development
export SCORPIUS_DEBUG=true
export PROMETHEUS_URL=http://localhost:9090
export GRAFANA_URL=http://localhost:3001
export OPENCOST_URL=http://localhost:9003

# Show helpful information
echo "✅ Development environment started successfully!"
echo ""
echo "🌐 Available Services:"
echo "  - API Gateway: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - Documentation: http://localhost:8080"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001 (admin/admin)"
echo "  - OpenCost: http://localhost:9003"
echo ""
echo "🛠️  Development Commands:"
echo "  make dev          - Start all services"
echo "  make test         - Run test suite"
echo "  make lint         - Run linting"
echo "  make build        - Build all images"
echo "  make clean        - Clean up environment"
echo "  make help         - Show all commands"
echo ""
echo "📊 Monitoring:"
echo "  make check-cost   - Check current costs"
echo "  make check-health - Check service health"
echo "  make logs         - View all service logs"
echo ""
echo "🧪 Testing:"
echo "  make unit-test    - Run unit tests"
echo "  make e2e-test     - Run end-to-end tests"
echo "  make chaos-test   - Run chaos engineering tests"
echo "  make perf-test    - Run performance tests"
echo ""
echo "Happy coding! 🎉"
