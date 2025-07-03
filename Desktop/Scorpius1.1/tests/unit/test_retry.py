import asyncio

import pytest

from backend.utils.retry import AsyncCircuitBreaker, AsyncRetry, CircuitBreakerError


class MockRPCCall:
    """Mock RPC call that fails a specified number of times."""
    def __init__(self, failures: int = 0):
        self.failures = failures

    async def __call__(self) -> str:
        if self.failures > 0:
            self.failures -= 1
            raise Exception("RPC call failed")
        return "success"


@pytest.mark.asyncio
async def test_async_retry_success():
    """Test successful retry."""
    retry = AsyncRetry(max_attempts=3)
    mock_call = MockRPCCall(failures=0)
    result = await retry(mock_call)()
    assert result == "success"


@pytest.mark.asyncio
async def test_async_retry_failure():
    """Test retry with failure threshold."""
    retry = AsyncRetry(max_attempts=2)
    mock_call = MockRPCCall(failures=3)
    with pytest.raises(Exception):
        await retry(mock_call)()


@pytest.mark.asyncio
async def test_circuit_breaker_success():
    """Test circuit breaker success."""
    breaker = AsyncCircuitBreaker(failure_threshold=3)
    mock_call = MockRPCCall(failures=0)
    result = await breaker(mock_call)()
    assert result == "success"


@pytest.mark.asyncio
async def test_circuit_breaker_failure():
    """Test circuit breaker failure."""
    breaker = AsyncCircuitBreaker(failure_threshold=1)

    # First call fails and opens circuit
    mock_call = MockRPCCall(failures=1)
    with pytest.raises(Exception):
        await breaker(mock_call)()

    # Second call fails due to open circuit
    mock_call2 = MockRPCCall(failures=0)
    with pytest.raises(CircuitBreakerError):
        await breaker(mock_call2)()


@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    """Test circuit breaker recovery."""
    breaker = AsyncCircuitBreaker(failure_threshold=1, reset_timeout=1)

    # First call fails and opens circuit
    mock_call = MockRPCCall(failures=1)
    with pytest.raises(Exception):
        await breaker(mock_call)()

    # Wait for circuit to reset
    await asyncio.sleep(1.1)

    # Circuit should be closed now
    mock_call2 = MockRPCCall(failures=0)
    result = await breaker(mock_call2)()
    assert result == "success"
