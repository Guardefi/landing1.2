"""Testing configuration and fixtures."""

import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest


# Mock implementations for testing
class MockRedisCache:
    """Mock Redis cache for testing."""

    def __init__(self):
        self.data = {}

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value, ttl=None):
        self.data[key] = value
        return True

    async def delete(self, key: str):
        return self.data.pop(key, None) is not None

    async def exists(self, key: str):
        return key in self.data


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_cache() -> AsyncGenerator[MockRedisCache, None]:
    """Provide mock cache for testing."""
    cache = MockRedisCache()
    yield cache


@pytest.fixture
def mock_blockchain_client():
    """Provide mock blockchain client for testing."""
    client = Mock()
    client.get_balance.return_value = 1000.0
    client.estimate_gas_fee.return_value = 0.001
    client.execute_transfer.return_value = "0x123...abc"
    client.get_confirmations.return_value = 12
    return client


@pytest.fixture
def mock_event_publisher():
    """Provide mock event publisher for testing."""
    publisher = Mock()
    publisher.publish = Mock()
    return publisher
