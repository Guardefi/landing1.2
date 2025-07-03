"""Pydantic schemas for validator operations."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class RegisterValidatorRequest(BaseModel):
    """Request to register a new validator."""

    address: str = Field(..., description="Validator wallet address")
    public_key: str = Field(..., description="Validator public key")
    stake_amount: Decimal = Field(..., gt=0, description="Initial stake amount")
    supported_chains: List[str] = Field(
        ..., description="Supported blockchain networks"
    )
    commission_rate: float = Field(
        default=0.05, ge=0.0, le=1.0, description="Commission rate (0-1)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional validator metadata"
    )

    @validator("address", "public_key")
    def validate_addresses(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Address/key must be at least 10 characters")
        return v

    @validator("supported_chains")
    def validate_chains(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one supported chain required")
        return [chain.lower() for chain in v]


class ValidatorResponse(BaseModel):
    """Validator information response."""

    id: str
    address: str
    public_key: str
    status: str
    stake_amount: str
    reputation_score: float
    commission_rate: float
    supported_chains: List[str]
    joined_at: datetime
    last_seen: datetime
    is_online: bool
    voting_power: float


class ValidatorPerformanceResponse(BaseModel):
    """Validator performance metrics."""

    validator_id: str
    total_validations: int
    successful_validations: int
    failed_validations: int
    success_rate: float
    response_time_avg: float
    uptime_percentage: float
    last_activity: Optional[datetime]


class StakeRequest(BaseModel):
    """Request to stake tokens with a validator."""

    amount: Decimal = Field(..., gt=0, description="Stake amount")


class UnstakeRequest(BaseModel):
    """Request to unstake tokens from a validator."""

    amount: Decimal = Field(..., gt=0, description="Unstake amount")
