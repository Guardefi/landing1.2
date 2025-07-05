"""
Performance Benchmarking Suite for Honeypot Detector API
"""
import asyncio
import csv
import os
import statistics
import sys
import time
from datetime import datetime

import httpx

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


class PerformanceBenchmark:
    """Performance benchmarking for the API"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key = settings.API_KEY
        self.headers = {"X-API-Key": self.api_key}
        self.results = []

    async def benchmark_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        json_data: dict = None,
        iterations: int = 100,
    ):
        """Benchmark a specific endpoint"""
        print(f"📊 Benchmarking {method} {endpoint} ({iterations} iterations)...")

        response_times = []
        status_codes = []
        errors = 0

        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            for i in range(iterations):
                start_time = time.perf_counter()

                try:
                    if method == "GET":
                        response = await client.get(endpoint, headers=self.headers)
                    elif method == "POST":
                        response = await client.post(
                            endpoint, json=json_data, headers=self.headers
                        )
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    end_time = time.perf_counter()
                    duration = end_time - start_time

                    response_times.append(duration)
                    status_codes.append(response.status_code)

                    if i % 20 == 0:
                        print(f"  Progress: {i}/{iterations} ({i/iterations*100:.1f}%)")

                except Exception as e:
                    errors += 1
                    print(f"  Error on iteration {i}: {str(e)}")

                # Small delay to prevent overwhelming the server
                await asyncio.sleep(0.01)

        # Calculate statistics
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": ((iterations - errors) / iterations) * 100,
                "min_time": min(response_times),
                "max_time": max(response_times),
                "avg_time": statistics.mean(response_times),
                "median_time": statistics.median(response_times),
                "p95_time": self.percentile(response_times, 95),
                "p99_time": self.percentile(response_times, 99),
                "requests_per_second": 1 / statistics.mean(response_times)
                if response_times
                else 0,
                "status_codes": dict(
                    zip(
                        *zip(
                            *[
                                (code, status_codes.count(code))
                                for code in set(status_codes)
                            ]
                        )
                    )
                ),
            }

            self.results.append(stats)
            self.print_stats(stats)

            return stats
        else:
            print("❌ No successful requests!")
            return None

    def percentile(self, data, percentile):
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight

    def print_stats(self, stats):
        """Print formatted statistics"""
        print(f"  ✅ Results for {stats['method']} {stats['endpoint']}:")
        print(f"     Success Rate: {stats['success_rate']:.1f}%")
        print(f"     Average Time: {stats['avg_time']*1000:.2f}ms")
        print(f"     Median Time: {stats['median_time']*1000:.2f}ms")
        print(f"     95th Percentile: {stats['p95_time']*1000:.2f}ms")
        print(f"     99th Percentile: {stats['p99_time']*1000:.2f}ms")
        print(f"     Requests/Second: {stats['requests_per_second']:.2f}")
        print(f"     Status Codes: {stats['status_codes']}")
        print()

    async def run_comprehensive_benchmark(self):
        """Run comprehensive benchmarks on all endpoints"""
        print("🚀 Running Comprehensive Performance Benchmark")
        print("=" * 60)

        # Health endpoints
        await self.benchmark_endpoint("/health", iterations=200)
        await self.benchmark_endpoint("/health/status", iterations=100)

        # Dashboard endpoints
        await self.benchmark_endpoint("/api/v1/dashboard/stats", iterations=50)
        await self.benchmark_endpoint("/api/v1/dashboard/trends?days=7", iterations=50)
        await self.benchmark_endpoint(
            "/api/v1/dashboard/search?limit=10", iterations=50
        )

        # Analysis endpoint (might fail if services not configured)
        analysis_data = {
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "chain_id": 1,
            "deep_analysis": False,
        }
        await self.benchmark_endpoint(
            "/api/v1/analyze", method="POST", json_data=analysis_data, iterations=10
        )

        print("=" * 60)
        print("📊 Benchmark Summary")
        print("=" * 60)

        if self.results:
            # Sort by average response time
            sorted_results = sorted(self.results, key=lambda x: x["avg_time"])

            print("🏆 Fastest to Slowest Endpoints:")
            for i, result in enumerate(sorted_results, 1):
                print(
                    f"{i}. {result['method']} {result['endpoint']}: "
                    f"{result['avg_time']*1000:.2f}ms avg, "
                    f"{result['success_rate']:.1f}% success"
                )

            # Generate CSV report
            self.generate_csv_report()

        return self.results

    async def stress_test(self, concurrent_users: int = 10, duration_seconds: int = 30):
        """Stress test with concurrent users"""
        print(
            f"🔥 Stress Test: {concurrent_users} concurrent users for {duration_seconds}s"
        )
        print("=" * 60)

        async def user_simulation(user_id: int):
            """Simulate a user making requests"""
            requests_made = 0
            errors = 0
            start_time = time.time()

            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=10.0
            ) as client:
                while time.time() - start_time < duration_seconds:
                    try:
                        # Simulate typical user behavior
                        endpoints = [
                            "/health",
                            "/api/v1/dashboard/stats",
                            "/api/v1/dashboard/trends?days=7",
                        ]

                        endpoint = endpoints[requests_made % len(endpoints)]
                        response = await client.get(endpoint, headers=self.headers)

                        if response.status_code == 200:
                            requests_made += 1
                        else:
                            errors += 1

                        # Simulate user think time
                        await asyncio.sleep(0.5)

                    except Exception:
                        errors += 1

            return {
                "user_id": user_id,
                "requests": requests_made,
                "errors": errors,
                "duration": time.time() - start_time,
            }

        # Run concurrent users
        tasks = [user_simulation(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)

        # Calculate aggregate stats
        total_requests = sum(r["requests"] for r in user_results)
        total_errors = sum(r["errors"] for r in user_results)
        avg_requests_per_user = total_requests / concurrent_users
        error_rate = (
            (total_errors / (total_requests + total_errors)) * 100
            if (total_requests + total_errors) > 0
            else 0
        )

        print(f"📊 Stress Test Results:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Total Errors: {total_errors}")
        print(f"   Error Rate: {error_rate:.2f}%")
        print(f"   Avg Requests/User: {avg_requests_per_user:.1f}")
        print(f"   Requests/Second: {total_requests / duration_seconds:.2f}")

        return user_results

    def generate_csv_report(self):
        """Generate CSV report of benchmark results"""
        filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "endpoint",
                "method",
                "iterations",
                "success_rate",
                "avg_time_ms",
                "median_time_ms",
                "p95_time_ms",
                "p99_time_ms",
                "requests_per_second",
                "errors",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                row = {
                    "endpoint": result["endpoint"],
                    "method": result["method"],
                    "iterations": result["iterations"],
                    "success_rate": f"{result['success_rate']:.2f}",
                    "avg_time_ms": f"{result['avg_time']*1000:.2f}",
                    "median_time_ms": f"{result['median_time']*1000:.2f}",
                    "p95_time_ms": f"{result['p95_time']*1000:.2f}",
                    "p99_time_ms": f"{result['p99_time']*1000:.2f}",
                    "requests_per_second": f"{result['requests_per_second']:.2f}",
                    "errors": result["errors"],
                }
                writer.writerow(row)

        print(f"📊 Benchmark report saved to: {filename}")


async def main():
    """Main benchmarking function"""
    benchmark = PerformanceBenchmark()

    print("🔬 Honeypot Detector - Performance Benchmark Suite")
    print("Make sure the API is running on http://localhost:8000")
    print("=" * 60)

    # Run comprehensive benchmark
    await benchmark.run_comprehensive_benchmark()

    # Run stress test
    await benchmark.stress_test(concurrent_users=5, duration_seconds=15)

    print("\n🎉 Performance benchmarking completed!")
    print("Check the generated CSV file for detailed results.")


if __name__ == "__main__":
    asyncio.run(main())
