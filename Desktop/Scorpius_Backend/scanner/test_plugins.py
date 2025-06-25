#!/usr/bin/env python3
"""
Comprehensive Plugin Test Suite for Scorpius Vulnerability Scanner

This script tests all available scanner plugins (Slither, Mythril, Manticore) 
to ensure they are properly configured and functional.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import Target, TargetType, ScanConfig, ScanType

console = Console()

# Sample vulnerable contract for testing
TEST_CONTRACT_SIMPLE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleVulnerable {
    mapping(address => uint256) public balances;
    
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");
        
        // Reentrancy vulnerability - external call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0;  // State update after external call
    }
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
}
"""

TEST_CONTRACT_COMPLEX = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;

contract ComplexVulnerable {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Integer overflow vulnerability (pre-0.8.0)
    function unsafeAdd(uint256 a, uint256 b) external pure returns (uint256) {
        return a + b;  // No SafeMath
    }
    
    // Unprotected function - missing access control
    function emergencyWithdraw() external {
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Reentrancy vulnerability
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;  // State change after external call
    }
    
    // Timestamp dependency
    function timeBasedAction() external view returns (bool) {
        return block.timestamp % 2 == 0;  // Predictable randomness
    }
}
"""


async def test_plugin_availability() -> Dict[str, bool]:
    """Test if required plugins/tools are available"""
    console.print("\n[bold cyan]🔍 Checking Plugin Dependencies...[/bold cyan]")
    
    availability = {}
    
    # Test Python packages
    packages_to_test = [
        ("slither-analyzer", "slither"),
        ("mythril", "mythril"),
        ("manticore", "manticore")
    ]
    
    for package_name, import_name in packages_to_test:
        try:
            if import_name == "slither":
                import slither
                availability[package_name] = True
                console.print(f"✅ {package_name}: Available (v{slither.__version__})")
            elif import_name == "mythril":
                import mythril
                availability[package_name] = True
                console.print(f"✅ {package_name}: Available")
            elif import_name == "manticore":
                import manticore
                availability[package_name] = True
                console.print(f"✅ {package_name}: Available (v{manticore.__version__})")
        except ImportError:
            availability[package_name] = False
            console.print(f"❌ {package_name}: Not installed")
        except Exception as e:
            availability[package_name] = False
            console.print(f"⚠️ {package_name}: Error - {e}")
    
    return availability


async def test_slither_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Slither plugin functionality"""
    try:
        from scanners.static.slither_plugin import SlitherPlugin
        
        plugin = SlitherPlugin()
        
        # Test initialization
        init_success = await plugin.initialize()
        if not init_success:
            return {"success": False, "error": "Failed to initialize Slither plugin"}
        
        # Create test target
        target = Target(
            identifier="test_contract.sol",
            name="Test Contract",
            target_type=TargetType.CONTRACT.value,
            source_code={"test_contract.sol": contract_code}
        )
        
        # Create scan config
        config = ScanConfig(
            timeout=60,
            max_depth=5
        )
        
        # Run scan
        findings = await plugin.scan(target, config)
        
        return {
            "success": True,
            "plugin_name": plugin.NAME,
            "findings_count": len(findings),
            "findings": [
                {
                    "title": f.title,
                    "severity": str(f.severity.name),
                    "type": f.vulnerability_type
                }
                for f in findings[:3]  # Show first 3 findings
            ]
        }
        
    except ImportError as e:
        return {"success": False, "error": f"Slither plugin import failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Slither plugin test failed: {e}"}


async def test_mythril_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Mythril plugin functionality"""
    try:
        from scanners.dynamic.mythril_plugin import MythrilPlugin
        
        plugin = MythrilPlugin()
        
        # Test initialization
        init_success = await plugin.initialize()
        if not init_success:
            return {"success": False, "error": "Failed to initialize Mythril plugin"}
        
        # Create test target
        target = Target(
            identifier="0x1234567890123456789012345678901234567890",
            name="Test Contract",
            target_type=TargetType.CONTRACT.value,
            source_code={"test_contract.sol": contract_code}
        )
        
        # Create scan config
        config = ScanConfig(
            timeout=120,  # Mythril can take longer
            max_depth=5
        )
        
        # Run scan
        findings = await plugin.scan(target, config)
        
        return {
            "success": True,
            "plugin_name": plugin.NAME,
            "findings_count": len(findings),
            "findings": [
                {
                    "title": f.title,
                    "severity": str(f.severity.name),
                    "type": f.vulnerability_type
                }
                for f in findings[:3]  # Show first 3 findings
            ]
        }
        
    except ImportError as e:
        return {"success": False, "error": f"Mythril plugin import failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Mythril plugin test failed: {e}"}


async def test_manticore_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Manticore plugin functionality"""
    try:
        from scanners.dynamic.manticore_plugin import ManticorePlugin
        
        plugin = ManticorePlugin()
        
        # Test initialization
        init_success = await plugin.initialize()
        if not init_success:
            return {"success": False, "error": "Failed to initialize Manticore plugin"}
        
        # Create test target
        target = Target(
            identifier="0x1234567890123456789012345678901234567890",
            name="Test Contract",
            target_type=TargetType.CONTRACT.value,
            source_code={"test_contract.sol": contract_code}
        )
        
        # Create scan config
        config = ScanConfig(
            timeout=180,  # Manticore can take even longer
            max_depth=3   # Reduce depth for faster testing
        )
        
        # Run scan
        findings = await plugin.scan(target, config)
        
        return {
            "success": True,
            "plugin_name": plugin.NAME,
            "findings_count": len(findings),
            "findings": [
                {
                    "title": f.title,
                    "severity": str(f.severity.name),
                    "type": f.vulnerability_type
                }
                for f in findings[:3]  # Show first 3 findings
            ]
        }
        
    except ImportError as e:
        return {"success": False, "error": f"Manticore plugin import failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Manticore plugin test failed: {e}"}


