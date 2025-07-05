#!/usr/bin/env python3
"""
Unified Scorpius API Gateway
============================

A comprehensive API gateway that provides:
- Service discovery and registration via core orchestrator
- Authentication and authorization
- Health checks and monitoring
- Request routing and load balancing
- Rate limiting and circuit breakers
- WebSocket support for real-time communication
- Centralized logging and metrics
"""

# Standard library imports
import os
import asyncio
import json
import time
import uuid
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from pathlib import Path

# Environment validation - MUST be before other imports
required_env_vars = ["JWT_SECRET", "REDIS_URL"]
for var in required_env_vars:
    assert os.getenv(var), f"⚠️  {var} missing – see .env.example"

# Third-party imports
import redis.asyncio as redis
import httpx
from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect, HTTPException, 
    Depends, Response, Request
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog
import jwt

# Local imports
sys.path.append(str(Path(__file__).parent / "packages" / "core"))
from orchestrator_new import CoreOrchestrator, ServiceInfo, ServiceStatus

# Configure structured logging
logger = structlog.get_logger("api_gateway")

# Metrics
REQUEST_COUNT = Counter('gateway_requests_total', 'Total requests', ['method', 'service', 'status'])
REQUEST_DURATION = Histogram('gateway_request_duration_seconds', 'Request duration', ['service'])
ACTIVE_CONNECTIONS = Gauge('gateway_active_websockets', 'Active WebSocket connections')
SERVICE_CIRCUIT_BREAKER = Gauge('gateway_circuit_breaker_state', 'Circuit breaker state', ['service'])
RATE_LIMIT_HITS = Counter('gateway_rate_limit_hits_total', 'Rate limit hits', ['client_id'])

# Configuration
class GatewayConfig:
    """Gateway configuration."""
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")  # Load from env
        self.jwt_algorithm = "HS256"
        self.rate_limit_per_minute = 100
        self.circuit_breaker_failure_threshold = 5
        self.circuit_breaker_recovery_timeout = 60
        self.health_check_interval = 30
        self.websocket_heartbeat_interval = 30

config = GatewayConfig()

# Request/Response models
class ServiceRequest(BaseModel):
    """Service request model."""
    service: str = Field(..., description="Target service name")
    method: str = Field(default="GET", description="HTTP method")
    path: str = Field(..., description="Service endpoint path")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Request body")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional headers")
    timeout: Optional[float] = Field(default=30.0, description="Request timeout")

class ServiceResponse(BaseModel):
    """Service response model."""
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message")
    service: str = Field(..., description="Source service")
    duration_ms: float = Field(..., description="Request duration in milliseconds")
    status_code: int = Field(..., description="HTTP status code")

class GatewayHealth(BaseModel):
    """Gateway health status."""
    status: str = Field(..., description="Overall gateway status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Service status")
    metrics: Dict[str, Any] = Field(..., description="Gateway metrics")
    uptime: float = Field(..., description="Gateway uptime in seconds")

