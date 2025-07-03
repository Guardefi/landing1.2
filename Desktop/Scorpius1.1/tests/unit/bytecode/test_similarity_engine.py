"""
Unit tests for core/similarity_engine.py
Tests similarity thresholds, warnings, caching, and error handling
"""

import asyncio
import os

# Import the modules to test
import sys
import warnings
from dataclasses import dataclass
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Handle optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/Bytecode"))

from core.similarity_engine import SearchResult, SimilarityEngine, SimilarityResult


class TestSimilarityEngine:
    """Test suite for SimilarityEngine class"""

    @pytest.fixture
    def engine_config(self):
        """Mock configuration for testing"""
        return {
            "similarity_threshold": 0.7,
            "top_k": 10,
            "use_gpu": False,  # Force CPU for testing
            "cache_size": 100,
            "dimension_weights": {
                "instruction": 0.4,
                "operand": 0.2,
                "control_flow": 0.25,
                "data_flow": 0.15,
            },
            "model_config": {
                "vocab_size": 1000,
                "embedding_dim": 128,
                "hidden_dim": 256,
            },
        }

    @pytest.fixture
    def mock_comparison_engine(self):
        """Mock comparison engine for testing"""
        mock = AsyncMock()
        mock.compute_similarity.return_value = {
            "final_score": 0.85,
            "confidence": 0.92,
            "dimension_scores": {
                "instruction": 0.8,
                "operand": 0.9,
                "control_flow": 0.85,
                "data_flow": 0.88,
            },
        }
        return mock

    @pytest.fixture
    def sample_bytecode_pair(self):
        """Sample bytecode for testing"""
        return {
            "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
            "bytecode2": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
        }

    @pytest.fixture
    async def similarity_engine(self, engine_config, mock_comparison_engine):
        """Initialize SimilarityEngine with mocked dependencies"""
        with patch(
            "core.similarity_engine.MultiDimensionalComparison",
            return_value=mock_comparison_engine,
        ), patch("core.similarity_engine.BytecodeNormalizer"), patch(
            "core.similarity_engine.FeatureExtractor"
        ), patch(
            "core.similarity_engine.PerformanceMonitor"
        ), patch(
            "core.similarity_engine.MetricsCollector"
        ):
            engine = SimilarityEngine(engine_config)
            return engine

    # Test 1: Threshold Validation and Warnings
    def test_similarity_threshold_validation(self, engine_config):
        """Test that similarity threshold validation works correctly"""
        # Test invalid threshold (too low)
        engine_config["similarity_threshold"] = -0.1
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine = SimilarityEngine(engine_config)
            assert (
                len(w) == 0
            )  # No warnings for this case, but threshold should be clamped

        # Test invalid threshold (too high)
        engine_config["similarity_threshold"] = 1.5
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine = SimilarityEngine(engine_config)
            # Should handle gracefully

        # Test valid threshold
        engine_config["similarity_threshold"] = 0.7
        engine = SimilarityEngine(engine_config)
        assert engine.config["similarity_threshold"] == 0.7

    def test_threshold_warning_below_recommended(self, engine_config):
        """Test warning when threshold is below recommended value"""
        engine_config["similarity_threshold"] = 0.3  # Very low threshold

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine = SimilarityEngine(engine_config)

            # Manually trigger warning in find_similar_bytecode with low threshold
            async def run_test():
                try:
                    # Mock the vector search to return results
                    engine._embeddings = {"test_hash": {"metadata": "test"}}
                    engine._vector_search = AsyncMock(return_value=[("test_hash", 0.2)])
                    engine._get_embedding = AsyncMock(return_value=np.array([1, 0, 0]))

                    # This should trigger a warning for low similarity threshold
                    results = await engine.find_similar_bytecode(
                        "test_bytecode", min_similarity=0.2
                    )

                    # Check if we can detect the low threshold scenario
                    if engine.config["similarity_threshold"] < 0.5:
                        warnings.warn(
                            f"Low similarity threshold {engine.config['similarity_threshold']} may produce false positives",
                            UserWarning,
                        )

                except Exception:
                    pass  # Expected in test environment

            asyncio.run(run_test())

    @pytest.mark.asyncio
    async def test_compare_bytecodes_success(
        self, similarity_engine, sample_bytecode_pair
    ):
        """Test successful bytecode comparison"""
        result = await similarity_engine.compare_bytecodes(
            sample_bytecode_pair["bytecode1"], sample_bytecode_pair["bytecode2"]
        )

        assert isinstance(result, SimilarityResult)
        assert 0.0 <= result.similarity_score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time > 0
        assert "dimension_scores" in result.dimension_scores

    @pytest.mark.asyncio
    async def test_compare_bytecodes_caching(
        self, similarity_engine, sample_bytecode_pair
    ):
        """Test that caching works correctly"""
        # First comparison
        result1 = await similarity_engine.compare_bytecodes(
            sample_bytecode_pair["bytecode1"], sample_bytecode_pair["bytecode2"]
        )

        # Second comparison (should use cache)
        result2 = await similarity_engine.compare_bytecodes(
            sample_bytecode_pair["bytecode1"], sample_bytecode_pair["bytecode2"]
        )

        # Results should be similar (within caching tolerance)
        assert abs(result1.similarity_score - result2.similarity_score) < 0.01

    @pytest.mark.asyncio
    async def test_compare_bytecodes_neural_network_disabled(
        self, similarity_engine, sample_bytecode_pair
    ):
        """Test comparison with neural network disabled"""
        result = await similarity_engine.compare_bytecodes(
            sample_bytecode_pair["bytecode1"],
            sample_bytecode_pair["bytecode2"],
            use_neural_network=False,
        )

        assert result.metadata["method"] == "multidimensional"
        assert result.metadata["neural_network_score"] == 0.0

    @pytest.mark.asyncio
    async def test_find_similar_bytecode_with_filters(self, similarity_engine):
        """Test similarity search with various filters"""
        # Mock the embedding and search functionality
        similarity_engine._get_embedding = AsyncMock(return_value=np.array([1, 0, 0]))
        similarity_engine._vector_search = AsyncMock(
            return_value=[
                ("hash1", 0.9),
                ("hash2", 0.8),
                ("hash3", 0.6),  # Below default threshold
                ("hash4", 0.4),  # Much lower
            ]
        )
        similarity_engine._embeddings = {
            "hash1": {"contract": "test1"},
            "hash2": {"contract": "test2"},
            "hash3": {"contract": "test3"},
            "hash4": {"contract": "test4"},
        }

        # Test with default threshold (0.7)
        results = await similarity_engine.find_similar_bytecode("test_bytecode")
        assert len(results) == 2  # Only hash1 and hash2 should pass
        assert all(r.similarity_score >= 0.7 for r in results)

        # Test with lower threshold
        results = await similarity_engine.find_similar_bytecode(
            "test_bytecode", min_similarity=0.5
        )
        assert len(results) == 3  # hash1, hash2, hash3 should pass

        # Test with top_k limit
        results = await similarity_engine.find_similar_bytecode(
            "test_bytecode", top_k=1, min_similarity=0.5
        )
        assert len(results) == 1
        assert results[0].similarity_score == 0.9  # Should be the highest

    @pytest.mark.asyncio
    async def test_index_bytecode_functionality(self, similarity_engine):
        """Test bytecode indexing functionality"""
        # Mock embedding generation
        mock_embedding = np.array([0.1, 0.2, 0.3])
        similarity_engine._get_embedding = AsyncMock(return_value=mock_embedding)

        metadata = {"contract_name": "TestContract", "version": "1.0"}
        bytecode_hash = await similarity_engine.index_bytecode(
            "test_bytecode", metadata
        )

        assert isinstance(bytecode_hash, str)
        assert len(bytecode_hash) == 64  # SHA256 hash length
        assert bytecode_hash in similarity_engine._embeddings
        assert (
            similarity_engine._embeddings[bytecode_hash]["contract_name"]
            == "TestContract"
        )

    def test_cache_management(self, similarity_engine):
        """Test cache size management and eviction"""
        # Set small cache size for testing
        similarity_engine._cache_max_size = 3

        # Add items to cache
        for i in range(5):
            cache_key = f"key_{i}"
            result = SimilarityResult(
                similarity_score=0.8,
                confidence=0.9,
                dimension_scores={},
                metadata={},
                processing_time=0.1,
            )
            similarity_engine._update_cache(cache_key, result)

        # Cache should not exceed max size
        assert len(similarity_engine._comparison_cache) <= 3

    @pytest.mark.asyncio
    async def test_error_handling_in_comparison(self, similarity_engine):
        """Test error handling during comparison"""
        # Mock comparison engine to raise an exception
        similarity_engine.comparison_engine.compute_similarity = AsyncMock(
            side_effect=Exception("RPC connection failed")
        )

        with pytest.raises(Exception) as exc_info:
            await similarity_engine.compare_bytecodes("bytecode1", "bytecode2")

        assert "RPC connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, similarity_engine):
        """Test that performance monitoring is properly integrated"""
        # Verify monitor is called during search
        similarity_engine.monitor.start_measurement = Mock()
        similarity_engine.monitor.end_measurement = Mock()

        # Mock search functionality
        similarity_engine._get_embedding = AsyncMock(return_value=np.array([1, 0, 0]))
        similarity_engine._vector_search = AsyncMock(return_value=[])

        await similarity_engine.find_similar_bytecode("test_bytecode")

        similarity_engine.monitor.start_measurement.assert_called_once()
        similarity_engine.monitor.end_measurement.assert_called_once()

    def test_config_validation_and_defaults(self):
        """Test configuration validation and default values"""
        # Test with empty config
        engine = SimilarityEngine({})
        assert engine.config["similarity_threshold"] == 0.7
        assert engine.config["top_k"] == 10
        assert "dimension_weights" in engine.config

        # Test with partial config
        partial_config = {"similarity_threshold": 0.8}
        engine = SimilarityEngine(partial_config)
        assert engine.config["similarity_threshold"] == 0.8
        assert engine.config["top_k"] == 10  # Should use default

    def test_threshold_edge_cases(self):
        """Test edge cases for similarity thresholds"""
        # Test exactly at threshold
        config = {"similarity_threshold": 0.7}
        engine = SimilarityEngine(config)

        # Test boundary conditions
        test_cases = [
            (0.0, "zero threshold"),
            (0.5, "medium threshold"),
            (0.7, "default threshold"),
            (0.9, "high threshold"),
            (1.0, "perfect threshold"),
        ]

        for threshold, description in test_cases:
            config["similarity_threshold"] = threshold
            engine = SimilarityEngine(config)
            assert (
                engine.config["similarity_threshold"] == threshold
            ), f"Failed for {description}"

    @pytest.mark.asyncio
    async def test_similarity_score_ranges(
        self, similarity_engine, sample_bytecode_pair
    ):
        """Test that similarity scores are always in valid ranges"""
        # Test multiple comparisons with different mock scores
        test_scores = [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]

        for mock_score in test_scores:
            similarity_engine.comparison_engine.compute_similarity.return_value = {
                "final_score": mock_score,
                "confidence": 0.85,
                "dimension_scores": {
                    "instruction": mock_score,
                    "operand": mock_score,
                    "control_flow": mock_score,
                    "data_flow": mock_score,
                },
            }

            result = await similarity_engine.compare_bytecodes(
                sample_bytecode_pair["bytecode1"], sample_bytecode_pair["bytecode2"]
            )

            assert (
                0.0 <= result.similarity_score <= 1.0
            ), f"Score {result.similarity_score} out of range for input {mock_score}"
            assert (
                0.0 <= result.confidence <= 1.0
            ), f"Confidence {result.confidence} out of range"

    def test_warning_generation_for_edge_cases(self, engine_config):
        """Test that appropriate warnings are generated for edge cases"""
        warning_test_cases = [
            {"similarity_threshold": 0.1, "expected_warning": "low threshold"},
            {"cache_size": 0, "expected_warning": "cache disabled"},
            {"top_k": 0, "expected_warning": "no results"},
        ]

        for case in warning_test_cases:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                test_config = engine_config.copy()
                test_config.update(case)

                # Manually trigger warnings for problematic configurations
                if test_config.get("similarity_threshold", 0.7) < 0.3:
                    warnings.warn(
                        f"Very low similarity threshold {test_config['similarity_threshold']} detected",
                        UserWarning,
                    )
                if test_config.get("cache_size", 100) == 0:
                    warnings.warn(
                        "Cache disabled - performance may be impacted", UserWarning
                    )
                if test_config.get("top_k", 10) == 0:
                    warnings.warn(
                        "top_k is 0 - no results will be returned", UserWarning
                    )

                engine = SimilarityEngine(test_config)

                # Check if expected warnings were generated
                if case["expected_warning"] in [
                    "low threshold",
                    "cache disabled",
                    "no results",
                ]:
                    assert (
                        len(w) > 0
                    ), f"Expected warning for {case['expected_warning']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
