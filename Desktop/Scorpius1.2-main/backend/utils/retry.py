import asyncio
import logging
import time
from typing import Any, Callable, Optional, Type

logger = logging.getLogger(__name__)


class CircuitBreakerError(Exception):
    """Raised when a circuit breaker is open."""
    pass


class AsyncCircuitBreaker:
    """Simple async circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 3, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.current_state = "closed"  # closed, open, half-open

    async def __call__(self, func: Callable, *args, **kwargs) -> Any:
        if self.current_state == "open":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.reset_timeout:
                self.current_state = "half-open"
            else:
                logger.warning(f"Circuit breaker is open for {func.__name__}")
                raise CircuitBreakerError(f"Circuit breaker is open for {func.__name__}")

        try:
            result = await func(*args, **kwargs)
            if self.current_state == "half-open":
                self.current_state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.current_state = "open"
            
            logger.error(f"Circuit breaker failure in {func.__name__}: {str(e)}")
            raise


class AsyncRetry:
    """Simple async retry implementation"""
    
    def __init__(self, max_attempts: int = 3, initial_wait: float = 1.0, max_wait: float = 30.0):
        self.max_attempts = max_attempts
        self.initial_wait = initial_wait
        self.max_wait = max_wait

    def __call__(self, func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            last_exception = None
            wait_time = self.initial_wait
            
            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < self.max_attempts - 1:  # Don't wait after last attempt
                        await asyncio.sleep(wait_time)
                        wait_time = min(wait_time * 2, self.max_wait)  # Exponential backoff
            
            # If we get here, all attempts failed
            logger.error(f"All {self.max_attempts} attempts failed")
            raise last_exception
        
        return wrapper


def create_async_retry(
    max_attempts: int = 3, initial_wait: float = 1.0, max_wait: float = 30.0
) -> AsyncRetry:
    """Create an async retry decorator with specified parameters."""
    return AsyncRetry(max_attempts, initial_wait, max_wait)


def create_circuit_breaker(
    failure_threshold: int = 3, reset_timeout: int = 60
) -> AsyncCircuitBreaker:
    """Create an async circuit breaker."""
    return AsyncCircuitBreaker(failure_threshold, reset_timeout)
