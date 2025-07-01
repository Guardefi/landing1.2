#!/bin/bash

# Time Machine Docker Build and Run Script

set -e

echo "🔧 Building Time Machine Docker image..."
docker build -t time-machine:latest .

echo "🚀 Starting Time Machine with Docker Compose..."
docker-compose up -d

echo "✅ Time Machine is starting up!"
echo "📊 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔗 Blockchain node (Anvil): http://localhost:8545"

echo "📝 View logs with:"
echo "   docker-compose logs -f time-machine"

echo "🛑 Stop services with:"
echo "   docker-compose down"
