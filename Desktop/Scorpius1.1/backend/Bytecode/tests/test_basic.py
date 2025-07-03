"""
Basic tests for SCORPIUS engine components
"""

import asyncio

import pytest
from core.comparison_engine import MultiDimensionalComparison
from core.similarity_engine import SimilarityEngine
from preprocessors.bytecode_normalizer import BytecodeNormalizer


class TestBytecodeNormalizer:
    """Test bytecode normalization"""

    @pytest.fixture
    def normalizer(self):
        return BytecodeNormalizer()

    @pytest.mark.asyncio
    async def test_normalize_basic_bytecode(self, normalizer):
        """Test basic bytecode normalization"""
        bytecode = "0x6080604052348015600f57600080fd5b50"
        normalized = await normalizer.normalize(bytecode)

        assert normalized is not None
        assert len(normalized) > 0
        assert not normalized.startswith("0x")

    @pytest.mark.asyncio
    async def test_normalize_empty_bytecode(self, normalizer):
        """Test normalization with empty bytecode"""
        bytecode = ""
        normalized = await normalizer.normalize(bytecode)

        assert normalized == ""

    @pytest.mark.asyncio
    async def test_normalize_hex_prefix(self, normalizer):
        """Test normalization handles hex prefix correctly"""
        bytecode_with_prefix = "0x6080604052"
        bytecode_without_prefix = "6080604052"

        normalized_with = await normalizer.normalize(bytecode_with_prefix)
        normalized_without = await normalizer.normalize(bytecode_without_prefix)

        assert normalized_with == normalized_without


class TestMultiDimensionalComparison:
    """Test multi-dimensional comparison engine"""

    @pytest.fixture
    def comparison_engine(self):
        config = {
            "dimension_weights": {
                "instruction": 0.4,
                "operand": 0.2,
                "control_flow": 0.25,
                "data_flow": 0.15,
            }
        }
        return MultiDimensionalComparison(config)

    @pytest.mark.asyncio
    async def test_identical_bytecodes(self, comparison_engine):
        """Test comparison of identical bytecodes"""
        bytecode = "6080604052348015600f57600080fd5b50"

        result = await comparison_engine.compute_similarity(bytecode, bytecode)

        assert result["final_score"] == 1.0
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_different_bytecodes(self, comparison_engine):
        """Test comparison of different bytecodes"""
        bytecode1 = "6080604052348015600f57600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b50"

        result = await comparison_engine.compute_similarity(bytecode1, bytecode2)

        assert 0.0 <= result["final_score"] <= 1.0
        assert "dimension_scores" in result
        assert len(result["dimension_scores"]) == 4

    @pytest.mark.asyncio
    async def test_empty_bytecodes(self, comparison_engine):
        """Test comparison of empty bytecodes"""
        result = await comparison_engine.compute_similarity("", "")

        assert result["final_score"] >= 0.0
        assert "confidence" in result


