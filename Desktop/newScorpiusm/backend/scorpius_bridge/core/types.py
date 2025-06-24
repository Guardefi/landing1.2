"""
Core data types and models for the Scorpius Bridge Network
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any


class ChainType(Enum):
    """Supported blockchain networks."""

    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    FANTOM = "fantom"
    SOLANA = "solana"
    COSMOS = "cosmos"
    POLKADOT = "polkadot"


class BridgeType(Enum):
    """Types of bridge mechanisms."""

    ATOMIC_SWAP = "atomic_swap"
    LOCK_AND_MINT = "lock_and_mint"
    BURN_AND_MINT = "burn_and_mint"
    LIQUIDITY_POOL = "liquidity_pool"
    VALIDATOR_SET = "validator_set"
    RELAY_CHAIN = "relay_chain"


class TransferStatus(Enum):
    """Bridge transfer statuses."""

    PENDING = "pending"
    INITIATED = "initiated"
    LOCKED = "locked"
    VALIDATED = "validated"
    MINTED = "minted"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SecurityLevel(Enum):
    """Security levels for bridge operations."""

    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    QUANTUM_RESISTANT = "quantum_resistant"


class ValidatorStatus(Enum):
    """Validator node statuses."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    JOINING = "joining"
    LEAVING = "leaving"
    SLASHED = "slashed"
    SUSPENDED = "suspended"


@dataclass
class ChainConfig:
    """Configuration for a blockchain network."""

    chain_type: ChainType
    chain_id: int
    name: str
    rpc_url: str
    explorer_url: str
    native_token: str
    confirmation_blocks: int
    gas_limit: int
    supported_tokens: list[str]
    bridge_contract: str
    validator_threshold: int = 2
    security_deposit: Decimal = Decimal("1000")

    # Additional production parameters
    max_gas_price: int = 100_000_000_000  # 100 gwei
    min_gas_price: int = 1_000_000_000  # 1 gwei
    block_time_seconds: int = 12
    finality_blocks: int = 64

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.confirmation_blocks < 1:
            raise ValueError("Confirmation blocks must be at least 1")
        if self.validator_threshold < 1:
            raise ValueError("Validator threshold must be at least 1")


@dataclass
class Asset:
    """Cross-chain asset definition."""

    symbol: str
    name: str
    decimals: int
    chain_addresses: dict[ChainType, str]
    is_native: bool = False
    bridgeable_chains: set[ChainType] = field(default_factory=set)
    min_transfer_amount: Decimal = Decimal("0.01")
    max_transfer_amount: Decimal = Decimal("1000000")

    # Price and market data
    usd_price: Decimal = Decimal("0")
    market_cap: Decimal = Decimal("0")
    daily_volume: Decimal = Decimal("0")

    def __post_init__(self):
        """Validate asset configuration."""
        if self.decimals < 0 or self.decimals > 18:
            raise ValueError("Asset decimals must be between 0 and 18")
        if self.min_transfer_amount >= self.max_transfer_amount:
            raise ValueError(
                "Min transfer amount must be less than max transfer amount"
            )


@dataclass
class BridgeTransfer:
    """A cross-chain bridge transfer with comprehensive tracking."""

    id: str
    from_chain: ChainType
    to_chain: ChainType
    asset: str
    amount: Decimal
    sender_address: str
    receiver_address: str
    bridge_type: BridgeType
    status: TransferStatus
    timestamp: datetime

    # Transaction details
    source_tx_hash: str | None = None
    dest_tx_hash: str | None = None
    lock_tx_hash: str | None = None
    mint_tx_hash: str | None = None

    # Security and validation
    security_level: SecurityLevel = SecurityLevel.STANDARD
    validator_signatures: list[str] = field(default_factory=list)
    required_confirmations: int = 12
    current_confirmations: int = 0

    # Fees and costs
    bridge_fee: Decimal = Decimal("0")
    gas_cost: Decimal = Decimal("0")
    exchange_rate: Decimal = Decimal("1")

    # Timing
    initiated_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime | None = None

    # Retry logic
    retry_count: int = 0
    max_retries: int = 3
    last_retry_at: datetime | None = None

    # User tracking
    user_id: str | None = None
    session_id: str | None = None

    # Metadata and context
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    @classmethod
    def create_new(
        cls,
        from_chain: ChainType,
        to_chain: ChainType,
        asset: str,
        amount: Decimal,
        sender_address: str,
        receiver_address: str,
        bridge_type: BridgeType = BridgeType.LOCK_AND_MINT,
        user_id: str | None = None,
    ) -> "BridgeTransfer":
        """Create a new bridge transfer with generated ID and timestamps."""
        transfer_id = f"bridge_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        now = datetime.now()

        return cls(
            id=transfer_id,
            from_chain=from_chain,
            to_chain=to_chain,
            asset=asset,
            amount=amount,
            sender_address=sender_address,
            receiver_address=receiver_address,
            bridge_type=bridge_type,
            status=TransferStatus.PENDING,
            timestamp=now,
            expires_at=now + timedelta(hours=24),
            user_id=user_id,
            session_id=uuid.uuid4().hex,
        )

    def can_retry(self) -> bool:
        """Check if transfer can be retried."""
        return (
            self.status in [TransferStatus.FAILED, TransferStatus.CANCELLED]
            and self.retry_count < self.max_retries
        )

    def is_expired(self) -> bool:
        """Check if transfer has expired."""
        return self.expires_at is not None and datetime.now() > self.expires_at

    def get_progress_percentage(self) -> float:
        """Get transfer progress as percentage."""
        status_progress = {
            TransferStatus.PENDING: 10,
            TransferStatus.INITIATED: 25,
            TransferStatus.LOCKED: 50,
            TransferStatus.VALIDATED: 75,
            TransferStatus.MINTED: 90,
            TransferStatus.COMPLETED: 100,
            TransferStatus.FAILED: 0,
            TransferStatus.CANCELLED: 0,
            TransferStatus.DISPUTED: 50,
        }
        return status_progress.get(self.status, 0)


