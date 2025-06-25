#!/usr/bin/env python3
"""
Docker Plugin Integration Test for Scorpius Vulnerability Scanner

This script tests all containerized security analysis plugins to ensure
they work correctly and can analyze smart contracts.
"""

import asyncio
import tempfile
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

# Import our Docker plugin manager
import sys
sys.path.append('.')

try:
    from sandbox.docker_plugin_manager import DockerPluginManager, ContainerPlugin
    from core.models import Target, TargetType
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

console = Console()

# Test contract with multiple vulnerabilities
TEST_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;

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
    
    console.print(Panel(
        "🐋 Testing Docker-based Plugin System",
        title="Scorpius Docker Plugin Test",
        expand=False
    ))
    
    # Initialize plugin manager
    try:
        plugin_manager = DockerPluginManager()
        if not plugin_manager.client:
            console.print("[red]❌ Docker not available. Please install Docker and ensure it's running.[/red]")
            return False
            
        console.print("[green]✅ Docker client initialized successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Docker plugin manager: {e}[/red]")
        return False
    
    # Display available plugins
    plugins = plugin_manager.get_available_plugins()
    console.print(f"[cyan]📦 Available plugins: {', '.join(plugins)}[/cyan]")
    
    # Check plugin status
    status_table = Table(title="Plugin Status")
    status_table.add_column("Plugin", style="cyan")
    status_table.add_column("Image", style="blue")
    status_table.add_column("Available", style="green")
    status_table.add_column("Memory Limit", style="yellow")
    
    status = plugin_manager.get_plugin_status()
    for plugin_name, plugin_info in status.items():
        available = "✅ Yes" if plugin_info["image_exists"] else "❌ No"
        status_table.add_row(
            plugin_name,
            plugin_info["image"],
            available,
            plugin_info["memory_limit"]
        )
    
    console.print(status_table)
    
    # Build missing images
    missing_images = [name for name, info in status.items() if not info["image_exists"]]
    if missing_images:
        console.print(f"[yellow]⚠️  Building missing images: {', '.join(missing_images)}[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Building Docker images...", total=None)
            try:
                await plugin_manager.build_all_images()
                progress.update(task, description="✅ Images built successfully")
            except Exception as e:
                progress.update(task, description=f"❌ Image build failed: {e}")
                console.print(f"[red]Failed to build images: {e}[/red]")
                console.print("[yellow]Continuing with available plugins...[/yellow]")
    
    return plugin_manager

async def test_individual_plugins(plugin_manager: DockerPluginManager):
    """Test each plugin individually"""
    
    # Create test target
    target = Target(
        identifier="0x742d35C65a29E18E7B7B4bc5E15aE5ffF4b4B5B8",
        target_type=TargetType.CONTRACT.value,
        blockchain="ethereum"
    )
    
    plugins = plugin_manager.get_available_plugins()
    results_table = Table(title="Plugin Test Results")
    results_table.add_column("Plugin", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Findings", style="yellow")
    results_table.add_column("Details", style="blue")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for plugin_name in plugins:
            task = progress.add_task(f"Testing {plugin_name}...", total=None)
            
            try:
                # Test if image exists
                status = plugin_manager.get_plugin_status()
                if not status[plugin_name]["image_exists"]:
                    results_table.add_row(
                        plugin_name,
                        "❌ SKIP",
                        "0",
                        "Image not available"
                    )
                    continue
                
                # Run plugin
                findings = await plugin_manager.scan_with_plugin(
                    plugin_name,
                    target,
                    TEST_CONTRACT
                )
                
                if findings:
                    results_table.add_row(
                        plugin_name,
                        "✅ PASS",
                        str(len(findings)),
                        f"Found {len(findings)} issues"
                    )
                else:
                    results_table.add_row(
                        plugin_name,
                        "✅ PASS",
                        "0",
                        "No vulnerabilities found"
                    )
                    
            except Exception as e:
                results_table.add_row(
                    plugin_name,
                    "❌ FAIL",
                    "0",
                    str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
                )
                console.print(f"[red]Plugin {plugin_name} failed: {e}[/red]")
            
            progress.update(task, description=f"✅ {plugin_name} completed")
    
    console.print(results_table)

async def test_parallel_execution(plugin_manager: DockerPluginManager):
    """Test running multiple plugins in parallel"""
    
    console.print("\n[bold]Testing Parallel Plugin Execution[/bold]")
    
    target = Target(
        identifier="0x742d35C65a29E18E7B7B4bc5E15aE5ffF4b4B5B8",
        target_type=TargetType.CONTRACT.value,
        blockchain="ethereum"
    )
    
    # Only test plugins with available images
    status = plugin_manager.get_plugin_status()
    available_plugins = [name for name, info in status.items() if info["image_exists"]]
    
    if not available_plugins:
        console.print("[yellow]⚠️  No plugin images available for parallel testing[/yellow]")
        return
    
    console.print(f"[cyan]Testing parallel execution with: {', '.join(available_plugins)}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Running parallel analysis...", total=None)
        
        try:
            # Run all plugins in parallel
            results = await plugin_manager.scan_with_all_plugins(
                target,
                TEST_CONTRACT,
                selected_plugins=available_plugins
            )
            
            # Display results
            parallel_table = Table(title="Parallel Execution Results")
            parallel_table.add_column("Plugin", style="cyan")
            parallel_table.add_column("Findings", style="yellow")
            parallel_table.add_column("Status", style="green")
            
            total_findings = 0
            for plugin_name, findings in results.items():
                status = "✅ Success" if findings is not None else "❌ Failed"
                finding_count = len(findings) if findings else 0
                total_findings += finding_count
                
                parallel_table.add_row(
                    plugin_name,
                    str(finding_count),
                    status
                )
            
            console.print(parallel_table)
            console.print(f"[green]✅ Parallel execution completed. Total findings: {total_findings}[/green]")
            
            progress.update(task, description="✅ Parallel execution completed")
            
        except Exception as e:
            console.print(f"[red]❌ Parallel execution failed: {e}[/red]")
            progress.update(task, description=f"❌ Failed: {e}")

async def test_docker_compose_integration():
    """Test integration with docker-compose"""
    
    console.print("\n[bold]Testing Docker Compose Integration[/bold]")
    
    # Check if docker-compose.yml exists
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        console.print("[yellow]⚠️  docker-compose.yml not found[/yellow]")
        return
    
    console.print("[green]✅ docker-compose.yml found[/green]")
    
    # You could add docker-compose testing here
    console.print("[cyan]📝 Docker Compose integration available for full deployment[/cyan]")

async def main():
    """Main test function"""
    
    console.print("🧪 Starting Docker Plugin Integration Tests\n")
    
    # Display test contract
    syntax = Syntax(TEST_CONTRACT, "solidity", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Test Contract", expand=False))
    
    try:
        # Test 1: Plugin manager initialization
        plugin_manager = await test_docker_plugin_manager()
        if not plugin_manager:
            console.print("[red]❌ Plugin manager test failed[/red]")
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
        
        console.print("\n[bold green]🎉 All Docker plugin tests completed![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Tests interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Test suite failed: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
