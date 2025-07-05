"""Main FastAPI application for Scorpius Bridge.

Enterprise-grade setup with proper dependency injection, middleware,
and error handling.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from scorpius_bridge.api.http.dependencies import setup_dependencies
from scorpius_bridge.api.http.routers import v1, v2
from scorpius_bridge.api.websocket.events import event_broadcaster
from scorpius_bridge.api.websocket.router import router as websocket_router
from scorpius_bridge.config import settings
from scorpius_bridge.domain.errors import DomainError


def setup_logging():
    """Setup structured logging from config file."""
    config_path = Path(__file__).parent / "config" / "logging.yaml"

    if config_path.exists():
        with open(config_path, "r") as f:
            log_config = yaml.safe_load(f)

        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        logging.config.dictConfig(log_config)
    else:
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    setup_logging()
    logger = logging.getLogger("scorpius_bridge.startup")
    logger.info("Starting Scorpius Bridge Network...")

    # Initialize dependencies (databases, caches, etc.)
    await setup_dependencies(app)

    # Start event broadcaster for WebSocket events
    await event_broadcaster.start()

    logger.info("Scorpius Bridge Network started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Scorpius Bridge Network...")

    # Stop event broadcaster
    await event_broadcaster.stop()

    # Clean up resources here
    logger.info("Scorpius Bridge Network shut down complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Scorpius Bridge Network",
        description="Advanced cross-chain interoperability system with atomic swaps, bridge validation, and secure multi-chain asset transfers.",
        version="2.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Security middleware
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.scorpius-bridge.com", "api.scorpius-bridge.com"],
        )

    # CORS middleware
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"]
            if settings.debug
            else ["https://app.scorpius-bridge.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    # Include routers
    app.include_router(v1.router, prefix="/api/v1")
    app.include_router(v2.router, prefix="/api/v2")
    app.include_router(websocket_router, prefix="/api")

    # Global exception handlers
    @app.exception_handler(DomainError)
    async def domain_exception_handler(request: Request, exc: DomainError):
        """Handle domain errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Domain Error",
                "message": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger = logging.getLogger("scorpius_bridge.error")
        logger.exception(f"Unexpected error: {exc}")

        if settings.debug:
            # Include traceback in debug mode
            import traceback

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": str(exc),
                    "traceback": traceback.format_exc() if settings.debug else None,
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                },
            )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "2.0.0",
            "environment": settings.environment,
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scorpius_bridge.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        access_log=True,
        log_config=None,  # Use our custom logging config
    )
