#!/bin/bash

# Docker entrypoint script for Scorpius Enterprise

set -e

# Initialize environment
echo "Starting Scorpius Enterprise Platform..."

# Check if data directories exist
if [ ! -d "/data/logs" ]; then
    mkdir -p /data/logs
fi

if [ ! -d "/data/snapshots" ]; then
    mkdir -p /data/snapshots
fi

if [ ! -d "/data/keys" ]; then
    mkdir -p /data/keys
fi

# Set proper permissions
chown -R app:app /data

# Wait for dependencies (if running with docker-compose)
if [ "$WAIT_FOR_POSTGRES" = "true" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z postgres 5432; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
fi

if [ "$WAIT_FOR_REDIS" = "true" ]; then
    echo "Waiting for Redis..."
    while ! nc -z redis 6379; do
        sleep 1
    done
    echo "Redis is ready!"
fi

# Run database migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    # python -m alembic upgrade head
fi

# Start the application
echo "Starting Scorpius with command: $@"
exec "$@"
