#!/usr/bin/env python3
"""
Cost Model Analyzer for Scorpius Load Testing
Analyzes k6 load test results and provides HPA scaling recommendations
Based on RPS vs CPU utilization metrics for optimal resource allocation
"""

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class ScalingRecommendation:
        """HPA scaling recommendation"""

        current_replicas: int
        recommended_replicas: int
        target_cpu_utilization: float
        predicted_rps: float
        cost_impact: float
        confidence: float
        reasoning: str


@dataclass
class CostMetrics:
        """Cost analysis metrics"""

        cpu_cost_per_hour: float
        memory_cost_per_hour: float
        total_cost_per_hour: float
        cost_per_rps: float
        efficiency_score: float


class CostModelAnalyzer:
        """Analyzes load test results and provides cost-optimized scaling recommendations"""

    def __init__(self, config_file: Optional[str] = None):
        # Default AWS pricing (adjust based on actual instance types)
        self.pricing = {
            "cpu_cost_per_core_hour": 0.0464,  # t3.medium equivalent
            "memory_cost_per_gb_hour": 0.0058,
            "network_cost_per_gb": 0.09,
            "storage_cost_per_gb_hour": 0.0001,
        }

        # HPA configuration
        self.hpa_config = {
            "min_replicas": 2,
            "max_replicas": 50,
            "target_cpu_utilization": 70,
            "scale_up_threshold": 80,
            "scale_down_threshold": 50,
            "scale_up_cooldown": 300,  # 5 minutes
            "scale_down_cooldown": 600,  # 10 minutes
        }

        # Performance baselines
        self.baselines = {
            "max_rps_per_replica": 100,
            "cpu_per_rps": 0.5,  # CPU percentage per RPS
            "memory_per_rps": 10,  # MB per RPS
            "latency_sla_p95": 2000,  # 2 seconds
            "error_rate_threshold": 0.05,  # 5%
        }

        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                self.pricing.update(config.get("pricing", {}))
                self.hpa_config.update(config.get("hpa", {}))
                self.baselines.update(config.get("baselines", {}))
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")

    def analyze_test_results(self, results_file: str) -> Dict:
        """Analyze k6 load test results"""
        with open(results_file, "r") as f:
            results = json.load(f)

        analysis = {
            "test_summary": self._extract_test_summary(results),
            "performance_metrics": self._analyze_performance(results),
            "resource_utilization": self._analyze_resource_usage(results),
            "cost_analysis": self._calculate_costs(results),
            "scaling_recommendations": self._generate_scaling_recommendations(results),
            "sla_compliance": self._check_sla_compliance(results),
        }


    def _extract_test_summary(self, results: Dict) -> Dict:
        """Extract high-level test summary"""
        metrics = results.get("metrics", {})

        return {
            "test_duration_minutes": results.get("test_duration", 0) / 1000 / 60,
            "total_requests": metrics.get("http_reqs", {}).get("count", 0),
            "total_errors": metrics.get("http_req_failed", {}).get("count", 0),
            "average_rps": metrics.get("http_reqs", {}).get("rate", 0),
            "error_rate": metrics.get("http_req_failed", {}).get("rate", 0),
            "avg_response_time": metrics.get("http_req_duration", {}).get("avg", 0),
            "p95_response_time": metrics.get("http_req_duration", {}).get("p95", 0),
            "mempool_transactions": metrics.get("mempool_transactions_total", {}).get(
                "count", 0
            ),
            "mempool_throughput": metrics.get("mempool_throughput_rps", {}).get(
                "rate", 0
            ),
        }

    def _analyze_performance(self, results: Dict) -> Dict:
        """Analyze performance characteristics"""
        metrics = results.get("metrics", {})

        # Calculate performance efficiency
        rps = metrics.get("http_reqs", {}).get("rate", 0)
        cpu_util = metrics.get("cpu_utilization_percent", {}).get("avg", 0)
        memory_util = metrics.get("memory_usage_mb", {}).get("avg", 0)

        efficiency = rps / max(cpu_util, 1) if cpu_util > 0 else 0

            "requests_per_second": rps,
            "cpu_utilization_avg": cpu_util,
            "cpu_utilization_p95": metrics.get("cpu_utilization_percent", {}).get(
                "p95", 0
            ),
            "memory_usage_avg_mb": memory_util,
            "memory_usage_p95_mb": metrics.get("memory_usage_mb", {}).get("p95", 0),
            "performance_efficiency": efficiency,
            "latency_p50": metrics.get("http_req_duration", {}).get("p50", 0),
            "latency_p90": metrics.get("http_req_duration", {}).get("p90", 0),
            "latency_p95": metrics.get("http_req_duration", {}).get("p95", 0),
            "latency_p99": metrics.get("http_req_duration", {}).get("p99", 0),
        }

    def _analyze_resource_usage(self, results: Dict) -> Dict:
        """Analyze resource utilization patterns"""
        metrics = results.get("metrics", {})

        cpu_avg = metrics.get("cpu_utilization_percent", {}).get("avg", 0)
        cpu_max = metrics.get("cpu_utilization_percent", {}).get("max", 0)
        memory_avg = metrics.get("memory_usage_mb", {}).get("avg", 0)
        memory_max = metrics.get("memory_usage_mb", {}).get("max", 0)

        # Calculate resource efficiency
        cpu_efficiency = (cpu_avg / max(cpu_max, 1)) * \
            100 if cpu_max > 0 else 0
        memory_efficiency = (
            (memory_avg / max(memory_max, 1)) * 100 if memory_max > 0 else 0
        )

            "cpu_utilization": {
                "average": cpu_avg,
                "maximum": cpu_max,
                "efficiency": cpu_efficiency,
            ],
            "memory_utilization": {
                "average_mb": memory_avg,
                "maximum_mb": memory_max,
                "efficiency": memory_efficiency,
            ],
            "resource_bottlenecks": self._identify_bottlenecks(cpu_avg, memory_avg),
            "utilization_trend": self._analyze_utilization_trend(metrics),
        }

    def _identify_bottlenecks(
            self,
            cpu_avg: float,
            memory_avg: float) -> List[str]:
        """Identify resource bottlenecks"""
        bottlenecks = []

        if cpu_avg > 80:
            bottlenecks.append("CPU_HIGH")
        elif cpu_avg < 20:
            bottlenecks.append("CPU_UNDERUTILIZED")

        if memory_avg > 3072:  # 3GB threshold
            bottlenecks.append("MEMORY_HIGH")
        elif memory_avg < 512:  # 512MB threshold
            bottlenecks.append("MEMORY_UNDERUTILIZED")


    def _analyze_utilization_trend(self, metrics: Dict) -> str:
        """Analyze resource utilization trend"""
        cpu_avg = metrics.get("cpu_utilization_percent", {}).get("avg", 0)
        cpu_p95 = metrics.get("cpu_utilization_percent", {}).get("p95", 0)

        if cpu_p95 > cpu_avg * 1.5:
            return "SPIKY"
        elif cpu_p95 > cpu_avg * 1.2:
            return "VARIABLE"
        else:
            return "STABLE"

    def _calculate_costs(self, results: Dict) -> CostMetrics:
        """Calculate cost metrics"""
        metrics = results.get("metrics", {})
        results.get("test_duration", 0) / 1000 / 3600

        cpu_avg = metrics.get(
            "cpu_utilization_percent", {}).get(
            "avg", 0) / 100
        memory_avg_gb = metrics.get("memory_usage_mb", {}).get("avg", 0) / 1024
        rps = metrics.get("http_reqs", {}).get("rate", 0)

        # Calculate costs per hour
        cpu_cost_per_hour = (
            cpu_avg * 2 * self.pricing["cpu_cost_per_core_hour"]
        )  # 2 cores assumed
        memory_cost_per_hour = memory_avg_gb * \
            self.pricing["memory_cost_per_gb_hour"]
        total_cost_per_hour = cpu_cost_per_hour + memory_cost_per_hour

        # Calculate cost per RPS
        cost_per_rps = total_cost_per_hour / max(rps, 1) if rps > 0 else 0

        # Calculate efficiency score (higher is better)
        efficiency_score = rps / max(total_cost_per_hour, 0.001) * 100

            cpu_cost_per_hour=cpu_cost_per_hour,
            memory_cost_per_hour=memory_cost_per_hour,
            total_cost_per_hour=total_cost_per_hour,
            cost_per_rps=cost_per_rps,
            efficiency_score=efficiency_score,
        )

    def _generate_scaling_recommendations(
        self, results: Dict
        ) -> List[ScalingRecommendation]:
        """Generate HPA scaling recommendations"""
        metrics = results.get("metrics", {})
        recommendations = []

        current_cpu = metrics.get("cpu_utilization_percent", {}).get("avg", 0)
        current_rps = metrics.get("http_reqs", {}).get("rate", 0)
        p95_latency = metrics.get("http_req_duration", {}).get("p95", 0)
        error_rate = metrics.get("http_req_failed", {}).get("rate", 0)

        # Current state analysis
        current_replicas = max(1, int(current_cpu / 50)
                               )  # Estimate based on CPU

        # Scenario 1: Optimize for cost
        cost_optimal = self._calculate_cost_optimal_scaling(
            current_cpu, current_rps, current_replicas
        )
        recommendations.append(cost_optimal)

        # Scenario 2: Optimize for performance
        perf_optimal = self._calculate_performance_optimal_scaling(
            current_cpu, current_rps, p95_latency, current_replicas
        )
        recommendations.append(perf_optimal)

        # Scenario 3: Balanced approach
        balanced = self._calculate_balanced_scaling(
            current_cpu, current_rps, p95_latency, error_rate, current_replicas
        )
        recommendations.append(balanced)


    def _calculate_cost_optimal_scaling(
        self, cpu: float, rps: float, current_replicas: int
        ) -> ScalingRecommendation:
        """Calculate cost-optimal scaling recommendation"""
        target_cpu = 75  # Higher utilization for cost savings

        if cpu > 0:
            optimal_replicas = max(
                self.hpa_config["min_replicas"],
                min(
                    self.hpa_config["max_replicas"],
                    int((cpu / target_cpu) * current_replicas),
                ),
            )
        else:
            optimal_replicas = self.hpa_config["min_replicas"]

        predicted_rps = rps * (current_replicas / max(optimal_replicas, 1))
        cost_impact = (current_replicas - optimal_replicas) * \
            0.0464  # Savings per hour

            current_replicas=current_replicas,
            recommended_replicas=optimal_replicas,
            target_cpu_utilization=target_cpu,
            predicted_rps=predicted_rps,
            cost_impact=cost_impact,
            confidence=0.8,
            reasoning="Optimized for cost efficiency with higher CPU utilization",
        )

    def _calculate_performance_optimal_scaling(
        self, cpu: float, rps: float, latency: float, current_replicas: int
        ) -> ScalingRecommendation:
        """Calculate performance-optimal scaling recommendation"""
        target_cpu = 50  # Lower utilization for better performance

        if cpu > 0:
            optimal_replicas = max(
                self.hpa_config["min_replicas"],
                min(
                    self.hpa_config["max_replicas"],
                    int((cpu / target_cpu) * current_replicas),
                ),
            )
        else:
            optimal_replicas = current_replicas

        # Adjust for latency concerns
        if latency > self.baselines["latency_sla_p95"]:
            optimal_replicas = int(optimal_replicas * 1.5)

        predicted_rps = rps * (optimal_replicas / max(current_replicas, 1))
        cost_impact = (optimal_replicas - current_replicas) * - \
            0.0464  # Additional cost

            current_replicas=current_replicas,
            recommended_replicas=optimal_replicas,
            target_cpu_utilization=target_cpu,
            predicted_rps=predicted_rps,
            cost_impact=cost_impact,
            confidence=0.9,
            reasoning="Optimized for performance with lower CPU utilization and better latency",
        )

    def _calculate_balanced_scaling(
        self,
        cpu: float,
        rps: float,
        latency: float,
        error_rate: float,
        current_replicas: int,
        ) -> ScalingRecommendation:
        """Calculate balanced scaling recommendation"""
        target_cpu = self.hpa_config["target_cpu_utilization"]

        if cpu > 0:
            optimal_replicas = max(
                self.hpa_config["min_replicas"],
                min(
                    self.hpa_config["max_replicas"],
                    int((cpu / target_cpu) * current_replicas),
                ),
            )
        else:
            optimal_replicas = current_replicas

        # Adjust based on error rate
        if error_rate > self.baselines["error_rate_threshold"]:
            optimal_replicas = int(optimal_replicas * 1.2)

        predicted_rps = rps * (optimal_replicas / max(current_replicas, 1))
        cost_impact = (optimal_replicas - current_replicas) * -0.0464

        confidence = 0.95
        if abs(optimal_replicas - current_replicas) / \
                max(current_replicas, 1) > 0.5:
            confidence = 0.7  # Lower confidence for large changes

            current_replicas=current_replicas,
            recommended_replicas=optimal_replicas,
            target_cpu_utilization=target_cpu,
            predicted_rps=predicted_rps,
            cost_impact=cost_impact,
            confidence=confidence,
            reasoning="Balanced approach considering cost, performance, and reliability",
        )

    def _check_sla_compliance(self, results: Dict) -> Dict:
        """Check SLA compliance"""
        metrics = results.get("metrics", {})
        thresholds = results.get("thresholds", {})

        p95_latency = metrics.get("http_req_duration", {}).get("p95", 0)
        error_rate = metrics.get("http_req_failed", {}).get("rate", 0)

        compliance = {
            "latency_sla": {
                "target": self.baselines["latency_sla_p95"],
                "actual": p95_latency,
                "compliant": p95_latency <= self.baselines["latency_sla_p95"],
            ],
            "error_rate_sla": {
                "target": self.baselines["error_rate_threshold"],
                "actual": error_rate,
                "compliant": error_rate <= self.baselines["error_rate_threshold"],
            ],
            "threshold_compliance": {
                name: threshold.get("passed", False)
                for name, threshold in thresholds.items()
            ],
        }


    def generate_report(self, analysis: Dict, output_file: str):
        """Generate comprehensive analysis report"""
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "executive_summary": self._generate_executive_summary(analysis),
            "detailed_analysis": analysis,
            "recommendations": self._prioritize_recommendations(analysis),
            "cost_optimization": self._generate_cost_optimization_plan(analysis),
            "monitoring_alerts": self._generate_monitoring_alerts(analysis),
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate visualizations
        self._generate_visualizations(
            analysis, output_file.replace(
                ".json", ""))

        print(f"Analysis report generated: {output_file}")

    def _generate_executive_summary(self, analysis: Dict) -> Dict:
        """Generate executive summary"""
        perf = analysis["performance_metrics"]
        cost = analysis["cost_analysis"]
        recommendations = analysis["scaling_recommendations"]

        # Find best recommendation
        best_rec = min(recommendations, key=lambda x: abs(x.cost_impact))

        return {
            "current_performance": {
                "rps": perf["requests_per_second"],
                "avg_latency_ms": perf["latency_p95"],
                "cpu_utilization": perf["cpu_utilization_avg"],
                "cost_per_hour": cost.total_cost_per_hour,
            ],
            "key_findings": [
                f"System handling {
                    perf['requests_per_second'}:.1f} RPS at {
                    perf['cpu_utilization_avg'}:.1f}% CPU",
                f"Cost efficiency: {cost.efficiency_score:.1f} RPS per dollar",
                f"P95 latency: {perf['latency_p95']:.0f}ms",
                f"Recommended scaling: {best_rec.reasoning}",
            },
            "immediate_actions": self._generate_immediate_actions(analysis),
            "estimated_savings": best_rec.cost_impact * 24 * 30,  # Monthly savings
        ]

    def _generate_immediate_actions(self, analysis: Dict) -> List[str]:
        """Generate immediate action items"""
        actions = []
        resource_util = analysis["resource_utilization"]
        sla_compliance = analysis["sla_compliance"]

        if "CPU_HIGH" in resource_util["resource_bottlenecks"]:
            actions.append("Scale up replicas to reduce CPU pressure")

        if "CPU_UNDERUTILIZED" in resource_util["resource_bottlenecks"]:
            actions.append("Scale down replicas to reduce costs")

        if not sla_compliance["latency_sla"]["compliant"]:
            actions.append(
                "Investigate latency issues and consider scaling up")

        if not sla_compliance["error_rate_sla"]["compliant"]:
            actions.append("Address error rate issues immediately")


    def _prioritize_recommendations(self, analysis: Dict) -> List[Dict]:
        """Prioritize scaling recommendations"""
        recommendations = analysis["scaling_recommendations"]

        # Sort by confidence and cost impact
        sorted_recs = sorted(
            recommendations,
            key=lambda x: (x.confidence, -abs(x.cost_impact)),
            reverse=True,
        )

            {
                "priority": i + 1,
                "recommendation": rec.reasoning,
                "replicas": rec.recommended_replicas,
                "cost_impact_monthly": rec.cost_impact * 24 * 30,
                "confidence": rec.confidence,
                "implementation_complexity": (
                    "Low"
                    if abs(rec.recommended_replicas - rec.current_replicas) <= 2
                    else "Medium"
                ),
            ]
            for i, rec in enumerate(sorted_recs)
        ]
    def _generate_cost_optimization_plan(self, analysis: Dict) -> Dict:
        """Generate cost optimization plan"""
        cost = analysis["cost_analysis"]
        analysis["performance_metrics"]

        return {
            "current_monthly_cost": cost.total_cost_per_hour * 24 * 30,
            "optimization_opportunities": [
                {
                    "area": "Right-sizing",
                    "potential_savings": cost.total_cost_per_hour * 0.2 * 24 * 30,
                    "description": "Optimize instance types based on actual usage",
                ],
                {
                    "area": "Auto-scaling tuning",
                    "potential_savings": cost.total_cost_per_hour * 0.15 * 24 * 30,
                    "description": "Fine-tune HPA parameters for better efficiency",
                ],
                {
                    "area": "Reserved instances",
                    "potential_savings": cost.total_cost_per_hour * 0.3 * 24 * 30,
                    "description": "Use reserved instances for baseline capacity",
                ],
            },
            "cost_efficiency_score": cost.efficiency_score,
            "benchmark_comparison": (
                "Above average" if cost.efficiency_score > 50 else "Below average"
            ),
        }

    def _generate_monitoring_alerts(self, analysis: Dict) -> List[Dict]:
        """Generate monitoring alert recommendations"""
        alerts = []

        # CPU-based alerts
        alerts.append(
            {
                "metric": "CPU Utilization",
                "threshold": 80,
                "action": "Scale up",
                "cooldown": 300,
            }
        )

        alerts.append(
            {
                "metric": "CPU Utilization",
                "threshold": 30,
                "action": "Scale down",
                "cooldown": 600,
            }
        )

        # Latency-based alerts
        alerts.append(
            {
                "metric": "P95 Latency",
                "threshold": 2000,
                "action": "Investigate performance",
                "cooldown": 0,
            }
        )

        # Error rate alerts
        alerts.append(
            {
                "metric": "Error Rate",
                "threshold": 5,
                "action": "Immediate investigation",
                "cooldown": 0,
            }
        )


    def _generate_visualizations(self, analysis: Dict, output_prefix: str):
        """Generate visualization charts"""
        try:
            pass

            # Performance metrics chart
            self._plot_performance_metrics(
                analysis, f"{output_prefix}_performance.png")

            # Cost analysis chart
            self._plot_cost_analysis(analysis, f"{output_prefix}_cost.png")

            # Scaling recommendations chart
            self._plot_scaling_recommendations(
                analysis, f"{output_prefix}_scaling.png")

        except ImportError:
            print("Matplotlib not available, skipping visualizations")

    def _plot_performance_metrics(self, analysis: Dict, filename: str):
        """Plot performance metrics"""
        perf = analysis["performance_metrics"]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))

        # RPS and CPU correlation
        ax1.scatter([perf["requests_per_second"]], [
                    perf["cpu_utilization_avg"]], s=100)
        ax1.set_xlabel("Requests per Second")
        ax1.set_ylabel("CPU Utilization (%)")
        ax1.set_title("RPS vs CPU Utilization")
        ax1.grid(True)

        # Latency distribution
        latencies = [
            perf["latency_p50"],
            perf["latency_p90"],
            perf["latency_p95"],
            perf["latency_p99"],
        ]
        percentiles = ["P50", "P90", "P95", "P99"]
        ax2.bar(percentiles, latencies)
        ax2.set_ylabel("Latency (ms)")
        ax2.set_title("Latency Distribution")

        # Resource utilization
        resources = ["CPU", "Memory"]
        utilization = [
            perf["cpu_utilization_avg"],
            perf["memory_usage_avg_mb"] / 40.96,
        }  # Normalize memory
        ax3.bar(resources, utilization)
        ax3.set_ylabel("Utilization (%)")
        ax3.set_title("Resource Utilization")

        # Performance efficiency
        ax4.bar(["Efficiency"], [perf["performance_efficiency"]])
        ax4.set_ylabel("RPS per CPU %")
        ax4.set_title("Performance Efficiency")

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_cost_analysis(self, analysis: Dict, filename: str):
        """Plot cost analysis"""
        cost = analysis["cost_analysis"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Cost breakdown
        costs = [cost.cpu_cost_per_hour, cost.memory_cost_per_hour]
        labels = ["CPU", "Memory"]
        ax1.pie(costs, labels=labels, autopct="%1.1f%%")
        ax1.set_title("Cost Breakdown (per hour)")

        # Efficiency metrics
        metrics = ["Cost per RPS", "Efficiency Score"]
        values = [cost.cost_per_rps * 1000,
                  cost.efficiency_score]  # Scale cost per RPS
        ax2.bar(metrics, values)
        ax2.set_title("Cost Efficiency Metrics")
        ax2.set_ylabel("Value")

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_scaling_recommendations(self, analysis: Dict, filename: str):
        """Plot scaling recommendations"""
        recommendations = analysis["scaling_recommendations"]

        fig, ax = plt.subplots(figsize=(10, 6))

        scenarios = [rec.reasoning.split()[0] for rec in recommendations]
        replicas = [rec.recommended_replicas for rec in recommendations]
        costs = [rec.cost_impact for rec in recommendations]

        x = np.arange(len(scenarios))
        width = 0.35

        ax1 = ax
        ax2 = ax1.twinx()

        bars1 = ax1.bar(
            x - width / 2,
            replicas,
            width,
            label="Recommended Replicas",
            color="skyblue",
        )
        bars2 = ax2.bar(
            x + width / 2,
            costs,
            width,
            label="Cost Impact ($/hour)",
            color="lightcoral",
        )

        ax1.set_xlabel("Scaling Scenario")
        ax1.set_ylabel("Replicas", color="blue")
        ax2.set_ylabel("Cost Impact ($/hour)", color="red")
        ax1.set_title("Scaling Recommendations Comparison")
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45)

        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def main():
        """Main function"""
        parser = argparse.ArgumentParser(
        description="Analyze k6 load test results and generate scaling recommendations")
        parser.add_argument("results_file", help="Path to k6 results JSON file")
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument(
        "--output", default="analysis_report.json", help="Output report file"
        )
        parser.add_argument(
        "--visualizations", action="store_true", help="Generate visualizations"
        )

        args = parser.parse_args()

        # Initialize analyzer
        analyzer = CostModelAnalyzer(args.config)

        # Analyze results
        print(f"Analyzing load test results from {args.results_file}...")
        analysis = analyzer.analyze_test_results(args.results_file)

        # Generate report
        report = analyzer.generate_report(analysis, args.output)

        # Print summary
        print("\n" + "=" * 50)
        print("LOAD TEST ANALYSIS SUMMARY")
        print("=" * 50)

        summary = report["executive_summary"]
        print(
        f"Current Performance: {
            summary['current_performance'}['rps'}:.1f} RPS"
        )
        print(
        f"CPU Utilization: {
            summary['current_performance'}['cpu_utilization'}:.1f}%"
        )
        print(
        f"Cost per Hour: ${
            summary['current_performance'}['cost_per_hour'}:.2f}"
        )
        print(f"Estimated Monthly Savings: ${summary['estimated_savings']:.2f}")

        print("\nKey Findings:")
        for finding in summary["key_findings"]:
        print(f"  • {finding}")

        print("\nImmediate Actions:")
        for action in summary["immediate_actions"]:
        print(f"  • {action}")

        print("\nTop Recommendations:")
        for rec in report["recommendations"][:3]:
        print(f"  {rec['priority']}. {rec['recommendation']}")
        print(
            f"     Replicas: {
                rec['replicas'}}, Monthly Impact: ${
                rec['cost_impact_monthly'}:.2f}"
        )

        print(f"\nDetailed report saved to: {args.output}")


if __name__ == "__main__":
        main()
