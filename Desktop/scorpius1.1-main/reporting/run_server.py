#!/usr/bin/env python3
"""
Scorpius Enterprise Reporting System
====================================

Entry point for running the FastAPI application.
"""

import uvicorn
from app import app
from config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("🚀 Starting Scorpius Enterprise Reporting System...")
    print(f"📍 Host: {settings.api.host}")
    print(f"🔌 Port: {settings.api.port}")
    print(f"🐛 Debug: {settings.debug}")
    
    uvicorn.run(
        app,
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
