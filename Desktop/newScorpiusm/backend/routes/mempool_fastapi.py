"""
Mempool Monitoring FastAPI Routes Module
Handles mempool transaction monitoring, analysis, and MEV detection
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import MempoolTransaction, MEVOpportunity, Session, User, get_db
from pydantic import BaseModel
from services.blockchain import MempoolMonitor, MEVDetector, Web3Service
from sqlalchemy import desc, func

router = APIRouter(prefix="/api/mempool", tags=["mempool"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models
class MempoolTransactionResponse(BaseModel):
    id: int
    transaction_hash: str
    from_address: str
    to_address: str
    value: float
    gas_price: int
    gas_limit: int
    nonce: int
    transaction_type: str
    detected_at: datetime
    block_number: int | None
    mev_potential: bool
    risk_score: float


class MEVAnalysisRequest(BaseModel):
    transaction_hashes: list[str]
    analysis_type: str = "full"


class MempoolStatsResponse(BaseModel):
    total_transactions: int
    pending_transactions: int
    average_gas_price: float
    high_value_transactions: int
    mev_opportunities: int
    risk_alerts: int


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    db = next(get_db())
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found") from e
    return user


@router.get("/transactions", response_model=list[MempoolTransactionResponse])
async def get_mempool_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, le=500),
    min_value: float | None = Query(None),
    transaction_type: str | None = Query(None),
    mev_potential: bool | None = Query(None),
):
    """Get mempool transactions with optional filtering"""
    try:
        query = db.query(MempoolTransaction)

        if min_value is not None:
            query = query.filter(MempoolTransaction.value >= min_value)

        if transaction_type:
            query = query.filter(
                MempoolTransaction.transaction_type == transaction_type
            )

        if mev_potential is not None:
            query = query.filter(MempoolTransaction.mev_potential == mev_potential)

        transactions = (
            query.order_by(desc(MempoolTransaction.detected_at)).limit(limit).all()
        )

        return [
            MempoolTransactionResponse(
                id=tx.id,
                transaction_hash=tx.transaction_hash,
                from_address=tx.from_address,
                to_address=tx.to_address,
                value=tx.value,
                gas_price=tx.gas_price,
                gas_limit=tx.gas_limit,
                nonce=tx.nonce,
                transaction_type=tx.transaction_type,
                detected_at=tx.detected_at,
                block_number=tx.block_number,
                mev_potential=tx.mev_potential,
                risk_score=tx.risk_score,
            )
            for tx in transactions
        ]
    except Exception as e:
        logger.error(f"Error fetching mempool transactions: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch mempool transactions"
        ) from e


@router.get("/stats", response_model=MempoolStatsResponse)
async def get_mempool_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    hours: int = Query(24, le=168),  # Last 24 hours by default, max 7 days
):
    """Get mempool statistics for the specified time period"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Basic transaction stats
        total_txs = (
            db.query(func.count(MempoolTransaction.id))
            .filter(MempoolTransaction.detected_at >= cutoff_time)
            .scalar()
        )

        pending_txs = (
            db.query(func.count(MempoolTransaction.id))
            .filter(
                MempoolTransaction.detected_at >= cutoff_time,
                MempoolTransaction.block_number.is_(None),
            )
            .scalar()
        )

        # Average gas price
        avg_gas_price = (
            db.query(func.avg(MempoolTransaction.gas_price))
            .filter(MempoolTransaction.detected_at >= cutoff_time)
            .scalar()
            or 0
        )

        # High value transactions (>1 ETH)
        high_value_txs = (
            db.query(func.count(MempoolTransaction.id))
            .filter(
                MempoolTransaction.detected_at >= cutoff_time,
                MempoolTransaction.value > 1.0,
            )
            .scalar()
        )

        # MEV opportunities
        mev_opportunities = (
            db.query(func.count(MEVOpportunity.id))
            .filter(MEVOpportunity.detected_at >= cutoff_time)
            .scalar()
        )

        # Risk alerts (high risk score transactions)
        risk_alerts = (
            db.query(func.count(MempoolTransaction.id))
            .filter(
                MempoolTransaction.detected_at >= cutoff_time,
                MempoolTransaction.risk_score > 0.7,
            )
            .scalar()
        )

        return MempoolStatsResponse(
            total_transactions=total_txs or 0,
            pending_transactions=pending_txs or 0,
            average_gas_price=float(avg_gas_price),
            high_value_transactions=high_value_txs or 0,
            mev_opportunities=mev_opportunities or 0,
            risk_alerts=risk_alerts or 0,
        )
    except Exception as e:
        logger.error(f"Error fetching mempool stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch mempool stats"
        ) from e


