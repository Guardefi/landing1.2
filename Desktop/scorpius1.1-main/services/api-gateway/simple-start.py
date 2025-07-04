#!/usr/bin/env python3
"""
Simple startup script for Scorpius API Gateway
This replaces the problematic entrypoint.sh script
"""

import os
import sys
import time
import subprocess
import socket
from pathlib import Path

def log(message):
    print(f"[STARTUP] {message}", flush=True)

def check_database_connection():
    """Wait for database to be ready"""
    db_host = os.environ.get('POSTGRES_HOST', 'postgres')
    db_port = int(os.environ.get('POSTGRES_PORT', '5432'))
    
    log(f"Waiting for database at {db_host}:{db_port}")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((db_host, db_port))
            sock.close()
            
            if result == 0:
                log("✅ Database is ready")
                return True
                
        except Exception as e:
            log(f"Database connection attempt {attempt + 1} failed: {e}")
            
        time.sleep(2)
        print(".", end="", flush=True)
    
    log("❌ Database failed to become ready")
    return False

def run_migrations():
    """Run database migrations if available"""
    if Path("alembic.ini").exists() and Path("migrations").exists():
        log("Running database migrations...")
        try:
            subprocess.run(["alembic", "-c", "alembic.ini", "upgrade", "head"], check=True)
            log("✅ Migrations completed")
        except subprocess.CalledProcessError as e:
            log(f"⚠️  Migrations failed: {e}")
    else:
        log("No migrations found, skipping...")

def start_server():
    """Start the API server"""
    port = os.environ.get('PORT', '8000')
    log(f"Starting API server on port {port}")
    
    # Start the server
    cmd = [
        "gunicorn",
        "main:app",
        "-k", "uvicorn.workers.UvicornWorker",
        "-b", f"0.0.0.0:{port}",
        "--workers", "1",
        "--timeout", "60",
        "--log-level", "info"
    ]
    
    log(f"Executing: {' '.join(cmd)}")
    os.execvp(cmd[0], cmd)

def main():
    """Main startup process"""
    log("🚀 Starting Scorpius API Gateway")
    
    # Change to app directory
    os.chdir("/app")
    
    # Check database connection
    if not check_database_connection():
        log("❌ Failed to connect to database")
        sys.exit(1)
    
    # Run migrations
    run_migrations()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 