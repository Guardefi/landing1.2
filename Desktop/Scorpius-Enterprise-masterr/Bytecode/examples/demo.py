#!/usr/bin/env python3
"""
Example script demonstrating SCORPIUS bytecode similarity analysis.

This script shows how to use the various components of the SCORPIUS engine
for bytecode similarity detection and analysis.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.comparison_engine import BytecodeComparisonEngine
from core.similarity_engine import SimilarityEngine
from preprocessors.bytecode_normalizer import BytecodeNormalizer


def load_sample_contracts():
    """Load sample contracts from the examples directory."""
    sample_file = Path(__file__).parent / "sample_contracts.json"
    with open(sample_file, "r") as f:
        return json.load(f)


def example_basic_comparison():
    """Example 1: Basic bytecode comparison."""
    print("🔍 Example 1: Basic Bytecode Comparison")
    print("=" * 50)

    # Load configuration
    config = {
        "similarity_threshold": 0.8,
        "batch_size": 32,
        "use_gpu": False,
        "collect_metrics": True,
    }

    # Initialize engine
    engine = SimilarityEngine(config)

    # Load sample contracts
    contracts = load_sample_contracts()

    # Compare two similar ERC20 contracts
    bytecode1 = contracts["erc20_token_standard"]
    bytecode2 = contracts["erc20_token_optimized"]

    print("Comparing ERC20 contracts:")
    print(f"Contract 1 length: {len(bytecode1)} characters")
    print(f"Contract 2 length: {len(bytecode2)} characters")

    # Perform comparison
    result = engine.compute_similarity(bytecode1, bytecode2)

    print("\nResults:")
    print(f"Overall Similarity: {result['overall_similarity']:.4f}")
    print(f"Jaccard Similarity: {result.get('jaccard_similarity', 'N/A')}")
    print(f"N-gram Similarity: {result.get('ngram_similarity', 'N/A')}")
    print(f"Structural Similarity: {result.get('structural_similarity', 'N/A')}")
    print(f"Are Similar: {result.get('is_similar', 'N/A')}")

    if "metrics" in result:
        print(f"Computation Time: {result['metrics']['computation_time']:.4f}s")

    print("\n")


def example_batch_analysis():
    """Example 2: Batch analysis of multiple contracts."""
    print("📊 Example 2: Batch Analysis")
    print("=" * 50)

    # Initialize engine
    config = {"similarity_threshold": 0.7, "batch_size": 16}
    engine = SimilarityEngine(config)

    # Load sample contracts
    contracts = load_sample_contracts()
    contract_names = list(contracts.keys())

    # Prepare all pairwise comparisons
    pairs = []
    pair_names = []

    for i, name1 in enumerate(contract_names):
        for j, name2 in enumerate(contract_names[i + 1 :], i + 1):
            pairs.append((contracts[name1], contracts[name2]))
            pair_names.append((name1, name2))

    print(f"Analyzing {len(pairs)} contract pairs...")

    # Perform batch comparison
    results = engine.compute_batch_similarity(pairs)

    # Display results
    print("\nBatch Analysis Results:")
    print("-" * 80)
    print(f"{'Pair':<40} {'Similarity':<12} {'Similar':<8}")
    print("-" * 80)

    for (name1, name2), result in zip(pair_names, results):
        pair_name = f"{name1[:15]}... vs {name2[:15]}..."
        similarity = f"{result['overall_similarity']:.4f}"
        is_similar = "Yes" if result.get("is_similar", False) else "No"
        print(f"{pair_name:<40} {similarity:<12} {is_similar:<8}")

    print("\n")


def example_feature_extraction():
    """Example 3: Feature extraction and analysis."""
    print("🧠 Example 3: Feature Extraction")
    print("=" * 50)

    # Initialize normalizer
    config = {
        "remove_metadata": True,
        "normalize_constants": True,
        "remove_nops": True,
        "extract_patterns": True,
    }
    normalizer = BytecodeNormalizer(config)

    # Load a contract
    contracts = load_sample_contracts()
    bytecode = contracts["simple_storage"]

    print("Analyzing Simple Storage Contract:")
    print(f"Original bytecode length: {len(bytecode)} characters")

    # Normalize and extract features
    normalized = normalizer.normalize(bytecode)
    feature_vector = normalizer.extract_feature_vector(bytecode)

    print(
        f"Normalized bytecode length: {len(normalized['normalized_bytecode'])} characters"
    )
    print(f"Number of instructions: {len(normalized['instructions'])}")
    print(f"Feature vector dimensions: {feature_vector.shape[0]}")

    # Show instruction breakdown
    print("\nInstruction Analysis:")
    opcodes = [inst["opcode"] for inst in normalized["instructions"]]
    opcode_counts = {}
    for opcode in opcodes:
        opcode_counts[opcode] = opcode_counts.get(opcode, 0) + 1

    # Show top opcodes
    sorted_opcodes = sorted(opcode_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 opcodes:")
    for opcode, count in sorted_opcodes[:10]:
        print(f"  {opcode}: {count}")

    # Show pattern features
    if "pattern_features" in normalized["features"]:
        patterns = normalized["features"]["pattern_features"]
        print(f"\nPattern Features: {len(patterns)} detected")
        for pattern, count in list(patterns.items())[:5]:
            print(f"  {pattern}: {count}")

    print("\n")


def example_similarity_search():
    """Example 4: Similarity search."""
    print("🔎 Example 4: Similarity Search")
    print("=" * 50)

    # Initialize engine
    config = {"similarity_threshold": 0.6}
    engine = SimilarityEngine(config)

    # Load contracts
    contracts = load_sample_contracts()

    # Use simple storage as query
    query_bytecode = contracts["simple_storage"]
    print("Query: Simple Storage Contract")

    # Search against all other contracts
    results = []
    for name, bytecode in contracts.items():
        if name != "simple_storage":
            similarity_result = engine.compute_similarity(query_bytecode, bytecode)
            results.append(
                {
                    "name": name,
                    "similarity": similarity_result["overall_similarity"],
                    "is_similar": similarity_result.get("is_similar", False),
                }
            )

    # Sort by similarity
    results.sort(key=lambda x: x["similarity"], reverse=True)

    print("\nSearch Results (sorted by similarity):")
    print("-" * 60)
    print(f"{'Contract':<25} {'Similarity':<12} {'Similar':<8}")
    print("-" * 60)

    for result in results:
        name = result["name"][:24]
        similarity = f"{result['similarity']:.4f}"
        is_similar = "Yes" if result["is_similar"] else "No"
        print(f"{name:<25} {similarity:<12} {is_similar:<8}")

    print("\n")


def example_advanced_comparison():
    """Example 5: Advanced multi-dimensional comparison."""
    print("⚡ Example 5: Advanced Multi-dimensional Comparison")
    print("=" * 50)

    # Initialize comparison engine directly
    config = {
        "jaccard_threshold": 0.8,
        "ngram_size": 4,
        "use_weighted_jaccard": True,
        "structural_weight": 0.3,
    }
    comparison_engine = BytecodeComparisonEngine(config)

    # Load contracts
    contracts = load_sample_contracts()
    bytecode1 = contracts["erc20_token_standard"]
    bytecode2 = contracts["erc20_token_optimized"]

    print("Multi-dimensional comparison of ERC20 variants:")

    # Perform detailed comparison
    result = comparison_engine.multi_dimensional_compare(bytecode1, bytecode2)

    print("\nDetailed Similarity Metrics:")
    print("-" * 40)
    for metric, value in result.items():
        if "similarity" in metric:
            print(f"{metric.replace('_', ' ').title():<25}: {value:.4f}")

    # Show individual comparisons
    print("\nIndividual Analysis:")
    print(
        f"Jaccard Similarity: {comparison_engine.jaccard_similarity(bytecode1, bytecode2):.4f}"
    )
    print(
        f"N-gram Similarity:  {comparison_engine.ngram_similarity(bytecode1, bytecode2):.4f}"
    )
    print(
        f"Structural Similarity: {comparison_engine.structural_similarity(bytecode1, bytecode2):.4f}"
    )
    print(
        f"Opcode Frequency Similarity: {comparison_engine.opcode_frequency_similarity(bytecode1, bytecode2):.4f}"
    )

    print("\n")


def example_performance_analysis():
    """Example 6: Performance analysis."""
    print("⚡ Example 6: Performance Analysis")
    print("=" * 50)

    import time

    # Initialize engine with metrics collection
    config = {"similarity_threshold": 0.8, "collect_metrics": True, "batch_size": 32}
    engine = SimilarityEngine(config)

    # Load contracts
    contracts = load_sample_contracts()
    contract_list = list(contracts.items())

    # Single comparison timing
    print("Single Comparison Performance:")
    bytecode1, bytecode2 = contract_list[0][1], contract_list[1][1]

    start_time = time.time()
    result = engine.compute_similarity(bytecode1, bytecode2)
    single_time = time.time() - start_time

    print(f"Single comparison time: {single_time:.4f} seconds")
    if "metrics" in result:
        print(
            f"Engine reported time: {result['metrics']['computation_time']:.4f} seconds"
        )
        print(f"Memory usage: {result['metrics'].get('memory_usage', 'N/A')} MB")

    # Batch comparison timing
    print("\nBatch Comparison Performance:")
    pairs = [
        (contract_list[i][1], contract_list[j][1])
        for i in range(len(contract_list))
        for j in range(i + 1, len(contract_list))
    ]

    start_time = time.time()
    engine.compute_batch_similarity(pairs)
    batch_time = time.time() - start_time

    print(f"Batch processing time: {batch_time:.4f} seconds")
    print(f"Number of pairs: {len(pairs)}")
    print(f"Average time per pair: {batch_time/len(pairs):.4f} seconds")
    print(f"Throughput: {len(pairs)/batch_time:.2f} comparisons/second")

    print("\n")


def main():
    """Run all examples."""
    print("🚀 SCORPIUS Bytecode Similarity Engine - Examples")
    print("=" * 70)
    print("This script demonstrates various features of the SCORPIUS engine.")
    print("=" * 70)
    print()

    try:
        # Run all examples
        example_basic_comparison()
        example_batch_analysis()
        example_feature_extraction()
        example_similarity_search()
        example_advanced_comparison()
        example_performance_analysis()

        print("✅ All examples completed successfully!")
        print("\nTo learn more about SCORPIUS:")
        print("- Check the README.md for detailed documentation")
        print("- Run 'python scorpius_cli.py --help' for CLI usage")
        print("- Explore the API documentation at /docs when serving")
        print("- Review the test cases in the tests/ directory")

    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
