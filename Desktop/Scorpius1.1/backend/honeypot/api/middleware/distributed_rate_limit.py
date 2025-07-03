"""
Distributed rate limiting middleware using Redis
"""
import logging
import time
from typing import Callable, Dict, Optional, Tuple

from database.cache_service import cache_service
from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.middleware.rate_limit")


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based distributed rate limiting middleware for FastAPI

    This middleware provides rate limiting across multiple API instances
    by using Redis as a shared counter store.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_limit: int = 100,
        window_seconds: int = 60,
        block_duration: int = 300,
        whitelist_paths: Optional[list] = None,
        error_message: str = "Rate limit exceeded. Please try again later.",
    ):
        """
        Initialize rate limiting middleware

        Args:
            app: ASGI application
            requests_limit: Maximum requests per window
            window_seconds: Time window in seconds
            block_duration: Duration to block after exceeding limit (seconds)
            whitelist_paths: List of paths to exclude from rate limiting
            error_message: Error message to return when rate limit exceeded
        """
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.block_duration = block_duration
        self.whitelist_paths = whitelist_paths or ["/health", "/metrics"]
        self.error_message = error_message

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request through the rate limiter

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response object
        """
        # Skip rate limiting for whitelisted paths
        if any(request.url.path.startswith(path) for path in self.whitelist_paths):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check if client is blocked
        is_blocked = await cache_service.is_rate_limited(client_id)
        if is_blocked:
            logger.warning(f"Blocked request from rate-limited client {client_id}")
            return self._rate_limit_response()

        # Check rate limit
        count, allowed = await cache_service.track_rate_limit(
            client_id=client_id, limit=self.requests_limit, window=self.window_seconds
        )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_limit - count)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.window_seconds)
        )

        # Block client if limit exceeded
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for client {client_id}: {count} requests"
            )
            await cache_service.block_client(client_id, self.block_duration)
            response.headers["Retry-After"] = str(self.block_duration)

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request

        Args:
            request: FastAPI request object

        Returns:
            Client identifier string
        """
        # Try to get API key from header first (authenticated clients)
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"api:{api_key}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            # Get first IP in forwarded chain
            client_ip = forwarded.split(",")[0].strip()
        else:
            # Get client host from direct connection
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    def _rate_limit_response(self) -> Response:
        """
        Create rate limit exceeded response

        Returns:
            JSON response with 429 status code
        """
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=self.error_message,
            headers={"Retry-After": str(self.block_duration)},
        )
