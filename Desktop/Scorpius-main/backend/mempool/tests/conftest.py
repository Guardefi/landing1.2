#!/usr/bin/env python3
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.main import app
from fastapi.testclient import TestClient
from core.session_manager import SessionManager
from core.enhanced_mempool_monitor import EnhancedMempoolMonitor
import pytest_asyncio
import pytest
from unittest.mock import AsyncMock
from typing import AsyncGenerator, Generator
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Test configuration and fixtures for the Elite Mempool System."""


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for FastAPI app."""
    return TestClient(app)


@pytest_asyncio.fixture
async def session_manager() -> AsyncGenerator[SessionManager, None]:
    """Create a SessionManager instance for testing."""
    manager = SessionManager()
    yield manager
    await manager.close_all_sessions()


@pytest_asyncio.fixture
async def mock_web3():
    """Create a mock Web3 instance."""
    mock = AsyncMock()
    mock.eth.get_pending_transactions = AsyncMock(return_value=[])
    mock.eth.get_transaction = AsyncMock(
        return_value={
            "hash": "0x123",
            "from": "0xabc",
            "to": "0xdef",
    "value": 1000000000000000000,
    "gasPrice": 20000000000,
    "gas": 21000,
    "nonce": 1,
            "input": "0x",
        }
    )
    return mock


@pytest_asyncio.fixture
async def mempool_monitor(
    session_manager: SessionManager,
) -> AsyncGenerator[EnhancedMempoolMonitor, None]:
    """Create a mempool monitor for testing."""
    monitor = EnhancedMempoolMonitor(
        chain_id=1,
        rpc_urls=["http://localhost:8545"],
        session_manager=session_manager,
        max_stored_txs=100,
        poll_interval=1.0,
    )
    yield monitor
    await monitor.stop()


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing."""
    return {
        "hash": "0x1234567890abcdef",
        "from": "0xfrom_address",
        "to": "0xto_address",
        "value": "1000000000000000000",  # 1 ETH
        "gasPrice": "20000000000",  # 20 Gwei
        "gas": "21000",
        "nonce": "1",
        "input": "0x",
    "blockNumber": None,
    "transactionIndex": None,
    }


@pytest.fixture
def sample_alert():
    """Sample alert data for testing."""
    return {
        "id": "alert-123",
        "rule_id": "rule-456",
        "transaction_hash": "0x1234567890abcdef",
    "chain_id": 1,
        "severity": "high",
        "title": "High Value Transaction",
        "description": "Transaction with value > 10 ETH detected",
        "metadata": {"value_eth": 15.5},
        "tags": ["high-value", "monitoring"],
    }


@pytest.fixture
def sample_mev_opportunity():
    """Sample MEV opportunity data for testing."""
    return {
        "id": "mev-123",
        "transaction_hash": "0x1234567890abcdef",
    "chain_id": 1,
        "pattern_type": "arbitrage",
    "estimated_profit": 0.5,
    "confidence_score": 0.85,
    "target_block": 18500000,
        "gas_price_required": "25000000000",
        "details": {
            "dex_a": "Uniswap",
            "dex_b": "SushiSwap",
            "token_pair": "WETH/USDC",
        ],
    }


# Mock database session
@pytest_asyncio.fixture
async def db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


# Configuration overrides for testing
@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for testing."""
    import os

    os.environ.update(
        {
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "DEBUG",
            "POSTGRES_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/1",
            "JWT_SECRET": "test-secret-key",
        }
    )


if __name__ == '__main__':
    print('Running test file...')

    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    passed = 0
    failed = 0

    for test_name in test_functions:
        try:
            test_func = globals()[test_name]
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            print(f'✓ {test_name} passed')
            passed += 1
        except Exception as e:
            print(f'✗ {test_name} failed: {e}')
            failed += 1

    print(f'\nTest results: {passed} passed, {failed} failed')
