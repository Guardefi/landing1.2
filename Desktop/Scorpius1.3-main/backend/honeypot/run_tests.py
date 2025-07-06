"""
Master Test Runner for Honeypot Detector API
Runs all test suites and generates comprehensive reports
"""
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """Master test runner"""

    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"🔬 {title}")
        print("=" * 70)

    def print_section(self, title):
        """Print formatted section"""
        print(f"\n📋 {title}")
        print("-" * 50)

    async def check_dependencies(self):
        """Check if required dependencies are available"""
        self.print_section("Checking Dependencies")

        dependencies = {
            "Python": {"cmd": [sys.executable, "--version"], "required": True},
            "FastAPI": {"module": "fastapi", "required": True},
            "httpx": {"module": "httpx", "required": True},
            "MongoDB": {"service": "mongodb://localhost:27017", "required": False},
            "Redis": {"service": "redis://localhost:6379", "required": False},
        }

        results = {}

        for name, config in dependencies.items():
            try:
                if "cmd" in config:
                    result = subprocess.run(
                        config["cmd"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ {name}: {result.stdout.strip()}")
                        results[name] = "available"
                    else:
                        print(f"❌ {name}: Not found")
                        results[name] = "missing"

                elif "module" in config:
                    __import__(config["module"])
                    print(f"✅ {name}: Available")
                    results[name] = "available"

                elif "service" in config:
                    # We'll test services during actual tests
                    print(f"⏳ {name}: Will test during service tests")
                    results[name] = "pending"

            except Exception as e:
                print(f"❌ {name}: {str(e)}")
                results[name] = "error"
                if config.get("required", False):
                    print(f"🚨 {name} is required but not available!")

        return results

    async def run_api_server_check(self):
        """Check if API server is running"""
        self.print_section("API Server Health Check")

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                if response.status_code == 200:
                    print("✅ API server is running and responding")
                    return True
                else:
                    print(
                        f"⚠️ API server responded with status: {response.status_code}"
                    )
                    return False
        except Exception as e:
            print(f"❌ API server not reachable: {str(e)}")
            print("🔧 To start the server, run: python start_api.py")
            return False

    async def run_comprehensive_tests(self):
        """Run comprehensive test suite"""
        self.print_section("Running Comprehensive Tests")

        try:
            from test_comprehensive import main as comprehensive_main

            result = await comprehensive_main()
            self.test_results["comprehensive"] = result
            return result
        except Exception as e:
            print(f"❌ Comprehensive tests failed: {str(e)}")
            self.test_results["comprehensive"] = False
            return False

    async def run_react_integration_tests(self):
        """Run React integration tests"""
        self.print_section("Running React Integration Tests")

        try:
            from test_react_integration import main as react_main

            result = await react_main()
            self.test_results["react_integration"] = result
            return result
        except Exception as e:
            print(f"❌ React integration tests failed: {str(e)}")
            self.test_results["react_integration"] = False
            return False

    async def run_performance_tests(self):
        """Run performance benchmarks"""
        self.print_section("Running Performance Benchmarks")

        try:
            from test_performance import PerformanceBenchmark

            benchmark = PerformanceBenchmark()
            results = await benchmark.run_comprehensive_benchmark()
            self.test_results["performance"] = len(results) > 0
            return len(results) > 0
        except Exception as e:
            print(f"❌ Performance tests failed: {str(e)}")
            self.test_results["performance"] = False
            return False

    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_section("Generating Test Report")

        report = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": (self.end_time - self.start_time).total_seconds()
                if self.end_time and self.start_time
                else 0,
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "test_results": self.test_results,
            "summary": {
                "total_test_suites": len(self.test_results),
                "passed_suites": sum(
                    1 for result in self.test_results.values() if result
                ),
                "failed_suites": sum(
                    1 for result in self.test_results.values() if not result
                ),
                "success_rate": (
                    sum(1 for result in self.test_results.values() if result)
                    / len(self.test_results)
                )
                * 100
                if self.test_results
                else 0,
            },
        }

        # Save report to file
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Test report saved to: {report_filename}")

        # Print summary
        print("\n📋 Test Summary:")
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {suite_name}: {status}")

        print(f"\n🎯 Overall Success Rate: {report['summary']['success_rate']:.1f}%")

        return report

    async def run_all_tests(self):
        """Run all test suites"""
        self.start_time = datetime.now()

        self.print_header("Honeypot Detector API - Master Test Suite")

        # Check dependencies
        deps = await self.check_dependencies()

        # Check if API server is running
        server_running = await self.run_api_server_check()

        if not server_running:
            print("\n🚨 API server is not running. Some tests will be skipped.")
            print("🔧 Start the server with: python start_api.py")
            response = input("\nDo you want to continue with available tests? (y/n): ")
            if response.lower() != "y":
                return False

        # Run test suites
        if server_running:
            await self.run_comprehensive_tests()
            await self.run_react_integration_tests()
            await self.run_performance_tests()
        else:
            print("⏭️ Skipping server-dependent tests")

        self.end_time = datetime.now()

        # Generate report
        report = self.generate_test_report()

        # Final status
        if all(self.test_results.values()):
            print(
                "\n🎉 ALL TESTS PASSED! Your honeypot detector is ready for production!"
            )
            print("\n🚀 Next Steps:")
            print("1. Deploy to your production environment")
            print("2. Configure your React dashboard to use the API endpoints")
            print("3. Set up monitoring and logging")
            print("4. Configure SSL/HTTPS for production")
        else:
            print(
                "\n⚠️ Some tests failed. Please review the output above and fix issues."
            )
            print("\n🔧 Common fixes:")
            print("- Ensure MongoDB and Redis are running")
            print("- Check your .env configuration")
            print("- Verify all dependencies are installed")

        return all(self.test_results.values())


def print_usage():
    """Print usage instructions"""
    print("🔬 Honeypot Detector API - Test Suite")
    print("=" * 50)
    print("\nUsage:")
    print("  python run_tests.py                 # Run all tests")
    print("  python run_tests.py --quick         # Run only quick tests")
    print("  python run_tests.py --performance   # Run only performance tests")
    print("  python run_tests.py --help          # Show this help")
    print("\nPrerequisites:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the API server: python start_api.py")
    print("3. Ensure MongoDB and Redis are running (optional for some tests)")
    print("\nFor React integration:")
    print("- Check the sample_data_for_react.json file after tests")
    print("- Use API key: honeypot-detector-api-key-12345")
    print("- Base URL: http://localhost:8000")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        if "--help" in sys.argv:
            print_usage()
            return
        elif "--quick" in sys.argv:
            print("🏃 Running quick tests only...")
            # Run only basic tests
        elif "--performance" in sys.argv:
            print("⚡ Running performance tests only...")
            from test_performance import main as perf_main

            await perf_main()
            return

    # Run full test suite
    runner = TestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {str(e)}")
        sys.exit(1)
