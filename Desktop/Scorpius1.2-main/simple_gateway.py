#!/usr/bin/env python3
"""
Simple API Gateway for Scorpius Platform
Handles CORS and routes requests to backend services
"""
import asyncio
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import hashlib
import secrets
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scorpius API Gateway", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3010", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:3010",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend service mappings
BACKEND_SERVICES = {
    "integration-hub": "http://localhost:8014",
    "bytecode": "http://localhost:8000",  # Container port
    "bridge": "http://localhost:8000",    # Container port
    "time-machine": "http://localhost:8000",  # Container port
    "mempool": "http://localhost:8000",   # Container port
    "quantum": "http://localhost:8000",   # Container port
    "honeypot": "http://localhost:8000",  # Container port
    "slither": "http://localhost:8002",
    "manticore": "http://localhost:8005",
    "mythril": "http://localhost:8003",
    "mythx": "http://localhost:8004",
}

# Simple in-memory user store (for demo purposes) - now using email as key
users_db = {}
sessions_db = {}

# Pydantic models
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{pwd_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, pwd_hash = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False

def create_token(email: str) -> str:
    """Create a simple JWT-like token"""
    payload = {
        "email": email,
        "exp": int(time.time()) + 3600,  # 1 hour expiry
        "iat": int(time.time())
    }
    token = secrets.token_urlsafe(32)
    sessions_db[token] = payload
    return token

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "API Gateway"
    }

