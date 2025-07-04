"""
API key authentication middleware
"""
import logging
from typing import Callable, Optional

from api.metrics import API_KEY_USAGE
from api.services.user_service import UserService
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.middleware.api_key_auth")


class APIKeyAuth(BaseHTTPMiddleware):
    """
    Middleware for API key authentication

    This middleware checks for a valid API key in the X-API-Key header
    for protected routes.
    """

    def __init__(
        self,
        app: ASGIApp,
        user_service: UserService,
        bypass_routes: Optional[list] = None,
        api_key_header: str = "X-API-Key",
    ):
        """
        Initialize API key authentication middleware

        Args:
            app: ASGI application
            user_service: User service for API key validation
            bypass_routes: Routes that don't require authentication
            api_key_header: Header name for API key
        """
        super().__init__(app)
        self.user_service = user_service
        self.bypass_routes = bypass_routes or ["/health", "/metrics"]
        self.api_key_header = api_key_header

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request through the authentication check

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response object
        """
        # Skip authentication for bypass routes
        if any(request.url.path.startswith(route) for route in self.bypass_routes):
            return await call_next(request)

        # Check if API key is provided
        api_key = request.headers.get(self.api_key_header)
        if not api_key:
            logger.warning(f"API key missing for request to {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key missing. Please provide a valid API key in the X-API-Key header.",
            )

        # For development/testing, allow static key from settings
        if settings.DEV_MODE and api_key == settings.API_KEY:
            request.state.user = {"id": "dev", "username": "dev", "is_admin": True}
            return await call_next(request)

        # Validate API key with user service
        user = await self.user_service.get_user_by_api_key(api_key)

        if not user:
            logger.warning(f"Invalid API key used: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key. Please provide a valid API key in the X-API-Key header.",
            )

        if user.get("is_disabled", False):
            logger.warning(f"Disabled account attempted access: {user['username']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been disabled. Please contact support.",
            )

        # Track API key usage in metrics
        API_KEY_USAGE.labels(api_key_id=str(user["_id"])).inc()

        # Add user to request state for later use
        request.state.user = user

        # Process request
        response = await call_next(request)
        return response
