"""
Admin routes for user management and system statistics
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.services.user_service import UserService
from database.cache_service import cache_service
from database.mongodb_client import MongoDBClient
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from config.settings import settings

# Configure logger
logger = logging.getLogger("api.routes.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])

# ---- Request/Response Models ----


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_admin: bool = False
    rate_limit: int = Field(default=100, ge=10, le=1000)


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_admin: bool
    rate_limit: int
    is_disabled: bool
    created_at: datetime
    api_key: Optional[str] = None


class ApiKeyRegenerateResponse(BaseModel):
    api_key: str


class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_contracts: int
    honeypots_detected: int
    analysis_count: int
    system_uptime: int


# ---- Helper Functions ----


async def get_user_service(request: Request) -> UserService:
    """Get user service instance from request state"""
    mongodb = MongoDBClient()
    if mongodb.db is None:
        await mongodb.connect()
    return UserService(mongodb)


async def admin_required(request: Request):
    """Check if user has admin privileges"""
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )

    return user


# ---- Routes ----


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
    admin_user: Dict = Depends(admin_required),
):
    """
    Create a new user (Admin only)

    Creates a new user account with the specified permissions and returns
    the user details including the generated API key.
    """
    try:
        created_user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            is_admin=user_data.is_admin,
            rate_limit=user_data.rate_limit,
        )

        # Convert ObjectId to string for response
        created_user["id"] = str(created_user.pop("_id"))

        logger.info(
            f"User created by admin {admin_user['username']}: {user_data.username}"
        )
        return created_user

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error creating user")


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    _: Dict = Depends(admin_required),
):
    """
    Get all users (Admin only)

    Returns a list of all users in the system, with pagination support.
    API keys are not included in the response.
    """
    users = await user_service.get_all_users(skip=skip, limit=limit)

    # Convert ObjectIds to strings
    for user in users:
        user["id"] = str(user.pop("_id"))
        # Don't expose API keys in listing
        user.pop("api_key", None)

    return users


@router.post("/users/{user_id}/regenerate-key", response_model=ApiKeyRegenerateResponse)
async def regenerate_api_key(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: Dict = Depends(admin_required),
):
    """
    Regenerate API key for a user (Admin only)

    Generates a new API key for the specified user and invalidates the old key.
    """
    new_api_key = await user_service.regenerate_api_key(user_id)

    if not new_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}"
        )

    logger.info(
        f"API key regenerated for user {user_id} by admin {admin_user['username']}"
    )
    return {"api_key": new_api_key}


@router.post("/users/{user_id}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: Dict = Depends(admin_required),
):
    """
    Disable a user account (Admin only)

    Disables the specified user account, preventing API access.
    """
    success = await user_service.disable_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}"
        )

    logger.info(f"User {user_id} disabled by admin {admin_user['username']}")
    return None


@router.post("/users/{user_id}/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: Dict = Depends(admin_required),
):
    """
    Enable a user account (Admin only)

    Enables a previously disabled user account, allowing API access.
    """
    success = await user_service.enable_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}"
        )

    logger.info(f"User {user_id} enabled by admin {admin_user['username']}")
    return None


@router.post("/users/{user_id}/rate-limit", status_code=status.HTTP_204_NO_CONTENT)
async def update_rate_limit(
    user_id: str,
    rate_limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    admin_user: Dict = Depends(admin_required),
):
    """
    Update user rate limit (Admin only)

    Updates the API rate limit for the specified user.
    """
    if rate_limit < 10 or rate_limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rate limit must be between 10 and 1000",
        )

    success = await user_service.update_rate_limit(user_id, rate_limit)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {user_id}"
        )

    logger.info(
        f"Rate limit updated for user {user_id} to {rate_limit} by admin {admin_user['username']}"
    )
    return None


@router.get("/system/stats", response_model=SystemStatsResponse)
async def get_system_stats(_: Dict = Depends(admin_required)):
    """
    Get system statistics (Admin only)

    Returns overall system statistics including user counts,
    contract analysis data, and system information.
    """
    try:
        # Get statistics from cache if available
        cached_stats = await cache_service.get("admin:system_stats")

        if cached_stats:
            return cached_stats

        # Otherwise gather statistics from various sources
        mongodb = MongoDBClient()
        if mongodb.db is None:
            await mongodb.connect()

        # User statistics
        users_coll = mongodb.db["users"]
        total_users = await users_coll.count_documents({})
        active_users = await users_coll.count_documents({"is_disabled": False})

        # Contract statistics
        contracts_coll = mongodb.db["contracts"]
        total_contracts = await contracts_coll.count_documents({})
        honeypot_contracts = await contracts_coll.count_documents(
            {"last_analysis.is_honeypot": True}
        )

        # Analysis statistics
        analyses_coll = mongodb.db["analyses"]
        analysis_count = await analyses_coll.count_documents({})

        # System uptime (placeholder, in production would use actual service uptime)
        import psutil

        system_uptime = int(psutil.boot_time())

        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "total_contracts": total_contracts,
            "honeypots_detected": honeypot_contracts,
            "analysis_count": analysis_count,
            "system_uptime": system_uptime,
        }

        # Cache for 5 minutes
        await cache_service.set("admin:system_stats", stats, ttl=300)

        return stats

    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Error retrieving system statistics"
        )


@router.post("/system/clear-cache", status_code=status.HTTP_200_OK)
async def clear_cache(cache_key_pattern: str = "*", _: Dict = Depends(admin_required)):
    """
    Clear cache entries (Admin only)

    Clears cache entries matching the specified pattern.
    Use with caution as this may affect system performance.
    """
    try:
        deleted_count = await cache_service.clear_pattern(cache_key_pattern)

        return {"deleted_keys": deleted_count, "pattern": cache_key_pattern}

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error clearing cache")