class AuthToken(BaseModel):
    """Authentication token model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

# Authentication and authorization
security = HTTPBearer()

class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm
        self.token_cache: Dict[str, Dict] = {}
    
    def create_token(self, user_data: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Create JWT token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = user_data.copy()
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

auth_manager = AuthManager(config.jwt_secret)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return auth_manager.verify_token(credentials.credentials)

# Rate limiting
class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(self, client_id: str, limit: int = 100, window: int = 60) -> bool:
        """Check if request is allowed under rate limit."""
        try:
            key = f"rate_limit:{client_id}"
            current = await self.redis.get(key)
            
            if current is None:
                await self.redis.setex(key, window, 1)
                return True
            
            current_count = int(current)
            if current_count >= limit:
                RATE_LIMIT_HITS.labels(client_id=client_id).inc()
                return False
            
            await self.redis.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Fail open

# WebSocket connection manager
class ConnectionManager:
    """Enhanced WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.service_subscriptions: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, 
                     user_data: Optional[Dict] = None, subscriptions: Optional[List[str]] = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_data": user_data or {},
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow()
        }
        
        # Handle service subscriptions
        if subscriptions:
            for service in subscriptions:
                if service not in self.service_subscriptions:
                    self.service_subscriptions[service] = set()
                self.service_subscriptions[service].add(connection_id)
        
        ACTIVE_CONNECTIONS.set(len(self.active_connections))
        logger.info(f"WebSocket connected: {connection_id}, Total: {len(self.active_connections)}")
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        
        # Remove from service subscriptions
        for service, connections in self.service_subscriptions.items():
            connections.discard(connection_id)
        
        ACTIVE_CONNECTIONS.set(len(self.active_connections))
        logger.info(f"WebSocket disconnected: {connection_id}, Total: {len(self.active_connections)}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                
                # Update heartbeat
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_heartbeat"] = datetime.utcnow()
                    
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_to_service(self, service: str, message: Dict[str, Any]):
        """Broadcast message to all connections subscribed to a service."""
        if service in self.service_subscriptions:
            connections = list(self.service_subscriptions[service])
            for connection_id in connections:
                await self.send_message(connection_id, message)
    
    async def broadcast_all(self, message: Dict[str, Any]):
        """Broadcast message to all connections."""
        connections = list(self.active_connections.keys())
        for connection_id in connections:
            await self.send_message(connection_id, message)
    
    async def cleanup_stale_connections(self):
        """Remove stale connections that haven't sent heartbeat."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        stale_connections = []
        
        for connection_id, metadata in self.connection_metadata.items():
            if metadata["last_heartbeat"] < cutoff_time:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            self.disconnect(connection_id)

# Circuit breaker for service calls
class ServiceCircuitBreaker:
    """Circuit breaker for service calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.circuit_state: Dict[str, str] = {}  # closed, open, half-open
    
    def is_available(self, service: str) -> bool:
        """Check if service is available (circuit not open)."""
        state = self.circuit_state.get(service, "closed")
        
        if state == "closed":
            return True
        elif state == "open":
            # Check if we should try half-open
            last_failure = self.last_failure_time.get(service)
            if last_failure and (datetime.utcnow() - last_failure).seconds >= self.recovery_timeout:
                self.circuit_state[service] = "half-open"
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self, service: str):
        """Record successful service call."""
        self.failure_count[service] = 0
        self.circuit_state[service] = "closed"
        SERVICE_CIRCUIT_BREAKER.labels(service=service).set(0)
    
    def record_failure(self, service: str):
        """Record failed service call."""
        self.failure_count[service] = self.failure_count.get(service, 0) + 1
        self.last_failure_time[service] = datetime.utcnow()
        
        if self.failure_count[service] >= self.failure_threshold:
            self.circuit_state[service] = "open"
            SERVICE_CIRCUIT_BREAKER.labels(service=service).set(1)
            logger.warning(f"Circuit breaker opened for service: {service}")

# Global instances
orchestrator = CoreOrchestrator()
connection_manager = ConnectionManager()
rate_limiter = None
circuit_breaker = ServiceCircuitBreaker(
    failure_threshold=config.circuit_breaker_failure_threshold,
    recovery_timeout=config.circuit_breaker_recovery_timeout
)

# Service proxy with circuit breaker
async def proxy_service_request(service_name: str, method: str, path: str,
                               data: Optional[Dict] = None, headers: Optional[Dict] = None,
                               timeout: float = 30.0) -> ServiceResponse:
    """Proxy request to service with circuit breaker protection."""
    start_time = time.time()
    
    # Check circuit breaker
    if not circuit_breaker.is_available(service_name):
        raise HTTPException(
            status_code=503, 
            detail=f"Service {service_name} is currently unavailable (circuit breaker open)"
        )
    
    # Get service info from orchestrator
    services = await orchestrator.get_all_services()
    if service_name not in services:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    service_info = services[service_name]
    if service_info.status != ServiceStatus.HEALTHY:
        raise HTTPException(status_code=503, detail=f"Service '{service_name}' is not healthy")
    
    # Build request URL
    url = f"{service_info.endpoint.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Prepare request
            request_headers = headers or {}
            request_headers.setdefault("Content-Type", "application/json")
            
            # Make request
            if method.upper() == "GET":
                response = await client.get(url, headers=request_headers, params=data)
            elif method.upper() == "POST":
                response = await client.post(url, headers=request_headers, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=request_headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=request_headers)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported method: {method}")
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            REQUEST_COUNT.labels(method=method, service=service_name, status=response.status_code).inc()
            REQUEST_DURATION.labels(service=service_name).observe(duration_ms / 1000)
            
            # Handle response
            success = 200 <= response.status_code < 300
            if success:
                circuit_breaker.record_success(service_name)
            else:
                circuit_breaker.record_failure(service_name)
            
            try:
                response_data = response.json()
            except Exception:
                response_data = response.text
            
            return ServiceResponse(
                success=success,
                data=response_data if success else None,
                error=None if success else f"Service returned {response.status_code}",
                service=service_name,
                duration_ms=duration_ms,
                status_code=response.status_code
            )
            
    except httpx.TimeoutException:
        circuit_breaker.record_failure(service_name)
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(method=method, service=service_name, status=408).inc()
        raise HTTPException(status_code=408, detail="Service request timeout")
    
    except Exception as e:
        circuit_breaker.record_failure(service_name)
        duration_ms = (time.time() - start_time) * 1000
        REQUEST_COUNT.labels(method=method, service=service_name, status=500).inc()
        logger.error(f"Service request error: {e}")
        raise HTTPException(status_code=500, detail=f"Service request failed: {str(e)}")

