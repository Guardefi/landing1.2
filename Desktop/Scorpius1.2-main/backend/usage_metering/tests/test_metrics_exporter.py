"""
Test metrics exporter functionality
"""

from unittest.mock import AsyncMock

import pytest


class TestMetricsExporter:
    """Test metrics export functionality"""

    @pytest.mark.asyncio
    async def test_generate_usage_metrics(self, metrics_exporter, redis_client):
        """Test generating Prometheus metrics"""
        # Set up test data
        await redis_client.set("usage:org1:scans", 50)
        await redis_client.set("usage:org1:wallet_checks", 200)
        await redis_client.set("usage:org2:scans", 30)

        # Set up organization data
        await redis_client.hset(
            "org:org1",
            mapping={
                "plan": "professional",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
        )
        await redis_client.hset(
            "org:org2",
            mapping={
                "plan": "free",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
        )

        # Generate metrics
        metrics = await metrics_exporter.generate_usage_metrics()

        # Verify metrics format
        assert "scorpius_total_organizations" in metrics
        assert "scorpius_feature_usage_total" in metrics
        assert "scorpius_plan_distribution" in metrics
        assert "# HELP" in metrics
        assert "# TYPE" in metrics

    @pytest.mark.asyncio
    async def test_feature_usage_breakdown(self, metrics_exporter, redis_client):
        """Test feature usage breakdown"""
        # Set up test data
        await redis_client.set("usage:org1:scans", 25)
        await redis_client.set("usage:org1:wallet_checks", 150)
        await redis_client.set("usage:org2:scans", 10)

        # Set up organization plans
        await redis_client.hset("org:org1", "plan", "professional")
        await redis_client.hset("org:org2", "plan", "free")

        # Get breakdown
        breakdown = await metrics_exporter._get_feature_usage_breakdown()

        # Verify breakdown
        assert ("scans", "professional") in breakdown
        assert ("wallet_checks", "professional") in breakdown
        assert ("scans", "free") in breakdown
        assert breakdown[("scans", "professional")] == 25
        assert breakdown[("wallet_checks", "professional")] == 150
        assert breakdown[("scans", "free")] == 10

    @pytest.mark.asyncio
    async def test_plan_distribution(self, metrics_exporter, redis_client):
        """Test plan distribution metrics"""
        # Set up organizations with different plans
        await redis_client.hset("org:org1", "plan", "free")
        await redis_client.hset("org:org2", "plan", "professional")
        await redis_client.hset("org:org3", "plan", "professional")
        await redis_client.hset("org:org4", "plan", "enterprise")

        # Get distribution
        distribution = await metrics_exporter._get_plan_distribution()

        # Verify distribution
        assert distribution["free"] == 1
        assert distribution["professional"] == 2
        assert distribution["enterprise"] == 1

    @pytest.mark.asyncio
    async def test_top_usage_orgs(self, metrics_exporter, redis_client):
        """Test top usage organizations"""
        # Set up usage data
        await redis_client.set("usage:org1:scans", 100)
        await redis_client.set("usage:org1:wallet_checks", 500)
        await redis_client.set("usage:org2:scans", 50)
        await redis_client.set("usage:org3:wallet_checks", 800)

        # Get top usage
        top_usage = await metrics_exporter._get_top_usage_orgs(limit=3)

        # Verify top usage (org3 should be first with 800, org1 second with 600, org2 third with 50)
        assert len(top_usage) <= 3
        assert "org1" in top_usage
        assert "org2" in top_usage
        assert "org3" in top_usage

    @pytest.mark.asyncio
    async def test_empty_metrics(self, metrics_exporter):
        """Test metrics generation with no data"""
        metrics = await metrics_exporter.generate_usage_metrics()

        # Should still generate valid metrics format
        assert "scorpius_total_organizations 0" in metrics
        assert "# HELP" in metrics
        assert "# TYPE" in metrics

    @pytest.mark.asyncio
    async def test_metrics_error_handling(self, metrics_exporter):
        """Test error handling in metrics generation"""
        # Mock Redis to raise an error
        metrics_exporter.redis = AsyncMock()
        metrics_exporter.redis.keys.side_effect = Exception("Redis error")

        # Should return error message instead of crashing
        metrics = await metrics_exporter.generate_usage_metrics()
        assert "Error generating metrics" in metrics
