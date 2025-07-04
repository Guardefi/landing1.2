import logging
from contextlib import asynccontextmanager

# from api.middleware.api_key_auth import APIKeyAuth
# from api.middleware.distributed_rate_limit import RedisRateLimitMiddleware
from api.routes import admin, analysis, health
from api.routes.dashboard import router as dashboard_router
from blockchain.web3_client import Web3Client
from core.engines.ml_engine import MLEngine
from core.engines.static_engine import StaticEngine
from core.engines.symbolic_engine import SymbolicEngine
from database.mongodb_client import MongoDBClient
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.main")


# Define lifespan context manager to handle startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize components on startup
    logger.info("Initializing application components")

    # Initialize database connection
    mongo_client = MongoDBClient()
    await mongo_client.initialize()
    app.state.mongo_client = mongo_client

    # Initialize blockchain client
    web3_client = Web3Client()
    await web3_client.initialize()
    app.state.web3_client = web3_client

    # Initialize ML engine
    ml_engine = MLEngine()
    await ml_engine.load_models()
    app.state.ml_engine = ml_engine

    # Initialize static analysis engine
    static_engine = StaticEngine()
    app.state.static_engine = static_engine

    # Initialize symbolic execution engine
    symbolic_engine = SymbolicEngine()
    await symbolic_engine.initialize()
    app.state.symbolic_engine = symbolic_engine

    logger.info("Application startup complete")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down application components")

    # Close database connection
    if hasattr(app.state, "mongo_client"):
        await app.state.mongo_client.close()

    # Close blockchain client
    if hasattr(app.state, "web3_client"):
        await app.state.web3_client.close()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Enterprise-grade smart contract honeypot detector with multi-engine analysis",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware - commented out for basic setup
# app.add_middleware(APIKeyAuth)
# app.add_middleware(RedisRateLimitMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint that redirects to health check"""
    return {
        "name": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "message": "Enterprise Honeypot Detection API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "analysis": "/api/v1/analysis",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
