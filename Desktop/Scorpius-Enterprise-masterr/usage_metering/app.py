"""
Usage Metering & Billing Service
Tracks usage by org_id and integrates with Stripe billing
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aioredis
import stripe
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from starlette.responses import Response

from .core.auth import verify_token
from .core.config import get_settings
from .models import BillingEvent, OrganizationUsage, UsageRecord
from .services.metrics_exporter import MetricsExporter
from .services.stripe_service import StripeService
from .services.usage_tracker import UsageTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
usage_counter = Counter(
    "scorpius_usage_total", "Total usage events", ["org_id", "feature", "plan"]
)
billing_events = Counter(
    "scorpius_billing_events_total", "Total billing events", ["event_type", "org_id"]
)
api_latency = Histogram("scorpius_usage_api_duration_seconds", "API request duration")

app = FastAPI(
    title="Scorpius Usage Metering Service",
    description="Enterprise usage tracking and billing integration",
    version="1.0.0",
)

security = HTTPBearer()
settings = get_settings()

# Global services
redis_client: Optional[aioredis.Redis] = None
usage_tracker: Optional[UsageTracker] = None
stripe_service: Optional[StripeService] = None
metrics_exporter: Optional[MetricsExporter] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global redis_client, usage_tracker, stripe_service, metrics_exporter

    try:
        # Initialize Redis client
        redis_client = aioredis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )

        # Initialize services
        usage_tracker = UsageTracker(redis_client)
        stripe_service = StripeService(settings.stripe_secret_key)
        metrics_exporter = MetricsExporter(redis_client)

        logger.info("Usage metering service started successfully")

    except Exception as e:
        logger.error(f"Failed to start usage metering service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if redis_client:
        await redis_client.close()


# Request/Response Models
class UsageEvent(BaseModel):
    org_id: str
    feature: str
    quantity: int = 1
    metadata: Dict = {}


class UsageResponse(BaseModel):
    org_id: str
    feature: str
    current_usage: int
    limit: int
    remaining: int
    reset_date: datetime


class BillingUpdate(BaseModel):
    org_id: str
    plan: str
    limits: Dict[str, int]
    stripe_customer_id: Optional[str] = None


# Dependency for authentication
async def get_current_org(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract org_id from JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        return payload.get("org_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


@app.post("/usage/track", response_model=UsageResponse)
@api_latency.time()
async def track_usage(event: UsageEvent, org_id: str = Depends(get_current_org)):
    """Track usage event for an organization"""
    try:
        # Verify org_id matches token
        if event.org_id != org_id:
            raise HTTPException(status_code=403, detail="Organization ID mismatch")

        # Record usage
        usage_record = await usage_tracker.record_usage(
            org_id=event.org_id,
            feature=event.feature,
            quantity=event.quantity,
            metadata=event.metadata,
        )

        # Check limits
        org_usage = await usage_tracker.get_organization_usage(event.org_id)
        feature_usage = org_usage.features.get(event.feature, {})

        current_usage = feature_usage.get("current", 0)
        limit = feature_usage.get("limit", float("inf"))

        # Update Prometheus metrics
        plan = org_usage.plan or "free"
        usage_counter.labels(org_id=event.org_id, feature=event.feature, plan=plan).inc(
            event.quantity
        )

        # Check for overage and trigger billing events
        if current_usage > limit:
            await _handle_overage(event.org_id, event.feature, current_usage, limit)

        return UsageResponse(
            org_id=event.org_id,
            feature=event.feature,
            current_usage=current_usage,
            limit=limit,
            remaining=max(0, limit - current_usage),
            reset_date=usage_record.reset_date,
        )

    except Exception as e:
        logger.error(f"Failed to track usage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/usage/{org_id}", response_model=OrganizationUsage)
@api_latency.time()
async def get_usage(org_id: str, current_org: str = Depends(get_current_org)):
    """Get current usage for an organization"""
    try:
        # Verify access
        if org_id != current_org:
            raise HTTPException(status_code=403, detail="Access denied")

        usage = await usage_tracker.get_organization_usage(org_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Organization not found")

        return usage

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/billing/update")
@api_latency.time()
async def update_billing(
    update: BillingUpdate,
    background_tasks: BackgroundTasks,
    current_org: str = Depends(get_current_org),
):
    """Update organization billing plan and limits"""
    try:
        # Verify admin access (you might want to add role checking here)
        if update.org_id != current_org:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update usage limits
        await usage_tracker.update_organization_limits(
            org_id=update.org_id, plan=update.plan, limits=update.limits
        )

        # Update Stripe customer if provided
        if update.stripe_customer_id:
            background_tasks.add_task(
                stripe_service.update_customer_plan,
                update.stripe_customer_id,
                update.plan,
            )

        billing_events.labels(event_type="plan_update", org_id=update.org_id).inc()

        return {"status": "success", "message": "Billing updated successfully"}

    except Exception as e:
        logger.error(f"Failed to update billing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/webhooks/stripe")
async def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        event = stripe_service.verify_webhook(payload, sig_header)

        if event["type"] == "customer.subscription.updated":
            await _handle_subscription_update(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            await _handle_subscription_cancellation(event["data"]["object"])
        elif event["type"] == "invoice.payment_failed":
            await _handle_payment_failure(event["data"]["object"])

        billing_events.labels(event_type=event["type"], org_id="webhook").inc()

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@app.get("/metrics/usage")
async def usage_metrics():
    """Prometheus metrics endpoint for usage data"""
    try:
        # Generate custom usage metrics
        metrics_data = await metrics_exporter.generate_usage_metrics()

        # Combine with Prometheus metrics
        prometheus_metrics = generate_latest()

        return Response(
            content=prometheus_metrics + metrics_data.encode(),
            media_type=CONTENT_TYPE_LATEST,
        )

    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        raise HTTPException(status_code=500, detail="Metrics generation failed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        await redis_client.ping()

        # Check Stripe connection
        stripe_health = await stripe_service.health_check()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": "healthy",
                "stripe": "healthy" if stripe_health else "unhealthy",
            },
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }


# Helper functions
async def _handle_overage(org_id: str, feature: str, current: int, limit: int):
    """Handle usage overage events"""
    overage_amount = current - limit

    # Log overage
    logger.warning(
        f"Usage overage detected: org={org_id}, feature={feature}, overage={overage_amount}"
    )

    # Create billing event
    billing_event = BillingEvent(
        org_id=org_id,
        event_type="overage",
        feature=feature,
        quantity=overage_amount,
        timestamp=datetime.utcnow(),
    )

    # Store for billing processing
    await usage_tracker.record_billing_event(billing_event)

    # Update metrics
    billing_events.labels(event_type="overage", org_id=org_id).inc()


async def _handle_subscription_update(subscription):
    """Handle Stripe subscription updates"""
    customer_id = subscription.get("customer")

    # Get organization by Stripe customer ID
    org_id = await usage_tracker.get_org_by_customer_id(customer_id)
    if not org_id:
        logger.error(f"No organization found for customer {customer_id}")
        return

    # Extract plan information
    plan_name = subscription["items"]["data"][0]["price"]["nickname"] or "enterprise"

    # Update organization plan
    plan_limits = _get_plan_limits(plan_name)
    await usage_tracker.update_organization_limits(org_id, plan_name, plan_limits)

    logger.info(f"Updated subscription for org {org_id} to plan {plan_name}")


async def _handle_subscription_cancellation(subscription):
    """Handle subscription cancellations"""
    customer_id = subscription.get("customer")
    org_id = await usage_tracker.get_org_by_customer_id(customer_id)

    if org_id:
        # Downgrade to free plan
        free_limits = _get_plan_limits("free")
        await usage_tracker.update_organization_limits(org_id, "free", free_limits)
        logger.info(f"Downgraded org {org_id} to free plan")


async def _handle_payment_failure(invoice):
    """Handle failed payments"""
    customer_id = invoice.get("customer")
    org_id = await usage_tracker.get_org_by_customer_id(customer_id)

    if org_id:
        # Implement soft limits or notifications
        await usage_tracker.mark_payment_overdue(org_id)
        logger.warning(f"Payment failed for org {org_id}")


def _get_plan_limits(plan_name: str) -> Dict[str, int]:
    """Get usage limits for a plan"""
    plan_limits = {
        "free": {"scans": 10, "wallet_checks": 100, "api_requests": 1000},
        "professional": {"scans": 1000, "wallet_checks": 10000, "api_requests": 50000},
        "enterprise": {
            "scans": -1,  # Unlimited
            "wallet_checks": -1,
            "api_requests": -1,
        },
    }

    return plan_limits.get(plan_name, plan_limits["free"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
