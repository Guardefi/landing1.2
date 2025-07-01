#!/bin/bash

# MevGuardian Deployment Script
# Automates the deployment process for production environments

set -e

echo "🚀 Starting MevGuardian deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before proceeding.${NC}"
    read -p "Press enter to continue after editing .env file..."
fi

# Validate required environment variables
echo "🔍 Validating environment configuration..."
source .env

required_vars=("RPC_URL" "PRIVATE_KEY" "POSTGRES_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set.${NC}"
        exit 1
    fi
done

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs config monitoring/grafana/dashboards

# Build the application
echo "🔨 Building MevGuardian Docker image..."
docker-compose build

# Start the database first
echo "🗄️  Starting database services..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Start all services
echo "🚀 Starting all MevGuardian services..."
docker-compose up -d

# Wait for services to start
sleep 15

# Check service health
echo "🏥 Checking service health..."
services=("mev-guardian" "postgres" "redis" "prometheus" "grafana")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✅ $service is running${NC}"
    else
        echo -e "${RED}❌ $service failed to start${NC}"
        docker-compose logs "$service"
    fi
done

# Display access information
echo ""
echo -e "${GREEN}🎉 MevGuardian deployment completed!${NC}"
echo ""
echo "📊 Service URLs:"
echo "  • MevGuardian API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "  • Prometheus: http://localhost:9090"
echo ""
echo "📋 Management Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart: docker-compose restart"
echo "  • Update: docker-compose pull && docker-compose up -d"
echo ""
echo -e "${YELLOW}⚠️  Remember to change default passwords in production!${NC}"