class TestSimilarityEngine:
    """Test main similarity engine"""

    @pytest.fixture
    async def engine(self):
        config = {
            "threshold": 0.7,
            "top_k": 10,
            "use_gpu": False,  # Use CPU for tests
            "cache_size": 100,
        }
        engine = SimilarityEngine(config)
        yield engine
        await engine.cleanup()

    @pytest.mark.asyncio
    async def test_compare_bytecodes(self, engine):
        """Test bytecode comparison"""
        bytecode1 = "6080604052348015600f57600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b50"

        result = await engine.compare_bytecodes(
            bytecode1, bytecode2, use_neural_network=False
        )

        assert hasattr(result, "similarity_score")
        assert hasattr(result, "confidence")
        assert hasattr(result, "processing_time")
        assert 0.0 <= result.similarity_score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time > 0.0

    @pytest.mark.asyncio
    async def test_index_bytecode(self, engine):
        """Test bytecode indexing"""
        bytecode = "6080604052348015600f57600080fd5b50"
        metadata = {"name": "test_contract", "type": "constructor"}

        bytecode_hash = await engine.index_bytecode(bytecode, metadata)

        assert bytecode_hash is not None
        assert len(bytecode_hash) > 0
        assert isinstance(bytecode_hash, str)

    @pytest.mark.asyncio
    async def test_find_similar_bytecode(self, engine):
        """Test similarity search"""
        # First index some bytecodes
        test_bytecodes = [
            ("6080604052348015600f57600080fd5b50", {"name": "test1"}),
            ("608060405234801561001057600080fd5b50", {"name": "test2"}),
            ("6080604052600436106100295760003560e01c", {"name": "test3"}),
        ]

        for bytecode, metadata in test_bytecodes:
            await engine.index_bytecode(bytecode, metadata)

        # Search for similar bytecodes
        query = "6080604052348015600f57600080fd5b50"
        results = await engine.find_similar_bytecode(query, top_k=5, min_similarity=0.1)

        assert isinstance(results, list)
        assert len(results) <= 5

        for result in results:
            assert hasattr(result, "bytecode_hash")
            assert hasattr(result, "similarity_score")
            assert hasattr(result, "confidence")

    @pytest.mark.asyncio
    async def test_batch_index_bytecodes(self, engine):
        """Test batch indexing"""
        bytecode_pairs = [
            ("6080604052348015600f57600080fd5b50", {"name": "batch_test1"}),
            ("608060405234801561001057600080fd5b50", {"name": "batch_test2"}),
            ("6080604052600436106100295760003560e01c", {"name": "batch_test3"}),
        ]

        hashes = await engine.batch_index_bytecodes(bytecode_pairs)

        assert isinstance(hashes, list)
        assert len(hashes) == len(bytecode_pairs)
        assert all(isinstance(h, str) for h in hashes)

    @pytest.mark.asyncio
    async def test_engine_stats(self, engine):
        """Test engine statistics"""
        # Index some data first
        await engine.index_bytecode(
            "6080604052348015600f57600080fd5b50", {"name": "stats_test"}
        )

        stats = engine.get_engine_stats()

        assert "total_indexed_bytecodes" in stats
        assert "cache_size" in stats
        assert "device" in stats
        assert "model_loaded" in stats
        assert "metrics" in stats
        assert stats["total_indexed_bytecodes"] >= 1

    @pytest.mark.asyncio
    async def test_cache_functionality(self, engine):
        """Test caching functionality"""
        bytecode1 = "6080604052348015600f57600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b50"

        # First comparison
        result1 = await engine.compare_bytecodes(
            bytecode1, bytecode2, use_neural_network=False
        )

        # Second comparison (should use cache)
        result2 = await engine.compare_bytecodes(
            bytecode1, bytecode2, use_neural_network=False
        )

        # Results should be identical
        assert result1.similarity_score == result2.similarity_score
        assert result1.confidence == result2.confidence

        # Clear cache and test
        engine.clear_cache()
        stats = engine.get_engine_stats()
        assert stats["cache_size"] == 0


# Integration tests
class TestIntegration:
    """Integration tests for the complete system"""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Initialize engine
        engine = SimilarityEngine()

        try:
            # Index some bytecodes
            bytecodes = [
                (
                    "6080604052348015600f57600080fd5b50",
                    {"contract": "TestContract1", "function": "constructor"},
                ),
                (
                    "608060405234801561001057600080fd5b50",
                    {"contract": "TestContract2", "function": "constructor"},
                ),
                (
                    "6080604052600436106100295760003560e01c",
                    {"contract": "TestContract3", "function": "dispatcher"},
                ),
            ]

            hashes = await engine.batch_index_bytecodes(bytecodes)
            assert len(hashes) == 3

            # Compare bytecodes
            comparison_result = await engine.compare_bytecodes(
                bytecodes[0][0], bytecodes[1][0], use_neural_network=False
            )
            assert comparison_result.similarity_score >= 0.0

            # Search for similar bytecodes
            search_results = await engine.find_similar_bytecode(
                bytecodes[0][0], top_k=5, min_similarity=0.1
            )
            assert len(search_results) <= 5

            # Check engine stats
            stats = engine.get_engine_stats()
            assert stats["total_indexed_bytecodes"] >= 3

        finally:
            await engine.cleanup()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
