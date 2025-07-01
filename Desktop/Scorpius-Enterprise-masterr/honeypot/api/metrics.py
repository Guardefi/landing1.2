"""
Metrics collection for Prometheus monitoring
"""
import time
from functools import wraps
from typing import Callable

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram, Summary

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests count", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        30.0,
        float("inf"),
    ),
)

ANALYSIS_COUNT = Counter(
    "analysis_count_total", "Total contract analyses performed", ["chain_id", "status"]
)

ANALYSIS_LATENCY = Histogram(
    "analysis_duration_seconds",
    "Contract analysis duration in seconds",
    ["chain_id", "deep_analysis"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, float("inf")),
)

HONEYPOT_DETECTED = Counter(
    "honeypot_detected_total",
    "Number of honeypots detected",
    ["chain_id", "risk_level"],
)

CONTRACT_SOURCE_AVAILABLE = Counter(
    "contract_source_available_total",
    "Number of contracts with source code available",
    ["chain_id", "available"],
)

SYSTEM_INFO = Gauge("system_info", "System information", ["component"])

# DB connection status
DB_CONNECTION_STATUS = Gauge(
    "db_connection_status",
    "Database connection status (1=connected, 0=disconnected)",
    ["database"],
)

# RPC connection status
RPC_CONNECTION_STATUS = Gauge(
    "rpc_connection_status",
    "RPC endpoint connection status (1=connected, 0=disconnected)",
    ["chain_id"],
)

# Analysis engines status
ENGINE_STATUS = Gauge(
    "engine_status", "Analysis engine status (1=running, 0=stopped)", ["engine"]
)

# Analysis queue size
ANALYSIS_QUEUE_SIZE = Gauge(
    "analysis_queue_size", "Number of analyses waiting in queue"
)

# Active workers
ACTIVE_WORKERS = Gauge("active_workers", "Number of active worker processes")

# Rate limiter metrics
RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total", "Number of rate limit hits", ["client_id"]
)

# API key usage
API_KEY_USAGE = Counter(
    "api_key_usage_total", "Number of API key usages", ["api_key_id"]
)


def track_request_metrics() -> Callable:
    """
    Middleware for tracking HTTP request metrics

    Returns:
        Middleware function
    """

    async def middleware(request: Request, call_next):
        start_time = time.time()

        # Default status code if there's an exception
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            # Record request duration
            duration = time.time() - start_time
            endpoint = request.url.path

            # Skip metrics endpoint to avoid recursion
            if endpoint != "/metrics":
                REQUEST_COUNT.labels(
                    method=request.method, endpoint=endpoint, status=status_code
                ).inc()

                REQUEST_LATENCY.labels(
                    method=request.method, endpoint=endpoint
                ).observe(duration)

    return middleware


def track_analysis_metrics(func):
    """
    Decorator for tracking contract analysis metrics
    """

    @wraps(func)
    async def wrapper(contract_address, chain_id, deep_analysis=False, *args, **kwargs):
        start_time = time.time()
        status = "success"

        try:
            result = await func(
                contract_address, chain_id, deep_analysis, *args, **kwargs
            )

            # Track risk level detection
            if "risk_level" in result:
                HONEYPOT_DETECTED.labels(
                    chain_id=chain_id, risk_level=result["risk_level"]
                ).inc()

            # Track source code availability
            if "source_available" in result:
                CONTRACT_SOURCE_AVAILABLE.labels(
                    chain_id=chain_id,
                    available="yes" if result["source_available"] else "no",
                ).inc()

            return result

        except Exception as e:
            status = "error"
            raise

        finally:
            # Record analysis duration and count
            duration = time.time() - start_time

            ANALYSIS_COUNT.labels(chain_id=chain_id, status=status).inc()

            ANALYSIS_LATENCY.labels(
                chain_id=chain_id, deep_analysis=str(deep_analysis).lower()
            ).observe(duration)

    return wrapper


def update_system_metrics(component_status):
    """
    Update system metrics based on component status

    Args:
        component_status: Dictionary of component statuses
    """
    # Update DB connection status
    for db_name, status in component_status.get("databases", {}).items():
        DB_CONNECTION_STATUS.labels(database=db_name).set(1 if status else 0)

    # Update RPC connection status
    for chain_id, status in component_status.get("rpc_endpoints", {}).items():
        RPC_CONNECTION_STATUS.labels(chain_id=chain_id).set(1 if status else 0)

    # Update engine status
    for engine_name, status in component_status.get("engines", {}).items():
        ENGINE_STATUS.labels(engine=engine_name).set(1 if status else 0)

    # Update queue size
    if "queue_size" in component_status:
        ANALYSIS_QUEUE_SIZE.set(component_status["queue_size"])

    # Update active workers
    if "active_workers" in component_status:
        ACTIVE_WORKERS.set(component_status["active_workers"])
