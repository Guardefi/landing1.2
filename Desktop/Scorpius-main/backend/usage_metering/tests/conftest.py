#!/usr/bin/env python3
from ..services.usage_tracker import UsageTracker
from ..services.stripe_service import StripeService
from ..services.metrics_exporter import MetricsExporter
from ..core.config import Settings
from ..app import app
from fastapi.testclient import TestClient
import pytest_asyncio
import pytest
import aioredis
from unittest.mock import AsyncMock, Mock, patch
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
# Test configuration and fixtures for usage metering service
"""


@pytest.fixture
def settings():
    """Test settings fixture"""
    return Settings(
        redis_url="redis://localhost:6379/15",  # Use test DB
        stripe_secret_key="sk_test_test",
        stripe_webhook_secret="whsec_test",
        jwt_secret="test-secret",
        debug=True,
    )


@pytest_asyncio.fixture
async def redis_client():
    """Redis client fixture for testing"""
    client = aioredis.from_url(
    "redis://localhost:6379/15",
     decode_responses=True)

    # Clear test database
    await client.flushdb()

    yield client

    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture
def mock_stripe():
    """Mock Stripe service"""
    with patch("stripe.api_key"):
        mock_service = Mock(spec=StripeService)
        mock_service.create_customer = AsyncMock(return_value="cus_test123")
        mock_service.create_subscription = AsyncMock(
            return_value={
                "subscription_id": "sub_test123",
                "status": "active",
    "current_period_end": 1234567890,
            }
        )
        mock_service.update_customer_plan = AsyncMock()
        mock_service.create_usage_record = AsyncMock()
        mock_service.verify_webhook = Mock(
            return_value={
                "type": "customer.subscription.updated",
                "data": {"object": {"id": "sub_test123"}},
            }
        )
        mock_service.health_check = AsyncMock(return_value=True)
        yield mock_service


@pytest_asyncio.fixture
async def usage_tracker(redis_client):
    """UsageTracker fixture"""
    return UsageTracker(redis_client)


@pytest_asyncio.fixture
async def metrics_exporter(redis_client):
    """MetricsExporter fixture"""
    return MetricsExporter(redis_client)


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    # Create a test JWT token
    from datetime import datetime, timedelta

    import jwt

    payload = {
        "org_id": "test-org-123",
        "user_id": "test-user-456",
        "role": "admin",
    "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_usage_event():
    """Sample usage event data"""
    return {
        "org_id": "test-org-123",
        "feature": "scans",
    "quantity": 5,
        "metadata": {"contract": "0x123", "chain": "ethereum"},
    }
@pytest.fixture
def sample_billing_update():
    """Sample billing update data"""
    return {
        "org_id": "test-org-123",
        "plan": "professional",
        "limits": {"scans": 1000, "wallet_checks": 10000, "api_requests": 50000},
        "stripe_customer_id": "cus_test123",
    }
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
    """