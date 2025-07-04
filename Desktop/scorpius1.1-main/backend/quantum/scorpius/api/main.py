"""
FastAPI Application for Scorpius Enterprise Platform
Provides REST API and WebSocket endpoints for React dashboard integration.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .. import ScorpiusEngine, get_engine, initialize_scorpius
from ..exceptions import LicenseError, ScorpiusError
from .dashboard import dashboard_router
from .dependencies import (
    get_current_user,
    get_scorpius_engine,
    is_scorpius_initialized,
    set_scorpius_initialized,
)
from .models import *
from .websockets import ConnectionManager

# Initialize FastAPI app
app = FastAPI(
    title="Scorpius Enterprise API",
    description="Enterprise-grade quantum-resistant cryptography and blockchain security platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "*",
    ],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include dashboard router
app.include_router(dashboard_router)

# Global state
logger = logging.getLogger(__name__)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize Scorpius platform on startup."""
    try:
        logger.info("Initializing Scorpius Enterprise Platform...")
        success = await initialize_scorpius(
            config_path="config/enterprise.yml",
            license_key="ENTERPRISE-API-LICENSE-KEY",
        )
        set_scorpius_initialized(success)
        if success:
            logger.info("Scorpius Enterprise Platform initialized successfully")
        else:
            logger.error("Failed to initialize Scorpius platform")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        set_scorpius_initialized(False)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Scorpius Enterprise Platform...")


# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if is_scorpius_initialized() else "unhealthy",
        timestamp=datetime.now(),
        version="2.0.0",
    )


@app.get("/status", response_model=PlatformStatusResponse)
async def get_platform_status(engine: ScorpiusEngine = Depends(get_scorpius_engine)):
    """Get comprehensive platform status."""
    try:
        status_data = await engine.get_platform_status()
        return PlatformStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform status: {str(e)}",
        )


# ============================================================================
# QUANTUM CRYPTOGRAPHY ENDPOINTS
# ============================================================================


@app.post("/quantum/encrypt", response_model=QuantumEncryptResponse)
async def quantum_encrypt(
    request: QuantumEncryptRequest,
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Encrypt data using quantum-resistant cryptography."""
    try:
        result = await engine.quantum_encrypt(
            message=request.message.encode(),
            algorithm=request.algorithm,
            security_level=request.security_level,
        )

        # Broadcast to WebSocket clients
        await manager.broadcast(
            {
                "type": "quantum_operation",
                "operation": "encrypt",
                "user": user["user_id"],
                "timestamp": datetime.now().isoformat(),
            }
        )

        return QuantumEncryptResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}",
        )


@app.post("/quantum/generate-keys", response_model=KeyGenerationResponse)
async def generate_quantum_keys(
    request: KeyGenerationRequest,
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Generate quantum-resistant key pairs."""
    try:
        # Simulate key generation (integrate with your quantum engine)
        result = {
            "key_id": f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "algorithm": request.algorithm,
            "security_level": request.security_level,
            "public_key": "quantum_public_key_placeholder",
            "created_at": datetime.now().isoformat(),
        }

        # Broadcast to WebSocket clients
        await manager.broadcast(
            {
                "type": "key_generation",
                "key_id": result["key_id"],
                "user": user["user_id"],
                "timestamp": datetime.now().isoformat(),
            }
        )

        return KeyGenerationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key generation failed: {str(e)}",
        )


# ============================================================================
# SECURITY SCANNING ENDPOINTS
# ============================================================================


@app.post("/security/scan", response_model=SecurityScanResponse)
async def security_scan(
    request: SecurityScanRequest,
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Perform security scan on target."""
    try:
        result = await engine.security_scan(
            target=request.target, scan_type=request.scan_type
        )

        # Broadcast scan results to WebSocket clients
        await manager.broadcast(
            {
                "type": "security_scan",
                "target": request.target,
                "scan_type": request.scan_type,
                "threats_found": result.get("threats_found", 0),
                "user": user["user_id"],
                "timestamp": datetime.now().isoformat(),
            }
        )

        return SecurityScanResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Security scan failed: {str(e)}",
        )


@app.get("/security/threats", response_model=List[ThreatAlert])
async def get_active_threats(
    limit: int = 100,
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Get active threat alerts."""
    try:
        # Simulate threat data (integrate with your security engine)
        threats = [
            {
                "id": f"threat_{i}",
                "level": "medium" if i % 2 else "high",
                "title": f"Suspicious Activity Detected #{i}",
                "description": "Potential security threat detected in transaction pattern",
                "detected_at": datetime.now().isoformat(),
                "source": "AI Detection Engine",
                "status": "active",
            }
            for i in range(min(limit, 5))  # Sample data
        ]

        return [ThreatAlert(**threat) for threat in threats]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get threats: {str(e)}",
        )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================


