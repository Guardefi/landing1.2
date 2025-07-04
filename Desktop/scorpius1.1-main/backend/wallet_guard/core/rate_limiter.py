"""
Rate limiting implementation - simplified for development
"""

from fastapi import HTTPException, Request


class MockLimiter:
    """Mock rate limiter for development"""

    def limit(self, rate: str):
        """Rate limit decorator"""

        def decorator(func):
            return func

        return decorator


# Mock limiter for development - will be replaced with Redis-based implementation
limiter = MockLimiter()


async def rate_limit_exceeded_handler(request: Request, exc: Exception):
    """Custom rate limit exceeded handler"""
    return HTTPException(
        status_code=429,
        detail={"error": "Rate limit exceeded"},
        headers={"Retry-After": "60"},
    )
