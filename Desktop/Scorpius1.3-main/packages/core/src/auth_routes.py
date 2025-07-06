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
        db.commit()

        # Create access token
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
        if "db" in locals():
            db.rollback()
        return (
            jsonify(
                {"success": False, "message": "An error occurred during registration"}
            ),
            500,
        )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        db = get_db()

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify(
            {
                "success": True,
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "isActive": user.is_active,
                        "createdAt": (
                            user.created_at.isoformat() + "Z"
                            if user.created_at
                            else None
                        ),
                        "lastLogin": (
                            user.last_login.isoformat() + "Z"
                            if user.last_login
                            else None
                        ),
                    }
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return (
            jsonify(
                {"success": False, "message": "Failed to retrieve user information"}
            ),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout endpoint"""
    try:
        # In a more complete implementation, you would blacklist the token
        return jsonify(
            {
                "success": True,
                "message": "Logged out successfully",
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({"success": False, "message": "Failed to logout"}), 500


@auth_bp.route("/validate", methods=["POST"])
@jwt_required()
def validate_token():
    """Validate JWT token"""
    try:
        user_id = get_jwt_identity()

        return jsonify(
            {
                "success": True,
                "message": "Token is valid",
                "data": {"userId": user_id, "isValid": True},
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({"success": False, "message": "Invalid token"}), 401
