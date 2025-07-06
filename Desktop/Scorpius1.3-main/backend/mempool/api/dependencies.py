"""
API Dependencies

Common dependencies used across API routers including:
- Authentication and authorization
- Database connections
- Request validation
"""

import os
from typing import Any, Optional

import asyncpg
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Security
security = HTTPBearer()


class DatabaseManager:
    """Database connection manager"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[redis.Redis] = None

    async def initialize(self):
        """Initialize database connections"""
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5433/elite_mempool",
        )
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6380")

        self.pool = await asyncpg.create_pool(database_url, min_size=5, max_size=20)
        self.redis = redis.from_url(redis_url)

    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.redis:
            await self.redis.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_database():
    """
    Dependency to get database connection pool.

    Returns the database connection pool for executing queries.
    """
    if not db_manager.pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_manager.pool


async def get_redis():
    """
    Dependency to get Redis connection.

    Returns the Redis connection for caching and session management.
    """
    if not db_manager.redis:
        raise HTTPException(status_code=500, detail="Redis not initialized")
    return db_manager.redis


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database),
) -> dict[str, Any]:
    """
    Get current authenticated user from JWT token.

    In a production environment, this would:
    1. Validate the JWT token
    2. Extract user information
    3. Check token expiration
    4. Verify user exists and is active

    For now, this is a placeholder that returns demo user data.
    """
    try:
        # Placeholder JWT validation
        # In production, you would:
        # 1. Decode and validate the JWT token
        # 2. Check token expiration
        # 3. Verify signature
        # 4. Extract user claims
        # 5. Check user status in database

        token = credentials.credentials

        # Demo user data (replace with real JWT validation)
        if token == "demo-token":
            return {
                "user_id": "demo_user",
                "username": "demo@example.com",
                "role": "admin",
                "permissions": ["read", "write", "admin"],
                "is_active": True,
            }

        # Simulate database lookup for user validation
        async with db.acquire() as conn:
            # In production, validate token and get user info
            # For now, return demo data
            pass

        # Default demo user for development
        return {
            "user_id": "user_123",
            "username": "user@example.com",
            "role": "user",
            "permissions": ["read"],
            "is_active": True,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Dependency that requires admin role.

    Validates that the current user has admin privileges.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


class RateLimitChecker:
    """Rate limiting dependency"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def __call__(
        self, current_user: dict = Depends(get_current_user), redis=Depends(get_redis)
    ):
        """
        Check rate limits for the current user.

        Implements sliding window rate limiting using Redis.
        """
        try:
            user_id = current_user["user_id"]
            current_time = int(time.time())
            window_start = current_time - 60  # 1 minute window

            # Redis key for rate limiting
            rate_limit_key = f"rate_limit:{user_id}"

            # Count requests in the current window
            request_count = await redis.zcount(
                rate_limit_key, window_start, current_time
            )

            if request_count >= self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )

            # Add current request to the sliding window
            await redis.zadd(rate_limit_key, {str(current_time): current_time})

            # Set expiration for cleanup
            await redis.expire(rate_limit_key, 120)  # 2 minutes

        except HTTPException:
            raise
        except Exception:
            # If rate limiting fails, allow the request but log the error
            # In production, you might want to be more strict
            pass


# Rate limiting dependencies with different limits
standard_rate_limit = RateLimitChecker(requests_per_minute=60)
strict_rate_limit = RateLimitChecker(requests_per_minute=30)
admin_rate_limit = RateLimitChecker(requests_per_minute=120)


async def validate_chain_id(chain_id: Optional[int] = None) -> Optional[int]:
    """
    Validate chain ID parameter.

    Ensures the chain ID is supported by the system.
    """
    if chain_id is None:
        return None

    # List of supported chain IDs
    supported_chains = [
        1,
        56,
        137,
        42161,
        10,
        43114,
    ]  # ETH, BSC, Polygon, Arbitrum, Optimism, Avalanche

    if chain_id not in supported_chains:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported chain ID: {chain_id}. Supported chains: {supported_chains}",
        )

    return chain_id


class PaginationValidator:
    """Pagination parameters validator"""

    def __init__(self, max_limit: int = 1000):
        self.max_limit = max_limit

    def __call__(self, limit: int = 100, offset: int = 0):
        """Validate pagination parameters"""
        if limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be greater than 0")

        if limit > self.max_limit:
            raise HTTPException(
                status_code=400, detail=f"Limit cannot exceed {self.max_limit}"
            )

        if offset < 0:
            raise HTTPException(
                status_code=400, detail="Offset must be greater than or equal to 0"
            )

        return {"limit": limit, "offset": offset}


# Default pagination validator
validate_pagination = PaginationValidator()


async def get_user_preferences(
    current_user: dict = Depends(get_current_user), redis=Depends(get_redis)
) -> dict[str, Any]:
    """
    Get user preferences and settings.

    Retrieves user-specific configuration from Redis cache or database.
    """
    try:
        user_id = current_user["user_id"]
        prefs_key = f"user_prefs:{user_id}"

        # Try to get from Redis cache first
        cached_prefs = await redis.get(prefs_key)
        if cached_prefs:
            import json

            return json.loads(cached_prefs)

        # Default preferences
        default_prefs = {
            "timezone": "UTC",
            "date_format": "ISO",
            "theme": "light",
            "notifications_enabled": True,
            "default_chain_filter": None,
            "dashboard_refresh_interval": 30,
            "alert_sound_enabled": True,
        }

        # Cache for future requests
        await redis.setex(prefs_key, 3600, json.dumps(default_prefs))  # 1 hour cache

        return default_prefs

    except Exception:
        # Return defaults if there's any error
        return {
            "timezone": "UTC",
            "date_format": "ISO",
            "theme": "light",
            "notifications_enabled": True,
        }


import json

# Import time for rate limiting
import time


async def verify_websocket_token(token: str) -> bool:
    """Verify WebSocket authentication token."""
    try:
        # Simplified token verification for now
        # In production, this should validate JWT tokens properly
        if not token or len(token) < 10:
            return False

        # For demo purposes, accept any token that looks valid
        # TODO: Implement proper JWT verification
        return True

    except Exception:
        return False


def get_websocket_user(token: str = None) -> dict:
    """Get user information from WebSocket token."""
    try:
        if not token:
            return {"user_id": "anonymous", "is_authenticated": False}

        # For demo purposes, return mock user
        # TODO: Implement proper user extraction from JWT
        return {
            "user_id": "demo_user",
            "is_authenticated": True,
            "permissions": ["read", "write"],
        }

    except Exception:
        return {"user_id": "anonymous", "is_authenticated": False}
