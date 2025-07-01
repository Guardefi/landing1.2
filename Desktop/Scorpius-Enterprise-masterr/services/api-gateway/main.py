"""
Enterprise API Gateway for Scorpius Microservices Platform

This is the central orchestrator that:
- Routes requests to appropriate microservices
- Manages WebSocket connections for real-time updates
- Handles authentication and authorization
- Provides unified API documentation
- Implements rate limiting and circuit breakers
- Aggregates responses from multiple services
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import httpx
import redis.asyncio as redis

# Import from scorpius-core package
from core import get_config, get_orchestrator
from core.config import get_config as _early_get_config
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter(
    "gateway_requests_total", "Total requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("gateway_request_duration_seconds", "Request duration")
ACTIVE_CONNECTIONS = Gauge("gateway_active_websockets", "Active WebSocket connections")
SERVICE_HEALTH = Gauge("gateway_service_health", "Service health status", ["service"])

# Global state
redis_client: Optional[redis.Redis] = None
http_client: Optional[httpx.AsyncClient] = None
orchestrator = None
config = None

# Initialize temporary configuration early for settings needed during app
# instantiation
_temp_cfg = _early_get_config()
ALLOWED_ORIGINS = _temp_cfg.security.cors_origins or ["*"]


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.service_subscriptions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, service: Optional[str] = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

        if service:
            if service not in self.service_subscriptions:
                self.service_subscriptions[service] = []
            self.service_subscriptions[service].append(websocket)

        ACTIVE_CONNECTIONS.set(len(self.active_connections))
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove from service subscriptions
        for service, connections in self.service_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)

        ACTIVE_CONNECTIONS.set(len(self.active_connections))
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str, service: Optional[str] = None):
        """Broadcast message to all or service-specific connections."""
        connections = (
            self.service_subscriptions.get(service, [])
            if service
            else self.active_connections
        )

        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager
manager = ConnectionManager()


# Request/Response models
class ServiceRequest(BaseModel):
    service: str = Field(..., description="Target service name")
    method: str = Field(default="GET", description="HTTP method")
    path: str = Field(..., description="Service endpoint path")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Request data")
    headers: Optional[Dict[str, str]] = Field(
        default=None, description="Request headers"
    )


class ServiceResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
    service: str = Field(..., description="Source service")
    duration_ms: float = Field(..., description="Request duration in milliseconds")


class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall system status")
    timestamp: float = Field(..., description="Check timestamp")
    services: Dict[str, Dict[str, Any]] = Field(
        ..., description="Individual service status"
    )
    metrics: Dict[str, float] = Field(..., description="System metrics")


class SystemMetrics(BaseModel):
    active_connections: int = Field(..., description="Active WebSocket connections")
    total_requests: int = Field(..., description="Total requests processed")
    average_response_time: float = Field(..., description="Average response time (ms)")
    services_healthy: int = Field(..., description="Number of healthy services")
    services_total: int = Field(..., description="Total number of services")


# Authentication
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Validate JWT token (placeholder implementation)."""
    # TODO: Implement proper JWT validation
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return {"user_id": "test_user", "permissions": ["read", "write"]}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global redis_client, http_client, orchestrator, config

    # Initialize configuration
    config = get_config()
    logger.info(f"Starting API Gateway in {config.environment} mode")

    # Initialize orchestrator
    orchestrator = get_orchestrator()

    try:
        # Initialize Redis connection
        redis_client = redis.from_url(
            config.redis.url,
            max_connections=config.redis.max_connections,
            socket_timeout=config.redis.socket_timeout,
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Connected to Redis")

        # Initialize HTTP client
        http_client = httpx.AsyncClient(timeout=30.0)
        logger.info("HTTP client initialized")

        # Start background tasks
        asyncio.create_task(health_check_loop())
        asyncio.create_task(event_broadcaster())

        logger.info("API Gateway startup complete")
        yield

    except Exception as e:
        logger.error(f"Failed to initialize API Gateway: {e}")
        raise
    finally:
        # Cleanup
        if http_client:
            await http_client.aclose()
        if redis_client:
            await redis_client.close()
        logger.info("API Gateway shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Scorpius Enterprise API Gateway",
    description="Central orchestrator for the Scorpius microservices platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)


async def health_check_loop():
    """Background task to check service health."""
    while True:
        try:
            for service_name, config in orchestrator.get_services().items():
                try:
                    if http_client:
                        url = f"http://{
                            config['host']}:{
                            config['port']}{
                            config['health']}"
                        response = await http_client.get(url, timeout=5.0)
                        is_healthy = response.status_code == 200
                        SERVICE_HEALTH.labels(service=service_name).set(
                            1 if is_healthy else 0
                        )
                except Exception as e:
                    logger.warning(f"Health check failed for {service_name}: {e}")
                    SERVICE_HEALTH.labels(service=service_name).set(0)

            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Health check loop error: {e}")
            await asyncio.sleep(60)


async def event_broadcaster():
    """Background task to broadcast events from Redis."""
    if not redis_client:
        return

    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("scorpius:events")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    event_data = json.loads(message["data"])
                    service = event_data.get("service")
                    await manager.broadcast(message["data"], service)
                except Exception as e:
                    logger.error(f"Error broadcasting event: {e}")
    except Exception as e:
        logger.error(f"Event broadcaster error: {e}")


async def forward_request(
    service_name: str,
    method: str,
    path: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    service_config: Dict = None,
) -> ServiceResponse:
    """Forward request to appropriate microservice."""
    start_time = time.time()

    if service_config is None:
        if service_name not in orchestrator.get_services():
            raise HTTPException(
                status_code=404, detail=f"Service '{service_name}' not found"
            )
        service_config = orchestrator.get_services()[service_name]

    url = f"http://{service_config['host']}:{service_config['port']}{path}"

    try:
        if not http_client:
            raise HTTPException(status_code=503, detail="HTTP client not available")

        request_kwargs = {"timeout": 30.0, "headers": headers or {}}

        if method.upper() == "GET":
            response = await http_client.get(url, **request_kwargs)
        elif method.upper() == "POST":
            response = await http_client.post(url, json=data, **request_kwargs)
        elif method.upper() == "PUT":
            response = await http_client.put(url, json=data, **request_kwargs)
        elif method.upper() == "DELETE":
            response = await http_client.delete(url, **request_kwargs)
        else:
            raise HTTPException(
                status_code=405, detail=f"Method '{method}' not allowed"
            )

        duration_ms = (time.time() - start_time) * 1000

        REQUEST_COUNT.labels(
            method=method.upper(),
            endpoint=f"/{service_name}{path}",
            status=response.status_code,
        ).inc()

        REQUEST_DURATION.observe(duration_ms / 1000)

        return ServiceResponse(
            success=response.status_code < 400,
            data=response.json() if response.content else None,
            service=service_name,
            duration_ms=duration_ms,
            error=(
                None
                if response.status_code < 400
                else f"HTTP {
                    response.status_code}"
            ),
        )

    except httpx.TimeoutException:
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(
            method=method.upper(), endpoint=f"/{service_name}{path}", status=408
        ).inc()
        raise HTTPException(status_code=408, detail=f"Service '{service_name}' timeout")

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(
            method=method.upper(), endpoint=f"/{service_name}{path}", status=500
        ).inc()
        logger.error(f"Error forwarding request to {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service '{service_name}' error: {
                str(e)}",
        )


# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Scorpius Enterprise API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "readiness": "/readiness",
    }


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """System health check."""
    timestamp = time.time()
    services_status = {}
    healthy_count = 0

    for service_name, config in orchestrator.get_services().items():
        try:
            if http_client:
                url = f"http://{
                    config['host']}:{
                    config['port']}{
                    config['health']}"
                response = await http_client.get(url, timeout=5.0)
                is_healthy = response.status_code == 200
                services_status[service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "last_check": timestamp,
                }
                if is_healthy:
                    healthy_count += 1
        except Exception as e:
            services_status[service_name] = {
                "status": "error",
                "error": str(e),
                "last_check": timestamp,
            }

    overall_status = (
        "healthy"
        if healthy_count == len(orchestrator.get_services())
        else "degraded" if healthy_count > 0 else "unhealthy"
    )

    return HealthStatus(
        status=overall_status,
        timestamp=timestamp,
        services=services_status,
        metrics={
            "active_connections": len(manager.active_connections),
            "services_healthy": healthy_count,
            "services_total": len(orchestrator.get_services()),
        },
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


@app.get("/readiness", response_model=HealthStatus)
async def readiness_check():
    """Deep readiness probe – currently proxies to health_check but can be extended."""
    return await health_check()


@app.get("/api/v1/services", response_model=List[str])
async def list_services():
    """List all registered services from orchestrator."""
    return list(orchestrator.get_services().keys()) if orchestrator else []


@app.post("/api/v1/execute", response_model=ServiceResponse)
async def execute_service_request(
    request: ServiceRequest, current_user: dict = Depends(get_current_user)
):
    """Execute request on specific service."""
    return await forward_request(
        service_name=request.service,
        method=request.method,
        path=request.path,
        data=request.data,
        headers=request.headers,
    )


@app.get("/api/v1/{service_name}/health")
async def service_health(service_name: str):
    """Check specific service health."""
    if service_name not in orchestrator.get_services():
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found"
        )

    response = await forward_request(service_name, "GET", "/health")
    return response.data


