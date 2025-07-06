"""
Scorpius Reporting Service - Authentication Module
API key validation and user authentication
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from functools import lru_cache

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthError(Exception):
    """Authentication error"""
    pass


@lru_cache(maxsize=1000)
async def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify API key with auth service
    
    Args:
        api_key: API key to verify
        
    Returns:
        Dict with user information if valid, None if invalid
    """
    if not api_key:
        return None
    
    try:
        # In development, use mock authentication
        if settings.DEBUG and api_key.startswith("dev_"):
            return {
                "user_id": "dev_user",
                "username": "developer",
                "role": "admin",
                "permissions": ["read", "write", "admin"],
                "expires_at": None
            }
        
        # Call auth service for validation
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/v1/auth/verify",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "user_id": data.get("user_id"),
                    "username": data.get("username"),
                    "role": data.get("role"),
                    "permissions": data.get("permissions", []),
                    "expires_at": data.get("expires_at")
                }
            elif response.status_code == 401:
                logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
                return None
            else:
                logger.error(f"Auth service error: {response.status_code}")
                # In case of auth service failure, reject the request
                return None
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        return None
    except httpx.RequestError as e:
        logger.error(f"Auth service request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected auth error: {e}")
        return None


async def verify_user_permissions(user_data: Dict[str, Any], required_permission: str) -> bool:
    """
    Verify user has required permission
    
    Args:
        user_data: User data from verify_api_key
        required_permission: Required permission string
        
    Returns:
        True if user has permission, False otherwise
    """
    if not user_data:
        return False
    
    permissions = user_data.get("permissions", [])
    role = user_data.get("role", "")
    
    # Admin role has all permissions
    if role == "admin":
        return True
    
    # Check specific permission
    return required_permission in permissions


async def get_api_key_from_header(authorization_header: str) -> Optional[str]:
    """
    Extract API key from authorization header
    
    Args:
        authorization_header: Authorization header value
        
    Returns:
        API key if valid format, None otherwise
    """
    if not authorization_header:
        return None
    
    # Support both "Bearer" and "ApiKey" prefixes
    if authorization_header.startswith("Bearer "):
        return authorization_header[7:]
    elif authorization_header.startswith("ApiKey "):
        return authorization_header[7:]
    else:
        # Direct API key without prefix
        return authorization_header


class APIKeyManager:
    """API Key management for the reporting service"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def validate_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key with caching"""
        
        # Check cache first
        cache_key = f"api_key:{api_key}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now(timezone.utc).timestamp() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        # Verify with auth service
        user_data = await verify_api_key(api_key)
        
        # Cache result
        if user_data:
            self.cache[cache_key] = (user_data, datetime.now(timezone.utc).timestamp())
        
        return user_data
    
    def invalidate_cache(self, api_key: str = None):
        """Invalidate API key cache"""
        if api_key:
            cache_key = f"api_key:{api_key}"
            self.cache.pop(cache_key, None)
        else:
            self.cache.clear()


# Global API key manager instance
api_key_manager = APIKeyManager()


async def require_permission(permission: str):
    """Dependency for requiring specific permission"""
    def dependency(user_data: Dict[str, Any]):
        if not verify_user_permissions(user_data, permission):
            raise AuthError(f"Permission '{permission}' required")
        return user_data
    return dependency


async def require_role(role: str):
    """Dependency for requiring specific role"""
    def dependency(user_data: Dict[str, Any]):
        if user_data.get("role") != role:
            raise AuthError(f"Role '{role}' required")
        return user_data
    return dependency


# Mock functions for development/testing
async def mock_verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Mock API key verification for testing"""
    mock_keys = {
        "test_admin": {
            "user_id": "test_admin_user",
            "username": "test_admin",
            "role": "admin",
            "permissions": ["read", "write", "admin"],
            "expires_at": None
        },
        "test_user": {
            "user_id": "test_user_id",
            "username": "test_user",
            "role": "user",
            "permissions": ["read"],
            "expires_at": None
        },
        "test_reporter": {
            "user_id": "test_reporter_id",
            "username": "test_reporter",
            "role": "reporter",
            "permissions": ["read", "write"],
            "expires_at": None
        }
    }
    
    return mock_keys.get(api_key)


# Use mock authentication in test environment
if os.getenv("ENVIRONMENT") == "testing":
    verify_api_key = mock_verify_api_key
