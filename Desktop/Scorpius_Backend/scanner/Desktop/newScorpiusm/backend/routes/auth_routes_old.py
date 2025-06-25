"""
Authentication Routes Module
Handles user authentication, login, logout, and JWT token management
"""

import hashlib
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import User, get_db

# Create blueprint
auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login endpoint - Enhanced with better security"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid request body",
                        "timestamp": datetime.now().isoformat() + "Z",
                    }
                ),
                400,
            )

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username and password are required",
                        "timestamp": datetime.now().isoformat() + "Z",
                    }
                ),
                400,
            )

        db = get_db()

        # Find user in database
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid username or password",
                        "timestamp": datetime.now().isoformat() + "Z",
                    }
                ),
                401,
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid username or password",
                        "timestamp": datetime.now().isoformat() + "Z",
                    }
                ),
                401,
            )

        # Update last login
        user.last_login = datetime.now()
        db.commit()  # Create access token
        access_token = create_access_token(identity=str(user.id))
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "access_token": access_token,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role,
                            "isActive": user.is_active,
                        },
                    },
                    "timestamp": datetime.now().isoformat() + "Z",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An error occurred during login",
                    "timestamp": datetime.now().isoformat() + "Z",
                }
            ),
            500,
        )


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request body"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username, email, and password are required",
                    }
                ),
                400,
            )

        db = get_db()

        # Check if user already exists
        existing_user = (
            db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )

        if existing_user:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "User with this username or email already exists",
                    }
                ),
                409,
            )

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="user",
            is_active=True,
            created_at=datetime.now(),
        )

        db.add(user)
        db.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role,
                        }
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback() if "db" in locals() else None
        return (
            jsonify(
                {"success": False, "message": "An error occurred during registration"}
            ),
            500,
        )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        current_user = get_jwt_identity()

        # TODO: Get user data from your database
        # user_data = get_user_by_username(current_user)

        # Enhanced user data
        role = "admin" if current_user in ["demo", "admin"] else "user"
        permissions = (
            ["scan:execute", "mev:manage", "system:admin"]
            if role == "admin"
            else ["scan:view"]
        )

        user_data = {
            "id": str(hash(current_user) % 10000),
            "username": current_user,
            "email": f"{current_user}@scorpius.io",
            "role": role,
            "permissions": permissions,
            "preferences": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "push": True,
                    "criticalThreats": True,
                    "mevOpportunities": True,
                    "systemAlerts": True,
                },
                "dashboard": {
                    "refreshInterval": 30000,
                    "defaultCharts": ["threats", "performance"],
                    "layout": "expanded",
                },
            },
            "lastLoginAt": datetime.now().isoformat() + "Z",
            "createdAt": "2023-12-01T00:00:00.000Z",
            "updatedAt": datetime.now().isoformat() + "Z",
        }

        return jsonify(
            {
                "success": True,
                "data": user_data,
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to get user information",
                    "timestamp": datetime.now().isoformat() + "Z",
                }
            ),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout endpoint"""
    try:
        current_user = get_jwt_identity()
        logger.info(f"User {current_user} logged out")

        return jsonify(
            {
                "success": True,
                "message": "Logged out successfully",
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Logout failed",
                    "timestamp": datetime.now().isoformat() + "Z",
                }
            ),
            500,
        )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_token():
    """Refresh JWT token"""
    try:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)

        return jsonify(
            {
                "success": True,
                "data": {"accessToken": new_token, "expiresIn": 86400},
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Token refresh failed",
                    "timestamp": datetime.now().isoformat() + "Z",
                }
            ),
            500,
        )
