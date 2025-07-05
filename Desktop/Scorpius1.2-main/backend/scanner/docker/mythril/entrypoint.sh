#!/bin/bash
# Mythril plugin entrypoint script

set -e

echo "Starting Mythril Analysis Service..."
echo "Mythril version: $(myth version)"

# Ensure directories exist
mkdir -p /workspace/input /workspace/output

# Start the FastAPI service
cd /workspace
python app.py
