"""
Enterprise authentication and RBAC
"""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Mock implementation - will be replaced with Keycloak integration
security = HTTPBearer()


class Organization(BaseModel):
    """Organization model"""

    id: str
    name: str
    plan: str = "enterprise"
    scan_quota: int = 10000
    scan_used: int = 0


class User(BaseModel):
    """User model"""

    id: str
    email: str
    org_id: str
    roles: list[str]


# Mock organizations for development
MOCK_ORGS = {
    "org_1": Organization(id="org_1", name="Acme Corp", plan="enterprise"),
    "org_2": Organization(id="org_2", name="Demo Inc", plan="professional"),
}


async def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    try:
        # Mock implementation - in production this validates JWT with Keycloak
        token = credentials.credentials

        # For development, accept any token and return mock user
        if token == "mock_token":
            return User(
                id="user_1", email="admin@example.com", org_id="org_1", roles=["admin"]
            )

        # In production: validate JWT token with Keycloak
        # payload = jwt.decode(token, verify=False)  # Keycloak validation
        # return User(**payload)

        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_org(user: User = Depends(get_current_user)) -> Organization:
    """Get current user's organization"""
    org = MOCK_ORGS.get(user.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def require_role(required_role: str):
    """Decorator to require specific role"""

    def role_checker(user: User = Depends(get_current_user)):
        if required_role not in user.roles:
            raise HTTPException(
                status_code=403, detail=f"Role '{required_role}' required"
            )
        return user

    return role_checker
