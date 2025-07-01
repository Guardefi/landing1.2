"""
Comprehensive tests for core SCORPIUS modules.
"""
import asyncio
import os

# Import the modules we're testing
import sys
import tempfile
import time
from unittest.mock import patch

import pytest
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.comparison_engine import MultiDimensionalComparison
from core.similarity_engine import SimilarityEngine
from models.siamese_network import SiameseNetwork
from preprocessors.bytecode_normalizer import BytecodeNormalizer
from utils.metrics import PerformanceMonitor


class TestSimilarityEngineCore:
    """Test cases for the core SimilarityEngine implementation."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.engine = SimilarityEngine()
        # Real EVM bytecode examples
        self.sample_bytecode1 = "608060405234801561001057600080fd5b50600436106100365760003560e01c8063893d20e81461003b578063a6f9dae114610059575b600080fd5b610043610075565b60405161005091906100a4565b60405180910390f35b610073600480360381019061006e91906100f0565b61009e565b005b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b8073ffffffffffffffffffffffffffffffffffffffff166108fc479081150290604051600060405180830381858888f193505050501580156100e4573d6000803e3d6000fd5b5050565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b6000610118826100ed565b9050919050565b6101288161010d565b811461013357600080fd5b50565b600081359050610145816101"
        self.sample_bytecode2 = "608060405234801561001057600080fd5b50600436106100365760003560e01c8063893d20e81461003b578063a6f9dae114610059575b600080fd5b610043610075565b60405161005091906100a4565b60405180910390f35b610073600480360381019061006e91906100f0565b61009e565b005b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b8073ffffffffffffffffffffffffffffffffffffffff166108fc479081150290604051600060405180830381858888f193505050501580156100e4573d6000803e3d6000fd5b5050565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b6000610118826100ed565b9050919050565b6101288161010d565b811461013357600080fd5b50565b600081359050610145816101"

    @pytest.mark.asyncio
    async def test_compare_bytecodes_basic(self):
        """Test basic bytecode comparison functionality."""
        with patch.object(
            self.engine.comparison_engine,
            "multi_dimensional_compare",
            return_value={
                "jaccard_similarity": 0.85,
                "opcode_similarity": 0.90,
                "control_flow_similarity": 0.80,
                "structural_similarity": 0.75,
            },
        ) as mock_compare:
            with patch.object(
                self.engine.neural_model, "compare_async", return_value=0.92
            ) as mock_neural:
                result = await self.engine.compare_bytecodes(
                    self.sample_bytecode1, self.sample_bytecode2
                )

                assert "jaccard_similarity" in result
                assert "neural_similarity" in result
                assert "combined_score" in result
                assert 0.0 <= result["combined_score"] <= 1.0
                mock_compare.assert_called_once()
                mock_neural.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_bytecode_input(self):
        """Test handling of invalid bytecode input."""
        with pytest.raises(ValueError, match="Invalid bytecode format"):
            await self.engine.compare_bytecodes("invalid", "also_invalid")

    @pytest.mark.asyncio
    async def test_identical_bytecodes(self):
        """Test that identical bytecodes return high similarity."""
        with patch.object(
            self.engine.comparison_engine,
            "multi_dimensional_compare",
            return_value={
                "jaccard_similarity": 1.0,
                "opcode_similarity": 1.0,
                "control_flow_similarity": 1.0,
                "structural_similarity": 1.0,
            },
        ):
            with patch.object(
                self.engine.neural_model, "compare_async", return_value=1.0
            ):
                result = await self.engine.compare_bytecodes(
                    self.sample_bytecode1, self.sample_bytecode1
                )

                assert result["jaccard_similarity"] == 1.0
                assert result["combined_score"] >= 0.9

    @pytest.mark.asyncio
    async def test_batch_comparison(self):
        """Test batch comparison functionality."""
        bytecodes = [self.sample_bytecode1, self.sample_bytecode2]

        with patch.object(
            self.engine, "compare_bytecodes", return_value={"combined_score": 0.85}
        ):
            results = await self.engine.batch_compare(bytecodes)

            assert len(results) == 1  # n*(n-1)/2 comparisons for n=2
            assert "bytecode1" in results[0]
            assert "bytecode2" in results[0]
            assert "similarity" in results[0]

    @pytest.mark.asyncio
    async def test_search_similar(self):
        """Test similarity search functionality."""
        target = self.sample_bytecode1
        candidates = [self.sample_bytecode2]

        with patch.object(
            self.engine, "compare_bytecodes", return_value={"combined_score": 0.85}
        ):
            results = await self.engine.search_similar(
                target, candidates, threshold=0.8, top_k=5
            )

            assert len(results) == 1
            assert results[0]["bytecode"] == self.sample_bytecode2
            assert results[0]["similarity"] == 0.85


class TestComparisonEngineCore:
    """Test cases for the MultiDimensionalComparison class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MultiDimensionalComparison()

    def test_jaccard_similarity_calculation(self):
        """Test Jaccard similarity calculation."""
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}

        similarity = self.engine.calculate_jaccard_similarity(set1, set2)
        expected = 2.0 / 4.0  # intersection=2, union=4

        assert abs(similarity - expected) < 1e-6

    def test_jaccard_empty_sets(self):
        """Test Jaccard similarity with empty sets."""
        set1 = set()
        set2 = {"a", "b"}

        similarity = self.engine.calculate_jaccard_similarity(set1, set2)
        assert similarity == 0.0

        # Both empty should return 1.0 (identical)
        similarity = self.engine.calculate_jaccard_similarity(set(), set())
        assert similarity == 1.0

    def test_multi_dimensional_compare(self):
        """Test multi-dimensional comparison."""
        with patch.object(self.engine.normalizer, "normalize", side_effect=lambda x: x):
            with patch.object(
                self.engine.normalizer,
                "extract_opcodes",
                return_value=["PUSH1", "MSTORE", "RETURN"],
            ):
                with patch.object(
                    self.engine.normalizer,
                    "extract_control_flow",
                    return_value=["JUMPI", "JUMP"],
                ):
                    result = self.engine.multi_dimensional_compare(
                        "bytecode1", "bytecode2"
                    )

                    assert "jaccard_similarity" in result
                    assert "opcode_similarity" in result
                    assert "control_flow_similarity" in result
                    assert "structural_similarity" in result

    def test_calculate_structural_similarity(self):
        """Test structural similarity calculation."""
        features1 = {"function_count": 3, "loop_count": 1, "branch_count": 2}
        features2 = {"function_count": 3, "loop_count": 2, "branch_count": 2}

        similarity = self.engine.calculate_structural_similarity(features1, features2)
        assert 0.0 <= similarity <= 1.0


