#!/bin/bash
# AI Orchestrator Scanner entrypoint script

set -e

echo "Starting AI Orchestrator Scanner Service..."
echo "🧠 Initializing AI-powered vulnerability scanner orchestrator..."

# Check for required API keys
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: No AI API keys provided. AI analysis will be disabled."
    echo "   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables"
else
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✅ OpenAI API key configured"
    fi
    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "✅ Anthropic API key configured"  
    fi
fi

# Check scanner connectivity
echo "🔍 Checking scanner connectivity..."

# Test scanner endpoints
SLITHER_ENDPOINT="${SLITHER_ENDPOINT:-http://scorpius-scanner-slither:8000}"
MYTHRIL_ENDPOINT="${MYTHRIL_ENDPOINT:-http://scorpius-scanner-mythril:8000}"
MANTICORE_ENDPOINT="${MANTICORE_ENDPOINT:-http://scorpius-scanner-manticore:8000}"

echo "   Slither endpoint: $SLITHER_ENDPOINT"
echo "   Mythril endpoint: $MYTHRIL_ENDPOINT"
echo "   Manticore endpoint: $MANTICORE_ENDPOINT"

# Ensure directories exist
mkdir -p /workspace/input /workspace/output /workspace/temp

# Set permissions
chown -R $(id -u):$(id -g) /workspace/input /workspace/output /workspace/temp

# Export scanner endpoints for the application
export SLITHER_ENDPOINT
export MYTHRIL_ENDPOINT  
export MANTICORE_ENDPOINT

# Start the AI Orchestrator API service
echo "🚀 Starting AI Orchestrator Scanner API on port 8000..."
cd /workspace
exec python app.py 