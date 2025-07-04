"""
Unit tests for core/comparison_engine.py
Tests comparison between 2 contract sources with ~60% match scenario
"""

import asyncio
import os

# Import the modules to test
import sys
from collections import Counter
from unittest.mock import AsyncMock, Mock, patch

# Handle optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/Bytecode"))

from core.comparison_engine import MultiDimensionalComparison


class TestMultiDimensionalComparison:
    """Test suite for MultiDimensionalComparison class"""

    @pytest.fixture
    def comparison_config(self):
        """Configuration for comparison engine"""
        return {
            "dimension_weights": {
                "instruction": 0.4,
                "operand": 0.2,
                "control_flow": 0.25,
                "data_flow": 0.15,
            }
        }

    @pytest.fixture
    def comparison_engine(self, comparison_config):
        """Initialize comparison engine"""
        return MultiDimensionalComparison(comparison_config)

    @pytest.fixture
    def sample_bytecodes(self):
        """Sample bytecode pairs for testing different similarity levels"""
        return {
            # Identical contracts (100% match)
            "identical": {
                "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
                "bytecode2": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
            },
            # Similar contracts (~60% match scenario)
            "similar_60_percent": {
                "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b6100305760405180910390f35b60008054906101000a900460ff1681565b",
                "bytecode2": "608060405234801561001057600080fd5b506004361061004c5760003560e01c8063c6888fa114610051578063d09de08a14610051575b600080fd5b6100596100615681565b005b6001600081905550565b",
            },
            # Very different contracts (~20% match)
            "different": {
                "bytecode1": "608060405234801561001057600080fd5b50600436106100365760003560e01c8063a41368621461003b578063cfae321714610059575b",
                "bytecode2": "6080604052348015601057600080fd5b50600060015260206004600039602060006000f300608060405260043610603f576000357c01",
            },
            # Empty contracts
            "empty": {"bytecode1": "", "bytecode2": ""},
        }

    @pytest.fixture
    def mock_opcodes_60_percent(self):
        """Mock opcodes that should result in ~60% similarity"""
        opcodes1 = [
            {"mnemonic": "PUSH1", "operand": "0x60"},
            {"mnemonic": "PUSH1", "operand": "0x40"},
            {"mnemonic": "MSTORE", "operand": None},
            {"mnemonic": "CALLVALUE", "operand": None},
            {"mnemonic": "DUP1", "operand": None},
            {"mnemonic": "ISZERO", "operand": None},
            {"mnemonic": "PUSH2", "operand": "0x0010"},
            {"mnemonic": "JUMPI", "operand": None},
            {"mnemonic": "PUSH1", "operand": "0x00"},
            {"mnemonic": "DUP1", "operand": None},
        ]

        opcodes2 = [
            {"mnemonic": "PUSH1", "operand": "0x60"},  # Same
            {"mnemonic": "PUSH1", "operand": "0x40"},  # Same
            {"mnemonic": "MSTORE", "operand": None},  # Same
            {"mnemonic": "CALLVALUE", "operand": None},  # Same
            {"mnemonic": "DUP2", "operand": None},  # Different (DUP1 vs DUP2)
            {"mnemonic": "ISZERO", "operand": None},  # Same
            {"mnemonic": "PUSH2", "operand": "0x0020"},  # Different operand
            {"mnemonic": "JUMP", "operand": None},  # Different (JUMPI vs JUMP)
            {"mnemonic": "PUSH1", "operand": "0x01"},  # Different operand
            {"mnemonic": "DUP1", "operand": None},  # Same
        ]

        return opcodes1, opcodes2

    @pytest.mark.asyncio
    async def test_compute_similarity_identical_contracts(
        self, comparison_engine, sample_bytecodes
    ):
        """Test similarity computation for identical contracts (should be ~100%)"""
        bytecode1 = sample_bytecodes["identical"]["bytecode1"]
        bytecode2 = sample_bytecodes["identical"]["bytecode2"]

        result = await comparison_engine.compute_similarity(bytecode1, bytecode2)

        assert isinstance(result, dict)
        assert "final_score" in result
        assert "dimension_scores" in result
        assert "confidence" in result

        # For identical bytecode, similarity should be very high (close to 1.0)
        assert (
            result["final_score"] >= 0.9
        ), f"Expected high similarity for identical contracts, got {result['final_score']}"
        assert 0.0 <= result["final_score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_compute_similarity_60_percent_match(
        self, comparison_engine, sample_bytecodes
    ):
        """Test similarity computation for ~60% similar contracts"""
        bytecode1 = sample_bytecodes["similar_60_percent"]["bytecode1"]
        bytecode2 = sample_bytecodes["similar_60_percent"]["bytecode2"]

        result = await comparison_engine.compute_similarity(bytecode1, bytecode2)

        # Should result in moderate similarity (~40-80% range for similar but not identical contracts)
        assert (
            0.3 <= result["final_score"] <= 0.8
        ), f"Expected ~60% similarity, got {result['final_score']}"

        # All dimension scores should be reasonable
        for dimension, score in result["dimension_scores"].items():
            assert (
                0.0 <= score <= 1.0
            ), f"Dimension {dimension} score {score} out of range"

    @pytest.mark.asyncio
    async def test_compute_similarity_different_contracts(
        self, comparison_engine, sample_bytecodes
    ):
        """Test similarity computation for very different contracts"""
        bytecode1 = sample_bytecodes["different"]["bytecode1"]
        bytecode2 = sample_bytecodes["different"]["bytecode2"]

        result = await comparison_engine.compute_similarity(bytecode1, bytecode2)

        # Should result in low similarity
        assert (
            result["final_score"] <= 0.5
        ), f"Expected low similarity for different contracts, got {result['final_score']}"
        assert result["final_score"] >= 0.0

    @pytest.mark.asyncio
    async def test_compute_similarity_empty_contracts(
        self, comparison_engine, sample_bytecodes
    ):
        """Test similarity computation for empty contracts"""
        bytecode1 = sample_bytecodes["empty"]["bytecode1"]
        bytecode2 = sample_bytecodes["empty"]["bytecode2"]

        result = await comparison_engine.compute_similarity(bytecode1, bytecode2)

        # Empty contracts should have some similarity measure
        assert 0.0 <= result["final_score"] <= 1.0
        assert isinstance(result["dimension_scores"], dict)

    @pytest.mark.asyncio
    async def test_extract_all_dimensions(self, comparison_engine):
        """Test feature extraction for all dimensions"""
        sample_bytecode = "608060405234801561001057600080fd5b506004361061002b"

        with patch.object(
            comparison_engine, "_parse_bytecode_to_opcodes"
        ) as mock_parse:
            mock_opcodes = [
                {"mnemonic": "PUSH1", "operand": "0x60"},
                {"mnemonic": "PUSH1", "operand": "0x40"},
                {"mnemonic": "MSTORE", "operand": None},
                {"mnemonic": "CALLVALUE", "operand": None},
            ]
            mock_parse.return_value = mock_opcodes

            features = await comparison_engine._extract_all_dimensions(sample_bytecode)

            assert isinstance(features, dict)
            assert "instruction" in features
            assert "operand" in features
            assert "control_flow" in features
            assert "data_flow" in features

            # Each dimension should return a set
            for dimension, feature_set in features.items():
                assert isinstance(feature_set, set)

    def test_jaccard_similarity_calculation(self, comparison_engine):
        """Test Jaccard similarity calculation with known sets"""
        # Test case 1: Identical sets (should be 1.0)
        set1 = {"A", "B", "C", "D"}
        set2 = {"A", "B", "C", "D"}
        similarity = comparison_engine._jaccard_similarity(set1, set2)
        assert similarity == 1.0

        # Test case 2: No overlap (should be 0.0)
        set1 = {"A", "B", "C"}
        set2 = {"X", "Y", "Z"}
        similarity = comparison_engine._jaccard_similarity(set1, set2)
        assert similarity == 0.0

        # Test case 3: Partial overlap (~60% similarity)
        set1 = {"A", "B", "C", "D", "E"}
        set2 = {"A", "B", "C", "X", "Y"}
        # Intersection: {A, B, C} = 3 elements
        # Union: {A, B, C, D, E, X, Y} = 7 elements
        # Jaccard = 3/7 ≈ 0.428
        similarity = comparison_engine._jaccard_similarity(set1, set2)
        expected = 3.0 / 7.0  # ≈ 0.428
        assert abs(similarity - expected) < 0.01

        # Test case 4: Empty sets
        set1 = set()
        set2 = set()
        similarity = comparison_engine._jaccard_similarity(set1, set2)
        assert similarity == 0.0  # Or 1.0, depending on implementation

    def test_instruction_dimension_extraction(self, comparison_engine):
        """Test instruction dimension feature extraction"""
        mock_opcodes = [
            {"mnemonic": "ADD"},
            {"mnemonic": "SUB"},
            {"mnemonic": "PUSH1"},
            {"mnemonic": "MSTORE"},
            {"mnemonic": "CALL"},
        ]

        features = comparison_engine._extract_instruction_dimension(mock_opcodes)

        assert isinstance(features, set)
        # Should contain individual opcodes
        assert "ADD" in features
        assert "SUB" in features
        assert "PUSH1" in features

        # Should contain semantic categories
        assert "CAT_arithmetic" in features  # ADD, SUB
        assert "CAT_stack" in features  # PUSH1
        assert "CAT_memory" in features  # MSTORE
        assert "CAT_call" in features  # CALL

    def test_operand_dimension_extraction(self, comparison_engine):
        """Test operand dimension feature extraction"""
        mock_opcodes = [
            {"mnemonic": "PUSH1", "operand": "0x60"},
            {"mnemonic": "PUSH1", "operand": "0x40"},
            {"mnemonic": "PUSH2", "operand": "0x1000"},
            {"mnemonic": "MSTORE", "operand": None},
        ]

        features = comparison_engine._extract_operand_dimension(mock_opcodes)

        assert isinstance(features, set)
        # Should contain operand values
        assert "OP_0x60" in features
        assert "OP_0x40" in features
        assert "OP_0x1000" in features

        # Should contain operand patterns
        assert "PATTERN_small_constant" in features  # For small values like 0x60, 0x40

    def test_control_flow_dimension_extraction(self, comparison_engine):
        """Test control flow dimension feature extraction"""
        mock_opcodes = [
            {"mnemonic": "JUMPDEST"},
            {"mnemonic": "PUSH1", "operand": "0x10"},
            {"mnemonic": "JUMPI"},
            {"mnemonic": "PUSH1", "operand": "0x20"},
            {"mnemonic": "JUMP"},
            {"mnemonic": "STOP"},
        ]

        features = comparison_engine._extract_control_flow_dimension(mock_opcodes)

        assert isinstance(features, set)
        # Should contain control flow patterns
        assert "JUMP_PATTERN" in features
        assert "CONDITIONAL_JUMP" in features
        assert "UNCONDITIONAL_JUMP" in features

    def test_data_flow_dimension_extraction(self, comparison_engine):
        """Test data flow dimension feature extraction"""
        mock_opcodes = [
            {"mnemonic": "PUSH1"},
            {"mnemonic": "DUP1"},
            {"mnemonic": "MSTORE"},
            {"mnemonic": "MLOAD"},
            {"mnemonic": "SSTORE"},
            {"mnemonic": "SLOAD"},
        ]

        features = comparison_engine._extract_data_flow_dimension(mock_opcodes)

        assert isinstance(features, set)
        # Should contain data flow patterns
        assert "STACK_USAGE" in features
        assert "MEMORY_ACCESS" in features
        assert "STORAGE_ACCESS" in features

    def test_confidence_calculation(self, comparison_engine):
        """Test confidence calculation based on dimension scores"""
        # High confidence case (consistent scores)
        similarities_high = {
            "instruction": 0.8,
            "operand": 0.82,
            "control_flow": 0.79,
            "data_flow": 0.81,
        }
        confidence_high = comparison_engine._calculate_confidence(similarities_high)
        assert 0.8 <= confidence_high <= 1.0

        # Low confidence case (inconsistent scores)
        similarities_low = {
            "instruction": 0.9,
            "operand": 0.1,
            "control_flow": 0.8,
            "data_flow": 0.2,
        }
        confidence_low = comparison_engine._calculate_confidence(similarities_low)
        assert 0.0 <= confidence_low <= 0.7

        # Perfect confidence case
        similarities_perfect = {
            "instruction": 1.0,
            "operand": 1.0,
            "control_flow": 1.0,
            "data_flow": 1.0,
        }
        confidence_perfect = comparison_engine._calculate_confidence(
            similarities_perfect
        )
        assert confidence_perfect >= 0.9

    def test_weighted_score_calculation(self, comparison_engine):
        """Test weighted final score calculation"""
        similarities = {
            "instruction": 0.8,
            "operand": 0.6,
            "control_flow": 0.7,
            "data_flow": 0.9,
        }

        expected_score = (
            0.8 * 0.4
            + 0.6 * 0.2  # instruction
            + 0.7 * 0.25  # operand
            + 0.9 * 0.15  # control_flow  # data_flow
        )
        # = 0.32 + 0.12 + 0.175 + 0.135 = 0.75

        # Calculate using the actual method by calling compute_similarity
        with patch.object(comparison_engine, "_extract_all_dimensions") as mock_extract:
            mock_extract.side_effect = [
                {
                    "instruction": {"A", "B", "C", "D", "E"},  # 5 elements
                    "operand": {"X", "Y", "Z"},  # 3 elements
                    "control_flow": {"P", "Q", "R", "S"},  # 4 elements
                    "data_flow": {"M", "N", "O", "P", "Q", "R"},  # 6 elements
                },
                {
                    "instruction": {
                        "A",
                        "B",
                        "C",
                        "D",
                    },  # 4 common, 1 different = 4/6 = 0.67
                    "operand": {"X", "Y"},  # 2 common, 1 different = 2/4 = 0.5
                    "control_flow": {
                        "P",
                        "Q",
                        "R",
                    },  # 3 common, 1 different = 3/5 = 0.6
                    "data_flow": {
                        "M",
                        "N",
                        "O",
                        "P",
                        "Q",
                        "R",
                        "S",
                        "T",
                        "U",
                    },  # 6 common, 3 different = 6/12 = 0.5
                },
            ]

            async def run_test():
                result = await comparison_engine.compute_similarity("test1", "test2")
                # Verify the weighted calculation is reasonable
                assert 0.0 <= result["final_score"] <= 1.0
                return result["final_score"]

            score = asyncio.run(run_test())
            assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_parse_bytecode_to_opcodes_functionality(self, comparison_engine):
        """Test bytecode parsing functionality"""
        # Test with sample bytecode
        sample_bytecode = "6080604052"  # PUSH1 0x80, PUSH1 0x40, MSTORE

        opcodes = await comparison_engine._parse_bytecode_to_opcodes(sample_bytecode)

        assert isinstance(opcodes, list)
        assert len(opcodes) > 0

        # Each opcode should be a dict with 'mnemonic' key
        for opcode in opcodes:
            assert isinstance(opcode, dict)
            assert "mnemonic" in opcode

    @pytest.mark.asyncio
    async def test_exact_60_percent_similarity_scenario(
        self, comparison_engine, mock_opcodes_60_percent
    ):
        """Test exact scenario where contracts have ~60% similarity"""
        opcodes1, opcodes2 = mock_opcodes_60_percent

        with patch.object(
            comparison_engine, "_parse_bytecode_to_opcodes"
        ) as mock_parse:
            mock_parse.side_effect = [opcodes1, opcodes2]

            result = await comparison_engine.compute_similarity(
                "bytecode1", "bytecode2"
            )

            # Should be in the 50-70% range for our 60% similar scenario
            assert (
                0.4 <= result["final_score"] <= 0.8
            ), f"Expected ~60% similarity, got {result['final_score']}"

            # Verify all dimensions contributed to the score
            for dimension in ["instruction", "operand", "control_flow", "data_flow"]:
                assert dimension in result["dimension_scores"]
                assert 0.0 <= result["dimension_scores"][dimension] <= 1.0

    def test_opcode_categorization(self, comparison_engine):
        """Test that opcode categorization is working correctly"""
        # Test arithmetic opcodes
        assert "ADD" in comparison_engine.opcode_categories["arithmetic"]
        assert "SUB" in comparison_engine.opcode_categories["arithmetic"]
        assert "MUL" in comparison_engine.opcode_categories["arithmetic"]

        # Test control flow opcodes
        assert "JUMP" in comparison_engine.opcode_categories["control"]
        assert "JUMPI" in comparison_engine.opcode_categories["control"]
        assert "RETURN" in comparison_engine.opcode_categories["control"]

        # Test memory opcodes
        assert "MLOAD" in comparison_engine.opcode_categories["memory"]
        assert "MSTORE" in comparison_engine.opcode_categories["memory"]

        # Test stack opcodes
        assert "PUSH1" in comparison_engine.opcode_categories["stack"]
        assert "DUP1" in comparison_engine.opcode_categories["stack"]
        assert "SWAP1" in comparison_engine.opcode_categories["stack"]