class TestBytecodeNormalizerCore:
    """Test cases for the BytecodeNormalizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = BytecodeNormalizer()

    def test_normalize_bytecode(self):
        """Test bytecode normalization."""
        bytecode = "608060405234801561001057600080fd5b50"
        normalized = self.normalizer.normalize(bytecode)

        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_extract_opcodes(self):
        """Test opcode extraction from bytecode."""
        bytecode = "608060405234801561001057600080fd5b50"
        opcodes = self.normalizer.extract_opcodes(bytecode)

        assert isinstance(opcodes, list)
        assert len(opcodes) > 0
        assert all(isinstance(op, str) for op in opcodes)

    def test_extract_control_flow(self):
        """Test control flow extraction."""
        bytecode = "608060405234801561001057600080fd5b50"
        control_flow = self.normalizer.extract_control_flow(bytecode)

        assert isinstance(control_flow, list)

    def test_extract_data_patterns(self):
        """Test data pattern extraction."""
        bytecode = "608060405234801561001057600080fd5b50"
        patterns = self.normalizer.extract_data_patterns(bytecode)

        assert isinstance(patterns, list)

    def test_validate_bytecode_valid(self):
        """Test validation of valid bytecode."""
        valid_bytecode = "608060405234801561001057600080fd5b50"
        assert self.normalizer.validate_bytecode(valid_bytecode)

    def test_validate_bytecode_invalid(self):
        """Test validation of invalid bytecode."""
        invalid_bytecode = "invalid_hex"
        assert not self.normalizer.validate_bytecode(invalid_bytecode)

    def test_remove_metadata(self):
        """Test metadata removal from bytecode."""
        bytecode_with_metadata = (
            "608060405234801561001057600080fd5b50a165627a7a72305820"
        )
        cleaned = self.normalizer.remove_metadata(bytecode_with_metadata)

        assert isinstance(cleaned, str)
        assert len(cleaned) <= len(bytecode_with_metadata)

    def test_extract_function_signatures(self):
        """Test function signature extraction."""
        bytecode = "608060405234801561001057600080fd5b50600436106100365760003560e01c8063893d20e8"
        signatures = self.normalizer.extract_function_signatures(bytecode)

        assert isinstance(signatures, list)


class TestSiameseNetworkCore:
    """Test cases for the SiameseNetwork class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "input_dim": 256,
            "hidden_dims": [128, 64],
            "dropout_rate": 0.2,
            "attention_heads": 4,
        }
        self.model = SiameseNetwork(self.config)

    def test_model_initialization(self):
        """Test that the model initializes correctly."""
        assert isinstance(self.model, SiameseNetwork)
        assert self.model.config == self.config

    def test_forward_pass(self):
        """Test forward pass through the model."""
        batch_size = 2
        input_dim = self.config["input_dim"]

        # Create dummy input tensors
        x1 = torch.randn(batch_size, input_dim)
        x2 = torch.randn(batch_size, input_dim)

        with torch.no_grad():
            output = self.model(x1, x2)

        assert output.shape == (batch_size,)
        assert torch.all(output >= 0) and torch.all(output <= 1)

    @pytest.mark.asyncio
    async def test_compare_async(self):
        """Test async comparison method."""
        bytecode1 = "608060405234801561001057600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b51"

        with patch.object(
            self.model, "preprocess_bytecode", return_value=torch.randn(256)
        ):
            with patch.object(self.model, "forward", return_value=torch.tensor([0.85])):
                similarity = await self.model.compare_async(bytecode1, bytecode2)
                assert isinstance(similarity, float)
                assert 0.0 <= similarity <= 1.0

    def test_preprocess_bytecode(self):
        """Test bytecode preprocessing for neural network."""
        bytecode = "608060405234801561001057600080fd5b50"
        processed = self.model.preprocess_bytecode(bytecode)

        assert isinstance(processed, torch.Tensor)
        assert processed.shape[-1] == self.config["input_dim"]

    def test_save_and_load_model(self):
        """Test model saving and loading."""
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Save model
            self.model.save_model(tmp_path)
            assert os.path.exists(tmp_path)

            # Load model
            loaded_model = SiameseNetwork(self.config)
            loaded_model.load_model(tmp_path)

            # Verify models have same parameters
            for p1, p2 in zip(self.model.parameters(), loaded_model.parameters()):
                assert torch.allclose(p1, p2, atol=1e-6)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestPerformanceMonitorCore:
    """Test cases for the PerformanceMonitor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = PerformanceMonitor()

    def test_record_comparison(self):
        """Test recording comparison metrics."""
        self.monitor.record_comparison(0.85, 125.5)

        assert len(self.monitor.comparison_times) == 1
        assert len(self.monitor.similarity_scores) == 1
        assert self.monitor.comparison_times[0] == 125.5
        assert self.monitor.similarity_scores[0] == 0.85

    def test_get_statistics(self):
        """Test getting performance statistics."""
        # Record some test data
        self.monitor.record_comparison(0.85, 100.0)
        self.monitor.record_comparison(0.92, 150.0)
        self.monitor.record_comparison(0.78, 120.0)

        stats = self.monitor.get_statistics()

        assert "avg_comparison_time" in stats
        assert "avg_similarity_score" in stats
        assert "total_comparisons" in stats
        assert stats["total_comparisons"] == 3
        assert abs(stats["avg_comparison_time"] - 123.33) < 0.1
        assert abs(stats["avg_similarity_score"] - 0.85) < 0.01

    def test_reset_metrics(self):
        """Test resetting performance metrics."""
        self.monitor.record_comparison(0.85, 100.0)
        assert len(self.monitor.comparison_times) == 1

        self.monitor.reset_metrics()
        assert len(self.monitor.comparison_times) == 0
        assert len(self.monitor.similarity_scores) == 0

    def test_get_system_metrics(self):
        """Test getting system performance metrics."""
        metrics = self.monitor.get_system_metrics()

        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "memory_used_mb" in metrics
        assert "disk_usage_percent" in metrics

        assert isinstance(metrics["cpu_percent"], (int, float))
        assert isinstance(metrics["memory_percent"], (int, float))
        assert isinstance(metrics["memory_used_mb"], (int, float))
        assert isinstance(metrics["disk_usage_percent"], (int, float))

    @pytest.mark.asyncio
    async def test_start_monitoring(self):
        """Test starting background monitoring."""
        # Start monitoring for a short time
        task = await self.monitor.start_monitoring(interval=0.1)

        # Let it run briefly
        await asyncio.sleep(0.25)

        # Stop monitoring
        task.cancel()

        # Should have collected some metrics
        assert len(self.monitor.system_metrics_history) > 0

    def test_export_metrics(self):
        """Test exporting metrics to file."""
        # Record some test data
        self.monitor.record_comparison(0.85, 100.0)
        self.monitor.record_comparison(0.92, 150.0)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            self.monitor.export_metrics(tmp_path)
            assert os.path.exists(tmp_path)

            # Verify file contains expected data
            import json

            with open(tmp_path, "r") as f:
                exported_data = json.load(f)

            assert "statistics" in exported_data
            assert "comparison_history" in exported_data
            assert len(exported_data["comparison_history"]) == 2

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Integration Tests
class TestCoreModulesIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_end_to_end_comparison(self):
        """Test complete end-to-end bytecode comparison."""
        engine = SimilarityEngine()

        bytecode1 = "608060405234801561001057600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b51"

        # Mock the neural model to avoid loading actual weights
        with patch.object(engine.neural_model, "compare_async", return_value=0.85):
            result = await engine.compare_bytecodes(bytecode1, bytecode2)

            # Verify complete result structure
            expected_keys = [
                "jaccard_similarity",
                "neural_similarity",
                "combined_score",
                "opcode_similarity",
                "control_flow_similarity",
                "structural_similarity",
            ]

            for key in expected_keys:
                assert key in result
                assert isinstance(result[key], (int, float))
                assert 0.0 <= result[key] <= 1.0

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self):
        """Test integration with performance monitoring."""
        engine = SimilarityEngine()
        monitor = PerformanceMonitor()

        bytecode1 = "608060405234801561001057600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b51"

        # Mock neural model
        with patch.object(engine.neural_model, "compare_async", return_value=0.85):
            start_time = time.time()
            result = await engine.compare_bytecodes(bytecode1, bytecode2)
            comparison_time = (time.time() - start_time) * 1000  # ms

            # Record in monitor
            monitor.record_comparison(result["combined_score"], comparison_time)

            # Verify monitoring data
            stats = monitor.get_statistics()
            assert stats["total_comparisons"] == 1
            assert stats["avg_similarity_score"] == result["combined_score"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
