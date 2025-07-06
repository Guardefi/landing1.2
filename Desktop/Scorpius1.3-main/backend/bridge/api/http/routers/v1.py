"""Version 1 API routes for Scorpius Bridge.

Legacy API endpoints for backward compatibility.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_bridge_service, get_current_user, rate_limit
from ..schemas.bridge import BridgeTransferResponse, InitiateTransferRequest

router = APIRouter(
    prefix="/bridge", tags=["Bridge V1"], dependencies=[Depends(rate_limit)]
)


@router.post("/transfer", response_model=BridgeTransferResponse)
async def initiate_transfer(
    request: InitiateTransferRequest,
    bridge_service=Depends(get_bridge_service),
    current_user=Depends(get_current_user),
) -> BridgeTransferResponse:
    """Initiate a new bridge transfer (V1 API)."""
    try:
        transfer_id = await bridge_service.initiate_transfer(request.to_command())
        return BridgeTransferResponse(
            transfer_id=transfer_id,
            status="initiated",
            message="Transfer initiated successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/transfer/{transfer_id}")
async def get_transfer(
    transfer_id: str,
    bridge_service=Depends(get_bridge_service),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """Get transfer details (V1 API)."""
    # Implementation would go here
    return {"transfer_id": transfer_id, "status": "placeholder"}


@router.get("/transfers")
async def list_transfers(
    limit: int = 50,
    offset: int = 0,
    bridge_service=Depends(get_bridge_service),
    current_user=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """List user transfers (V1 API)."""
    # Implementation would go here
    return []
