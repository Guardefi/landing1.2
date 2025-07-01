#!/usr/bin/env python3
"""
Enterprise Test Runner for Scorpius
Clean, reliable test execution system.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import glob


class EnterpriseTestRunner:
    """Enterprise-grade test runner for systematic test execution"""

    def __init__(self):
        self.results = {
            "total_found": 0,
            "total_run": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "details": []
        }
        self.project_root = Path(__file__).parent

    def find_test_files(self):
        """Find all test files systematically"""
        test_files = set()

        # Search for different patterns
        test_files.update(self.project_root.rglob("test_*.py"))
        test_files.update(self.project_root.rglob("*test*.py"))

        # Filter out problematic files
        excluded_patterns = [
            "conftest.py",
            "__pycache__",
            "fix_",
            "test_runner",
            ".backup",
            "__init__.py"
        ]

        filtered_files = []
        for test_file in test_files:
            skip = False
            for pattern in excluded_patterns:
                if pattern in str(test_file):
                    skip = True
                    break
            if not skip and test_file.suffix == '.py':
                filtered_files.append(test_file)

        return sorted(filtered_files)

    def analyze_test_file(self, test_file):
        """Analyze test file structure"""
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return {
                "has_main": '__name__ == "__main__"' in content,
                "has_pytest": "pytest" in content,
                "has_unittest": "unittest" in content or "TestCase" in content,
                "has_asyncio": "asyncio" in content or "async def" in content,
                "file_size": len(content),
                "line_count": len(content.split('\n'))
            }
        except Exception as e:
            return {"error": str(e)}

    def run_test_file(self, test_file):
        """Run a single test file"""
        original_cwd = os.getcwd()
        try:
            # Change to test file directory
            test_dir = test_file.parent
            os.chdir(test_dir)

            # Add test directory to Python path
            sys.path.insert(0, str(test_dir))

            # Run the test file
            result = subprocess.run([sys.executable,
                                     str(test_file)],
                                    capture_output=True,
                                    text=True,
                                    timeout=60,
                                    encoding='utf-8',
                                    errors='replace')

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Test timed out after 60 seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Error running test: {str(e)}",
                "returncode": -1
            }
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if str(test_file.parent) in sys.path:
                sys.path.remove(str(test_file.parent))

    def run_single_test(self, test_file):
        """Execute a single test with full reporting"""
        print(f"\n{'='*60}")
        print(f"Running: {test_file.relative_to(self.project_root)}")
        print(f"{'='*60}")

        # Analyze the test file first
        analysis = self.analyze_test_file(test_file)

        if "error" in analysis:
            print(f"[ERROR] Failed to analyze: {analysis['error']}")
            self.results["errors"] += 1
            self.results["details"].append({
                "file": str(test_file.relative_to(self.project_root)),
                "status": "error",
                "message": f"Analysis error: {analysis['error']}"
            })
            return

        print(
            f"Analysis: main={
                analysis['has_main']}, pytest={
                analysis['has_pytest']}, unittest={
                analysis['has_unittest']}")

        # Skip files without main execution
        if not analysis["has_main"]:
            print("[SKIP] No main execution block")
            self.results["skipped"] += 1
            self.results["details"].append({
                "file": str(test_file.relative_to(self.project_root)),
                "status": "skipped",
                "message": "No main execution block found"
            })
            return

        # Run the test
        result = self.run_test_file(test_file)

        if result["success"]:
            print("[PASS] SUCCESS")
            self.results["passed"] += 1
            self.results["details"].append({
                "file": str(test_file.relative_to(self.project_root)),
                "status": "passed",
                "message": "Test completed successfully"
            })
            if result["stdout"]:
                # Truncate long output
                print(f"OUTPUT: {result['stdout'][:500]}...")
        else:
            print(f"[FAIL] FAILED")
            print(f"Return code: {result['returncode']}")
            if result["stderr"]:
                # Truncate long errors
                print(f"STDERR: {result['stderr'][:500]}...")

            self.results["failed"] += 1
            self.results["details"].append({
                "file": str(test_file.relative_to(self.project_root)),
                "status": "failed",
                "message": f"Exit code {result['returncode']}"
            })

    def run_all_tests(self):
        """Execute all tests systematically"""
        print(">> Scorpius Enterprise Test Runner")
        print("=" * 60)

        # Find all test files
        test_files = self.find_test_files()
        print(f"Found {len(test_files)} test files")

        self.results["total_found"] = len(test_files)

        # Execute each test
        for i, test_file in enumerate(test_files, 1):
            print(f"\n[{i}/{len(test_files)}] Processing: {test_file.name}")
            try:
                self.run_single_test(test_file)
                self.results["total_run"] += 1
            except KeyboardInterrupt:
                print("\n>> Test execution interrupted by user")
                break
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                self.results["errors"] += 1
                self.results["total_run"] += 1

    def print_summary(self):
        """Print comprehensive test summary"""
        print(f"\n{'='*60}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total found: {self.results['total_found']}")
        print(f"Total run: {self.results['total_run']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Skipped: {self.results['skipped']}")
        print(f"Errors: {self.results['errors']}")

        if self.results['total_run'] > 0:
            success_rate = (
                self.results['passed'] / self.results['total_run']) * 100
            print(f"Success rate: {success_rate:.1f}%")

        # Save detailed results
        with open('enterprise_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nDetailed results saved to enterprise_test_results.json")


def main():
    """Main execution function"""
    runner = EnterpriseTestRunner()

    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n>> Test execution interrupted")
    finally:
        runner.print_summary()

    return runner.results['failed'] == 0 and runner.results['errors'] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
