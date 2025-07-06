"""
MEV Analysis API Router

Handles MEV (Maximal Extractable Value) related endpoints including:
- MEV opportunity detection
- MEV pattern analysis
- MEV statistics and insights
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..dependencies import get_current_user, get_database
from ..models import PaginationParams

router = APIRouter(prefix="/api/v1/mev", tags=["mev"])


class MEVOpportunity(BaseModel):
    """MEV opportunity data model"""

    id: UUID
    transaction_hash: str
    chain_id: int
    mev_type: str  # sandwich, arbitrage, liquidation, frontrunning
    estimated_profit: str
    confidence_score: float
    block_number: int
    timestamp: datetime
    involved_addresses: list[str]
    metadata: dict[str, Any]


class MEVAnalysisRequest(BaseModel):
    """MEV analysis request"""

    transaction_hashes: list[str]
    analysis_type: str = Field(
        ..., description="sandwich, arbitrage, liquidation, frontrunning, all"
    )


class MEVAnalysisResponse(BaseModel):
    """MEV analysis response"""

    transaction_hash: str
    mev_detected: bool
    mev_patterns: list[str]
    confidence_scores: dict[str, float]
    estimated_profit: Optional[str]
    attack_vector: Optional[str]
    involved_addresses: list[str]
    recommendations: list[str]


class MEVStatsResponse(BaseModel):
    """MEV statistics response"""

    total_opportunities: int
    total_extracted_value: str
    opportunities_by_type: dict[str, int]
    top_extractors: list[dict[str, Any]]
    avg_profit_per_opportunity: str
    success_rate: float
    trends: dict[str, Any]


@router.get("/opportunities", response_model=list[MEVOpportunity])
async def get_mev_opportunities(
    pagination: PaginationParams = Depends(),
    mev_type: Optional[str] = Query(
        None, description="sandwich, arbitrage, liquidation, frontrunning"
    ),
    chain_id: Optional[int] = Query(None),
    min_profit: Optional[float] = Query(None),
    min_confidence: Optional[float] = Query(0.5, ge=0, le=1),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get MEV opportunities with filtering.

    Supports filtering by:
    - MEV type (sandwich, arbitrage, liquidation, frontrunning)
    - Chain ID
    - Minimum profit threshold
    - Minimum confidence score
    """
    try:
        query_parts = [
            """
        SELECT mo.*, t.timestamp, t.block_number
        FROM mev_opportunities mo
        JOIN transactions t ON mo.transaction_hash = t.hash
        WHERE 1=1
        """
        ]
        params = []
        param_count = 0

        if mev_type:
            param_count += 1
            query_parts.append(f"AND mo.mev_type = ${param_count}")
            params.append(mev_type)

        if chain_id:
            param_count += 1
            query_parts.append(f"AND mo.chain_id = ${param_count}")
            params.append(chain_id)

        if min_profit:
            param_count += 1
            query_parts.append(f"AND mo.estimated_profit::numeric >= ${param_count}")
            params.append(min_profit)

        if min_confidence:
            param_count += 1
            query_parts.append(f"AND mo.confidence_score >= ${param_count}")
            params.append(min_confidence)

        query_parts.append("ORDER BY t.timestamp DESC")

        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(pagination.limit)

        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(pagination.offset)

        query = " ".join(query_parts)

        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve MEV opportunities: {str(e)}"
        )