@dataclass
class ValidatorNode:
    """Bridge validator node with enhanced tracking."""

    id: str
    address: str
    public_key: str
    stake_amount: Decimal
    reputation_score: float
    active: bool = True
    last_seen: datetime = field(default_factory=datetime.now)
    validated_transfers: int = 0
    slashing_events: int = 0

    # Performance metrics
    response_time_avg: float = 0.0
    uptime_percentage: float = 100.0
    validation_accuracy: float = 100.0

    # Network participation
    joined_at: datetime = field(default_factory=datetime.now)
    last_validation_at: datetime | None = None
    total_rewards_earned: Decimal = Decimal("0")
    total_slashed: Decimal = Decimal("0")

    def update_reputation(self, validation_success: bool):
        """Update validator reputation based on validation performance."""
        if validation_success:
            self.reputation_score = min(100.0, self.reputation_score + 0.1)
            self.validation_accuracy = min(100.0, self.validation_accuracy + 0.01)
        else:
            self.reputation_score = max(0.0, self.reputation_score - 1.0)
            self.validation_accuracy = max(0.0, self.validation_accuracy - 0.1)

        self.last_validation_at = datetime.now()

    def is_reliable(self) -> bool:
        """Check if validator is reliable for validation tasks."""
        return (
            self.active
            and self.reputation_score >= 50.0
            and self.uptime_percentage >= 95.0
            and self.validation_accuracy >= 95.0
        )


@dataclass
class LiquidityPoolInfo:
    """Information about a liquidity pool."""

    chain: ChainType
    asset: str
    total_liquidity: Decimal
    available_liquidity: Decimal
    utilization_rate: Decimal
    fee_rate: Decimal
    providers: dict[str, Decimal] = field(default_factory=dict)

    # Performance metrics
    daily_volume: Decimal = Decimal("0")
    weekly_volume: Decimal = Decimal("0")
    apy: float = 0.0

    def get_utilization_percentage(self) -> float:
        """Get utilization as percentage."""
        if self.total_liquidity == 0:
            return 0.0
        return float(
            (self.total_liquidity - self.available_liquidity)
            / self.total_liquidity
            * 100
        )


@dataclass
class NetworkStatistics:
    """Comprehensive network statistics."""

    total_transfers: int
    completed_transfers: int
    active_transfers: int
    failed_transfers: int

    total_volume: Decimal
    daily_volume: Decimal
    weekly_volume: Decimal

    active_validators: int
    total_validators: int

    supported_chains: int
    supported_assets: int
    liquidity_pools: int

    average_transfer_time: float
    success_rate: float
    uptime_percentage: float

    timestamp: datetime = field(default_factory=datetime.now)


# Error classes
class BridgeError(Exception):
    """Base exception for bridge operations."""

    pass


class TransferError(BridgeError):
    """Error during transfer processing."""

    pass


class ValidationError(BridgeError):
    """Error during validation."""

    pass


class LiquidityError(BridgeError):
    """Error related to liquidity."""

    pass


class ChainConnectionError(BridgeError):
    """Error connecting to blockchain."""

    pass