@app.post("/analytics/reports", response_model=AnalyticsReportResponse)
async def generate_analytics_report(
    request: AnalyticsReportRequest,
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Generate analytics report."""
    try:
        result = await engine.generate_analytics_report(
            report_type=request.report_type, timeframe=request.timeframe
        )

        return AnalyticsReportResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@app.get("/analytics/metrics", response_model=MetricsResponse)
async def get_platform_metrics(
    timeframe: str = "1h",
    engine: ScorpiusEngine = Depends(get_scorpius_engine),
    user: dict = Depends(get_current_user),
):
    """Get platform performance metrics."""
    try:
        # Generate sample metrics (integrate with your metrics collection)
        metrics = {
            "quantum_operations": {
                "encryptions": 1250,
                "decryptions": 1180,
                "key_generations": 45,
                "signatures": 890,
            },
            "security_scans": {
                "total_scans": 156,
                "threats_detected": 12,
                "false_positives": 2,
                "avg_scan_time": 1.2,
            },
            "performance": {
                "avg_response_time": 45.6,
                "requests_per_second": 234.5,
                "cpu_usage": 67.8,
                "memory_usage": 82.1,
            },
            "timestamp": datetime.now().isoformat(),
        }

        return MetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}",
        )


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================


@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "subscribe":
                # Client wants to subscribe to specific events
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscription_confirmed",
                            "events": message.get("events", []),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )
            elif message.get("type") == "ping":
                # Heartbeat
                await websocket.send_text(
                    json.dumps(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    await manager.connect(websocket, "metrics")
    try:
        while True:
            # Send metrics every 5 seconds
            await asyncio.sleep(5)

            # Generate real-time metrics
            metrics = {
                "type": "metrics_update",
                "data": {
                    "cpu_usage": 65.4,
                    "memory_usage": 78.2,
                    "active_connections": len(manager.active_connections),
                    "operations_per_minute": 456,
                    "threats_detected_today": 23,
                },
                "timestamp": datetime.now().isoformat(),
            }

            await websocket.send_text(json.dumps(metrics))

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================


@app.get("/config", response_model=ConfigResponse)
async def get_configuration(user: dict = Depends(get_current_user)):
    """Get platform configuration."""
    try:
        # Return sanitized configuration (no sensitive data)
        config = {
            "platform_version": "2.0.0",
            "enterprise_edition": True,
            "features": {
                "quantum_crypto": True,
                "ai_security": True,
                "real_time_analytics": True,
                "clustering": True,
            },
            "limits": {
                "max_concurrent_scans": 100,
                "max_key_generations_per_hour": 1000,
                "retention_days": 365,
            },
        }

        return ConfigResponse(**config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}",
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Scorpius Enterprise API",
        "version": "2.0.0",
        "description": "Enterprise-grade quantum-resistant cryptography and blockchain security platform",
        "documentation": "/docs",
        "websocket_endpoints": {"dashboard": "/ws/dashboard", "metrics": "/ws/metrics"},
        "status": "operational" if is_scorpius_initialized() else "initializing",
    }


@app.get("/api/v1/info")
async def api_info():
    """API information and available endpoints."""
    return {
        "api_version": "v1",
        "platform_version": "2.0.0",
        "endpoints": {
            "quantum": {
                "encrypt": "/quantum/encrypt",
                "generate_keys": "/quantum/generate-keys",
            },
            "security": {"scan": "/security/scan", "threats": "/security/threats"},
            "analytics": {
                "reports": "/analytics/reports",
                "metrics": "/analytics/metrics",
            },
            "websockets": {"dashboard": "/ws/dashboard", "metrics": "/ws/metrics"},
        },
    }


# Error handlers
@app.exception_handler(ScorpiusError)
async def scorpius_exception_handler(request, exc):
    return JSONResponse(
        status_code=500, content={"detail": f"Scorpius Error: {str(exc)}"}
    )


@app.exception_handler(LicenseError)
async def license_exception_handler(request, exc):
    return JSONResponse(
        status_code=403, content={"detail": f"License Error: {str(exc)}"}
    )


# For running the server directly
if __name__ == "__main__":
    uvicorn.run(
        "scorpius.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