@router.get("/opportunities/{opportunity_id}", response_model=MEVOpportunity)
async def get_mev_opportunity_details(
    opportunity_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get detailed information about a specific MEV opportunity."""
    try:
        query = """
        SELECT mo.*, t.timestamp, t.block_number, t.from_address, t.to_address,
               t.value, t.gas_price
        FROM mev_opportunities mo
        JOIN transactions t ON mo.transaction_hash = t.hash
        WHERE mo.id = $1
        """

        async with db.acquire() as conn:
            row = await conn.fetchrow(query, opportunity_id)

            if not row:
                raise HTTPException(status_code=404, detail="MEV opportunity not found")

            return dict(row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve MEV opportunity details: {str(e)}",
        )


@router.post("/analyze", response_model=list[MEVAnalysisResponse])
async def analyze_transactions_for_mev(
    analysis_request: MEVAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Analyze transactions for MEV patterns.

    Performs real-time analysis on provided transaction hashes
    to detect various MEV patterns and estimate potential profits.
    """
    try:
        if len(analysis_request.transaction_hashes) > 100:
            raise HTTPException(
                status_code=400,
                detail="Cannot analyze more than 100 transactions at once",
            )

        results = []

        async with db.acquire() as conn:
            for tx_hash in analysis_request.transaction_hashes:
                # Get transaction data
                tx_query = """
                SELECT * FROM transactions_view WHERE hash = $1
                """
                tx_row = await conn.fetchrow(tx_query, tx_hash)

                if not tx_row:
                    results.append(
                        MEVAnalysisResponse(
                            transaction_hash=tx_hash,
                            mev_detected=False,
                            mev_patterns=[],
                            confidence_scores={},
                            involved_addresses=[],
                            recommendations=["Transaction not found"],
                        )
                    )
                    continue

                tx_data = dict(tx_row)

                # Perform MEV analysis
                analysis_result = await _analyze_transaction_mev(
                    tx_data, analysis_request.analysis_type, conn
                )

                results.append(analysis_result)

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze transactions for MEV: {str(e)}"
        )


