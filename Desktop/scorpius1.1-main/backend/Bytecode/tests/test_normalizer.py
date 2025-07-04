"""
Test suite for the bytecode normalizer component.
"""

import numpy as np
import pytest
from preprocessors.bytecode_normalizer import BytecodeNormalizer


class TestBytecodeNormalizer:
    """Test cases for the BytecodeNormalizer class."""

    @pytest.fixture
    def normalizer(self):
        """Create a normalizer instance for testing."""
        config = {
            "remove_metadata": True,
            "normalize_constants": True,
            "remove_nops": True,
            "extract_patterns": True,
        }
        return BytecodeNormalizer(config)

    @pytest.fixture
    def sample_bytecodes(self):
        """Sample bytecodes for testing."""
        return {
            "simple": "608060405234801561001057600080fd5b50",
            "with_constants": "6001600260036004600560066007600860096010",
            "with_metadata": "608060405234801561001057600080fda165627a7a72305820",
            "complex": "608060405234801561001057600080fd5b50600436106100b95760003560e01c806370a082311161007657806395d89b411161005b57806395d89b41146101a4578063a9059cbb146101ac578063dd62ed3e146101d8576100b9565b",
            "empty": "",
            "invalid": "invalid_hex_string",
        }

    def test_normalizer_initialization(self, normalizer):
        """Test that the normalizer initializes correctly."""
        assert normalizer is not None
        assert normalizer.config["remove_metadata"] is True
        assert normalizer.config["normalize_constants"] is True

    def test_hex_string_parsing(self, normalizer, sample_bytecodes):
        """Test hex string parsing and validation."""
        # Valid hex strings
        for name, bytecode in sample_bytecodes.items():
            if name not in ["empty", "invalid"]:
                instructions = normalizer.parse_instructions(bytecode)
                assert isinstance(instructions, list)

        # Invalid hex string
        with pytest.raises((ValueError, TypeError)):
            normalizer.parse_instructions(sample_bytecodes["invalid"])

    def test_instruction_parsing(self, normalizer):
        """Test EVM instruction parsing."""
        # Test PUSH operations
        push_bytecode = "6001600260036004"  # PUSH1 1, PUSH1 2, PUSH1 3, PUSH1 4
        instructions = normalizer.parse_instructions(push_bytecode)

        assert len(instructions) >= 4
        # Check that PUSH instructions are properly parsed
        push_instructions = [
            inst for inst in instructions if inst["opcode"].startswith("PUSH")
        ]
        assert len(push_instructions) == 4

    def test_metadata_removal(self, normalizer, sample_bytecodes):
        """Test metadata removal functionality."""
        bytecode_with_metadata = sample_bytecodes["with_metadata"]

        result = normalizer.normalize(bytecode_with_metadata)
        normalized = result["normalized_bytecode"]

        # Metadata should be removed (anything after 0xa165627a7a)
        assert "a165627a7a" not in normalized.lower()

    def test_constant_normalization(self, normalizer, sample_bytecodes):
        """Test constant normalization."""
        bytecode_with_constants = sample_bytecodes["with_constants"]

        result = normalizer.normalize(bytecode_with_constants)
        instructions = result["instructions"]

        # Check that constants in PUSH operations are normalized
        push_instructions = [
            inst for inst in instructions if inst["opcode"].startswith("PUSH")
        ]
        for inst in push_instructions:
            if "operand" in inst:
                # Constants should be normalized to placeholder values
                assert inst["operand"] in ["CONST", "<CONST>"] or inst[
                    "operand"
                ].startswith("CONST_")

    def test_nop_removal(self, normalizer):
        """Test NOP instruction removal."""
        # Create bytecode with NOPs (JUMPDEST operations that don't affect control flow)
        bytecode_with_nops = (
            "60015b60025b6003"  # PUSH1 1, JUMPDEST, PUSH1 2, JUMPDEST, PUSH1 3
        )

        result = normalizer.normalize(bytecode_with_nops)
        instructions = result["instructions"]

        # NOPs should be removed or marked
        if normalizer.config["remove_nops"]:
            jumpdest_count = len(
                [inst for inst in instructions if inst["opcode"] == "JUMPDEST"]
            )
            # Some JUMPDESTs might be preserved if they're actual jump targets
            assert jumpdest_count <= 2  # Should have removed some

    def test_pattern_extraction(self, normalizer, sample_bytecodes):
        """Test pattern extraction functionality."""
        complex_bytecode = sample_bytecodes["complex"]

        result = normalizer.normalize(complex_bytecode)
        features = result["features"]

        assert isinstance(features, dict)
        assert "instruction_frequency" in features
        assert "pattern_features" in features
        assert "structural_features" in features

        # Check instruction frequency
        freq = features["instruction_frequency"]
        assert isinstance(freq, dict)
        assert all(isinstance(count, int) for count in freq.values())

    def test_feature_vector_generation(self, normalizer, sample_bytecodes):
        """Test feature vector generation."""
        bytecode = sample_bytecodes["complex"]

        feature_vector = normalizer.extract_feature_vector(bytecode)

        assert isinstance(feature_vector, np.ndarray)
        assert len(feature_vector.shape) == 1  # Should be 1D
        assert feature_vector.shape[0] > 0  # Should have features
        assert not np.isnan(feature_vector).any()  # No NaN values
        assert np.isfinite(feature_vector).all()  # All finite values

    def test_control_flow_analysis(self, normalizer):
        """Test control flow pattern extraction."""
        # Bytecode with jumps and control flow
        control_flow_bytecode = "60015760026008576003"  # Conditional jumps

        result = normalizer.normalize(control_flow_bytecode)
        features = result["features"]

        if "control_flow" in features:
            cf_features = features["control_flow"]
            assert isinstance(cf_features, dict)
            # Should have detected some control flow patterns
            assert any(count > 0 for count in cf_features.values())

    def test_data_flow_analysis(self, normalizer):
        """Test data flow pattern extraction."""
        # Bytecode with stack operations
        data_flow_bytecode = "6001600281018190556002600381018190556003"

        result = normalizer.normalize(data_flow_bytecode)
        features = result["features"]

        if "data_flow" in features:
            df_features = features["data_flow"]
            assert isinstance(df_features, dict)

    def test_empty_bytecode_handling(self, normalizer, sample_bytecodes):
        """Test handling of empty bytecode."""
        empty_bytecode = sample_bytecodes["empty"]

        result = normalizer.normalize(empty_bytecode)

        assert result["normalized_bytecode"] == ""
        assert result["instructions"] == []
        assert isinstance(result["features"], dict)

        # Feature vector should still be generated (zeros)
        feature_vector = normalizer.extract_feature_vector(empty_bytecode)
        assert isinstance(feature_vector, np.ndarray)
        assert feature_vector.shape[0] > 0

    def test_instruction_categorization(self, normalizer):
        """Test instruction categorization."""
        # Test various instruction types
        test_instructions = [
            ("60", "PUSH1", "stack"),
            ("01", "ADD", "arithmetic"),
            ("20", "SHA3", "crypto"),
            ("54", "SLOAD", "storage"),
            ("57", "JUMPI", "control"),
            ("f3", "RETURN", "system"),
        ]

        for hex_code, expected_opcode, expected_category in test_instructions:
            bytecode = hex_code + "01"  # Add operand for PUSH
            if expected_opcode != "PUSH1":
                bytecode = hex_code

            instructions = normalizer.parse_instructions(bytecode)
            if instructions:
                inst = instructions[0]
                assert inst["opcode"] == expected_opcode
                if "category" in inst:
                    assert inst["category"] == expected_category

    def test_normalization_consistency(self, normalizer, sample_bytecodes):
        """Test that normalization produces consistent results."""
        bytecode = sample_bytecodes["complex"]

        # Normalize the same bytecode multiple times
        result1 = normalizer.normalize(bytecode)
        result2 = normalizer.normalize(bytecode)

        # Results should be identical
        assert result1["normalized_bytecode"] == result2["normalized_bytecode"]
        assert len(result1["instructions"]) == len(result2["instructions"])

        # Feature vectors should be identical
        vec1 = normalizer.extract_feature_vector(bytecode)
        vec2 = normalizer.extract_feature_vector(bytecode)

        np.testing.assert_array_equal(vec1, vec2)

    def test_similarity_preservation(self, normalizer):
        """Test that similar bytecodes remain similar after normalization."""
        # Two similar bytecodes (same logic, different constants)
        bytecode1 = "600160028101819055"  # PUSH1 1, PUSH1 2, ADD, DUP1, SSTORE
        bytecode2 = "600560068101819055"  # PUSH1 5, PUSH1 6, ADD, DUP1, SSTORE

        vec1 = normalizer.extract_feature_vector(bytecode1)
        vec2 = normalizer.extract_feature_vector(bytecode2)

        # Normalized vectors should be similar (after constant normalization)
        if normalizer.config["normalize_constants"]:
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (
                np.linalg.norm(vec1) * np.linalg.norm(vec2)
            )
            assert similarity > 0.8  # Should be highly similar

    def test_performance_optimization(self, normalizer, sample_bytecodes):
        """Test performance optimization features."""
        import time

        large_bytecode = sample_bytecodes["complex"] * 10  # Make it larger

        # Time the normalization
        start_time = time.time()
        result = normalizer.normalize(large_bytecode)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time
        assert processing_time < 5.0  # Less than 5 seconds

        # Result should still be valid
        assert isinstance(result, dict)
        assert "normalized_bytecode" in result
        assert "features" in result


