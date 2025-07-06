"""
Analytics API Router

Handles analytics and reporting endpoints including:
- System performance metrics
- Transaction analytics
- Custom dashboard data
- Export functionality
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..dependencies import get_current_user, get_database
from ..models import PaginationParams

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class DashboardMetrics(BaseModel):
    """Dashboard overview metrics"""

    total_transactions: int
    total_alerts: int
    active_rules: int
    chains_monitored: int
    avg_processing_time_ms: float
    system_health_score: float
    uptime_percentage: float
    recent_activity: dict[str, Any]


class TimeSeriesData(BaseModel):
    """Time series data point"""

    timestamp: datetime
    value: float
    metadata: Optional[dict[str, Any]] = None


class AnalyticsReport(BaseModel):
    """Analytics report response"""

    report_id: str
    title: str
    description: str
    time_range: dict[str, datetime]
    metrics: dict[str, Any]
    charts: list[dict[str, Any]]
    generated_at: datetime


class CustomQuery(BaseModel):
    """Custom analytics query"""

    query_name: str
    description: str
    sql_query: str
    parameters: Optional[dict[str, Any]] = None
    visualization_type: str = Field(..., description="chart, table, metric")


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get comprehensive dashboard metrics for the main overview.
    """
    try:
        async with db.acquire() as conn:
            # Basic counts
            total_tx = await conn.fetchval("SELECT COUNT(*) FROM transactions")
            total_alerts = await conn.fetchval("SELECT COUNT(*) FROM alerts")
            active_rules = await conn.fetchval(
                "SELECT COUNT(*) FROM rules WHERE enabled = true"
            )

            # Chain monitoring
            chains_monitored = await conn.fetchval(
                "SELECT COUNT(DISTINCT chain_id) FROM transactions"
            )

            # Processing performance
            avg_processing = await conn.fetchval(
                """
                SELECT AVG(EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000)
                FROM transaction_processing_log 
                WHERE received_at > NOW() - INTERVAL '1 hour'
            """
            )

            # System health (placeholder calculation)
            system_health = 95.5  # Placeholder
            uptime_percentage = 99.9  # Placeholder

            # Recent activity
            recent_tx_count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM transactions 
                WHERE timestamp > extract(epoch from now() - interval '1 hour')
            """
            )

            recent_alerts = await conn.fetchval(
                """
                SELECT COUNT(*) FROM alerts 
                WHERE created_at > NOW() - INTERVAL '1 hour'
            """
            )

            recent_activity = {
                "transactions_last_hour": recent_tx_count or 0,
                "alerts_last_hour": recent_alerts or 0,
                "processing_queue_size": 0,  # Placeholder
                "error_rate": 0.1,  # Placeholder
            }

            return DashboardMetrics(
                total_transactions=total_tx or 0,
                total_alerts=total_alerts or 0,
                active_rules=active_rules or 0,
                chains_monitored=chains_monitored or 0,
                avg_processing_time_ms=avg_processing or 45.0,
                system_health_score=system_health,
                uptime_percentage=uptime_percentage,
                recent_activity=recent_activity,
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard metrics: {str(e)}"
        )


@router.get("/timeseries/transactions")
async def get_transaction_timeseries(
    hours: int = Query(24, ge=1, le=168),
    interval: str = Query("hour", description="minute, hour, day"),
    chain_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get transaction count time series data.
    """
    try:
        # Validate interval
        if interval not in ["minute", "hour", "day"]:
            raise HTTPException(
                status_code=400, detail="Interval must be 'minute', 'hour', or 'day'"
            )

        # Build query based on interval
        if interval == "minute":
            date_trunc = "minute"
            time_range = f"{hours} hours"
        elif interval == "hour":
            date_trunc = "hour"
            time_range = f"{hours} hours"
        else:  # day
            date_trunc = "day"
            time_range = f"{hours // 24} days" if hours >= 24 else "1 day"

        chain_filter = f"AND chain_id = {chain_id}" if chain_id else ""

        async with db.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT 
                    date_trunc('{date_trunc}', to_timestamp(timestamp)) as time_bucket,
                    COUNT(*) as transaction_count,
                    AVG(gas_price::numeric) as avg_gas_price,
                    SUM(CASE WHEN mev_patterns != '{{}}' THEN 1 ELSE 0 END) as mev_count
                FROM transactions 
                WHERE timestamp > extract(epoch from now() - interval '{time_range}')
                {chain_filter}
                GROUP BY time_bucket
                ORDER BY time_bucket
            """
            )

            return {
                "data": [
                    {
                        "timestamp": row["time_bucket"],
                        "transaction_count": row["transaction_count"],
                        "avg_gas_price": float(row["avg_gas_price"])
                        if row["avg_gas_price"]
                        else 0,
                        "mev_count": row["mev_count"],
                    }
                    for row in rows
                ],
                "interval": interval,
                "hours": hours,
                "chain_id": chain_id,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transaction timeseries: {str(e)}",
        )


@router.get("/timeseries/alerts")
async def get_alert_timeseries(
    hours: int = Query(24, ge=1, le=168),
    interval: str = Query("hour", description="minute, hour, day"),
    severity: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get alert count time series data.
    """
    try:
        # Validate interval
        if interval not in ["minute", "hour", "day"]:
            raise HTTPException(
                status_code=400, detail="Interval must be 'minute', 'hour', or 'day'"
            )

        severity_filter = f"AND severity = '{severity}'" if severity else ""

        async with db.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT 
                    date_trunc('{interval}', created_at) as time_bucket,
                    COUNT(*) as alert_count,
                    COUNT(*) FILTER (WHERE severity = 'critical') as critical_count,
                    COUNT(*) FILTER (WHERE severity = 'high') as high_count,
                    COUNT(*) FILTER (WHERE severity = 'medium') as medium_count,
                    COUNT(*) FILTER (WHERE severity = 'low') as low_count
                FROM alerts 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
                {severity_filter}
                GROUP BY time_bucket
                ORDER BY time_bucket
            """
            )

            return {
                "data": [
                    {
                        "timestamp": row["time_bucket"],
                        "alert_count": row["alert_count"],
                        "by_severity": {
                            "critical": row["critical_count"],
                            "high": row["high_count"],
                            "medium": row["medium_count"],
                            "low": row["low_count"],
                        },
                    }
                    for row in rows
                ],
                "interval": interval,
                "hours": hours,
                "severity_filter": severity,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve alert timeseries: {str(e)}"
        )


@router.get("/performance/system")
async def get_system_performance(
    hours: int = Query(24, ge=1, le=168),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get system performance metrics.
    """
    try:
        async with db.acquire() as conn:
            # Processing times
            processing_stats = await conn.fetchrow(
                f"""
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000) as avg_processing_ms,
                    MIN(EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000) as min_processing_ms,
                    MAX(EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000) as max_processing_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000) as p95_processing_ms
                FROM transaction_processing_log 
                WHERE received_at > NOW() - INTERVAL '{hours} hours'
            """
            )

            # Throughput
            throughput_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) / {hours} as avg_transactions_per_hour,
                    COUNT(*) as total_processed
                FROM transactions 
                WHERE timestamp > extract(epoch from now() - interval '{hours} hours')
            """
            )

            # Error rates
            error_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
                    COUNT(*) as total_count
                FROM transaction_processing_log 
                WHERE received_at > NOW() - INTERVAL '{hours} hours'
            """
            )

            error_rate = (
                (error_stats["failed_count"] / error_stats["total_count"] * 100)
                if error_stats["total_count"] > 0
                else 0
            )

            # Memory and CPU usage (placeholders)
            resource_usage = {
                "cpu_usage_percent": 65.5,
                "memory_usage_percent": 78.2,
                "disk_usage_percent": 45.1,
                "network_io_mbps": 125.6,
            }

            return {
                "processing_performance": {
                    "avg_processing_time_ms": round(
                        float(processing_stats["avg_processing_ms"] or 0), 2
                    ),
                    "min_processing_time_ms": round(
                        float(processing_stats["min_processing_ms"] or 0), 2
                    ),
                    "max_processing_time_ms": round(
                        float(processing_stats["max_processing_ms"] or 0), 2
                    ),
                    "p95_processing_time_ms": round(
                        float(processing_stats["p95_processing_ms"] or 0), 2
                    ),
                },
                "throughput": {
                    "avg_transactions_per_hour": round(
                        float(throughput_stats["avg_transactions_per_hour"] or 0), 2
                    ),
                    "total_processed": throughput_stats["total_processed"] or 0,
                },
                "reliability": {
                    "error_rate_percent": round(error_rate, 2),
                    "failed_count": error_stats["failed_count"] or 0,
                    "success_count": (error_stats["total_count"] or 0)
                    - (error_stats["failed_count"] or 0),
                },
                "resource_usage": resource_usage,
                "analysis_period_hours": hours,
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve system performance: {str(e)}"
        )


