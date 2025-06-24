"""
MEV Operations FastAPI Routes Module
Handles MEV strategies, opportunities, and performance monitoring
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import MEVOpportunity, MEVStrategy, Session, User, get_db
from pydantic import BaseModel
from sqlalchemy import desc

router = APIRouter(prefix="/api/mev", tags=["mev"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class MEVStrategyCreate(BaseModel):
    name: str
    strategy_type: str
    description: str | None = None
    parameters: dict | None = None
    risk_level: str | None = "medium"
    target_profit: float | None = None


class MEVStrategyResponse(BaseModel):
    id: int
    name: str
    strategy_type: str
    description: str | None
    status: str
    profit_target: float | None
    current_profit: float | None
    trades_executed: int
    win_rate: float
    risk_level: str
    created_at: datetime
    updated_at: datetime


class MEVOpportunityResponse(BaseModel):
    id: int
    transaction_hash: str
    block_number: int
    opportunity_type: str
    estimated_profit: float
    gas_cost: float
    net_profit: float
    status: str
    detected_at: datetime


# Dependency for getting current user from JWT
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # TODO: Implement proper JWT validation
    # For now, return a default user
    db = next(get_db())
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found") from e
    return user


@router.get("/strategies", response_model=list[MEVStrategyResponse])
async def get_mev_strategies(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all MEV strategies for the current user"""
    try:
        strategies = (
            db.query(MEVStrategy)
            .filter(MEVStrategy.user_id == current_user.id)
            .order_by(desc(MEVStrategy.created_at))
            .all()
        )

        return [
            MEVStrategyResponse(
                id=strategy.id,
                name=strategy.name,
                strategy_type=strategy.strategy_type,
                description=strategy.description,
                status=strategy.status,
                profit_target=strategy.profit_target,
                current_profit=strategy.current_profit,
                trades_executed=strategy.trades_executed,
                win_rate=strategy.win_rate,
                risk_level=strategy.risk_level,
                created_at=strategy.created_at,
                updated_at=strategy.updated_at,
            )
            for strategy in strategies
        ]
    except Exception as e:
        logger.error(f"Error fetching MEV strategies: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch MEV strategies"
        ) from e


@router.post("/strategies", response_model=MEVStrategyResponse)
async def create_mev_strategy(
    strategy_data: MEVStrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new MEV strategy"""
    try:
        strategy = MEVStrategy(
            name=strategy_data.name,
            strategy_type=strategy_data.strategy_type,
            description=strategy_data.description,
            parameters=strategy_data.parameters or {},
            risk_level=strategy_data.risk_level,
            profit_target=strategy_data.target_profit,
            user_id=current_user.id,
            status="active",
        )

        db.add(strategy)
        db.commit()
        db.refresh(strategy)

        return MEVStrategyResponse(
            id=strategy.id,
            name=strategy.name,
            strategy_type=strategy.strategy_type,
            description=strategy.description,
            status=strategy.status,
            profit_target=strategy.profit_target,
            current_profit=strategy.current_profit or 0.0,
            trades_executed=strategy.trades_executed or 0,
            win_rate=strategy.win_rate or 0.0,
            risk_level=strategy.risk_level,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating MEV strategy: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create MEV strategy"
        ) from e


@router.get("/opportunities", response_model=list[MEVOpportunityResponse])
async def get_mev_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=100),
    status: str | None = Query(None),
):
    """Get MEV opportunities"""
    try:
        query = db.query(MEVOpportunity)

        if status:
            query = query.filter(MEVOpportunity.status == status)

        opportunities = (
            query.order_by(desc(MEVOpportunity.detected_at)).limit(limit).all()
        )

        return [
            MEVOpportunityResponse(
                id=opp.id,
                transaction_hash=opp.transaction_hash,
                block_number=opp.block_number,
                opportunity_type=opp.opportunity_type,
                estimated_profit=opp.estimated_profit,
                gas_cost=opp.gas_cost,
                net_profit=opp.net_profit,
                status=opp.status,
                detected_at=opp.detected_at,
            )
            for opp in opportunities
        ]
    except Exception as e:
        logger.error(f"Error fetching MEV opportunities: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch MEV opportunities"
        ) from e


@router.get("/strategies/{strategy_id}/performance")
async def get_strategy_performance(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, le=365),
):
    """Get performance metrics for a specific MEV strategy"""
    try:
        strategy = (
            db.query(MEVStrategy)
            .filter(
                MEVStrategy.id == strategy_id, MEVStrategy.user_id == current_user.id
            )
            .first()
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found") from e

        # Get opportunities from the last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        opportunities = (
            db.query(MEVOpportunity)
            .filter(
                MEVOpportunity.strategy_id == strategy_id,
                MEVOpportunity.detected_at >= cutoff_date,
            )
            .all()
        )

        total_profit = sum(opp.net_profit for opp in opportunities if opp.net_profit)
        successful_trades = len(
            [
                opp
                for opp in opportunities
                if opp.status == "executed" and opp.net_profit > 0
            ]
        )
        total_trades = len([opp for opp in opportunities if opp.status == "executed"])
        win_rate = (successful_trades / total_trades) if total_trades > 0 else 0

        return {
            "strategy_id": strategy_id,
            "period_days": days,
            "total_profit": total_profit,
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "win_rate": win_rate,
            "avg_profit_per_trade": (
                total_profit / total_trades if total_trades > 0 else 0
            ),
            "opportunities": len(opportunities),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategy performance: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch strategy performance"
        ) from e


@router.post("/strategies/{strategy_id}/toggle")
async def toggle_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle MEV strategy active/inactive status"""
    try:
        strategy = (
            db.query(MEVStrategy)
            .filter(
                MEVStrategy.id == strategy_id, MEVStrategy.user_id == current_user.id
            )
            .first()
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found") from e

        strategy.status = "inactive" if strategy.status == "active" else "active"
        strategy.updated_at = datetime.utcnow()

        db.commit()

        return {"strategy_id": strategy_id, "status": strategy.status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling strategy: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to toggle strategy") from e


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a MEV strategy"""
    try:
        strategy = (
            db.query(MEVStrategy)
            .filter(
                MEVStrategy.id == strategy_id, MEVStrategy.user_id == current_user.id
            )
            .first()
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found") from e

        db.delete(strategy)
        db.commit()

        return {"message": "Strategy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting strategy: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete strategy") from e
