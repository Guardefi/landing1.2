#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z postgres 5432; do
    sleep 1
done

echo "Database is ready"

# Start the application
exec uvicorn app:app --host 0.0.0.0 --port ${PORT}