@app.get("/services")
async def list_services():
    """List available backend services"""
    return {
        "services": list(BACKEND_SERVICES.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/register")
async def register_user(request: Request):
    """Register a new user with email and password only"""
    try:
        # Log the raw request for debugging
        body = await request.body()
        logger.info(f"Registration request body: {body}")
        logger.info(f"Registration request headers: {dict(request.headers)}")
        
        # Parse the JSON manually to get better error handling
        try:
            data = json.loads(body)
            logger.info(f"Parsed registration data: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required fields - only email and password are mandatory
        required_fields = ["email", "password"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing required fields: {missing_fields}")
        
        email = data["email"]
        password = data["password"]
        
        # Handle full_name from frontend format (firstName + lastName) or fallback
        full_name = data.get("full_name")
        if not full_name:
            first_name = data.get("firstName", "")
            last_name = data.get("lastName", "")
            full_name = f"{first_name} {last_name}".strip() or email.split("@")[0]
        
        # Check if user already exists (using email as primary key)
        if email in users_db:
            logger.warning(f"User registration failed: User with email {email} already exists")
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password and store user
        hashed_password = hash_password(password)
        users_db[email] = {
            "email": email,
            "password": hashed_password,
            "full_name": full_name,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "role": "user",
            "tier": "free",
            "subscription": {
                "tier": "free",
                "features": [],
                "status": "active"
            }
        }
        
        # Create token
        token = create_token(email)
        
        response_data = {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": email,
                "full_name": full_name,
                "role": "user",
                "tier": "free",
                "subscription": {
                    "tier": "free",
                    "features": [],
                    "status": "active"
                }
            }
        }
        
        logger.info(f"User {email} registered successfully")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.options("/auth/register")
async def register_options():
    """Handle OPTIONS request for CORS"""
    return JSONResponse(content={}, headers={"Access-Control-Allow-Methods": "POST, OPTIONS"})

@app.post("/auth/login")
async def login_user(request: Request):
    """Login user with email and password"""
    try:
        # Log the raw request for debugging
        body = await request.body()
        logger.info(f"Login request body: {body}")
        
        # Parse the JSON manually to get better error handling
        try:
            data = json.loads(body)
            logger.info(f"Parsed login data: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required fields
        required_fields = ["email", "password"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing required fields: {missing_fields}")
        
        email = data["email"]
        password = data["password"]
        
        # Check if user exists
        if email not in users_db:
            logger.warning(f"Login failed: User with email {email} not found")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = users_db[email]
        
        # Verify password
        if not verify_password(password, user["password"]):
            logger.warning(f"Login failed: Invalid password for user {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_token(email)
        
        response_data = {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user.get("role", "user"),
                "tier": user.get("tier", "free"),
                "subscription": user.get("subscription", {
                    "tier": "free",
                    "features": [],
                    "status": "active"
                })
            }
        }
        
        logger.info(f"User {email} logged in successfully")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.options("/auth/login")
async def login_options():
    """Handle OPTIONS request for CORS"""
    return JSONResponse(content={}, headers={"Access-Control-Allow-Methods": "POST, OPTIONS"})

@app.get("/auth/me")
async def get_current_user(request: Request):
    """Get current user info from token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.replace("Bearer ", "")
        
        # Verify token
        if token not in sessions_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        session = sessions_db[token]
        
        # Check if token is expired
        if session["exp"] < int(time.time()):
            del sessions_db[token]
            raise HTTPException(status_code=401, detail="Token expired")
        
        email = session["email"]
        
        # Get user info
        if email not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = users_db[email]
        
        return {
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "role": user.get("role", "user"),
            "tier": user.get("tier", "free"),
            "subscription": user.get("subscription", {
                "tier": "free",
                "features": [],
                "status": "active"
            })
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_user_from_token(request: Request):
    """Get user from authorization token"""
    auth_header = request.headers.get("Authorization")
    logger.info(f"Authorization header: {auth_header}")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"Missing or invalid authorization header: {auth_header}")
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.replace("Bearer ", "")
    logger.info(f"Extracted token: {token[:20]}...")
    
    # Verify token
    if token not in sessions_db:
        logger.warning(f"Invalid token: {token[:20]}... not found in sessions")
        logger.info(f"Active sessions: {list(sessions_db.keys())}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session = sessions_db[token]
    
    # Check if token is expired
    if session["exp"] < int(time.time()):
        logger.warning(f"Token expired for user {session['email']}")
        del sessions_db[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    email = session["email"]
    
    # Get user info
    if email not in users_db:
        logger.warning(f"User {email} not found in database")
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.info(f"Token validation successful for user {email}")
    return users_db[email]

@app.get("/subscription")
async def get_subscription(request: Request):
    """Get current user's subscription info"""
    try:
        user = get_user_from_token(request)
        
        return {
            "tier": user.get("tier", "free"),
            "status": "active",
            "features": user.get("subscription", {}).get("features", []),
            "limits": {
                "scans_per_month": 1000 if user.get("tier") == "enterprise" else 100,
                "advanced_analytics": user.get("tier") == "enterprise",
                "priority_support": user.get("tier") == "enterprise"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get subscription error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/subscription/upgrade")
async def upgrade_subscription(request: Request):
    """Upgrade user to enterprise tier"""
    try:
        user = get_user_from_token(request)
        email = user["email"]
        
        # Update user to enterprise tier
        users_db[email]["tier"] = "enterprise"
        users_db[email]["subscription"] = {
            "tier": "enterprise",
            "features": ["advanced-analytics", "priority-support", "unlimited-scans"],
            "status": "active"
        }
        
        logger.info(f"User {email} upgraded to enterprise tier")
        
        return {
            "success": True,
            "message": "Successfully upgraded to enterprise tier",
            "tier": "enterprise",
            "features": ["advanced-analytics", "priority-support", "unlimited-scans"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upgrade subscription error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.options("/subscription")
async def subscription_options():
    """Handle OPTIONS request for CORS"""
    return JSONResponse(content={}, headers={"Access-Control-Allow-Methods": "GET, OPTIONS"})

@app.options("/subscription/upgrade")
async def subscription_upgrade_options():
    """Handle OPTIONS request for CORS"""
    return JSONResponse(content={}, headers={"Access-Control-Allow-Methods": "POST, OPTIONS"})

@app.post("/admin/upgrade-user")
async def admin_upgrade_user(request: Request):
    """Admin endpoint to upgrade specific user to enterprise"""
    try:
        body = await request.body()
        data = json.loads(body)
        
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        if email not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user to enterprise tier
        users_db[email]["tier"] = "enterprise"
        users_db[email]["role"] = "admin"
        users_db[email]["subscription"] = {
            "tier": "enterprise",
            "features": ["advanced-analytics", "priority-support", "unlimited-scans", "api-access"],
            "status": "active"
        }
        
        logger.info(f"Admin upgraded user {email} to enterprise tier")
        
        return {
            "success": True,
            "message": f"Successfully upgraded {email} to enterprise tier",
            "user": {
                "email": email,
                "tier": "enterprise",
                "role": "admin",
                "features": ["advanced-analytics", "priority-support", "unlimited-scans", "api-access"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin upgrade user error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Proxy requests to backend services"""
    
    if service not in BACKEND_SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    service_url = BACKEND_SERVICES[service]
    target_url = f"{service_url}/{path}"
    
    # Handle query parameters
    query_params = str(request.url.query)
    if query_params:
        target_url += f"?{query_params}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Get request body if present
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]},
                content=body,
                timeout=30.0
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request to {target_url} failed: {e}")
            raise HTTPException(status_code=503, detail=f"Service '{service}' unavailable")
        except Exception as e:
            logger.error(f"Unexpected error proxying to {target_url}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Scorpius API Gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": list(BACKEND_SERVICES.keys())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 