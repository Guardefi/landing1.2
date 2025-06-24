"""
FastAPI routes for Scorpius Bridge Network
"""

import logging
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core.types import BridgeType, ChainType, SecurityLevel
from ..storage.database import get_database_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/bridge", tags=["Bridge Network"])

# Global instances (will be set by main app)
_bridge_network = None
_validator_manager = None
_atomic_swap_engine = None
_liquidity_manager = None


def get_bridge_network():
    """Get the bridge network instance."""
    if _bridge_network is None:
        raise HTTPException(
            status_code=503, detail="Bridge network not initialized"
        ) from e
    return _bridge_network


def get_validator_manager():
    """Get the validator manager instance."""
    if _validator_manager is None:
        raise HTTPException(
            status_code=503, detail="Validator manager not initialized"
        ) from e
    return _validator_manager


def get_atomic_swap_engine():
    """Get the atomic swap engine instance."""
    if _atomic_swap_engine is None:
        raise HTTPException(
            status_code=503, detail="Atomic swap engine not initialized"
        ) from e
    return _atomic_swap_engine


def get_liquidity_manager():
    """Get the liquidity manager instance."""
    if _liquidity_manager is None:
        raise HTTPException(
            status_code=503, detail="Liquidity manager not initialized"
        ) from e
    return _liquidity_manager


def set_bridge_components(network, validator_mgr, swap_engine, liquidity_mgr):
    """Set all bridge component instances."""
    global _bridge_network, _validator_manager, _atomic_swap_engine, _liquidity_manager
    _bridge_network = network
    _validator_manager = validator_mgr
    _atomic_swap_engine = swap_engine
    _liquidity_manager = liquidity_mgr


# Request/Response Models
class TransferRequest(BaseModel):
    """Request model for initiating a bridge transfer."""

    from_chain: str = Field(..., description="Source blockchain")
    to_chain: str = Field(..., description="Destination blockchain")
    asset: str = Field(..., description="Asset symbol")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    sender_address: str = Field(..., description="Sender wallet address")
    receiver_address: str = Field(..., description="Receiver wallet address")
    bridge_type: str = Field(
        default="lock_and_mint", description="Bridge mechanism type"
    )
    security_level: str = Field(
        default="standard", description="Security level for the transfer"
    )
    user_id: str | None = Field(None, description="User identifier")


class TransferResponse(BaseModel):
    """Response model for transfer operations."""

    transfer_id: str
    status: str
    message: str
    estimated_completion_time: str | None = None
    bridge_fee: Decimal | None = None
    gas_estimate: int | None = None


class TransferStatusResponse(BaseModel):
    """Response model for transfer status."""

    id: str
    status: str
    progress_percentage: float
    from_chain: str
    to_chain: str
    asset: str
    amount: Decimal
    sender_address: str
    receiver_address: str
    bridge_fee: Decimal
    gas_cost: Decimal
    created_at: datetime
    completed_at: datetime | None = None
    confirmations: str
    transaction_hashes: dict[str, str | None]
    error_message: str | None = None


class NetworkStatsResponse(BaseModel):
    """Response model for network statistics."""

    total_transfers: int
    completed_transfers: int
    active_transfers: int
    success_rate: float
    total_volume: Decimal
    daily_volume: Decimal
    active_validators: int
    supported_chains: int
    supported_assets: int
    uptime_percentage: float
    average_transfer_time: float


# API Endpoints
@router.post("/transfers", response_model=TransferResponse)
async def initiate_transfer(
    request: TransferRequest,
    background_tasks: BackgroundTasks,
    bridge=Depends(get_bridge_network),
):
    """Initiate a cross-chain bridge transfer."""
    try:
        # Validate chain types
        try:
            from_chain = ChainType(request.from_chain.lower())
            to_chain = ChainType(request.to_chain.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported chain: {request.from_chain} or {request.to_chain}",
            )

        # Validate bridge type
        try:
            bridge_type = BridgeType(request.bridge_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported bridge type: {request.bridge_type}",
            )

        # Validate security level
        try:
            security_level = SecurityLevel(request.security_level.lower())
        except ValueError:
            security_level = SecurityLevel.STANDARD

        # Initiate the transfer
        transfer_id = await bridge.initiate_transfer(
            from_chain=from_chain,
            to_chain=to_chain,
            asset=request.asset,
            amount=request.amount,
            sender=request.sender_address,
            receiver=request.receiver_address,
            bridge_type=bridge_type,
            user_id=request.user_id,
        )

        # Get the created transfer for response details
        transfer = await bridge.get_transfer_status(transfer_id)

        return TransferResponse(
            transfer_id=transfer_id,
            status="initiated",
            message="Transfer initiated successfully",
            estimated_completion_time="15-30 minutes",
            bridge_fee=transfer.bridge_fee if transfer else None,
            gas_estimate=21000,  # Placeholder
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to initiate transfer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/transfers/{transfer_id}", response_model=TransferStatusResponse)
async def get_transfer_status(transfer_id: str, bridge=Depends(get_bridge_network)):
    """Get the status of a bridge transfer."""
    try:
        transfer = await bridge.get_transfer_status(transfer_id)

        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found") from e

        return TransferStatusResponse(
            id=transfer.id,
            status=transfer.status.value,
            progress_percentage=transfer.get_progress_percentage(),
            from_chain=transfer.from_chain.value,
            to_chain=transfer.to_chain.value,
            asset=transfer.asset,
            amount=transfer.amount,
            sender_address=transfer.sender_address,
            receiver_address=transfer.receiver_address,
            bridge_fee=transfer.bridge_fee,
            gas_cost=transfer.gas_cost,
            created_at=transfer.timestamp,
            completed_at=transfer.completed_at,
            confirmations=f"{transfer.current_confirmations}/{transfer.required_confirmations}",
            transaction_hashes={
                "source": transfer.source_tx_hash,
                "destination": transfer.dest_tx_hash,
                "lock": transfer.lock_tx_hash,
                "mint": transfer.mint_tx_hash,
            },
            error_message=transfer.error_message,
        )

    except Exception as e:
        logger.error(f"Failed to get transfer status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/transfers", response_model=list[TransferStatusResponse])
async def list_transfers(
    user_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    bridge=Depends(get_bridge_network),
):
    """List bridge transfers with optional filtering."""
    try:
        # This would need to be implemented in the bridge network
        transfers = await bridge.list_transfers(
            user_id=user_id, status=status, limit=limit, offset=offset
        )

        return [
            TransferStatusResponse(
                id=t.id,
                status=t.status.value,
                progress_percentage=t.get_progress_percentage(),
                from_chain=t.from_chain.value,
                to_chain=t.to_chain.value,
                asset=t.asset,
                amount=t.amount,
                sender_address=t.sender_address,
                receiver_address=t.receiver_address,
                bridge_fee=t.bridge_fee,
                gas_cost=t.gas_cost,
                created_at=t.timestamp,
                completed_at=t.completed_at,
                confirmations=f"{t.current_confirmations}/{t.required_confirmations}",
                transaction_hashes={
                    "source": t.source_tx_hash,
                    "destination": t.dest_tx_hash,
                    "lock": t.lock_tx_hash,
                    "mint": t.mint_tx_hash,
                },
                error_message=t.error_message,
            )
            for t in transfers
        ]

    except Exception as e:
        logger.error(f"Failed to list transfers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/transfers/{transfer_id}/retry")
async def retry_transfer(transfer_id: str, bridge=Depends(get_bridge_network)):
    """Retry a failed transfer."""
    try:
        success = await bridge.retry_transfer(transfer_id)

        if not success:
            raise HTTPException(
                status_code=400, detail="Transfer cannot be retried"
            ) from e

        return {"message": "Transfer retry initiated"}

    except Exception as e:
        logger.error(f"Failed to retry transfer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.delete("/transfers/{transfer_id}")
async def cancel_transfer(transfer_id: str, bridge=Depends(get_bridge_network)):
    """Cancel a pending transfer."""
    try:
        success = await bridge.cancel_transfer(transfer_id)

        if not success:
            raise HTTPException(
                status_code=400, detail="Transfer cannot be cancelled"
            ) from e

        return {"message": "Transfer cancelled successfully"}

    except Exception as e:
        logger.error(f"Failed to cancel transfer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/statistics", response_model=NetworkStatsResponse)
async def get_network_statistics(bridge=Depends(get_bridge_network)):
    """Get comprehensive bridge network statistics."""
    try:
        stats = await bridge.get_network_statistics()

        return NetworkStatsResponse(
            total_transfers=stats["total_transfers"],
            completed_transfers=stats["completed_transfers"],
            active_transfers=stats["active_transfers"],
            success_rate=stats["success_rate"],
            total_volume=Decimal(str(stats["total_volume"])),
            daily_volume=Decimal("0"),  # Would need to be calculated
            active_validators=stats["active_validators"],
            supported_chains=stats["supported_chains"],
            supported_assets=stats["supported_assets"],
            uptime_percentage=99.9,  # Would be calculated from monitoring
            average_transfer_time=20.5,  # Would be calculated from historical data
        )

    except Exception as e:
        logger.error(f"Failed to get network statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/health")
async def health_check(bridge=Depends(get_bridge_network)):
    """Health check endpoint for the bridge network."""
    try:
        # Check if bridge network is running
        is_healthy = bridge.running if hasattr(bridge, "running") else True

        # Check database connectivity
        db_manager = await get_database_manager()
        db_healthy = True  # Would implement actual check

        status = "healthy" if (is_healthy and db_healthy) else "unhealthy"

        return {
            "status": status,
            "bridge_network": is_healthy,
            "database": db_healthy,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/chains")
async def get_supported_chains():
    """Get list of supported blockchain networks."""
    return {
        "supported_chains": [chain.value for chain in ChainType],
        "bridge_types": [bridge_type.value for bridge_type in BridgeType],
        "security_levels": [level.value for level in SecurityLevel],
    }


@router.get("/fees/{from_chain}/{to_chain}/{asset}")
async def estimate_bridge_fee(
    from_chain: str,
    to_chain: str,
    asset: str,
    amount: Decimal,
    bridge=Depends(get_bridge_network),
):
    """Estimate bridge fee for a transfer."""
    try:
        # Validate chain types
        try:
            from_chain_enum = ChainType(from_chain.lower())
            to_chain_enum = ChainType(to_chain.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Unsupported chain: {from_chain} or {to_chain}"
            ) from e

        # Calculate fee (would be implemented in bridge network)
        base_fee_percentage = Decimal("0.003")  # 0.3%
        bridge_fee = amount * base_fee_percentage

        return {
            "bridge_fee": bridge_fee,
            "bridge_fee_percentage": float(base_fee_percentage * 100),
            "estimated_gas_cost": "0.01",  # Would be calculated dynamically
            "total_cost": bridge_fee + Decimal("0.01"),
        }

    except Exception as e:
        logger.error(f"Failed to estimate fee: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# =============================================================================
# VALIDATOR MANAGEMENT ENDPOINTS
# =============================================================================


class ValidatorRegistrationRequest(BaseModel):
    """Request model for validator registration."""

    validator_id: str = Field(..., description="Unique validator identifier")
    address: str = Field(..., description="Validator address")
    stake_amount: Decimal = Field(..., gt=0, description="Stake amount")
    public_key: str = Field(..., description="Validator public key")


@router.post("/validators/register")
async def register_validator(
    request: ValidatorRegistrationRequest,
    validator_manager=Depends(get_validator_manager),
):
    """Register a new validator."""
    try:
        success = await validator_manager.register_validator(
            validator_id=request.validator_id,
            address=request.address,
            stake_amount=request.stake_amount,
            public_key=request.public_key,
        )

        if success:
            return {
                "message": "Validator registered successfully",
                "validator_id": request.validator_id,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Failed to register validator"
            ) from e

    except Exception as e:
        logger.error(f"Validator registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/validators/{validator_id}")
async def unregister_validator(
    validator_id: str,
    validator_manager=Depends(get_validator_manager),
):
    """Unregister a validator."""
    try:
        success = await validator_manager.unregister_validator(validator_id)

        if success:
            return {"message": "Validator unregistered successfully"}
        else:
            raise HTTPException(status_code=404, detail="Validator not found") from e

    except Exception as e:
        logger.error(f"Validator unregistration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validators")
async def get_validators(validator_manager=Depends(get_validator_manager)):
    """Get all validators and their status."""
    try:
        counts = validator_manager.get_validator_count()
        active_validators = validator_manager.get_active_validators()

        return {
            "counts": counts,
            "active_validators": [
                {
                    "validator_id": v.validator_id,
                    "address": v.address,
                    "stake_amount": str(v.stake_amount),
                    "status": v.status.value,
                    "reputation_score": v.metrics.reputation_score,
                    "uptime_percentage": v.metrics.uptime_percentage,
                    "total_validations": v.metrics.total_validations,
                }
                for v in active_validators
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get validators: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validators/stats")
async def get_validator_stats(validator_manager=Depends(get_validator_manager)):
    """Get comprehensive validator network statistics."""
    try:
        stats = await validator_manager.get_network_stats()
        return stats

    except Exception as e:
        logger.error(f"Failed to get validator stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ATOMIC SWAP ENDPOINTS
# =============================================================================


class AtomicSwapRequest(BaseModel):
    """Request model for initiating an atomic swap."""

    transfer_id: str = Field(..., description="Bridge transfer ID")
    timeout_hours: int = Field(default=24, gt=0, le=168, description="Timeout in hours")


@router.post("/atomic-swaps/initiate")
async def initiate_atomic_swap(
    request: AtomicSwapRequest,
    bridge_network=Depends(get_bridge_network),
    swap_engine=Depends(get_atomic_swap_engine),
):
    """Initiate an atomic swap for a bridge transfer."""
    try:
        # Get transfer details (would fetch from database in production)
        transfer = await bridge_network.get_transfer(request.transfer_id)
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found") from e

        swap = await swap_engine.initiate_swap(transfer, request.timeout_hours)

        return {
            "swap_id": swap.swap_id,
            "hash_lock": swap.hash_lock,
            "timeout_block": swap.timeout_block,
            "status": swap.status.value,
            "message": "Atomic swap initiated successfully",
        }

    except Exception as e:
        logger.error(f"Failed to initiate atomic swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atomic-swaps/{swap_id}/lock")
async def lock_swap_funds(
    swap_id: str,
    swap_engine=Depends(get_atomic_swap_engine),
):
    """Lock funds for an atomic swap."""
    try:
        success = await swap_engine.lock_funds(swap_id)

        if success:
            return {"message": "Funds locked successfully", "swap_id": swap_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to lock funds") from e

    except Exception as e:
        logger.error(f"Failed to lock swap funds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class RevealSecretRequest(BaseModel):
    """Request model for revealing atomic swap secret."""

    secret: str = Field(..., description="Secret to reveal")


@router.post("/atomic-swaps/{swap_id}/reveal")
async def reveal_swap_secret(
    swap_id: str,
    request: RevealSecretRequest,
    swap_engine=Depends(get_atomic_swap_engine),
):
    """Reveal secret to complete atomic swap."""
    try:
        success = await swap_engine.reveal_secret(swap_id, request.secret)

        if success:
            return {"message": "Secret revealed successfully", "swap_id": swap_id}
        else:
            raise HTTPException(
                status_code=400, detail="Invalid secret or swap state"
            ) from e

    except Exception as e:
        logger.error(f"Failed to reveal secret: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atomic-swaps/{swap_id}/complete")
async def complete_atomic_swap(
    swap_id: str,
    swap_engine=Depends(get_atomic_swap_engine),
):
    """Complete an atomic swap."""
    try:
        success = await swap_engine.complete_swap(swap_id)

        if success:
            return {"message": "Atomic swap completed successfully", "swap_id": swap_id}
        else:
            raise HTTPException(status_code=400, detail="Cannot complete swap") from e

    except Exception as e:
        logger.error(f"Failed to complete atomic swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/atomic-swaps/{swap_id}")
async def get_atomic_swap(
    swap_id: str,
    swap_engine=Depends(get_atomic_swap_engine),
):
    """Get atomic swap details."""
    try:
        swap = swap_engine.get_swap(swap_id)

        if not swap:
            raise HTTPException(status_code=404, detail="Swap not found") from e

        return {
            "swap_id": swap.swap_id,
            "status": swap.status.value,
            "initiator_address": swap.initiator_address,
            "participant_address": swap.participant_address,
            "source_chain": swap.source_chain,
            "destination_chain": swap.destination_chain,
            "source_amount": str(swap.source_amount),
            "destination_amount": str(swap.destination_amount),
            "hash_lock": swap.hash_lock,
            "timeout_block": swap.timeout_block,
            "created_at": swap.created_at.isoformat(),
            "updated_at": swap.updated_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get atomic swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# LIQUIDITY POOL ENDPOINTS
# =============================================================================


class CreatePoolRequest(BaseModel):
    """Request model for creating a liquidity pool."""

    chain: str = Field(..., description="Blockchain network")
    token_address: str = Field(..., description="Token contract address")
    token_symbol: str = Field(..., description="Token symbol")
    initial_liquidity: Decimal = Field(
        default=Decimal("0"), ge=0, description="Initial liquidity"
    )


@router.post("/liquidity/pools")
async def create_liquidity_pool(
    request: CreatePoolRequest,
    liquidity_manager=Depends(get_liquidity_manager),
):
    """Create a new liquidity pool."""
    try:
        pool_id = await liquidity_manager.create_pool(
            chain=request.chain,
            token_address=request.token_address,
            token_symbol=request.token_symbol,
            initial_liquidity=request.initial_liquidity,
        )

        return {"pool_id": pool_id, "message": "Liquidity pool created successfully"}

    except Exception as e:
        logger.error(f"Failed to create liquidity pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AddLiquidityRequest(BaseModel):
    """Request model for adding liquidity."""

    provider_address: str = Field(..., description="Liquidity provider address")
    amount: Decimal = Field(..., gt=0, description="Amount to add")


@router.post("/liquidity/pools/{pool_id}/add")
async def add_liquidity(
    pool_id: str,
    request: AddLiquidityRequest,
    liquidity_manager=Depends(get_liquidity_manager),
):
    """Add liquidity to a pool."""
    try:
        pool = liquidity_manager.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found") from e

        success = await pool.add_liquidity(request.provider_address, request.amount)

        if success:
            return {"message": "Liquidity added successfully", "pool_id": pool_id}
        else:
            raise HTTPException(
                status_code=400, detail="Failed to add liquidity"
            ) from e

    except Exception as e:
        logger.error(f"Failed to add liquidity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class RemoveLiquidityRequest(BaseModel):
    """Request model for removing liquidity."""

    provider_address: str = Field(..., description="Liquidity provider address")
    amount: Decimal = Field(..., gt=0, description="Amount to remove")


@router.post("/liquidity/pools/{pool_id}/remove")
async def remove_liquidity(
    pool_id: str,
    request: RemoveLiquidityRequest,
    liquidity_manager=Depends(get_liquidity_manager),
):
    """Remove liquidity from a pool."""
    try:
        pool = liquidity_manager.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found") from e

        success = await pool.remove_liquidity(request.provider_address, request.amount)

        if success:
            return {"message": "Liquidity removed successfully", "pool_id": pool_id}
        else:
            raise HTTPException(
                status_code=400, detail="Failed to remove liquidity"
            ) from e

    except Exception as e:
        logger.error(f"Failed to remove liquidity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity/pools")
async def get_liquidity_pools(
    chain: str | None = None,
    token: str | None = None,
    liquidity_manager=Depends(get_liquidity_manager),
):
    """Get liquidity pools with optional filtering."""
    try:
        if chain:
            pools = liquidity_manager.get_pools_by_chain(chain)
        elif token:
            pools = liquidity_manager.get_pools_by_token(token)
        else:
            pools = liquidity_manager.get_all_pools()

        return {
            "pools": [pool.get_pool_info() for pool in pools],
            "total_pools": len(pools),
        }

    except Exception as e:
        logger.error(f"Failed to get liquidity pools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity/pools/{pool_id}")
async def get_liquidity_pool(
    pool_id: str,
    liquidity_manager=Depends(get_liquidity_manager),
):
    """Get detailed information about a specific liquidity pool."""
    try:
        pool = liquidity_manager.get_pool(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found") from e

        return pool.get_pool_info()

    except Exception as e:
        logger.error(f"Failed to get liquidity pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liquidity/stats")
async def get_liquidity_stats(liquidity_manager=Depends(get_liquidity_manager)):
    """Get comprehensive liquidity statistics."""
    try:
        total_liquidity = await liquidity_manager.get_total_liquidity()
        all_pools = liquidity_manager.get_all_pools()

        return {
            "total_liquidity_by_token": {k: str(v) for k, v in total_liquidity.items()},
            "total_pools": len(all_pools),
            "pools_by_chain": {
                chain: len([p for p in all_pools if p.chain == chain])
                for chain in set(p.chain for p in all_pools)
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get liquidity stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
