#!/usr/bin/env python3
"""
Comprehensive Benchmarking Script
Performance evaluation and testing for SCORPIUS engine
"""

import argparse
import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import yaml
from core.similarity_engine import SimilarityEngine
from utils.metrics import BenchmarkSuite, PerformanceMonitor, SimilarityMetrics

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveBenchmark:
    """Comprehensive benchmarking suite for the similarity engine"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.engine = None
        self.monitor = PerformanceMonitor()
        self.results = {}

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            return {
                "similarity_engine": {"threshold": 0.7, "top_k": 10, "use_gpu": True}
            }

    async def initialize_engine(self):
        """Initialize the similarity engine"""
        logger.info("Initializing similarity engine...")
        self.engine = SimilarityEngine(self.config.get("similarity_engine", {}))

        # Index some test bytecodes
        await self._setup_test_data()

        logger.info("Engine initialization complete")

    async def _setup_test_data(self):
        """Setup test data for benchmarking"""
        test_bytecodes = [
            (
                "6080604052348015600f57600080fd5b50",
                {"name": "test1", "type": "constructor"},
            ),
            (
                "608060405234801561001057600080fd5b50",
                {"name": "test2", "type": "constructor"},
            ),
            (
                "6080604052600436106100295760003560e01c",
                {"name": "test3", "type": "dispatcher"},
            ),
            ("608060405260043610610029576000", {"name": "test4", "type": "dispatcher"}),
            (
                "6080604052348015600f57600080fd5b506004361061003b5760003560e01c",
                {"name": "test5", "type": "complex"},
            ),
        ]

        await self.engine.batch_index_bytecodes(test_bytecodes)
        logger.info(f"Indexed {len(test_bytecodes)} test bytecodes")

    async def run_similarity_benchmark(self) -> Dict:
        """Benchmark similarity comparison performance"""
        logger.info("Running similarity comparison benchmark...")

        test_pairs = [
            (
                "6080604052348015600f57600080fd5b50",
                "608060405234801561001057600080fd5b50",
            ),
            (
                "6080604052600436106100295760003560e01c",
                "608060405260043610610029576000",
            ),
            (
                "6080604052348015600f57600080fd5b50",
                "6080604052600436106100295760003560e01c",
            ),
        ]

        results = {
            "total_comparisons": 0,
            "total_time": 0,
            "comparison_times": [],
            "similarity_scores": [],
            "average_time": 0,
            "throughput": 0,
        }

        self.monitor.start_measurement()

        for bytecode1, bytecode2 in test_pairs:
            start_time = time.time()

            result = await self.engine.compare_bytecodes(bytecode1, bytecode2)

            comparison_time = time.time() - start_time
            results["comparison_times"].append(comparison_time)
            results["similarity_scores"].append(result.similarity_score)
            results["total_comparisons"] += 1

        metrics = self.monitor.end_measurement("similarity_benchmark")
        results["total_time"] = metrics["duration"]
        results["average_time"] = sum(results["comparison_times"]) / len(
            results["comparison_times"]
        )
        results["throughput"] = results["total_comparisons"] / results["total_time"]

        logger.info(
            f"Similarity benchmark completed: {results['total_comparisons']} comparisons in {results['total_time']:.2f}s"
        )

        return results

    async def run_search_benchmark(self) -> Dict:
        """Benchmark similarity search performance"""
        logger.info("Running similarity search benchmark...")

        query_bytecode = "6080604052348015600f57600080fd5b50"

        results = {
            "total_searches": 0,
            "total_time": 0,
            "search_times": [],
            "results_counts": [],
            "average_time": 0,
            "throughput": 0,
        }

        # Run multiple searches
        num_searches = 10

        self.monitor.start_measurement()

        for i in range(num_searches):
            start_time = time.time()

            search_results = await self.engine.find_similar_bytecode(
                query_bytecode, top_k=5, min_similarity=0.1
            )

            search_time = time.time() - start_time
            results["search_times"].append(search_time)
            results["results_counts"].append(len(search_results))
            results["total_searches"] += 1

        metrics = self.monitor.end_measurement("search_benchmark")
        results["total_time"] = metrics["duration"]
        results["average_time"] = sum(results["search_times"]) / len(
            results["search_times"]
        )
        results["throughput"] = results["total_searches"] / results["total_time"]

        logger.info(
            f"Search benchmark completed: {results['total_searches']} searches in {results['total_time']:.2f}s"
        )

        return results

    async def run_indexing_benchmark(self) -> Dict:
        """Benchmark indexing performance"""
        logger.info("Running indexing benchmark...")

        # Generate test bytecodes
        test_bytecodes = []
        for i in range(100):
            bytecode = f"6080604052348015600f57600080fd5b50{i:04x}"
            metadata = {"name": f"bench_test_{i}", "index": i}
            test_bytecodes.append((bytecode, metadata))

        results = {
            "total_indexed": 0,
            "total_time": 0,
            "indexing_rate": 0,
            "batch_size": len(test_bytecodes),
        }

        self.monitor.start_measurement()

        # Batch index
        hashes = await self.engine.batch_index_bytecodes(test_bytecodes)

        metrics = self.monitor.end_measurement("indexing_benchmark")

        results["total_indexed"] = len(hashes)
        results["total_time"] = metrics["duration"]
        results["indexing_rate"] = results["total_indexed"] / results["total_time"]

        logger.info(
            f"Indexing benchmark completed: {results['total_indexed']} bytecodes in {results['total_time']:.2f}s"
        )

        return results

    async def run_accuracy_benchmark(self) -> Dict:
        """Benchmark accuracy with synthetic data"""
        logger.info("Running accuracy benchmark...")

        # Create test pairs with known similarity
        similar_pairs = [
            (
                "6080604052348015600f57600080fd5b50",
                "6080604052348015600f57600080fd5b50",
            ),  # Identical
            (
                "6080604052348015600f57600080fd5b50",
                "6080604052348015600f57600080fd5b51",
            ),  # Very similar
        ]

        dissimilar_pairs = [
            (
                "6080604052348015600f57600080fd5b50",
                "608060405234801561001057600080fd5b50",
            ),  # Different
            ("6080604052600436106100295760003560e01c", "f3fe"),  # Very different
        ]

        y_true = []
        y_pred = []
        y_scores = []

        # Test similar pairs
        for bytecode1, bytecode2 in similar_pairs:
            result = await self.engine.compare_bytecodes(bytecode1, bytecode2)
            y_true.append(1)  # Similar
            y_pred.append(1 if result.similarity_score > 0.7 else 0)
            y_scores.append(result.similarity_score)

        # Test dissimilar pairs
        for bytecode1, bytecode2 in dissimilar_pairs:
            result = await self.engine.compare_bytecodes(bytecode1, bytecode2)
            y_true.append(0)  # Not similar
            y_pred.append(1 if result.similarity_score > 0.7 else 0)
            y_scores.append(result.similarity_score)

        # Calculate metrics
        metrics = SimilarityMetrics.calculate_comprehensive_metrics(
            y_true, y_pred, y_scores
        )

        logger.info(
            f"Accuracy benchmark completed - Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}"
        )

        return metrics

    async def run_memory_benchmark(self) -> Dict:
        """Benchmark memory usage"""
        logger.info("Running memory benchmark...")

        import gc

        import psutil

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run some operations
        await self.run_similarity_benchmark()
        await self.run_search_benchmark()

        # Force garbage collection
        gc.collect()

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        results = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "peak_memory_mb": process.memory_info().peak_wss / 1024 / 1024
            if hasattr(process.memory_info(), "peak_wss")
            else None,
        }

        logger.info(
            f"Memory benchmark completed - Memory increase: {memory_increase:.2f} MB"
        )

        return results

    async def run_all_benchmarks(self) -> Dict:
        """Run comprehensive benchmark suite"""
        logger.info("Starting comprehensive benchmark suite...")

        await self.initialize_engine()

        all_results = {
            "timestamp": time.time(),
            "engine_config": self.config,
            "benchmarks": {},
        }

        # Run individual benchmarks
        try:
            all_results["benchmarks"][
                "similarity"
            ] = await self.run_similarity_benchmark()
        except Exception as e:
            logger.error(f"Similarity benchmark failed: {e}")
            all_results["benchmarks"]["similarity"] = {"error": str(e)}

        try:
            all_results["benchmarks"]["search"] = await self.run_search_benchmark()
        except Exception as e:
            logger.error(f"Search benchmark failed: {e}")
            all_results["benchmarks"]["search"] = {"error": str(e)}

        try:
            all_results["benchmarks"]["indexing"] = await self.run_indexing_benchmark()
        except Exception as e:
            logger.error(f"Indexing benchmark failed: {e}")
            all_results["benchmarks"]["indexing"] = {"error": str(e)}

        try:
            all_results["benchmarks"]["accuracy"] = await self.run_accuracy_benchmark()
        except Exception as e:
            logger.error(f"Accuracy benchmark failed: {e}")
            all_results["benchmarks"]["accuracy"] = {"error": str(e)}

        try:
            all_results["benchmarks"]["memory"] = await self.run_memory_benchmark()
        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")
            all_results["benchmarks"]["memory"] = {"error": str(e)}

        # Engine statistics
        all_results["engine_stats"] = self.engine.get_engine_stats()

        logger.info("Comprehensive benchmark suite completed")

        return all_results

    def save_results(self, results: Dict, output_path: str):
        """Save benchmark results to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Benchmark results saved to {output_file}")

    def print_summary(self, results: Dict):
        """Print benchmark summary"""
        print("\n" + "=" * 80)
        print("SCORPIUS BYTECODE SIMILARITY ENGINE - BENCHMARK RESULTS")
        print("=" * 80)

        benchmarks = results.get("benchmarks", {})

        # Similarity benchmark
        if "similarity" in benchmarks and "error" not in benchmarks["similarity"]:
            sim_results = benchmarks["similarity"]
            print(f"\n📊 SIMILARITY COMPARISON:")
            print(f"   Total Comparisons: {sim_results['total_comparisons']}")
            print(f"   Average Time: {sim_results['average_time']:.4f}s")
            print(f"   Throughput: {sim_results['throughput']:.2f} comparisons/sec")

        # Search benchmark
        if "search" in benchmarks and "error" not in benchmarks["search"]:
            search_results = benchmarks["search"]
            print(f"\n🔍 SIMILARITY SEARCH:")
            print(f"   Total Searches: {search_results['total_searches']}")
            print(f"   Average Time: {search_results['average_time']:.4f}s")
            print(f"   Throughput: {search_results['throughput']:.2f} searches/sec")

        # Indexing benchmark
        if "indexing" in benchmarks and "error" not in benchmarks["indexing"]:
            idx_results = benchmarks["indexing"]
            print(f"\n📚 INDEXING PERFORMANCE:")
            print(f"   Total Indexed: {idx_results['total_indexed']}")
            print(f"   Indexing Rate: {idx_results['indexing_rate']:.2f} bytecodes/sec")

        # Accuracy benchmark
        if "accuracy" in benchmarks and "error" not in benchmarks["accuracy"]:
            acc_results = benchmarks["accuracy"]
            print(f"\n🎯 ACCURACY METRICS:")
            print(f"   Accuracy: {acc_results['accuracy']:.3f}")
            print(f"   Precision: {acc_results['precision']:.3f}")
            print(f"   Recall: {acc_results['recall']:.3f}")
            print(f"   F1-Score: {acc_results['f1_score']:.3f}")

        # Memory benchmark
        if "memory" in benchmarks and "error" not in benchmarks["memory"]:
            mem_results = benchmarks["memory"]
            print(f"\n💾 MEMORY USAGE:")
            print(f"   Initial Memory: {mem_results['initial_memory_mb']:.2f} MB")
            print(f"   Final Memory: {mem_results['final_memory_mb']:.2f} MB")
            print(f"   Memory Increase: {mem_results['memory_increase_mb']:.2f} MB")

        print("\n" + "=" * 80)


async def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description="Run SCORPIUS engine benchmarks")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument(
        "--output",
        type=str,
        default="results/benchmark_results.json",
        help="Output file for results",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        choices=["all", "similarity", "search", "indexing", "accuracy", "memory"],
        default="all",
        help="Specific benchmark to run",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print summary to console"
    )

    args = parser.parse_args()

    # Initialize benchmark suite
    benchmark = ComprehensiveBenchmark(args.config)

    if args.benchmark == "all":
        results = await benchmark.run_all_benchmarks()
    else:
        await benchmark.initialize_engine()

        if args.benchmark == "similarity":
            results = {"similarity": await benchmark.run_similarity_benchmark()}
        elif args.benchmark == "search":
            results = {"search": await benchmark.run_search_benchmark()}
        elif args.benchmark == "indexing":
            results = {"indexing": await benchmark.run_indexing_benchmark()}
        elif args.benchmark == "accuracy":
            results = {"accuracy": await benchmark.run_accuracy_benchmark()}
        elif args.benchmark == "memory":
            results = {"memory": await benchmark.run_memory_benchmark()}

    # Save results
    benchmark.save_results(results, args.output)

    # Print summary if requested
    if args.summary:
        benchmark.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
