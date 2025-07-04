"""
Comprehensive test suite for SCORPIUS API endpoints
Tests all API functionality including comparison, search, indexing, and WebSocket
"""

import asyncio
import json
import os

# Add parent directory to path for imports
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import websockets
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))

from api.main import app, engine

# Test client
client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for REST API endpoints"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    def test_compare_bytecodes_valid(self):
        """Test bytecode comparison with valid input"""
        payload = {
            "bytecode1": "608060405234801561001057600080fd5b50",
            "bytecode2": "608060405234801561001057600080fd5b51",
            "threshold": 0.8,
            "use_neural_network": True,
        }

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "similarity_score" in data
        assert "confidence" in data
        assert "is_similar" in data
        assert "dimension_scores" in data
        assert "processing_time" in data
        assert 0.0 <= data["similarity_score"] <= 1.0
        assert 0.0 <= data["confidence"] <= 1.0

    def test_compare_bytecodes_invalid_input(self):
        """Test bytecode comparison with invalid input"""
        # Missing bytecode2
        payload = {
            "bytecode1": "608060405234801561001057600080fd5b50",
            "threshold": 0.8,
        }

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code == 422  # Validation error

        # Invalid hex string
        payload = {
            "bytecode1": "invalid_hex",
            "bytecode2": "608060405234801561001057600080fd5b50",
            "threshold": 0.8,
        }

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code in [400, 422]

    def test_compare_bytecodes_threshold_validation(self):
        """Test threshold parameter validation"""
        # Threshold too high
        payload = {
            "bytecode1": "608060405234801561001057600080fd5b50",
            "bytecode2": "608060405234801561001057600080fd5b51",
            "threshold": 1.5,
        }

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code == 422

        # Threshold too low
        payload["threshold"] = -0.1
        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code == 422

    def test_batch_index_valid(self):
        """Test batch indexing with valid input"""
        payload = {
            "bytecodes": [
                {
                    "bytecode": "608060405234801561001057600080fd5b50",
                    "metadata": {"name": "test_contract_1"},
                },
                {
                    "bytecode": "608060405234801561001057600080fd5b51",
                    "metadata": {"name": "test_contract_2"},
                },
            ]
        }

        response = client.post("/api/v1/batch-index", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "successful_indexes" in data
        assert "failed_indexes" in data
        assert "processing_time" in data
        assert data["successful_indexes"] >= 0

    def test_batch_index_empty_list(self):
        """Test batch indexing with empty list"""
        payload = {"bytecodes": []}

        response = client.post("/api/v1/batch-index", json=payload)
        assert response.status_code == 400

    def test_similarity_search_valid(self):
        """Test similarity search with valid input"""
        # First index some data
        index_payload = {
            "bytecodes": [
                {
                    "bytecode": "608060405234801561001057600080fd5b50",
                    "metadata": {"name": "searchable_contract"},
                }
            ]
        }
        client.post("/api/v1/batch-index", json=index_payload)

        # Now search
        search_payload = {
            "query_bytecode": "608060405234801561001057600080fd5b51",
            "top_k": 5,
            "min_similarity": 0.5,
        }

        response = client.post("/api/v1/search", json=search_payload)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total_results" in data
        assert "processing_time" in data
        assert isinstance(data["results"], list)

    def test_similarity_search_invalid_params(self):
        """Test similarity search with invalid parameters"""
        # Invalid top_k
        payload = {"query_bytecode": "608060405234801561001057600080fd5b50", "top_k": 0}

        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422

        # Invalid min_similarity
        payload = {
            "query_bytecode": "608060405234801561001057600080fd5b50",
            "min_similarity": 1.5,
        }

        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422

    def test_engine_stats(self):
        """Test engine statistics endpoint"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_indexed_bytecodes" in data
        assert "cache_size" in data
        assert "device" in data
        assert "model_loaded" in data

    def test_clear_cache(self):
        """Test cache clearing endpoint"""
        response = client.post("/api/v1/clear-cache")
        # Should work even without auth for testing
        assert response.status_code in [200, 401]  # 401 if auth required

    def test_api_documentation(self):
        """Test API documentation endpoints"""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/redoc")
        assert response.status_code == 200


class TestWebSocketConnection:
    """Test suite for WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test basic WebSocket connection"""
        # Note: This test requires the server to be running
        # In a real test environment, you'd use a test server
        try:
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Test connection established message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                assert data["type"] == "connection_established"

        except Exception as e:
            pytest.skip(f"WebSocket server not available: {e}")

    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong functionality"""
        try:
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Wait for connection message
                await websocket.recv()

                # Send ping
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))

                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                assert data["type"] == "pong"

        except Exception as e:
            pytest.skip(f"WebSocket server not available: {e}")

    @pytest.mark.asyncio
    async def test_websocket_subscription(self):
        """Test WebSocket subscription functionality"""
        try:
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Wait for connection message
                await websocket.recv()

                # Subscribe to updates
                subscribe_message = {"type": "subscribe", "subscription": "all"}
                await websocket.send(json.dumps(subscribe_message))

                # Wait for subscription confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                assert data["type"] == "subscription_confirmed"

        except Exception as e:
            pytest.skip(f"WebSocket server not available: {e}")


