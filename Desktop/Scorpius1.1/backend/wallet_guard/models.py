"""
Pydantic models for Wallet Guard API
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ChainEnum(str, Enum):
    """Supported blockchain networks"""

    ETHEREUM = "ethereum"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    BASE = "base"


class TokenTypeEnum(str, Enum):
    """Supported token standards"""

    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"


class RiskLevel(str, Enum):
    """Risk assessment levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WalletCheckRequest(BaseModel):
    """Request model for wallet security check"""

    addresses: List[str] = Field(
        ..., min_items=1, max_items=25, description="Wallet addresses to check"
    )
    chains: List[ChainEnum] = Field(
        default=[ChainEnum.ETHEREUM], description="Blockchain networks to check"
    )
    include_approvals: bool = Field(
        default=True, description="Check for risky token approvals"
    )
    include_signatures: bool = Field(
        default=True, description="Check for drainer signatures"
    )
    include_spoofed: bool = Field(
        default=True, description="Check for spoofed approvals"
    )


class ApprovalRisk(BaseModel):
    """Risk assessment for a token approval"""

    spender_address: str = Field(..., description="Address with approval")
    token_address: str = Field(..., description="Token contract address")
    token_type: TokenTypeEnum = Field(..., description="Token standard")
    approved_amount: str = Field(..., description="Approved amount or token ID")
    risk_level: RiskLevel = Field(..., description="Risk assessment")
    risk_reasons: List[str] = Field(
        default=[], description="Reasons for risk classification"
    )
    last_activity: Optional[str] = Field(None, description="Last transaction timestamp")


class DrainerSignature(BaseModel):
    """Detected drainer signature pattern"""

    signature_hash: str = Field(..., description="Function signature hash")
    contract_address: str = Field(..., description="Contract address")
    risk_level: RiskLevel = Field(..., description="Risk level")
    description: str = Field(..., description="Description of the drainer pattern")
    first_seen: str = Field(..., description="First detection timestamp")


class SpoofedApproval(BaseModel):
    """Detected spoofed approval attempt"""

    fake_address: str = Field(..., description="Spoofed contract address")
    real_address: str = Field(..., description="Real contract address being spoofed")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Address similarity score"
    )
    risk_level: RiskLevel = Field(..., description="Risk level")


class WalletCheckResponse(BaseModel):
    """Response model for wallet security check"""

    wallet_address: str = Field(..., description="Checked wallet address")
    chain: ChainEnum = Field(..., description="Blockchain network")
    risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall risk score (0-100)"
    )
    overall_risk_level: RiskLevel = Field(..., description="Overall risk assessment")

    risky_approvals: List[ApprovalRisk] = Field(
        default=[], description="Risky token approvals"
    )
    drainer_signatures: List[DrainerSignature] = Field(
        default=[], description="Detected drainer signatures"
    )
    spoofed_approvals: List[SpoofedApproval] = Field(
        default=[], description="Detected spoofed approvals"
    )

    analysis_timestamp: str = Field(..., description="Analysis completion timestamp")
    result_hash: str = Field(..., description="SHA-256 hash of analysis results")


class RevokeRequest(BaseModel):
    """Request model for approval revocation"""

    wallet_address: str = Field(
        ..., description="Wallet address to revoke approvals for"
    )
    chain: ChainEnum = Field(..., description="Blockchain network")
    approval_addresses: List[str] = Field(
        ..., min_items=1, description="Addresses to revoke approvals for"
    )
    token_types: List[TokenTypeEnum] = Field(
        default=[TokenTypeEnum.ERC20], description="Token types to revoke"
    )
    gas_price_gwei: Optional[float] = Field(
        None, description="Custom gas price in Gwei"
    )


class TransactionData(BaseModel):
    """Transaction data for revocation"""

    to: str = Field(..., description="Transaction recipient")
    data: str = Field(..., description="Transaction data")
    value: str = Field(default="0", description="Transaction value in wei")
    gas_limit: str = Field(..., description="Gas limit")
    gas_price: str = Field(..., description="Gas price in wei")


class RevokeResponse(BaseModel):
    """Response model for approval revocation"""

    wallet_address: str = Field(..., description="Wallet address")
    chain: ChainEnum = Field(..., description="Blockchain network")
    transactions: List[TransactionData] = Field(
        ..., description="Revocation transactions to sign"
    )
    total_gas_estimate: str = Field(..., description="Total estimated gas cost")
    transaction_hash: str = Field(..., description="Transaction batch hash for audit")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: float = Field(..., description="Current timestamp")
