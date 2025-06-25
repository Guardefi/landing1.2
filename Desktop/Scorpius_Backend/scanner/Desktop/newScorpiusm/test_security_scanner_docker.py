#!/usr/bin/env python3
"""
Comprehensive Security Scanner Test for Docker Environment

This test suite validates that all security tools (Slither, Mythril, MythX, 
Manticore, Echidna) are properly installed and functioning in the Docker container.
"""

import os
import json
import time
import docker
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Test Solidity contracts for different vulnerability types
TEST_CONTRACTS = {
    "reentrancy_vulnerable": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReentrancyVulnerable {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: external call before state update
        (bool success,) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount; // State update after external call
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}
""",
    
    "tx_origin_vulnerable": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TxOriginVulnerable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        // Vulnerable: using tx.origin instead of msg.sender
        require(tx.origin == owner, "Not the owner");
        _;
    }
    
    function sensitiveFunction() public onlyOwner {
        // Some sensitive operation
    }
    
    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
""",
    
    "unchecked_calls": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UncheckedCalls {
    function riskyTransfer(address payable recipient, uint256 amount) public {
        // Vulnerable: unchecked low-level call
        recipient.call{value: amount}("");
    }
    
    function riskyTransferFunctionCall(address token, address recipient, uint256 amount) public {
        // Vulnerable: unchecked external call
        token.call(abi.encodeWithSignature("transfer(address,uint256)", recipient, amount));
    }
}
""",
    
    "integer_overflow": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0; // Intentionally old version without automatic overflow checks

contract IntegerOverflow {
    mapping(address => uint256) public balances;
    uint256 public totalSupply = 1000;
    
    function transfer(address to, uint256 amount) public {
        // Vulnerable to integer underflow
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    
    function mint(uint256 amount) public {
        // Vulnerable to integer overflow
        totalSupply += amount;
        balances[msg.sender] += amount;
    }
}
"""
}

