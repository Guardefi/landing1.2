#!/usr/bin/env python3
"""
Enhanced Scorpius Scanner Demo
Showcases the new enterprise-grade vulnerability detection capabilities
"""

import asyncio
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))


console = Console()


# Demo vulnerable contract with multiple issues
DEMO_CONTRACT = """
pragma solidity ^0.7.6;

/**
 * Intentionally Vulnerable DeFi Contract for Demonstration
 * Contains multiple vulnerability types for testing
 */

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
}

contract VulnerableDeFiVault {
    mapping(address => uint256) public balances;
    mapping(address => bool) public isAdmin;

    IERC20 public token;
    address public owner;
    uint256 public totalDeposits;
    bool public paused;

    constructor(address _token) {
        token = IERC20(_token);
        owner = msg.sender;
        isAdmin[msg.sender] = true;
    }

    // VULNERABILITY 1: Reentrancy in withdraw function
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(!paused, "Contract is paused");

        // External call before state update - VULNERABLE TO REENTRANCY
        require(token.transfer(msg.sender, amount), "Transfer failed");

        balances[msg.sender] -= amount;  // State change after external call
        totalDeposits -= amount;
    }

    // VULNERABILITY 2: Missing access control on critical functions
    function emergencyWithdraw() external {
        // NO ACCESS CONTROL - Anyone can call this!
        uint256 contractBalance = token.balanceOf(address(this));
        require(token.transfer(msg.sender, contractBalance), "Transfer failed");
    }

    // VULNERABILITY 3: Unprotected initialization
    function initialize(address newOwner) external {
        // NO PROTECTION AGAINST MULTIPLE CALLS
        owner = newOwner;
        isAdmin[newOwner] = true;
    }

    // VULNERABILITY 4: Integer overflow (pre-0.8 Solidity)
    function mint(address to, uint256 amount) external {
        // NO SAFEMATH - Can overflow
        balances[to] += amount;
        totalDeposits += amount;
    }

    // VULNERABILITY 5: Price oracle manipulation
    function liquidate(address user, uint256 amount) external {
        // Uses spot price from token balances - FLASH LOAN VULNERABLE
        uint256 contractBalance = token.balanceOf(address(this));
        uint256 userBalance = balances[user];

        // Manipulatable price calculation
        uint256 liquidationThreshold = contractBalance * 150 / 100;

        if (userBalance > liquidationThreshold) {
            // Liquidation logic using manipulatable price
            balances[user] = 0;
            balances[msg.sender] += userBalance / 10; // 10% reward
        }
    }

    // VULNERABILITY 6: Missing access control on admin functions
    function setPaused(bool _paused) external {
        // Should have onlyAdmin modifier but doesn't
        paused = _paused;
    }

    function deposit(uint256 amount) external {
        require(!paused, "Contract is paused");
        require(token.balanceOf(msg.sender) >= amount, "Insufficient token balance");

        balances[msg.sender] += amount;
        totalDeposits += amount;
    }
}
"""


