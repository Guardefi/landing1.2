"""
Authentication utilities for usage metering service
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import HTTPException

from .config import get_settings

settings = get_settings()


def verify_token(token: str) -> Dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")

        # Ensure org_id is present
        if not payload.get("org_id"):
            raise HTTPException(status_code=401, detail="Invalid token: missing org_id")

        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_token(
    org_id: str,
    user_id: str,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT token for testing purposes"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "org_id": org_id,
        "user_id": user_id,
        "role": role,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_admin_role(payload: Dict) -> bool:
    """Check if user has admin role"""
    role = payload.get("role", "user")
    return role in ["admin", "billing_admin"]
