import logging
from typing import Any, Callable

from pybreaker import CircuitBreaker
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class AsyncCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.breaker = CircuitBreaker(
            fail_max=failure_threshold, reset_timeout=reset_timeout
        )

    async def __call__(self, func: Callable, *args, **kwargs) -> Any:
        if self.breaker.current_state == "open":
            logger.warning(f"Circuit breaker is open for {func.__name__}")
            raise CircuitBreakerError(
                f"Circuit breaker is open for {
                    func.__name__}"
            )

        try:
            return await func(*args, **kwargs)
        except Exception:
            self.breaker.fail()
            raise
        finally:
            if self.breaker.current_state == "half-open":
                self.breaker.success()


class AsyncRetry:
    def __init__(
        self, max_attempts: int = 3, initial_wait: float = 1.0, max_wait: float = 30.0
    ):
        self.max_attempts = max_attempts
        self.initial_wait = initial_wait
        self.max_wait = max_wait

    def __call__(self, func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=self.initial_wait, max=self.max_wait),
            retry=retry_if_exception_type(),
        )
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Retry attempt failed: {str(e)}")
                raise

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


class CircuitBreakerError(Exception):
    """Raised when a circuit breaker is open."""