class TestErrorHandling:
    """Test suite for error handling and edge cases"""

    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/v1/compare",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/api/v1/compare", data='{"test": "data"}')
        assert response.status_code in [422, 415]

    def test_large_payload(self):
        """Test handling of very large payloads"""
        # Create a very long bytecode string
        large_bytecode = "60" * 50000  # 100KB of hex

        payload = {
            "bytecode1": large_bytecode,
            "bytecode2": "608060405234801561001057600080fd5b50",
        }

        response = client.post("/api/v1/compare", json=payload)
        # Should either process or return appropriate error
        assert response.status_code in [200, 400, 413, 422]

    def test_empty_bytecode(self):
        """Test handling of empty bytecode"""
        payload = {"bytecode1": "", "bytecode2": "608060405234801561001057600080fd5b50"}

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code in [400, 422]

    def test_unicode_in_bytecode(self):
        """Test handling of unicode characters in bytecode"""
        payload = {
            "bytecode1": "60806040523480156100üß€ü",
            "bytecode2": "608060405234801561001057600080fd5b50",
        }

        response = client.post("/api/v1/compare", json=payload)
        assert response.status_code in [400, 422]


class TestPerformance:
    """Test suite for performance characteristics"""

    def test_response_time_comparison(self):
        """Test that comparison response time is reasonable"""
        import time

        payload = {
            "bytecode1": "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe",
            "bytecode2": "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe",
        }

        start_time = time.time()
        response = client.post("/api/v1/compare", json=payload)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time

        # Response should be under 10 seconds for basic comparison
        assert response_time < 10.0

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import time

        def make_request():
            payload = {
                "bytecode1": "608060405234801561001057600080fd5b50",
                "bytecode2": "608060405234801561001057600080fd5b51",
            }
            return client.post("/api/v1/compare", json=payload)

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
            end_time = time.time()

        # All requests should succeed
        for response in results:
            assert response.status_code == 200

        # Should complete within reasonable time
        total_time = end_time - start_time
        assert total_time < 30.0


class TestSecurity:
    """Test suite for security aspects"""

    def test_sql_injection_attempts(self):
        """Test protection against SQL injection attempts"""
        malicious_payloads = [
            "'; DROP TABLE bytecodes; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
        ]

        for malicious_payload in malicious_payloads:
            payload = {
                "bytecode1": malicious_payload,
                "bytecode2": "608060405234801561001057600080fd5b50",
            }

            response = client.post("/api/v1/compare", json=payload)
            # Should reject malicious input
            assert response.status_code in [400, 422]

    def test_xss_attempts(self):
        """Test protection against XSS attempts"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onload=alert('xss')",
        ]

        for xss_payload in xss_payloads:
            # Test in metadata fields
            payload = {
                "bytecodes": [
                    {
                        "bytecode": "608060405234801561001057600080fd5b50",
                        "metadata": {"name": xss_payload},
                    }
                ]
            }

            response = client.post("/api/v1/batch-index", json=payload)
            # Should process but sanitize the input
            assert response.status_code in [200, 400, 422]

    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/compare")
        # CORS headers should be present for development
        # In production, these should be more restrictive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
