"""
Test Stripe integration service
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import stripe


class TestStripeService:
    """Test Stripe integration functionality"""

    @patch("stripe.Customer.create")
    def test_create_customer(self, mock_create, mock_stripe):
        """Test creating Stripe customer"""
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        mock_create.return_value = mock_customer

        # Test the method (would be async in real implementation)
        result = mock_stripe.create_customer("test-org", "test@example.com", "Test Org")

        # Verify result
        assert result == "cus_test123"

    @patch("stripe.Subscription.create")
    def test_create_subscription(self, mock_create, mock_stripe):
        """Test creating Stripe subscription"""
        mock_subscription = Mock()
        mock_subscription.id = "sub_test123"
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1234567890
        mock_create.return_value = mock_subscription

        result = mock_stripe.create_subscription("cus_test123", "price_test")

        expected = {
            "subscription_id": "sub_test123",
            "status": "active",
            "current_period_end": 1234567890,
        }
        assert result == expected

    @patch("stripe.Subscription.list")
    @patch("stripe.Subscription.modify")
    def test_update_customer_plan(self, mock_modify, mock_list, mock_stripe):
        """Test updating customer plan"""
        # Mock existing subscription
        mock_subscription = Mock()
        mock_subscription.id = "sub_test123"
        mock_subscription.__getitem__ = Mock(
            return_value={"data": [{"id": "si_test123"}]}
        )

        mock_list_result = Mock()
        mock_list_result.data = [mock_subscription]
        mock_list.return_value = mock_list_result

        # Should not raise exception
        mock_stripe.update_customer_plan("cus_test123", "professional")

    @patch("stripe.UsageRecord.create")
    def test_create_usage_record(self, mock_create, mock_stripe):
        """Test creating usage records"""
        mock_record = Mock()
        mock_record.id = "usage_test123"
        mock_create.return_value = mock_record

        result = mock_stripe.create_usage_record("si_test123", 100)
        assert result == mock_record

    def test_verify_webhook(self, mock_stripe):
        """Test webhook verification"""
        test_event = {
            "type": "customer.subscription.updated",
            "data": {"object": {"id": "sub_test123"}},
        }

        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.return_value = test_event

            result = mock_stripe.verify_webhook(b"payload", "sig_header")
            assert result == test_event

    @patch("stripe.Customer.list")
    def test_get_customer_by_org(self, mock_list, mock_stripe):
        """Test finding customer by organization ID"""
        mock_customer = Mock()
        mock_customer.id = "cus_test123"

        mock_list_result = Mock()
        mock_list_result.data = [mock_customer]
        mock_list.return_value = mock_list_result

        result = mock_stripe.get_customer_by_org("test-org")
        assert result == mock_customer

    @patch("stripe.Plan.list")
    def test_health_check(self, mock_list, mock_stripe):
        """Test Stripe health check"""
        mock_list.return_value = Mock()

        result = mock_stripe.health_check()
        assert result == True

    @patch("stripe.Invoice.upcoming")
    def test_get_invoice_preview(self, mock_upcoming, mock_stripe):
        """Test invoice preview"""
        mock_line = Mock()
        mock_line.description = "Test item"
        mock_line.amount = 1000
        mock_line.quantity = 1

        mock_lines = Mock()
        mock_lines.data = [mock_line]

        mock_invoice = Mock()
        mock_invoice.amount_due = 1000
        mock_invoice.currency = "usd"
        mock_invoice.period_start = 1234567890
        mock_invoice.period_end = 1234567900
        mock_invoice.lines = mock_lines

        mock_upcoming.return_value = mock_invoice

        result = mock_stripe.get_invoice_preview("cus_test123")

        assert result["amount_due"] == 1000
        assert result["currency"] == "usd"
        assert len(result["lines"]) == 1
        assert result["lines"][0]["description"] == "Test item"

    def test_webhook_signature_verification_error(self, mock_stripe):
        """Test webhook signature verification failure"""
        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.side_effect = stripe.error.SignatureVerificationError(
                "Invalid signature", "sig_header"
            )

            with pytest.raises(stripe.error.SignatureVerificationError):
                mock_stripe.verify_webhook(b"payload", "invalid_sig")

    @patch("stripe.Customer.create")
    def test_create_customer_stripe_error(self, mock_create, mock_stripe):
        """Test handling Stripe errors"""
        mock_create.side_effect = stripe.error.StripeError("Test error")

        with pytest.raises(stripe.error.StripeError):
            mock_stripe.create_customer("test-org", "test@example.com", "Test Org")
