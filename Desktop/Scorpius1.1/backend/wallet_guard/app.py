"""
Wallet Guard Service Main Application
FastAPI service for wallet protection and security analysis
"""

import os
import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from core.auth import Organization, get_current_org
from core.config import settings
from core.monitoring import metrics
from core.rate_limiter import limiter
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from models import (
    HealthResponse,
    RevokeRequest,
    RevokeResponse,
    WalletCheckRequest,
    WalletCheckResponse,
)
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from services.chain_adapters import ChainAdapterFactory
from services.wallet_analyzer import WalletAnalyzer

# Add the packages/core directory to the Python path for service registration
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "packages", "core")
)

from service_registration import register_wallet_guard

# Prometheus metrics
WALLET_CHECK_COUNTER = Counter(
    "wallet_guard_checks_total", "Total wallet checks", ["chain", "status"]
)
WALLET_CHECK_DURATION = Histogram(
    "wallet_guard_check_duration_seconds", "Wallet check duration"
)
REVOKE_COUNTER = Counter(
    "wallet_guard_revokes_total", "Total revoke requests", ["chain"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await ChainAdapterFactory.initialize()

    # Register service with the orchestrator
    try:
        from .service_registration import register_wallet_guard

        await register_wallet_guard()
    except Exception as e:
        print(f"Failed to register service: {e}")

    yield
    # Shutdown
    await ChainAdapterFactory.cleanup()


app = FastAPI(
    title="Scorpius Wallet Guard",
    description="Enterprise wallet protection and security analysis service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0", timestamp=time.time())


@app.post("/wallet/check", response_model=WalletCheckResponse)
@limiter.limit("60/minute")
async def check_wallet(
    request: WalletCheckRequest,
    background_tasks: BackgroundTasks,
    org: Organization = Depends(get_current_org),
):
    """
    Check wallet for risky approvals, drainer signatures, and spoofed approvals

    Supports batch analysis across multiple chains with 95th percentile
    latency ≤ 1.8s for ≤ 25 addresses
    """
    start_time = time.time()

    try:
        # Validate request limits
        if len(request.addresses) > 25:
            raise HTTPException(
                status_code=400, detail="Maximum 25 addresses allowed per request"
            )

        # Initialize wallet analyzer
        analyzer = WalletAnalyzer(org_id=org.id)

        # Perform wallet analysis
        result = await analyzer.analyze_wallets(
            addresses=request.addresses,
            chains=request.chains,
            include_approvals=request.include_approvals,
            include_signatures=request.include_signatures,
            include_spoofed=request.include_spoofed,
        )

        # Record metrics
        duration = time.time() - start_time
        WALLET_CHECK_DURATION.observe(duration)

        for chain in request.chains:
            WALLET_CHECK_COUNTER.labels(chain=chain, status="success").inc()

        # Background audit logging
        background_tasks.add_task(
            metrics.log_wallet_check,
            org_id=org.id,
            addresses=request.addresses,
            chains=request.chains,
            result_hash=result.result_hash,
        )

        return result

    except Exception as e:
        # Record error metrics
        for chain in request.chains:
            WALLET_CHECK_COUNTER.labels(chain=chain, status="error").inc()

        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wallet/revoke", response_model=RevokeResponse)
@limiter.limit("30/minute")
async def revoke_approvals(
    request: RevokeRequest,
    background_tasks: BackgroundTasks,
    org: Organization = Depends(get_current_org),
):
    """
    Generate signed revoke transaction JSON for unsafe approvals

    Uses batch multicall for ERC-20/721/1155 across supported chains.
    Does not broadcast transactions - returns signed JSON for user execution.
    """
    try:
        # Initialize wallet analyzer
        analyzer = WalletAnalyzer(org_id=org.id)

        # Generate revoke transactions
        result = await analyzer.generate_revoke_transactions(
            wallet_address=request.wallet_address,
            chain=request.chain,
            approval_addresses=request.approval_addresses,
            token_types=request.token_types,
        )

        # Record metrics
        REVOKE_COUNTER.labels(chain=request.chain).inc()

        # Background audit logging
        background_tasks.add_task(
            metrics.log_revoke_request,
            org_id=org.id,
            wallet_address=request.wallet_address,
            chain=request.chain,
            tx_hash=result.transaction_hash,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
    )
