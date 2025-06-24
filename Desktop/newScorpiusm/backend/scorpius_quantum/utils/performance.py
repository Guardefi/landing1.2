"""
Performance monitoring utilities for quantum cryptography.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..core.types import PerformanceMetrics, QuantumAlgorithm, SecurityLevel


@dataclass
class PerformanceTracker:
    """Tracks performance metrics for quantum operations."""

    metrics: list[PerformanceMetrics] = field(default_factory=list)
    start_time: float | None = None
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))

    def start_operation(
        self,
        operation_type: str,
        algorithm: QuantumAlgorithm,
        security_level: SecurityLevel,
    ) -> None:
        """Start tracking an operation."""
        self.start_time = time.time()
        self.current_operation = {
            "operation_type": operation_type,
            "algorithm": algorithm,
            "security_level": security_level,
        }

    def end_operation(
        self, success: bool = True, error_message: str | None = None
    ) -> PerformanceMetrics:
        """End tracking and record metrics."""
        if self.start_time is None:
            raise ValueError("No operation started")

        execution_time = time.time() - self.start_time

        metric = PerformanceMetrics(
            operation_type=self.current_operation["operation_type"],
            algorithm=self.current_operation["algorithm"],
            security_level=self.current_operation["security_level"],
            execution_time=execution_time,
            memory_usage=0,  # Would implement actual memory tracking
            cpu_usage=0.0,  # Would implement actual CPU tracking
            success=success,
            error_message=error_message,
        )

        self.metrics.append(metric)
        self.start_time = None

        return metric

    def get_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        if not self.metrics:
            return {"total_operations": 0}

        total_ops = len(self.metrics)
        successful_ops = sum(1 for m in self.metrics if m.success)

        avg_time = sum(m.execution_time for m in self.metrics) / total_ops

        # Algorithm breakdown
        algo_stats = {}
        for metric in self.metrics:
            algo = metric.algorithm.value
            if algo not in algo_stats:
                algo_stats[algo] = {"count": 0, "avg_time": 0, "total_time": 0}
            algo_stats[algo]["count"] += 1
            algo_stats[algo]["total_time"] += metric.execution_time

        for algo in algo_stats:
            algo_stats[algo]["avg_time"] = (
                algo_stats[algo]["total_time"] / algo_stats[algo]["count"]
            )

        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": successful_ops / total_ops,
            "average_execution_time": avg_time,
            "algorithm_breakdown": algo_stats,
            "latest_operations": [
                {
                    "operation": m.operation_type,
                    "algorithm": m.algorithm.value,
                    "time": m.execution_time,
                    "success": m.success,
                }
                for m in self.metrics[-10:]  # Last 10 operations
            ],
        }


class PerformanceMonitor:
    """Global performance monitoring for quantum operations."""

    def __init__(self):
        self.trackers: dict[str, PerformanceTracker] = {}
        self.logger = logging.getLogger(__name__)

    def get_tracker(self, session_id: str = "default") -> PerformanceTracker:
        """Get or create a performance tracker for a session."""
        if session_id not in self.trackers:
            self.trackers[session_id] = PerformanceTracker()
        return self.trackers[session_id]

    def get_global_stats(self) -> dict[str, Any]:
        """Get aggregated statistics across all sessions."""
        all_metrics = []
        for tracker in self.trackers.values():
            all_metrics.extend(tracker.metrics)

        if not all_metrics:
            return {"total_operations": 0, "sessions": len(self.trackers)}

        total_ops = len(all_metrics)
        successful_ops = sum(1 for m in all_metrics if m.success)

        # Time-based analysis
        now = datetime.now()
        recent_metrics = [
            m for m in all_metrics if (now - m.timestamp).total_seconds() < 3600
        ]  # Last hour

        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": successful_ops / total_ops if total_ops > 0 else 0,
            "total_sessions": len(self.trackers),
            "recent_operations_1h": len(recent_metrics),
            "recent_success_rate_1h": (
                sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
                if recent_metrics
                else 0
            ),
        }

    async def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metrics to prevent memory growth."""
        cutoff_time = datetime.now()
        cutoff_time = cutoff_time.replace(hour=cutoff_time.hour - max_age_hours)

        for tracker in self.trackers.values():
            tracker.metrics = [m for m in tracker.metrics if m.timestamp > cutoff_time]

        self.logger.info(f"Cleaned up metrics older than {max_age_hours} hours")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def track_performance(
    operation_type: str,
    algorithm: QuantumAlgorithm,
    security_level: SecurityLevel,
    session_id: str = "default",
):
    """Decorator to track performance of quantum operations."""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            tracker = performance_monitor.get_tracker(session_id)
            tracker.start_operation(operation_type, algorithm, security_level)

            try:
                result = await func(*args, **kwargs)
                tracker.end_operation(success=True)
                return result
            except Exception as e:
                tracker.end_operation(success=False, error_message=str(e))
                raise e from e

        def sync_wrapper(*args, **kwargs):
            tracker = performance_monitor.get_tracker(session_id)
            tracker.start_operation(operation_type, algorithm, security_level)

            try:
                result = func(*args, **kwargs)
                tracker.end_operation(success=True)
                return result
            except Exception as e:
                tracker.end_operation(success=False, error_message=str(e))
                raise e from e

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
