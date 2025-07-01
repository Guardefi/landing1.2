#!/bin/bash
# Scorpius Enterprise Scanner - Stop Script (Linux/Mac)
# Stops all scanner plugins and backend services

echo "🛑 Stopping Scorpius Enterprise Scanner..."
echo "=========================================="

# Navigate to scanner directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop all services
echo "🔄 Stopping all services..."
docker-compose down --remove-orphans

# Show final status
echo "📊 Final Status:"
docker-compose ps

echo ""
echo "✅ Scorpius Enterprise Scanner stopped successfully!"
