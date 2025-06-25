"""
Scorpius FastAPI Backend - Minimal Production Version
Core FastAPI application without advanced monitoring modules
"""



# Configure structured logging with loguru
loguru_logger.remove()  # Remove default handler
loguru_logger.add(
    "logs/scorpius_{time:YYYY-MM-DD}.log",
    rotation="daily",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
    serialize=True,  # JSON format
)
loguru_logger.add(
    lambda msg: print(msg, end=""),  # Console output
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Initialize Redis for rate limiting (fallback to in-memory if Redis unavailable)
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )
    redis_client.ping()  # Test connection
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}",
    )
    loguru_logger.info("✅ Redis connected for rate limiting")
except Exception as e:
    loguru_logger.warning(f"Redis unavailable, using in-memory rate limiting: {e}")
    limiter = Limiter(key_func=get_remote_address)

# Configure legacy logging for compatibility
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import existing FastAPI modules

# Import new FastAPI routes (replacing Flask)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for initialization and cleanup."""
    loguru_logger.info("🚀 Starting Scorpius X - Blockchain Security Platform")

    # Initialize database
    try:

        init_database()
        loguru_logger.info("✅ Database initialized")
    except Exception as e:
        loguru_logger.error(f"❌ Database initialization error: {e}")

    loguru_logger.info("🌟 Scorpius X ready for production!")

    yield

    # Cleanup
    loguru_logger.info("🛑 Shutting down Scorpius X")


app = FastAPI(
    title="Scorpius X • Blockchain Security Platform",
    description="Advanced blockchain security with MEV protection and mempool monitoring",
    version="2.0.0",
    lifespan=lifespan,
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Prometheus metrics instrumentation

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/healthz", "/readyz"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="scorpius_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# Production-ready CORS configuration
allowed_origins = (
    os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if os.getenv("CORS_ALLOWED_ORIGINS")
    else []
)
if not allowed_origins:
    # Default to DENY in production, allow localhost in development
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "development":
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    else:
        allowed_origins = []  # DENY by default in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    expose_headers=[
        "Content-Type",
        "X-API-Version",
        "X-Request-ID",
        "X-Scorpius-Version",
    ],
)

# Register existing routers
for r in [
    dashboard_router,
    system_router,
    scanner_router,
    simulation_router,
]:
    app.include_router(r, prefix="/api")

# Register new FastAPI routers (replacing Flask)
app.include_router(auth_fastapi_router)
app.include_router(mev_fastapi_router)
app.include_router(mempool_fastapi_router)

# =============================================================================
# OBSERVABILITY & HEALTH CHECK ENDPOINTS
# =============================================================================


@app.get("/healthz")
async def health_check():
    """Kubernetes-style health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "scorpius-backend",
    }


@app.get("/readyz")
async def readiness_check():
    """Kubernetes-style readiness check endpoint"""
    try:
        # Check database connectivity

        db = next(get_db())
        db.execute("SELECT 1")
        db_healthy = True
    except Exception:
        db_healthy = False

    ready = db_healthy
    status_code = 200 if ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if ready else "not ready",
            "checks": {"database": "healthy" if db_healthy else "unhealthy"},
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# =============================================================================
# MAIN API ENDPOINTS
# =============================================================================


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with platform information."""
    return {
        "status": "online",
        "platform": "Scorpius X - Blockchain Security Platform",
        "version": "2.0.0",
        "capabilities": [
            "MEV Strategy Management",
            "Mempool Monitoring",
            "Contract Scanning",
            "Real-time Threat Detection",
            "Performance Analytics",
        ],
        "endpoints": {
            "authentication": "/api/auth",
            "mev_operations": "/api/mev",
            "mempool_monitoring": "/api/mempool",
            "health_check": "/healthz",
            "readiness": "/readyz",
            "metrics": "/metrics",
        },
    }


@app.get("/api/status")
async def get_system_status():
    """Get comprehensive system status."""
    try:

        db = next(get_db())

        user_count = db.query(func.count(User.id)).scalar() or 0
        strategy_count = db.query(func.count(MEVStrategy.id)).scalar() or 0
        opportunity_count = db.query(func.count(MEVOpportunity.id)).scalar() or 0

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "total_users": user_count,
                "active_strategies": strategy_count,
                "opportunities_detected": opportunity_count,
            },
            "services": {
                "database": "healthy",
                "blockchain": "connected",
                "mempool_monitor": "active",
            },
        }
    except Exception as e:
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import redis
import uvicorn
from dashboard_routes import router as dashboard_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger as loguru_logger
from models import MEVOpportunity, MEVStrategy, User, get_db, init_database
from prometheus_fastapi_instrumentator import Instrumentator
from routes.auth_fastapi import router as auth_fastapi_router
from routes.mempool_fastapi import router as mempool_fastapi_router
from routes.mev_fastapi import router as mev_fastapi_router
from scanner_routes import router as scanner_router
from simulation_routes import router as simulation_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import func
from system_health import router as system_router

        loguru_logger.error(f"Error fetching system status: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "error": "Unable to fetch full system status",
            },
        )


if __name__ == "__main__":

    uvicorn.run(
        "main_minimal:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