@router.get("/reports/summary", response_model=AnalyticsReport)
async def generate_summary_report(
    hours: int = Query(24, ge=1, le=168),
    include_charts: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Generate a comprehensive analytics summary report.
    """
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        end_time = datetime.utcnow()

        async with db.acquire() as conn:
            # Core metrics
            metrics = {}

            # Transaction metrics
            tx_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) as total_transactions,
                    COUNT(DISTINCT chain_id) as chains_active,
                    AVG(gas_price::numeric) as avg_gas_price,
                    SUM(value::numeric) as total_value
                FROM transactions 
                WHERE timestamp > extract(epoch from now() - interval '{hours} hours')
            """
            )
            metrics["transactions"] = dict(tx_stats) if tx_stats else {}

            # Alert metrics
            alert_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) as total_alerts,
                    COUNT(*) FILTER (WHERE severity = 'critical') as critical_alerts,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending_alerts,
                    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60) as avg_response_time_min
                FROM alerts 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
            """
            )
            metrics["alerts"] = dict(alert_stats) if alert_stats else {}

            # MEV metrics
            mev_stats = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) as total_opportunities,
                    SUM(estimated_profit::numeric) as total_profit,
                    AVG(confidence_score) as avg_confidence
                FROM mev_opportunities 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
            """
            )
            metrics["mev"] = dict(mev_stats) if mev_stats else {}

            # Generate charts data
            charts = []
            if include_charts:
                # Transaction volume chart
                tx_chart_data = await conn.fetch(
                    f"""
                    SELECT 
                        date_trunc('hour', to_timestamp(timestamp)) as hour,
                        COUNT(*) as count
                    FROM transactions 
                    WHERE timestamp > extract(epoch from now() - interval '{hours} hours')
                    GROUP BY hour
                    ORDER BY hour
                """
                )

                charts.append(
                    {
                        "type": "line",
                        "title": "Transaction Volume Over Time",
                        "data": [
                            {"x": row["hour"].isoformat(), "y": row["count"]}
                            for row in tx_chart_data
                        ],
                    }
                )

                # Alert severity distribution
                severity_data = await conn.fetch(
                    f"""
                    SELECT severity, COUNT(*) as count
                    FROM alerts 
                    WHERE created_at > NOW() - INTERVAL '{hours} hours'
                    GROUP BY severity
                """
                )

                charts.append(
                    {
                        "type": "pie",
                        "title": "Alert Distribution by Severity",
                        "data": [
                            {"label": row["severity"], "value": row["count"]}
                            for row in severity_data
                        ],
                    }
                )

        report_id = f"summary_{int(datetime.utcnow().timestamp())}"

        return AnalyticsReport(
            report_id=report_id,
            title=f"System Analytics Summary ({hours}h)",
            description=f"Comprehensive analytics report covering {hours} hours of system activity",
            time_range={"start": start_time, "end": end_time},
            metrics=metrics,
            charts=charts,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate summary report: {str(e)}"
        )


