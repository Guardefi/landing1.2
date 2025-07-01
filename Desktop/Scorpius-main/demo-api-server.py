#!/usr/bin/env python3
"""
Demo API Server for Scorpius Frontend
=====================================

A simple Flask server to handle login and basic API requests
for the Scorpius frontend demo.
"""

import time
from datetime import datetime, timedelta

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    origins=["http://localhost:3000", "https://*.scorpius.io"],
    supports_credentials=True,
)

# Demo configuration
JWT_SECRET = "demo-jwt-secret-key"
JWT_ALGORITHM = "HS256"


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "current_users": 12847,
            "security_level": "Elite",
            "uptime_percentage": "99.97%",
            "total_nodes": 127,
        }
    )


@app.route("/auth/login", methods=["POST"])
def login():
    """Login endpoint - accepts any credentials for demo."""
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify(
            {"success": False, "error": "Email and password required"}), 400

    email = data.get("email", "")

    # Determine user role based on email
    if "admin" in email.lower():
        roles = ["admin", "user"]
        permissions = ["scan", "analyze", "admin", "manage_users"]
        subscription_tier = "enterprise"
    elif "enterprise" in email.lower():
        roles = ["user"]
        permissions = ["scan", "analyze", "advanced_features"]
        subscription_tier = "enterprise"
    elif "pro" in email.lower():
        roles = ["user"]
        permissions = ["scan", "analyze", "pro_features"]
        subscription_tier = "pro"
    else:
        roles = ["user"]
        permissions = ["scan", "analyze"]
        subscription_tier = "free"

    # Create JWT token
    payload = {
        "sub": f"user_{int(time.time())}",
        "email": email,
        "username": email.split("@")[0],
        "roles": roles,
        "permissions": permissions,
        "subscription_tier": subscription_tier,
        "is_active": True,
        "is_verified": True,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify(
        {
            "success": True,
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 86400,
            },
        }
    )


@app.route("/auth/refresh", methods=["POST"])
def refresh_token():
    """Refresh token endpoint."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Invalid token"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Create new token
        new_payload = {
            **payload,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }

        new_token = jwt.encode(
            new_payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM)

        return jsonify(
            {
                "success": True,
                "data": {
                    "access_token": new_token,
                    "token_type": "bearer",
                    "expires_in": 86400,
                },
            }
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Invalid token"}), 401


@app.route("/auth/me", methods=["GET"])
def get_user_profile():
    """Get current user profile."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify(
            {"success": False, "error": "Authentication required"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        user_data = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "firstName": "Demo",
            "lastName": "User",
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
            "subscription_tier": payload.get("subscription_tier", "free"),
            "isActive": payload.get("is_active", True),
            "isVerified": payload.get("is_verified", True),
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
            "subscription": {
                "tier": payload.get("subscription_tier", "free"),
                "features": ["basic_scan", "real_time_monitoring"],
                "expiresAt": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            },
        }

        return jsonify({"success": True, "data": user_data})

    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "Invalid token"}), 401


@app.route("/auth/csrf", methods=["GET"])
def get_csrf_token():
    """Get CSRF token."""
    return jsonify({"csrf_token": f"csrf_{int(time.time())}"})


# Catch-all for other API endpoints


@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def api_fallback(path):
    """Fallback for other API endpoints."""
    return jsonify(
        {
            "success": True,
            "message": f"Demo API endpoint: /{path}",
            "data": {"demo": True, "timestamp": datetime.utcnow().isoformat()},
        }
    )


if __name__ == "__main__":
    print("🚀 Starting Scorpius Demo API Server")
    print("📝 Available endpoints:")
    print("   • POST /auth/login - Login with any credentials")
    print("   • GET /health - Health check")
    print("   • GET /auth/me - Get user profile")
    print("   • POST /auth/refresh - Refresh token")
    print("🔗 Frontend should connect to: http://localhost:8000")

    app.run(host="0.0.0.0", port=8000, debug=True)
