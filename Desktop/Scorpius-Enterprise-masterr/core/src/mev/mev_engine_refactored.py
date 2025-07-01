"""
Refactored MEV Engine using Plugin Architecture
Addresses the god-class complexity issue from code review
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field

from strategies.mev_strategy_plugins import (
    ArbitragePlugin,
    ExecutionResult,
    LiquidationPlugin,
    MEVOpportunity,
    MEVStrategyPlugin,
    SandwichAttackPlugin,
    StrategyType,
)


@dataclass
class EngineStats:
    """MEV Engine statistics"""

    start_time: float = field(default_factory=time.time)
    opportunities_detected: int = 0
    opportunities_executed: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_profit: float = 0.0
    total_gas_spent: float = 0.0
    active_strategies: int = 0


class MEVEngineRefactored:
    """
    Refactored MEV Engine with plugin-based architecture

    This addresses the god-class issue by:
    1. Separating strategy logic into plugins
    2. Using composition over inheritance
    3. Implementing clear interfaces
    4. Reducing single-class responsibility
    """

    def __init__(self, config: dict[str, any]):
        self.config = config
        self.logger = logging.getLogger("MEVEngine")

        # Engine state
        self.running = False
        self.stats = EngineStats()

        # Plugin management
        self.strategies: dict[StrategyType, MEVStrategyPlugin] = {}
        self.active_opportunities: dict[str, MEVOpportunity] = {}
        self.executed_opportunities: dict[str, ExecutionResult] = {}

        # Task management
        self.detection_tasks: list[asyncio.Task] = []
        self.execution_tasks: list[asyncio.Task] = []

        # Initialize strategies
        self._initialize_strategy_plugins()

        self.logger.info("MEV Engine initialized with plugin architecture")

    def _initialize_strategy_plugins(self):
        """Initialize strategy plugins based on configuration"""
        strategy_configs = self.config.get("strategies", {})

        # Sandwich attack strategy
        if strategy_configs.get("sandwich", {}).get("enabled", True):
            sandwich_config = strategy_configs.get("sandwich", {})
            self.strategies[StrategyType.SANDWICH] = SandwichAttackPlugin(
                sandwich_config
            )
            self.logger.info("Sandwich attack plugin initialized")

        # Arbitrage strategy
        if strategy_configs.get("arbitrage", {}).get("enabled", True):
            arbitrage_config = strategy_configs.get("arbitrage", {})
            self.strategies[StrategyType.ARBITRAGE] = ArbitragePlugin(arbitrage_config)
            self.logger.info("Arbitrage plugin initialized")

        # Liquidation strategy
        if strategy_configs.get("liquidation", {}).get("enabled", True):
            liquidation_config = strategy_configs.get("liquidation", {})
            self.strategies[StrategyType.LIQUIDATION] = LiquidationPlugin(
                liquidation_config
            )
            self.logger.info("Liquidation plugin initialized")

        # Update stats
        self.stats.active_strategies = len(self.strategies)

        self.logger.info(f"Initialized {len(self.strategies)} strategy plugins")

    def register_strategy(self, strategy: MEVStrategyPlugin):
        """Register a new strategy plugin"""
        strategy_type = strategy.get_strategy_type()
        self.strategies[strategy_type] = strategy
        self.stats.active_strategies = len(self.strategies)
        self.logger.info(f"Registered strategy plugin: {strategy.name}")

    def unregister_strategy(self, strategy_type: StrategyType):
        """Unregister a strategy plugin"""
        if strategy_type in self.strategies:
            strategy_name = self.strategies[strategy_type].name
            del self.strategies[strategy_type]
            self.stats.active_strategies = len(self.strategies)
            self.logger.info(f"Unregistered strategy plugin: {strategy_name}")

    async def start(self):
        """Start the MEV engine"""
        if self.running:
            self.logger.warning("MEV Engine is already running")
            return

        self.running = True
        self.stats.start_time = time.time()

        self.logger.info("Starting MEV Engine...")

        # Start detection loop
        detection_task = asyncio.create_task(self._detection_loop())
        self.detection_tasks.append(detection_task)

        # Start execution loop
        execution_task = asyncio.create_task(self._execution_loop())
        self.execution_tasks.append(execution_task)

        self.logger.info("MEV Engine started successfully")

    async def stop(self):
        """Stop the MEV engine"""
        if not self.running:
            self.logger.warning("MEV Engine is not running")
            return

        self.running = False

        self.logger.info("Stopping MEV Engine...")

        # Cancel all tasks
        for task in self.detection_tasks + self.execution_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(
            *self.detection_tasks, *self.execution_tasks, return_exceptions=True
        )

        self.detection_tasks.clear()
        self.execution_tasks.clear()

        self.logger.info("MEV Engine stopped")

    async def _detection_loop(self):
        """Main detection loop that coordinates all strategy plugins"""
        self.logger.info("Detection loop started")

        while self.running:
            try:
                # Get mempool data (simplified - would connect to actual mempool)
                mempool_data = await self._get_mempool_data()

                # Run detection across all strategies
                detection_tasks = []
                for _strategy_type, strategy in self.strategies.items():
                    if strategy.enabled:
                        task = asyncio.create_task(
                            self._detect_strategy_opportunities(strategy, mempool_data)
                        )
                        detection_tasks.append(task)

                # Wait for all detection tasks to complete
                if detection_tasks:
                    results = await asyncio.gather(
                        *detection_tasks, return_exceptions=True
                    )

                    # Process results
                    for result in results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Detection error: {result}")
                        elif isinstance(result, list):
                            for opportunity in result:
                                await self._queue_opportunity(opportunity)

                # Sleep before next detection cycle
                await asyncio.sleep(self.config.get("detection_interval", 1.0))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Detection loop error: {e}")
                await asyncio.sleep(5.0)  # Error backoff

        self.logger.info("Detection loop stopped")

    async def _detect_strategy_opportunities(
        self, strategy: MEVStrategyPlugin, mempool_data: dict[str, any]
    ) -> list[MEVOpportunity]:
        """Detect opportunities for a specific strategy"""
        try:
            opportunities = await strategy.detect_opportunities(mempool_data)
            self.stats.opportunities_detected += len(opportunities)

            if opportunities:
                self.logger.debug(
                    f"{strategy.name} detected {len(opportunities)} opportunities"
                )

            return opportunities

        except Exception as e:
            self.logger.error(f"Error in {strategy.name} detection: {e}")
            return []

    async def _execution_loop(self):
        """Main execution loop that processes queued opportunities"""
        self.logger.info("Execution loop started")

        while self.running:
            try:
                # Get opportunities ready for execution
                ready_opportunities = await self._get_ready_opportunities()

                if ready_opportunities:
                    # Execute opportunities concurrently (with limits)
                    execution_tasks = []
                    max_concurrent = self.config.get("max_concurrent_executions", 3)

                    for opportunity in ready_opportunities[:max_concurrent]:
                        task = asyncio.create_task(
                            self._execute_opportunity(opportunity)
                        )
                        execution_tasks.append(task)

                    if execution_tasks:
                        results = await asyncio.gather(
                            *execution_tasks, return_exceptions=True
                        )

                        # Process execution results
                        for result in results:
                            if isinstance(result, Exception):
                                self.logger.error(f"Execution error: {result}")
                            elif isinstance(result, ExecutionResult):
                                await self._process_execution_result(result)

                # Sleep before next execution cycle
                await asyncio.sleep(self.config.get("execution_interval", 0.5))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Execution loop error: {e}")
                await asyncio.sleep(5.0)  # Error backoff

        self.logger.info("Execution loop stopped")

    async def _get_mempool_data(self) -> dict[str, any]:
        """Get current mempool data (simplified simulation)"""
        # In real implementation, this would connect to mempool data sources
        return {
            "pending_swaps": {
                f"0x{uuid.uuid4().hex}": {
                    "value": 15.5,
                    "slippage_tolerance": 0.02,
                    "dex": "uniswap_v2",
                    "token_in": "ETH",
                    "token_out": "USDC",
                    "gas_price": 25e9,
                }
            },
            "price_updates": {
                "ETH/USDC": {
                    "uniswap_v2": 3500.0,
                    "sushiswap": 3515.0,
                    "balancer": 3520.0,
                }
            },
            "lending_positions": {
                f"pos_{uuid.uuid4().hex}": {
                    "health_factor": 1.05,
                    "debt_amount": 100.0,
                    "liquidation_bonus": 0.05,
                    "protocol": "aave",
                    "debt_token": "USDC",
                    "collateral_token": "ETH",
                }
            },
        }

    async def _queue_opportunity(self, opportunity: MEVOpportunity):
        """Queue an opportunity for execution"""
        # Validate opportunity before queuing
        strategy = self.strategies.get(opportunity.strategy_type)
        if strategy and await strategy.validate_opportunity(opportunity):
            self.active_opportunities[opportunity.id] = opportunity
            self.logger.debug(f"Queued opportunity: {opportunity.id}")
        else:
            self.logger.debug(f"Opportunity validation failed: {opportunity.id}")

    async def _get_ready_opportunities(self) -> list[MEVOpportunity]:
        """Get opportunities ready for execution"""
        ready = []
        time.time()

        for opp_id, opportunity in list(self.active_opportunities.items()):
            # Check if opportunity is still valid and profitable
            strategy = self.strategies.get(opportunity.strategy_type)
            if strategy:
                try:
                    # Run simulation to check profitability
                    is_profitable = await strategy.simulate_execution(opportunity)

                    if is_profitable:
                        ready.append(opportunity)
                    else:
                        # Remove unprofitable opportunity
                        del self.active_opportunities[opp_id]
                        self.logger.debug(f"Removed unprofitable opportunity: {opp_id}")

                except Exception as e:
                    self.logger.error(f"Simulation error for {opp_id}: {e}")
                    del self.active_opportunities[opp_id]

        # Sort by estimated profit (highest first)
        ready.sort(key=lambda opp: opp.estimated_profit, reverse=True)

        return ready

    async def _execute_opportunity(
        self, opportunity: MEVOpportunity
    ) -> ExecutionResult:
        """Execute a specific opportunity"""
        strategy = self.strategies.get(opportunity.strategy_type)
        if not strategy:
            raise ValueError(f"No strategy found for {opportunity.strategy_type}")

        # Remove from active opportunities
        if opportunity.id in self.active_opportunities:
            del self.active_opportunities[opportunity.id]

        self.logger.info(f"Executing opportunity: {opportunity.id}")

        # Execute the strategy
        result = await strategy.execute_strategy(opportunity)
        result.opportunity_id = opportunity.id  # Add opportunity ID to result

        # Store result
        self.executed_opportunities[opportunity.id] = result

        return result

    async def _process_execution_result(self, result: ExecutionResult):
        """Process execution result and update statistics"""
        self.stats.opportunities_executed += 1

        if result.success:
            self.stats.successful_executions += 1
            self.stats.total_profit += result.actual_profit
            self.logger.info(
                f"Successful execution: {result.transaction_hash}, "
                f"profit: {result.actual_profit:.4f} ETH"
            )
        else:
            self.stats.failed_executions += 1
            self.logger.warning(f"Failed execution: {result.error_message}")

        # Update gas tracking
        gas_cost_eth = (result.gas_used * 25e9) / 1e18  # Estimate gas cost
        self.stats.total_gas_spent += gas_cost_eth

    def get_engine_stats(self) -> dict[str, any]:
        """Get comprehensive engine statistics"""
        uptime = time.time() - self.stats.start_time

        return {
            "running": self.running,
            "uptime_seconds": uptime,
            "active_strategies": self.stats.active_strategies,
            "active_opportunities": len(self.active_opportunities),
            "opportunities_detected": self.stats.opportunities_detected,
            "opportunities_executed": self.stats.opportunities_executed,
            "successful_executions": self.stats.successful_executions,
            "failed_executions": self.stats.failed_executions,
            "success_rate": (
                self.stats.successful_executions
                / max(self.stats.opportunities_executed, 1)
            ),
            "total_profit_eth": self.stats.total_profit,
            "total_gas_spent_eth": self.stats.total_gas_spent,
            "net_profit_eth": self.stats.total_profit - self.stats.total_gas_spent,
            "strategies": {
                strategy_type.value: strategy.get_stats()
                for strategy_type, strategy in self.strategies.items()
            },
        }

    def get_recent_executions(self, limit: int = 10) -> list[dict[str, any]]:
        """Get recent execution results"""
        executions = list(self.executed_opportunities.values())
        executions.sort(key=lambda x: x.execution_time, reverse=True)

        return [
            {
                "transaction_hash": result.transaction_hash,
                "success": result.success,
                "actual_profit": result.actual_profit,
                "gas_used": result.gas_used,
                "execution_time": result.execution_time,
                "error_message": result.error_message,
            }
            for result in executions[:limit]
        ]
