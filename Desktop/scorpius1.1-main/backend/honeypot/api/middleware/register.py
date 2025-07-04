"""
Middleware registration module for FastAPI application
"""
import logging

from api.metrics import metrics_middleware
from api.middleware.api_key_auth import ApiKeyAuthMiddleware
from api.middleware.cors import setup_cors
from api.middleware.distributed_rate_limit import DistributedRateLimitMiddleware
from api.services.user_service import UserService
from database.cache_service import cache_service
from database.mongodb_client import MongoDBClient
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

logger = logging.getLogger("api.middleware")


async def register_all_middleware(app: FastAPI):
    """
    Register all middleware with the FastAPI application

    Order of middleware registration is important:
    1. CORS - Always first to handle preflight requests
    2. Metrics - To capture all requests including unauthorized ones
    3. Rate Limiting - Before auth to prevent DoS even from invalid keys
    4. API Key Auth - After rate limiting
    """
    logger.info("Registering API middleware components...")

    # 1. Setup CORS middleware
    setup_cors(app)

    # 2. Add metrics middleware - track all requests
    @app.middleware("http")
    async def metrics_middleware_wrapper(request: Request, call_next):
        return await metrics_middleware(request, call_next)

    # 3. Add distributed rate limiting middleware
    # Initialize cache service if not already initialized
    if not cache_service.is_initialized():
        await cache_service.initialize()

    # Path whitelist - these endpoints don't require rate limiting
    rate_limit_whitelist = [
        "/health",
        "/health/liveness",
        "/metrics",
        "/metrics-summary",
        "/docs",
        "/openapi.json",
    ]

    app.add_middleware(
        DistributedRateLimitMiddleware,
        redis_client=cache_service.redis,
        rate_limit_per_minute=settings.DEFAULT_RATE_LIMIT,
        whitelist_paths=rate_limit_whitelist,
        block_duration_seconds=settings.BLOCK_DURATION_SECONDS,
        include_headers=True,
    )

    # 4. Add API key authentication middleware
    mongodb_client = MongoDBClient()
    if not mongodb_client.is_connected():
        await mongodb_client.connect()

    user_service = UserService(mongodb_client)

    # Path whitelist - these endpoints don't require authentication
    auth_whitelist = [
        "/health",
        "/health/liveness",
        "/metrics",
        "/metrics-summary",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]

    app.add_middleware(
        ApiKeyAuthMiddleware,
        user_service=user_service,
        whitelist_paths=auth_whitelist,
        dev_mode=settings.DEV_MODE,
        dev_api_key=settings.API_KEY,
    )

    logger.info("All middleware components registered successfully")


async def shutdown_middleware():
    """Shutdown and cleanup middleware resources"""
    logger.info("Shutting down middleware components...")

    # Close Redis connections used by middleware
    if cache_service.is_initialized():
        await cache_service.close()

    logger.info("Middleware components shutdown complete")
