import time
from functools import wraps
from typing import Callable, Any
from redis import Redis
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse

class RateLimiter:
    def __init__(self, redis: Redis, limit: int = 100, window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            redis: Redis client instance
            limit: Number of requests allowed in window
            window: Time window in seconds
        """
        self.redis = redis
        self.limit = limit
        self.window = window

    def get_key(self, request: Request) -> str:
        """Generate unique key for rate limiting"""
        return f"rate_limit:{request.client.host}:{request.url.path}"

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Middleware implementation"""
        key = self.get_key(request)
        
        # Get current count and timestamp
        count = self.redis.get(key)
        timestamp = self.redis.get(f"{key}:timestamp")
        
        # Check if we need to reset the window
        if timestamp:
            current_time = time.time()
            if current_time - float(timestamp) > self.window:
                self.redis.delete(key)
                self.redis.delete(f"{key}:timestamp")
                count = None
        
        # If count exists and exceeds limit
        if count and int(count) >= self.limit:
            reset_time = float(timestamp) + self.window - time.time()
            headers = {
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time)
            }
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "reset_in": reset_time
                },
                headers=headers
            )
        
        # Update count and timestamp
        if not count:
            count = 1
            self.redis.set(f"{key}:timestamp", str(time.time()))
        else:
            count = int(count) + 1
        
        self.redis.set(key, str(count), ex=self.window)
        
        # Set rate limit headers
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.limit - count),
            "X-RateLimit-Reset": str(self.window)
        }
        
        response = await call_next(request)
        response.headers.update(headers)
        return response

def rate_limit(limit: int = 100, window: int = 60):
    """
    Decorator to apply rate limiting to endpoints
    
    Args:
        limit: Number of requests allowed in window
        window: Time window in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Response:
            # Create rate limiter instance
            redis = Redis.from_url(request.app.state.redis_url)
            limiter = RateLimiter(redis, limit, window)
            
            # Check rate limit
            key = f"endpoint:{request.url.path}"
            count = redis.get(key)
            
            if count and int(count) >= limit:
                reset_time = float(redis.get(f"{key}:timestamp")) + window - time.time()
                headers = {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded",
                        "reset_in": reset_time
                    },
                    headers=headers
                )
            
            # Update count
            if not count:
                count = 1
                redis.set(f"{key}:timestamp", str(time.time()))
            else:
                count = int(count) + 1
            
            redis.set(key, str(count), ex=window)
            
            # Set rate limit headers
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(limit - count),
                "X-RateLimit-Reset": str(window)
            }
            
            # Call the actual endpoint
            response = await func(request, *args, **kwargs)
            response.headers.update(headers)
            return response
        
        return wrapper
    
    return decorator
