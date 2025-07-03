#!/bin/bash
# MythX plugin entrypoint script

set -e

echo "Starting MythX Analysis Service..."

# Check if API key is provided
if [ -z "$MYTHX_API_KEY" ]; then
    echo "Warning: MYTHX_API_KEY not provided. MythX functionality will be limited."
fi

# Ensure directories exist
mkdir -p /workspace/input /workspace/output

# Start the FastAPI service
cd /workspace
node app.js
