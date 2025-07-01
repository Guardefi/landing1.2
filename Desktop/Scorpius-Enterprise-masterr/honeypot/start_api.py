#!/usr/bin/env python3
"""
Startup script for the Honeypot Detector API
"""
import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from api.main import app


def main():
    """Run the FastAPI application"""
    print("🚀 Starting Honeypot Detector API...")
    print("📝 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("📊 Dashboard API at: http://localhost:8000/api/v1/dashboard/stats")
    print("🛡️  Analysis API at: http://localhost:8000/api/v1/analyze")

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
