"""
Test configuration and fixtures for Scorpius backend tests.
"""
import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Test database


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    return mock_redis


@pytest.fixture
def app() -> FastAPI:
    """Create FastAPI app instance for testing."""
    # Create a minimal test app to avoid complex import dependencies
    app = FastAPI(title="Scorpius Test App", version="0.1.0")
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "testing": True}
        
    @app.get("/api/v1/status")
    def api_status():
        return {"api": "running", "version": "0.1.0"}
    
    @app.post("/api/v1/scan")
    def scan_contract(contract_data: dict = None):
        return {
            "scan_id": "test-123",
            "status": "completed",
            "vulnerabilities": [],
            "gas_estimate": 21000
        }
        
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_web3():
    """Mock Web3 provider."""
    mock_web3 = MagicMock()
    mock_web3.is_connected.return_value = True
    mock_web3.eth.get_block.return_value = {
        "number": 12345,
        "hash": "0x" + "a" * 64,
        "timestamp": 1234567890
    }
    return mock_web3


@pytest.fixture
def sample_contract_bytecode():
    """Sample contract bytecode for testing."""
    return (
        "0x608060405234801561001057600080fd5b50600436106100415760003560e01c8063"
        "4f2be91f146100465780636057361d1461006257806386975a1b1461007e575b600080fd5b"
        "61004e61009a565b60405161005991906100f5565b60405180910390f35b61007c6004803603"
        "81019061007791906100bc565b6100a0565b005b610098600480360381019061009391906100bc"
        "565b6100aa565b005b60005481565b8060008190555050565b806000819055505056fea264"
        "69706673582212206b6b7c645f42e3e5b6b7e8a6a1b8e7d5c5b6a8e7d5c5b6a8e7d5c5"
        "b6a8e7d564736f6c63430008070033"
    )


@pytest.fixture
def sample_vulnerability_report():
    """Sample vulnerability report structure."""
    return {
        "contract_address": "0x1234567890abcdef",
        "scan_id": "test-scan-123",
        "vulnerabilities": [
            {
                "type": "reentrancy",
                "severity": "high",
                "description": "Potential reentrancy vulnerability",
                "line": 42,
                "confidence": 0.85
            }
        ],
        "gas_analysis": {
            "estimated_gas": 21000,
            "optimization_level": "standard"
        },
        "timestamp": "2025-06-24T00:00:00Z"
    }


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {
        "Authorization": "Bearer test-token-123",
        "Content-Type": "application/json"
    }


# Test markers
pytestmark = pytest.mark.asyncio
