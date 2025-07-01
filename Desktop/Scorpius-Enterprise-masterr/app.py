"""
Scorpius Enterprise Reporting System
====================================

Main application entry point for the enterprise reporting system.
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

# Handle both relative and absolute imports
try:
    from .config import get_settings
    from .api import router as api_router
    from .persistence.db import init_database, close_database
    from .webhook.notifier import webhook_manager
except ImportError:
    # Fall back to absolute imports when run directly
    from config import get_settings
    from api import router as api_router
    from persistence.db import init_database, close_database
    from webhook.notifier import webhook_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scorpius_reporting.log")
    ]
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Scorpius Enterprise Reporting System",
        description="Enterprise-grade reporting engine for smart contract vulnerability scanning",
        version="1.0.0",
        docs_url="/docs" if settings.api.debug else None,
        redoc_url="/redoc" if settings.api.debug else None,
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # API routes
    app.include_router(api_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "scorpius-reporting"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Scorpius Enterprise Reporting System",
            "version": "1.0.0",
            "docs": "/docs" if settings.api.debug else None
        }
    
    return app


async def startup_event():
    """Application startup tasks"""
    logger.info("Starting Scorpius Enterprise Reporting System...")
    
    settings = get_settings()
    
    # Initialize database
    try:
        await init_database(settings)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Configure webhooks
    if settings.webhook.enabled and settings.webhook.urls:
        webhook_manager.configure(
            webhook_urls=settings.webhook.urls,
            enabled=True,
            timeout=settings.webhook.timeout,
            max_retries=settings.webhook.max_retries
        )
        logger.info(f"Webhooks configured with {len(settings.webhook.urls)} endpoints")
    
    logger.info("Scorpius Enterprise Reporting System started successfully")


async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down Scorpius Enterprise Reporting System...")
    
    # Close database connections
    try:
        await close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    logger.info("Scorpius Enterprise Reporting System shutdown complete")


# Create application instance
app = create_app()

# Event handlers
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "reporting.app:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
