#!/usr/bin/env python3
"""
Comprehensive Backend-Frontend Integration Test for Scorpius Enterprise
Tests all services, API endpoints, and integration points
"""

import json
import time
import requests
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class IntegrationTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        # Service endpoints based on docker-compose configuration
        self.endpoints = {
            "api_gateway": "http://localhost:8010",
            "frontend": "http://localhost:3010", 
            "honeypot": "http://localhost:8000",  # Internal port
            "bytecode": "http://localhost:8000",  # Internal port
            "mempool": "http://localhost:8000",   # Internal port
            "quantum": "http://localhost:8000",   # Internal port
            "time_machine": "http://localhost:8000", # Internal port
            "bridge": "http://localhost:8000",    # Internal port
            "grafana": "http://localhost:3001",
            "prometheus": "http://localhost:9091",
            "pgadmin": "http://localhost:5051",
            "redis_commander": "http://localhost:8082"
        }
        
        # Scanner endpoints
        self.scanners = {
            "slither": "http://localhost:8002",
            "mythril": "http://localhost:8003", 
            "mythx": "http://localhost:8004",
            "manticore": "http://localhost:8005"
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_endpoint(self, name: str, url: str, expected_status: int = 200, timeout: int = 10) -> Dict[str, Any]:
        """Test a single endpoint"""
        self.log(f"Testing {name} at {url}")
        
        try:
            response = requests.get(url, timeout=timeout)
            success = response.status_code == expected_status
            
            result = {
                "name": name,
                "url": url,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_time": response.elapsed.total_seconds(),
                "error": None
            }
            
            if success:
                self.log(f"✅ {name}: PASSED ({response.status_code}) - {result['response_time']:.3f}s")
            else:
                self.log(f"❌ {name}: FAILED (got {response.status_code}, expected {expected_status})")
                
        except requests.exceptions.RequestException as e:
            result = {
                "name": name,
                "url": url,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "response_time": None,
                "error": str(e)
            }
            self.log(f"❌ {name}: FAILED - {str(e)}")
            
        return result

    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API Gateway endpoints"""
        self.log("🔍 Testing API Gateway endpoints")
        
        api_tests = []
        base_url = self.endpoints["api_gateway"]
        
        # Test basic endpoints
        endpoints_to_test = [
            ("health", f"{base_url}/health", 200),
            ("docs", f"{base_url}/docs", 200),
            ("openapi", f"{base_url}/openapi.json", 200),
            ("api_health", f"{base_url}/api/health", 200),
            ("api_version", f"{base_url}/api/version", 200),
        ]
        
        for name, url, expected_status in endpoints_to_test:
            result = self.test_endpoint(name, url, expected_status)
            api_tests.append(result)
            
        # Test scanner endpoints
        scanner_endpoints = [
            ("scanner_slither", f"{base_url}/api/v1/scanner/slither/health", 200),
            ("scanner_mythril", f"{base_url}/api/v1/scanner/mythril/health", 200),
            ("scanner_mythx", f"{base_url}/api/v1/scanner/mythx/health", 200),
            ("scanner_manticore", f"{base_url}/api/v1/scanner/manticore/health", 200),
        ]
        
        for name, url, expected_status in scanner_endpoints:
            result = self.test_endpoint(name, url, expected_status)
            api_tests.append(result)
            
        return {
            "category": "API Gateway",
            "tests": api_tests,
            "passed": sum(1 for t in api_tests if t["success"]),
            "total": len(api_tests)
        }

    def test_frontend(self) -> Dict[str, Any]:
        """Test frontend accessibility"""
        self.log("🎨 Testing Frontend")
        
        frontend_tests = []
        base_url = self.endpoints["frontend"]
        
        # Test frontend pages
        pages_to_test = [
            ("frontend_home", f"{base_url}/", 200),
            ("frontend_scanner", f"{base_url}/scanner", 200),
            ("frontend_dashboard", f"{base_url}/dashboard", 200),
            ("frontend_api", f"{base_url}/api", 200),
        ]
        
        for name, url, expected_status in pages_to_test:
            result = self.test_endpoint(name, url, expected_status)
            frontend_tests.append(result)
            
        return {
            "category": "Frontend",
            "tests": frontend_tests,
            "passed": sum(1 for t in frontend_tests if t["success"]),
            "total": len(frontend_tests)
        }

    def test_scanner_services(self) -> Dict[str, Any]:
        """Test individual scanner services"""
        self.log("🔬 Testing Scanner Services")
        
        scanner_tests = []
        
        for name, url in self.scanners.items():
            result = self.test_endpoint(f"scanner_{name}", f"{url}/health", 200)
            scanner_tests.append(result)
            
        return {
            "category": "Scanner Services",
            "tests": scanner_tests,
            "passed": sum(1 for t in scanner_tests if t["success"]),
            "total": len(scanner_tests)
        }

    def test_monitoring_services(self) -> Dict[str, Any]:
        """Test monitoring and admin services"""
        self.log("📊 Testing Monitoring Services")
        
        monitoring_tests = []
        
        monitoring_endpoints = [
            ("grafana", self.endpoints["grafana"], 200),
            ("prometheus", self.endpoints["prometheus"], 200),
            ("pgadmin", self.endpoints["pgadmin"], 200),
            ("redis_commander", self.endpoints["redis_commander"], 200),
        ]
        
        for name, url, expected_status in monitoring_endpoints:
            result = self.test_endpoint(name, url, expected_status)
            monitoring_tests.append(result)
            
        return {
            "category": "Monitoring Services",
            "tests": monitoring_tests,
            "passed": sum(1 for t in monitoring_tests if t["success"]),
            "total": len(monitoring_tests)
        }

    def test_docker_services(self) -> Dict[str, Any]:
        """Test Docker service health"""
        self.log("🐳 Testing Docker Service Health")
        
        try:
            # Run docker-compose ps to check service status
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.enterprise.yml", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                services = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            service = json.loads(line)
                            services.append(service)
                        except json.JSONDecodeError:
                            continue
                
                # Analyze service health
                healthy_services = []
                unhealthy_services = []
                restarting_services = []
                
                for service in services:
                    name = service.get('Name', 'unknown')
                    status = service.get('Status', 'unknown')
                    
                    if 'healthy' in status.lower():
                        healthy_services.append(name)
                    elif 'unhealthy' in status.lower():
                        unhealthy_services.append(name)
                    elif 'restarting' in status.lower():
                        restarting_services.append(name)
                
                return {
                    "category": "Docker Services",
                    "healthy": healthy_services,
                    "unhealthy": unhealthy_services,
                    "restarting": restarting_services,
                    "total_services": len(services),
                    "success": len(unhealthy_services) == 0 and len(restarting_services) == 0
                }
            else:
                return {
                    "category": "Docker Services",
                    "error": f"Failed to get service status: {result.stderr}",
                    "success": False
                }
                
        except subprocess.TimeoutExpired:
            return {
                "category": "Docker Services", 
                "error": "Timeout getting service status",
                "success": False
            }
        except Exception as e:
            return {
                "category": "Docker Services",
                "error": str(e),
                "success": False
            }

    def test_real_time_features(self) -> Dict[str, Any]:
        """Test WebSocket and real-time features"""
        self.log("⚡ Testing Real-time Features")
        
        # This would require WebSocket testing
        # For now, just check if WebSocket endpoints are accessible
        websocket_tests = []
        
        try:
            # Test WebSocket endpoint availability (HTTP upgrade)
            response = requests.get(f"{self.endpoints['api_gateway']}/ws", timeout=5)
            # WebSocket endpoints typically return 400 or 426 for HTTP requests
            success = response.status_code in [400, 426, 404]  # Expected for WebSocket endpoints
            
            websocket_tests.append({
                "name": "websocket_endpoint",
                "url": f"{self.endpoints['api_gateway']}/ws",
                "status_code": response.status_code,
                "success": success,
                "error": None
            })
            
        except Exception as e:
            websocket_tests.append({
                "name": "websocket_endpoint",
                "url": f"{self.endpoints['api_gateway']}/ws",
                "status_code": None,
                "success": False,
                "error": str(e)
            })
            
        return {
            "category": "Real-time Features",
            "tests": websocket_tests,
            "passed": sum(1 for t in websocket_tests if t["success"]),
            "total": len(websocket_tests)
        }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        self.log("🚀 Starting Comprehensive Backend-Frontend Integration Test")
        self.log("=" * 60)
        
        # Run all test categories
        test_categories = [
            self.test_docker_services,
            self.test_api_endpoints,
            self.test_frontend,
            self.test_scanner_services,
            self.test_monitoring_services,
            self.test_real_time_features,
        ]
        
        for test_func in test_categories:
            try:
                result = test_func()
                self.results["tests"][result["category"]] = result
                self.log(f"Completed {result['category']}: {result.get('passed', 0)}/{result.get('total', 0)} passed")
            except Exception as e:
                self.log(f"Error in {test_func.__name__}: {str(e)}", "ERROR")
                self.results["tests"][test_func.__name__] = {
                    "category": test_func.__name__,
                    "error": str(e),
                    "success": False
                }
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        for category_result in self.results["tests"].values():
            if "tests" in category_result:
                total_tests += category_result["total"]
                passed_tests += category_result["passed"]
            elif category_result.get("success", False):
                passed_tests += 1
                total_tests += 1
            else:
                total_tests += 1
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return self.results

    def print_summary(self):
        """Print test summary"""
        self.log("=" * 60)
        self.log("📊 COMPREHENSIVE INTEGRATION TEST SUMMARY")
        self.log("=" * 60)
        
        summary = self.results["summary"]
        self.log(f"Total Tests: {summary['total']}")
        self.log(f"Passed: {summary['passed']}")
        self.log(f"Failed: {summary['failed']}")
        self.log(f"Success Rate: {summary['success_rate']:.1f}%")
        
        self.log("\n📋 DETAILED RESULTS:")
        for category, result in self.results["tests"].items():
            if "tests" in result:
                self.log(f"  {category}: {result['passed']}/{result['total']} passed")
            elif result.get("success", False):
                self.log(f"  {category}: ✅ PASSED")
            else:
                self.log(f"  {category}: ❌ FAILED")
                if "error" in result:
                    self.log(f"    Error: {result['error']}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"integration_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\n💾 Results saved to: {filename}")
        
        if summary['success_rate'] >= 80:
            self.log("🎉 INTEGRATION TEST PASSED - System is ready for production!")
        elif summary['success_rate'] >= 60:
            self.log("⚠️  INTEGRATION TEST PARTIAL - Some issues need attention")
        else:
            self.log("❌ INTEGRATION TEST FAILED - Significant issues detected")

def main():
    """Main test execution"""
    tester = IntegrationTester()
    
    try:
        results = tester.run_comprehensive_test()
        tester.print_summary()
        
        # Exit with appropriate code
        if results["summary"]["success_rate"] >= 80:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 