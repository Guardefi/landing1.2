"""
Pact Contract Tests for Scorpius Frontend ↔ Backend Integration
Ensures API contracts between React frontend and FastAPI backend
"""

import pytest
import requests
import json
from typing import Dict, Any

# Mock Pact implementation for contract testing
class MockPact:
    """Simple contract testing framework for API validation."""
    
    def __init__(self, consumer: str, provider: str):
        self.consumer = consumer
        self.provider = provider
        self.interactions = []
        
    def given(self, state: str):
        self.current_state = state
        return self
        
    def upon_receiving(self, description: str):
        self.current_description = description
        return self
        
    def with_request(self, method: str, path: str, headers: Dict = None, body: Dict = None):
        self.current_request = {
            "method": method,
            "path": path,
            "headers": headers or {},
            "body": body
        }
        return self
        
    def will_respond_with(self, status: int, headers: Dict = None, body: Dict = None):
        self.current_response = {
            "status": status,
            "headers": headers or {},
            "body": body
        }
        return self
        
    def verify_contract(self, base_url: str) -> bool:
        """Verify the contract against the actual API."""
        try:
            response = requests.request(
                method=self.current_request["method"],
                url=f"{base_url}{self.current_request['path']}",
                headers=self.current_request["headers"],
                json=self.current_request["body"],
                timeout=10
            )
            
            # Check status code
            if response.status_code != self.current_response["status"]:
                print(f"❌ Status mismatch: expected {self.current_response['status']}, got {response.status_code}")
                return False
                
            # Check response structure if body is expected
            if self.current_response["body"]:
                try:
                    response_data = response.json()
                    expected_keys = set(self.current_response["body"].keys())
                    actual_keys = set(response_data.keys())
                    
                    if not expected_keys.issubset(actual_keys):
                        missing_keys = expected_keys - actual_keys
                        print(f"❌ Missing keys in response: {missing_keys}")
                        return False
                        
                except Exception as e:
                    print(f"❌ JSON parsing error: {e}")
                    return False
            
            print(f"✅ Contract verified: {self.current_description}")
            return True
            
        except Exception as e:
            print(f"❌ Contract verification failed: {e}")
            return False

# Initialize Pact
pact = MockPact('scorpius-frontend', 'scorpius-backend')
BASE_URL = "http://localhost:8000"

class TestAPIContracts:
    """Test API contracts between frontend and backend."""
    
    def test_health_check_contract(self):
        """Test health check endpoint contract."""
        contract_valid = (pact
                         .given("API is healthy")
                         .upon_receiving("a health check request")
                         .with_request("GET", "/health")
                         .will_respond_with(200, body={"status": "ok"})
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "Health check contract failed"
    
    def test_openapi_schema_contract(self):
        """Test OpenAPI schema endpoint contract."""
        contract_valid = (pact
                         .given("API schema is available")
                         .upon_receiving("a request for OpenAPI schema")
                         .with_request("GET", "/openapi.json")
                         .will_respond_with(200, body={"openapi": "3.0.0", "info": {}, "paths": {}})
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "OpenAPI schema contract failed"
    
    def test_bridge_stats_contract(self):
        """Test bridge statistics endpoint contract."""
        contract_valid = (pact
                         .given("Bridge service is running")
                         .upon_receiving("a request for bridge stats")
                         .with_request("GET", "/api/v2/stats")
                         .will_respond_with(200, body={
                             "total_transfers": 0,
                             "total_volume": "0",
                             "active_validators": 0,
                             "total_liquidity": "0"
                         })
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "Bridge stats contract failed"
    
    def test_bridge_fees_contract(self):
        """Test bridge fee estimation contract."""
        contract_valid = (pact
                         .given("Bridge service can estimate fees")
                         .upon_receiving("a request for fee estimation")
                         .with_request("GET", "/api/v2/bridge/fees?source_chain=ethereum&destination_chain=polygon&amount=100")
                         .will_respond_with(200, body={
                             "bridge_fee": "0.003",
                             "gas_fee": "0.001", 
                             "total_fee": "0.004"
                         })
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "Bridge fees contract failed"
    
    def test_validators_list_contract(self):
        """Test validators list endpoint contract."""
        contract_valid = (pact
                         .given("Validator service is running")
                         .upon_receiving("a request for validators list")
                         .with_request("GET", "/api/v2/validators")
                         .will_respond_with(200, body=[])
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "Validators list contract failed"
    
    def test_liquidity_pools_contract(self):
        """Test liquidity pools endpoint contract."""
        contract_valid = (pact
                         .given("Liquidity service is running")
                         .upon_receiving("a request for liquidity pools")
                         .with_request("GET", "/api/v2/liquidity/pools")
                         .will_respond_with(200, body=[])
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "Liquidity pools contract failed"

    def test_websocket_stats_contract(self):
        """Test WebSocket statistics endpoint contract."""
        contract_valid = (pact
                         .given("WebSocket service is running")
                         .upon_receiving("a request for WebSocket stats")
                         .with_request("GET", "/api/ws/stats")
                         .will_respond_with(200, body={"active_connections": 0, "total_messages": 0})
                         .verify_contract(BASE_URL))
        
        assert contract_valid, "WebSocket stats contract failed"

if __name__ == "__main__":
    print("📄 Running API Contract Tests...")
    pytest.main([__file__, "-v"]) 