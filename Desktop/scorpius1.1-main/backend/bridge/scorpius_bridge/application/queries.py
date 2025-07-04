"""CQRS Queries for Scorpius Bridge.

Queries represent read operations that return data without changing state.
They follow the Query pattern and return DTOs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from ..domain.models.bridge_tx import SecurityLevel, TransferStatus
from ..domain.models.liquidity_pool import PoolStatus
from ..domain.models.validator import ValidatorStatus


class SortOrder(Enum):
    """Sort order for queries."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class Query:
    """Base query class."""

    pass


@dataclass
class PaginationParams:
    """Pagination parameters for queries."""

    page: int = 1
    size: int = 50
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC


@dataclass
class GetBridgeTransferQuery(Query):
    """Query to get a bridge transfer by ID."""

    transfer_id: str


@dataclass
class GetTransferHistoryQuery(Query):
    """Query to get transfer history with filters."""

    sender_address: Optional[str] = None
    recipient_address: Optional[str] = None
    source_chain: Optional[str] = None
    destination_chain: Optional[str] = None
    status: Optional[TransferStatus] = None
    security_level: Optional[SecurityLevel] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    pagination: PaginationParams = field(default_factory=PaginationParams)


@dataclass
class GetTransferStatsQuery(Query):
    """Query to get transfer statistics."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    chain: Optional[str] = None
    group_by: str = "day"  # "hour", "day", "week", "month"


@dataclass
class GetLiquidityPoolQuery(Query):
    """Query to get a liquidity pool by ID."""

    pool_id: str


@dataclass
class GetLiquidityPoolsQuery(Query):
    """Query to get liquidity pools with filters."""

    source_chain: Optional[str] = None
    destination_chain: Optional[str] = None
    token_address: Optional[str] = None
    status: Optional[PoolStatus] = None
    min_liquidity: Optional[Decimal] = None
    pagination: PaginationParams = field(default_factory=PaginationParams)


@dataclass
class GetPoolMetricsQuery(Query):
    """Query to get pool performance metrics."""

    pool_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class GetLiquidityPositionQuery(Query):
    """Query to get liquidity position for a provider."""

    provider_address: str
    pool_id: Optional[str] = None


@dataclass
class GetValidatorQuery(Query):
    """Query to get a validator by ID."""

    validator_id: str


@dataclass
class GetValidatorsQuery(Query):
    """Query to get validators with filters."""

    status: Optional[ValidatorStatus] = None
    supported_chain: Optional[str] = None
    min_stake: Optional[Decimal] = None
    min_reputation: Optional[float] = None
    is_online: Optional[bool] = None
    pagination: PaginationParams = field(default_factory=PaginationParams)


@dataclass
class GetValidatorPerformanceQuery(Query):
    """Query to get validator performance metrics."""

    validator_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class GetNetworkStatsQuery(Query):
    """Query to get overall network statistics."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class GetChainStatusQuery(Query):
    """Query to get status of supported chains."""

    chain_name: Optional[str] = None


@dataclass
class GetFeesQuery(Query):
    """Query to get fee information."""

    source_chain: str
    destination_chain: str
    amount: Decimal
    security_level: SecurityLevel = SecurityLevel.STANDARD


@dataclass
class HealthCheckQuery(Query):
    """Query to check system health."""

    component: Optional[str] = None  # "api", "database", "blockchain", "validators"


@dataclass
class GetAuditLogQuery(Query):
    """Query to get audit log entries."""

    entity_type: Optional[str] = None  # "transfer", "validator", "pool"
    entity_id: Optional[str] = None
    action: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    pagination: PaginationParams = field(default_factory=PaginationParams)


@dataclass
class SearchTransfersQuery(Query):
    """Query to search transfers with full-text search."""

    search_term: str
    filters: Optional[Dict[str, Any]] = None
    pagination: PaginationParams = field(default_factory=PaginationParams)


@dataclass
class GetRiskAnalysisQuery(Query):
    """Query to get risk analysis for a transfer."""

    source_chain: str
    destination_chain: str
    amount: Decimal
    sender_address: str
    recipient_address: str
