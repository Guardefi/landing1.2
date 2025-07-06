"""
Pydantic models for usage metering service
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class UsageRecord(BaseModel):
    """Individual usage record"""

    org_id: str
    feature: str
    quantity: int
    timestamp: datetime
    reset_date: datetime
    metadata: Dict = {}


class FeatureUsage(BaseModel):
    """Usage data for a specific feature"""

    current: int = 0
    limit: int = -1  # -1 means unlimited
    reset_date: datetime
    last_updated: datetime


class OrganizationUsage(BaseModel):
    """Complete usage data for an organization"""

    org_id: str
    plan: str = "free"
    features: Dict[str, FeatureUsage] = {}
    stripe_customer_id: Optional[str] = None
    payment_overdue: bool = False
    created_at: datetime
    updated_at: datetime


class BillingEvent(BaseModel):
    """Billing event for processing"""

    org_id: str
    event_type: str  # overage, plan_change, payment_failure
    feature: Optional[str] = None
    quantity: int = 0


class MeteringRequest(BaseModel):
    """Request model for usage metering queries"""

    org_id: str
    start_date: str
    end_date: str
    feature: Optional[str] = None


class UsageEvent(BaseModel):
    """Usage event model for tracking feature usage"""

    org_id: str
    feature: str
    quantity: int = 1
    timestamp: float
    metadata: Optional[Dict] = {}
    processed: bool = False
    metadata: Dict = {}


class UsageMetrics(BaseModel):
    """Aggregated usage metrics"""

    total_organizations: int
    total_usage_events: int
    features_breakdown: Dict[str, int]
    plan_distribution: Dict[str, int]
    timestamp: datetime


class PlanLimits(BaseModel):
    """Plan configuration with limits"""

    name: str
    limits: Dict[str, int]
    price_monthly: Optional[float] = None
    stripe_price_id: Optional[str] = None
    features: List[str] = []
