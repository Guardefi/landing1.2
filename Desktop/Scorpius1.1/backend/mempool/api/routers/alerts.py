"""
Alerts API Router

Handles all alert-related API endpoints including:
- Alert queries with filtering
- Alert management (acknowledge, dismiss)
- Alert subscriptions and notifications
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..dependencies import get_current_user, get_database
from ..models import AlertResponse, AlertSeverity, PaginationParams

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertFilters(BaseModel):
    """Alert filtering parameters"""

    severity: Optional[AlertSeverity] = None
    chain_id: Optional[int] = None
    rule_id: Optional[UUID] = None
    status: Optional[str] = Field(None, description="pending, acknowledged, dismissed")
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    tags: Optional[list[str]] = None


class AlertUpdateRequest(BaseModel):
    """Alert update request"""

    status: str = Field(..., description="acknowledged, dismissed")
    notes: Optional[str] = None


class AlertStatsResponse(BaseModel):
    """Alert statistics response"""

    total_alerts: int
    alerts_by_severity: dict[str, int]
    alerts_by_chain: dict[int, int]
    resolution_rate: float
    avg_response_time_minutes: float
    top_triggered_rules: list[dict[str, Any]]


@router.get("", response_model=list[AlertResponse])
async def get_alerts(
    pagination: PaginationParams = Depends(),
    filters: AlertFilters = Depends(),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get alerts with advanced filtering and pagination.

    Supports filtering by:
    - Severity level
    - Chain ID
    - Rule ID
    - Status (pending, acknowledged, dismissed)
    - Date range
    - Tags
    """
    try:
        # Build dynamic query
        query_parts = [
            """
        SELECT a.*, r.name as rule_name
        FROM alerts a 
        LEFT JOIN rules r ON a.rule_id = r.id
        WHERE 1=1
        """
        ]
        params = []
        param_count = 0

        if filters.severity:
            param_count += 1
            query_parts.append(f"AND a.severity = ${param_count}")
            params.append(filters.severity.value)

        if filters.chain_id:
            param_count += 1
            query_parts.append(f"AND a.chain_id = ${param_count}")
            params.append(filters.chain_id)

        if filters.rule_id:
            param_count += 1
            query_parts.append(f"AND a.rule_id = ${param_count}")
            params.append(filters.rule_id)

        if filters.status:
            param_count += 1
            query_parts.append(f"AND a.status = ${param_count}")
            params.append(filters.status)

        if filters.from_date:
            param_count += 1
            query_parts.append(f"AND a.created_at >= ${param_count}")
            params.append(filters.from_date)

        if filters.to_date:
            param_count += 1
            query_parts.append(f"AND a.created_at <= ${param_count}")
            params.append(filters.to_date)

        if filters.tags:
            param_count += 1
            query_parts.append(f"AND a.tags && ${param_count}")
            params.append(filters.tags)

        # Add ordering and pagination
        query_parts.append("ORDER BY a.created_at DESC")

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
            status_code=500, detail=f"Failed to retrieve alerts: {str(e)}"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_details(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get detailed information about a specific alert."""
    try:
        query = """
        SELECT a.*, r.name as rule_name, r.description as rule_description,
               t.hash as transaction_hash, t.from_address, t.to_address, t.value
        FROM alerts a
        LEFT JOIN rules r ON a.rule_id = r.id
        LEFT JOIN transactions t ON a.transaction_hash = t.hash
        WHERE a.id = $1
        """

        async with db.acquire() as conn:
            row = await conn.fetchrow(query, alert_id)

            if not row:
                raise HTTPException(status_code=404, detail="Alert not found")

            return dict(row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve alert details: {str(e)}"
        )


@router.patch("/{alert_id}")
async def update_alert(
    alert_id: UUID,
    update_data: AlertUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Update alert status (acknowledge or dismiss)."""
    try:
        # Validate status
        if update_data.status not in ["acknowledged", "dismissed"]:
            raise HTTPException(
                status_code=400, detail="Status must be 'acknowledged' or 'dismissed'"
            )

        query = """
        UPDATE alerts 
        SET status = $1, updated_at = NOW(), updated_by = $2, notes = $3
        WHERE id = $4
        RETURNING id
        """

        async with db.acquire() as conn:
            result = await conn.fetchval(
                query,
                update_data.status,
                current_user["user_id"],
                update_data.notes,
                alert_id,
            )

            if not result:
                raise HTTPException(status_code=404, detail="Alert not found")

            return {
                "id": alert_id,
                "status": update_data.status,
                "message": f"Alert {update_data.status} successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")


@router.post("/bulk-update")
async def bulk_update_alerts(
    alert_ids: list[UUID],
    update_data: AlertUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Bulk update multiple alerts."""
    try:
        if len(alert_ids) > 100:
            raise HTTPException(
                status_code=400, detail="Cannot update more than 100 alerts at once"
            )

        # Validate status
        if update_data.status not in ["acknowledged", "dismissed"]:
            raise HTTPException(
                status_code=400, detail="Status must be 'acknowledged' or 'dismissed'"
            )

        query = """
        UPDATE alerts 
        SET status = $1, updated_at = NOW(), updated_by = $2, notes = $3
        WHERE id = ANY($4)
        RETURNING id
        """

        async with db.acquire() as conn:
            results = await conn.fetch(
                query,
                update_data.status,
                current_user["user_id"],
                update_data.notes,
                alert_ids,
            )

            updated_count = len(results)

            return {
                "updated_count": updated_count,
                "status": update_data.status,
                "message": f"{updated_count} alerts {update_data.status} successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update alerts: {str(e)}"
        )


@router.get("/stats/summary", response_model=AlertStatsResponse)
async def get_alert_stats(
    hours: int = Query(24, ge=1, le=168),  # Last 1-168 hours
    chain_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get alert statistics summary."""
    try:
        time_filter = f"created_at > NOW() - INTERVAL '{hours} hours'"
        chain_filter = f"AND chain_id = {chain_id}" if chain_id else ""

        async with db.acquire() as conn:
            # Total alerts
            total_alerts = await conn.fetchval(
                f"SELECT COUNT(*) FROM alerts WHERE {time_filter} {chain_filter}"
            )

            # Alerts by severity
            severity_stats = await conn.fetch(
                f"""
                SELECT severity, COUNT(*) as count
                FROM alerts 
                WHERE {time_filter} {chain_filter}
                GROUP BY severity
            """
            )

            # Alerts by chain
            chain_stats = await conn.fetch(
                f"""
                SELECT chain_id, COUNT(*) as count
                FROM alerts 
                WHERE {time_filter} {chain_filter}
                GROUP BY chain_id
                ORDER BY count DESC
            """
            )

            # Resolution rate
            resolution_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status IN ('acknowledged', 'dismissed')) as resolved
                FROM alerts 
                WHERE {time_filter} {chain_filter}
            """
            )

            resolution_rate = (
                (resolution_stats["resolved"] / resolution_stats["total"] * 100)
                if resolution_stats["total"] > 0
                else 0
            )

            # Average response time (placeholder calculation)
            avg_response_time = await conn.fetchval(
                f"""
                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60)
                FROM alerts 
                WHERE {time_filter} {chain_filter} 
                AND status IN ('acknowledged', 'dismissed')
            """
            )

            # Top triggered rules
            top_rules = await conn.fetch(
                f"""
                SELECT r.id, r.name, COUNT(*) as alert_count
                FROM alerts a
                JOIN rules r ON a.rule_id = r.id
                WHERE {time_filter} {chain_filter}
                GROUP BY r.id, r.name
                ORDER BY alert_count DESC
                LIMIT 10
            """
            )

            return AlertStatsResponse(
                total_alerts=total_alerts or 0,
                alerts_by_severity={
                    row["severity"]: row["count"] for row in severity_stats
                },
                alerts_by_chain={row["chain_id"]: row["count"] for row in chain_stats},
                resolution_rate=round(resolution_rate, 2),
                avg_response_time_minutes=round(avg_response_time or 0, 2),
                top_triggered_rules=[
                    {
                        "rule_id": str(row["id"]),
                        "rule_name": row["name"],
                        "alert_count": row["alert_count"],
                    }
                    for row in top_rules
                ],
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve alert stats: {str(e)}"
        )


@router.get("/feed/live")
async def get_live_alert_feed(
    severity: Optional[AlertSeverity] = Query(None),
    chain_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get live alert feed for real-time dashboard updates."""
    try:
        query_parts = [
            """
        SELECT a.*, r.name as rule_name
        FROM alerts a 
        LEFT JOIN rules r ON a.rule_id = r.id
        WHERE a.created_at > NOW() - INTERVAL '1 hour'
        """
        ]
        params = []
        param_count = 0

        if severity:
            param_count += 1
            query_parts.append(f"AND a.severity = ${param_count}")
            params.append(severity.value)

        if chain_id:
            param_count += 1
            query_parts.append(f"AND a.chain_id = ${param_count}")
            params.append(chain_id)

        query_parts.append("ORDER BY a.created_at DESC")

        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(limit)

        query = " ".join(query_parts)

        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return {
                "alerts": [dict(row) for row in rows],
                "timestamp": datetime.utcnow(),
                "total_count": len(rows),
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve live alert feed: {str(e)}"
        )


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Delete an alert (admin only)."""
    try:
        # Check if user has admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        query = "DELETE FROM alerts WHERE id = $1 RETURNING id"

        async with db.acquire() as conn:
            result = await conn.fetchval(query, alert_id)

            if not result:
                raise HTTPException(status_code=404, detail="Alert not found")

            return {"id": alert_id, "message": "Alert deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")