# Background tasks
async def health_monitor():
    """Background health monitoring."""
    while True:
        try:
            # Check orchestrator health
            orchestrator_health = await orchestrator.health_check()
            
            # Broadcast health updates via WebSocket
            await connection_manager.broadcast_all({
                "type": "health_update",
                "data": orchestrator_health,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await asyncio.sleep(config.health_check_interval)
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            await asyncio.sleep(10)

async def websocket_heartbeat():
    """WebSocket heartbeat and cleanup."""
    while True:
        try:
            await connection_manager.cleanup_stale_connections()
            
            # Send heartbeat to all connections
            await connection_manager.broadcast_all({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await asyncio.sleep(config.websocket_heartbeat_interval)
            
        except Exception as e:
            logger.error(f"WebSocket heartbeat error: {e}")
            await asyncio.sleep(10)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global rate_limiter
    
    logger.info("Starting Unified API Gateway")
    
    try:
        # Initialize Redis
        redis_client = redis.from_url(config.redis_url)
        await redis_client.ping()
        rate_limiter = RateLimiter(redis_client)
        logger.info("Connected to Redis")
        
        # Start orchestrator
        await orchestrator.start()
        logger.info("Core orchestrator started")
        
        # Start background tasks
        asyncio.create_task(health_monitor())
        asyncio.create_task(websocket_heartbeat())
        
        logger.info("Unified API Gateway startup complete")
        yield
        
    except Exception as e:
        logger.error(f"Gateway startup failed: {e}")
        raise
    finally:
        # Cleanup
        await orchestrator.stop()
        if rate_limiter and hasattr(rate_limiter, 'redis'):
            await rate_limiter.redis.close()
        logger.info("Unified API Gateway shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Scorpius Unified API Gateway",
    description="Unified gateway for the Scorpius enterprise platform with orchestration, auth, and monitoring",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
@app.get("/healthz")
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/readyz")
async def readiness_probe():
    """Kubernetes readiness probe endpoint."""
    try:
        orchestrator_health = await orchestrator.health_check()
        if orchestrator_health["status"] == "healthy":
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/health", response_model=GatewayHealth)
async def gateway_health():
    """Get comprehensive gateway health status."""
    orchestrator_health = await orchestrator.health_check()
    
    # Convert orchestrator services format to expected format
    services_dict = {}
    if orchestrator.services:
        for service_name, service in orchestrator.services.items():
            services_dict[service_name] = {
                "status": service.status.value if hasattr(service.status, 'value') else str(service.status),
                "last_heartbeat": service.last_heartbeat.isoformat() if service.last_heartbeat else None,
                "host": service.host,
                "port": service.port
            }
    
    return GatewayHealth(
        status="healthy" if orchestrator_health["status"] == "healthy" else "unhealthy",
        timestamp=datetime.utcnow(),
        services=services_dict,
        metrics={
            "active_websockets": len(connection_manager.active_connections),
            "uptime": orchestrator_health.get("uptime", 0),
            "total_services": orchestrator_health.get("services", {}).get("total", 0),
            "healthy_services": orchestrator_health.get("services", {}).get("healthy", 0)
        },
        uptime=orchestrator_health.get("uptime", 0)
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/auth/token", response_model=AuthToken)
async def create_access_token(user_id: str, permissions: List[str] = None):
    """Create authentication token (placeholder - implement proper auth)."""
    user_data = {
        "user_id": user_id,
        "permissions": permissions or ["read"]
    }
    
    token = auth_manager.create_token(user_data)
    
    return AuthToken(
        access_token=token,
        token_type="bearer",
        expires_in=86400  # 24 hours
    )

@app.post("/services/register")
async def register_service(service_info: ServiceInfo, current_user: Dict = Depends(get_current_user)):
    """Register a new service with the orchestrator."""
    await orchestrator.register_service(service_info)
    return {"message": f"Service {service_info.name} registered successfully"}

@app.get("/services")
async def list_services(current_user: Dict = Depends(get_current_user)):
    """List all registered services."""
    services = await orchestrator.get_all_services()
    return {
        "services": {name: {
            "name": info.name,
            "version": info.version,
            "status": info.status.value,
            "endpoint": info.endpoint,
            "capabilities": info.capabilities,
            "last_heartbeat": info.last_heartbeat.isoformat() if info.last_heartbeat else None
        } for name, info in services.items()}
    }

@app.post("/proxy", response_model=ServiceResponse)
async def proxy_request(request: ServiceRequest, current_user: Dict = Depends(get_current_user)):
    """Proxy request to a registered service."""
    # Check rate limit
    client_id = current_user.get("user_id", "anonymous")
    if rate_limiter and not await rate_limiter.is_allowed(client_id, config.rate_limit_per_minute):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return await proxy_service_request(
        service_name=request.service,
        method=request.method,
        path=request.path,
        data=request.data,
        headers=request.headers,
        timeout=request.timeout
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for real-time communication."""
    connection_id = str(uuid.uuid4())
    user_data = None
    
    # Authenticate WebSocket connection
    if token:
        try:
            user_data = auth_manager.verify_token(token)
        except HTTPException:
            await websocket.close(code=4001, reason="Invalid token")
            return
    
    await connection_manager.connect(websocket, connection_id, user_data)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "heartbeat":
                    await connection_manager.send_message(connection_id, {
                        "type": "heartbeat_ack",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message_type == "subscribe":
                    # Handle service subscription
                    service = message.get("service")
                    if service:
                        if service not in connection_manager.service_subscriptions:
                            connection_manager.service_subscriptions[service] = set()
                        connection_manager.service_subscriptions[service].add(connection_id)
                        
                        await connection_manager.send_message(connection_id, {
                            "type": "subscription_ack",
                            "service": service
                        })
                
            except json.JSONDecodeError:
                await connection_manager.send_message(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON message"
                })
                
    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(connection_id)

# Convenience API routes for easier frontend integration
@app.post("/api/wallet/check")
async def wallet_check(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Convenience endpoint for wallet security check."""
    # Proxy to wallet_guard service
    return await proxy_service_request(
        service_name="wallet_guard",
        method="POST",
        path="wallet/check",
        data=request,
        timeout=30.0
    )

@app.post("/api/wallet/revoke")
async def wallet_revoke(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Convenience endpoint for wallet approval revocation."""
    # Proxy to wallet_guard service
    return await proxy_service_request(
        service_name="wallet_guard",
        method="POST",
        path="wallet/revoke",
        data=request,
        timeout=30.0
    )

@app.post("/api/honeypot/check")
async def honeypot_check(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Convenience endpoint for honeypot detection."""
    return await proxy_service_request(
        service_name="honeypot",
        method="POST",
        path="check",
        data=request,
        timeout=15.0
    )

@app.get("/api/mempool/monitor")
async def mempool_monitor(
    current_user: Dict = Depends(get_current_user)
):
    """Convenience endpoint for mempool monitoring."""
    return await proxy_service_request(
        service_name="mempool",
        method="GET",
        path="monitor",
        timeout=10.0
    )

@app.post("/api/mempool/analyze")
async def mempool_analyze(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Convenience endpoint for mempool analysis."""
    return await proxy_service_request(
        service_name="mempool",
        method="POST",
        path="analyze",
        data=request,
        timeout=20.0
    )

# Service registration and heartbeat endpoints
@app.delete("/services/{service_name}")
async def unregister_service(
    service_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Unregister a service."""
    await orchestrator.unregister_service(service_name)
    return {"message": f"Service {service_name} unregistered successfully"}

@app.post("/services/{service_name}/heartbeat")
async def service_heartbeat(
    service_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Receive heartbeat from a service."""
    services = await orchestrator.get_all_services()
    if service_name in services:
        services[service_name].last_heartbeat = datetime.utcnow()
        services[service_name].status = ServiceStatus.HEALTHY
        return {"message": "Heartbeat received"}
    else:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

# Enhanced proxy endpoint with direct path routing
@app.api_route("/proxy/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def enhanced_proxy(
    service_name: str,
    path: str,
    request: Request,
    current_user: Dict = Depends(get_current_user)
):
    """Enhanced proxy endpoint that forwards requests to services."""
    # Check rate limit
    client_id = current_user.get("user_id", "anonymous")
    if rate_limiter and not await rate_limiter.is_allowed(client_id, config.rate_limit_per_minute):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get request body
    try:
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else None
    except:
        body = None
    
    # Get query parameters
    query_params = dict(request.query_params)
    
    return await proxy_service_request(
        service_name=service_name,
        method=request.method,
        path=path,
        data=body or query_params,
        headers=dict(request.headers),
        timeout=30.0
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
