"""
Models for Enterprise Authentication
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RoleEnum(str, Enum):
    """Available user roles"""

    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"
    BILLING_ADMIN = "billing_admin"


class User(BaseModel):
    """User model"""

    id: str
    email: str
    name: str
    org_id: str
    roles: List[RoleEnum]
    is_active: bool = True


class Organization(BaseModel):
    """Organization model"""

    id: str
    name: str
    plan: str = "enterprise"
    scan_quota: int = 10000
    scan_used: int = 0
    is_active: bool = True


class Role(BaseModel):
    """Role definition"""

    name: RoleEnum
    permissions: List[str]
    description: str


class TokenResponse(BaseModel):
    """OAuth token response"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: User


class LoginRequest(BaseModel):
    """Login request"""

    username: str
    password: str


class Permission(BaseModel):
    """Permission model"""

    resource: str
    action: str
    conditions: Optional[dict] = None
