"""
Metrics exporter for Prometheus integration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

import aioredis

logger = logging.getLogger(__name__)


class MetricsExporter:
    """Export usage metrics in Prometheus format"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.usage_prefix = "usage:"
        self.org_prefix = "org:"

    async def generate_usage_metrics(self) -> str:
        """Generate Prometheus metrics for usage data"""
        try:
            metrics = []

            # Get all organizations
            org_keys = await self.redis.keys(f"{self.org_prefix}*")
            org_count = len([k for k in org_keys if not k.endswith(":limits")])

            # Total organizations metric
            metrics.append(
                f"# HELP scorpius_total_organizations Total number of organizations"
            )
            metrics.append(f"# TYPE scorpius_total_organizations gauge")
            metrics.append(f"scorpius_total_organizations {org_count}")

            # Usage by feature and plan
            feature_usage = await self._get_feature_usage_breakdown()

            metrics.append(
                f"# HELP scorpius_feature_usage_total Total usage by feature and plan"
            )
            metrics.append(f"# TYPE scorpius_feature_usage_total counter")

            for (feature, plan), usage in feature_usage.items():
                metrics.append(
                    f'scorpius_feature_usage_total{{feature="{feature}",plan="{plan}"}} {usage}'
                )

            # Plan distribution
            plan_distribution = await self._get_plan_distribution()

            metrics.append(f"# HELP scorpius_plan_distribution Organizations by plan")
            metrics.append(f"# TYPE scorpius_plan_distribution gauge")

            for plan, count in plan_distribution.items():
                metrics.append(f'scorpius_plan_distribution{{plan="{plan}"}} {count}')

            # Usage metrics by organization (top 10)
            top_usage = await self._get_top_usage_orgs()

            metrics.append(f"# HELP scorpius_org_usage_total Usage by organization")
            metrics.append(f"# TYPE scorpius_org_usage_total counter")

            for org_id, usage in top_usage.items():
                metrics.append(f'scorpius_org_usage_total{{org_id="{org_id}"}} {usage}')

            return "\n".join(metrics) + "\n"

        except Exception as e:
            logger.error(f"Failed to generate usage metrics: {e}")
            return "# Error generating metrics\n"

    async def _get_feature_usage_breakdown(self) -> Dict:
        """Get usage breakdown by feature and plan"""
        try:
            feature_usage = {}

            # Get all usage keys
            usage_keys = await self.redis.keys(f"{self.usage_prefix}*")

            for key in usage_keys:
                if key.endswith(":reset") or ":records:" in key:
                    continue

                # Extract org_id and feature
                key_parts = key.replace(self.usage_prefix, "").split(":")
                if len(key_parts) < 2:
                    continue

                org_id = key_parts[0]
                feature = key_parts[1]

                # Get organization plan
                org_key = f"{self.org_prefix}{org_id}"
                org_data = await self.redis.hgetall(org_key)
                plan = org_data.get("plan", "free")

                # Get usage value
                usage = await self.redis.get(key) or 0

                key_tuple = (feature, plan)
                feature_usage[key_tuple] = feature_usage.get(key_tuple, 0) + int(usage)

            return feature_usage

        except Exception as e:
            logger.error(f"Failed to get feature usage breakdown: {e}")
            return {}

    async def _get_plan_distribution(self) -> Dict[str, int]:
        """Get distribution of organizations by plan"""
        try:
            plan_distribution = {}

            # Get all organization keys
            org_keys = await self.redis.keys(f"{self.org_prefix}*")

            for org_key in org_keys:
                if org_key.endswith(":limits"):
                    continue

                org_data = await self.redis.hgetall(org_key)
                plan = org_data.get("plan", "free")
                plan_distribution[plan] = plan_distribution.get(plan, 0) + 1

            return plan_distribution

        except Exception as e:
            logger.error(f"Failed to get plan distribution: {e}")
            return {}

    async def _get_top_usage_orgs(self, limit: int = 10) -> Dict[str, int]:
        """Get top organizations by total usage"""
        try:
            org_usage = {}

            # Get all usage keys
            usage_keys = await self.redis.keys(f"{self.usage_prefix}*")

            for key in usage_keys:
                if key.endswith(":reset") or ":records:" in key:
                    continue

                # Extract org_id
                key_parts = key.replace(self.usage_prefix, "").split(":")
                if len(key_parts) < 2:
                    continue

                org_id = key_parts[0]
                usage = await self.redis.get(key) or 0

                org_usage[org_id] = org_usage.get(org_id, 0) + int(usage)

            # Sort and limit
            sorted_usage = sorted(org_usage.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_usage[:limit])

        except Exception as e:
            logger.error(f"Failed to get top usage orgs: {e}")
            return {}
