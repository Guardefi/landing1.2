"""
Integration tests for usage metering service
"""

import asyncio
from datetime import datetime, timedelta

import aioredis
import pytest
from fastapi.testclient import TestClient

from ..app import app
from ..models import OrganizationUsage, UsageRecord


class TestIntegration:
    """Integration tests with real Redis"""

    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create event loop for class"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(scope="class")
    async def redis_setup(self):
        """Set up Redis for integration tests"""
        redis_client = aioredis.from_url(
            "redis://localhost:6379/15", decode_responses=True
        )
        await redis_client.flushdb()
        yield redis_client
        await redis_client.flushdb()
        await redis_client.close()

    @pytest.mark.integration
    async def test_full_usage_flow(self, redis_setup):
        """Test complete usage tracking flow"""
        redis_client = redis_setup

        from ..services.usage_tracker import UsageTracker

        tracker = UsageTracker(redis_client)

        # Record initial usage
        record1 = await tracker.record_usage("test-org", "scans", 5)
        assert record1.quantity == 5

        # Record more usage
        record2 = await tracker.record_usage("test-org", "scans", 3)
        assert record2.quantity == 3

        # Check total usage
        usage = await tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 8
        assert usage.features["scans"].limit == 10  # Free plan default

        # Upgrade plan
        await tracker.update_organization_limits(
            "test-org", "professional", {"scans": 1000, "wallet_checks": 10000}
        )

        # Verify upgrade
        usage = await tracker.get_organization_usage("test-org")
        assert usage.plan == "professional"
        assert usage.features["scans"].current == 8  # Usage preserved
        assert usage.features["scans"].limit == 1000  # New limit

    @pytest.mark.integration
    async def test_overage_handling(self, redis_setup):
        """Test usage overage scenarios"""
        redis_client = redis_setup

        from ..services.usage_tracker import UsageTracker

        tracker = UsageTracker(redis_client)

        # Set low limits
        await tracker.update_organization_limits(
            "test-org", "free", {"scans": 5, "wallet_checks": 10}
        )

        # Record usage up to limit
        await tracker.record_usage("test-org", "scans", 5)
        usage = await tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 5

        # Exceed limit
        await tracker.record_usage("test-org", "scans", 2)
        usage = await tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 7  # Over limit

    @pytest.mark.integration
    async def test_billing_cycle_reset(self, redis_setup):
        """Test billing cycle reset functionality"""
        redis_client = redis_setup

        from ..services.usage_tracker import UsageTracker

        tracker = UsageTracker(redis_client)

        # Record usage
        await tracker.record_usage("test-org", "scans", 8)

        # Verify initial usage
        usage = await tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 8

        # Simulate month rollover by setting old reset date
        past_date = datetime.utcnow() - timedelta(days=32)
        reset_key = "usage:test-org:scans:reset"
        await redis_client.set(reset_key, past_date.isoformat())

        # Record new usage (should trigger reset)
        await tracker.record_usage("test-org", "scans", 3)

        # Should show only new usage
        usage = await tracker.get_organization_usage("test-org")
        assert usage.features["scans"].current == 3

    @pytest.mark.integration
    async def test_multiple_orgs_isolation(self, redis_setup):
        """Test that organizations are properly isolated"""
        redis_client = redis_setup

        from ..services.usage_tracker import UsageTracker

        tracker = UsageTracker(redis_client)

        # Record usage for different orgs
        await tracker.record_usage("org-1", "scans", 10)
        await tracker.record_usage("org-2", "scans", 20)
        await tracker.record_usage("org-1", "wallet_checks", 50)

        # Check org-1 usage
        usage1 = await tracker.get_organization_usage("org-1")
        assert usage1.features["scans"].current == 10
        assert usage1.features["wallet_checks"].current == 50
        assert "org-1" == usage1.org_id

        # Check org-2 usage
        usage2 = await tracker.get_organization_usage("org-2")
        assert usage2.features["scans"].current == 20
        assert "wallet_checks" not in usage2.features
        assert "org-2" == usage2.org_id

    @pytest.mark.integration
    async def test_metrics_generation(self, redis_setup):
        """Test metrics generation with real data"""
        redis_client = redis_setup

        from ..services.metrics_exporter import MetricsExporter

        exporter = MetricsExporter(redis_client)

        # Set up test data
        await redis_client.set("usage:org1:scans", 100)
        await redis_client.set("usage:org1:wallet_checks", 500)
        await redis_client.set("usage:org2:scans", 50)

        await redis_client.hset(
            "org:org1",
            mapping={
                "plan": "professional",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        await redis_client.hset(
            "org:org2",
            mapping={
                "plan": "free",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        # Generate metrics
        metrics = await exporter.generate_usage_metrics()

        # Verify content
        assert "scorpius_total_organizations 2" in metrics
        assert (
            'scorpius_feature_usage_total{feature="scans",plan="professional"} 100'
            in metrics
        )
        assert (
            'scorpius_feature_usage_total{feature="wallet_checks",plan="professional"} 500'
            in metrics
        )
        assert 'scorpius_feature_usage_total{feature="scans",plan="free"} 50' in metrics
        assert 'scorpius_plan_distribution{plan="professional"} 1' in metrics
        assert 'scorpius_plan_distribution{plan="free"} 1' in metrics
