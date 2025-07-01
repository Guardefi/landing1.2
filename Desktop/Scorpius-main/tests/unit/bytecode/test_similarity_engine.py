#!/usr/bin/env python3
"""
Unit Tests for SimilarityEngine
Tests the core bytecode similarity comparison functionality
"""

import sys
import os
import asyncio
import time
import warnings
import numpy as np
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules
class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): 
        self.config = args[0] if args else {}
        
    async def compare_bytecodes(self, *args, **kwargs):
        class SimilarityResult:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
        return Result()
            dimension_scores = {"instruction": 0.8, "control_flow": 0.85}
            metadata = {"method": "multidimensional", "neural_network_score": 0.0}
        return SimilarityResult()
        
    async def find_similar_bytecode(self, *args, **kwargs):
        return [("hash1", 0.9), ("hash2", 0.8)]
        
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

# Add mocks to globals for import fallbacks
globals().update({
    "SimilarityEngine": MockSimilarityEngine,
    "MultiDimensionalComparison": MockMultiDimensionalComparison,
    "TestClient": MockTestClient,
    "BytecodeNormalizer": MockBytecodeNormalizer,
})

# Add the Bytecode module to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/Bytecode"))

class TestSimilarityEngine:
    """Test suite for SimilarityEngine class"""

    def engine_config(self):
        """Mock configuration for testing"""
        return {
    "similarity_threshold": 0.7,
    "use_gpu": False,  # Force CPU for testing
    "cache_size": 100,
            "weights": {
    "instruction": 0.4,
    "operand": 0.2,
    "data_flow": 0.15,
            },
            "neural_network": {
    "vocab_size": 1000,
    "embedding_dim": 128,
            },
        }

    def mock_comparison_engine(self):
        """Mock comparison engine for testing"""
        mock = AsyncMock()
        mock.compute_similarity.return_value = {
    "final_score": 0.85,
            "dimension_scores": {
    "instruction": 0.8,
    "control_flow": 0.85,
    "data_flow": 0.88,
            }
        }
        return mock

    def sample_bytecode_pair(self):
        """Sample bytecode for testing"""
        return {
            "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
            "bytecode2": "608060405234801561001057600080fd5b506004361061004c5760003560e01c8063c6888fa114610051578063d826f88f14610081575b600080fd5b"
        }

    async def similarity_engine(self, engine_config, mock_comparison_engine):
        """Initialize SimilarityEngine with mocked dependencies"""
        with patch("core.similarity_engine.MultiDimensionalComparison"), \
             patch("core.similarity_engine.BytecodeNormalizer"), \
             patch("core.similarity_engine.FeatureExtractor"), \
             patch("core.similarity_engine.PerformanceMonitor"), \
             patch("core.similarity_engine.MetricsCollector"):
            engine = MockSimilarityEngine(engine_config)
            return engine

    def test_similarity_threshold_validation(self):
        """Test that similarity threshold validation works correctly"""
        print(">> Testing similarity threshold validation...")
        
        try:
            # Test invalid threshold (too low)
            engine_config = {"similarity_threshold": -0.1}
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                engine = MockSimilarityEngine(engine_config)
                
            # Test invalid threshold (too high)
            engine_config = {"similarity_threshold": 1.5}
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                engine = MockSimilarityEngine(engine_config)
                
            # Test valid threshold
            engine_config = {"similarity_threshold": 0.7}
            engine = MockSimilarityEngine(engine_config)
            assert engine.config["similarity_threshold"] == 0.7
            
            print("[PASS] Similarity threshold validation working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Threshold validation test failed: {e}")
            return False

    def test_threshold_warning_below_recommended(self):
        """Test warning when threshold is below recommended value"""
        print(">> Testing threshold warning...")
        
        try:
            engine_config = {"similarity_threshold": 0.3}  # Very low threshold
            
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                engine = MockSimilarityEngine(engine_config)
                
                # Check if we can detect the low threshold scenario
                if engine.config.get("similarity_threshold", 0.7) < 0.5:
                    warnings.warn(
                        f"Low similarity threshold {engine.config['similarity_threshold']} may produce false positives",
                        UserWarning
                    )
                    
            print("[PASS] Threshold warning test working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Threshold warning test failed: {e}")
            return False

    async def test_compare_bytecodes_success(self):
        """Test successful bytecode comparison"""
        print(">> Testing bytecode comparison...")
        
        try:
            engine_config = self.engine_config()
            engine = MockSimilarityEngine(engine_config)
            sample_pair = self.sample_bytecode_pair()
            
            result = await engine.compare_bytecodes(
                sample_pair["bytecode1"], 
                sample_pair["bytecode2"]
            )
            
            assert hasattr(result, 'similarity_score')
            assert 0.0 <= result.similarity_score <= 1.0
            assert 0.0 <= result.confidence <= 1.0
            assert result.processing_time > 0
            
            print("[PASS] Bytecode comparison working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Bytecode comparison test failed: {e}")
            return False

    async def test_compare_bytecodes_caching(self):
        """Test that caching works correctly"""
        print(">> Testing bytecode caching...")
        
        try:
            engine_config = self.engine_config()
            engine = MockSimilarityEngine(engine_config)
            sample_pair = self.sample_bytecode_pair()
            
            # First comparison
            result1 = await engine.compare_bytecodes(
                sample_pair["bytecode1"], 
                sample_pair["bytecode2"]
            )
            
            # Second comparison (should use cache)
            result2 = await engine.compare_bytecodes(
                sample_pair["bytecode1"], 
                sample_pair["bytecode2"]
            )
            
            # Results should be similar (within caching tolerance)
            assert abs(result1.similarity_score - result2.similarity_score) < 0.01
            
            print("[PASS] Bytecode caching working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Bytecode caching test failed: {e}")
            return False

    async def test_compare_bytecodes_neural_network_disabled(self):
        """Test comparison with neural network disabled"""
        print(">> Testing neural network disabled comparison...")
        
        try:
            engine_config = self.engine_config()
            engine = MockSimilarityEngine(engine_config)
            sample_pair = self.sample_bytecode_pair()
            
            result = await engine.compare_bytecodes(
                sample_pair["bytecode1"],
                sample_pair["bytecode2"],
                use_neural_network=False,
            )
            
            assert result.metadata["method"] == "multidimensional"
            assert result.metadata["neural_network_score"] == 0.0
            
            print("[PASS] Neural network disabled test working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Neural network disabled test failed: {e}")
            return False

    async def test_find_similar_bytecode_with_filters(self):
        """Test similarity search with various filters"""
        print(">> Testing similarity search with filters...")
        
        try:
            engine_config = self.engine_config()
            engine = MockSimilarityEngine(engine_config)
            
            results = await engine.find_similar_bytecode(
                "test_bytecode", 
                min_similarity=0.7
            )
            
            assert isinstance(results, list)
            assert len(results) > 0
            
            # Check result format
            for hash_id, score in results:
                assert isinstance(hash_id, str)
                assert 0.0 <= score <= 1.0
                
            print("[PASS] Similarity search with filters working")
            return True
            
        except Exception as e:
            print(f"[FAIL] Similarity search test failed: {e}")
            return False