async def run_plugin_tests() -> Dict[str, Any]:
    """Run comprehensive plugin tests"""
    console.print("\n[bold cyan]🧪 Running Plugin Functionality Tests...[/bold cyan]")
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Test Slither
        task = progress.add_task("Testing Slither plugin...", total=None)
        try:
            results["slither"] = await asyncio.wait_for(
                test_slither_plugin(TEST_CONTRACT_SIMPLE), 
                timeout=120
            )
        except asyncio.TimeoutError:
            results["slither"] = {"success": False, "error": "Slither test timed out"}
        except Exception as e:
            results["slither"] = {"success": False, "error": str(e)}
        progress.update(task, completed=True)
        
        # Test Mythril
        task = progress.add_task("Testing Mythril plugin...", total=None)
        try:
            results["mythril"] = await asyncio.wait_for(
                test_mythril_plugin(TEST_CONTRACT_SIMPLE), 
                timeout=180
            )
        except asyncio.TimeoutError:
            results["mythril"] = {"success": False, "error": "Mythril test timed out"}
        except Exception as e:
            results["mythril"] = {"success": False, "error": str(e)}
        progress.update(task, completed=True)
        
        # Test Manticore
        task = progress.add_task("Testing Manticore plugin...", total=None)
        try:
            results["manticore"] = await asyncio.wait_for(
                test_manticore_plugin(TEST_CONTRACT_SIMPLE), 
                timeout=240
            )
        except asyncio.TimeoutError:
            results["manticore"] = {"success": False, "error": "Manticore test timed out"}
        except Exception as e:
            results["manticore"] = {"success": False, "error": str(e)}
        progress.update(task, completed=True)
    
    return results


def display_test_results(availability: Dict[str, bool], plugin_results: Dict[str, Any]):
    """Display comprehensive test results"""
    console.print("\n")
    console.print(Panel.fit(
        "🔍 Plugin Test Results",
        style="bold cyan"
    ))
    
    # Dependency availability table
    dep_table = Table(title="Plugin Dependencies")
    dep_table.add_column("Tool", style="cyan")
    dep_table.add_column("Status", justify="center")
    dep_table.add_column("Notes", style="dim")
    
    for tool, available in availability.items():
        status = "✅ Available" if available else "❌ Missing"
        notes = "Ready for use" if available else "Install with: pip install " + tool
        dep_table.add_row(tool, status, notes)
    
    console.print(dep_table)
    console.print()
    
    # Plugin functionality table
    func_table = Table(title="Plugin Functionality Tests")
    func_table.add_column("Plugin", style="cyan")
    func_table.add_column("Status", justify="center")
    func_table.add_column("Findings", justify="center")
    func_table.add_column("Details", style="dim")
    
    for plugin_name, result in plugin_results.items():
        if result["success"]:
            status = "✅ PASS"
            findings = str(result.get("findings_count", 0))
            details = f"Found {result.get('findings_count', 0)} vulnerabilities"
            
            # Show finding details if available
            if result.get("findings"):
                finding_types = [f["type"] for f in result["findings"]]
                details += f" ({', '.join(finding_types[:2])}{'...' if len(finding_types) > 2 else ''})"
        else:
            status = "❌ FAIL"
            findings = "0"
            details = result.get("error", "Unknown error")[:50]
        
        func_table.add_row(plugin_name.title(), status, findings, details)
    
    console.print(func_table)
    
    # Summary and recommendations
    working_plugins = sum(1 for result in plugin_results.values() if result["success"])
    total_plugins = len(plugin_results)
    
    console.print(f"\n[bold]Summary:[/bold] {working_plugins}/{total_plugins} plugins working")
    
    if working_plugins == total_plugins:
        console.print("[bold green]🎉 All plugins are working correctly![/bold green]")
    else:
        console.print("\n[bold yellow]⚠️ Recommendations:[/bold yellow]")
        for plugin_name, result in plugin_results.items():
            if not result["success"]:
                if "import failed" in result.get("error", ""):
                    console.print(f"• Install {plugin_name}: [cyan]pip install {plugin_name}[/cyan]")
                elif "not found" in result.get("error", "").lower():
                    console.print(f"• Ensure {plugin_name} is in PATH")
                else:
                    console.print(f"• Check {plugin_name} configuration: {result.get('error', '')[:100]}")


async def main():
    """Main test execution function"""
    console.print(Panel.fit(
        "🛡️ Scorpius Plugin Test Suite",
        style="bold cyan"
    ))
    
    try:
        # Test plugin availability
        availability = await test_plugin_availability()
        
        # Run plugin functionality tests
        plugin_results = await run_plugin_tests()
        
        # Display results
        display_test_results(availability, plugin_results)
        
        # Return status for CI/CD
        all_working = all(result["success"] for result in plugin_results.values())
        return 0 if all_working else 1
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Test suite failed: {e}[/red]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
