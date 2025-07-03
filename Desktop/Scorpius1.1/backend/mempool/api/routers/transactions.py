"""
Transactions API Router

Handles all transaction-related API endpoints including:
- Transaction queries with filtering
- Transaction details and analytics
- MEV detection results
"""

from typing import Any, Optional
from uuid import UUID

from core.utils import calculate_risk_score
from fastapi import APIRouter, Depends, HTTPException, Query
from mev_analysis.mev_detector import detect_mev_patterns
from pydantic import BaseModel, Field

from ..dependencies import get_current_user, get_database
from ..models import PaginationParams, TransactionResponse

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


class TransactionFilters(BaseModel):
    """Transaction filtering parameters"""

    chain_id: Optional[int] = None
    status: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    min_gas_price: Optional[str] = None
    max_gas_price: Optional[str] = None
    has_mev: Optional[bool] = None
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None


class TransactionDetailResponse(TransactionResponse):
    """Extended transaction response with additional analytics"""

    gas_efficiency: Optional[float] = None
    mev_details: Optional[dict[str, Any]] = None
    risk_analysis: Optional[dict[str, Any]] = None
    similar_transactions: Optional[list[str]] = None


@router.get("", response_model=list[TransactionResponse])
async def get_transactions(
    pagination: PaginationParams = Depends(),
    filters: TransactionFilters = Depends(),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get transactions with advanced filtering and pagination.

    Supports filtering by:
    - Chain ID
    - Transaction status
    - Address (from/to)
    - Value range
    - Gas price range
    - MEV detection results
    - Risk score range
    """
    try:
        # Build dynamic query based on filters
        query_parts = ["SELECT * FROM transactions_view WHERE 1=1"]
        params = []
        param_count = 0

        if filters.chain_id:
            param_count += 1
            query_parts.append(f"AND chain_id = ${param_count}")
            params.append(filters.chain_id)

        if filters.status:
            param_count += 1
            query_parts.append(f"AND status = ${param_count}")
            params.append(filters.status)

        if filters.from_address:
            param_count += 1
            query_parts.append(f"AND from_address = ${param_count}")
            params.append(filters.from_address)

        if filters.to_address:
            param_count += 1
            query_parts.append(f"AND to_address = ${param_count}")
            params.append(filters.to_address)

        if filters.min_value:
            param_count += 1
            query_parts.append(f"AND value::numeric >= ${param_count}::numeric")
            params.append(filters.min_value)

        if filters.max_value:
            param_count += 1
            query_parts.append(f"AND value::numeric <= ${param_count}::numeric")
            params.append(filters.max_value)

        if filters.has_mev is not None:
            if filters.has_mev:
                query_parts.append("AND mev_patterns != '{}'")
            else:
                query_parts.append("AND mev_patterns = '{}'")

        if filters.min_risk_score is not None:
            param_count += 1
            query_parts.append(f"AND risk_score >= ${param_count}")
            params.append(filters.min_risk_score)

        if filters.max_risk_score is not None:
            param_count += 1
            query_parts.append(f"AND risk_score <= ${param_count}")
            params.append(filters.max_risk_score)

        # Add ordering and pagination
        query_parts.append("ORDER BY timestamp DESC")

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
            status_code=500, detail=f"Failed to retrieve transactions: {str(e)}"
        )


@router.get("/{transaction_hash}", response_model=TransactionDetailResponse)
async def get_transaction_details(
    transaction_hash: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get detailed information about a specific transaction.

    Includes:
    - Basic transaction data
    - MEV analysis results
    - Risk assessment
    - Similar transaction analysis
    """
    try:
        # Get transaction data
        query = """
        SELECT * FROM transactions_view 
        WHERE hash = $1
        """

        async with db.acquire() as conn:
            row = await conn.fetchrow(query, transaction_hash)

            if not row:
                raise HTTPException(status_code=404, detail="Transaction not found")

            tx_data = dict(row)

            # Enhance with additional analytics
            # Calculate gas efficiency
            if tx_data.get("gas_used") and tx_data.get("gas"):
                gas_efficiency = float(tx_data["gas_used"]) / float(tx_data["gas"])
                tx_data["gas_efficiency"] = round(gas_efficiency, 4)

            # Get MEV analysis details
            mev_patterns = detect_mev_patterns(tx_data)
            if mev_patterns:
                tx_data["mev_details"] = {
                    "patterns": mev_patterns,
                    "confidence": 0.85,  # Placeholder
                    "estimated_profit": "0.1 ETH",  # Placeholder
                }

            # Get risk analysis
            risk_score = calculate_risk_score(tx_data)
            tx_data["risk_analysis"] = {
                "score": risk_score,
                "factors": ["unusual_gas_price", "new_address"]
                if risk_score > 0.5
                else [],
                "recommendation": "monitor" if risk_score > 0.7 else "normal",
            }

            # Find similar transactions (placeholder)
            similar_query = """
            SELECT hash FROM transactions 
            WHERE from_address = $1 OR to_address = $2
            AND hash != $3
            ORDER BY timestamp DESC
            LIMIT 5
            """
            similar_rows = await conn.fetch(
                similar_query,
                tx_data["from_address"],
                tx_data["to_address"],
                transaction_hash,
            )
            tx_data["similar_transactions"] = [row["hash"] for row in similar_rows]

            return tx_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve transaction details: {str(e)}"
        )


