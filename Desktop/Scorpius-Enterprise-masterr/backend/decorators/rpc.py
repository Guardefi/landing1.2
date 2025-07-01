import logging
from typing import Any, Callable

from backend.utils.retry import AsyncCircuitBreaker, AsyncRetry

logger = logging.getLogger(__name__)


def resilient_rpc(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 30.0,
    failure_threshold: int = 3,
    reset_timeout: int = 60,
):
    """
    Decorator that combines retry and circuit breaker for RPC calls.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time between retries
        max_wait: Maximum wait time between retries
        failure_threshold: Number of failures before circuit opens
        reset_timeout: Time before circuit closes after opening
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            # Create retry and circuit breaker instances
            retry = AsyncRetry(max_attempts, initial_wait, max_wait)
            breaker = AsyncCircuitBreaker(failure_threshold, reset_timeout)

            # Define the actual RPC call with circuit breaker
            @retry
            async def rpc_call(*args, **kwargs):
                try:
                    return await breaker(func)(*args, **kwargs)
                except Exception as e:
                    logger.error(f"RPC call failed: {str(e)}")
                    raise

            return await rpc_call(*args, **kwargs)

        return wrapper

    return decorator


# Example usage:
@resilient_rpc(
    max_attempts=3,
    initial_wait=1.0,
    max_wait=30.0,
    failure_threshold=3,
    reset_timeout=60,
)
async def make_rpc_call(endpoint: str, params: dict) -> dict:
    """Make a resilient RPC call."""
    # Implementation of RPC call
