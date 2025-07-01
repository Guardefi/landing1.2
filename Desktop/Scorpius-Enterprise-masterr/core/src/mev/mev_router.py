"""MEV Bot router extensions (strategies list)."""

router = APIRouter(prefix="/mev", tags=["MEV"])


@router.get("/strategies")
async def list_strategies():
    return [
        {"name": "Sandwich V2", "enabled": True},
        {"name": "Liquidation Aave", "enabled": False},
        {"name": "JIT Liquidity", "enabled": True},
    ]
