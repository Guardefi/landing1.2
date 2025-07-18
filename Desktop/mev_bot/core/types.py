"""
Core data structures for Scorpius Enterprise MEV Bot
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class StrategyType(Enum):
    """Supported MEV strategy types"""

    SANDWICH = "sandwich"
    TWO_HOP_ARB = "two_hop_arb"
    CROSS_CHAIN_BRIDGE_ARB = "cross_chain_bridge_arb"
    AAVE_V3_LIQUIDATION = "aave_v3_liquidation"
    JIT_LIQUIDITY = "jit_liquidity"
    CUSTOM = "custom"


class BundleStatus(Enum):
    """Bundle execution status"""

    PENDING = "pending"
    SUBMITTED = "submitted"
    INCLUDED = "included"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TransactionData:
    """Raw transaction data from mempool"""

    hash: str
    from_address: str
    to_address: str | None
    value: int
    gas_price: int
    gas_limit: int
    data: str
    nonce: int
    block_number: int | None = None
    timestamp: datetime | None = None
    priority_fee: int | None = None
    max_fee: int | None = None

    @property
    def value_eth(self) -> Decimal:
        """Transaction value in ETH"""
        return Decimal(self.value) / Decimal(10**18)

    @property
    def selector(self) -> str:
        """Function selector (first 4 bytes of data)"""
        return self.data[:10] if len(self.data) >= 10 else ""


@dataclass
class MEVOpportunity:
    """Detected MEV opportunity"""

    id: str
    strategy_type: StrategyType
    profit_estimate: Decimal
    gas_cost: Decimal
    net_profit: Decimal
    confidence: float
    victim_tx: TransactionData
    block_number: int
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_profitable(self) -> bool:
        """Check if opportunity is profitable after gas costs"""
        return self.net_profit > 0


@dataclass
class BundleTransaction:
    """Transaction within a bundle"""

    to: str
    value: int
    data: str
    gas_limit: int
    gas_price: int | None = None
    priority_fee: int | None = None
    max_fee: int | None = None


@dataclass
class BundleRequest:
    """Bundle request for submission to MEV relay"""

    transactions: list[BundleTransaction]
    block_number: int
    min_timestamp: int | None = None
    max_timestamp: int | None = None
    reverting_tx_hashes: list[str] = field(default_factory=list)

    def to_flashbots_bundle(self) -> dict[str, Any]:
        """Convert to Flashbots bundle format"""
        return {
            "txs": [
                {
                    "to": tx.to,
                    "value": hex(tx.value),
                    "data": tx.data,
                    "gasLimit": hex(tx.gas_limit),
                    "gasPrice": hex(tx.gas_price) if tx.gas_price else None,
                    "maxFeePerGas": hex(tx.max_fee) if tx.max_fee else None,
                    "maxPriorityFeePerGas": (
                        hex(tx.priority_fee) if tx.priority_fee else None
                    ),
                }
                for tx in self.transactions
            ],
            "blockNumber": hex(self.block_number),
            "minTimestamp": self.min_timestamp,
            "maxTimestamp": self.max_timestamp,
            "revertingTxHashes": self.reverting_tx_hashes,
        }


@dataclass
class StrategyResult:
    """Result from strategy execution"""

    success: bool
    bundle: BundleRequest | None = None
    profit: Decimal | None = None
    gas_used: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyConfig:
    """Strategy configuration"""

    enabled: bool
    min_profit_wei: int
    max_gas_price_gwei: int
    max_slippage_pct: float
    parameters: dict[str, Any] = field(default_factory=dict)


class Filter:
    """Compiled filter for transaction filtering"""

    def __init__(self, expression: str):
        """
        Initialize filter with expression

        Args:
            expression: Filter expression like "(valueEth > 1.0) & (to in hotPairs)"
        """
        self.expression = expression
        self._compiled = self._compile_expression(expression)

    def _compile_expression(self, expr: str) -> Callable[[TransactionData], bool]:
        """Compile expression to bytecode for fast evaluation"""
        # This would implement the DSL compiler
        # For now, return a simple lambda
        return lambda tx: True

    def matches(self, tx: TransactionData) -> bool:
        """Check if transaction matches filter"""
        try:
            return self._compiled(tx)
        except Exception:
            return False


@dataclass
class GasConfig:
    """Gas configuration for transaction execution"""

    base_fee_multiplier: float = 1.1
    priority_fee_percentile: int = 95  # Use 95th percentile priority fee
    max_fee_per_gas: int | None = None
    max_priority_fee_per_gas: int | None = None
    gas_limit_multiplier: float = 1.2


@dataclass
class WalletConfig:
    """Wallet configuration for strategy execution"""

    address: str
    private_key: str | None = None  # Only for dev mode
    kms_key_id: str | None = None  # For production
    nonce: int | None = None


@dataclass
class RelayConfig:
    """MEV relay configuration"""

    name: str
    endpoint: str
    public_key: str
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    last_updated: datetime | None = None
