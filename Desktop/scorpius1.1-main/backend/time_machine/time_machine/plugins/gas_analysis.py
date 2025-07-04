"""
Gas Analysis Plugin for Time Machine
Provides detailed gas usage analysis and optimization insights
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.execution_vm import BaseVMAdapter
from ..core.models import AnalysisPlugin, AnalysisResult


@dataclass
class GasMetrics:
    """Gas usage metrics for analysis"""

    total_gas_used: int
    average_gas_per_tx: float
    max_gas_tx: Optional[str]
    min_gas_tx: Optional[str]
    gas_efficiency_score: float
    optimization_opportunities: List[str]


@dataclass
class TransactionGasProfile:
    """Gas profile for a single transaction"""

    tx_hash: str
    gas_limit: int
    gas_used: int
    gas_price: int
    gas_efficiency: float
    function_signature: Optional[str]
    contract_address: Optional[str]
    gas_breakdown: Dict[str, int]


class GasAnalysisPlugin(AnalysisPlugin):
    """Advanced gas analysis plugin"""

    def __init__(self):
        super().__init__(
            plugin_id="gas_analyzer",
            name="Gas Analysis Plugin",
            version="1.0.0",
            description="Comprehensive gas usage analysis and optimization insights",
            author="Time Machine Team",
            plugin_type="gas",
        )

    async def analyze(
        self, vm_adapter: BaseVMAdapter, config: Dict[str, Any]
    ) -> AnalysisResult:
        """Perform gas analysis on blockchain data"""
        start_block = config.get("start_block", 0)
        end_block = config.get("end_block", 100)
        analyze_patterns = config.get("analyze_patterns", True)
        include_optimizations = config.get("include_optimizations", True)

        try:
            # Load block data
            blocks = await vm_adapter.load_block_range(start_block, end_block)

            # Analyze gas usage
            gas_metrics = await self._analyze_gas_usage(blocks, vm_adapter)

            # Pattern analysis
            patterns = {}
            if analyze_patterns:
                patterns = await self._analyze_gas_patterns(blocks, vm_adapter)

            # Optimization suggestions
            optimizations = []
            if include_optimizations:
                optimizations = await self._generate_optimizations(
                    gas_metrics, patterns
                )

            results = {
                "metrics": gas_metrics.__dict__,
                "patterns": patterns,
                "optimizations": optimizations,
                "block_range": {"start": start_block, "end": end_block},
                "total_blocks_analyzed": len(blocks),
            }

            return AnalysisResult(
                plugin_id=self.plugin_id,
                status="completed",
                results=results,
                metadata={"analysis_type": "gas_usage", "config": config},
                score=gas_metrics.gas_efficiency_score,
            )

        except Exception as e:
            return AnalysisResult(
                plugin_id=self.plugin_id,
                status="failed",
                results={"error": str(e)},
                metadata={"config": config},
            )

    async def _analyze_gas_usage(
        self, blocks: List[Dict], vm_adapter: BaseVMAdapter
    ) -> GasMetrics:
        """Analyze gas usage across blocks"""
        total_gas = 0
        tx_count = 0
        gas_per_tx = []
        max_gas_tx = None
        min_gas_tx = None
        max_gas = 0
        min_gas = float("inf")

        for block in blocks:
            block_gas = int(block.get("gasUsed", "0x0"), 16)
            total_gas += block_gas

            for tx in block.get("transactions", []):
                if isinstance(tx, dict):
                    # Get transaction receipt for actual gas used
                    receipt = await vm_adapter._rpc_call(
                        "eth_getTransactionReceipt", [tx["hash"]]
                    )
                    if receipt:
                        gas_used = int(receipt.get("gasUsed", "0x0"), 16)
                        gas_per_tx.append(gas_used)
                        tx_count += 1

                        if gas_used > max_gas:
                            max_gas = gas_used
                            max_gas_tx = tx["hash"]

                        if gas_used < min_gas:
                            min_gas = gas_used
                            min_gas_tx = tx["hash"]

        avg_gas = sum(gas_per_tx) / len(gas_per_tx) if gas_per_tx else 0

        # Calculate efficiency score (0-100)
        efficiency_score = self._calculate_efficiency_score(gas_per_tx, total_gas)

        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            gas_per_tx, avg_gas
        )

        return GasMetrics(
            total_gas_used=total_gas,
            average_gas_per_tx=avg_gas,
            max_gas_tx=max_gas_tx,
            min_gas_tx=min_gas_tx,
            gas_efficiency_score=efficiency_score,
            optimization_opportunities=optimization_opportunities,
        )

    async def _analyze_gas_patterns(
        self, blocks: List[Dict], vm_adapter: BaseVMAdapter
    ) -> Dict[str, Any]:
        """Analyze gas usage patterns"""
        patterns = {
            "hourly_usage": defaultdict(int),
            "function_signatures": defaultdict(list),
            "contract_usage": defaultdict(int),
            "gas_price_trends": [],
            "efficiency_by_contract": {},
            "common_inefficiencies": [],
        }

        for block in blocks:
            timestamp = int(block.get("timestamp", "0x0"), 16)
            hour = timestamp // 3600  # Group by hour

            for tx in block.get("transactions", []):
                if isinstance(tx, dict):
                    receipt = await vm_adapter._rpc_call(
                        "eth_getTransactionReceipt", [tx["hash"]]
                    )
                    if receipt:
                        gas_used = int(receipt.get("gasUsed", "0x0"), 16)
                        gas_price = int(tx.get("gasPrice", "0x0"), 16)

                        patterns["hourly_usage"][hour] += gas_used
                        patterns["gas_price_trends"].append(
                            {
                                "timestamp": timestamp,
                                "gas_price": gas_price,
                                "gas_used": gas_used,
                            }
                        )

                        # Analyze function signatures
                        if tx.get("input") and len(tx["input"]) >= 10:
                            func_sig = tx["input"][:10]
                            patterns["function_signatures"][func_sig].append(gas_used)

                        # Contract usage
                        if tx.get("to"):
                            patterns["contract_usage"][tx["to"]] += gas_used

        # Process function signature efficiency
        for func_sig, gas_usages in patterns["function_signatures"].items():
            if len(gas_usages) > 1:
                avg_gas = sum(gas_usages) / len(gas_usages)
                variance = sum((x - avg_gas) ** 2 for x in gas_usages) / len(gas_usages)
                patterns["function_signatures"][func_sig] = {
                    "call_count": len(gas_usages),
                    "average_gas": avg_gas,
                    "variance": variance,
                    "min_gas": min(gas_usages),
                    "max_gas": max(gas_usages),
                }

        return dict(patterns)

    async def _generate_optimizations(
        self, gas_metrics: GasMetrics, patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        optimizations = []

        # High gas usage transactions
        if gas_metrics.max_gas_tx:
            optimizations.append(
                {
                    "type": "high_gas_transaction",
                    "priority": "high",
                    "description": f"Transaction {gas_metrics.max_gas_tx} uses excessive gas",
                    "recommendation": "Review transaction logic for gas optimization opportunities",
                    "potential_savings": "15-30%",
                }
            )

        # Function signature inefficiencies
        for func_sig, data in patterns.get("function_signatures", {}).items():
            if (
                isinstance(data, dict)
                and data.get("variance", 0) > data.get("average_gas", 0) * 0.5
            ):
                optimizations.append(
                    {
                        "type": "function_inefficiency",
                        "priority": "medium",
                        "function_signature": func_sig,
                        "description": f"Function {func_sig} shows high gas variance",
                        "recommendation": "Standardize input validation and optimize conditional logic",
                        "potential_savings": "10-20%",
                    }
                )

        # Gas price optimization
        gas_prices = [
            trend["gas_price"] for trend in patterns.get("gas_price_trends", [])
        ]
        if gas_prices:
            avg_price = sum(gas_prices) / len(gas_prices)
            max_price = max(gas_prices)
            if max_price > avg_price * 2:
                optimizations.append(
                    {
                        "type": "gas_price_optimization",
                        "priority": "low",
                        "description": "Some transactions use significantly higher gas prices than average",
                        "recommendation": "Implement dynamic gas pricing based on network conditions",
                        "potential_savings": "5-15%",
                    }
                )

        # Contract-specific optimizations
        contract_usage = patterns.get("contract_usage", {})
        for contract, total_gas in contract_usage.items():
            if total_gas > gas_metrics.total_gas_used * 0.1:  # >10% of total gas
                optimizations.append(
                    {
                        "type": "contract_optimization",
                        "priority": "medium",
                        "contract_address": contract,
                        "description": f"Contract {contract} consumes {total_gas:,} gas ({total_gas/gas_metrics.total_gas_used*100:.1f}% of total)",
                        "recommendation": "Focus optimization efforts on this high-usage contract",
                        "potential_savings": "20-40%",
                    }
                )

        return optimizations

    def _calculate_efficiency_score(
        self, gas_per_tx: List[int], total_gas: int
    ) -> float:
        """Calculate gas efficiency score (0-100)"""
        if not gas_per_tx:
            return 0.0

        # Base score on variance and average
        avg_gas = sum(gas_per_tx) / len(gas_per_tx)
        variance = sum((x - avg_gas) ** 2 for x in gas_per_tx) / len(gas_per_tx)
        std_dev = variance**0.5

        # Lower variance = higher efficiency
        coefficient_of_variation = std_dev / avg_gas if avg_gas > 0 else 1.0

        # Score inversely related to coefficient of variation
        efficiency = max(0, 100 - (coefficient_of_variation * 100))

        return min(100.0, efficiency)

    def _identify_optimization_opportunities(
        self, gas_per_tx: List[int], avg_gas: float
    ) -> List[str]:
        """Identify gas optimization opportunities"""
        opportunities = []

        if not gas_per_tx:
            return opportunities

        # High variance indicates optimization potential
        variance = sum((x - avg_gas) ** 2 for x in gas_per_tx) / len(gas_per_tx)
        std_dev = variance**0.5

        if std_dev > avg_gas * 0.3:
            opportunities.append(
                "High gas usage variance detected - review transaction patterns"
            )

        # Check for outliers
        outliers = [gas for gas in gas_per_tx if gas > avg_gas + 2 * std_dev]
        if outliers:
            opportunities.append(
                f"{len(outliers)} transactions with exceptional gas usage detected"
            )

        # Check for consistently high usage
        high_usage_count = sum(1 for gas in gas_per_tx if gas > avg_gas * 1.5)
        if high_usage_count > len(gas_per_tx) * 0.2:  # >20% of transactions
            opportunities.append(
                "Consistently high gas usage pattern - consider algorithm optimization"
            )

        return opportunities


# Factory function for plugin registration
def create_plugin() -> GasAnalysisPlugin:
    """Create and return gas analysis plugin instance"""
    return GasAnalysisPlugin()
