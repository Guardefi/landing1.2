"""
Performance Monitoring and Metrics
Comprehensive performance monitoring for similarity engine
"""

import logging
import time
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Docker
import matplotlib.pyplot as plt
import numpy as np
import psutil
import seaborn as sns
import torch
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Comprehensive performance monitoring for similarity engine"""

    def __init__(self):
        self.metrics_history = []
        self.start_time = None

    def start_measurement(self):
        """Start performance measurement"""
        self.start_time = time.time()

    def end_measurement(self, operation_name: str, additional_metrics: Dict = None):
        """End measurement and record metrics"""
        if self.start_time is None:
            return

        end_time = time.time()
        duration = end_time - self.start_time

        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()

        # GPU metrics if available
        gpu_metrics = {}
        if torch.cuda.is_available():
            gpu_metrics = {
                "gpu_memory_allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "gpu_memory_cached": torch.cuda.memory_reserved() / 1024**3,  # GB
                "gpu_utilization": self._get_gpu_utilization(),
            }

        metrics = {
            "operation": operation_name,
            "duration": duration,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_info.percent,
            "memory_used_gb": memory_info.used / 1024**3,
            "timestamp": end_time,
            **gpu_metrics,
        }

        if additional_metrics:
            metrics.update(additional_metrics)

        self.metrics_history.append(metrics)
        self.start_time = None

        return metrics

    def _get_gpu_utilization(self):
        """Get GPU utilization if available"""
        try:
            if hasattr(torch.cuda, "utilization"):
                return torch.cuda.utilization()
            else:
                return 0
        except Exception:
            return 0

    def get_performance_summary(self, operation_filter: str = None) -> Dict:
        """Get performance summary statistics"""
        filtered_metrics = self.metrics_history
        if operation_filter:
            filtered_metrics = [
                m for m in self.metrics_history if operation_filter in m["operation"]
            ]

        if not filtered_metrics:
            return {}

        durations = [m["duration"] for m in filtered_metrics]
        cpu_usages = [m["cpu_percent"] for m in filtered_metrics]
        memory_usages = [m["memory_percent"] for m in filtered_metrics]

        return {
            "total_operations": len(filtered_metrics),
            "avg_duration": np.mean(durations),
            "median_duration": np.median(durations),
            "p95_duration": np.percentile(durations, 95),
            "p99_duration": np.percentile(durations, 99),
            "avg_cpu_usage": np.mean(cpu_usages),
            "avg_memory_usage": np.mean(memory_usages),
            "throughput_ops_per_second": len(filtered_metrics) / sum(durations)
            if sum(durations) > 0
            else 0,
        }

    def export_metrics(self, filepath: str):
        """Export metrics to file"""
        import json

        with open(filepath, "w") as f:
            json.dump(self.metrics_history, f, indent=2)
        logger.info(f"Metrics exported to {filepath}")


class SimilarityMetrics:
    """Metrics calculation for similarity detection"""

    @staticmethod
    def calculate_comprehensive_metrics(
        y_true: List[int], y_pred: List[int], y_scores: List[float]
    ) -> Dict:
        """Calculate comprehensive similarity detection metrics"""

        # Basic classification metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average="binary"
        )

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()

        # Additional metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

        # Calculate AUC-ROC and AUC-PR
        auc_roc = roc_auc_score(y_true, y_scores)
        auc_pr = average_precision_score(y_true, y_scores)

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "specificity": specificity,
            "false_positive_rate": fpr,
            "false_negative_rate": fnr,
            "auc_roc": auc_roc,
            "auc_pr": auc_pr,
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        }

    @staticmethod
    def plot_confusion_matrix(
        y_true: List[int], y_pred: List[int], save_path: str = None
    ):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Not Similar", "Similar"],
            yticklabels=["Not Similar", "Similar"],
        )
        plt.title("Confusion Matrix - Bytecode Similarity Detection")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    @staticmethod
    def plot_roc_curve(y_true: List[int], y_scores: List[float], save_path: str = None):
        """Plot ROC curve"""
        from sklearn.metrics import roc_curve

        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        auc = roc_auc_score(y_true, y_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, linewidth=2, label=f"ROC Curve (AUC = {auc:.3f})")
        plt.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve - Bytecode Similarity Detection")
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    @staticmethod
    def plot_precision_recall_curve(
        y_true: List[int], y_scores: List[float], save_path: str = None
    ):
        """Plot Precision-Recall curve"""
        from sklearn.metrics import precision_recall_curve

        precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
        auc_pr = average_precision_score(y_true, y_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, linewidth=2, label=f"PR Curve (AUC = {auc_pr:.3f})")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve - Bytecode Similarity Detection")
        plt.legend(loc="lower left")
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()


class BenchmarkSuite:
    """Comprehensive benchmarking suite"""

    def __init__(self, similarity_engine):
        self.engine = similarity_engine
        self.monitor = PerformanceMonitor()

    async def run_scalability_benchmark(self, test_sizes: List[int]) -> Dict:
        """Test scalability with different dataset sizes"""
        results = {}

        for size in test_sizes:
            logger.info(f"Testing with {size} bytecode samples...")

            # Generate test data
            test_bytecodes = self._generate_test_bytecodes(size)

            # Measure indexing time
            self.monitor.start_measurement()
            await self._index_bytecodes(test_bytecodes)
            indexing_metrics = self.monitor.end_measurement(f"indexing_{size}")

            # Measure search time
            query_bytecode = test_bytecodes[0]
            self.monitor.start_measurement()
            search_results = await self.engine.find_similar_bytecode(
                query_bytecode, top_k=10
            )
            search_metrics = self.monitor.end_measurement(f"search_{size}")

            results[size] = {
                "indexing_time": indexing_metrics["duration"],
                "search_time": search_metrics["duration"],
                "memory_usage": search_metrics["memory_used_gb"],
                "results_count": len(search_results),
            }

        return results

    async def run_accuracy_benchmark(self, test_dataset: Dict) -> Dict:
        """Test accuracy on labeled dataset"""
        y_true = []
        y_pred = []
        y_scores = []

        for pair, label in zip(test_dataset["pairs"], test_dataset["labels"]):
            bytecode1, bytecode2 = pair

            # Get similarity prediction
            result = await self.engine._analyze_similarity(
                bytecode1, {"bytecode": bytecode2, "hash": "test"}, True
            )

            prediction = 1 if result.similarity_score > 0.7 else 0

            y_true.append(label)
            y_pred.append(prediction)
            y_scores.append(result.similarity_score)

        # Calculate metrics
        metrics = SimilarityMetrics.calculate_comprehensive_metrics(
            y_true, y_pred, y_scores
        )

        return metrics

    async def run_performance_benchmark(self, num_comparisons: int = 1000) -> Dict:
        """Test performance with repeated comparisons"""
        # Generate test bytecodes
        test_bytecodes = self._generate_test_bytecodes(100)

        # Measure comparison performance
        self.monitor.start_measurement()

        comparison_times = []
        for i in range(num_comparisons):
            start = time.time()
            bytecode1 = test_bytecodes[i % len(test_bytecodes)]
            bytecode2 = test_bytecodes[(i + 1) % len(test_bytecodes)]

            await self.engine.compare_bytecodes(bytecode1, bytecode2)

            comparison_times.append(time.time() - start)

        total_metrics = self.monitor.end_measurement(
            f"performance_benchmark_{num_comparisons}"
        )

        return {
            "total_comparisons": num_comparisons,
            "total_time": total_metrics["duration"],
            "avg_comparison_time": np.mean(comparison_times),
            "median_comparison_time": np.median(comparison_times),
            "p95_comparison_time": np.percentile(comparison_times, 95),
            "throughput_cps": num_comparisons
            / total_metrics["duration"],  # comparisons per second
        }

    def _generate_test_bytecodes(self, count: int) -> List[str]:
        """Generate synthetic test bytecodes"""
        # This should generate realistic EVM bytecodes for testing
        # Simplified version - implement proper generation
        test_bytecodes = []

        base_patterns = [
            "6080604052348015600f57600080fd5b50",  # Standard constructor
            "608060405234801561001057600080fd5b50",  # Another constructor pattern
            "6080604052600436106100295760003560e01c",  # Function dispatcher
        ]

        for i in range(count):
            # Add some variation
            base = base_patterns[i % len(base_patterns)]
            variation = hex(i)[2:].zfill(4)
            modified = base + variation + "00"
            test_bytecodes.append(modified)

        return test_bytecodes

    async def _index_bytecodes(self, bytecodes: List[str]):
        """Index bytecodes for similarity search"""
        # Implement indexing logic
        embeddings = []
        metadata = []

        for i, bytecode in enumerate(bytecodes):
            # This would use the actual embedding engine
            # For now, create dummy embeddings
            embedding = np.random.random(256)  # Dummy 256-dim embedding
            embeddings.append(embedding)
            metadata.append(
                {"hash": f"test_{i}", "bytecode": bytecode, "source": "benchmark"}
            )

        # This would add to the actual vector index
        logger.info(f"Indexed {len(embeddings)} bytecode embeddings")

    def generate_benchmark_report(self, results: Dict, output_path: str):
        """Generate comprehensive benchmark report"""
        report = {
            "timestamp": time.time(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024**3,
                "gpu_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count()
                if torch.cuda.is_available()
                else 0,
            },
            "results": results,
            "performance_summary": self.monitor.get_performance_summary(),
        }

        import json

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Benchmark report saved to {output_path}")


class MetricsCollector:
    """Collect and aggregate metrics during runtime"""

    def __init__(self):
        self.metrics = {
            "comparisons_count": 0,
            "total_comparison_time": 0,
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def record_comparison(self, duration: float, success: bool = True):
        """Record a comparison operation"""
        self.metrics["comparisons_count"] += 1
        self.metrics["total_comparison_time"] += duration
        if not success:
            self.metrics["error_count"] += 1

    def record_cache_hit(self):
        """Record a cache hit"""
        self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        metrics = self.metrics.copy()
        if metrics["comparisons_count"] > 0:
            metrics["avg_comparison_time"] = (
                metrics["total_comparison_time"] / metrics["comparisons_count"]
            )
            metrics["error_rate"] = (
                metrics["error_count"] / metrics["comparisons_count"]
            )

        total_cache_ops = metrics["cache_hits"] + metrics["cache_misses"]
        if total_cache_ops > 0:
            metrics["cache_hit_rate"] = metrics["cache_hits"] / total_cache_ops

        return metrics

    def reset(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = 0