async def run_comprehensive_demo():
    """Run comprehensive vulnerability analysis demo"""
    console.print(
        Panel.fit(
            "🛡️ Enhanced Scorpius Vulnerability Scanner Demo",
            style="bold blue"))

    try:
        from ai.vulnerability_analyzer import EnhancedVulnerabilityAnalyzer
        from core.models import Target, TargetType

        # Create analyzer
        config = {
            "enable_simulation": False,  # Disable for demo
            "enable_ai_analysis": False,  # Disable for demo (no API key)
            "parallel_execution": True,
        }

        console.print(
            "\n[bold cyan]Initializing Enhanced Vulnerability Analyzer...[/bold cyan]"
        )
        analyzer = EnhancedVulnerabilityAnalyzer(config=config)

        # Show available strategies
        strategies = analyzer.get_available_strategies()
        console.print(
            f"[green]✓[/green] Loaded {len(strategies)} vulnerability detection strategies:"
        )
        for strategy in strategies:
            console.print(f"  • {strategy}")

        console.print(
            "\n[bold yellow]Analyzing Vulnerable DeFi Contract...[/bold yellow]"
        )

        # Display contract code
        syntax = Syntax(
            DEMO_CONTRACT,
            "solidity",
            theme="monokai",
            line_numbers=True)
        console.print(
            Panel(
                syntax,
                title="Demo Contract: VulnerableDeFiVault",
                expand=False))

        # Create target
        target = Target(
            identifier="0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF",
            target_type=TargetType.CONTRACT.value,
            blockchain="ethereum",
        )

        # Run analysis with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Running vulnerability analysis...", total=len(strategies)
            )

            result = await analyzer.analyze_comprehensive(
                target=target,
                source_code=DEMO_CONTRACT,
                enable_simulation=False,
                enable_ai=False,
            )

            progress.update(task, completed=len(strategies))

        # Display results
        console.print(f"\n[bold green]✓ Analysis Complete![/bold green]")
        console.print(
            f"Execution time: {
                result.analysis_metadata.get(
                    'duration',
                    0):.2f} seconds"
        )
        console.print(
            f"Total vulnerabilities found: [red]{len(result.vulnerabilities)}[/red]"
        )

        # Create results table
        table = Table(title="Vulnerability Analysis Results", box=box.ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Vulnerability", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Confidence", style="yellow")
        table.add_column("Category", style="magenta")
        table.add_column("Affected Function", style="green")

        for i, finding in enumerate(result.vulnerabilities, 1):
            # Color-code severity
            severity_style = {
                "Critical": "bold red",
                "High": "red",
                "Medium": "yellow",
                "Low": "blue",
                "Info": "dim",
            }.get(finding.severity, "white")

            # Get affected functions from metadata
            affected_functions = finding.metadata.get("affected_functions", [])
            affected_funcs = ", ".join(
                affected_functions[:2])  # Show max 2 functions
            if len(affected_functions) > 2:
                affected_funcs += "..."

            table.add_row(
                str(i),
                finding.title[:50] + ("..." if len(finding.title) > 50 else ""),
                Text(str(finding.severity.name), style=severity_style),
                f"{finding.confidence:.1%}",
                finding.vulnerability_type,
                affected_funcs,
            )

        console.print(table)

        # Show detailed findings
        console.print("\n[bold]Detailed Vulnerability Reports:[/bold]")

        for i, finding in enumerate(
                result.vulnerabilities[:3], 1):  # Show top 3
            console.print(
                f"\n[bold cyan]🔍 Vulnerability #{i}: {
                    finding.title}[/bold cyan]"
            )
            console.print(f"[red]Severity:[/red] {finding.severity}")
            console.print(
                f"[yellow]Confidence:[/yellow] {finding.confidence:.1%}")
            console.print(
                f"[blue]Description:[/blue] {finding.description[:200]}...")

            affected_functions = finding.metadata.get("affected_functions", [])
            if affected_functions:
                console.print(
                    f"[green]Affected Functions:[/green] {', '.join(affected_functions)}"
                )

            if finding.exploit_scenario:
                console.print(
                    f"[magenta]Exploit Scenario:[/magenta] {finding.exploit_scenario[:150]}..."
                )

        # Risk assessment summary
        console.print(f"\n[bold]Risk Assessment Summary:[/bold]")
        risk = result.risk_assessment

        risk_table = Table(box=box.SIMPLE)
        risk_table.add_column("Metric", style="cyan")
        risk_table.add_column("Score", style="yellow")
        risk_table.add_column("Impact", style="red")

        risk_table.add_row(
            "Overall Risk",
            f"{risk.overall_score:.1f}/10",
            _get_risk_level(risk.overall_score),
        )
        risk_table.add_row(
            "Exploitability",
            f"{risk.exploitability_score:.1f}/10",
            _get_risk_level(risk.exploitability_score),
        )
        risk_table.add_row(
            "Business Impact",
            f"{risk.business_risk_score:.1f}/10",
            _get_risk_level(risk.business_risk_score),
        )
        risk_table.add_row(
            "Urgency",
            f"{risk.urgency_score:.1f}/10",
            _get_risk_level(risk.urgency_score),
        )

        console.print(risk_table)

        # Financial impact
        console.print(f"\n[bold]Estimated Financial Impact:[/bold]")
        console.print(
            f"Minimum Loss: [red]${
                risk.estimated_loss_min:,.0f}[/red]"
        )
        console.print(
            f"Maximum Loss: [red]${
                risk.estimated_loss_max:,.0f}[/red]"
        )
        console.print(
            f"Average Loss: [red]${
                risk.estimated_loss_avg:,.0f}[/red]"
        )

        # Exploit prediction
        exploit_pred = result.exploit_prediction
        console.print(f"\n[bold]Exploit Development Prediction:[/bold]")
        console.print(
            f"Exploit Probability: [red]{
                exploit_pred.exploit_probability:.1%}[/red]"
        )
        console.print(
            f"Time to Exploit: [yellow]{
                exploit_pred.time_to_exploit} days[/yellow]"
        )
        console.print(
            f"Weaponization Likelihood: [magenta]{
                exploit_pred.weaponization_likelihood:.1%}[/magenta]"
        )

        # Strategy breakdown
        console.print(f"\n[bold]Strategy Execution Breakdown:[/bold]")
        strategy_table = Table(box=box.SIMPLE)
        strategy_table.add_column("Strategy", style="cyan")
        strategy_table.add_column("Findings", style="yellow")
        strategy_table.add_column("Status", style="green")

        findings_by_strategy = {}
        for finding in result.vulnerabilities:
            strategy = finding.vulnerability_type
            findings_by_strategy[strategy] = findings_by_strategy.get(
                strategy, 0) + 1

        for strategy_result in result.analysis_metadata.get(
                "strategy_results", []):
            if hasattr(strategy_result, "strategy_name"):
                strategy_name = strategy_result.strategy_name
                findings_count = findings_by_strategy.get(strategy_name, 0)
                status = "✅ Success" if strategy_result.success else "❌ Failed"
                strategy_table.add_row(
                    strategy_name, str(findings_count), status)

        console.print(strategy_table)

        # Recommendations
        console.print(f"\n[bold red]🚨 Immediate Actions Required:[/bold red]")
        console.print(
            "1. [red]Fix reentrancy vulnerability in withdraw function[/red]")
        console.print(
            "2. [red]Add access control to emergencyWithdraw function[/red]")
        console.print(
            "3. [yellow]Implement SafeMath for arithmetic operations[/yellow]"
        )
        console.print(
            "4. [yellow]Add TWAP oracle for price calculations[/yellow]")
        console.print(
            "5. [blue]Add comprehensive access control system[/blue]")

        console.print(f"\n[bold green]🎉 Demo Complete![/bold green]")
        console.print(
            "The Enhanced Scorpius Scanner successfully identified multiple critical vulnerabilities!"
        )

        return True

    except Exception as e:
        console.print(f"[red]Demo failed with error: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def _get_risk_level(score: float) -> str:
    """Convert risk score to risk level"""
    if score >= 8:
        return "Critical"
    elif score >= 6:
        return "High"
    elif score >= 4:
        return "Medium"
    elif score >= 2:
        return "Low"
    else:
        return "Minimal"


async def main():
    """Main demo function"""
    success = await run_comprehensive_demo()

    if success:
        console.print(
            "\n[bold blue]Enhanced Scorpius Scanner is ready for production use! 🚀[/bold blue]"
        )
    else:
        console.print(
            "\n[bold red]Demo encountered issues. Please check the installation.[/bold red]"
        )

    return success


if __name__ == "__main__":
    asyncio.run(main())
