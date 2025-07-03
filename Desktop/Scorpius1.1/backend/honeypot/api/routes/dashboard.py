"""
Dashboard-specific routes for React frontend integration
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from api.middleware.auth import authenticate_token
from fastapi import APIRouter, Depends, HTTPException, Request, status
from models.data_models import HoneypotTechnique, RiskLevel
from pydantic import BaseModel

# Configure logger
logger = logging.getLogger("api.routes.dashboard")

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStatsResponse(BaseModel):
    total_analyses: int
    honeypots_detected: int
    false_positives: int
    detection_rate: float
    recent_analyses: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    technique_distribution: Dict[str, int]


class RecentAnalysisItem(BaseModel):
    address: str
    is_honeypot: bool
    confidence: float
    risk_level: RiskLevel
    timestamp: datetime
    techniques: List[str]


class TrendDataResponse(BaseModel):
    dates: List[str]
    honeypot_counts: List[int]
    analysis_counts: List[int]
    detection_rates: List[float]


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    req: Request, days: int = 30, token: str = Depends(authenticate_token)
):
    """
    Get comprehensive dashboard statistics for React frontend

    Returns aggregated statistics for the dashboard including:
    - Total analyses performed
    - Honeypots detected
    - Detection rates
    - Recent analyses
    - Risk level distribution
    - Technique distribution
    """
    try:
        # Get repository from app state
        if not hasattr(req.app.state, "mongo_client"):
            raise HTTPException(status_code=500, detail="Database not initialized")

        mongo_client = req.app.state.mongo_client
        db = mongo_client.get_database()
        analyses_collection = db.analyses

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get total analyses
        total_analyses = await analyses_collection.count_documents(
            {"analysis_timestamp": {"$gte": start_date}}
        )

        # Get honeypots detected
        honeypots_detected = await analyses_collection.count_documents(
            {"analysis_timestamp": {"$gte": start_date}, "is_honeypot": True}
        )

        # Calculate detection rate
        detection_rate = (
            (honeypots_detected / total_analyses * 100) if total_analyses > 0 else 0
        )

        # Get recent analyses
        recent_cursor = (
            analyses_collection.find({"analysis_timestamp": {"$gte": start_date}})
            .sort("analysis_timestamp", -1)
            .limit(10)
        )

        recent_analyses = []
        async for doc in recent_cursor:
            recent_analyses.append(
                {
                    "address": doc.get("address", ""),
                    "is_honeypot": doc.get("is_honeypot", False),
                    "confidence": doc.get("confidence", 0.0),
                    "risk_level": doc.get("risk_level", "low"),
                    "timestamp": doc.get("analysis_timestamp"),
                    "techniques": doc.get("detected_techniques", []),
                }
            )

        # Get risk level distribution
        risk_pipeline = [
            {"$match": {"analysis_timestamp": {"$gte": start_date}}},
            {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}},
        ]
        risk_cursor = analyses_collection.aggregate(risk_pipeline)
        risk_distribution = {}
        async for doc in risk_cursor:
            risk_distribution[doc["_id"]] = doc["count"]

        # Get technique distribution
        technique_pipeline = [
            {"$match": {"analysis_timestamp": {"$gte": start_date}}},
            {"$unwind": "$detected_techniques"},
            {"$group": {"_id": "$detected_techniques", "count": {"$sum": 1}}},
        ]
        technique_cursor = analyses_collection.aggregate(technique_pipeline)
        technique_distribution = {}
        async for doc in technique_cursor:
            technique_distribution[doc["_id"]] = doc["count"]

        return DashboardStatsResponse(
            total_analyses=total_analyses,
            honeypots_detected=honeypots_detected,
            false_positives=total_analyses - honeypots_detected,
            detection_rate=round(detection_rate, 2),
            recent_analyses=recent_analyses,
            risk_distribution=risk_distribution,
            technique_distribution=technique_distribution,
        )

    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=TrendDataResponse)
async def get_trend_data(
    req: Request, days: int = 30, token: str = Depends(authenticate_token)
):
    """
    Get trend data for charts in React dashboard

    Returns time-series data for:
    - Daily analysis counts
    - Daily honeypot detection counts
    - Daily detection rates
    """
    try:
        # Get repository from app state
        if not hasattr(req.app.state, "mongo_client"):
            raise HTTPException(status_code=500, detail="Database not initialized")

        mongo_client = req.app.state.mongo_client
        db = mongo_client.get_database()
        analyses_collection = db.analyses

        # Calculate date range
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)

        # Aggregate daily data
        pipeline = [
            {"$match": {"analysis_timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$analysis_timestamp",
                        }
                    },
                    "total_analyses": {"$sum": 1},
                    "honeypots": {
                        "$sum": {"$cond": [{"$eq": ["$is_honeypot", True]}, 1, 0]}
                    },
                }
            },
            {"$sort": {"_id": 1}},
        ]

        cursor = analyses_collection.aggregate(pipeline)
        daily_data = {}
        async for doc in cursor:
            date = doc["_id"]
            total = doc["total_analyses"]
            honeypots = doc["honeypots"]
            detection_rate = (honeypots / total * 100) if total > 0 else 0

            daily_data[date] = {
                "total_analyses": total,
                "honeypots": honeypots,
                "detection_rate": round(detection_rate, 2),
            }

        # Fill in missing dates with zeros
        dates = []
        analysis_counts = []
        honeypot_counts = []
        detection_rates = []

        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)

            if date in daily_data:
                analysis_counts.append(daily_data[date]["total_analyses"])
                honeypot_counts.append(daily_data[date]["honeypots"])
                detection_rates.append(daily_data[date]["detection_rate"])
            else:
                analysis_counts.append(0)
                honeypot_counts.append(0)
                detection_rates.append(0.0)

        return TrendDataResponse(
            dates=dates,
            honeypot_counts=honeypot_counts,
            analysis_counts=analysis_counts,
            detection_rates=detection_rates,
        )

    except Exception as e:
        logger.error(f"Error retrieving trend data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contract/{address}/details")
async def get_contract_details(
    address: str, req: Request, token: str = Depends(authenticate_token)
):
    """
    Get detailed contract information for dashboard

    Returns comprehensive information about a specific contract
    including all historical analyses and metadata
    """
    try:
        # Address validation
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError("Invalid Ethereum address format")

        # Get repository from app state
        if not hasattr(req.app.state, "mongo_client"):
            raise HTTPException(status_code=500, detail="Database not initialized")

        mongo_client = req.app.state.mongo_client
        db = mongo_client.get_database()
        analyses_collection = db.analyses

        # Get all analyses for this contract
        cursor = analyses_collection.find({"address": address.lower()}).sort(
            "analysis_timestamp", -1
        )

        analyses = []
        async for doc in cursor:
            analyses.append(
                {
                    "analysis_id": str(doc.get("_id", "")),
                    "is_honeypot": doc.get("is_honeypot", False),
                    "confidence": doc.get("confidence", 0.0),
                    "risk_level": doc.get("risk_level", "low"),
                    "detected_techniques": doc.get("detected_techniques", []),
                    "analysis_timestamp": doc.get("analysis_timestamp"),
                    "engine_results": doc.get("engine_results", {}),
                    "transaction_history": doc.get("transaction_history", {}),
                }
            )

        if not analyses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis data found for address {address}",
            )

        # Calculate summary statistics
        total_analyses = len(analyses)
        honeypot_analyses = sum(1 for a in analyses if a["is_honeypot"])
        avg_confidence = sum(a["confidence"] for a in analyses) / total_analyses

        # Get all unique techniques detected
        all_techniques = set()
        for analysis in analyses:
            all_techniques.update(analysis["detected_techniques"])

        return {
            "address": address,
            "summary": {
                "total_analyses": total_analyses,
                "honeypot_detections": honeypot_analyses,
                "average_confidence": round(avg_confidence, 3),
                "all_techniques_detected": list(all_techniques),
                "latest_analysis": analyses[0] if analyses else None,
            },
            "analysis_history": analyses,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error retrieving contract details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_contracts(
    req: Request,
    query: str = "",
    risk_level: Optional[RiskLevel] = None,
    is_honeypot: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    token: str = Depends(authenticate_token),
):
    """
    Search and filter contracts for dashboard

    Provides advanced search and filtering capabilities for the React dashboard
    """
    try:
        # Get repository from app state
        if not hasattr(req.app.state, "mongo_client"):
            raise HTTPException(status_code=500, detail="Database not initialized")

        mongo_client = req.app.state.mongo_client
        db = mongo_client.get_database()
        analyses_collection = db.analyses

        # Build search filter
        search_filter = {}

        if query:
            # Search in address (partial match)
            search_filter["address"] = {"$regex": query.lower(), "$options": "i"}

        if risk_level:
            search_filter["risk_level"] = risk_level.value

        if is_honeypot is not None:
            search_filter["is_honeypot"] = is_honeypot

        # Get total count
        total_count = await analyses_collection.count_documents(search_filter)

        # Get results with pagination
        cursor = (
            analyses_collection.find(search_filter)
            .sort("analysis_timestamp", -1)
            .skip(offset)
            .limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append(
                {
                    "address": doc.get("address", ""),
                    "is_honeypot": doc.get("is_honeypot", False),
                    "confidence": doc.get("confidence", 0.0),
                    "risk_level": doc.get("risk_level", "low"),
                    "detected_techniques": doc.get("detected_techniques", []),
                    "analysis_timestamp": doc.get("analysis_timestamp"),
                    "analysis_id": str(doc.get("_id", "")),
                }
            )

        return {
            "results": results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count,
        }

    except Exception as e:
        logger.error(f"Error searching contracts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