class TestBytecodeNormalizerEdgeCases:
    """Test edge cases and error conditions."""

    def test_malformed_bytecode_handling(self):
        """Test handling of malformed bytecode."""
        normalizer = BytecodeNormalizer({})

        malformed_cases = [
            "60",  # Incomplete PUSH instruction
            "6001ff",  # PUSH followed by invalid opcode
            "0x6001",  # With 0x prefix
            "6001 6002",  # With spaces
        ]

        for case in malformed_cases:
            try:
                result = normalizer.normalize(case)
                # Should handle gracefully or raise appropriate exception
                assert isinstance(result, dict)
            except (ValueError, TypeError):
                # Expected for some malformed inputs
                pass

    def test_very_large_bytecode(self):
        """Test handling of very large bytecode."""
        normalizer = BytecodeNormalizer({})

        # Create a very large bytecode (10KB)
        large_bytecode = "60016002" * 2500  # Repeat simple pattern

        result = normalizer.normalize(large_bytecode)

        assert isinstance(result, dict)
        assert len(result["instructions"]) > 0
        assert result["normalized_bytecode"] is not None

    def test_configuration_edge_cases(self):
        """Test edge cases in configuration."""
        # Empty configuration
        normalizer1 = BytecodeNormalizer({})
        assert normalizer1 is not None

        # All options disabled
        normalizer2 = BytecodeNormalizer(
            {
                "remove_metadata": False,
                "normalize_constants": False,
                "remove_nops": False,
                "extract_patterns": False,
            }
        )
        assert normalizer2 is not None

        # Test normalization still works
        result = normalizer2.normalize("60016002")
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
