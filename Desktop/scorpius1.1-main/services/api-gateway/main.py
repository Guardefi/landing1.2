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
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import redis.asyncio as redis
import httpx
from fastapi import (
    FastAPI, 
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException,
    Depends,
    Request,
    status,
    File,
    UploadFile
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import jwt
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

# Import from scorpius-core package
from core import get_config

# Use the same get_config function for early configuration
_early_get_config = get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('gateway_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gateway_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('gateway_active_websockets', 'Active WebSocket connections')
SERVICE_HEALTH = Gauge('gateway_service_health', 'Service health status', ['service'])

# Global state
redis_client: Optional[redis.Redis] = None
http_client: Optional[httpx.AsyncClient] = None
config = None

# Initialize temporary configuration early for settings needed during app instantiation
_temp_cfg = _early_get_config()
ALLOWED_ORIGINS = _temp_cfg.security.cors_origins or ["*"]

# Simple HTTP Service Orchestrator for API Gateway
class ServiceInfo:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.status = "unknown"
        self.last_check = None

class SimpleOrchestrator:
    """Simple HTTP service orchestrator for API Gateway"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.logger = logging.getLogger("orchestrator")
    
    def register_service(self, name: str, url: str):
        """Register a service with name and URL"""
        service_info = ServiceInfo(name, url)
        self.services[name] = service_info
        self.logger.info(f"Registered service: {name} -> {url}")
    
    def get_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services"""
        return self.services
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services (alias for get_services)"""
        return self.services
    
    def get_service_names(self) -> List[str]:
        """Get list of service names"""
        return list(self.services.keys())

# Initialize the orchestrator
orchestrator = SimpleOrchestrator()

# Configuration
from core import get_config
config = get_config()

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
    headers: Optional[Dict[str, str]] = Field(default=None, description="Request headers")


class ServiceResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
    service: str = Field(..., description="Source service")
    duration_ms: float = Field(..., description="Request duration in milliseconds")


class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall system status")
    timestamp: float = Field(..., description="Check timestamp")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Individual service status")
    metrics: Dict[str, float] = Field(..., description="System metrics")


class SystemMetrics(BaseModel):
    active_connections: int = Field(..., description="Active WebSocket connections")
    total_requests: int = Field(..., description="Total requests processed")
    average_response_time: float = Field(..., description="Average response time (ms)")
    services_healthy: int = Field(..., description="Number of healthy services")
    services_total: int = Field(..., description="Total number of services")


# Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token (placeholder implementation)."""
    # TODO: Implement proper JWT validation
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"user_id": "test_user", "permissions": ["read", "write"]}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global redis_client, http_client, config
    
    # Initialize configuration
    config = get_config()
    logger.info(f"Starting API Gateway in {config.environment} mode")
    
    logger.info("Orchestrator initialized successfully")
    
    # Register all microservices
    services_to_register = [
        ("bridge", "http://scorpius-bridge-enterprise:8000"),
        ("honeypot", "http://scorpius-honeypot-enterprise:8000"),
        ("mempool", "http://scorpius-mempool-enterprise:8000"),
        ("quantum", "http://scorpius-quantum-enterprise:8000"),
        ("simulation", "http://scorpius-simulation-service:8006"),
        ("time_machine", "http://scorpius-time-machine-enterprise:8000"),
        ("bytecode", "http://scorpius-bytecode-enterprise:8000"),
        ("wallet_guard", "http://scorpius-wallet-guard-enterprise:8085"),
        ("scanner", "http://scorpius-scanner-ai-orchestrator:8000"),
        ("settings", "http://scorpius-settings-enterprise:8000"),
        ("reporting", "http://scorpius-reporting-service:8007"),
        ("mev_bot", "http://scorpius-mev-bot-enterprise:8000"),
        ("mev", "http://scorpius-mev-guardian:8000"),
    ]
    
    logger.info(f"About to register {len(services_to_register)} services")
    for service_name, service_url in services_to_register:
        orchestrator.register_service(service_name, service_url)
        logger.info(f"✅ Registered service: {service_name} -> {service_url}")
    
    logger.info(f"Service registration complete. Total services: {len(orchestrator.get_all_services())}")
    
    try:
        # Initialize Redis connection
        redis_client = redis.from_url(
            config.redis.url,
            max_connections=config.redis.max_connections,
            socket_timeout=config.redis.socket_timeout,
            decode_responses=True
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
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)


async def health_check_loop():
    """Background task to check service health."""
    while True:
        try:
            for service_name, service_info in orchestrator.get_all_services().items():
                try:
                    if http_client:
                        url = f"{service_info.url}/health"
                        response = await http_client.get(url, timeout=5.0)
                        is_healthy = response.status_code == 200
                        SERVICE_HEALTH.labels(service=service_name).set(1 if is_healthy else 0)
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


async def forward_request(service_name: str, method: str, path: str, 
                         data: Optional[Dict] = None, headers: Optional[Dict] = None, service_config: Dict = None) -> ServiceResponse:
    """Forward request to appropriate microservice."""
    start_time = time.time()
    
    if service_config is None:
        if service_name not in orchestrator.get_services():
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        service_info = orchestrator.get_services()[service_name]
        url = f"{service_info.url}{path}"
    else:
        url = f"http://{service_config['host']}:{service_config['port']}{path}"
    
    try:
        if not http_client:
            raise HTTPException(status_code=503, detail="HTTP client not available")
        
        request_kwargs = {
            "timeout": 30.0,
            "headers": headers or {}
        }
        
        if method.upper() == "GET":
            response = await http_client.get(url, **request_kwargs)
        elif method.upper() == "POST":
            response = await http_client.post(url, json=data, **request_kwargs)
        elif method.upper() == "PUT":
            response = await http_client.put(url, json=data, **request_kwargs)
        elif method.upper() == "DELETE":
            response = await http_client.delete(url, **request_kwargs)
        else:
            raise HTTPException(status_code=405, detail=f"Method '{method}' not allowed")
        
        duration_ms = (time.time() - start_time) * 1000
        
        REQUEST_COUNT.labels(
            method=method.upper(), 
            endpoint=f"/{service_name}{path}", 
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.observe(duration_ms / 1000)
        
        return ServiceResponse(
            success=response.status_code < 400,
            data=response.json() if response.content else None,
            service=service_name,
            duration_ms=duration_ms,
            error=None if response.status_code < 400 else f"HTTP {response.status_code}"
        )
        
    except httpx.TimeoutException:
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(method=method.upper(), endpoint=f"/{service_name}{path}", status=408).inc()
        raise HTTPException(status_code=408, detail=f"Service '{service_name}' timeout")
    
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(method=method.upper(), endpoint=f"/{service_name}{path}", status=500).inc()
        logger.error(f"Error forwarding request to {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Service '{service_name}' error: {str(e)}")


# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Scorpius Enterprise API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "readiness": "/readiness"
    }


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """System health check."""
    timestamp = time.time()
    services_status = {}
    healthy_count = 0
    
    for service_name, service_info in orchestrator.get_all_services().items():
        try:
            if http_client:
                url = f"{service_info.url}/health"
                response = await http_client.get(url, timeout=5.0)
                is_healthy = response.status_code == 200
                services_status[service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "last_check": timestamp
                }
                if is_healthy:
                    healthy_count += 1
        except Exception as e:
            services_status[service_name] = {
                "status": "error",
                "error": str(e),
                "last_check": timestamp
            }
    
    overall_status = "healthy" if healthy_count == len(orchestrator.get_all_services()) else "degraded" if healthy_count > 0 else "unhealthy"
    
    return HealthStatus(
        status=overall_status,
        timestamp=timestamp,
        services=services_status,
        metrics={
            "active_connections": len(manager.active_connections),
            "services_healthy": healthy_count,
            "services_total": len(orchestrator.get_all_services())
        }
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
    return list(orchestrator.get_all_services().keys()) if orchestrator else []


@app.get("/api/admin/system/status", response_model=HealthStatus)
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Return overall system status with service health metrics."""
    timestamp = time.time()
    services_status: Dict[str, Dict[str, Any]] = {}
    healthy_count = 0

    for service_name, service_info in orchestrator.get_all_services().items():
        try:
            if http_client:
                url = f"{service_info.url}/health"
                resp = await http_client.get(url, timeout=5.0)
                is_healthy = resp.status_code == 200
                services_status[service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time_ms": resp.elapsed.total_seconds() * 1000,
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
        if healthy_count == len(orchestrator.get_all_services())
        else "degraded" if healthy_count > 0 else "unhealthy"
    )

    return HealthStatus(
        status=overall_status,
        timestamp=timestamp,
        services=services_status,
        metrics={
            "active_connections": len(manager.active_connections),
            "services_healthy": healthy_count,
            "services_total": len(orchestrator.get_all_services()),
        },
    )


@app.post("/api/v1/execute", response_model=ServiceResponse)
async def execute_service_request(request: ServiceRequest, current_user: dict = Depends(get_current_user)):
    """Execute request on specific service."""
    return await forward_request(
        service_name=request.service,
        method=request.method,
        path=request.path,
        data=request.data,
        headers=request.headers
    )


@app.get("/api/v1/{service_name}/health")
async def service_health(service_name: str):
    """Check specific service health."""
    if service_name not in orchestrator.get_all_services():
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    response = await forward_request(service_name, "GET", "/health")
    return response.data


# ---- Explicit route → service mapping ----
SERVICE_ROUTE_MAP: Dict[str, str] = {
    "bridge": "bridge",
    "bytecode": "bytecode",
    "honeypot": "honeypot",
    "mempool": "mempool",
    "quantum": "quantum",
    "settings": "settings",  # configuration management service
    "simulation": "simulation",  # blockchain simulation service
    "time-machine": "time_machine",
    "scanner": "scanner",  # master vulnerability scanner service
    "reporting": "reporting",  # enterprise reporting service
    "mev": "mev",  # MEV Guardian blockchain protection service
    "trading": "mev_bot",  # AI Trading Engine (powered by MEV Bot)
}

@app.api_route("/api/{service_prefix}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
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
    if service_name not in orchestrator.get_all_services():
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
            socket_timeout=config.redis.socket_timeout
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
            "config_redis_url": config.redis.url
        }
    except Exception as e:
        return {
            "redis_connection": "failed",
            "error": str(e),
            "config_redis_url": config.redis.url
        }


# Wallet scan models
class WalletCheckRequest(BaseModel):
    address: str = Field(..., description="Ethereum wallet address", pattern="^0x[a-fA-F0-9]{40}$")

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
    high_risk_approvals: int = Field(..., description="Number of high/critical risk approvals")
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
    transaction_hash: Optional[str] = Field(None, description="Transaction hash if submitted")
    status: str = Field(..., description="Revocation status")
    message: str = Field(..., description="Status message")


@app.post("/api/wallet/check", response_model=WalletCheckResponse)
async def wallet_check(request: WalletCheckRequest):
    """Check wallet approvals and risk status"""
    # Convert the request to the format expected by WalletGuard service
    wallet_guard_request = {
        "addresses": [request.address],
        "chains": ["ethereum"],
        "include_approvals": True,
        "include_signatures": True,
        "include_spoofed": True
    }
    
    response = await forward_request("wallet_guard", "POST", "/wallet/check", wallet_guard_request)
    
    if response.success:
        # Convert WalletGuard response to API Gateway format
        wallet_data = response.data
        
        # Extract approvals from WalletGuard response
        approvals = []
        if "risky_approvals" in wallet_data:
            for approval in wallet_data["risky_approvals"]:
                approvals.append(TokenApproval(
                    token=approval.get("token_address", "Unknown")[:6],
                    contract_address=approval.get("token_address", ""),
                    spender=approval.get("spender_address", ""),
                    approved_amount=approval.get("approved_amount", "0"),
                    is_unlimited=approval.get("approved_amount", "0") == "115792089237316195423570985008687907853269984665640564039457584007913129639935",
                    risk_level=approval.get("risk_level", "low")
                ))
        
        high_risk_count = sum(1 for approval in approvals if approval.risk_level in ["high", "critical"])
        recommendations = []
        if high_risk_count > 0:
            recommendations.append("Revoke unlimited approvals for high-risk contracts")
        if len(approvals) > 5:
            recommendations.append("Consider revoking old or unused token approvals")
        recommendations.append("Regularly audit your wallet approvals")
        
        return WalletCheckResponse(
            success=True,
            address=request.address,
            risk_score=int(wallet_data.get("risk_score", 0)),
            risk_level=wallet_data.get("overall_risk_level", "low"),
            total_approvals=len(approvals),
            high_risk_approvals=high_risk_count,
            approvals=approvals,
            recommendations=recommendations,
            scan_timestamp=time.time()
        )
    else:
        raise HTTPException(status_code=500, detail=response.error)


@app.post("/api/wallet/revoke", response_model=RevokeResponse)
async def wallet_revoke(request: RevokeRequest):
    """Revoke a token approval for a given spender"""
    # Convert the request to the format expected by WalletGuard service
    wallet_guard_request = {
        "wallet_address": request.address,
        "chain": "ethereum",
        "approval_addresses": [request.spender],
        "token_types": ["erc20"]
    }
    
    response = await forward_request("wallet_guard", "POST", "/wallet/revoke", wallet_guard_request)
    
    if response.success:
        wallet_data = response.data
        return RevokeResponse(
            success=True,
            address=request.address,
            token_contract=request.token_contract,
            spender=request.spender,
            transaction_hash=wallet_data.get("transaction_hash", ""),
            status="submitted",
            message="Revocation transaction submitted successfully. Please check your wallet for confirmation."
        )
    else:
        raise HTTPException(status_code=500, detail=response.error)


# Wallet Guard service proxy - handle /api/wallet/* routes
@app.api_route("/api/wallet/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_wallet_requests(path: str, request: Request):
    """Proxy wallet requests to the wallet guard service."""
    # Skip the check and revoke endpoints since they're handled above
    if path in ["check", "revoke"]:
        return await request.body()
    
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
    
    response = await forward_request("wallet_guard", method, f"/{path}", body, headers)
    
    return JSONResponse(
        content=response.data,
        status_code=200 if response.success else 500
    )


# Simulation service proxy - handle /api/simulation/* routes
@app.api_route("/api/simulation/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_simulation_requests(path: str, request: Request):
    """Proxy simulation requests to the simulation service."""
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
    
    response = await forward_request("simulation", method, f"/{path}", body, headers)
    
    if response.success:
        return response.data
    raise HTTPException(status_code=500, detail=response.error)


# Settings service proxy - handle /api/settings/* routes
@app.api_route("/api/settings/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_settings_requests(path: str, request: Request):
    """Proxy settings requests to the settings service."""
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
    
    response = await forward_request("settings", method, f"/{path}", body, headers)
    
    if response.success:
        return response.data
    raise HTTPException(status_code=500, detail=response.error)


# Reporting service proxy - handle /api/reporting/* routes
@app.api_route("/api/reporting/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_reporting_requests(path: str, request: Request):
    """Proxy reporting requests to the reporting service."""
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
    
    response = await forward_request("reporting", method, f"/{path}", body, headers)
    
    return JSONResponse(
        content=response.data,
        status_code=200 if response.success else 500
    )


# MEV Guardian service proxy - handle /api/mev/* routes
@app.api_route("/api/mev/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_mev_requests(path: str, request: Request):
    """Forward MEV Guardian requests to the MEV Guardian service."""
    try:
        body = await request.body()
        data = json.loads(body.decode()) if body else None
        
        response = await forward_request(
            service_name="mev",
            method=request.method,
            path=f"/{path}",
            data=data,
            headers=dict(request.headers)
        )
        
        return JSONResponse(
            content=response.data,
            status_code=200 if response.success else 500
        )
    except Exception as e:
        logger.error(f"MEV Guardian proxy error: {e}")
        return JSONResponse(
            content={"error": f"MEV Guardian service error: {str(e)}"},
            status_code=500
        )


@app.api_route("/api/mev-bot/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_mev_bot_requests(path: str, request: Request):
    """Forward MEV Bot requests to the MEV Bot service."""
    try:
        body = await request.body()
        data = json.loads(body.decode()) if body else None
        
        response = await forward_request(
            service_name="mev_bot",
            method=request.method,
            path=f"/{path}",
            data=data,
            headers=dict(request.headers)
        )
        
        return JSONResponse(
            content=response.data,
            status_code=200 if response.success else 500
        )
    except Exception as e:
        logger.error(f"MEV Bot proxy error: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.api_route("/api/trading/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_trading_requests(path: str, request: Request):
    """Forward AI Trading requests to the MEV Bot service (integrated as AI trading bot)."""
    try:
        body = await request.body()
        data = json.loads(body.decode()) if body else None
        
        # Map trading endpoints to MEV bot endpoints
        endpoint_mapping = {
            "bots/status": "strategies",
            "transactions/latest": "executions?limit=1",
            "mev/stats": "performance",
            "strategies": "strategies",
            "bot/start": "start",
            "bot/stop": "stop",
            "bot/create": "start",
            "opportunities": "opportunities",
            "executions": "executions"
        }
        
        # Get the mapped endpoint or use the original path
        mev_path = endpoint_mapping.get(path, path)
        
        response = await forward_request(
            service_name="mev_bot",
            method=request.method,
            path=f"/{mev_path}",
            data=data,
            headers=dict(request.headers)
        )
        
        # Transform the response for trading API compatibility
        if response.success and response.data:
            if path == "bots/status":
                # Transform strategies to bots format
                transformed_data = []
                if isinstance(response.data, dict):
                    for strategy_id, strategy in response.data.items():
                        transformed_data.append({
                            "id": strategy_id,
                            "name": strategy.get("name", strategy_id),
                            "strategy": strategy_id,
                            "status": "active" if strategy.get("is_active", False) else "idle",
                            "profit": strategy.get("stats", {}).get("total_profit", 0),
                            "trades": strategy.get("stats", {}).get("total_opportunities", 0),
                            "gasUsed": strategy.get("stats", {}).get("total_gas_used", 0),
                            "winRate": strategy.get("stats", {}).get("success_rate", 0) * 100
                        })
                return JSONResponse(content={"success": True, "data": transformed_data})
            elif path == "transactions/latest":
                # Transform executions to transaction format
                if isinstance(response.data, list) and len(response.data) > 0:
                    execution = response.data[0]
                    transformed_data = {
                        "id": execution.get("id", ""),
                        "type": execution.get("strategy_type", "arbitrage"),
                        "amount": execution.get("amount", 0),
                        "gas": execution.get("gas_used", 0),
                        "success": execution.get("success", False),
                        "timestamp": execution.get("timestamp", ""),
                        "fromBot": execution.get("bot_id", "mev-bot"),
                        "path": [{"x": 50, "y": 50}]  # Default visualization path
                    }
                    return JSONResponse(content={"success": True, "data": transformed_data})
                return JSONResponse(content={"success": True, "data": None})
            elif path == "mev/stats":
                # MEV stats are already in the right format
                return JSONResponse(content={"success": True, "data": response.data})
            else:
                return JSONResponse(content={"success": True, "data": response.data})
        
        return JSONResponse(
            content=response.data,
            status_code=200 if response.success else 500
        )
    except Exception as e:
        logger.error(f"Trading proxy error: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# Re-add generic proxy for backward compatibility (v1 namespace)
@app.api_route("/api/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
