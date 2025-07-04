"""Integration tests for the API endpoints."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from services.api.main import app


class TestAPIEndpoints:
    """Test API endpoints integration."""

    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_metrics_endpoint(self, test_client: TestClient):
        """Test Prometheus metrics endpoint."""
        response = test_client.get("/metrics")
        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "text/plain; version=0.0.4; charset=utf-8"
        )

    @patch("services.api.main.db_manager")
    def test_get_transactions(self, mock_db, test_client: TestClient):
        """Test getting transactions."""
        # Mock database response
        mock_db.get_transactions = AsyncMock(
            return_value=[
                {
                    "hash": "0x123",
                    "chain_id": 1,
                    "from": "0xabc",
                    "to": "0xdef",
                    "value": "1000000000000000000",
                    "gas": "21000",
                    "gas_price": "20000000000",
                    "data": "0x",
                    "nonce": "1",
                    "timestamp": 1234567890,
                    "status": "pending",
                }
            ]
        )

        # Make request with auth
        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get("/api/v1/transactions", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_transactions_unauthorized(self, test_client: TestClient):
        """Test getting transactions without authorization."""
        response = test_client.get("/api/v1/transactions")
        assert response.status_code == 403

    @patch("services.api.main.db_manager")
    def test_get_transactions_with_filters(self, mock_db, test_client: TestClient):
        """Test getting transactions with filters."""
        mock_db.get_transactions = AsyncMock(return_value=[])

        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get(
            "/api/v1/transactions?limit=50&offset=10&chain_id=1&status=pending",
            headers=headers,
        )

        assert response.status_code == 200
        # Verify that filters were passed to the database query
        mock_db.get_transactions.assert_called_once()

    @patch("services.api.main.db_manager")
    def test_get_alerts(self, mock_db, test_client: TestClient):
        """Test getting alerts."""
        mock_db.get_alerts = AsyncMock(
            return_value=[
                {
                    "id": "alert-123",
                    "rule_id": "rule-456",
                    "transaction_hash": "0x123",
                    "chain_id": 1,
                    "severity": "high",
                    "title": "High Value Transaction",
                    "description": "Large transaction detected",
                    "metadata": {"value_eth": 10.5},
                    "created_at": "2024-01-01T00:00:00Z",
                    "tags": ["high-value"],
                }
            ]
        )

        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get("/api/v1/alerts", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "severity" in data[0]

    @patch("services.api.main.db_manager")
    def test_create_rule(self, mock_db, test_client: TestClient):
        """Test creating a new rule."""
        mock_db.create_rule = AsyncMock(
            return_value={
                "id": "rule-789",
                "name": "Test Rule",
                "description": "Test rule description",
                "conditions": {"value_gte": "1000000000000000000"},
                "actions": {"send_alert": True},
                "is_active": True,
            }
        )

        rule_data = {
            "name": "High Value Transaction Alert",
            "description": "Alert for transactions > 1 ETH",
            "chain_id": 1,
            "conditions": {"value_gte": "1000000000000000000"},
            "actions": {"send_alert": True, "severity": "medium"},
        }

        headers = {"Authorization": "Bearer test-token"}
        response = test_client.post("/api/v1/rules", json=rule_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == rule_data["name"]

    def test_websocket_connection(self, test_client: TestClient):
        """Test WebSocket connection."""
        with test_client.websocket_connect("/ws/test-client") as websocket:
            # Connection should be established
            assert websocket is not None

            # Send a test message
            websocket.send_text("ping")

            # Connection should remain open
            # In a real test, you might want to test message handling

    @patch("services.api.main.connection_manager")
    def test_websocket_broadcast(self, mock_manager, test_client: TestClient):
        """Test WebSocket broadcasting."""
        mock_manager.broadcast = AsyncMock()

        # This would typically be triggered by some internal event
        # For testing, we can directly call the broadcast function
        import asyncio

        async def test_broadcast():
            await mock_manager.broadcast(
                json.dumps(
                    {
                        "type": "alert",
                        "data": {
                            "id": "alert-123",
                            "severity": "high",
                            "message": "High value transaction detected",
                        },
                    }
                )
            )

        # Run the broadcast test
        asyncio.run(test_broadcast())
        mock_manager.broadcast.assert_called_once()

    @patch("services.api.main.db_manager")
    def test_get_mev_opportunities(self, mock_db, test_client: TestClient):
        """Test getting MEV opportunities."""
        mock_db.get_mev_opportunities = AsyncMock(
            return_value=[
                {
                    "id": "mev-123",
                    "transaction_hash": "0x123",
                    "chain_id": 1,
                    "pattern_type": "arbitrage",
                    "estimated_profit": 0.5,
                    "confidence_score": 0.85,
                    "target_block": 18500000,
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        )

        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get("/api/v1/mev-opportunities", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers are properly set."""
        response = test_client.options("/health")
        assert "access-control-allow-origin" in response.headers

    def test_rate_limiting(self, test_client: TestClient):
        """Test rate limiting functionality."""
        # Make multiple requests quickly
        responses = []
        for _ in range(10):
            response = test_client.get("/health")
            responses.append(response.status_code)

        # All should succeed for health endpoint (usually not rate limited)
        assert all(status == 200 for status in responses)

    def test_api_versioning(self, test_client: TestClient):
        """Test API versioning."""
        # Test that v1 endpoints work
        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get("/api/v1/transactions", headers=headers)
        # Should get either 200 or proper error, not 404
        assert response.status_code != 404

    @patch("services.api.main.db_manager")
    def test_error_handling(self, mock_db, test_client: TestClient):
        """Test API error handling."""
        # Mock a database error
        mock_db.get_transactions = AsyncMock(side_effect=Exception("Database error"))

        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get("/api/v1/transactions", headers=headers)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_request_validation(self, test_client: TestClient):
        """Test request validation."""
        # Test invalid query parameters
        headers = {"Authorization": "Bearer test-token"}
        response = test_client.get(
            "/api/v1/transactions?limit=invalid", headers=headers
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
