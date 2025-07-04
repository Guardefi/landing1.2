#!/bin/bash
# Manticore plugin entrypoint script

set -e

echo "Starting Manticore Analysis Service..."
echo "Manticore version: $(python -c 'import manticore; print(manticore.__version__)')"

# Ensure directories exist
mkdir -p /workspace/input /workspace/output

# Start the FastAPI service
cd /workspace
python app.py
