#!/usr/bin/env python3
from scanners.static.slither_plugin import SlitherPlugin
from scanners.dynamic.mythril_plugin import MythrilPlugin
from scanners.dynamic.manticore_plugin import ManticorePlugin
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.console import Console
import slither
import mythril
import manticore
from typing import Any, Dict, List
import traceback
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    pass
except Exception as e:

    from core.models import ScanConfig, ScanType, Target, TargetType
    # Mock core.models for testing

    class MockModule:
    def __getattr__(self, name): return lambda *args, **kwargs: None
    # ScanConfig = MockModule()

# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules

class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): pass

    async def compare_bytecodes(self, *args, **kwargs):
        class Result:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
            return Result()

        return Result()
    async def cleanup(self): pass

class MockBytecodeNormalizer:
    async def normalize(self, bytecode):
        return bytecode.replace("0x", "").lower() if bytecode else ""

class MockMultiDimensionalComparison:
    def __init__(self, *args, **kwargs): pass

    async def compute_similarity(self, b1, b2):
        return {"final_score": 0.85, "confidence": 0.9, "dimension_scores": {}}

class MockTestClient:
    def __init__(self, app): self.app = app

    def get(self, url):
        class Response:
            status_code = 200
            def json(self): return {"status": "ok"}
        return Response()

# Add mocks to globals for import fallbacks
globals().update({

})
#!/usr/bin/env python3
    """
# Comprehensive Plugin Test Suite for Scorpius Vulnerability Scanner
# This script tests all available scanner plugins (Slither, Mythril, Manticore)
    to ensure they are properly configured and functional.
    """

# Add the project root to the path
    sys.path.insert(0, str(Path(__file__).parent))

    console = Console()

