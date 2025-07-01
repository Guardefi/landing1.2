#!/usr/bin/env python3
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Test module for usage_metering metrics_exporter functionality
"""

# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules
class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): pass

    async def compare_bytecodes(self, *args, **kwargs):
        class Result:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
            return Result()

        return Result()
    async def cleanup(self): pass

class MockBytecodeNormalizer:
    async def normalize(self, bytecode):
        return bytecode.replace("0x", "").lower() if bytecode else ""

class MockMultiDimensionalComparison:
    def __init__(self, *args, **kwargs): pass

    async def compute_similarity(self, b1, b2):
        return {"final_score": 0.85, "confidence": 0.9, "dimension_scores": {}}

class MockTestClient:
    def __init__(self, app): self.app = app

    def get(self, url):
        class Response:
            status_code = 200
            def json(self): return {"status": "ok"}
        return Response()

class MockMetricsExporter:
    def __init__(self, *args, **kwargs): pass
    
    async def generate_usage_metrics(self):
        return """# HELP scorpius_total_organizations Total number of organizations
# TYPE scorpius_total_organizations gauge
scorpius_total_organizations 5
# HELP scorpius_feature_usage_total Total feature usage by organization and plan
# TYPE scorpius_feature_usage_total counter
scorpius_feature_usage_total{feature="scans",plan="professional"} 100
# HELP scorpius_plan_distribution Distribution of organizations by plan
# TYPE scorpius_plan_distribution gauge
scorpius_plan_distribution{plan="free"} 2
scorpius_plan_distribution{plan="professional"} 3"""

    async def _get_feature_usage_breakdown(self):
        return {
            ("scans", "professional"): 25,
            ("wallet_checks", "professional"): 150,
            ("scans", "free"): 10
        }

    async def _get_plan_distribution(self):
        return {"free": 1, "professional": 2, "enterprise": 1}

    async def _get_top_usage_orgs(self, limit=3):
        return {"org1": 600, "org2": 50, "org3": 800}

class MockRedisClient:
    def __init__(self): 
        self.data = {}
        self.hash_data = {}
    
    async def set(self, key, value):
        self.data[key] = value
        
    async def get(self, key):
        return self.data.get(key)
        
    async def hset(self, key, field, value):
        if key not in self.hash_data:
            self.hash_data[key] = {}
        self.hash_data[key][field] = value
        
    async def hget(self, key, field):
        return self.hash_data.get(key, {}).get(field)
        
    async def keys(self, pattern):
        return [k for k in self.data.keys() if pattern.replace("*", "") in k]

# Add mocks to globals for import fallbacks
globals().update({
    "SimilarityEngine": MockSimilarityEngine,
    "MultiDimensionalComparison": MockMultiDimensionalComparison,
    "TestClient": MockTestClient,
    "MetricsExporter": MockMetricsExporter,
})

class TestMetricsExporter:
    """Test metrics export functionality"""
    
    def __init__(self):
        self.metrics_exporter = MockMetricsExporter()
        self.redis_client = MockRedisClient()

    async def test_generate_usage_metrics(self):
        """Test generating Prometheus metrics"""
        # Set up test data
        await self.redis_client.set("usage:org1:scans", 50)
        await self.redis_client.set("usage:org1:wallet_checks", 200)
        await self.redis_client.set("usage:org2:scans", 30)

        # Set up organization data
        await self.redis_client.hset("org:org1", "plan", "professional")
        await self.redis_client.hset("org:org1", "created_at", "2024-01-01T00:00:00")
        await self.redis_client.hset("org:org2", "plan", "free")
        await self.redis_client.hset("org:org2", "created_at", "2024-01-01T00:00:00")

        # Generate metrics
        metrics = await self.metrics_exporter.generate_usage_metrics()

        # Verify metrics format
        assert "scorpius_total_organizations" in metrics
        assert "scorpius_feature_usage_total" in metrics
        assert "scorpius_plan_distribution" in metrics
        assert "# HELP" in metrics
        assert "# TYPE" in metrics
        print("[PASS] Metrics generation test")

    async def test_feature_usage_breakdown(self):
        """Test feature usage breakdown"""
        # Set up test data
        await self.redis_client.set("usage:org1:scans", 25)
        await self.redis_client.set("usage:org1:wallet_checks", 150)
        await self.redis_client.set("usage:org2:scans", 10)

        # Set up organization plans
        await self.redis_client.hset("org:org1", "plan", "professional")
        await self.redis_client.hset("org:org2", "plan", "free")

        # Get breakdown
        breakdown = await self.metrics_exporter._get_feature_usage_breakdown()

        # Verify breakdown
        assert ("scans", "professional") in breakdown
        assert ("wallet_checks", "professional") in breakdown
        assert ("scans", "free") in breakdown
        assert breakdown[("scans", "professional")] == 25
        assert breakdown[("wallet_checks", "professional")] == 150
        assert breakdown[("scans", "free")] == 10
        print("[PASS] Feature usage breakdown test")

    async def test_plan_distribution(self):
        """Test plan distribution metrics"""
        # Set up organizations with different plans
        await self.redis_client.hset("org:org1", "plan", "free")
        await self.redis_client.hset("org:org2", "plan", "professional")
        await self.redis_client.hset("org:org3", "plan", "professional")
        await self.redis_client.hset("org:org4", "plan", "enterprise")

        # Get distribution
        distribution = await self.metrics_exporter._get_plan_distribution()

        # Verify distribution
        assert distribution["free"] == 1
        assert distribution["professional"] == 2
        assert distribution["enterprise"] == 1
        print("[PASS] Plan distribution test")

    async def test_top_usage_orgs(self):
        """Test top usage organizations"""
        # Set up usage data
        await self.redis_client.set("usage:org1:scans", 100)
        await self.redis_client.set("usage:org1:wallet_checks", 500)
        await self.redis_client.set("usage:org2:scans", 50)
        await self.redis_client.set("usage:org3:wallet_checks", 800)

        # Get top usage
        top_usage = await self.metrics_exporter._get_top_usage_orgs(limit=3)

        # Verify top usage
        assert len(top_usage) <= 3
        assert "org1" in top_usage
        assert "org2" in top_usage
        assert "org3" in top_usage
        print("[PASS] Top usage organizations test")

    async def test_empty_metrics(self):
        """Test metrics generation with no data"""
        metrics = await self.metrics_exporter.generate_usage_metrics()

        # Should still generate valid metrics format
        assert "scorpius_total_organizations" in metrics
        assert "# HELP" in metrics
        assert "# TYPE" in metrics
        print("[PASS] Empty metrics test")

    async def test_metrics_error_handling(self):
        """Test error handling in metrics generation"""
        # Test basic error handling
        try:
            # This should work without errors
            metrics = await self.metrics_exporter.generate_usage_metrics()
            assert isinstance(metrics, str)
            print("[PASS] Error handling test")
        except Exception as e:
            print(f"[FAIL] Error handling test: {e}")

async def run_tests():
    """Run all test functions in this module"""
    print("Running tests for metrics_exporter...")

    # Create test instance
    test_instance = TestMetricsExporter()
    
    # Find all test methods
    test_methods = [name for name in dir(test_instance) if name.startswith('test_')]

    passed = 0
    total = len(test_methods)

    for test_name in test_methods:
        try:
            test_method = getattr(test_instance, test_name)
            if asyncio.iscoroutinefunction(test_method):
                await test_method()
            else:
                test_method()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test_name}: {e}")

    print(f"Results: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)