@router.get("/stats", response_model=MEVStatsResponse)
async def get_mev_stats(
    hours: int = Query(24, ge=1, le=168),
    chain_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get MEV statistics and insights."""
    try:
        time_filter = f"created_at > NOW() - INTERVAL '{hours} hours'"
        chain_filter = f"AND chain_id = {chain_id}" if chain_id else ""

        async with db.acquire() as conn:
            # Total opportunities
            total_opportunities = await conn.fetchval(
                f"""
                SELECT COUNT(*) FROM mev_opportunities 
                WHERE {time_filter} {chain_filter}
            """
            )

            # Total extracted value
            total_value = await conn.fetchval(
                f"""
                SELECT SUM(estimated_profit::numeric) FROM mev_opportunities 
                WHERE {time_filter} {chain_filter}
            """
            )

            # Opportunities by type
            type_stats = await conn.fetch(
                f"""
                SELECT mev_type, COUNT(*) as count
                FROM mev_opportunities 
                WHERE {time_filter} {chain_filter}
                GROUP BY mev_type
                ORDER BY count DESC
            """
            )

            # Top extractors
            extractor_stats = await conn.fetch(
                f"""
                SELECT 
                    mo.involved_addresses[1] as extractor,
                    COUNT(*) as opportunity_count,
                    SUM(mo.estimated_profit::numeric) as total_profit
                FROM mev_opportunities mo
                WHERE {time_filter} {chain_filter}
                AND array_length(mo.involved_addresses, 1) > 0
                GROUP BY mo.involved_addresses[1]
                ORDER BY total_profit DESC
                LIMIT 10
            """
            )

            # Average profit
            avg_profit = await conn.fetchval(
                f"""
                SELECT AVG(estimated_profit::numeric) FROM mev_opportunities 
                WHERE {time_filter} {chain_filter}
            """
            )

            # Success rate (placeholder calculation)
            success_rate = 0.75  # 75% success rate placeholder

            # Trends (placeholder)
            trends = {
                "hourly_opportunities": [5, 8, 12, 15, 20, 18, 14],
                "profit_trend": "increasing",
                "most_active_chain": 1,
                "emerging_patterns": ["multi-block arbitrage", "cross-chain MEV"],
            }

            return MEVStatsResponse(
                total_opportunities=total_opportunities or 0,
                total_extracted_value=str(total_value or 0),
                opportunities_by_type={
                    row["mev_type"]: row["count"] for row in type_stats
                },
                top_extractors=[
                    {
                        "address": row["extractor"],
                        "opportunity_count": row["opportunity_count"],
                        "total_profit": str(row["total_profit"]),
                    }
                    for row in extractor_stats
                ],
                avg_profit_per_opportunity=str(avg_profit or 0),
                success_rate=success_rate,
                trends=trends,
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve MEV stats: {str(e)}"
        )


@router.get("/patterns/trending")
async def get_trending_mev_patterns(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get trending MEV patterns and attack vectors."""
    try:
        async with db.acquire() as conn:
            # Get trending patterns
            pattern_stats = await conn.fetch(
                f"""
                SELECT 
                    mev_type,
                    COUNT(*) as occurrence_count,
                    AVG(confidence_score) as avg_confidence,
                    SUM(estimated_profit::numeric) as total_profit,
                    COUNT(*) / EXTRACT(EPOCH FROM INTERVAL '{hours} hours') * 3600 as frequency_per_hour
                FROM mev_opportunities 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
                GROUP BY mev_type
                ORDER BY occurrence_count DESC
                LIMIT $1
            """,
                limit,
            )

            # Get emerging attack vectors
            emerging_vectors = await conn.fetch(
                f"""
                SELECT DISTINCT
                    metadata->>'attack_vector' as vector,
                    COUNT(*) as count
                FROM mev_opportunities 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
                AND metadata->>'attack_vector' IS NOT NULL
                GROUP BY metadata->>'attack_vector'
                ORDER BY count DESC
                LIMIT 5
            """
            )

            return {
                "trending_patterns": [
                    {
                        "pattern": row["mev_type"],
                        "occurrence_count": row["occurrence_count"],
                        "avg_confidence": round(float(row["avg_confidence"]), 3),
                        "total_profit": str(row["total_profit"]),
                        "frequency_per_hour": round(
                            float(row["frequency_per_hour"]), 2
                        ),
                    }
                    for row in pattern_stats
                ],
                "emerging_vectors": [
                    {"vector": row["vector"], "count": row["count"]}
                    for row in emerging_vectors
                ],
                "analysis_period_hours": hours,
                "timestamp": datetime.utcnow(),
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve trending MEV patterns: {str(e)}",
        )


@router.get("/protection/recommendations")
async def get_mev_protection_recommendations(
    address: Optional[str] = Query(None),
    transaction_hash: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get MEV protection recommendations for addresses or transactions."""
    try:
        recommendations = []

        if address:
            # Analyze address MEV exposure
            async with db.acquire() as conn:
                exposure_stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_transactions,
                        COUNT(*) FILTER (WHERE mev_patterns != '{}') as mev_affected,
                        AVG(risk_score) as avg_risk_score
                    FROM transactions_view 
                    WHERE from_address = $1 OR to_address = $1
                    AND timestamp > extract(epoch from now() - interval '30 days')
                """,
                    address,
                )

                if exposure_stats and exposure_stats["total_transactions"] > 0:
                    mev_rate = (
                        exposure_stats["mev_affected"]
                        / exposure_stats["total_transactions"]
                    ) * 100

                    if mev_rate > 10:
                        recommendations.extend(
                            [
                                "Consider using MEV protection services",
                                "Implement private mempool solutions",
                                "Use flashloan protection mechanisms",
                            ]
                        )

                    if exposure_stats["avg_risk_score"] > 0.7:
                        recommendations.extend(
                            [
                                "Review transaction patterns",
                                "Consider address rotation strategies",
                            ]
                        )

        if transaction_hash:
            # Analyze specific transaction
            async with db.acquire() as conn:
                tx_analysis = await conn.fetchrow(
                    """
                    SELECT mev_patterns, risk_score, gas_price
                    FROM transactions_view 
                    WHERE hash = $1
                """,
                    transaction_hash,
                )

                if tx_analysis:
                    if tx_analysis["mev_patterns"]:
                        recommendations.extend(
                            [
                                "Transaction shows MEV patterns",
                                "Consider timing optimization",
                                "Review gas price strategy",
                            ]
                        )

        # Default recommendations
        if not recommendations:
            recommendations = [
                "Monitor transaction patterns regularly",
                "Use MEV protection tools when available",
                "Stay informed about emerging MEV techniques",
                "Consider private transaction pools for sensitive operations",
            ]

        return {
            "recommendations": recommendations,
            "address": address,
            "transaction_hash": transaction_hash,
            "generated_at": datetime.utcnow(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate MEV protection recommendations: {str(e)}",
        )


# Helper functions
async def _analyze_transaction_mev(
    tx_data: dict, analysis_type: str, db_conn
) -> MEVAnalysisResponse:
    """Analyze a single transaction for MEV patterns."""

    mev_patterns = []
    confidence_scores = {}
    estimated_profit = None
    attack_vector = None
    involved_addresses = [tx_data["from_address"], tx_data["to_address"]]
    recommendations = []

    # Analyze based on type
    if analysis_type in ["sandwich", "all"]:
        sandwich_score = await _detect_sandwich_attack(tx_data, db_conn)
        if sandwich_score > 0.5:
            mev_patterns.append("sandwich")
            confidence_scores["sandwich"] = sandwich_score
            if sandwich_score > 0.8:
                attack_vector = "sandwich_attack"
                estimated_profit = "0.05 ETH"  # Placeholder

    if analysis_type in ["arbitrage", "all"]:
        arbitrage_score = await _detect_arbitrage(tx_data, db_conn)
        if arbitrage_score > 0.5:
            mev_patterns.append("arbitrage")
            confidence_scores["arbitrage"] = arbitrage_score
            if arbitrage_score > 0.7:
                estimated_profit = "0.1 ETH"  # Placeholder

    if analysis_type in ["liquidation", "all"]:
        liquidation_score = await _detect_liquidation(tx_data, db_conn)
        if liquidation_score > 0.5:
            mev_patterns.append("liquidation")
            confidence_scores["liquidation"] = liquidation_score

    if analysis_type in ["frontrunning", "all"]:
        frontrun_score = await _detect_frontrunning(tx_data, db_conn)
        if frontrun_score > 0.5:
            mev_patterns.append("frontrunning")
            confidence_scores["frontrunning"] = frontrun_score

    # Generate recommendations
    if mev_patterns:
        recommendations.extend(
            [
                "Consider using MEV protection services",
                "Review transaction timing and gas pricing",
                "Monitor for follow-up transactions",
            ]
        )
    else:
        recommendations.append("No immediate MEV concerns detected")

    return MEVAnalysisResponse(
        transaction_hash=tx_data["hash"],
        mev_detected=len(mev_patterns) > 0,
        mev_patterns=mev_patterns,
        confidence_scores=confidence_scores,
        estimated_profit=estimated_profit,
        attack_vector=attack_vector,
        involved_addresses=involved_addresses,
        recommendations=recommendations,
    )


async def _detect_sandwich_attack(tx_data: dict, db_conn) -> float:
    """Detect sandwich attack patterns."""
    # Placeholder implementation
    # In reality, this would analyze surrounding transactions
    return 0.3  # Low confidence placeholder


async def _detect_arbitrage(tx_data: dict, db_conn) -> float:
    """Detect arbitrage opportunities."""
    # Placeholder implementation
    return 0.2  # Low confidence placeholder


async def _detect_liquidation(tx_data: dict, db_conn) -> float:
    """Detect liquidation MEV."""
    # Placeholder implementation
    return 0.1  # Low confidence placeholder


async def _detect_frontrunning(tx_data: dict, db_conn) -> float:
    """Detect frontrunning patterns."""
    # Placeholder implementation
    return 0.25  # Low confidence placeholder
