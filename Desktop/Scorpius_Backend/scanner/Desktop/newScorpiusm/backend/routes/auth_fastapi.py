"""
Authentication FastAPI Routes Module
Handles user authentication, registration, and JWT token management
"""

import hashlib
import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import Session, User, get_db
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


# ───────────────────────────────
# Pydantic models
# ───────────────────────────────
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    last_login: datetime | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# ───────────────────────────────
# Helpers
# ───────────────────────────────
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a random salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against stored salt+hash combo."""
    try:
        salt, hash_value = hashed_password.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except ValueError:
        return False


def generate_token(user_id: int) -> str:
    """Naïve token generator – replace with JWT in production."""
    token_data = f"{user_id}:{datetime.utcnow().timestamp()}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()


# ───────────────────────────────
# Routes
# ───────────────────────────────
@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    """Register a new user account."""
    try:
        # Duplicate-check (username OR e-mail)
        existing_user = (
            db.query(User)
            .filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
            .first()
        )
        if existing_user:
            msg = (
                "Username already registered"
                if existing_user.username == user_data.username
                else "Email already registered"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        # Create and persist user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return TokenResponse(
            access_token=generate_token(new_user.id),
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                full_name=new_user.full_name,
                is_active=new_user.is_active,
                created_at=new_user.created_at,
                last_login=new_user.last_login,
            ),
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:  # noqa: BLE001
        logger.exception("Error registering user")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from e


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return an access token."""
    try:
        user = db.query(User).filter(User.username == login_data.username).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive"
            )

        user.last_login = datetime.utcnow()
        db.commit()

        return TokenResponse(
            access_token=generate_token(user.id),
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login,
            ),
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:  # noqa: BLE001
        logger.exception("Error during login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Dummy token validation – replace with real JWT verification."""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.is_active).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:  # noqa: BLE001
        logger.exception("Error validating token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Return the current user profile."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update mutable profile fields."""
    try:
        if "full_name" in profile_data:
            current_user.full_name = profile_data["full_name"]

        if "email" in profile_data:
            clash = (
                db.query(User)
                .filter(User.email == profile_data["email"], User.id != current_user.id)
                .first()
            )
            if clash:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken",
                )
            current_user.email = profile_data["email"]

        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:  # noqa: BLE001
        logger.exception("Error updating profile")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        ) from e


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    try:
        if not verify_password(
            password_data.current_password, current_user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        current_user.password_hash = hash_password(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        return {"message": "Password changed successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:  # noqa: BLE001
        logger.exception("Error changing password")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        ) from e


@router.post("/forgot-password")
async def forgot_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Handle a forgotten-password request (placeholder)."""
    try:
        user = db.query(User).filter(User.email == reset_data.email).first()
        if user:
            logger.info("Password reset requested for user %s", user.username)
        # Always respond the same to avoid user enumeration
        return {"message": "If the email exists, a reset link has been sent"}

    except Exception as e:  # noqa: BLE001
        logger.exception("Error processing password reset")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset",
        ) from e


@router.post("/logout")
async def logout_user(_: User = Depends(get_current_user)):
    """Invalidate token (stub)."""
    return {"message": "Logged out successfully"}


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Check if the supplied token is still valid."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
    }