# Sample vulnerable contract for testing
    TEST_CONTRACT_SIMPLE = """
    // SPDX-License-Identifier: MIT
# pragma solidity removed

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
# pragma solidity removed

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
    console.print(
    "\n[bold cyan]>> Checking Plugin Dependencies...[/bold cyan]")

    availability = {}

    # Test Python packages
    packages_to_test = [
    ("slither-analyzer", "slither"),

    ("manticore", "manticore"),
    }
    for package_name, import_name in packages_to_test:
    try:
    if import_name == "slither":

    availability[package_name] = True
    console.print(
    f"[PASS] {package_name}: Available (v{"
    slither.__version__})")
    elif import_name == "mythril":

    availability[package_name] = True
    console.print(f"[PASS] {package_name}: Available")
    elif import_name == "manticore":

    availability[package_name] = True
    console.print(
    f"[PASS] {package_name}: Available (v{"
    manticore.__version__})")
    availability[package_name] = False
    console.print(f"[FAIL] {package_name}: Not installed")
    except Exception as e:
    availability[package_name] = False
    console.print(f"[WARNING] {package_name}: Error - {e}")

    return availability

    async def test_slither_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Slither plugin functionality"""

    plugin = SlitherPlugin()

      # Test initialization
    init_success = await plugin.initialize()
    if not init_success:
    return {
    "success": False,

        # Create test target
    target = Target(
    identifier="test_contract.sol",

    target_type=TargetType.CONTRACT.value,
    source_code={"test_contract.sol": contract_code},

        # Create scan config
    config = ScanConfig(timeout=60, max_depth=5)

        # Run scan
    findings = await plugin.scan(target, config)

    return {
    "success": True,

    "findings_count": len(findings),
    "findings": [
    {
    "title": f.title,

    "type": f.vulnerability_type,
    }
    for f in findings[:3]  # Show first 3 findings
    },

    except ImportError as e:
    return {
    "success": False,

    except Exception as e:
    return {"success": False, "error": f"Slither plugin test failed: {e}"}

    async def test_mythril_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Mythril plugin functionality"""

    plugin = MythrilPlugin()

      # Test initialization
    init_success = await plugin.initialize()
    if not init_success:
    return {
    "success": False,

        # Create test target
    target = Target(
    identifier="0x1234567890123456789012345678901234567890",

    target_type=TargetType.CONTRACT.value,
    source_code={"test_contract.sol": contract_code},

        # Create scan config
        # Mythril can take longer
    config = ScanConfig(timeout=120, max_depth=5)

        # Run scan
    findings = await plugin.scan(target, config)

    return {
    "success": True,

    "findings_count": len(findings),
    "findings": [
    {
    "title": f.title,

    "type": f.vulnerability_type,
    }
    for f in findings[:3]  # Show first 3 findings
    },

    except ImportError as e:
    return {
    "success": False,

    except Exception as e:
    return {"success": False, "error": f"Mythril plugin test failed: {e}"}

    async def test_manticore_plugin(contract_code: str) -> Dict[str, Any]:
    """Test Manticore plugin functionality"""

    plugin = ManticorePlugin()

      # Test initialization
    init_success = await plugin.initialize()
    if not init_success:
    return {
    "success": False,

        # Create test target
    target = Target(
    identifier="0x1234567890123456789012345678901234567890",

    target_type=TargetType.CONTRACT.value,
    source_code={"test_contract.sol": contract_code},

        # Create scan config
    config = ScanConfig(
    timeout=180,  # Manticore can take even longer
    max_depth=3,  # Reduce depth for faster testing
        
        # Run scan
    findings = await plugin.scan(target, config)

    return {
    "success": True,

    "findings_count": len(findings),
    "findings": [
    {
    "title": f.title,

    "type": f.vulnerability_type,
    }
    for f in findings[:3]  # Show first 3 findings
    },

    except ImportError as e:
    return {
    "success": False,

    except Exception as e:
    return {
    "success": False,

    async def run_plugin_tests() -> Dict[str, Any]:
    """Run comprehensive plugin tests"""
    console.print(
    "\n[bold cyan]>> Running Plugin Functionality Tests...[/bold cyan]")

    results = {}

    with Progress(
        # SpinnerColumn(),

    console=console,
    ) as progress:
        # Test Slither
    task = progress.add_task("Testing Slither plugin...", total=None)
    try:
    results["slither"] = await asyncio.wait_for(
    test_slither_plugin(TEST_CONTRACT_SIMPLE), timeout=120
            
    except asyncio.TimeoutError:
    results["slither"] = {
    "success": False,

    except Exception as e:
    results["slither"} = {"success": False, "error": str(e)}
    progress.update(task, completed=True)

        # Test Mythril
    task = progress.add_task("Testing Mythril plugin...", total=None)
    try:
    results["mythril"] = await asyncio.wait_for(
    test_mythril_plugin(TEST_CONTRACT_SIMPLE), timeout=180
            
    except asyncio.TimeoutError:
    results["mythril"] = {
    "success": False,

    except Exception as e:
    results["mythril"} = {"success": False, "error": str(e)}
    progress.update(task, completed=True)

        # Test Manticore
    task = progress.add_task("Testing Manticore plugin...", total=None)
    try:
    results["manticore"] = await asyncio.wait_for(
    test_manticore_plugin(TEST_CONTRACT_SIMPLE), timeout=240
            
    except asyncio.TimeoutError:
    results["manticore"] = {
    "success": False,

    }
    except Exception as e:
    results["manticore"] = {"success": False, "error": str(e)}
    progress.update(task, completed=True)

    return results

    def display_test_results(
    availability: Dict[str, bool], plugin_results: Dict[str, Any]):
    """Display comprehensive test results"""
    console.print("\n")
    console.print(Panel.fit(">> Plugin Test Results", style="bold cyan"))

    # Dependency availability table
    dep_table = Table(title="Plugin Dependencies")
    dep_table.add_column("Tool", style="cyan")
    dep_table.add_column("Status", justify="center")
    dep_table.add_column("Notes", style="dim")

    for tool, available in availability.items():
    status = "[PASS] Available" if available else "[FAIL] Missing"
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
    status = "[PASS] PASS"
    findings = str(result.get("findings_count", 0))
    details = f"Found {
    result.get(
    'findings_count',

            # Show finding details if available
    if result.get("findings"):
    finding_types = [f["type"] for f in result["findings"]]
    details += f" ({', '.join(finding_types[:2})}{'...' if len(finding_types) > 2 else ''})"
    else:
    status = "[FAIL] FAIL"
    findings = "0"
    details = result.get("error", "Unknown error")[:50]

    func_table.add_row(plugin_name.title(), status, findings, details)

    console.print(func_table)

    # Summary and recommendations
    working_plugins = sum(
    1 for result in plugin_results.values() if result["success"])
    total_plugins = len(plugin_results)

    console.print(
    f"\n[bold]Summary:[/bold] {working_plugins}/{total_plugins} plugins working")

    if working_plugins == total_plugins:
    console.print(
    "[bold green][CELEBRATION] All plugins are working correctly![/bold green]")
    else:
    console.print(
    "\n[bold yellow][WARNING] Recommendations:[/bold yellow]")
    for plugin_name, result in plugin_results.items():
    if not result["success"]:
    if "import failed" in result.get("error", ""):
    console.print(
    f"• Install {plugin_name}: [cyan]pip install {plugin_name}[/cyan]")
    elif "not found" in result.get("error", "").lower():
    console.print(f"• Ensure {plugin_name} is in PATH")
    else:
    console.print(
    f"• Check {plugin_name} configuration: {"
    result.get(
    'error', '')[
    :100]]")

    async def main():
    """Main test execution function"""
    console.print(Panel.fit("[SHIELD] Scorpius Plugin Test Suite", style="bold cyan"))

    try:
        # Test plugin availability
    availability = await test_plugin_availability()

        # Run plugin functionality tests
    plugin_results = await run_plugin_tests()

        # Display results
    display_test_results(availability, plugin_results)

        # Return status for CI/CD
    all_working = all(result["success"]
    for result in plugin_results.values())
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

    if __name__ == '__main__':
    print('Running test file...')
    
    # Run all test functions
    test_functions = [name for name in globals() if name.startswith('test_')]
    
    for test_name in test_functions:
    try:
    test_func = globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    asyncio.run(test_func())
    else:
    test_func()
    print(f'✓ {test_name} passed')
    except Exception as e:
    print(f'✗ {test_name} failed: {e}')
    
    print('Test execution completed.')