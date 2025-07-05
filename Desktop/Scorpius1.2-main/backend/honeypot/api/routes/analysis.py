import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.middleware.auth import authenticate_token
from core.detector import HoneypotDetector
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from models.data_models import AnalysisRequest, AnalysisResponse, RiskLevel
from pydantic import BaseModel, Field, validator

# Configure logger
logger = logging.getLogger("api.routes.analysis")

router = APIRouter(tags=["Analysis"])


class ContractAnalysisRequest(BaseModel):
    address: str = Field(..., description="Smart contract address")
    chain_id: int = Field(
        default=1, description="Blockchain network ID (1=Ethereum, 56=BSC)"
    )
    deep_analysis: bool = Field(
        default=False, description="Enable comprehensive analysis"
    )

    @validator("address")
    def validate_address(cls, v):
        # Basic validation for Ethereum addresses
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum address format")
        return v.lower()


class AnalysisHistoryResponse(BaseModel):
    analysis_id: str
    address: str
    is_honeypot: bool
    confidence: float
    risk_level: RiskLevel
    detected_techniques: List[str]
    analysis_timestamp: datetime


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_contract(
    request: ContractAnalysisRequest,
    req: Request,
    token: str = Depends(authenticate_token),
):
    """
    Analyze a smart contract for honeypot patterns

    This endpoint performs comprehensive analysis on a smart contract to detect
    if it's a potential honeypot. The analysis combines multiple detection engines
    including static analysis, machine learning, and symbolic execution.

    For deeper analysis that includes symbolic execution, set deep_analysis=true
    """
    try:
        logger.info(
            f"Analysis requested for address: {request.address} on chain {request.chain_id}"
        )
        start_time = time.time()

        # Get detector instance from app state
        detector = req.app.state.detector
        if not detector:
            raise HTTPException(status_code=500, detail="Detector not initialized")

        # Run the analysis
        result = await detector.analyze_contract(
            address=request.address,
            chain_id=request.chain_id,
            deep_analysis=request.deep_analysis,
        )

        # Log result
        duration = time.time() - start_time
        logger.info(
            f"Analysis completed for {request.address} in {duration:.2f}s: "
            f"honeypot={result.is_honeypot}, confidence={result.confidence:.2f}"
        )

        return result

    except ValueError as e:
        # Client errors (invalid inputs)
        logger.warning(f"Invalid analysis request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Server errors
        logger.error(
            f"Error analyzing contract {request.address}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{address}", response_model=List[AnalysisHistoryResponse])
async def get_analysis_history(
    address: str,
    req: Request,
    limit: int = 10,
    token: str = Depends(authenticate_token),
):
    """
    Get historical analysis data for a contract address

    Returns a list of previous analyses performed on the specified contract,
    ordered by most recent first.
    """
    try:
        # Address validation
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError("Invalid Ethereum address format")

        # Get detector instance
        detector = req.app.state.detector
        if not detector:
            raise HTTPException(status_code=500, detail="Detector not initialized")

        # Get history from repository
        history = await detector.get_analysis_history(address.lower(), limit=limit)

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis history found for address {address}",
            )

        return history

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(req: Request, token: str = Depends(authenticate_token)):
    """
    Get statistics about honeypot detections

    Returns aggregated statistics about analyzed contracts and honeypot detections.
    """
    try:
        # Get detector instance
        detector = req.app.state.detector
        if not detector:
            raise HTTPException(status_code=500, detail="Detector not initialized")

        # Get statistics from repository
        stats = await detector.analysis_repo.get_honeypot_statistics()

        return stats

    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
