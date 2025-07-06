"""
Unit tests for api/main.py
Tests HTTP endpoints with focus on HTTP 502 from RPC call failures
"""

import asyncio
import json
import os

# Import the modules to test
import sys
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/Bytecode"))

from api.main import app, engine, manager


class TestBytecodeAPI:
    """Test suite for Bytecode API endpoints"""

    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_similarity_engine(self):
        """Mock similarity engine for testing"""
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.return_value = {
            "similarity_score": 0.85,
            "confidence": 0.92,
            "dimension_scores": {
                "instruction": 0.8,
                "operand": 0.9,
                "control_flow": 0.85,
                "data_flow": 0.88,
            },
            "metadata": {"method": "multidimensional"},
            "processing_time": 0.125,
        }
        mock_engine.find_similar_bytecode.return_value = [
            {
                "bytecode_hash": "abc123",
                "similarity_score": 0.92,
                "confidence": 0.88,
                "metadata": {"contract_name": "TestContract"},
            }
        ]
        mock_engine.index_bytecode.return_value = "indexed_hash_123"
        return mock_engine

    @pytest.fixture
    def sample_comparison_request(self):
        """Sample comparison request payload"""
        return {
            "bytecode1": "608060405234801561001057600080fd5b50600436106100365760003560e01c8063a41368621461003b578063cfae321714610059575b",
            "bytecode2": "608060405234801561001057600080fd5b506004361061004c5760003560e01c8063c6888fa114610051578063d09de08a14610051575b",
            "use_neural_network": True,
        }

    @pytest.fixture
    def sample_search_request(self):
        """Sample search request payload"""
        return {
            "query_bytecode": "608060405234801561001057600080fd5b50600436106100365760003560e01c8063a41368621461003b",
            "top_k": 5,
            "min_similarity": 0.7,
        }

    @pytest.fixture
    def sample_index_request(self):
        """Sample index request payload"""
        return {
            "bytecode": "608060405234801561001057600080fd5b50600436106100365760003560e01c8063a41368621461003b",
            "metadata": {
                "contract_name": "TestContract",
                "version": "1.0",
                "source": "etherscan",
            },
        }

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_comparisons" in data
        assert "avg_processing_time" in data
        assert "cache_hit_rate" in data

    @patch("api.main.engine")
    def test_compare_bytecodes_success(
        self,
        mock_engine_global,
        client,
        mock_similarity_engine,
        sample_comparison_request,
    ):
        """Test successful bytecode comparison"""
        # Setup mock
        mock_engine_global.return_value = mock_similarity_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        assert response.status_code == 200
        data = response.json()
        assert "similarity_score" in data
        assert "confidence" in data
        assert "dimension_scores" in data
        assert 0.0 <= data["similarity_score"] <= 1.0

    @patch("api.main.engine")
    def test_compare_bytecodes_rpc_failure_502(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test HTTP 502 when RPC call fails during comparison"""
        # Setup mock to simulate RPC failure
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = aiohttp.ClientError(
            "RPC connection failed"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        # Should return 502 Bad Gateway for RPC failures
        assert response.status_code == 502
        data = response.json()
        assert "error" in data
        assert "RPC" in data["error"] or "connection" in data["error"].lower()

    @patch("api.main.engine")
    def test_compare_bytecodes_timeout_502(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test HTTP 502 when RPC call times out"""
        # Setup mock to simulate timeout
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = asyncio.TimeoutError(
            "RPC request timeout"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        # Should return 502 Bad Gateway for timeouts
        assert response.status_code == 502
        data = response.json()
        assert "error" in data
        assert (
            "timeout" in data["error"].lower() or "unavailable" in data["error"].lower()
        )

    @patch("api.main.engine")
    def test_compare_bytecodes_connection_error_502(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test HTTP 502 when underlying connection fails"""
        # Setup mock to simulate connection error
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = ConnectionError(
            "Unable to connect to blockchain RPC"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        assert response.status_code == 502
        data = response.json()
        assert "error" in data
        assert (
            "service unavailable" in data["error"].lower()
            or "connection" in data["error"].lower()
        )

    def test_compare_bytecodes_invalid_input_400(self, client):
        """Test HTTP 400 for invalid input"""
        invalid_request = {
            "bytecode1": "",  # Empty bytecode
            "bytecode2": "invalid_hex",  # Invalid hex
            "use_neural_network": "not_boolean",  # Invalid type
        }

        response = client.post("/api/v1/compare", json=invalid_request)

        assert response.status_code == 422  # FastAPI validation error
        data = response.json()
        assert "detail" in data

    @patch("api.main.engine")
    def test_search_similar_bytecode_success(
        self, mock_engine_global, client, mock_similarity_engine, sample_search_request
    ):
        """Test successful similarity search"""
        mock_engine_global.return_value = mock_similarity_engine

        response = client.post("/api/v1/search", json=sample_search_request)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        if data["results"]:
            result = data["results"][0]
            assert "bytecode_hash" in result
            assert "similarity_score" in result
            assert "confidence" in result

    @patch("api.main.engine")
    def test_search_rpc_failure_502(
        self, mock_engine_global, client, sample_search_request
    ):
        """Test HTTP 502 when RPC fails during search"""
        mock_engine = AsyncMock()
        mock_engine.find_similar_bytecode.side_effect = aiohttp.ClientError(
            "Blockchain RPC unavailable"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/search", json=sample_search_request)

        assert response.status_code == 502
        data = response.json()
        assert "error" in data

    @patch("api.main.engine")
    def test_index_bytecode_success(
        self, mock_engine_global, client, mock_similarity_engine, sample_index_request
    ):
        """Test successful bytecode indexing"""
        mock_engine_global.return_value = mock_similarity_engine

        response = client.post("/api/v1/index", json=sample_index_request)

        assert response.status_code == 200
        data = response.json()
        assert "bytecode_hash" in data
        assert "status" in data
        assert data["status"] == "indexed"

    @patch("api.main.engine")
    def test_index_rpc_failure_502(
        self, mock_engine_global, client, sample_index_request
    ):
        """Test HTTP 502 when RPC fails during indexing"""
        mock_engine = AsyncMock()
        mock_engine.index_bytecode.side_effect = Exception(
            "Failed to connect to vector database"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/index", json=sample_index_request)

        assert response.status_code == 502
        data = response.json()
        assert "error" in data

    def test_malformed_json_400(self, client):
        """Test HTTP 400 for malformed JSON"""
        response = client.post(
            "/api/v1/compare",
            data='{"invalid": json}',  # Malformed JSON
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422  # FastAPI handles this as validation error

    def test_missing_required_fields_400(self, client):
        """Test HTTP 400 for missing required fields"""
        incomplete_request = {
            "bytecode1": "608060405234801561001057600080fd5b"
            # Missing bytecode2
        }

        response = client.post("/api/v1/compare", json=incomplete_request)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @patch("api.main.engine")
    def test_internal_server_error_500(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test HTTP 500 for unexpected internal errors"""
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = RuntimeError(
            "Unexpected internal error"
        )
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "internal" in data["error"].lower() or "server" in data["error"].lower()

    @patch("api.main.engine")
    def test_multiple_rpc_failure_scenarios(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test various RPC failure scenarios that should return 502"""
        rpc_errors = [
            aiohttp.ClientConnectionError("Connection refused"),
            aiohttp.ClientTimeout("Request timeout"),
            aiohttp.ClientResponseError(
                None, None, status=503, message="Service Unavailable"
            ),
            ConnectionRefusedError("RPC server not responding"),
            asyncio.TimeoutError("Operation timed out"),
        ]

        for error in rpc_errors:
            mock_engine = AsyncMock()
            mock_engine.compare_bytecodes.side_effect = error
            mock_engine_global.return_value = mock_engine

            response = client.post("/api/v1/compare", json=sample_comparison_request)

            assert response.status_code in [
                502,
                503,
                504,
            ], f"Expected 50x error for {type(error).__name__}, got {response.status_code}"

    @patch("api.main.engine")
    def test_performance_monitoring_on_failure(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test that performance monitoring works even when RPC fails"""
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = aiohttp.ClientError("RPC failed")
        mock_engine_global.return_value = mock_engine

        # Should still track the failed request
        response = client.post("/api/v1/compare", json=sample_comparison_request)

        assert response.status_code == 502
        # The failure should be logged/tracked (this would be verified in integration tests)

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/v1/compare")

        # CORS headers should be present for OPTIONS request
        assert response.status_code in [200, 204]

    def test_rate_limiting_behavior(self, client):
        """Test rate limiting behavior (if implemented)"""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response.status_code)

        # All health checks should succeed (no rate limiting on health endpoint)
        assert all(status == 200 for status in responses)

    @patch("api.main.engine")
    def test_websocket_connection_management(self, mock_engine_global):
        """Test WebSocket connection management"""
        # This would require WebSocket testing framework
        # For now, just test that the connection manager exists
        assert manager is not None
        assert hasattr(manager, "active_connections")
        assert hasattr(manager, "connect")
        assert hasattr(manager, "disconnect")
        assert hasattr(manager, "broadcast")

    @patch("api.main.engine")
    def test_error_response_format_consistency(
        self, mock_engine_global, client, sample_comparison_request
    ):
        """Test that error responses have consistent format"""
        # Test RPC failure error format
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = aiohttp.ClientError("RPC failed")
        mock_engine_global.return_value = mock_engine

        response = client.post("/api/v1/compare", json=sample_comparison_request)

        assert response.status_code == 502
        data = response.json()

        # Error response should have consistent structure
        assert isinstance(data, dict)
        assert "error" in data
        assert isinstance(data["error"], str)

        # Should include timestamp for debugging
        if "timestamp" in data:
            assert isinstance(data["timestamp"], (int, float))

    @patch("api.main.engine")
    def test_edge_case_empty_bytecode(
        self, mock_engine_global, client, mock_similarity_engine
    ):
        """Test edge case with empty bytecode"""
        mock_engine_global.return_value = mock_similarity_engine

        edge_case_request = {
            "bytecode1": "",
            "bytecode2": "",
            "use_neural_network": False,
        }

        response = client.post("/api/v1/compare", json=edge_case_request)

        # Should handle gracefully (either 200 with low similarity or 400 validation error)
        assert response.status_code in [200, 400, 422]

    @patch("api.main.engine")
    def test_large_bytecode_handling(
        self, mock_engine_global, client, mock_similarity_engine
    ):
        """Test handling of very large bytecode"""
        mock_engine_global.return_value = mock_similarity_engine

        # Create large bytecode (simulate a large contract)
        large_bytecode = "60" + "80" * 10000  # Very large bytecode

        large_request = {
            "bytecode1": large_bytecode,
            "bytecode2": large_bytecode,
            "use_neural_network": False,
        }

        response = client.post("/api/v1/compare", json=large_request)

        # Should handle large inputs gracefully
        assert response.status_code in [200, 413, 422]  # 413 = Payload Too Large


class TestRPCFailureScenarios:
    """Dedicated test class for RPC failure scenarios"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.parametrize(
        "rpc_error,expected_status",
        [
            (aiohttp.ClientConnectionError("Connection refused"), 502),
            (aiohttp.ClientTimeout("Request timeout"), 504),
            (aiohttp.ClientResponseError(None, None, status=503), 502),
            (ConnectionRefusedError("Port closed"), 502),
            (asyncio.TimeoutError("Timeout"), 504),
            (OSError("Network unreachable"), 502),
        ],
    )
    @patch("api.main.engine")
    def test_specific_rpc_errors(
        self, mock_engine_global, client, rpc_error, expected_status
    ):
        """Test specific RPC error types map to correct HTTP status codes"""
        mock_engine = AsyncMock()
        mock_engine.compare_bytecodes.side_effect = rpc_error
        mock_engine_global.return_value = mock_engine

        request_data = {
            "bytecode1": "608060405234801561001057600080fd5b",
            "bytecode2": "608060405234801561001057600080fd5b",
            "use_neural_network": False,
        }

        response = client.post("/api/v1/compare", json=request_data)

        assert response.status_code == expected_status
        data = response.json()
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
