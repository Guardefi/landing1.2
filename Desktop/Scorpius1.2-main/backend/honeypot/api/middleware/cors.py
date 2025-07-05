"""
CORS middleware configuration for the API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Get allowed origins from settings
    origins = settings.ALLOWED_ORIGINS

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400,  # 24 hours
    )