@router.post("/analyze")
async def analyze_transactions(
    request: MEVAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze specific transactions for MEV opportunities"""
    try:
        # Validate transaction hashes
        if not request.transaction_hashes:
            raise HTTPException(
                status_code=400, detail="No transaction hashes provided"
            ) from e

        if len(request.transaction_hashes) > 50:
            raise HTTPException(
                status_code=400, detail="Too many transactions to analyze (max 50)"
            )

        # Start background analysis
        background_tasks.add_task(
            _analyze_transactions_background,
            request.transaction_hashes,
            request.analysis_type,
            current_user.id,
        )

        return {
            "message": "Analysis started",
            "transaction_count": len(request.transaction_hashes),
            "analysis_type": request.analysis_type,
            "status": "processing",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting transaction analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis") from e


async def _analyze_transactions_background(
    tx_hashes: list[str], analysis_type: str, user_id: int
):
    """Background task for transaction analysis"""
    try:
        db = next(get_db())
        mev_detector = MEVDetector()
        web3_service = Web3Service()

        for tx_hash in tx_hashes:
            try:
                # Get transaction details
                tx_data = await web3_service.get_transaction(tx_hash)
                if not tx_data:
                    continue

                # Analyze for MEV potential
                mev_analysis = await mev_detector.analyze_transaction(tx_data)

                # Store/update transaction record
                existing_tx = (
                    db.query(MempoolTransaction)
                    .filter(MempoolTransaction.transaction_hash == tx_hash)
                    .first()
                )

                if existing_tx:
                    existing_tx.mev_potential = mev_analysis.get(
                        "has_mev_potential", False
                    )
                    existing_tx.risk_score = mev_analysis.get("risk_score", 0.0)
                else:
                    # Create new transaction record
                    new_tx = MempoolTransaction(
                        transaction_hash=tx_hash,
                        from_address=tx_data.get("from", ""),
                        to_address=tx_data.get("to", ""),
                        value=float(tx_data.get("value", 0))
                        / 10**18,  # Convert Wei to ETH
                        gas_price=tx_data.get("gasPrice", 0),
                        gas_limit=tx_data.get("gas", 0),
                        nonce=tx_data.get("nonce", 0),
                        transaction_type="analysis",
                        mev_potential=mev_analysis.get("has_mev_potential", False),
                        risk_score=mev_analysis.get("risk_score", 0.0),
                        detected_at=datetime.utcnow(),
                    )
                    db.add(new_tx)

                # Create MEV opportunity if detected
                if mev_analysis.get("has_mev_potential"):
                    opportunity = MEVOpportunity(
                        transaction_hash=tx_hash,
                        block_number=tx_data.get("blockNumber"),
                        opportunity_type=mev_analysis.get(
                            "opportunity_type", "arbitrage"
                        ),
                        estimated_profit=mev_analysis.get("estimated_profit", 0.0),
                        gas_cost=mev_analysis.get("gas_cost", 0.0),
                        net_profit=mev_analysis.get("net_profit", 0.0),
                        status="detected",
                        detected_at=datetime.utcnow(),
                    )
                    db.add(opportunity)

                db.commit()

            except Exception as tx_error:
                logger.error(f"Error analyzing transaction {tx_hash}: {tx_error}")
                continue

        db.close()

    except Exception as e:
        logger.error(f"Error in background transaction analysis: {e}")


@router.get("/live")
async def get_live_mempool_feed(
    current_user: User = Depends(get_current_user), limit: int = Query(20, le=100)
):
    """Get live mempool feed (most recent transactions)"""
    try:
        # Initialize mempool monitor
        mempool_monitor = MempoolMonitor()

        # Get recent transactions from mempool
        live_transactions = await mempool_monitor.get_pending_transactions(limit=limit)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_count": len(live_transactions),
            "transactions": live_transactions,
        }
    except Exception as e:
        logger.error(f"Error fetching live mempool feed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch live mempool feed"
        ) from e


@router.post("/monitor/start")
async def start_mempool_monitoring(
    background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)
):
    """Start continuous mempool monitoring"""
    try:
        # Start background monitoring task
        background_tasks.add_task(_start_mempool_monitoring_background, current_user.id)

        return {
            "message": "Mempool monitoring started",
            "status": "active",
            "user_id": current_user.id,
        }
    except Exception as e:
        logger.error(f"Error starting mempool monitoring: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to start mempool monitoring"
        ) from e


async def _start_mempool_monitoring_background(user_id: int):
    """Background task for continuous mempool monitoring"""
    try:
        mempool_monitor = MempoolMonitor()
        await mempool_monitor.start_monitoring(user_id=user_id)
    except Exception as e:
        logger.error(f"Error in mempool monitoring background task: {e}")


@router.post("/monitor/stop")
async def stop_mempool_monitoring(current_user: User = Depends(get_current_user)):
    """Stop mempool monitoring for the current user"""
    try:
        mempool_monitor = MempoolMonitor()
        await mempool_monitor.stop_monitoring(user_id=current_user.id)

        return {
            "message": "Mempool monitoring stopped",
            "status": "inactive",
            "user_id": current_user.id,
        }
    except Exception as e:
        logger.error(f"Error stopping mempool monitoring: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to stop mempool monitoring"
        ) from e
