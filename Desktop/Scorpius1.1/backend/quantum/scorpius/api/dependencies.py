"""
Dependencies and utilities for Scorpius API endpoints.
Separated to avoid circular imports between main.py and dashboard.py.
"""

from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import ScorpiusEngine, get_engine
from ..exceptions import ScorpiusError

# Security
security = HTTPBearer()

# Global state
scorpius_initialized = False


def set_scorpius_initialized(status: bool):
    """Set the global initialization status."""
    global scorpius_initialized
    scorpius_initialized = status


def is_scorpius_initialized() -> bool:
    """Check if Scorpius is initialized."""
    return scorpius_initialized


async def get_scorpius_engine() -> ScorpiusEngine:
    """Get the Scorpius engine instance."""
    if not scorpius_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scorpius platform not initialized",
        )
    try:
        return get_engine()
    except ScorpiusError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Validate authentication token."""
    # TODO: Implement actual token validation
    if credentials.credentials == "demo-token":
        return {"user_id": "demo", "role": "admin"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )
