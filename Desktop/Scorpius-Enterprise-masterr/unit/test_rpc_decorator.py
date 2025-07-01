import asyncio

import pytest

from backend.decorators.rpc import resilient_rpc
from backend.utils.retry import CircuitBreakerError


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
async def test_resilient_rpc_success():
    """Test successful RPC call."""
    mock_call = MockRPCCall(failures=0)

    @resilient_rpc()
    async def test_call():
        return await mock_call()

    result = await test_call()
    assert result == "success"


@pytest.mark.asyncio
async def test_resilient_rpc_retry():
    """Test RPC call with retries."""
    mock_call = MockRPCCall(failures=2)

    @resilient_rpc(max_attempts=3)
    async def test_call():
        return await mock_call()

    result = await test_call()
    assert result == "success"


@pytest.mark.asyncio
async def test_resilient_rpc_circuit_breaker():
    """Test RPC call with circuit breaker."""

    breaker_call_count = 0

    @resilient_rpc(failure_threshold=1)
    async def test_call():
        nonlocal breaker_call_count
        breaker_call_count += 1
        if breaker_call_count == 1:
            raise Exception("RPC call failed")
        return "success"

    # First call fails and opens circuit
    with pytest.raises(Exception):
        await test_call()

    # Second call fails due to open circuit
    with pytest.raises(CircuitBreakerError):
        await test_call()
