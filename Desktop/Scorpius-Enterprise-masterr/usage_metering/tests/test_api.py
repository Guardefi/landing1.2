"""
Test API endpoints for usage metering service
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from ..models import FeatureUsage, OrganizationUsage, UsageRecord


class TestUsageAPI:
    """Test usage tracking API endpoints"""

    def test_track_usage_success(self, client, auth_headers, sample_usage_event):
        """Test successful usage tracking"""
        with patch("app.usage_tracker") as mock_tracker:
            # Mock the usage tracker
            mock_record = UsageRecord(
                org_id="test-org-123",
                feature="scans",
                quantity=5,
                timestamp=datetime.utcnow(),
                reset_date=datetime.utcnow(),
                metadata={},
            )
            mock_tracker.record_usage = AsyncMock(return_value=mock_record)

            mock_usage = OrganizationUsage(
                org_id="test-org-123",
                plan="free",
                features={
                    "scans": FeatureUsage(
                        current=5,
                        limit=10,
                        reset_date=datetime.utcnow(),
                        last_updated=datetime.utcnow(),
                    )
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            mock_tracker.get_organization_usage = AsyncMock(return_value=mock_usage)

            response = client.post(
                "/usage/track", json=sample_usage_event, headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["org_id"] == "test-org-123"
            assert data["feature"] == "scans"
            assert data["current_usage"] == 5
            assert data["remaining"] == 5

    def test_track_usage_org_mismatch(self, client, auth_headers):
        """Test usage tracking with org ID mismatch"""
        event = {"org_id": "different-org", "feature": "scans", "quantity": 1}

        response = client.post("/usage/track", json=event, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_track_usage_invalid_token(self, client, sample_usage_event):
        """Test usage tracking with invalid authentication"""
        response = client.post(
            "/usage/track",
            json=sample_usage_event,
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_usage_success(self, client, auth_headers):
        """Test successful usage retrieval"""
        with patch("app.usage_tracker") as mock_tracker:
            mock_usage = OrganizationUsage(
                org_id="test-org-123",
                plan="professional",
                features={
                    "scans": FeatureUsage(
                        current=50,
                        limit=1000,
                        reset_date=datetime.utcnow(),
                        last_updated=datetime.utcnow(),
                    ),
                    "wallet_checks": FeatureUsage(
                        current=500,
                        limit=10000,
                        reset_date=datetime.utcnow(),
                        last_updated=datetime.utcnow(),
                    ),
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            mock_tracker.get_organization_usage = AsyncMock(return_value=mock_usage)

            response = client.get("/usage/test-org-123", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["org_id"] == "test-org-123"
            assert data["plan"] == "professional"
            assert "scans" in data["features"]

    def test_get_usage_not_found(self, client, auth_headers):
        """Test usage retrieval for non-existent organization"""
        with patch("app.usage_tracker") as mock_tracker:
            mock_tracker.get_organization_usage = AsyncMock(return_value=None)

            response = client.get("/usage/test-org-123", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_billing_success(self, client, auth_headers, sample_billing_update):
        """Test successful billing update"""
        with patch("app.usage_tracker") as mock_tracker:
            mock_tracker.update_organization_limits = AsyncMock()

            response = client.post(
                "/billing/update", json=sample_billing_update, headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "success"

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        with patch("app.metrics_exporter") as mock_exporter:
            mock_exporter.generate_usage_metrics = AsyncMock(
                return_value="# Test metrics\ntest_metric 1.0\n"
            )

            with patch("prometheus_client.generate_latest") as mock_prometheus:
                mock_prometheus.return_value = b"# Prometheus metrics\n"

                response = client.get("/metrics/usage")

                assert response.status_code == status.HTTP_200_OK
                assert "test_metric" in response.text

    def test_health_check(self, client):
        """Test health check endpoint"""
        with patch("app.redis_client") as mock_redis, patch(
            "app.stripe_service"
        ) as mock_stripe:
            mock_redis.ping = AsyncMock()
            mock_stripe.health_check = AsyncMock(return_value=True)

            response = client.get("/health")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["services"]["redis"] == "healthy"
            assert data["services"]["stripe"] == "healthy"


class TestWebhookAPI:
    """Test Stripe webhook handling"""

    def test_subscription_updated_webhook(self, client):
        """Test subscription updated webhook"""
        webhook_payload = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "customer": "cus_test123",
                    "items": {"data": [{"price": {"nickname": "professional"}}]},
                }
            },
        }

        with patch("app.stripe_service") as mock_stripe, patch(
            "app.usage_tracker"
        ) as mock_tracker:
            mock_stripe.verify_webhook = AsyncMock(return_value=webhook_payload)
            mock_tracker.get_org_by_customer_id = AsyncMock(return_value="test-org-123")
            mock_tracker.update_organization_limits = AsyncMock()

            response = client.post(
                "/webhooks/stripe",
                json=webhook_payload,
                headers={"stripe-signature": "test-signature"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "success"
