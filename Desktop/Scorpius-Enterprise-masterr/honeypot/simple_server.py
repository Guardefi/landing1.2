#!/usr/bin/env python3
"""
Simple FastAPI server for testing basic functionality
"""
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="Honeypot Detector API",
    description="API for detecting honeypot smart contracts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Honeypot Detector API", "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-24T12:00:00Z",
        "services": {
            "api": "healthy",
            "database": "not_connected",
            "cache": "not_connected",
        },
    }


@app.post("/api/v1/analyze")
async def analyze_contract(contract_data: Dict[str, Any]):
    """Analyze a smart contract for honeypot patterns"""
    return {
        "contract_address": contract_data.get("address", "0x..."),
        "is_honeypot": False,
        "confidence": 0.95,
        "risk_score": 0.1,
        "analysis_time": "2025-06-24T12:00:00Z",
        "findings": [
            {
                "type": "info",
                "description": "Contract analysis completed",
                "severity": "low",
            }
        ],
        "metadata": {"analyzer_version": "1.0.0", "analysis_method": "static"},
    }


@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "total_analyses": 1250,
        "honeypots_detected": 180,
        "contracts_scanned": 1070,
        "detection_rate": 14.4,
        "avg_analysis_time": 2.3,
        "last_updated": "2025-06-24T12:00:00Z",
    }


@app.get("/api/v1/dashboard/recent")
async def get_recent_analyses():
    """Get recent analyses"""
    return {
        "analyses": [
            {
                "id": "analysis_1",
                "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
                "is_honeypot": True,
                "risk_score": 0.85,
                "analyzed_at": "2025-06-24T11:45:00Z",
            },
            {
                "id": "analysis_2",
                "contract_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "is_honeypot": False,
                "risk_score": 0.15,
                "analyzed_at": "2025-06-24T11:30:00Z",
            },
        ]
    }


@app.get("/api/v1/dashboard/trends")
async def get_trend_data():
    """Get trend data for dashboard"""
    return {
        "daily_analyses": [
            {"date": "2025-06-24", "count": 45, "honeypots": 8},
            {"date": "2025-06-23", "count": 52, "honeypots": 12},
            {"date": "2025-06-22", "count": 38, "honeypots": 5},
            {"date": "2025-06-21", "count": 41, "honeypots": 9},
            {"date": "2025-06-20", "count": 47, "honeypots": 11},
        ],
        "risk_distribution": {"low": 65, "medium": 25, "high": 10},
    }


if __name__ == "__main__":
    print("🚀 Starting Simple Honeypot Detector API Server...")
    print(f"📁 Working directory: {PROJECT_ROOT}")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Dashboard API: http://localhost:8000/api/v1/dashboard/stats")
    print("🛡️  Analysis API: http://localhost:8000/api/v1/analyze")

    uvicorn.run(
        "simple_server:app", host="0.0.0.0", port=8000, reload=True, access_log=True
    )
