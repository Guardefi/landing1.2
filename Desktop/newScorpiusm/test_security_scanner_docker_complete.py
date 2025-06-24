#!/usr/bin/env python3
"""
Comprehensive Docker-based Security Scanner Test
Tests the vulnerability scanner with all security tools in Docker environment.
"""

import subprocess
import json
import time
import requests
import sys
import os
from pathlib import Path

# Test Solidity contract with multiple vulnerabilities
VULNERABLE_CONTRACT = '''
pragma solidity ^0.8.0;

contract VulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;
    bool public locked = false;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Reentrancy vulnerability
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // Vulnerable: external call before state change
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0; // State change after external call
    }
    
    // tx.origin vulnerability
    function transferOwnership(address newOwner) public {
        require(tx.origin == owner, "Only owner can transfer"); // Vulnerable: using tx.origin
        owner = newOwner;
    }
    
    // Unchecked low-level call
    function unsafeCall(address target, bytes memory data) public {
        require(msg.sender == owner, "Only owner");
        target.call(data); // Vulnerable: unchecked return value
    }
    
    // Integer overflow (in older Solidity versions)
    function deposit() public payable {
        balances[msg.sender] += msg.value; // Could overflow
    }
    
    // Access control issue
    function emergencyWithdraw() public {
        require(!locked, "Contract is locked");
        payable(msg.sender).transfer(address(this).balance); // Anyone can call
    }
    
    // Timestamp dependence
    function timeLock() public view returns (bool) {
        return block.timestamp > 1640995200; // Vulnerable to timestamp manipulation
    }
    
    receive() external payable {
        deposit();
    }
}
'''

def wait_for_docker_build():
    """Wait for Docker build to complete"""
    print("Checking Docker build status...")
    
    # Check if Docker daemon is running
    try:
        result = subprocess.run(['docker', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("Docker daemon not running")
            return False
    except Exception as e:
        print(f"Error checking Docker: {e}")
        return False
    
    # Check if our image exists
    try:
        result = subprocess.run(['docker', 'images', 'scorpius-backend'], 
                              capture_output=True, text=True, timeout=10)
        if 'scorpius-backend' in result.stdout:
            print("✅ Docker image found")
            return True
        else:
            print("❌ Docker image not found, build may still be running")
            return False
    except Exception as e:
        print(f"Error checking Docker images: {e}")
        return False

def test_tools_in_docker():
    """Test security tools inside Docker container"""
    print("\n🔧 Testing security tools in Docker container...")
    
    # Create a temporary contract file
    contract_file = Path("test_contract.sol")
    contract_file.write_text(VULNERABLE_CONTRACT)
    
    try:
        # Test Slither
        print("\n📊 Testing Slither...")
        slither_cmd = [
            'docker', 'run', '--rm', 
            '-v', f'{os.getcwd()}:/workspace',
            'scorpius-backend',
            'slither', '/workspace/test_contract.sol', '--json', '-'
        ]
        
        try:
            slither_result = subprocess.run(slither_cmd, capture_output=True, text=True, timeout=60)
            if slither_result.returncode == 0:
                print("✅ Slither analysis completed successfully")
                # Try to parse JSON output
                try:
                    slither_data = json.loads(slither_result.stdout)
                    issues = slither_data.get('results', {}).get('detectors', [])
                    print(f"   Found {len(issues)} potential issues")
                except json.JSONDecodeError:
                    print("   Raw output (not JSON):", slither_result.stdout[:200])
            else:
                print(f"❌ Slither failed: {slither_result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Slither timed out")
        except Exception as e:
            print(f"❌ Slither error: {e}")
        
        # Test Mythril
        print("\n🔮 Testing Mythril...")
        mythril_cmd = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}:/workspace',
            'scorpius-backend',
            'myth', 'analyze', '/workspace/test_contract.sol', '--output', 'json'
        ]
        
        try:
            mythril_result = subprocess.run(mythril_cmd, capture_output=True, text=True, timeout=120)
            if mythril_result.returncode == 0:
                print("✅ Mythril analysis completed successfully")
                try:
                    mythril_data = json.loads(mythril_result.stdout)
                    issues = mythril_data.get('issues', [])
                    print(f"   Found {len(issues)} security issues")
                except json.JSONDecodeError:
                    print("   Raw output:", mythril_result.stdout[:200])
            else:
                print(f"❌ Mythril failed: {mythril_result.stderr}")
        except subprocess.TimeoutExpired:
            print("❌ Mythril timed out")
        except Exception as e:
            print(f"❌ Mythril error: {e}")
        
        # Test Solidity compiler
        print("\n🔨 Testing Solidity compiler...")
        solc_cmd = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}:/workspace',
            'scorpius-backend',
            'solc', '--version'
        ]
        
        try:
            solc_result = subprocess.run(solc_cmd, capture_output=True, text=True, timeout=30)
            if solc_result.returncode == 0:
                print("✅ Solidity compiler available")
                print(f"   Version: {solc_result.stdout.strip()}")
            else:
                print(f"❌ Solidity compiler failed: {solc_result.stderr}")
        except Exception as e:
            print(f"❌ Solidity compiler error: {e}")
        
        # Test Manticore (if available)
        print("\n🐍 Testing Manticore...")
        manticore_cmd = [
            'docker', 'run', '--rm',
            'scorpius-backend',
            'python', '-c', 'import manticore; print("Manticore available")'
        ]
        
        try:
            manticore_result = subprocess.run(manticore_cmd, capture_output=True, text=True, timeout=30)
            if manticore_result.returncode == 0:
                print("✅ Manticore is available")
            else:
                print(f"❌ Manticore not available: {manticore_result.stderr}")
        except Exception as e:
            print(f"❌ Manticore test error: {e}")
        
        # Test Echidna (if available)
        print("\n🦔 Testing Echidna...")
        echidna_cmd = [
            'docker', 'run', '--rm',
            'scorpius-backend',
            'echidna', '--version'
        ]
        
        try:
            echidna_result = subprocess.run(echidna_cmd, capture_output=True, text=True, timeout=30)
            if echidna_result.returncode == 0:
                print("✅ Echidna is available")
                print(f"   Version: {echidna_result.stdout.strip()}")
            else:
                print(f"❌ Echidna not available: {echidna_result.stderr}")
        except Exception as e:
            print(f"❌ Echidna test error: {e}")
            
    finally:
        # Clean up
        if contract_file.exists():
            contract_file.unlink()

