import logging
import os
import platform
import time
from typing import Any, Dict

import psutil
from database.mongodb_client import MongoDBClient
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.health")

router = APIRouter(tags=["Health"])

# Health check cache to avoid repeated DB calls
health_cache = {"last_check": 0, "status": None, "cache_ttl": 30}  # seconds


@router.get("/", summary="Simple health check")
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint

    Returns:
        Basic status message
    """
    return {"status": "ok"}


@router.get("/health", summary="Docker health check")
async def docker_health_check() -> Dict[str, str]:
    """
    Docker health check endpoint

    Returns:
        Basic status message for Docker health checks
    """
    return {"status": "healthy", "service": "honeypot"}


@router.get("/status", summary="Detailed system status")
async def system_status() -> Dict[str, Any]:
    """
    Detailed system status check

    Returns:
        System status including component health
    """
    # Use cache if recent
    current_time = time.time()
    if (
        current_time - health_cache["last_check"] < health_cache["cache_ttl"]
        and health_cache["status"]
    ):
        return health_cache["status"]

    # Initialize status object
    status = {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": int(current_time),
        "components": {},
    }

    # System info
    try:
        status["components"]["system"] = {
            "status": "ok",
            "hostname": platform.node(),
            "platform": platform.platform(),
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        status["components"]["system"] = {"status": "error", "message": str(e)}
        status["status"] = "degraded"

    # Database connectivity
    try:
        db_client = MongoDBClient()
        await db_client.connect()
        await db_client.database.command("ping")
        status["components"]["database"] = {"status": "ok"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status["components"]["database"] = {"status": "error", "message": str(e)}
        status["status"] = "degraded"

    # Check BlockChain RPC connectivity
    try:
        from blockchain.web3_client import Web3Client

        web3_client = Web3Client()
        # Just initialize, don't need full test
        status["components"]["blockchain"] = {"status": "ok"}
    except Exception as e:
        logger.error(f"Blockchain connectivity check failed: {e}")
        status["components"]["blockchain"] = {"status": "error", "message": str(e)}
        status["status"] = "degraded"

    # Check ML models
    try:
        model_path = "models/ml_models/trained_models/honeypot_classifier.pkl"
        if os.path.exists(model_path):
            model_size = os.path.getsize(model_path)
            status["components"]["ml_models"] = {
                "status": "ok",
                "model_size": model_size,
                "model_exists": True,
            }
        else:
            status["components"]["ml_models"] = {
                "status": "warning",
                "model_exists": False,
                "message": "Models not yet trained",
            }
    except Exception as e:
        logger.error(f"ML model check failed: {e}")
        status["components"]["ml_models"] = {"status": "error", "message": str(e)}
        status["status"] = "degraded"

    # Update cache
    health_cache["status"] = status
    health_cache["last_check"] = current_time

    return status


@router.get("/ready", summary="Readiness probe", status_code=200)
async def readiness_probe(response: Response) -> Dict[str, str]:
    """
    Kubernetes-style readiness probe

    Returns:
        Status indicating if service is ready to receive traffic
    """
    # Check essential services
    try:
        # Check database
        db_client = MongoDBClient()
        await db_client.connect()
        await db_client.database.command("ping")

        # All essential checks passed
        return {"status": "ready"}

    except Exception as e:
        # Service not ready
        logger.error(f"Readiness check failed: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "message": "Essential services unavailable"}


@router.get("/live", summary="Liveness probe", status_code=200)
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes-style liveness probe

    Returns:
        Status indicating if service is alive
    """
    # Simple check that the app is running and responding
    return {"status": "alive"}


@router.get("/metrics-summary", summary="Metrics summary for diagnostics")
async def metrics_summary() -> Dict[str, Any]:
    """
    Summary of key metrics for diagnostic purposes

    Returns:
        Dictionary of metrics summaries
    """
    from api.metrics import DB_CONNECTION_STATUS, SYSTEM_INFO
    from database.cache_service import cache_service

    # Get cached statistics if available
    stats = await cache_service.get_statistics() or {}

    # Augment with live system data
    stats["system"] = {
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "uptime_seconds": int(time.time() - psutil.boot_time()),
    }

    # Add API version
    stats["version"] = settings.VERSION

    # Add worker status if available
    if "workers" not in stats:
        stats["workers"] = {
            "status": "unknown",
            "active": 0,
            "tasks_pending": 0,
            "tasks_completed_24h": 0,
        }

    # Update system metrics
    SYSTEM_INFO.labels(component="api").set(1)

    return stats
