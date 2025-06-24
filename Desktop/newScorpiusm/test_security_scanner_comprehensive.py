#!/usr/bin/env python3
"""
Comprehensive Security Scanner Test
Tests the real vulnerability scanner with actual security tools in Docker environment.
"""

import asyncio
import json
import os
import tempfile
import time
from typing import Dict, List

import requests

# Test contracts with various vulnerabilities
TEST_CONTRACTS = {
    "reentrancy_vulnerable": """
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable to reentrancy - external call before state change
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;  // State change after external call
    }
}
""",

    "tx_origin_vulnerable": """
pragma solidity ^0.8.0;

contract TxOriginVulnerable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        // Vulnerable: using tx.origin instead of msg.sender
        require(tx.origin == owner, "Not owner");
        _;
    }
    
    function sensitiveFunction() public onlyOwner {
        // Some sensitive operation
    }
}
""",

    "unchecked_transfer": """
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract UncheckedTransfer {
    IERC20 public token;
    
    constructor(address _token) {
        token = IERC20(_token);
    }
    
    function transferTokens(address to, uint256 amount) public {
        // Vulnerable: not checking return value
        token.transfer(to, amount);
    }
}
""",

    "integer_overflow": """
pragma solidity ^0.7.6; // Using older version without built-in overflow protection

contract IntegerOverflow {
    mapping(address => uint256) public balances;
    
    function add(uint256 amount) public {
        // Vulnerable to integer overflow in older Solidity versions
        balances[msg.sender] += amount;
    }
    
    function subtract(uint256 amount) public {
        // Vulnerable to integer underflow
        balances[msg.sender] -= amount;
    }
}
""",

    "access_control": """
pragma solidity ^0.8.0;

contract AccessControlIssue {
    address public admin;
    mapping(address => bool) public authorized;
    
    constructor() {
        admin = msg.sender;
    }
    
    // Missing access control modifier
    function setAdmin(address newAdmin) public {
        admin = newAdmin;
    }
    
    // Missing access control
    function authorize(address user) public {
        authorized[user] = true;
    }
    
    function criticalFunction() public {
        require(authorized[msg.sender], "Not authorized");
        // Critical operation
    }
}
"""
}

class SecurityScannerTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def wait_for_service(self, timeout: int = 60) -> bool:
        """Wait for the scanner service to be available."""
        print(f"Waiting for scanner service at {self.base_url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Scanner service is available!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            print("⏳ Still waiting for scanner service...")
        
        print("❌ Scanner service did not become available within timeout")
        return False
    
    def test_scan_endpoint(self, contract_name: str, contract_code: str) -> Dict:
        """Test the vulnerability scanning endpoint with a contract."""
        print(f"\n🔍 Testing vulnerability scan for: {contract_name}")
        
        # Create a temporary file for the contract
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(contract_code)
            contract_file = f.name
        
        try:
            # Test direct code scanning
            scan_request = {
                "source_code": contract_code,
                "contract_name": contract_name,
                "enable_mythril": True,
                "enable_slither": True,
                "enable_manticore": True,
                "enable_echidna": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/scanner/scan",
                json=scan_request,
                timeout=120  # Long timeout for comprehensive analysis
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.print_scan_results(contract_name, result)
                return result
            else:
                print(f"❌ Scan failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return {}
                
        finally:
            # Cleanup temporary file
            try:
                os.unlink(contract_file)
            except:
                pass
    
    def print_scan_results(self, contract_name: str, results: Dict):
        """Print formatted scan results."""
        print(f"\n📋 Scan Results for {contract_name}:")
        print("=" * 60)
        
        # Print summary
        if "summary" in results:
            summary = results["summary"]
            print(f"🎯 Total vulnerabilities found: {summary.get('total_issues', 0)}")
            print(f"🔴 High severity: {summary.get('high_severity', 0)}")
            print(f"🟡 Medium severity: {summary.get('medium_severity', 0)}")
            print(f"🟢 Low severity: {summary.get('low_severity', 0)}")
        
        # Print tool-specific results
        tools = ["mythril", "slither", "manticore", "echidna"]
        for tool in tools:
            if tool in results:
                tool_results = results[tool]
                print(f"\n🔧 {tool.upper()} Results:")
                
                if "vulnerabilities" in tool_results:
                    vulns = tool_results["vulnerabilities"]
                    if vulns:
                        for i, vuln in enumerate(vulns, 1):
                            severity = vuln.get("severity", "unknown").upper()
                            title = vuln.get("title", "Unknown vulnerability")
                            print(f"  {i}. [{severity}] {title}")
                            if "description" in vuln:
                                desc = vuln["description"][:100] + "..." if len(vuln["description"]) > 100 else vuln["description"]
                                print(f"     📝 {desc}")
                    else:
                        print("  ✅ No vulnerabilities detected")
                
                if "errors" in tool_results and tool_results["errors"]:
                    print(f"  ⚠️ Tool errors: {tool_results['errors']}")
    
    def test_tool_availability(self) -> Dict[str, bool]:
        """Test which security tools are available in the container."""
        print("\n🔧 Testing security tool availability...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/scanner/tools/status")
            if response.status_code == 200:
                tools_status = response.json()
                print("\n📋 Tool Availability:")
                for tool, available in tools_status.items():
                    status = "✅" if available else "❌"
                    print(f"  {status} {tool}")
                return tools_status
            else:
                print(f"❌ Failed to get tools status: {response.status_code}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking tools status: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Run comprehensive vulnerability scanner tests."""
        print("🚀 Starting Comprehensive Security Scanner Test")
        print("=" * 60)
        
        # Wait for service to be available
        if not self.wait_for_service():
            print("❌ Cannot proceed - scanner service is not available")
            return False
        
        # Test tool availability
        tools_status = self.test_tool_availability()
        
        # Test each contract
        all_results = {}
        for contract_name, contract_code in TEST_CONTRACTS.items():
            result = self.test_scan_endpoint(contract_name, contract_code)
            all_results[contract_name] = result
            time.sleep(2)  # Brief pause between tests
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 60)
        
        total_contracts = len(TEST_CONTRACTS)
        successful_scans = len([r for r in all_results.values() if r])
        
        print(f"📦 Total contracts tested: {total_contracts}")
        print(f"✅ Successful scans: {successful_scans}")
        print(f"❌ Failed scans: {total_contracts - successful_scans}")
        
        # Count total vulnerabilities found
        total_vulns = 0
        for contract_name, results in all_results.items():
            if results and "summary" in results:
                total_vulns += results["summary"].get("total_issues", 0)
        
        print(f"🎯 Total vulnerabilities detected: {total_vulns}")
        
        # Tool performance summary
        print(f"\n🔧 Tool Performance:")
        available_tools = [tool for tool, status in tools_status.items() if status]
        print(f"📊 Available tools: {len(available_tools)}/{len(tools_status)}")
        print(f"🛠️ Working tools: {', '.join(available_tools)}")
        
        return successful_scans > 0

def main():
    """Run the comprehensive security scanner test."""
    tester = SecurityScannerTester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            print("\n🎉 Comprehensive testing completed successfully!")
            exit(0)
        else:
            print("\n💥 Testing failed - check the logs above")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        exit(1)

if __name__ == "__main__":
    main()