def start_docker_services():
    """Start the backend services in Docker"""
    print("\n🚀 Starting Docker services...")
    
    # Stop any existing containers
    try:
        subprocess.run(['docker', 'stop', 'scorpius-backend-test'], 
                      capture_output=True, timeout=10)
        subprocess.run(['docker', 'rm', 'scorpius-backend-test'], 
                      capture_output=True, timeout=10)
    except:
        pass
    
    # Start the backend container
    start_cmd = [
        'docker', 'run', '-d',
        '--name', 'scorpius-backend-test',
        '-p', '8000:8000',
        '-p', '8081:8081',
        'scorpius-backend'
    ]
    
    try:
        result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Backend container started")
            container_id = result.stdout.strip()
            
            # Wait for services to be ready
            print("Waiting for services to start...")
            time.sleep(10)
            
            return container_id
        else:
            print(f"❌ Failed to start container: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting container: {e}")
        return None

def test_api_endpoints(container_id):
    """Test the API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test scanner endpoint
    try:
        scan_data = {
            "contract_source": VULNERABLE_CONTRACT,
            "tools": ["slither", "mythril"],
            "include_patterns": True
        }
        
        response = requests.post(
            "http://localhost:8000/scanner/analyze",
            json=scan_data,
            timeout=120
        )
        
        if response.status_code == 200:
            print("✅ Scanner endpoint working")
            result = response.json()
            
            # Check results
            vulnerabilities = result.get('vulnerabilities', [])
            print(f"   Found {len(vulnerabilities)} vulnerabilities")
            
            for vuln in vulnerabilities[:3]:  # Show first 3
                severity = vuln.get('severity', 'unknown')
                name = vuln.get('name', 'Unknown')
                print(f"   - {severity.upper()}: {name}")
                
        else:
            print(f"❌ Scanner endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw response: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Scanner endpoint error: {e}")

def check_container_logs(container_id):
    """Check container logs for any errors"""
    print("\n📋 Checking container logs...")
    
    try:
        logs_cmd = ['docker', 'logs', container_id]
        result = subprocess.run(logs_cmd, capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("📋 Container output:")
            print(result.stdout[-500:])  # Last 500 chars
            
        if result.stderr:
            print("⚠️ Container errors:")
            print(result.stderr[-500:])  # Last 500 chars
            
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def cleanup_docker(container_id):
    """Clean up Docker resources"""
    print("\n🧹 Cleaning up...")
    
    if container_id:
        try:
            subprocess.run(['docker', 'stop', container_id], 
                          capture_output=True, timeout=10)
            subprocess.run(['docker', 'rm', container_id], 
                          capture_output=True, timeout=10)
            print("✅ Container cleaned up")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

def main():
    """Main test function"""
    print("🔐 Comprehensive Docker Security Scanner Test")
    print("=" * 50)
    
    # Check if Docker image is ready
    if not wait_for_docker_build():
        print("❌ Docker image not ready. Please ensure Docker build completed successfully.")
        return 1
    
    # Test security tools
    test_tools_in_docker()
    
    # Start services and test APIs
    container_id = start_docker_services()
    
    if container_id:
        try:
            # Test API endpoints
            test_api_endpoints(container_id)
            
            # Check logs
            check_container_logs(container_id)
            
        finally:
            # Always cleanup
            cleanup_docker(container_id)
    
    print("\n✅ Test completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
