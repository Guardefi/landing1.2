"""Pydantic schemas for liquidity operations."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class AddLiquidityRequest(BaseModel):
    """Request to add liquidity to a pool."""

    amount: Decimal = Field(..., gt=0, description="Liquidity amount to add")
    token_address: str = Field(..., description="Token contract address")

    @validator("token_address")
    def validate_token_address(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Token address must be at least 10 characters")
        return v


class RemoveLiquidityRequest(BaseModel):
    """Request to remove liquidity from a pool."""

    shares: Decimal = Field(..., gt=0, description="LP shares to burn")


class LiquidityPoolResponse(BaseModel):
    """Liquidity pool information."""

    id: str
    name: str
    source_chain: str
    destination_chain: str
    token_address: str
    token_symbol: str
    total_liquidity: str
    available_liquidity: str
    reserved_liquidity: str
    fee_rate: float
    status: str
    utilization_rate: float
    provider_count: int
    created_at: datetime


class PoolMetricsResponse(BaseModel):
    """Pool performance metrics."""

    pool_id: str
    total_liquidity: str
    utilization_rate: float
    total_volume: str
    daily_volume: str
    total_fees_collected: str
    transfer_count: int
    avg_transfer_size: str


class LiquidityPositionResponse(BaseModel):
    """Liquidity provider position."""

    pool_id: str
    provider_address: str
    amount: str
    shares: str
    provided_at: datetime
    current_value: str
    unrealized_pnl: str
