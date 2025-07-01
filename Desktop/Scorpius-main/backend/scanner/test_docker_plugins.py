#!/usr/bin/env python3
from sandbox.docker_plugin_manager import ContainerPlugin, DockerPluginManager
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.console import Console
import traceback
import tempfile
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

    from core.models import Target, TargetType
    # Mock core.models for testing

    class MockModule:
    def __getattr__(self, name): return lambda *args, **kwargs: None
    # Target = MockModule()

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
# Docker Plugin Integration Test for Scorpius Vulnerability Scanner
# This script tests all containerized security analysis plugins to ensure
    they work correctly and can analyze smart contracts.
    """

# Import our Docker plugin manager

    sys.path.append(".")

    except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

    console = Console()

# Test contract with multiple vulnerabilities
    TEST_CONTRACT = """
    // SPDX-License-Identifier: MIT
# pragma solidity removed

    contract TestVulnerableContract {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
    owner = msg.sender;
    }
    // Reentrancy vulnerability
    function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient balance");

    // External call before state update - VULNERABLE!
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");

    balances[msg.sender] -= amount;  // State update after external call
    }
    // Missing access control
    function emergencyWithdraw() external {
    // NO ACCESS CONTROL - Anyone can call this!
    payable(msg.sender).transfer(address(this).balance);
    }
    // Integer overflow (pre-0.8.0)
    function deposit() external payable {
    // NO SAFEMATH - Can overflow in older Solidity versions
    balances[msg.sender] += msg.value;
    }
    // Unsafe external call
    function callExternal(address target, bytes calldata data) external {
    // No validation of target or data
    target.call(data);
    }
    }
    """

    async def test_docker_plugin_manager():
    """Test the Docker plugin manager functionality"""

    console.print(
        # Panel(
    "🐋 Testing Docker-based Plugin System",

    expand=False,

    # Initialize plugin manager
    try:
    plugin_manager=DockerPluginManager()
    if not plugin_manager.client:
    console.print(
    "[red][FAIL] Docker not available. Please install Docker and ensure it's running.[/red]"

    return False

    console.print(
    "[green][PASS] Docker client initialized successfully[/green]")

    except Exception as e:
    console.print(
    f"[red][FAIL] Failed to initialize Docker plugin manager: {e}[/red]")
    return False

    # Display available plugins
    plugins=plugin_manager.get_available_plugins()
    console.print(f"[cyan]📦 Available plugins: {', '.join(plugins)}[/cyan]")

    # Check plugin status
    status_table=Table(title="Plugin Status")
    status_table.add_column("Plugin", style="cyan")
    status_table.add_column("Image", style="blue")
    status_table.add_column("Available", style="green")
    status_table.add_column("Memory Limit", style="yellow")

    status=plugin_manager.get_plugin_status()
    for plugin_name, plugin_info in status.items():
    available="[PASS] Yes" if plugin_info["image_exists"] else "[FAIL] No"
    status_table.add_row(
    plugin_name,

    available,
    plugin_info["memory_limit"])

    console.print(status_table)

    # Build missing images
    missing_images=[
    name for name,

    if missing_images:
    console.print(
    f"[yellow][WARNING]  Building missing images: {
    ', '.join(missing_images)][/yellow]")

    with Progress(
            # SpinnerColumn(),

    console=console,
    ) as progress:
    task = progress.add_task("Building Docker images...", total=None)
    try:
    pass
    except Exception as e:

    await plugin_manager.build_all_images()
    progress.update(
    task, description="[PASS] Images built successfully")
    except Exception as e:
    progress.update(
    task, description=f"[FAIL] Image build failed: {e}")
    console.print(f"[red]Failed to build images: {e}[/red]")
    console.print(
    "[yellow]Continuing with available plugins...[/yellow]")

    return plugin_manager

    async def test_individual_plugins(plugin_manager: DockerPluginManager):
    """Test each plugin individually"""

    # Create test target
    target = Target(
    identifier="0x742d35C65a29E18E7B7B4bc5E15aE5ffF4b4B5B8",

    blockchain="ethereum",

    plugins=plugin_manager.get_available_plugins()
    results_table=Table(title="Plugin Test Results")
    results_table.add_column("Plugin", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Findings", style="yellow")
    results_table.add_column("Details", style="blue")

    with Progress(
        # SpinnerColumn(),

    console=console,
    ) as progress:
    for plugin_name in plugins:
    task=progress.add_task(f"Testing {plugin_name}...", total=None)

    try:
    pass
    except Exception as e:

                # Test if image exists
    status=plugin_manager.get_plugin_status()
    if not status[plugin_name]["image_exists"]:
    results_table.add_row(
    plugin_name, "[FAIL] SKIP", "0", "Image not available"

    continue

                # Run plugin
    findings=await plugin_manager.scan_with_plugin(
    plugin_name, target, TEST_CONTRACT

    if findings:
    results_table.add_row(
    plugin_name,

    str(len(findings)),
    f"Found {len(findings)} issues",

    results_table.add_row(
    plugin_name, "[PASS] PASS", "0", "No vulnerabilities found")

    except Exception as e:
    results_table.add_row(
    plugin_name,

    "0",
    str(e)[:50] + "..." if len(str(e)) > 50 else str(e),

    progress.update(
    task, description=f"[PASS] {plugin_name} completed")

    console.print(results_table)

    async def test_parallel_execution(plugin_manager: DockerPluginManager):
    """Test running multiple plugins in parallel"""

    console.print("\n[bold]Testing Parallel Plugin Execution[/bold]")

    target=Target(
    identifier="0x742d35C65a29E18E7B7B4bc5E15aE5ffF4b4B5B8",

    blockchain="ethereum",

    # Only test plugins with available images
    status=plugin_manager.get_plugin_status()
    available_plugins=[
    name for name,

    if not available_plugins:
    console.print(
    "[yellow][WARNING]  No plugin images available for parallel testing[/yellow]"

    return

    console.print(
    f"[cyan]Testing parallel execution with: {
    ', '.join(available_plugins)}[/cyan}")

    with Progress(
        # SpinnerColumn(),

    console=console,
    ) as progress:
    task=progress.add_task("Running parallel analysis...", total=None)

    try:
    pass
    except Exception as e:

            # Run all plugins in parallel
    results=await plugin_manager.scan_with_all_plugins(
    target, TEST_CONTRACT, selected_plugins=available_plugins

            # Display results
    parallel_table=Table(title="Parallel Execution Results")
    parallel_table.add_column("Plugin", style="cyan")
    parallel_table.add_column("Findings", style="yellow")
    parallel_table.add_column("Status", style="green")

    total_findings=0
    for plugin_name, findings in results.items():
    status="[PASS] Success" if findings is not None else "[FAIL] Failed"
    finding_count=len(findings) if findings else 0
    total_findings += finding_count

    parallel_table.add_row(plugin_name, str(finding_count), status)

    console.print(parallel_table)
    console.print(
    f"[green][PASS] Parallel execution completed. Total findings: {total_findings}[/green]")

    progress.update(
    task, description="[PASS] Parallel execution completed")

    except Exception as e:
    console.print(f"[red][FAIL] Parallel execution failed: {e}[/red]")
    progress.update(task, description=f"[FAIL] Failed: {e}")

    async def test_docker_compose_integration():
    """Test integration with docker-compose"""

    console.print("\n[bold]Testing Docker Compose Integration[/bold]")

    # Check if docker-compose.yml exists
    compose_file=Path("docker-compose.yml")
    if not compose_file.exists():
    console.print(
    "[yellow][WARNING]  docker-compose.yml not found[/yellow]")
    return

    console.print("[green][PASS] docker-compose.yml found[/green]")

    # You could add docker-compose testing here
    console.print(
    "[cyan]📝 Docker Compose integration available for full deployment[/cyan]"

    async def main():
    """Main test function"""

    console.print(">> Starting Docker Plugin Integration Tests\n")

    # Display test contract
    syntax=Syntax(
    # TEST_CONTRACT,

    theme="monokai",
    line_numbers=True)
    console.print(Panel(syntax, title="Test Contract", expand=False))

    try:
    pass
    except Exception as e:

        # Test 1: Plugin manager initialization
    plugin_manager=await test_docker_plugin_manager()
    if not plugin_manager:
    console.print("[red][FAIL] Plugin manager test failed[/red]")
    return

    console.print()

        # Test 2: Individual plugin testing
    await test_individual_plugins(plugin_manager)

    console.print()

        # Test 3: Parallel execution
    await test_parallel_execution(plugin_manager)

    console.print()

        # Test 4: Docker Compose integration
    await test_docker_compose_integration()

        # Cleanup
    plugin_manager.cleanup()

    console.print(
    "\n[bold green][CELEBRATION] All Docker plugin tests completed![/bold green]")

    except KeyboardInterrupt:
    console.print(
    "\n[yellow][WARNING]  Tests interrupted by user[/yellow]")
    except Exception as e:
    console.print(f"\n[red][FAIL] Test suite failed: {e}[/red]")

    console.print(f"[red]{traceback.format_exc()}[/red]")

    if __name__ == "__main__":
    asyncio.run(main())

    if __name__ == '__main__':
    print('Running test file...')

    # Run all test functions
    test_functions=[name for name in globals() if name.startswith('test_')]

    for test_name in test_functions:
    try:
    test_func=globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    asyncio.run(test_func())
    else:
    test_func()
    print(f'✓ {test_name} passed')
    except Exception as e:
    print(f'✗ {test_name} failed: {e}')

    print('Test execution completed.')