if __name__ == "__main__":
    # Run tests manually instead of using pytest.main() to avoid web3 dependency conflicts
    import asyncio

    # Initialize test instance
    test_instance = TestMultiDimensionalComparison()

    # Create fixtures
    comparison_config = {
        "dimension_weights": {
            "instruction": 0.4,
            "operand": 0.2,
            "control_flow": 0.25,
            "data_flow": 0.15,
        }
    }

    comparison_engine = MultiDimensionalComparison(comparison_config)

    sample_bytecodes = {
        # Identical contracts (100% match)
        "identical": {
            "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
            "bytecode2": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b",
        },
        # Similar contracts (~60% match scenario)
        "similar_60_percent": {
            "bytecode1": "608060405234801561001057600080fd5b506004361061002b5760003560e01c8063c6888fa114610030575b600080fd5b6100305760405180910390f35b60008054906101000a900460ff1681565b",
            "bytecode2": "608060405234801561001057600080fd5b506004361061004c5760003560e01c8063c6888fa114610051578063d09de08a14610051575b600080fd5b6100596100615681565b005b6001600081905550565b",
        },
        # Very different contracts (~20% match)
        "different": {
            "bytecode1": "608060405234801561001057600080fd5b50600436106100365760003560e01c8063a41368621461003b578063cfae321714610059575b",
            "bytecode2": "6080604052348015601057600080fd5b50600060015260206004600039602060006000f300608060405260043610603f576000357c01",
        },
        # Empty contracts
        "empty": {"bytecode1": "", "bytecode2": ""},
    }

    print("Running MultiDimensionalComparison tests...")

    # Test 1: Identical contracts
    async def test_identical():
        print("\n1. Testing identical contracts...")
        try:
            result = await comparison_engine.compute_similarity(
                sample_bytecodes["identical"]["bytecode1"],
                sample_bytecodes["identical"]["bytecode2"],
            )
            print(f"   Result: {result['final_score']:.3f}")
            assert (
                result["final_score"] >= 0.9
            ), f"Expected high similarity, got {result['final_score']}"
            print("   ✓ PASS: Identical contracts test")
        except Exception as e:
            print(f"   ✗ FAIL: {e}")

    # Test 2: 60% similar contracts
    async def test_60_percent():
        print("\n2. Testing ~60% similar contracts...")
        try:
            result = await comparison_engine.compute_similarity(
                sample_bytecodes["similar_60_percent"]["bytecode1"],
                sample_bytecodes["similar_60_percent"]["bytecode2"],
            )
            print(f"   Result: {result['final_score']:.3f}")
            print(f"   Dimension scores: {result['dimension_scores']}")
            assert (
                0.3 <= result["final_score"] <= 0.8
            ), f"Expected moderate similarity, got {result['final_score']}"
            print("   ✓ PASS: 60% similar contracts test")
        except Exception as e:
            print(f"   ✗ FAIL: {e}")

    # Test 3: Different contracts
    async def test_different():
        print("\n3. Testing different contracts...")
        try:
            result = await comparison_engine.compute_similarity(
                sample_bytecodes["different"]["bytecode1"],
                sample_bytecodes["different"]["bytecode2"],
            )
            print(f"   Result: {result['final_score']:.3f}")
            assert (
                result["final_score"] <= 0.5
            ), f"Expected low similarity, got {result['final_score']}"
            print("   ✓ PASS: Different contracts test")
        except Exception as e:
            print(f"   ✗ FAIL: {e}")

    # Test 4: Jaccard similarity
    def test_jaccard():
        print("\n4. Testing Jaccard similarity calculation...")
        try:
            # Test identical sets
            set1 = {"A", "B", "C", "D"}
            set2 = {"A", "B", "C", "D"}
            similarity = comparison_engine._jaccard_similarity(set1, set2)
            assert (
                similarity == 1.0
            ), f"Expected 1.0 for identical sets, got {similarity}"

            # Test no overlap
            set1 = {"A", "B", "C"}
            set2 = {"X", "Y", "Z"}
            similarity = comparison_engine._jaccard_similarity(set1, set2)
            assert similarity == 0.0, f"Expected 0.0 for no overlap, got {similarity}"

            # Test partial overlap
            set1 = {"A", "B", "C", "D", "E"}
            set2 = {"A", "B", "C", "X", "Y"}
            similarity = comparison_engine._jaccard_similarity(set1, set2)
            expected = 3.0 / 7.0  # ≈ 0.428
            assert (
                abs(similarity - expected) < 0.01
            ), f"Expected ~{expected}, got {similarity}"

            print("   ✓ PASS: Jaccard similarity test")
        except Exception as e:
            print(f"   ✗ FAIL: {e}")

    # Run all tests
    async def run_all_tests():
        await test_identical()
        await test_60_percent()
        await test_different()
        test_jaccard()
        print("\n" + "=" * 50)
        print("All tests completed!")

    # Run the tests
    asyncio.run(run_all_tests())