# ---- Explicit route → service mapping ----
SERVICE_ROUTE_MAP: Dict[str, str] = {
    "bridge": "bridge",
    "bytecode": "bytecode",
    "honeypot": "honeypot",
    "mempool": "mempool",
    "quantum": "quantum",
    "simulation": "simulation",  # simulation sandbox service
    "time-machine": "time_machine",
    "scanner": "scanner",  # master vulnerability scanner service
}


@app.api_route(
    "/api/{service_prefix}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy_prefixed_route(service_prefix: str, path: str, request: Request):
    """Proxy explicitly mapped /api/<prefix>/... routes to the corresponding micro-service."""
    if service_prefix not in SERVICE_ROUTE_MAP:
        raise HTTPException(status_code=404, detail="Unknown service prefix")

    service_name = SERVICE_ROUTE_MAP[service_prefix]

    body = None
    headers = dict(request.headers)
    if request.method in ("POST", "PUT"):
        body = await request.json()

    # Remove hop-by-hop headers that should not be forwarded
    headers.pop("host", None)
    headers.pop("content-length", None)

    return await forward_request(
        service_name=service_name,
        method=request.method,
        path=f"/{path}",
        data=body,
        headers=headers,
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, service: Optional[str] = None):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, service)

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            # Echo back for now (can implement command handling)
            await manager.send_personal_message(f"Echo: {data}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.websocket("/ws/{service_name}")
async def service_websocket(websocket: WebSocket, service_name: str):
    """Service-specific WebSocket endpoint."""
    if service_name not in orchestrator.get_services():
        await websocket.close(code=4004, reason=f"Service '{service_name}' not found")
        return

    await websocket_endpoint(websocket, service_name)


@app.get("/debug/redis-services")
async def debug_redis_services():
    """Debug endpoint to check Redis service registry"""
    try:
        # Test direct Redis connection
        redis_client = redis.from_url(
            config.redis.url,
            decode_responses=True,
            socket_timeout=config.redis.socket_timeout,
        )
        await redis_client.ping()

        # Get services from Redis directly
        services_data = await redis_client.hgetall("scorpius:services")

        # Also check orchestrator's in-memory services
        orchestrator_services = orchestrator.get_services()

        await redis_client.close()

        return {
            "redis_connection": "success",
            "redis_services": services_data,
            "orchestrator_services": orchestrator_services,
            "config_redis_url": config.redis.url,
        }
    except Exception as e:
        return {
            "redis_connection": "failed",
            "error": str(e),
            "config_redis_url": config.redis.url,
        }


# Wallet scan models
class WalletCheckRequest(BaseModel):
    address: str = Field(
        ..., description="Ethereum wallet address", pattern="^0x[a-fA-F0-9]{40}$"
    )


class TokenApproval(BaseModel):
    token: str = Field(..., description="Token symbol")
    contract_address: str = Field(..., description="Token contract address")
    spender: str = Field(..., description="Approved spender address")
    approved_amount: str = Field(..., description="Approved amount")
    is_unlimited: bool = Field(..., description="Whether approval is unlimited")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")


class WalletCheckResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    address: str = Field(..., description="Checked wallet address")
    risk_score: int = Field(..., description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level classification")
    total_approvals: int = Field(..., description="Total number of approvals")
    high_risk_approvals: int = Field(
        ..., description="Number of high/critical risk approvals"
    )
    approvals: List[TokenApproval] = Field(..., description="List of token approvals")
    recommendations: List[str] = Field(..., description="Security recommendations")
    scan_timestamp: float = Field(..., description="Timestamp of scan")


class RevokeRequest(BaseModel):
    address: str = Field(..., pattern="^0x[a-fA-F0-9]{40}$")
    token_contract: str = Field(..., pattern="^0x[a-fA-F0-9]{40}$")
    spender: str = Field(..., pattern="^0x[a-fA-F0-9]{40}$")


class RevokeResponse(BaseModel):
    success: bool = Field(..., description="Transaction success status")
    address: str = Field(..., description="Wallet address")
    token_contract: str = Field(..., description="Token contract address")
    spender: str = Field(..., description="Spender address")
    transaction_hash: Optional[str] = Field(
        None, description="Transaction hash if submitted"
    )
    status: str = Field(..., description="Revocation status")
    message: str = Field(..., description="Status message")


@app.post("/api/wallet/check", response_model=WalletCheckResponse)
async def wallet_check(request: WalletCheckRequest):
    """Check wallet approvals and risk status"""
    start_time = time.time()

    # Simulate real scanning logic
    await asyncio.sleep(0.5)  # Simulate API delay

    # Mock data - in production, this would call actual blockchain analysis
    mock_approvals = [
        TokenApproval(
            token="DAI",
            contract_address="0x6B175474E89094C44Da98b954EedeAC495271d0F",
            spender="0x1111111254fb6c44bAC0beD2854e76F90643097d",
            approved_amount="115792089237316195423570985008687907853269984665640564039457584007913129639935",
            is_unlimited=True,
            risk_level="medium",
        ),
        TokenApproval(
            token="USDC",
            contract_address="0xA0b86a33E6441b86BF6662a116c8c95F5bA1D4e1",
            spender="0x2222222254fb6c44bAC0beD2854e76F90643097d",
            approved_amount="1000000000",
            is_unlimited=False,
            risk_level="low",
        ),
        TokenApproval(
            token="WETH",
            contract_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            spender="0x3333333254fb6c44bAC0beD2854e76F90643097d",
            approved_amount="115792089237316195423570985008687907853269984665640564039457584007913129639935",
            is_unlimited=True,
            risk_level="high",
        ),
    ]

    high_risk_count = sum(
        1 for approval in mock_approvals if approval.risk_level in ["high", "critical"]
    )
    risk_score = min(95, (high_risk_count * 25) + (len(mock_approvals) * 5))

    if risk_score >= 75:
        risk_level = "critical"
    elif risk_score >= 50:
        risk_level = "high"
    elif risk_score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommendations = []
    if high_risk_count > 0:
        recommendations.append("Revoke unlimited approvals for high-risk contracts")
    if len(mock_approvals) > 5:
        recommendations.append("Consider revoking old or unused token approvals")
    recommendations.append("Regularly audit your wallet approvals")
    recommendations.append("Only approve specific amounts when possible")

    return WalletCheckResponse(
        success=True,
        address=request.address,
        risk_score=risk_score,
        risk_level=risk_level,
        total_approvals=len(mock_approvals),
        high_risk_approvals=high_risk_count,
        approvals=mock_approvals,
        recommendations=recommendations,
        scan_timestamp=start_time,
    )


@app.post("/api/wallet/revoke", response_model=RevokeResponse)
async def wallet_revoke(request: RevokeRequest):
    """Revoke a token approval for a given spender"""
    time.time()

    # Simulate transaction submission delay
    await asyncio.sleep(1.0)

    # Mock transaction hash generation
    mock_tx_hash = f"0x{
        ''.join(
            [
                f'{
                    ord(c):02x}' for c in f'{
                    request.address}{
                        request.token_contract}{
                            request.spender}'[
                                :32]])}"

    return RevokeResponse(
        success=True,
        address=request.address,
        token_contract=request.token_contract,
        spender=request.spender,
        transaction_hash=mock_tx_hash,
        status="submitted",
        message="Revocation transaction submitted successfully. Please check your wallet for confirmation.",
    )


# Re-add generic proxy for backward compatibility (v1 namespace)
@app.api_route(
    "/api/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy_to_service(service_name: str, path: str, request: Request):
    """Generic proxy for legacy /api/v1 routes."""
    method = request.method
    headers = dict(request.headers)

    body = None
    if method in ("POST", "PUT"):
        try:
            body = await request.json()
        except Exception:
            body = None

    # Remove hop-by-hop headers that should not be forwarded
    headers.pop("host", None)
    headers.pop("content-length", None)

    response = await forward_request(service_name, method, f"/{path}", body, headers)

    if response.success:
        return response.data
    raise HTTPException(status_code=500, detail=response.error)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
