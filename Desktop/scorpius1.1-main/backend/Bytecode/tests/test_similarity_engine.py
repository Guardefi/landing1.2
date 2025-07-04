"""
Test suite for the main similarity engine functionality.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest
import torch
from core.similarity_engine import SimilarityEngine
from models.siamese_network import SiameseNetwork


class TestSimilarityEngine:
    """Test cases for the SimilarityEngine class."""

    @pytest.fixture
    def sample_bytecode_pairs(self):
        """Sample bytecode pairs for testing."""
        return [
            # Similar bytecodes (same contract, different optimization)
            (
                "608060405234801561001057600080fd5b50610150806100206000396000f3fe",
                "608060405234801561001057600080fd5b50610150806100206000396000f3fe",
            ),
            # Dissimilar bytecodes
            (
                "608060405234801561001057600080fd5b50610150806100206000396000f3fe",
                "6001600081905550600254600160026000600260026002600260026002",
            ),
            # Empty bytecode cases
            ("", ""),
            ("608060405234801561001057600080fd5b50", ""),
        ]

    @pytest.fixture
    def engine(self):
        """Create a similarity engine instance for testing."""
        config = {
            "model_path": "test_model.pth",
            "similarity_threshold": 0.8,
            "batch_size": 32,
            "use_gpu": False,
            "normalization": {
                "remove_metadata": True,
                "normalize_constants": True,
                "remove_nops": True,
            },
        }
        return SimilarityEngine(config)

    def test_engine_initialization(self, engine):
        """Test that the engine initializes correctly."""
        assert engine is not None
        assert engine.config["similarity_threshold"] == 0.8
        assert engine.comparison_engine is not None
        assert engine.normalizer is not None

    def test_bytecode_normalization(self, engine, sample_bytecode_pairs):
        """Test bytecode normalization functionality."""
        bytecode1, _ = sample_bytecode_pairs[0]

        normalized = engine.normalizer.normalize(bytecode1)
        assert isinstance(normalized, dict)
        assert "normalized_bytecode" in normalized
        assert "features" in normalized
        assert "instructions" in normalized

    def test_traditional_similarity_comparison(self, engine, sample_bytecode_pairs):
        """Test traditional similarity comparison methods."""
        bytecode1, bytecode2 = sample_bytecode_pairs[0]

        # Test Jaccard similarity
        similarity = engine.comparison_engine.jaccard_similarity(bytecode1, bytecode2)
        assert 0.0 <= similarity <= 1.0

        # Test n-gram similarity
        ngram_sim = engine.comparison_engine.ngram_similarity(bytecode1, bytecode2)
        assert 0.0 <= ngram_sim <= 1.0

        # Test structural similarity
        struct_sim = engine.comparison_engine.structural_similarity(
            bytecode1, bytecode2
        )
        assert 0.0 <= struct_sim <= 1.0

    @pytest.mark.asyncio
    async def test_async_similarity_computation(self, engine, sample_bytecode_pairs):
        """Test asynchronous similarity computation."""
        bytecode1, bytecode2 = sample_bytecode_pairs[0]

        result = await engine.compute_similarity_async(bytecode1, bytecode2)

        assert isinstance(result, dict)
        assert "overall_similarity" in result
        assert "jaccard_similarity" in result
        assert "ngram_similarity" in result
        assert "structural_similarity" in result
        assert "neural_similarity" in result

        # Check that similarities are in valid range
        for key, value in result.items():
            if "similarity" in key:
                assert 0.0 <= value <= 1.0

    def test_batch_similarity_computation(self, engine, sample_bytecode_pairs):
        """Test batch processing of similarity computations."""
        pairs = sample_bytecode_pairs[:2]  # Use first two pairs

        results = engine.compute_batch_similarity(pairs)

        assert len(results) == len(pairs)
        for result in results:
            assert isinstance(result, dict)
            assert "overall_similarity" in result

    def test_identical_bytecode_similarity(self, engine):
        """Test that identical bytecodes have high similarity."""
        bytecode = "608060405234801561001057600080fd5b50610150806100206000396000f3fe"

        result = engine.compute_similarity(bytecode, bytecode)

        # Identical bytecodes should have very high similarity
        assert result["overall_similarity"] >= 0.95
        assert result["jaccard_similarity"] == 1.0

    def test_empty_bytecode_handling(self, engine, sample_bytecode_pairs):
        """Test handling of empty bytecodes."""
        empty_pair = sample_bytecode_pairs[2]  # Both empty
        mixed_pair = sample_bytecode_pairs[3]  # One empty, one not

        # Both empty should be considered similar
        result_empty = engine.compute_similarity(*empty_pair)
        assert result_empty["overall_similarity"] >= 0.5

        # Mixed should have low similarity
        result_mixed = engine.compute_similarity(*mixed_pair)
        assert result_mixed["overall_similarity"] < 0.5

    def test_similarity_threshold_application(self, engine):
        """Test that similarity threshold is properly applied."""
        bytecode1 = "608060405234801561001057600080fd5b50610150806100206000396000f3fe"
        bytecode2 = "6001600081905550600254600160026000600260026002600260026002"

        result = engine.compute_similarity(bytecode1, bytecode2)

        # Check if result includes threshold comparison
        assert "is_similar" in result
        assert isinstance(result["is_similar"], bool)

        # is_similar should be True if overall_similarity >= threshold
        expected = result["overall_similarity"] >= engine.config["similarity_threshold"]
        assert result["is_similar"] == expected

    def test_feature_extraction(self, engine):
        """Test feature extraction from bytecode."""
        bytecode = "608060405234801561001057600080fd5b50610150806100206000396000f3fe"

        features = engine.extract_features(bytecode)

        assert isinstance(features, np.ndarray)
        assert len(features.shape) == 1  # Should be 1D feature vector
        assert features.shape[0] > 0  # Should have some features

    @patch("torch.load")
    def test_neural_model_loading(self, mock_torch_load, engine):
        """Test neural model loading and inference."""
        # Mock model loading
        mock_model = Mock(spec=SiameseNetwork)
        mock_model.eval.return_value = mock_model
        mock_model.return_value = torch.tensor([[0.85]])
        mock_torch_load.return_value = mock_model

        # Test model loading
        engine.load_neural_model()

        assert engine.neural_model is not None
        mock_torch_load.assert_called_once()

    def test_performance_metrics_collection(self, engine, sample_bytecode_pairs):
        """Test that performance metrics are collected during operation."""
        bytecode1, bytecode2 = sample_bytecode_pairs[0]

        # Ensure metrics collection is enabled
        engine.collect_metrics = True

        result = engine.compute_similarity(bytecode1, bytecode2)

        assert "metrics" in result
        assert "computation_time" in result["metrics"]
        assert "memory_usage" in result["metrics"]
        assert result["metrics"]["computation_time"] > 0

    def test_caching_functionality(self, engine):
        """Test that caching improves performance for repeated computations."""
        bytecode1 = "608060405234801561001057600080fd5b50610150806100206000396000f3fe"
        bytecode2 = "6001600081905550600254600160026000600260026002600260026002"

        # First computation
        result1 = engine.compute_similarity(bytecode1, bytecode2)
        time1 = result1.get("metrics", {}).get("computation_time", 0)

        # Second computation (should be cached)
        result2 = engine.compute_similarity(bytecode1, bytecode2)
        time2 = result2.get("metrics", {}).get("computation_time", 0)

        # Results should be identical
        assert result1["overall_similarity"] == result2["overall_similarity"]

        # Second computation should be faster (if caching is working)
        # Note: This test might be flaky due to timing variations
        if time1 > 0 and time2 > 0:
            assert time2 <= time1 * 1.1  # Allow 10% variance

    def test_error_handling_invalid_bytecode(self, engine):
        """Test error handling for invalid bytecode inputs."""
        invalid_bytecodes = [
            "invalid_hex",  # Invalid hex
            "60g0",  # Invalid hex character
            None,  # None input
        ]

        valid_bytecode = "608060405234801561001057600080fd5b50"

        for invalid in invalid_bytecodes:
            try:
                result = engine.compute_similarity(valid_bytecode, invalid)
                # Should either handle gracefully or raise appropriate exception
                assert isinstance(result, dict)
            except (ValueError, TypeError):
                # Expected for invalid inputs
                assert True

    def test_configuration_validation(self):
        """Test that invalid configurations are rejected."""
        invalid_configs = [
            {"similarity_threshold": 1.5},  # Threshold > 1
            {"similarity_threshold": -0.1},  # Threshold < 0
            {"batch_size": 0},  # Invalid batch size
            {"batch_size": -1},  # Negative batch size
        ]

        for config in invalid_configs:
            with pytest.raises((ValueError, AssertionError)):
                SimilarityEngine(config)


class TestSimilarityEngineIntegration:
    """Integration tests for the complete similarity engine workflow."""

    @pytest.fixture
    def real_bytecode_samples(self):
        """Real-world bytecode samples for integration testing."""
        return {
            "erc20_token": "608060405234801561001057600080fd5b50600436106100b95760003560e01c806370a082311161007657806395d89b411161005b57806395d89b41146101a4578063a9059cbb146101ac578063dd62ed3e146101d8576100b9565b806370a082311461016a5780638da5cb5b14610190576100b9565b806318160ddd116100a757806318160ddd1461012857806323b872dd14610130578063313ce56714610166576100b9565b806306fdde03146100be578063095ea7b3146100f6575b600080fd5b6100c6610206565b6040805160208082528351818301528351919283929083019185019080838360005b838110156101005781810151838201526020016100e8565b50505050905090810190601f16801561012d5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b610118610294565b60408051918252519081900360200190f35b61015c6004803603606081101561014657600080fd5b506001600160a01b0381358116916020810135909116906040013561029a565b604080519115158252519081900360200190f35b61016e610307565b60408051918252519081900360200190f35b6101186004803603602081101561018057600080fd5b50356001600160a01b031661030d565b610198610328565b60408051918252519081900360200190f35b6100c661032e565b61015c600480360360408110156101c257600080fd5b506001600160a01b038135169060200135610389565b610118600480360360408110156101ee57600080fd5b506001600160a01b0381358116916020013516610396565b60008054604080516020601f60026000196101006001881615020190951694909404938401819004810282018101909252828152606093909290918301828280156102925780601f1061026757610100808354040283529160200191610292565b820191906000526020600020905b81548152906001019060200180831161027557829003601f168201915b505050505090505b90565b60055490565b6000826001600160a01b0381166102b057600080fd5b6001600160a01b0385166000908152600460205260409020548411156102d557600080fd5b6102e08585856103c1565b6001600160a01b03851660009081526004602052604090205484111561015c57600080fd5b60025490565b6001600160a01b031660009081526004602052604090205490565b60035490565b60018054604080516020601f600260001961010087891615020190951694909404938401819004810282018101909252828152606093909290918301828280156102925780601f1061026757610100808354040283529160200191610292565b6000610396338484610489565b600080fd5b6001600160a01b03918216600090815260066020908152604080832093909416825291909152205490565b6001600160a01b0383166000908152600460205260409020546103e4908261053e565b6001600160a01b03808516600090815260046020526040808220939093559084168152205461041390826105ab565b6001600160a01b0380841660008181526004602052604090819020939093559151908516907fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef906104669085815260200190565b60405180910390a36001600160a01b03808416600090815260066020908152604080832033845282529091205461049c9082610614565b6001600160a01b03851660009081526006602090815260408083203384529091529020555050505050565b6001600160a01b03821615806104e957506001600160a01b038316158015906104e957506001600160a01b038216155b6104f257600080fd5b6001600160a01b0383166000908152600660209081526040808320858452909152902054610520908261053e565b6001600160a01b0390931660009081526006602090815260408083209590955291815292902091909155505050565b60008282111561054d57600080fd5b50900390565b6000828201838110156105a457fe5b9392505050565b60008282018381101561059e57600080fd5b6000828211156105c457600080fd5b50039056fea165627a7a7230582020",
            "simple_storage": "608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b6040518082815260200191505060405180910390f35b6100736004803603602081101561006f57600080fd5b503561007e565b005b60008054905090565b600081905550565b56fea2646970667358221220",
            "multisig_wallet": "608060405234801561001057600080fd5b50600436106101735760003560e01c806370a08231116100de578063a0e67e2b11610097578063c6427474116100715780631234567811610061578063d006b222116100415780001e5b90565b8063e00e8d06166000b9576100be565b600080fd5b",
        }

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, real_bytecode_samples):
        """Test the complete similarity analysis workflow."""
        config = {
            "model_path": None,  # Skip neural model for integration test
            "similarity_threshold": 0.7,
            "batch_size": 16,
            "use_gpu": False,
        }

        engine = SimilarityEngine(config)

        # Test all pairwise comparisons
        contracts = list(real_bytecode_samples.items())
        results = []

        for i, (name1, bytecode1) in enumerate(contracts):
            for j, (name2, bytecode2) in enumerate(contracts[i + 1 :], i + 1):
                result = await engine.compute_similarity_async(bytecode1, bytecode2)
                results.append(
                    {
                        "contract1": name1,
                        "contract2": name2,
                        "similarity": result["overall_similarity"],
                        "is_similar": result["is_similar"],
                    }
                )

        # Verify results
        assert len(results) > 0
        for result in results:
            assert 0.0 <= result["similarity"] <= 1.0
            assert isinstance(result["is_similar"], bool)

    def test_performance_benchmarking(self, real_bytecode_samples):
        """Test performance benchmarking capabilities."""
        config = {
            "model_path": None,
            "similarity_threshold": 0.8,
            "collect_metrics": True,
        }

        engine = SimilarityEngine(config)

        # Run benchmark on sample data
        contracts = list(real_bytecode_samples.values())
        pairs = [
            (contracts[i], contracts[j])
            for i in range(len(contracts))
            for j in range(i + 1, len(contracts))
        ]

        # Measure batch processing performance
        start_time = time.time()
        results = engine.compute_batch_similarity(pairs)
        end_time = time.time()

        total_time = end_time - start_time
        throughput = len(pairs) / total_time if total_time > 0 else 0

        # Verify performance metrics
        assert len(results) == len(pairs)
        assert throughput > 0

        # Check that metrics are collected
        for result in results:
            if "metrics" in result:
                assert "computation_time" in result["metrics"]


if __name__ == "__main__":
    import time

    pytest.main([__file__, "-v"])