@router.post("/query/custom")
async def execute_custom_query(
    query: CustomQuery,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Execute custom analytics queries (admin only).

    Allows execution of custom SQL queries for advanced analytics.
    Restricted to admin users for security.
    """
    try:
        # Check admin permissions
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403, detail="Admin access required for custom queries"
            )

        # Validate query (basic security check)
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
        query_upper = query.sql_query.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise HTTPException(
                    status_code=400,
                    detail=f"Query contains forbidden keyword: {keyword}",
                )

        async with db.acquire() as conn:
            # Execute the query with parameters
            if query.parameters:
                rows = await conn.fetch(query.sql_query, *query.parameters.values())
            else:
                rows = await conn.fetch(query.sql_query)

            # Convert to list of dicts
            results = [dict(row) for row in rows]

            return {
                "query_name": query.query_name,
                "description": query.description,
                "visualization_type": query.visualization_type,
                "row_count": len(results),
                "results": results,
                "executed_at": datetime.utcnow(),
                "executed_by": current_user["user_id"],
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute custom query: {str(e)}"
        )


@router.get("/export/data")
async def export_analytics_data(
    data_type: str = Query(..., description="transactions, alerts, mev_opportunities"),
    format: str = Query("json", description="json, csv"),
    hours: int = Query(24, ge=1, le=168),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Export analytics data in various formats.
    """
    try:
        # Validate data type
        valid_types = ["transactions", "alerts", "mev_opportunities"]
        if data_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Must be one of: {valid_types}",
            )

        # Validate format
        if format not in ["json", "csv"]:
            raise HTTPException(
                status_code=400, detail="Format must be 'json' or 'csv'"
            )

        # Build appropriate query
        queries = {
            "transactions": f"""
                SELECT * FROM transactions_view 
                WHERE timestamp > extract(epoch from now() - interval '{hours} hours')
                ORDER BY timestamp DESC
            """,
            "alerts": f"""
                SELECT * FROM alerts 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
                ORDER BY created_at DESC
            """,
            "mev_opportunities": f"""
                SELECT * FROM mev_opportunities 
                WHERE created_at > NOW() - INTERVAL '{hours} hours'
                ORDER BY created_at DESC
            """,
        }

        async with db.acquire() as conn:
            rows = await conn.fetch(queries[data_type])
            data = [dict(row) for row in rows]

        if format == "json":
            return {
                "data_type": data_type,
                "format": format,
                "record_count": len(data),
                "export_timestamp": datetime.utcnow(),
                "data": data,
            }
        else:  # CSV format
            # For CSV, we'd typically use FastAPI's StreamingResponse
            # This is a simplified version
            import csv
            import io

            if not data:
                return {"message": "No data to export"}

            # Create CSV content
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            csv_content = output.getvalue()

            return {
                "data_type": data_type,
                "format": format,
                "record_count": len(data),
                "export_timestamp": datetime.utcnow(),
                "csv_data": csv_content,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export analytics data: {str(e)}"
        )