@router.get("/{transaction_hash}/trace")
async def get_transaction_trace(
    transaction_hash: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get transaction execution trace and internal transactions.
    """
    try:
        query = """
        SELECT trace_data FROM transaction_traces 
        WHERE transaction_hash = $1
        """

        async with db.acquire() as conn:
            row = await conn.fetchrow(query, transaction_hash)

            if not row:
                raise HTTPException(
                    status_code=404, detail="Transaction trace not found"
                )

            return {"trace": row["trace_data"]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve transaction trace: {str(e)}"
        )


@router.get("/address/{address}")
async def get_address_transactions(
    address: str,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get all transactions for a specific address (sent or received).
    """
    try:
        query = """
        SELECT * FROM transactions_view 
        WHERE from_address = $1 OR to_address = $1
        ORDER BY timestamp DESC
        LIMIT $2 OFFSET $3
        """

        async with db.acquire() as conn:
            rows = await conn.fetch(query, address, pagination.limit, pagination.offset)

            return [dict(row) for row in rows]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve address transactions: {str(e)}"
        )


@router.get("/stats/summary")
async def get_transaction_stats(
    chain_id: Optional[int] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # Last 1-168 hours
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get transaction statistics summary.
    """
    try:
        time_filter = (
            f"timestamp > extract(epoch from now() - interval '{hours} hours')"
        )
        chain_filter = f"AND chain_id = {chain_id}" if chain_id else ""

        queries = {
            "total_count": f"SELECT COUNT(*) FROM transactions WHERE {time_filter} {chain_filter}",
            "total_value": f"SELECT SUM(value::numeric) FROM transactions WHERE {time_filter} {chain_filter}",
            "avg_gas_price": f"SELECT AVG(gas_price::numeric) FROM transactions WHERE {time_filter} {chain_filter}",
            "mev_count": f"SELECT COUNT(*) FROM transactions WHERE {time_filter} {chain_filter} AND mev_patterns != '{{}}'",
            "high_risk_count": f"SELECT COUNT(*) FROM transactions WHERE {time_filter} {chain_filter} AND risk_score > 0.7",
        }

        async with db.acquire() as conn:
            results = {}
            for key, query in queries.items():
                result = await conn.fetchval(query)
                results[key] = result or 0

            # Calculate additional metrics
            results["mev_percentage"] = (
                (results["mev_count"] / results["total_count"] * 100)
                if results["total_count"] > 0
                else 0
            )
            results["risk_percentage"] = (
                (results["high_risk_count"] / results["total_count"] * 100)
                if results["total_count"] > 0
                else 0
            )

            return {**results, "period_hours": hours, "chain_id": chain_id}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve transaction stats: {str(e)}"
        )
