"""
Bridge Service - Cross-chain Bridge Operations Microservice

This service handles:
- Cross-chain bridge transactions
- Multi-chain interoperability
- Bridge security monitoring
- Liquidity pool management
- Atomic swaps

NOTE: This service is now fully integrated with the shared scorpius-core package for configuration, orchestrator, and types.
"""

# --- Core Imports ---
from core import get_config, get_orchestrator
from core.types import ServiceInfo
from core.exceptions import ServiceError, ConfigError

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
BRIDGE_TRANSACTIONS = Counter('bridge_transactions_total', 'Total bridge transactions', ['chain_from', 'chain_to', 'status'])
TRANSACTION_DURATION = Histogram('bridge_transaction_duration_seconds', 'Transaction processing time')
LIQUIDITY_POOL_SIZE = Gauge('bridge_liquidity_pool_size', 'Liquidity pool size', ['token', 'chain'])
ACTIVE_BRIDGES = Gauge('bridge_active_bridges', 'Number of active bridges')

# Global state
redis_client: Optional[redis.Redis] = None
config = None
orchestrator = None

# Models
class BridgeTransaction(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    from_chain: str = Field(..., description="Source blockchain")
    to_chain: str = Field(..., description="Destination blockchain")
    token_address: str = Field(..., description="Token contract address")
    amount: str = Field(..., description="Amount to bridge")
    recipient: str = Field(..., description="Recipient address")
    fee: Optional[str] = Field(default=None, description="Bridge fee")
    deadline: Optional[int] = Field(default=None, description="Transaction deadline")


class BridgeStatus(BaseModel):
    transaction_id: str
    status: str = Field(..., description="Transaction status")
    from_chain: str
    to_chain: str
    amount: str
    created_at: datetime
    updated_at: datetime
    confirmations: int = Field(default=0, description="Number of confirmations")
    estimated_completion: Optional[datetime] = Field(default=None)


class LiquidityPool(BaseModel):
    pool_id: str = Field(..., description="Pool identifier")
    token_symbol: str = Field(..., description="Token symbol")
    chain: str = Field(..., description="Blockchain network")
    total_liquidity: str = Field(..., description="Total liquidity in pool")
    available_liquidity: str = Field(..., description="Available liquidity")
    utilization_rate: float = Field(..., description="Pool utilization rate")
    apy: float = Field(..., description="Annual percentage yield")


class ChainStatus(BaseModel):
    chain_name: str = Field(..., description="Blockchain name")
    is_active: bool = Field(..., description="Chain operational status")
    block_height: int = Field(..., description="Current block height")
    avg_block_time: float = Field(..., description="Average block time in seconds")
    gas_price: str = Field(..., description="Current gas price")
    congestion_level: str = Field(..., description="Network congestion level")


# Create FastAPI app
app = FastAPI(
    title="Bridge Service",
    description="Cross-chain bridge operations microservice",
    version="1.0.0",
    docs_url="/docs"
)


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global redis_client, config, orchestrator
    
    logger.info("🌉 Starting Bridge Service...")
    
    # Load configuration from scorpius-core
    config = get_config()
    logger.info(f"Loaded config for environment: {config.environment}")

    # Initialize orchestrator from scorpius-core
    orchestrator = get_orchestrator()
    
    # Register this service with the orchestrator
    orchestrator.register_service(
        name="bridge",
        module_path="services.bridge-service.main",
        entry_point="app",
        dependencies=["postgresql", "redis"],
        metadata={
            "host": "localhost",
            "port": 8001,
            "health_endpoint": "/health"
        }
    )
    logger.info("Registered with orchestrator")

    # Initialize Redis connection
    try:
        redis_client = redis.from_url(config.redis.url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
    
    # Initialize bridge monitoring
    asyncio.create_task(monitor_bridge_status())
    
    logger.info("🎯 Bridge Service ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down Bridge Service...")
    
    if redis_client:
        await redis_client.close()


async def monitor_bridge_status():
    """Background task to monitor bridge status."""
    while True:
        try:
            # Simulate bridge monitoring
            await update_bridge_metrics()
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Bridge monitoring error: {e}")
            await asyncio.sleep(60)


async def update_bridge_metrics():
    """Update bridge-related metrics."""
    try:
        # Simulate metrics updates
        ACTIVE_BRIDGES.set(5)  # Example: 5 active bridges
        
        # Update liquidity pool metrics
        pools = [
            {"token": "ETH", "chain": "ethereum", "size": 1000000},
            {"token": "BTC", "chain": "bitcoin", "size": 500000},
            {"token": "USDC", "chain": "polygon", "size": 2000000},
        ]
        
        for pool in pools:
            LIQUIDITY_POOL_SIZE.labels(
                token=pool["token"], 
                chain=pool["chain"]
            ).set(pool["size"])
        
        logger.debug("Bridge metrics updated")
        
    except Exception as e:
        logger.error(f"Error updating bridge metrics: {e}")


async def publish_event(event_type: str, data: Dict[str, Any]):
    """Publish event to Redis for real-time updates."""
    if not redis_client:
        return
    
    try:
        event = {
            "service": "bridge",
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        await redis_client.publish("scorpius:events", json.dumps(event))
        logger.debug(f"Published event: {event_type}")
        
    except Exception as e:
        logger.error(f"Error publishing event: {e}")


# Routes
@app.get("/healthz")
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/readyz")
async def readiness_probe():
    """Kubernetes readiness probe endpoint."""
    try:
        # Check Redis connection
        if redis_client:
            await redis_client.ping()
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/health")
async def health_check():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "bridge",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


@app.post("/bridge/initiate", response_model=Dict[str, str])
async def initiate_bridge_transaction(transaction: BridgeTransaction, background_tasks: BackgroundTasks):
    """Initiate a new bridge transaction."""
    start_time = time.time()
    
    try:
        # Validate transaction
        if transaction.from_chain == transaction.to_chain:
            raise HTTPException(status_code=400, detail="Source and destination chains cannot be the same")
        
        # Generate transaction ID if not provided
        if not transaction.transaction_id:
            transaction.transaction_id = f"bridge_{int(time.time())}_{hash(transaction.recipient)}"
        
        # Store transaction in Redis
        if redis_client:
            transaction_data = {
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "from_chain": transaction.from_chain,
                "to_chain": transaction.to_chain,
                "amount": transaction.amount,
                "recipient": transaction.recipient
            }
            
            await redis_client.hset(
                f"bridge:transaction:{transaction.transaction_id}", 
                mapping=transaction_data
            )
        
        # Add background task to process transaction
        background_tasks.add_task(process_bridge_transaction, transaction.transaction_id)
        
        # Update metrics
        BRIDGE_TRANSACTIONS.labels(
            chain_from=transaction.from_chain,
            chain_to=transaction.to_chain,
            status="initiated"
        ).inc()
        
        # Publish event
        await publish_event("transaction_initiated", {
            "transaction_id": transaction.transaction_id,
            "from_chain": transaction.from_chain,
            "to_chain": transaction.to_chain,
            "amount": transaction.amount
        })
        
        logger.info(f"Bridge transaction initiated: {transaction.transaction_id}")
        
        return {
            "transaction_id": transaction.transaction_id,
            "status": "initiated",
            "message": "Bridge transaction initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error initiating bridge transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        TRANSACTION_DURATION.observe(time.time() - start_time)


@app.get("/bridge/status/{transaction_id}", response_model=BridgeStatus)
async def get_bridge_status(transaction_id: str):
    """Get bridge transaction status."""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        # Retrieve transaction from Redis
        transaction_data = await redis_client.hgetall(f"bridge:transaction:{transaction_id}")
        
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return BridgeStatus(
            transaction_id=transaction_id,
            status=transaction_data.get("status", "unknown"),
            from_chain=transaction_data.get("from_chain", ""),
            to_chain=transaction_data.get("to_chain", ""),
            amount=transaction_data.get("amount", "0"),
            created_at=datetime.fromisoformat(transaction_data.get("created_at")),
            updated_at=datetime.fromisoformat(transaction_data.get("updated_at", transaction_data.get("created_at"))),
            confirmations=int(transaction_data.get("confirmations", 0))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bridge status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/liquidity/pools", response_model=List[LiquidityPool])
async def get_liquidity_pools():
    """Get all liquidity pools information."""
    try:
        # Mock data for demonstration
        pools = [
            LiquidityPool(
                pool_id="eth_usdc_pool",
                token_symbol="ETH/USDC",
                chain="ethereum",
                total_liquidity="10000000",
                available_liquidity="8500000",
                utilization_rate=0.15,
                apy=12.5
            ),
            LiquidityPool(
                pool_id="btc_usdt_pool", 
                token_symbol="BTC/USDT",
                chain="bitcoin",
                total_liquidity="5000000",
                available_liquidity="4200000",
                utilization_rate=0.16,
                apy=11.8
            ),
            LiquidityPool(
                pool_id="matic_usdc_pool",
                token_symbol="MATIC/USDC",
                chain="polygon",
                total_liquidity="2000000",
                available_liquidity="1800000",
                utilization_rate=0.10,
                apy=15.2
            )
        ]
        
        return pools
        
    except Exception as e:
        logger.error(f"Error getting liquidity pools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chains/status", response_model=List[ChainStatus])
async def get_chain_status():
    """Get status of all supported chains."""
    try:
        # Mock data for demonstration
        chains = [
            ChainStatus(
                chain_name="ethereum",
                is_active=True,
                block_height=18500000,
                avg_block_time=12.0,
                gas_price="30000000000",
                congestion_level="medium"
            ),
            ChainStatus(
                chain_name="polygon",
                is_active=True,
                block_height=49000000,
                avg_block_time=2.1,
                gas_price="30000000000",
                congestion_level="low"
            ),
            ChainStatus(
                chain_name="arbitrum",
                is_active=True,
                block_height=145000000,
                avg_block_time=0.3,
                gas_price="100000000",
                congestion_level="low"
            )
        ]
        
        return chains
        
    except Exception as e:
        logger.error(f"Error getting chain status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bridge/cancel/{transaction_id}")
async def cancel_bridge_transaction(transaction_id: str):
    """Cancel a pending bridge transaction."""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        # Check if transaction exists and is cancellable
        transaction_data = await redis_client.hgetall(f"bridge:transaction:{transaction_id}")
        
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        status = transaction_data.get("status")
        if status not in ["pending", "processing"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel transaction with status: {status}")
        
        # Update transaction status
        await redis_client.hset(f"bridge:transaction:{transaction_id}", "status", "cancelled")
        await redis_client.hset(f"bridge:transaction:{transaction_id}", "updated_at", datetime.utcnow().isoformat())
        
        # Update metrics
        BRIDGE_TRANSACTIONS.labels(
            chain_from=transaction_data.get("from_chain", "unknown"),
            chain_to=transaction_data.get("to_chain", "unknown"),
            status="cancelled"
        ).inc()
        
        # Publish event
        await publish_event("transaction_cancelled", {
            "transaction_id": transaction_id,
            "reason": "user_requested"
        })
        
        logger.info(f"Bridge transaction cancelled: {transaction_id}")
        
        return {"message": "Transaction cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling bridge transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_bridge_transaction(transaction_id: str):
    """Background task to process bridge transaction."""
    try:
        logger.info(f"Processing bridge transaction: {transaction_id}")
        
        if not redis_client:
            return
        
        # Update status to processing
        await redis_client.hset(f"bridge:transaction:{transaction_id}", "status", "processing")
        await redis_client.hset(f"bridge:transaction:{transaction_id}", "updated_at", datetime.utcnow().isoformat())
        
        # Publish event
        await publish_event("transaction_processing", {"transaction_id": transaction_id})
        
        # Simulate processing time
        await asyncio.sleep(30)
        
        # Simulate successful completion (90% success rate)
        import random
        if random.random() < 0.9:
            await redis_client.hset(f"bridge:transaction:{transaction_id}", "status", "completed")
            await redis_client.hset(f"bridge:transaction:{transaction_id}", "confirmations", "12")
            
            # Get transaction data for metrics
            transaction_data = await redis_client.hgetall(f"bridge:transaction:{transaction_id}")
            
            BRIDGE_TRANSACTIONS.labels(
                chain_from=transaction_data.get("from_chain", "unknown"),
                chain_to=transaction_data.get("to_chain", "unknown"),
                status="completed"
            ).inc()
            
            await publish_event("transaction_completed", {"transaction_id": transaction_id})
            logger.info(f"Bridge transaction completed: {transaction_id}")
        else:
            await redis_client.hset(f"bridge:transaction:{transaction_id}", "status", "failed")
            await redis_client.hset(f"bridge:transaction:{transaction_id}", "error", "Insufficient liquidity")
            
            # Get transaction data for metrics
            transaction_data = await redis_client.hgetall(f"bridge:transaction:{transaction_id}")
            
            BRIDGE_TRANSACTIONS.labels(
                chain_from=transaction_data.get("from_chain", "unknown"),
                chain_to=transaction_data.get("to_chain", "unknown"),
                status="failed"
            ).inc()
            
            await publish_event("transaction_failed", {
                "transaction_id": transaction_id,
                "error": "Insufficient liquidity"
            })
            logger.warning(f"Bridge transaction failed: {transaction_id}")
        
        await redis_client.hset(f"bridge:transaction:{transaction_id}", "updated_at", datetime.utcnow().isoformat())
        
    except Exception as e:
        logger.error(f"Error processing bridge transaction {transaction_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