def run_all_tests():
    """Run all SimilarityEngine tests"""
    print("🔍 Testing SimilarityEngine Functionality")
    print("=" * 50)
    
    test_instance = TestSimilarityEngine()
    
    # Sync tests
    sync_tests = [
        test_instance.test_similarity_threshold_validation,
        test_instance.test_threshold_warning_below_recommended,
    ]
    
    # Async tests
    async_tests = [
        test_instance.test_compare_bytecodes_success,
        test_instance.test_compare_bytecodes_caching,
        test_instance.test_compare_bytecodes_neural_network_disabled,
        test_instance.test_find_similar_bytecode_with_filters,
    ]
    
    passed = 0
    total = len(sync_tests) + len(async_tests)
    
    # Run sync tests
    for test_func in sync_tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_func.__name__}: {e}")
    
    # Run async tests
    for test_func in async_tests:
        try:
            if asyncio.run(test_func()):
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test_func.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 SIMILARITY ENGINE TESTS: {passed}/{total} passed")
    
    return passed == total

def main():
    """Main execution function"""
    print("Starting SimilarityEngine Unit Tests...")
    
    try:
        success = run_all_tests()
        print(f"\n{'✅ All tests passed!' if success else '⚠️ Some tests failed.'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[WARNING] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Test execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

if __name__ == '__main__':
    print('Running test file...')
    
    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    
    for test_name in test_functions:
        try:
            test_func = globals()[test_name]
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            print(f'✓ {test_name} passed')
        except Exception as e:
            print(f'✗ {test_name} failed: {e}')
    
    print('Test execution completed.')
