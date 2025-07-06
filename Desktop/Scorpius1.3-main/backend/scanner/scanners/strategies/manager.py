"""
Enhanced Strategy Manager
Orchestrates advanced vulnerability detection strategies with parallel execution
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from core.models import Target, VulnerabilityFinding

from .access_control_strategy import AccessControlStrategy
from .arithmetic_overflow_strategy import ArithmeticOverflowStrategy
from .base import BaseStrategy, StrategyContext
from .flash_loan_strategy import FlashLoanAttackStrategy
from .reentrancy_strategy import ReentrancyStrategy


@dataclass
class StrategyResult:
    """Result from strategy execution"""

    strategy_name: str
    findings: List[VulnerabilityFinding]
    execution_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class ScanReport:
    """Comprehensive scan report"""

    target: Target
    strategies_executed: int
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings_by_strategy: Dict[str, int]
    total_execution_time: float
    start_time: datetime
    end_time: datetime
    findings: List[VulnerabilityFinding]
    strategy_results: List[StrategyResult]


class EnhancedStrategyManager:
    """Manages and executes vulnerability detection strategies"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the strategy manager"""
        self.config = config or {}
        self.logger = logging.getLogger("scorpius.strategy_manager")
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_execution_order: List[str] = []

        # Initialize built-in strategies
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available strategies"""
        # Core vulnerability strategies
        self.register_strategy(ReentrancyStrategy())
        self.register_strategy(FlashLoanAttackStrategy())
        self.register_strategy(AccessControlStrategy())
        self.register_strategy(ArithmeticOverflowStrategy())

        # Set default execution order
        self.strategy_execution_order = [
            "reentrancy",
            "flash_loan_attack",
            "access_control",
            "arithmetic_overflow",
        ]

        self.logger.info(
            f"Initialized {len(self.strategies)} vulnerability detection strategies"
        )

    def register_strategy(self, strategy: BaseStrategy) -> None:
        """Register a new strategy"""
        self.strategies[strategy.name] = strategy
        self.logger.debug(f"Registered strategy: {strategy.name}")

    def unregister_strategy(self, strategy_name: str) -> None:
        """Unregister a strategy"""
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            if strategy_name in self.strategy_execution_order:
                self.strategy_execution_order.remove(strategy_name)
            self.logger.debug(f"Unregistered strategy: {strategy_name}")

    def get_strategy(self, strategy_name: str) -> Optional[BaseStrategy]:
        """Get a specific strategy by name"""
        return self.strategies.get(strategy_name)

    def list_strategies(self) -> List[str]:
        """List all registered strategy names"""
        return list(self.strategies.keys())

    def set_execution_order(self, strategy_names: List[str]) -> None:
        """Set the order in which strategies are executed"""
        # Validate that all strategy names exist
        invalid_strategies = [
            name for name in strategy_names if name not in self.strategies
        ]
        if invalid_strategies:
            raise ValueError(f"Invalid strategy names: {invalid_strategies}")

        self.strategy_execution_order = strategy_names
        self.logger.info(f"Updated strategy execution order: {strategy_names}")

    async def execute_all_strategies(
        self,
        target: Target,
        source_code: Optional[str] = None,
        bytecode: Optional[str] = None,
        transaction_history: Optional[List[Dict[str, Any]]] = None,
        simulation_engine: Optional[Any] = None,
        web3_provider: Optional[Any] = None,
        parallel_execution: bool = True,
        enabled_strategies: Optional[List[str]] = None,
    ) -> ScanReport:
        """
        Execute all enabled strategies against the target

        Args:
            target: Target to analyze
            source_code: Contract source code
            bytecode: Contract bytecode
            transaction_history: Historical transaction data
            simulation_engine: Simulation engine instance
            web3_provider: Web3 provider instance
            parallel_execution: Whether to run strategies in parallel
            enabled_strategies: List of strategy names to run (None for all)

        Returns:
            Comprehensive scan report
        """
        start_time = datetime.now()
        self.logger.info(f"Starting vulnerability scan for target: {target.identifier}")

        # Create strategy context
        context = StrategyContext(
            target=target,
            source_code=source_code,
            bytecode=bytecode,
            transaction_history=transaction_history,
            simulation_engine=simulation_engine,
            web3_provider=web3_provider,
        )

        # Determine which strategies to run
        strategies_to_run = self._get_strategies_to_run(enabled_strategies)

        # Execute strategies
        if parallel_execution and len(strategies_to_run) > 1:
            strategy_results = await self._execute_strategies_parallel(
                context, strategies_to_run
            )
        else:
            strategy_results = await self._execute_strategies_sequential(
                context, strategies_to_run
            )

        # Generate scan report
        end_time = datetime.now()
        scan_report = self._generate_scan_report(
            target, strategy_results, start_time, end_time
        )

        self.logger.info(
            f"Scan completed: {scan_report.total_findings} findings from "
            f"{scan_report.strategies_executed} strategies in "
            f"{scan_report.total_execution_time:.2f} seconds"
        )

        return scan_report

    def _get_strategies_to_run(
        self, enabled_strategies: Optional[List[str]]
    ) -> List[str]:
        """Determine which strategies should be executed"""
        if enabled_strategies:
            # Use specified strategies
            strategies_to_run = [
                name
                for name in enabled_strategies
                if name in self.strategies and self.strategies[name].is_enabled()
            ]
        else:
            # Use all enabled strategies in execution order
            strategies_to_run = [
                name
                for name in self.strategy_execution_order
                if name in self.strategies and self.strategies[name].is_enabled()
            ]

            # Add any enabled strategies not in execution order
            for name in self.strategies:
                if name not in strategies_to_run and self.strategies[name].is_enabled():
                    strategies_to_run.append(name)

        self.logger.info(
            f"Running {len(strategies_to_run)} strategies: {strategies_to_run}"
        )
        return strategies_to_run

    async def _execute_strategies_parallel(
        self, context: StrategyContext, strategy_names: List[str]
    ) -> List[StrategyResult]:
        """Execute strategies in parallel"""
        self.logger.info("Executing strategies in parallel")

        tasks = []
        for strategy_name in strategy_names:
            strategy = self.strategies[strategy_name]
            task = asyncio.create_task(
                self._execute_single_strategy(strategy, context),
                name=f"strategy_{strategy_name}",
            )
            tasks.append(task)

        # Wait for all strategies to complete
        strategy_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(strategy_results):
            strategy_name = strategy_names[i]
            if isinstance(result, Exception):
                self.logger.error(
                    f"Strategy {strategy_name} failed with exception: {result}"
                )
                processed_results.append(
                    StrategyResult(
                        strategy_name=strategy_name,
                        findings=[],
                        execution_time=0.0,
                        success=False,
                        error_message=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_strategies_sequential(
        self, context: StrategyContext, strategy_names: List[str]
    ) -> List[StrategyResult]:
        """Execute strategies sequentially"""
        self.logger.info("Executing strategies sequentially")

        strategy_results = []
        for strategy_name in strategy_names:
            strategy = self.strategies[strategy_name]
            result = await self._execute_single_strategy(strategy, context)
            strategy_results.append(result)

        return strategy_results

    async def _execute_single_strategy(
        self, strategy: BaseStrategy, context: StrategyContext
    ) -> StrategyResult:
        """Execute a single strategy and measure performance"""
        start_time = asyncio.get_event_loop().time()

        try:
            self.logger.debug(f"Executing strategy: {strategy.name}")
            findings = await strategy.run_with_timeout(context)
            execution_time = asyncio.get_event_loop().time() - start_time

            self.logger.debug(
                f"Strategy {strategy.name} completed: {len(findings)} findings "
                f"in {execution_time:.2f} seconds"
            )

            return StrategyResult(
                strategy_name=strategy.name,
                findings=findings,
                execution_time=execution_time,
                success=True,
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Strategy {strategy.name} failed: {e}")

            return StrategyResult(
                strategy_name=strategy.name,
                findings=[],
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def _generate_scan_report(
        self,
        target: Target,
        strategy_results: List[StrategyResult],
        start_time: datetime,
        end_time: datetime,
    ) -> ScanReport:
        """Generate comprehensive scan report"""
        # Collect all findings
        all_findings = []
        for result in strategy_results:
            all_findings.extend(result.findings)

        # Calculate statistics
        findings_by_severity = {}
        for finding in all_findings:
            severity = finding.severity
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        findings_by_strategy = {}
        for result in strategy_results:
            findings_by_strategy[result.strategy_name] = len(result.findings)

        total_execution_time = (end_time - start_time).total_seconds()
        successful_strategies = sum(1 for result in strategy_results if result.success)

        return ScanReport(
            target=target,
            strategies_executed=successful_strategies,
            total_findings=len(all_findings),
            findings_by_severity=findings_by_severity,
            findings_by_strategy=findings_by_strategy,
            total_execution_time=total_execution_time,
            start_time=start_time,
            end_time=end_time,
            findings=all_findings,
            strategy_results=strategy_results,
        )

    async def execute_strategy(
        self,
        strategy_name: str,
        target: Target,
        source_code: Optional[str] = None,
        bytecode: Optional[str] = None,
        transaction_history: Optional[List[Dict[str, Any]]] = None,
        simulation_engine: Optional[Any] = None,
        web3_provider: Optional[Any] = None,
    ) -> StrategyResult:
        """Execute a specific strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy '{strategy_name}' not found")

        strategy = self.strategies[strategy_name]
        if not strategy.is_enabled():
            raise ValueError(f"Strategy '{strategy_name}' is disabled")

        context = StrategyContext(
            target=target,
            source_code=source_code,
            bytecode=bytecode,
            transaction_history=transaction_history,
            simulation_engine=simulation_engine,
            web3_provider=web3_provider,
        )

        return await self._execute_single_strategy(strategy, context)

    def get_scan_summary(self, scan_report: ScanReport) -> Dict[str, Any]:
        """Generate a summary of the scan report"""
        return {
            "target_address": scan_report.target.identifier,
            "scan_duration": f"{scan_report.total_execution_time:.2f} seconds",
            "strategies_executed": scan_report.strategies_executed,
            "total_findings": scan_report.total_findings,
            "findings_by_severity": scan_report.findings_by_severity,
            "findings_by_strategy": scan_report.findings_by_strategy,
            "critical_findings": scan_report.findings_by_severity.get("Critical", 0),
            "high_findings": scan_report.findings_by_severity.get("High", 0),
            "medium_findings": scan_report.findings_by_severity.get("Medium", 0),
            "low_findings": scan_report.findings_by_severity.get("Low", 0),
            "scan_timestamp": scan_report.start_time.isoformat(),
        }
