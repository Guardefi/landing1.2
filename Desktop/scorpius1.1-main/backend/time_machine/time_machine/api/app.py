"""
Time Machine FastAPI Application
Main FastAPI app that includes all routes and middleware.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("Starting Time Machine API...")
    
    # Initialize the global engine from routes
    from .routes import engine
    try:
        await engine.initialize()
        logger.info("Time Machine engine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        # Continue anyway, engine will work in limited mode
    
    yield
    
    # Shutdown
    logger.info("Shutting down Time Machine API...")
    try:
        await engine.cleanup()
        logger.info("Time Machine engine cleaned up")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="Time Machine API",
    description="Blockchain Forensic Analysis Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Time Machine API",
        "version": "1.0.0",
        "description": "Blockchain Forensic Analysis Platform",
        "docs": "/docs",
        "health": "/health"
    }


# Health endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "service": "time_machine"} 