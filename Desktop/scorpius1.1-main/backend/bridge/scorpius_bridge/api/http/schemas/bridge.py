"""Pydantic schemas for bridge operations.

Request/response DTOs for bridge API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from scorpius_bridge.application.commands import InitiateBridgeTransferCommand
from scorpius_bridge.domain.models.bridge_tx import SecurityLevel


class SecurityLevelEnum(str, Enum):
    """Security level enumeration for API."""

    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    QUANTUM_RESISTANT = "quantum_resistant"


class InitiateTransferRequest(BaseModel):
    """Request to initiate a bridge transfer."""

    source_chain: str = Field(..., description="Source blockchain")
    destination_chain: str = Field(..., description="Destination blockchain")
    token_address: str = Field(..., description="Token contract address")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    sender_address: str = Field(..., description="Sender wallet address")
    recipient_address: str = Field(..., description="Recipient wallet address")
    security_level: SecurityLevelEnum = Field(
        default=SecurityLevelEnum.STANDARD,
        description="Security level for the transfer",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )

    @validator("source_chain", "destination_chain")
    def validate_chains(cls, v):
        """Validate chain names."""
        if not v or len(v) < 2:
            raise ValueError("Chain name must be at least 2 characters")
        return v.lower()

    @validator("token_address", "sender_address", "recipient_address")
    def validate_addresses(cls, v):
        """Validate addresses."""
        if not v or len(v) < 10:
            raise ValueError("Address must be at least 10 characters")
        return v

    def to_command(self) -> InitiateBridgeTransferCommand:
        """Convert to application command."""
        return InitiateBridgeTransferCommand(
            source_chain=self.source_chain,
            destination_chain=self.destination_chain,
            token_address=self.token_address,
            amount=self.amount,
            sender_address=self.sender_address,
            recipient_address=self.recipient_address,
            security_level=SecurityLevel(self.security_level.value),
            metadata=self.metadata,
        )


class BridgeTransferResponse(BaseModel):
    """Response for bridge transfer operations."""

    transfer_id: str = Field(..., description="Unique transfer ID")
    status: str = Field(..., description="Transfer status")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[datetime] = Field(
        default=None, description="Estimated completion time"
    )
    fees: Optional[Dict[str, str]] = Field(default=None, description="Fee breakdown")


class TransferDetailsResponse(BaseModel):
    """Detailed transfer information."""

    id: str
    source_chain: str
    destination_chain: str
    token_address: str
    amount: str
    sender_address: str
    recipient_address: str
    status: str
    security_level: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    source_tx_hash: Optional[str]
    destination_tx_hash: Optional[str]
    bridge_fee: str
    gas_fee: str
    validator_signatures: Dict[str, str]
    metadata: Dict[str, Any]


class TransferHistoryResponse(BaseModel):
    """Paginated transfer history."""

    transfers: List[TransferDetailsResponse]
    total: int
    page: int
    size: int
    total_pages: int


class FeeEstimateRequest(BaseModel):
    """Request for fee estimation."""

    source_chain: str
    destination_chain: str
    amount: Decimal = Field(..., gt=0)
    security_level: SecurityLevelEnum = SecurityLevelEnum.STANDARD


class FeeEstimateResponse(BaseModel):
    """Fee estimation response."""

    bridge_fee: str
    estimated_gas_fee: str
    total_fee: str
    fee_rate: float
    security_level: str
    estimated_completion_time: str