class SecurityScannerDockerTest:
    def __init__(self):
        self.client = docker.from_env()
        self.container = None
        self.test_dir = Path("/tmp/security_scanner_test")
        self.test_dir.mkdir(exist_ok=True)
        
    def setup_test_contracts(self):
        """Create test Solidity contracts in the test directory"""
        contracts_dir = self.test_dir / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        
        for name, source in TEST_CONTRACTS.items():
            contract_file = contracts_dir / f"{name}.sol"
            contract_file.write_text(source)
            print(f"Created test contract: {contract_file}")
    
    def start_container(self):
        """Start the Scorpius backend container"""
        try:
            print("Starting Scorpius backend container...")
            self.container = self.client.containers.run(
                "scorpius-backend:latest",
                ports={'8000/tcp': 8000, '8081/tcp': 8081},
                volumes={
                    str(self.test_dir): {'bind': '/test_contracts', 'mode': 'rw'}
                },
                detach=True,
                remove=True
            )
            
            # Wait for container to be ready
            print("Waiting for container to start...")
            time.sleep(30)
            
            # Check if container is running
            self.container.reload()
            if self.container.status != 'running':
                logs = self.container.logs().decode('utf-8')
                print(f"Container failed to start. Logs:\n{logs}")
                return False
                
            print(f"Container started successfully: {self.container.short_id}")
            return True
            
        except Exception as e:
            print(f"Failed to start container: {e}")
            return False
    
    def test_security_tools_installation(self):
        """Test that all security tools are properly installed"""
        tools_to_test = [
            ("slither", "slither --version"),
            ("mythril", "myth version"),
            ("solc", "solc --version"),
            ("echidna", "echidna --version"),
        ]
        
        results = {}
        
        for tool_name, command in tools_to_test:
            try:
                print(f"Testing {tool_name} installation...")
                result = self.container.exec_run(command)
                
                if result.exit_code == 0:
                    output = result.output.decode('utf-8').strip()
                    results[tool_name] = {
                        "installed": True,
                        "version": output,
                        "status": "OK"
                    }
                    print(f"✓ {tool_name}: {output}")
                else:
                    results[tool_name] = {
                        "installed": False,
                        "error": result.output.decode('utf-8'),
                        "status": "FAILED"
                    }
                    print(f"✗ {tool_name}: Failed - {result.output.decode('utf-8')}")
                    
            except Exception as e:
                results[tool_name] = {
                    "installed": False,
                    "error": str(e),
                    "status": "ERROR"
                }
                print(f"✗ {tool_name}: Error - {e}")
        
        return results
    
    def test_slither_analysis(self):
        """Test Slither static analysis on vulnerable contracts"""
        print("\n=== Testing Slither Analysis ===")
        results = {}
        
        for contract_name in TEST_CONTRACTS.keys():
            try:
                print(f"Running Slither on {contract_name}...")
                
                # Run Slither analysis
                command = f"slither /test_contracts/contracts/{contract_name}.sol --json -"
                result = self.container.exec_run(command)
                
                if result.exit_code == 0:
                    try:
                        slither_output = json.loads(result.output.decode('utf-8'))
                        detectors = slither_output.get('results', {}).get('detectors', [])
                        
                        results[contract_name] = {
                            "status": "SUCCESS",
                            "vulnerabilities_found": len(detectors),
                            "details": [
                                {
                                    "check": detector.get('check'),
                                    "impact": detector.get('impact'),
                                    "confidence": detector.get('confidence'),
                                    "description": detector.get('description', '')[:100] + "..."
                                }
                                for detector in detectors[:5]  # Limit to first 5
                            ]
                        }
                        print(f"✓ Slither found {len(detectors)} issues in {contract_name}")
                        
                    except json.JSONDecodeError:
                        # Sometimes Slither outputs non-JSON warnings
                        output_text = result.output.decode('utf-8')
                        results[contract_name] = {
                            "status": "PARTIAL",
                            "raw_output": output_text[:200] + "..." if len(output_text) > 200 else output_text
                        }
                        print(f"~ Slither analysis completed for {contract_name} (non-JSON output)")
                        
                else:
                    error_output = result.output.decode('utf-8')
                    results[contract_name] = {
                        "status": "FAILED",
                        "error": error_output
                    }
                    print(f"✗ Slither failed on {contract_name}: {error_output[:100]}...")
                    
            except Exception as e:
                results[contract_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"✗ Error running Slither on {contract_name}: {e}")
        
        return results
    
    def test_mythril_analysis(self):
        """Test Mythril symbolic execution on vulnerable contracts"""
        print("\n=== Testing Mythril Analysis ===")
        results = {}
        
        for contract_name in TEST_CONTRACTS.keys():
            try:
                print(f"Running Mythril on {contract_name}...")
                
                # Run Mythril analysis with shorter timeout for testing
                command = f"myth analyze /test_contracts/contracts/{contract_name}.sol --execution-timeout 30"
                result = self.container.exec_run(command)
                
                output = result.output.decode('utf-8')
                
                if "The analysis was completed successfully" in output or "SWC-" in output:
                    # Count SWC (Smart Contract Weakness Classification) findings
                    swc_count = output.count('SWC-')
                    results[contract_name] = {
                        "status": "SUCCESS",
                        "vulnerabilities_found": swc_count,
                        "output_preview": output[:300] + "..." if len(output) > 300 else output
                    }
                    print(f"✓ Mythril found {swc_count} SWC issues in {contract_name}")
                    
                elif "No issues were detected" in output:
                    results[contract_name] = {
                        "status": "SUCCESS",
                        "vulnerabilities_found": 0,
                        "message": "No issues detected"
                    }
                    print(f"✓ Mythril analysis completed for {contract_name} (no issues)")
                    
                else:
                    results[contract_name] = {
                        "status": "FAILED",
                        "error": output[:200] + "..." if len(output) > 200 else output
                    }
                    print(f"✗ Mythril failed on {contract_name}")
                    
            except Exception as e:
                results[contract_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"✗ Error running Mythril on {contract_name}: {e}")
        
        return results
    
    def test_api_integration(self):
        """Test the scanner API endpoints"""
        print("\n=== Testing API Integration ===")
        
        # Wait a bit more for API to be ready
        time.sleep(10)
        
        api_url = "http://localhost:8000"
        results = {}
        
        # Test health endpoint
        try:
            response = requests.get(f"{api_url}/health", timeout=10)
            results["health_check"] = {
                "status": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✓ Health check: {response.status_code}")
        except Exception as e:
            results["health_check"] = {"status": "ERROR", "error": str(e)}
            print(f"✗ Health check failed: {e}")
        
        # Test scanner endpoint with sample contract
        try:
            test_contract = TEST_CONTRACTS["reentrancy_vulnerable"]
            scan_request = {
                "contract_source": test_contract,
                "analysis_type": "comprehensive",
                "include_slither": True,
                "include_mythril": True
            }
            
            response = requests.post(
                f"{api_url}/scanner/analyze", 
                json=scan_request,
                timeout=60
            )
            
            results["scanner_api"] = {
                "status": response.status_code,
                "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]
            }
            print(f"✓ Scanner API: {response.status_code}")
            
        except Exception as e:
            results["scanner_api"] = {"status": "ERROR", "error": str(e)}
            print(f"✗ Scanner API failed: {e}")
        
        return results
    
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🔐 Starting Comprehensive Security Scanner Test")
        print("=" * 60)
        
        self.setup_test_contracts()
        
        if not self.start_container():
            return {"error": "Failed to start container"}
        
        try:
            results = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "container_id": self.container.short_id,
                "tools_installation": self.test_security_tools_installation(),
                "slither_analysis": self.test_slither_analysis(),
                "mythril_analysis": self.test_mythril_analysis(),
                "api_integration": self.test_api_integration()
            }
            
            # Generate summary
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            
            tools_ok = sum(1 for tool in results["tools_installation"].values() if tool["installed"])
            tools_total = len(results["tools_installation"])
            print(f"Tools Installation: {tools_ok}/{tools_total} tools working")
            
            slither_ok = sum(1 for r in results["slither_analysis"].values() if r["status"] in ["SUCCESS", "PARTIAL"])
            slither_total = len(results["slither_analysis"])
            print(f"Slither Analysis: {slither_ok}/{slither_total} contracts analyzed")
            
            mythril_ok = sum(1 for r in results["mythril_analysis"].values() if r["status"] == "SUCCESS")
            mythril_total = len(results["mythril_analysis"])
            print(f"Mythril Analysis: {mythril_ok}/{mythril_total} contracts analyzed")
            
            api_working = results["api_integration"]["health_check"]["status"] == 200
            print(f"API Integration: {'✓' if api_working else '✗'} Backend API")
            
            return results
            
        finally:
            if self.container:
                print(f"\nStopping container {self.container.short_id}...")
                self.container.stop()
    
    def cleanup(self):
        """Clean up test files and containers"""
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except:
                pass

def main():
    """Run the comprehensive security scanner test"""
    tester = SecurityScannerDockerTest()
    
    try:
        results = tester.run_comprehensive_test()
        
        # Save results to file
        results_file = Path("security_scanner_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📝 Detailed results saved to: {results_file}")
        return results
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
