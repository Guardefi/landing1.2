"""
Backend test configuration and fixtures for Scorpius DeFi Security Platform.
"""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app and models here
# from backend.main import app
# from backend.models import Base, get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_file() -> Generator[str, None, None]:
    """Create a temporary SQLite database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        yield tmp.name
    os.unlink(tmp.name)


@pytest.fixture
def test_db_engine(temp_db_file: str):
    """Create a test database engine with SQLite."""
    database_url = f"sqlite:///{temp_db_file}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
async def async_test_db_engine(temp_db_file: str):
    """Create an async test database engine with SQLite."""
    database_url = f"sqlite+aiosqlite:///{temp_db_file}"
    engine = create_async_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def db_session(test_db_engine):
    """Create a database session for synchronous tests."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture
async def async_db_session(async_test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for async tests."""
    async_session = sessionmaker(
        async_test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    # Uncomment when you have your main app
    # return TestClient(app)
    pass


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    # Uncomment when you have your main app
    # async with AsyncClient(app=app, base_url="http://test") as client:
    #     yield client
    pass


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    test_env = {
        "SECRET_KEY": "test-secret-key-32-chars-long-123",
        "JWT_SECRET_KEY": "test-jwt-secret-key-32-chars-long",
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379/15",  # Use test DB
        "ENVIRONMENT": "testing",
        "DEBUG": "false",
        "LOG_LEVEL": "WARNING",
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_env
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_smart_contract():
    """Sample smart contract code for testing."""
    return '''
    pragma solidity ^0.8.0;
    
    contract TestContract {
        mapping(address => uint256) public balances;
        
        function deposit() public payable {
            balances[msg.sender] += msg.value;
        }
        
        function withdraw(uint256 amount) public {
            require(balances[msg.sender] >= amount, "Insufficient balance");
            balances[msg.sender] -= amount;
            payable(msg.sender).transfer(amount);
        }
    }
    '''


@pytest.fixture
def sample_vulnerability_report():
    """Sample vulnerability report for testing."""
    return {
        "contract_address": "0x1234567890123456789012345678901234567890",
        "vulnerabilities": [
            {
                "id": "REENTRANCY_001",
                "title": "Reentrancy Vulnerability",
                "severity": "HIGH",
                "description": "Potential reentrancy attack in withdraw function",
                "line_number": 10,
                "function_name": "withdraw",
                "recommendation": "Use checks-effects-interactions pattern",
            }
        ],
        "risk_score": 7.5,
        "scan_timestamp": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_mev_transaction():
    """Sample MEV transaction for testing."""
    return {
        "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "from": "0x1111111111111111111111111111111111111111",
        "to": "0x2222222222222222222222222222222222222222",
        "value": "1000000000000000000",  # 1 ETH in wei
        "gas": 21000,
        "gasPrice": "20000000000",  # 20 gwei
        "block_number": 18000000,
        "transaction_index": 0,
        "mev_type": "arbitrage",
        "profit": "100000000000000000",  # 0.1 ETH profit
    }


@pytest.fixture
def sample_blockchain_data():
    """Sample blockchain data for testing."""
    return {
        "block": {
            "number": 18000000,
            "hash": "0xblock123456789abcdef123456789abcdef123456789abcdef123456789abcdef",
            "timestamp": 1704067200,  # 2024-01-01 00:00:00 UTC
            "transactions": [
                {
                    "hash": "0xtx1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab",
                    "from": "0x1111111111111111111111111111111111111111",
                    "to": "0x2222222222222222222222222222222222222222",
                    "value": "1000000000000000000",
                }
            ],
        }
    }


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "security: Security-related tests")
    config.addinivalue_line("markers", "mev: MEV protection tests")
    config.addinivalue_line("markers", "scanner: Vulnerability scanner tests")


# Auto-use fixtures for common setup
@pytest.fixture(autouse=True)
def setup_test_environment(mock_env_vars):
    """Automatically set up test environment for all tests."""
    pass
