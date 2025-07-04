import asyncio
import logging
import time
from typing import Callable, Dict, List, Optional

from fastapi import HTTPException, Request, status

# Configure logger
logger = logging.getLogger("api.rate_limit")


class RateLimiter:
    def __init__(
        self,
        requests_limit: int = 100,
        window_seconds: int = 60,
        block_duration_seconds: int = 300,
    ):
        """
        Simple rate limiter using in-memory storage

        Args:
            requests_limit: Maximum requests allowed in time window
            window_seconds: Time window in seconds
            block_duration_seconds: Duration to block if limit exceeded
        """
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.block_duration_seconds = block_duration_seconds
        self.request_records: Dict[str, List[float]] = {}
        self.blocked_clients: Dict[str, float] = {}

    async def initialize(self):
        """Start cleanup task"""
        asyncio.create_task(self._cleanup_expired_records())

    async def _cleanup_expired_records(self):
        """Periodically clean up expired records"""
        while True:
            try:
                current_time = time.time()

                # Clean request records
                for client_id, timestamps in list(self.request_records.items()):
                    # Filter out timestamps older than window
                    valid_timestamps = [
                        ts
                        for ts in timestamps
                        if current_time - ts <= self.window_seconds
                    ]
                    if valid_timestamps:
                        self.request_records[client_id] = valid_timestamps
                    else:
                        del self.request_records[client_id]

                # Clean blocked clients
                for client_id, block_time in list(self.blocked_clients.items()):
                    if current_time - block_time > self.block_duration_seconds:
                        del self.blocked_clients[client_id]

            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")

            # Run every minute
            await asyncio.sleep(60)

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        client_host = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key", "")

        # Prefer API key if available, otherwise use IP
        return api_key if api_key else client_host

    async def check_rate_limit(self, request: Request):
        """
        Check if request exceeds rate limit

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If rate limit exceeded
        """
        client_id = self._get_client_id(request)
        current_time = time.time()

        # Check if client is blocked
        if client_id in self.blocked_clients:
            block_time = self.blocked_clients[client_id]
            block_remaining = int(
                self.block_duration_seconds - (current_time - block_time)
            )

            if block_remaining > 0:
                logger.warning(f"Blocked request from {client_id}: {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {block_remaining} seconds.",
                )
            else:
                # Unblock if duration elapsed
                del self.blocked_clients[client_id]

        # Initialize client record if not exists
        if client_id not in self.request_records:
            self.request_records[client_id] = []

        # Get timestamps in current window
        window_start = current_time - self.window_seconds
        recent_requests = [
            ts for ts in self.request_records[client_id] if ts >= window_start
        ]

        # Check if limit exceeded
        if len(recent_requests) >= self.requests_limit:
            # Block client
            self.blocked_clients[client_id] = current_time
            logger.warning(
                f"Rate limit exceeded for {client_id}, blocked for {self.block_duration_seconds}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_limit} requests per {self.window_seconds} seconds. Try again later.",
            )

        # Record this request
        self.request_records[client_id].append(current_time)


# Create global limiter instance
rate_limiter = RateLimiter(
    requests_limit=100, window_seconds=60, block_duration_seconds=300
)


async def rate_limit_middleware(request: Request, call_next: Callable):
    """
    FastAPI middleware for rate limiting

    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler

    Returns:
        Response from next handler
    """
    try:
        # Skip rate limiting for health checks
        if not request.url.path.startswith("/health"):
            await rate_limiter.check_rate_limit(request)
    except HTTPException as exc:
        # Re-raise HTTP exceptions from rate limiter
        raise exc
    except Exception as e:
        logger.error(f"Rate limit error: {e}")

    # Continue with request processing
    return await call_next(request)
