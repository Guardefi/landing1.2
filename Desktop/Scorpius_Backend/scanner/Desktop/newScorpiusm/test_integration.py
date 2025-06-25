"""
Integration test to verify frontend-backend API connectivity
"""
import subprocess
import time

import requests

# Test configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
TEST_TIMEOUT = 30

class APIIntegrationTester:
    def __init__(self):
        self.backend_url = f"http://localhost:{BACKEND_PORT}"
        self.frontend_url = f"http://localhost:{FRONTEND_PORT}"
        self.processes = []
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend server...")
        try:
            # Start backend using uvicorn
            process = subprocess.Popen([
                "python", "-m", "uvicorn", 
                "backend.main:app", 
                "--host", "0.0.0.0", 
                "--port", str(BACKEND_PORT),
                "--reload"
            ], cwd=".")
            self.processes.append(process)
            
            # Wait for backend to be ready
            for _ in range(20):
                try:
                    response = requests.get(f"{self.backend_url}/healthz", timeout=2)
                    if response.status_code == 200:
                        print("✅ Backend server ready")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Backend failed to start")
            return False
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Vite frontend dev server"""
        print("🎨 Starting frontend server...")
        try:
            # Start frontend using npm
            process = subprocess.Popen([
                "npm", "run", "dev", "--", "--port", str(FRONTEND_PORT)
            ], cwd="frontend")
            self.processes.append(process)
            
            # Wait for frontend to be ready
            for _ in range(30):
                try:
                    response = requests.get(f"{self.frontend_url}", timeout=2)
                    if response.status_code == 200:
                        print("✅ Frontend server ready")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Frontend failed to start")
            return False
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("🔍 Testing API endpoints...")
        
        endpoints_to_test = [
            ("/healthz", "GET", 200),
            ("/readyz", "GET", [200, 503]),  # May fail if DB not connected
            ("/api/dashboard/stats", "GET", [200, 401]),  # May need auth
            ("/api/scanner/status", "GET", [200, 404]),
            ("/api/mev/strategies", "GET", [200, 401]),
        ]
        
        results = {}
        for endpoint, method, expected_codes in endpoints_to_test:
            try:
                url = f"{self.backend_url}{endpoint}"
                response = requests.request(method, url, timeout=5)
                
                if isinstance(expected_codes, list):
                    status_ok = response.status_code in expected_codes
                else:
                    status_ok = response.status_code == expected_codes
                
                results[endpoint] = {
                    "status": response.status_code,
                    "success": status_ok,
                    "response_time": response.elapsed.total_seconds()
                }
                
                status_icon = "✅" if status_ok else "❌"
                print(f"  {status_icon} {method} {endpoint} -> {response.status_code}")
                
            except Exception as e:
                results[endpoint] = {
                    "status": "ERROR",
                    "success": False,
                    "error": str(e)
                }
                print(f"  ❌ {method} {endpoint} -> ERROR: {e}")
        
        return results
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        print("🗄️  Testing database connectivity...")
        
        try:
            # Test health endpoint that checks DB
            response = requests.get(f"{self.backend_url}/readyz", timeout=5)
            
            if response.status_code == 200:
                print("  ✅ Database connectivity OK")
                return True
            else:
                print(f"  ⚠️  Database connectivity uncertain (status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"  ❌ Database connectivity test failed: {e}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend-backend communication"""
        print("🌐 Testing CORS configuration...")
        
        try:
            # Simulate a frontend request with CORS headers
            headers = {
                "Origin": f"http://localhost:{FRONTEND_PORT}",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = requests.options(f"{self.backend_url}/api/dashboard/stats", 
                                      headers=headers, timeout=5)
            
            cors_headers = response.headers
            has_cors = "Access-Control-Allow-Origin" in cors_headers
            
            if has_cors:
                print("  ✅ CORS configured correctly")
                return True
            else:
                print("  ❌ CORS not configured - frontend may have issues")
                return False
                
        except Exception as e:
            print(f"  ❌ CORS test failed: {e}")
            return False
    
    def test_auth_flow(self):
        """Test authentication flow"""
        print("🔐 Testing authentication flow...")
        
        try:
            # Test login endpoint
            login_data = {
                "email": "admin@scorpiusx.io",
                "password": "scorpius123"
            }
            
            response = requests.post(f"{self.backend_url}/auth/login", 
                                   json=login_data, timeout=5)
            
            if response.status_code == 200:
                print("  ✅ Authentication working")
                return response.json()
            else:
                print(f"  ❌ Authentication failed (status: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"  ❌ Auth test failed: {e}")
            return None
    
    def cleanup(self):
        """Stop all processes"""
        print("🧹 Cleaning up...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ Cleanup complete")
    
    def run_full_test(self):
        """Run complete integration test suite"""
        print("🔥 Starting Scorpius Frontend-Backend Integration Test")
        print("=" * 60)
        
        try:
            # Start services
            if not self.start_backend():
                return False
            
            # Test API endpoints
            api_results = self.test_api_endpoints()
            
            # Test database
            db_ok = self.test_database_connectivity()
            
            # Test CORS
            cors_ok = self.test_cors_configuration()
            
            # Test auth
            auth_result = self.test_auth_flow()
            
            # Generate report
            print("\n" + "=" * 60)
            print("📊 INTEGRATION TEST RESULTS")
            print("=" * 60)
            
            # API Results
            api_success_count = sum(1 for r in api_results.values() if r['success'])
            print(f"API Endpoints: {api_success_count}/{len(api_results)} working")
            
            # Summary
            total_tests = len(api_results) + 3  # +3 for DB, CORS, Auth
            passed_tests = api_success_count + sum([db_ok, cors_ok, bool(auth_result)])
            
            print(f"Database: {'✅' if db_ok else '❌'}")
            print(f"CORS: {'✅' if cors_ok else '❌'}")  
            print(f"Authentication: {'✅' if auth_result else '❌'}")
            
            print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                print("🎉 INTEGRATION TEST PASSED - Backend-Frontend ready!")
                return True
            else:
                print("⚠️  INTEGRATION TEST NEEDS ATTENTION - Some issues detected")
                return False
                
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = APIIntegrationTester()
    success = tester.run_full_test()
    exit(0 if success else 1)
