"""
Centralized utility functions for the Scorpius backend
Consolidates retry logic, async helpers, and common utilities
"""



logger = logging.getLogger(__name__)

T = TypeVar("T")


class ScorpiusUtils:
    """Centralized utility class for common operations"""

    @staticmethod
    async def retry_async(
        func: Callable[..., T],
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
    ) -> T:
        """
        Async retry helper with exponential backoff

        Args:
            func: Async function to retry
            max_attempts: Maximum number of retry attempts
            delay: Initial delay between retries
            backoff_factor: Multiplier for delay after each attempt
            exceptions: Tuple of exceptions that trigger retries
        """
        last_exception = None
        current_delay = delay

        for attempt in range(max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()
            except exceptions as e:
                last_exception = e
                if attempt == max_attempts - 1:
                    break

                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                    f"Retrying in {current_delay}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor

        raise last_exception

    @staticmethod
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def safe_http_request(
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        timeout: int = 30,
        **kwargs,
    ) -> dict:
        """
        Safe HTTP request with automatic retries and error handling
        """
        async with session.request(
            method, url, timeout=aiohttp.ClientTimeout(total=timeout), **kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    def timing_decorator(func: Callable) -> Callable:
        """Decorator to measure function execution time"""

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise e from e

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise e from e

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address format"""
        if not address or not isinstance(address, str):
            return False

        # Remove 0x prefix if present
        addr = address.lower()
        if addr.startswith("0x"):
            addr = addr[2:]

        # Check if it's a valid hex string of correct length
        if len(addr) != 40:
            return False

        try:
            int(addr, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def sanitize_input(data: Any, max_length: int = 1000) -> Any:
        """Sanitize user input to prevent injection attacks"""
        if isinstance(data, str):
            # Remove dangerous characters and limit length
            sanitized = data.replace("<", "").replace(">", "").replace("&", "")
            return sanitized[:max_length]
        elif isinstance(data, dict):
            return {
                k: ScorpiusUtils.sanitize_input(v, max_length) for k, v in data.items()
            }
import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

        elif isinstance(data, list):
            return [ScorpiusUtils.sanitize_input(item, max_length) for item in data]
        else:
            return data


# Convenience functions for backward compatibility
retry_async = ScorpiusUtils.retry_async
safe_http_request = ScorpiusUtils.safe_http_request
timing_decorator = ScorpiusUtils.timing_decorator
validate_ethereum_address = ScorpiusUtils.validate_ethereum_address
sanitize_input = ScorpiusUtils.sanitize_input
