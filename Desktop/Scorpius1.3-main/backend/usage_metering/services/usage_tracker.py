"""
Usage tracking service using Redis for fast access
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aioredis

from ..models import BillingEvent, FeatureUsage, OrganizationUsage, UsageRecord

logger = logging.getLogger(__name__)


class UsageTracker:
    """Redis-based usage tracking service"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.usage_prefix = "usage:"
        self.org_prefix = "org:"
        self.billing_prefix = "billing:"

    async def record_usage(
        self, org_id: str, feature: str, quantity: int = 1, metadata: Dict = None
    ) -> UsageRecord:
        """Record a usage event"""
        try:
            timestamp = datetime.utcnow()
            reset_date = self._get_next_reset_date(timestamp)

            # Create usage record
            usage_record = UsageRecord(
                org_id=org_id,
                feature=feature,
                quantity=quantity,
                timestamp=timestamp,
                reset_date=reset_date,
                metadata=metadata or {},
            )

            # Update current usage in Redis
            usage_key = f"{self.usage_prefix}{org_id}:{feature}"
            reset_key = f"{usage_key}:reset"

            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()

            # Check if we need to reset usage (new period)
            current_reset = await self.redis.get(reset_key)
            if not current_reset or datetime.fromisoformat(current_reset) < timestamp:
                # Reset usage for new period
                pipe.set(usage_key, quantity)
                pipe.set(reset_key, reset_date.isoformat())
            else:
                # Increment existing usage
                pipe.incrby(usage_key, quantity)

            # Set expiration (1 month after reset date)
            expire_seconds = int(
                (reset_date + timedelta(days=30) - timestamp).total_seconds()
            )
            pipe.expire(usage_key, expire_seconds)
            pipe.expire(reset_key, expire_seconds)

            await pipe.execute()

            # Store individual usage record for audit
            record_key = f"{self.usage_prefix}records:{org_id}:{timestamp.isoformat()}"
            await self.redis.setex(
                record_key, expire_seconds, json.dumps(usage_record.dict(), default=str)
            )

            logger.info(
                f"Recorded usage: org={org_id}, feature={feature}, quantity={quantity}"
            )
            return usage_record

        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            raise

    async def get_organization_usage(self, org_id: str) -> Optional[OrganizationUsage]:
        """Get current usage for an organization"""
        try:
            # Get organization metadata
            org_key = f"{self.org_prefix}{org_id}"
            org_data = await self.redis.hgetall(org_key)

            if not org_data:
                # Create default organization
                org_data = {
                    "plan": "free",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                await self.redis.hset(org_key, mapping=org_data)

            # Get all usage keys for this organization
            usage_pattern = f"{self.usage_prefix}{org_id}:*"
            usage_keys = await self.redis.keys(usage_pattern)

            features = {}

            for key in usage_keys:
                if key.endswith(":reset"):
                    continue

                # Extract feature name
                feature = key.replace(f"{self.usage_prefix}{org_id}:", "")

                # Get current usage and reset date
                current_usage = await self.redis.get(key) or 0
                reset_key = f"{key}:reset"
                reset_date_str = await self.redis.get(reset_key)

                if reset_date_str:
                    reset_date = datetime.fromisoformat(reset_date_str)
                else:
                    reset_date = self._get_next_reset_date(datetime.utcnow())

                # Get limits from organization plan
                limits = await self._get_plan_limits(org_data.get("plan", "free"))
                feature_limit = limits.get(feature, -1)

                features[feature] = FeatureUsage(
                    current=int(current_usage),
                    limit=feature_limit,
                    reset_date=reset_date,
                    last_updated=datetime.utcnow(),
                )

            return OrganizationUsage(
                org_id=org_id,
                plan=org_data.get("plan", "free"),
                features=features,
                stripe_customer_id=org_data.get("stripe_customer_id"),
                payment_overdue=bool(org_data.get("payment_overdue", False)),
                created_at=datetime.fromisoformat(org_data["created_at"]),
                updated_at=datetime.fromisoformat(org_data["updated_at"]),
            )

        except Exception as e:
            logger.error(f"Failed to get organization usage: {e}")
            return None

    async def update_organization_limits(
        self, org_id: str, plan: str, limits: Dict[str, int]
    ):
        """Update organization plan and limits"""
        try:
            org_key = f"{self.org_prefix}{org_id}"

            # Update organization data
            await self.redis.hset(
                org_key,
                mapping={"plan": plan, "updated_at": datetime.utcnow().isoformat()},
            )

            # Store plan limits
            limits_key = f"{self.org_prefix}limits:{plan}"
            await self.redis.hset(limits_key, mapping=limits)

            logger.info(f"Updated organization limits: org={org_id}, plan={plan}")

        except Exception as e:
            logger.error(f"Failed to update organization limits: {e}")
            raise

    async def record_billing_event(self, event: BillingEvent):
        """Record a billing event for processing"""
        try:
            event_key = (
                f"{self.billing_prefix}{event.org_id}:{event.timestamp.isoformat()}"
            )
            await self.redis.setex(
                event_key,
                86400 * 30,  # 30 days retention
                json.dumps(event.dict(), default=str),
            )

            logger.info(
                f"Recorded billing event: {event.event_type} for org {event.org_id}"
            )

        except Exception as e:
            logger.error(f"Failed to record billing event: {e}")
            raise

    async def get_org_by_customer_id(self, customer_id: str) -> Optional[str]:
        """Get organization ID by Stripe customer ID"""
        try:
            # Search for organization with this customer ID
            pattern = f"{self.org_prefix}*"
            org_keys = await self.redis.keys(pattern)

            for org_key in org_keys:
                org_data = await self.redis.hgetall(org_key)
                if org_data.get("stripe_customer_id") == customer_id:
                    # Extract org_id from key
                    return org_key.replace(self.org_prefix, "")

            return None

        except Exception as e:
            logger.error(f"Failed to find org by customer ID: {e}")
            return None

    async def mark_payment_overdue(self, org_id: str):
        """Mark organization as having overdue payment"""
        try:
            org_key = f"{self.org_prefix}{org_id}"
            await self.redis.hset(org_key, "payment_overdue", "true")

            logger.warning(f"Marked payment overdue for org {org_id}")

        except Exception as e:
            logger.error(f"Failed to mark payment overdue: {e}")
            raise

    def _get_next_reset_date(self, current_date: datetime) -> datetime:
        """Calculate next reset date based on billing cycle"""
        # For monthly billing, reset on the first of next month
        if current_date.month == 12:
            return datetime(current_date.year + 1, 1, 1)
        else:
            return datetime(current_date.year, current_date.month + 1, 1)

    async def _get_plan_limits(self, plan: str) -> Dict[str, int]:
        """Get limits for a plan"""
        try:
            limits_key = f"{self.org_prefix}limits:{plan}"
            limits = await self.redis.hgetall(limits_key)

            if not limits:
                # Default limits
                default_limits = {
                    "free": {"scans": 10, "wallet_checks": 100, "api_requests": 1000},
                    "professional": {
                        "scans": 1000,
                        "wallet_checks": 10000,
                        "api_requests": 50000,
                    },
                    "enterprise": {
                        "scans": -1,
                        "wallet_checks": -1,
                        "api_requests": -1,
                    },
                }

                limits = default_limits.get(plan, default_limits["free"])
                await self.redis.hset(limits_key, mapping=limits)

            # Convert to integers
            return {k: int(v) for k, v in limits.items()}

        except Exception as e:
            logger.error(f"Failed to get plan limits: {e}")
            return {"scans": 10, "wallet_checks": 100, "api_requests": 1000}
