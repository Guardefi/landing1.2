#!/usr/bin/env python3
"""
SCORPIUS Bytecode Similarity Engine
Simple entrypoint for production deployment
"""

import os
import sys
from pathlib import Path

import uvicorn

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entrypoint for the SCORPIUS API server."""

    # Configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    reload = os.getenv("API_RELOAD", "false").lower() == "true"

    print(f"🚀 Starting SCORPIUS API server on {host}:{port}")
    print(f"📊 Workers: {workers}, Log Level: {log_level}")

    # Start the server
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        log_level=log_level,
        reload=reload,
        access_log=True,
    )


if __name__ == "__main__":
    main()
