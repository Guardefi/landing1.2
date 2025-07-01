"""
Test usage tracker service
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from backend.usage_metering.models import BillingEvent, OrganizationUsage, UsageRecord
from backend.usage_metering.services.usage_tracker import UsageTracker


class TestUsageTracker:
    """Test usage tracking functionality"""

    @pytest.mark.asyncio
    async def test_record_usage(self, usage_tracker):
        """Test recording usage events"""
        result = await usage_tracker.record_usage(
            org_id="test-org", feature="scans", quantity=5, metadata={"test": "data"}
        )

        assert isinstance(result, UsageRecord)
        assert result.org_id == "test-org"
        assert result.feature == "scans"
        assert result.quantity == 5
        assert result.metadata == {"test": "data"}

    @pytest.mark.asyncio
    async def test_get_organization_usage(self, usage_tracker):
        """Test retrieving organization usage"""
        # First record some usage
        await usage_tracker.record_usage("test-org", "scans", 3)
        await usage_tracker.record_usage("test-org", "wallet_checks", 10)

        # Get usage
        usage = await usage_tracker.get_organization_usage("test-org")

        assert isinstance(usage, OrganizationUsage)
        assert usage.org_id == "test-org"
        assert usage.plan == "free"  # Default plan
        assert "scans" in usage.features
        assert "wallet_checks" in usage.features
        assert usage.features["scans"].current == 3
        assert usage.features["wallet_checks"].current == 10

    @pytest.mark.asyncio
    async def test_update_organization_limits(self, usage_tracker):
        """Test updating organization limits"""
        limits = {"scans": 1000, "wallet_checks": 10000, "api_requests": 50000}

        await usage_tracker.update_organization_limits(
            org_id="test-org", plan="professional", limits=limits
        )

        # Verify the update
        usage = await usage_tracker.get_organization_usage("test-org")
        assert usage.plan == "professional"

    @pytest.mark.asyncio
    async def test_record_billing_event(self, usage_tracker):
        """Test recording billing events"""
        event = BillingEvent(
            org_id="test-org",
            event_type="overage",
            feature="scans",
            quantity=5,
            timestamp=datetime.utcnow(),
        )

        # Should not raise exception
        await usage_tracker.record_billing_event(event)

    @pytest.mark.asyncio
    async def test_usage_reset_cycle(self, usage_tracker):
        """Test usage reset functionality"""
        # Record usage
        await usage_tracker.record_usage("test-org", "scans", 5)

        # Get current usage
        usage = await usage_tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 5

        # Simulate reset by setting past reset date
        past_date = datetime.utcnow() - timedelta(days=32)
        reset_key = f"usage:test-org:scans:reset"
        await usage_tracker.redis.set(reset_key, past_date.isoformat())

        # Record new usage (should reset)
        await usage_tracker.record_usage("test-org", "scans", 2)

        # Should show only new usage
        usage = await usage_tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 2

    @pytest.mark.asyncio
    async def test_get_org_by_customer_id(self, usage_tracker):
        """Test finding organization by Stripe customer ID"""
        # Set up organization with customer ID
        org_key = "org:test-org"
        await usage_tracker.redis.hset(
            org_key,
            mapping={
                "plan": "professional",
                "stripe_customer_id": "cus_test123",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        # Find by customer ID
        org_id = await usage_tracker.get_org_by_customer_id("cus_test123")
        assert org_id == "test-org"

        # Test not found
        org_id = await usage_tracker.get_org_by_customer_id("cus_notfound")
        assert org_id is None

    @pytest.mark.asyncio
    async def test_mark_payment_overdue(self, usage_tracker):
        """Test marking payment as overdue"""
        await usage_tracker.mark_payment_overdue("test-org")

        # Verify the flag is set
        usage = await usage_tracker.get_organization_usage("test-org")
        assert usage.payment_overdue == True

    @pytest.mark.asyncio
    async def test_plan_limits(self, usage_tracker):
        """Test plan limits functionality"""
        # Test default limits
        limits = await usage_tracker._get_plan_limits("free")
        assert limits["scans"] == 10
        assert limits["wallet_checks"] == 100

        # Test professional limits
        limits = await usage_tracker._get_plan_limits("professional")
        assert limits["scans"] == 1000
        assert limits["wallet_checks"] == 10000

        # Test enterprise limits (unlimited)
        limits = await usage_tracker._get_plan_limits("enterprise")
        assert limits["scans"] == -1
        assert limits["wallet_checks"] == -1

    def test_next_reset_date(self, usage_tracker):
        """Test reset date calculation"""
        # Test middle of year
        current = datetime(2024, 6, 15)
        next_reset = usage_tracker._get_next_reset_date(current)
        assert next_reset == datetime(2024, 7, 1)

        # Test end of year
        current = datetime(2024, 12, 15)
        next_reset = usage_tracker._get_next_reset_date(current)
        assert next_reset == datetime(2025, 1, 1)
