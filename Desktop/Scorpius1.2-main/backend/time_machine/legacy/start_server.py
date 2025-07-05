#!/usr/bin/env python3
"""
Simple server startup script for Time Machine
"""

import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our API routes
from packages.core.api.routes import router as api_router

app = FastAPI(
    title="Time Machine - Blockchain Forensics",
    description="Advanced blockchain forensic analysis and exploit replay platform",
    version="1.0.0",
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "time-machine"}


# Serve the React UI (if built)
ui_build_path = project_root / "ui" / "build"
if ui_build_path.exists():
    app.mount(
        "/static", StaticFiles(directory=str(ui_build_path / "static")), name="static"
    )

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Serve React app for all non-API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        return FileResponse(str(ui_build_path / "index.html"))

else:

    @app.get("/")
    async def root():
        return {
            "message": "Time Machine API Server",
            "status": "running",
            "ui_available": False,
            "note": "Build the React UI to serve the frontend",
        }


if __name__ == "__main__":
    print("🕰️  Starting Time Machine Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📍 API docs at: http://localhost:8000/docs")
    print("📍 Health check at: http://localhost:8000/health")

    uvicorn.run(
        "start_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
