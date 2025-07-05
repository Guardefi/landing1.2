#!/bin/sh

# Wait for PostgreSQL to be ready
while ! nc -z postgres 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

# Run the main application
python main.py
