"""Authentication endpoints for Scorpius X."""

import time

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Hardcoded credentials for demonstration
# In production, use a secure database with hashed passwords
VALID_USERS = {
    "admin@scorpiusx.io": {
        "password": "scorpius123",
        "role": "admin",
        "name": "Admin",
        "avatar": "🦂",
    }
}


class LoginRequest(BaseModel):
    email: str
    password: str


class User(BaseModel):
    email: str
    role: str
    name: str
    avatar: str
    token: str


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate a user."""
    try:
        if request.email not in VALID_USERS:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_data = VALID_USERS[request.email]
        if request.password != user_data["password"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate a simple token (use JWT in production)
        token = f"{request.email}:{int(time.time())}"

        return {
            "success": True,
            "user": {
                "email": request.email,
                "role": user_data["role"],
                "name": user_data["name"],
                "avatar": user_data["avatar"],
                "token": token,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed") from e


@router.get("/me")
async def get_current_user(token: str | None = None):
    """Get current user from token."""
    try:
        if not token:
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

            raise HTTPException(status_code=401, detail="Not authenticated")) from e

        # Parse the simple token
        email, _ = token.split(":", 1)
        if email not in VALID_USERS:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_data = VALID_USERS[email]
        return {
            "email": email,
            "role": user_data["role"],
            "name": user_data["name"],
            "avatar": user_data["avatar"],
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
