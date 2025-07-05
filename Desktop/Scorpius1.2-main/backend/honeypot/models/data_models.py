from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HoneypotTechnique(str, Enum):
    HIDDEN_STATE_UPDATE = "Hidden State Update"
    BALANCE_DISORDER = "Balance Disorder"
    STRAW_MAN_CONTRACT = "Straw Man Contract"
    ACCESS_RESTRICTION = "Access Restriction"
    UNEXPECTED_REVERT = "Unexpected Revert"
    HIDDEN_TRANSFER = "Hidden Transfer"
    FALSE_ADVERTISING = "False Advertising"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisRequest(BaseModel):
    address: str = Field(..., description="Smart contract address")
    chain_id: int = Field(default=1, description="Blockchain network ID")
    deep_analysis: bool = Field(
        default=False, description="Enable comprehensive analysis"
    )


class EngineResult(BaseModel):
    confidence: float = Field(..., description="Confidence score from 0 to 1")
    techniques: Optional[List[str]] = Field(
        default_factory=list, description="Detected techniques"
    )
    error: Optional[str] = None
    prediction: Optional[bool] = None
    features_used: Optional[int] = None
    vulnerable_paths: Optional[int] = None
    coverage: Optional[float] = None


class AnalysisResponse(BaseModel):
    address: str
    is_honeypot: bool
    confidence: float
    risk_level: RiskLevel
    detected_techniques: List[str] = []
    analysis_timestamp: datetime
    engine_results: Optional[Dict[str, Any]] = None
    transaction_history: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "address": "0x1234567890abcdef1234567890abcdef12345678",
                "is_honeypot": True,
                "confidence": 0.92,
                "risk_level": "high",
                "detected_techniques": ["Hidden State Update", "Straw Man Contract"],
                "analysis_timestamp": "2025-06-24T12:34:56.789Z",
            }
        }


class AnalysisHistoryItem(BaseModel):
    analysis_id: str
    address: str
    is_honeypot: bool
    confidence: float
    risk_level: RiskLevel
    detected_techniques: List[str]
    analysis_timestamp: datetime
    requested_by: Optional[str] = None
