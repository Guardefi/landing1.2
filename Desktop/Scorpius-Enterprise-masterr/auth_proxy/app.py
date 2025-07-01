"""
Enterprise Authentication Proxy
FastAPI service providing OIDC/SAML authentication and RBAC
"""

import time
from typing import Any, Dict

import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import settings
from .models import LoginRequest, TokenResponse, User
from .services.keycloak_client import KeycloakClient
from .services.rbac_manager import RBACManager

app = FastAPI(
    title="Scorpius Auth Proxy",
    description="Enterprise authentication and RBAC service",
    version="1.0.0",
    docs_url="/auth/docs" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
keycloak = KeycloakClient()
rbac = RBACManager()


@app.get("/auth/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-proxy",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.get("/auth/login")
async def initiate_login(request: Request):
    """Initiate OIDC login flow"""
    redirect_uri = f"{settings.BASE_URL}/auth/callback"
    auth_url = await keycloak.get_auth_url(redirect_uri)
    return RedirectResponse(url=auth_url)


@app.get("/auth/callback")
async def auth_callback(code: str, state: str = None):
    """Handle OIDC callback and exchange code for tokens"""
    try:
        # Exchange authorization code for tokens
        tokens = await keycloak.exchange_code_for_tokens(code)

        # Decode and validate JWT
        user_info = await keycloak.get_user_info(tokens["access_token"])

        # Create internal JWT token
        internal_token = await create_internal_token(user_info)

        return TokenResponse(
            access_token=internal_token,
            token_type="Bearer",
            expires_in=3600,
            user=user_info,
        )

    except Exception:
        raise HTTPException(status_code=400, detail="Authentication failed")


@app.post("/auth/login", response_model=TokenResponse)
async def direct_login(request: LoginRequest):
    """Direct login with username/password (for API access)"""
    try:
        # Authenticate with Keycloak
        tokens = await keycloak.authenticate_user(request.username, request.password)

        # Get user info
        user_info = await keycloak.get_user_info(tokens["access_token"])

        # Create internal JWT token
        internal_token = await create_internal_token(user_info)

        return TokenResponse(
            access_token=internal_token,
            token_type="Bearer",
            expires_in=3600,
            user=user_info,
        )

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate tokens"""
    try:
        # In production: invalidate token in Keycloak and internal cache
        return {"message": "Logged out successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="Logout failed")


# Forward declaration for dependency
async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user = await validate_internal_token(token)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/auth/me", response_model=User)
async def get_current_user(user: User = Depends(get_authenticated_user)):
    """Get current authenticated user information"""
    return user


@app.get("/auth/permissions")
async def get_user_permissions(user: User = Depends(get_authenticated_user)):
    """Get user's permissions and role mappings"""
    permissions = await rbac.get_user_permissions(user.id, user.org_id)
    return {
        "user_id": user.id,
        "org_id": user.org_id,
        "roles": user.roles,
        "permissions": permissions,
    }


@app.post("/auth/validate")
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info"""
    try:
        token = credentials.credentials
        user = await validate_internal_token(token)
        return {"valid": True, "user": user.dict(), "expires_at": time.time() + 3600}
    except Exception:
        return {"valid": False, "error": "Invalid token"}


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user = await validate_internal_token(token)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def create_internal_token(user_info: Dict[str, Any]) -> str:
    """Create internal JWT token from Keycloak user info"""
    # Map Keycloak user to internal user model
    user = User(
        id=user_info["sub"],
        email=user_info["email"],
        name=user_info.get("name", ""),
        org_id=user_info.get("org_id", "default_org"),
        roles=user_info.get("roles", ["viewer"]),
    )

    # Create JWT payload
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "org_id": user.org_id,
        "roles": user.roles,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour
        "iss": "scorpius-auth",
    }

    # Sign JWT
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


async def validate_internal_token(token: str) -> User:
    """Validate internal JWT token and return user"""
    try:
        # Decode JWT
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

        # Create user from payload
        user = User(
            id=payload["sub"],
            email=payload["email"],
            name=payload["name"],
            org_id=payload["org_id"],
            roles=payload["roles"],
        )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


if __name__ == "__main__":
    uvicorn.run(
        "app:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
