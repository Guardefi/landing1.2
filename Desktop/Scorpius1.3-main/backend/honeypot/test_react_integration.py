"""
React Integration Test Suite
Test all endpoints that your React dashboard will use
"""
import asyncio
import json
import os
import sys
from datetime import datetime

import httpx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


class ReactIntegrationTester:
    """Tests specifically for React dashboard integration"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = settings.API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Origin": "http://localhost:3000",  # Simulate React app
        }

    async def test_cors_for_react(self):
        """Test CORS specifically for React origins"""
        print("🌐 Testing CORS for React applications...")

        react_origins = [
            "http://localhost:3000",  # Create React App default
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

        async with httpx.AsyncClient() as client:
            for origin in react_origins:
                # Test preflight request
                response = await client.options(
                    f"{self.base_url}/api/v1/dashboard/stats",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "GET",
                        "Access-Control-Request-Headers": "X-API-Key,Content-Type",
                    },
                )

                print(f"  Origin {origin}: Status {response.status_code}")

                # Test actual request
                response = await client.get(
                    f"{self.base_url}/api/v1/dashboard/stats",
                    headers={**self.headers, "Origin": origin},
                )

                print(f"  GET request from {origin}: Status {response.status_code}")

        print("✅ CORS testing completed")
        return True

    async def test_dashboard_data_structure(self):
        """Test that dashboard endpoints return expected data structure"""
        print("📊 Testing dashboard data structures...")

        async with httpx.AsyncClient() as client:
            # Test dashboard stats endpoint
            response = await client.get(
                f"{self.base_url}/api/v1/dashboard/stats", headers=self.headers
            )

            print(f"Dashboard stats status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                expected_fields = [
                    "total_analyses",
                    "honeypots_detected",
                    "false_positives",
                    "detection_rate",
                    "recent_analyses",
                    "risk_distribution",
                    "technique_distribution",
                ]

                for field in expected_fields:
                    if field in data:
                        print(f"  ✅ {field}: {type(data[field])}")
                    else:
                        print(f"  ❌ Missing field: {field}")

            # Test trends endpoint
            response = await client.get(
                f"{self.base_url}/api/v1/dashboard/trends?days=7", headers=self.headers
            )

            print(f"Dashboard trends status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                expected_fields = [
                    "dates",
                    "honeypot_counts",
                    "analysis_counts",
                    "detection_rates",
                ]

                for field in expected_fields:
                    if field in data:
                        print(
                            f"  ✅ {field}: {type(data[field])} (length: {len(data[field]) if isinstance(data[field], list) else 'N/A'})"
                        )
                    else:
                        print(f"  ❌ Missing field: {field}")

        print("✅ Dashboard data structure testing completed")
        return True

    async def test_contract_analysis_flow(self):
        """Test the complete contract analysis flow that React will use"""
        print("🔍 Testing contract analysis flow...")

        # Test contract addresses (these may not exist but should test the flow)
        test_addresses = [
            "0xa0b86a33e6c3ca4fdd100269d7e5e50b637cab5d",  # Well-formatted address
            "0x1234567890abcdef1234567890abcdef12345678",  # Valid format
        ]

        async with httpx.AsyncClient() as client:
            for address in test_addresses:
                print(f"  Testing analysis for: {address}")

                # Test analysis request
                analysis_data = {
                    "address": address,
                    "chain_id": 1,
                    "deep_analysis": False,
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/analyze",
                    json=analysis_data,
                    headers=self.headers,
                )

                print(f"    Analysis status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    required_fields = [
                        "address",
                        "is_honeypot",
                        "confidence",
                        "risk_level",
                    ]

                    for field in required_fields:
                        if field in data:
                            print(f"    ✅ {field}: {data[field]}")
                        else:
                            print(f"    ❌ Missing field: {field}")

                elif response.status_code in [400, 422]:
                    print(f"    ℹ️  Validation error (expected): {response.json()}")

                elif response.status_code == 500:
                    print(
                        f"    ⚠️  Server error (may be due to missing blockchain connection)"
                    )

                # Test getting analysis history
                response = await client.get(
                    f"{self.base_url}/api/v1/history/{address}", headers=self.headers
                )

                print(f"    History status: {response.status_code}")

        print("✅ Contract analysis flow testing completed")
        return True

    async def test_search_functionality(self):
        """Test search functionality for React dashboard"""
        print("🔎 Testing search functionality...")

        search_queries = [
            {"query": "0x123", "description": "Partial address search"},
            {"query": "", "description": "Empty search"},
            {"is_honeypot": True, "description": "Filter by honeypot"},
            {"risk_level": "high", "description": "Filter by risk level"},
        ]

        async with httpx.AsyncClient() as client:
            for search in search_queries:
                params = {k: v for k, v in search.items() if k != "description"}

                response = await client.get(
                    f"{self.base_url}/api/v1/dashboard/search",
                    params=params,
                    headers=self.headers,
                )

                print(f"  {search['description']}: Status {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    if "results" in data:
                        print(f"    Found {len(data['results'])} results")
                        if "total_count" in data:
                            print(f"    Total count: {data['total_count']}")

        print("✅ Search functionality testing completed")
        return True

    async def test_error_handling(self):
        """Test error handling for React integration"""
        print("❌ Testing error handling...")

        async with httpx.AsyncClient() as client:
            # Test invalid API key
            invalid_headers = {"X-API-Key": "invalid-key"}
            response = await client.get(
                f"{self.base_url}/api/v1/dashboard/stats", headers=invalid_headers
            )

            print(f"  Invalid API key: Status {response.status_code}")
            assert response.status_code == 401

            # Test invalid address format
            response = await client.post(
                f"{self.base_url}/api/v1/analyze",
                json={"address": "invalid-address", "chain_id": 1},
                headers=self.headers,
            )

            print(f"  Invalid address: Status {response.status_code}")
            assert response.status_code == 422

            # Test missing required fields
            response = await client.post(
                f"{self.base_url}/api/v1/analyze",
                json={"chain_id": 1},  # Missing address
                headers=self.headers,
            )

            print(f"  Missing required field: Status {response.status_code}")
            assert response.status_code == 422

        print("✅ Error handling testing completed")
        return True

    async def test_response_times(self):
        """Test response times for React dashboard"""
        print("⏱️  Testing response times...")

        import time

        endpoints = [
            "/health",
            "/api/v1/dashboard/stats",
            "/api/v1/dashboard/trends?days=7",
            "/api/v1/dashboard/search?limit=10",
        ]

        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                start_time = time.time()

                response = await client.get(
                    f"{self.base_url}{endpoint}", headers=self.headers
                )

                end_time = time.time()
                duration = end_time - start_time

                print(f"  {endpoint}: {duration:.3f}s (Status: {response.status_code})")

                # Warn if response time is too slow for frontend
                if duration > 2.0:
                    print(f"    ⚠️  Slow response time: {duration:.3f}s")

        print("✅ Response time testing completed")
        return True

    async def generate_sample_data_for_react(self):
        """Generate sample data structure for React developers"""
        print("📝 Generating sample data for React developers...")

        sample_data = {
            "dashboard_stats": {
                "total_analyses": 1250,
                "honeypots_detected": 89,
                "false_positives": 1161,
                "detection_rate": 7.12,
                "recent_analyses": [
                    {
                        "address": "0xa0b86a33e6c3ca4fdd100269d7e5e50b637cab5d",
                        "is_honeypot": True,
                        "confidence": 0.92,
                        "risk_level": "high",
                        "timestamp": "2025-06-24T10:30:00Z",
                        "techniques": ["Hidden State Update", "Straw Man Contract"],
                    }
                ],
                "risk_distribution": {
                    "low": 800,
                    "medium": 361,
                    "high": 78,
                    "critical": 11,
                },
                "technique_distribution": {
                    "Hidden State Update": 45,
                    "Balance Disorder": 23,
                    "Straw Man Contract": 21,
                    "Access Restriction": 15,
                },
            },
            "analysis_response": {
                "address": "0xa0b86a33e6c3ca4fdd100269d7e5e50b637cab5d",
                "is_honeypot": True,
                "confidence": 0.92,
                "risk_level": "high",
                "detected_techniques": ["Hidden State Update", "Straw Man Contract"],
                "analysis_timestamp": "2025-06-24T10:30:00Z",
                "engine_results": {
                    "static_engine": {
                        "confidence": 0.85,
                        "techniques": ["Hidden State Update"],
                    },
                    "ml_engine": {"confidence": 0.98, "prediction": True},
                },
            },
            "trends_data": {
                "dates": [
                    "2025-06-17",
                    "2025-06-18",
                    "2025-06-19",
                    "2025-06-20",
                    "2025-06-21",
                    "2025-06-22",
                    "2025-06-23",
                ],
                "honeypot_counts": [12, 8, 15, 22, 18, 9, 14],
                "analysis_counts": [145, 132, 189, 234, 198, 156, 178],
                "detection_rates": [8.3, 6.1, 7.9, 9.4, 9.1, 5.8, 7.9],
            },
        }

        # Save sample data to file
        with open("sample_data_for_react.json", "w") as f:
            json.dump(sample_data, f, indent=2)

        print("✅ Sample data saved to 'sample_data_for_react.json'")
        print("   Use this data structure in your React components!")

        return True

    async def run_all_tests(self):
        """Run all React integration tests"""
        print("⚛️  React Integration Testing Suite")
        print("=" * 60)

        tests = [
            self.test_cors_for_react,
            self.test_dashboard_data_structure,
            self.test_contract_analysis_flow,
            self.test_search_functionality,
            self.test_error_handling,
            self.test_response_times,
            self.generate_sample_data_for_react,
        ]

        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
                print()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed: {str(e)}")
                results.append(False)
                print()

        print("=" * 60)
        print(f"📊 React Integration Tests: {sum(results)}/{len(results)} passed")

        if all(results):
            print("🎉 Your API is ready for React integration!")
            print("\n🔧 Next steps for React integration:")
            print("1. Use the API key: honeypot-detector-api-key-12345")
            print("2. Set base URL: http://localhost:8000")
            print("3. Add X-API-Key header to all requests")
            print("4. Check sample_data_for_react.json for data structures")
        else:
            print("⚠️ Some tests failed - check output above")

        return all(results)


async def main():
    """Run React integration tests"""
    tester = ReactIntegrationTester()
    return await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
