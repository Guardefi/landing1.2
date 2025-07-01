#!/bin/bash
# Slither plugin entrypoint script

set -e

echo "Starting Slither Analysis Service..."
echo "Slither version: $(slither --version)"

# Ensure directories exist
mkdir -p /workspace/input /workspace/output

# Start the FastAPI service
cd /workspace
python app.py
