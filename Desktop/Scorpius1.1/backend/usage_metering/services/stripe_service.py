"""
Stripe integration service for billing
"""

import logging
from datetime import datetime
from typing import Dict, Optional

import stripe

logger = logging.getLogger(__name__)


class StripeService:
    """Stripe integration for billing operations"""

    def __init__(self, secret_key: str, webhook_secret: str = None):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        stripe.api_key = secret_key

    async def create_customer(self, org_id: str, email: str, name: str) -> str:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email, name=name, metadata={"org_id": org_id}
            )

            logger.info(f"Created Stripe customer {customer.id} for org {org_id}")
            return customer.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def create_subscription(
        self, customer_id: str, price_id: str, metadata: Dict = None
    ) -> Dict:
        """Create a subscription for a customer"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
            )

            logger.info(
                f"Created subscription {subscription.id} for customer {customer_id}"
            )
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    async def update_customer_plan(self, customer_id: str, plan: str):
        """Update customer's plan in Stripe"""
        try:
            # Get plan price ID mapping
            price_mapping = {
                "professional": "price_professional_monthly",
                "enterprise": "price_enterprise_monthly",
            }

            price_id = price_mapping.get(plan)
            if not price_id:
                logger.warning(f"No Stripe price ID for plan {plan}")
                return

            # Get customer's current subscription
            subscriptions = stripe.Subscription.list(
                customer=customer_id, status="active"
            )

            if subscriptions.data:
                subscription = subscriptions.data[0]

                # Update subscription
                stripe.Subscription.modify(
                    subscription.id,
                    items=[
                        {
                            "id": subscription["items"]["data"][0].id,
                            "price": price_id,
                        }
                    ],
                )

                logger.info(
                    f"Updated subscription for customer {customer_id} to plan {plan}"
                )
            else:
                logger.warning(
                    f"No active subscription found for customer {customer_id}"
                )

        except stripe.error.StripeError as e:
            logger.error(f"Failed to update customer plan: {e}")
            raise

    async def create_usage_record(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[datetime] = None,
    ):
        """Create a usage record for metered billing"""
        try:
            usage_record = stripe.UsageRecord.create(
                subscription_item=subscription_item_id,
                quantity=quantity,
                timestamp=int(timestamp.timestamp()) if timestamp else None,
            )

            logger.info(
                f"Created usage record: {quantity} units for item {subscription_item_id}"
            )
            return usage_record

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create usage record: {e}")
            raise

    def verify_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """Verify and parse Stripe webhook"""
        try:
            if not self.webhook_secret:
                raise ValueError("Webhook secret not configured")

            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )

            return event

        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"Webhook verification failed: {e}")
            raise

    async def get_customer_by_org(self, org_id: str) -> Optional[Dict]:
        """Get Stripe customer by organization ID"""
        try:
            customers = stripe.Customer.list(
                limit=1, expand=["data.subscriptions"], metadata={"org_id": org_id}
            )

            if customers.data:
                return customers.data[0]

            return None

        except stripe.error.StripeError as e:
            logger.error(f"Failed to get customer: {e}")
            return None

    async def health_check(self) -> bool:
        """Check Stripe API connectivity"""
        try:
            # Simple API call to test connection
            stripe.Plan.list(limit=1)
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Stripe health check failed: {e}")
            return False

    async def get_invoice_preview(self, customer_id: str) -> Dict:
        """Get preview of upcoming invoice"""
        try:
            invoice = stripe.Invoice.upcoming(customer=customer_id)

            return {
                "amount_due": invoice.amount_due,
                "currency": invoice.currency,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "lines": [
                    {
                        "description": line.description,
                        "amount": line.amount,
                        "quantity": line.quantity,
                    }
                    for line in invoice.lines.data
                ],
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to get invoice preview: {e}")
            raise
