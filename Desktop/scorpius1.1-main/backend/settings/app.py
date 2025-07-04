#!/usr/bin/env python3
"""
Scorpius Settings Service
Manages environment variables and configuration for all Scorpius modules
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from dotenv import load_dotenv, set_key, unset_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("settings_service")

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Scorpius Settings Service",
    description="Comprehensive configuration management for the Scorpius platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Environment file path
ENV_FILE_PATH = Path(".env")
if not ENV_FILE_PATH.exists():
    ENV_FILE_PATH = Path("/app/.env")

class ConfigCategory(BaseModel):
    """Configuration category definition"""
    name: str
    description: str
    icon: str
    order: int

class ConfigVariable(BaseModel):
    """Configuration variable definition"""
    key: str
    value: Optional[str] = None
    default_value: Optional[str] = None
    description: str
    category: str
    is_public: bool = False
    is_required: bool = False
    is_secret: bool = False
    data_type: str = "string"  # string, number, boolean, url, email
    validation_pattern: Optional[str] = None
    options: Optional[List[str]] = None  # For select dropdowns

class ConfigUpdate(BaseModel):
    """Configuration update request"""
    updates: Dict[str, Any]

class SettingsResponse(BaseModel):
    """Settings API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# Configuration schema - defines all Scorpius settings
SETTINGS_SCHEMA = {
    "categories": [
        {"name": "blockchain", "description": "Blockchain RPC Endpoints", "icon": "link", "order": 1},
        {"name": "mev", "description": "MEV & Mempool Configuration", "icon": "zap", "order": 2},
        {"name": "analysis", "description": "Static & Dynamic Analysis", "icon": "search", "order": 3},
        {"name": "ai", "description": "AI & LLM Engines", "icon": "brain", "order": 4},
        {"name": "bridge", "description": "Bridge Intelligence", "icon": "shuffle", "order": 5},
        {"name": "wallet", "description": "Wallet Guard Options", "icon": "shield", "order": 6},
        {"name": "reporting", "description": "Reporting & Exports", "icon": "file-text", "order": 7},
        {"name": "notifications", "description": "Observability & Notifications", "icon": "bell", "order": 8},
        {"name": "infrastructure", "description": "Database & Cache", "icon": "server", "order": 9},
        {"name": "frontend", "description": "Frontend Configuration", "icon": "monitor", "order": 10},
    ],
    "variables": [
        # === BLOCKCHAIN RPC ENDPOINTS ===
        {
            "key": "RPC_ETH_MAIN",
            "description": "Ethereum Mainnet RPC endpoint",
            "category": "blockchain",
            "is_required": True,
            "data_type": "url",
            "default_value": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
        },
        {
            "key": "RPC_ARB_ONE", 
            "description": "Arbitrum One RPC endpoint",
            "category": "blockchain",
            "data_type": "url",
            "default_value": "https://arb-mainnet.g.alchemy.com/v2/YOUR_PROJECT_ID"
        },
        {
            "key": "RPC_POLYGON",
            "description": "Polygon Mainnet RPC endpoint", 
            "category": "blockchain",
            "data_type": "url",
            "default_value": "https://polygon-mainnet.g.alchemy.com/v2/YOUR_PROJECT_ID"
        },
        {
            "key": "RPC_BSC",
            "description": "BSC Mainnet WebSocket endpoint",
            "category": "blockchain", 
            "data_type": "url",
            "default_value": "wss://bsc-mainnet.nodereal.io/ws/v1/YOUR_PROJECT_ID"
        },
        {
            "key": "RPC_BASE",
            "description": "Base Mainnet RPC endpoint",
            "category": "blockchain",
            "data_type": "url", 
            "default_value": "https://base-mainnet.g.alchemy.com/v2/YOUR_PROJECT_ID"
        },
        {
            "key": "PUBLIC_RPC_ETH_MAIN",
            "description": "Public Ethereum RPC for frontend",
            "category": "blockchain",
            "is_public": True,
            "data_type": "url"
        },
        {
            "key": "PUBLIC_RPC_ARB_ONE", 
            "description": "Public Arbitrum RPC for frontend",
            "category": "blockchain",
            "is_public": True,
            "data_type": "url"
        },
        
        # === MEV / MEMPOOL ===
        {
            "key": "FLASHBOTS_SIGNER_KEY",
            "description": "Flashbots signer private key",
            "category": "mev",
            "is_secret": True,
            "data_type": "string",
            "validation_pattern": "^0x[a-fA-F0-9]{64}$"
        },
        {
            "key": "MEV_SHARE_JWT",
            "description": "MEV Share JWT token",
            "category": "mev", 
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "EDEN_API_KEY",
            "description": "Eden Network API key (optional)",
            "category": "mev",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "BLOCKNATIVE_API_KEY",
            "description": "Blocknative API key (optional)",
            "category": "mev",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "BLOXROUTE_API_KEY",
            "description": "BloxRoute API key (optional)",
            "category": "mev",
            "is_secret": True,
            "data_type": "string"
        },
        
        # === ANALYSIS ===
        {
            "key": "ETHERSCAN_KEY",
            "description": "Etherscan API key",
            "category": "analysis",
            "is_secret": True,
            "is_required": True,
            "data_type": "string"
        },
        {
            "key": "ARBISCAN_KEY",
            "description": "Arbiscan API key",
            "category": "analysis", 
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "POLYGONSCAN_KEY",
            "description": "Polygonscan API key",
            "category": "analysis",
            "is_secret": True, 
            "data_type": "string"
        },
        {
            "key": "BSC_SCAN_KEY",
            "description": "BSC Scan API key",
            "category": "analysis",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "COINGECKO_BASE",
            "description": "CoinGecko API base URL",
            "category": "analysis",
            "is_public": True,
            "data_type": "url",
            "default_value": "https://api.coingecko.com"
        },
        {
            "key": "DEX_SCREENER_BASE",
            "description": "DexScreener API base URL",
            "category": "analysis",
            "is_public": True,
            "data_type": "url",
            "default_value": "https://api.dexscreener.com/latest/dex"
        },
        
        # === AI / LLM ===
        {
            "key": "OPENAI_API_KEY",
            "description": "OpenAI API key",
            "category": "ai",
            "is_secret": True,
            "is_required": True,
            "data_type": "string",
            "validation_pattern": "^sk-[a-zA-Z0-9\\-_]+"
        },
        {
            "key": "OPENAI_MODEL",
            "description": "OpenAI model to use",
            "category": "ai",
            "is_public": True,
            "data_type": "string",
            "default_value": "gpt-4o-2025-06",
            "options": ["gpt-4o-2025-06", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        {
            "key": "CLAUDE_API_KEY",
            "description": "Claude API key",
            "category": "ai",
            "is_secret": True,
            "data_type": "string",
            "validation_pattern": "^sk-ant-[a-zA-Z0-9\\-_]+"
        },
        {
            "key": "CLAUDE_MODEL",
            "description": "Claude model to use",
            "category": "ai",
            "is_public": True,
            "data_type": "string",
            "default_value": "claude-3-opus-20240229",
            "options": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        },
        
        # === BRIDGE INTEL ===
        {
            "key": "LIFI_API_KEY",
            "description": "LiFi API key (optional)",
            "category": "bridge",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "SOCKET_API_KEY",
            "description": "Socket API key (optional)",
            "category": "bridge",
            "is_secret": True,
            "data_type": "string"
        },
        
        # === WALLET GUARD ===
        {
            "key": "DEBANK_API_KEY",
            "description": "DeBank API key (optional)",
            "category": "wallet",
            "is_secret": True,
            "data_type": "string"
        },
        
        # === REPORTING ===
        {
            "key": "PDF_PROVIDER",
            "description": "PDF generation provider",
            "category": "reporting",
            "is_public": True,
            "data_type": "string",
            "default_value": "docraptor",
            "options": ["docraptor", "pdfshift", "puppeteer"]
        },
        {
            "key": "PDF_API_KEY",
            "description": "PDF service API key",
            "category": "reporting",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "S3_ENDPOINT",
            "description": "S3 endpoint URL",
            "category": "reporting",
            "data_type": "url",
            "default_value": "https://s3.us-east-1.amazonaws.com"
        },
        {
            "key": "S3_BUCKET",
            "description": "S3 bucket name",
            "category": "reporting",
            "data_type": "string",
            "default_value": "scorpius-reports"
        },
        {
            "key": "S3_ACCESS_KEY",
            "description": "S3 access key",
            "category": "reporting",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "S3_SECRET_KEY",
            "description": "S3 secret key",
            "category": "reporting",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "S3_REGION",
            "description": "S3 region",
            "category": "reporting",
            "data_type": "string",
            "default_value": "us-east-1"
        },
        {
            "key": "PUBLIC_REPORT_DOWNLOAD_BASE",
            "description": "Public URL for report downloads",
            "category": "reporting",
            "is_public": True,
            "data_type": "url",
            "default_value": "https://cdn.scorpius.io/reports"
        },
        
        # === NOTIFICATIONS ===
        {
            "key": "SENTRY_DSN",
            "description": "Sentry DSN for error tracking",
            "category": "notifications",
            "is_secret": True,
            "data_type": "url"
        },
        {
            "key": "POSTMARK_API_KEY",
            "description": "Postmark API key for emails",
            "category": "notifications",
            "is_secret": True,
            "data_type": "string"
        },
        {
            "key": "SLACK_WEBHOOK_URL",
            "description": "Slack webhook URL",
            "category": "notifications",
            "is_secret": True,
            "data_type": "url"
        },
        
        # === INFRASTRUCTURE ===
        {
            "key": "DATABASE_URL",
            "description": "PostgreSQL database URL",
            "category": "infrastructure",
            "is_required": True,
            "data_type": "string",
            "default_value": "postgresql://scorpius:password@db:5432/scorpius"
        },
        {
            "key": "REDIS_URL",
            "description": "Redis cache URL",
            "category": "infrastructure",
            "is_required": True,
            "data_type": "string",
            "default_value": "redis://cache:6379/0"
        },
        {
            "key": "NATS_URL",
            "description": "NATS messaging URL",
            "category": "infrastructure",
            "data_type": "string",
            "default_value": "nats://nats:4222"
        },
        
        # === FRONTEND ===
        {
            "key": "VITE_PUBLIC_CHAIN_ETH",
            "description": "Frontend Ethereum RPC",
            "category": "frontend",
            "is_public": True,
            "data_type": "url"
        },
        {
            "key": "VITE_PUBLIC_CHAIN_ARB",
            "description": "Frontend Arbitrum RPC",
            "category": "frontend",
            "is_public": True,
            "data_type": "url"
        },
        {
            "key": "VITE_PUBLIC_RECAPTCHA_SITEKEY",
            "description": "reCAPTCHA site key",
            "category": "frontend",
            "is_public": True,
            "data_type": "string"
        },
    ]
}

def get_env_value(key: str) -> Optional[str]:
    """Get environment variable value"""
    return os.getenv(key)

def set_env_value(key: str, value: str) -> bool:
    """Set environment variable value in .env file"""
    try:
        if ENV_FILE_PATH.exists():
            set_key(str(ENV_FILE_PATH), key, value)
        else:
            # Create .env file if it doesn't exist
            ENV_FILE_PATH.write_text(f"{key}={value}\n")
        
        # Also set in current environment
        os.environ[key] = value
        return True
    except Exception as e:
        logger.error(f"Failed to set environment variable {key}: {e}")
        return False

def remove_env_value(key: str) -> bool:
    """Remove environment variable from .env file"""
    try:
        if ENV_FILE_PATH.exists():
            unset_key(str(ENV_FILE_PATH), key)
        
        # Also remove from current environment
        os.environ.pop(key, None)
        return True
    except Exception as e:
        logger.error(f"Failed to remove environment variable {key}: {e}")
        return False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return SettingsResponse(
        success=True,
        data={
            "status": "healthy",
            "version": "1.0.0",
            "service": "settings",
            "env_file_exists": ENV_FILE_PATH.exists(),
            "variables_count": len(SETTINGS_SCHEMA["variables"])
        }
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get service capabilities"""
    return SettingsResponse(
        success=True,
        data={
            "name": "settings",
            "version": "1.0.0",
            "description": "Comprehensive configuration management for Scorpius platform",
            "features": [
                "environment-variable-management",
                "configuration-schema",
                "public-private-separation",
                "validation-rules",
                "category-organization"
            ],
            "categories": len(SETTINGS_SCHEMA["categories"]),
            "variables": len(SETTINGS_SCHEMA["variables"])
        }
    )

@app.get("/schema")
async def get_schema():
    """Get complete configuration schema"""
    return SettingsResponse(
        success=True,
        data=SETTINGS_SCHEMA
    )

@app.get("/categories")
async def get_categories():
    """Get configuration categories"""
    return SettingsResponse(
        success=True,
        data={"categories": SETTINGS_SCHEMA["categories"]}
    )

@app.get("/variables")
async def get_variables(category: Optional[str] = None, public_only: bool = False):
    """Get configuration variables"""
    variables = SETTINGS_SCHEMA["variables"]
    
    if category:
        variables = [v for v in variables if v["category"] == category]
    
    if public_only:
        variables = [v for v in variables if v.get("is_public", False)]
    
    # Add current values (hide secrets)
    result_variables = []
    for var in variables:
        var_copy = var.copy()
        current_value = get_env_value(var["key"])
        
        if var.get("is_secret", False) and current_value:
            # Mask secret values
            var_copy["value"] = "*" * min(len(current_value), 8)
            var_copy["has_value"] = True
        else:
            var_copy["value"] = current_value
            var_copy["has_value"] = current_value is not None
        
        result_variables.append(var_copy)
    
    return SettingsResponse(
        success=True,
        data={"variables": result_variables}
    )

@app.get("/variables/{key}")
async def get_variable(key: str):
    """Get specific configuration variable"""
    variable = next((v for v in SETTINGS_SCHEMA["variables"] if v["key"] == key), None)
    
    if not variable:
        raise HTTPException(status_code=404, detail=f"Variable '{key}' not found")
    
    var_copy = variable.copy()
    current_value = get_env_value(key)
    
    if variable.get("is_secret", False) and current_value:
        var_copy["value"] = "*" * min(len(current_value), 8)
        var_copy["has_value"] = True
    else:
        var_copy["value"] = current_value
        var_copy["has_value"] = current_value is not None
    
    return SettingsResponse(
        success=True,
        data={"variable": var_copy}
    )

@app.post("/variables/{key}")
async def update_variable(key: str, update: Dict[str, Any]):
    """Update specific configuration variable"""
    variable = next((v for v in SETTINGS_SCHEMA["variables"] if v["key"] == key), None)
    
    if not variable:
        raise HTTPException(status_code=404, detail=f"Variable '{key}' not found")
    
    value = update.get("value")
    if value is None:
        raise HTTPException(status_code=400, detail="Value is required")
    
    # Validate value if pattern is specified
    if variable.get("validation_pattern") and value:
        pattern = variable["validation_pattern"]
        if not re.match(pattern, str(value)):
            raise HTTPException(status_code=400, detail=f"Value does not match required pattern: {pattern}")
    
    # Validate options if specified
    if variable.get("options") and value not in variable["options"]:
        raise HTTPException(status_code=400, detail=f"Value must be one of: {variable['options']}")
    
    # Set the value
    success = set_env_value(key, str(value))
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update configuration")
    
    return SettingsResponse(
        success=True,
        data={"key": key, "updated": True},
        message=f"Configuration variable '{key}' updated successfully"
    )

@app.delete("/variables/{key}")
async def delete_variable(key: str):
    """Delete configuration variable"""
    variable = next((v for v in SETTINGS_SCHEMA["variables"] if v["key"] == key), None)
    
    if not variable:
        raise HTTPException(status_code=404, detail=f"Variable '{key}' not found")
    
    if variable.get("is_required", False):
        raise HTTPException(status_code=400, detail="Cannot delete required variable")
    
    success = remove_env_value(key)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete configuration")
    
    return SettingsResponse(
        success=True,
        data={"key": key, "deleted": True},
        message=f"Configuration variable '{key}' deleted successfully"
    )

@app.post("/variables")
async def update_multiple_variables(update: ConfigUpdate):
    """Update multiple configuration variables"""
    results = []
    errors = []
    
    for key, value in update.updates.items():
        variable = next((v for v in SETTINGS_SCHEMA["variables"] if v["key"] == key), None)
        
        if not variable:
            errors.append(f"Variable '{key}' not found")
            continue
        
        # Validate value
        if variable.get("validation_pattern") and value:
            pattern = variable["validation_pattern"]
            if not re.match(pattern, str(value)):
                errors.append(f"Variable '{key}' does not match required pattern: {pattern}")
                continue
        
        if variable.get("options") and value not in variable["options"]:
            errors.append(f"Variable '{key}' must be one of: {variable['options']}")
            continue
        
        # Set the value
        success = set_env_value(key, str(value))
        
        if success:
            results.append({"key": key, "updated": True})
        else:
            errors.append(f"Failed to update variable '{key}'")
    
    return SettingsResponse(
        success=len(errors) == 0,
        data={
            "updated": results,
            "errors": errors,
            "total_updated": len(results),
            "total_errors": len(errors)
        },
        message=f"Updated {len(results)} variables" + (f", {len(errors)} errors" if errors else "")
    )

@app.get("/export")
async def export_configuration():
    """Export current configuration (public values only)"""
    public_variables = [v for v in SETTINGS_SCHEMA["variables"] if v.get("is_public", False)]
    
    config = {}
    for variable in public_variables:
        value = get_env_value(variable["key"])
        if value:
            config[variable["key"]] = value
    
    return SettingsResponse(
        success=True,
        data={
            "configuration": config,
            "exported_at": datetime.utcnow().isoformat(),
            "variable_count": len(config)
        }
    )

@app.post("/blueprint")
async def create_env_blueprint():
    """Create a complete .env blueprint file"""
    blueprint_lines = [
        "################################################################################",
        "# ███████  ██████  ██████  ██████  ██████  ██    ██ ██ ██    ██ ███████ ███████ ",
        "# ███████████████████████████████████████████████████████████████████████████████",
        "# UNIVERSAL ENV FOR ── SCORPIUS FX + HUNTER EDITION ── ALL MODULES ENABLED",
        "# Generated by Scorpius Settings Service",
        f"# Created: {datetime.utcnow().isoformat()}",
        "################################################################################",
        ""
    ]
    
    # Group variables by category
    categories = {}
    for variable in SETTINGS_SCHEMA["variables"]:
        category = variable["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(variable)
    
    # Generate blueprint by category
    for category_info in SETTINGS_SCHEMA["categories"]:
        category = category_info["name"]
        if category in categories:
            blueprint_lines.append(f"############################")
            blueprint_lines.append(f"# === {category_info['description'].upper()} ===")
            blueprint_lines.append(f"############################")
            
            for variable in categories[category]:
                current_value = get_env_value(variable["key"])
                default_value = variable.get("default_value", "")
                
                # Add description as comment
                blueprint_lines.append(f"# {variable['description']}")
                
                # Add validation info if available
                if variable.get("validation_pattern"):
                    blueprint_lines.append(f"# Pattern: {variable['validation_pattern']}")
                
                if variable.get("options"):
                    blueprint_lines.append(f"# Options: {', '.join(variable['options'])}")
                
                # Add the variable line
                value = current_value or default_value
                if variable.get("is_secret") and not current_value:
                    value = f"<{variable['key'].lower().replace('_', '-')}>"
                
                blueprint_lines.append(f"{variable['key']}={value}")
                blueprint_lines.append("")
            
            blueprint_lines.append("")
    
    blueprint_lines.extend([
        "################################################################################",
        "# End of file — save as `.env` (backend) and `.env.local` (frontend)            #",
        "# For CI: map secrets accordingly (GitHub Actions → Settings → Secrets/Vars)    #",
        "# Never commit any *SK / API_KEY / SECRET* to Git — use vault/CI injection.     #",
        "################################################################################"
    ])
    
    blueprint_content = "\n".join(blueprint_lines)
    
    return SettingsResponse(
        success=True,
        data={
            "blueprint": blueprint_content,
            "line_count": len(blueprint_lines),
            "variable_count": len(SETTINGS_SCHEMA["variables"])
        }
    )

@app.get("/validate")
async def validate_configuration():
    """Validate current configuration"""
    validation_results = []
    errors = []
    warnings = []
    
    for variable in SETTINGS_SCHEMA["variables"]:
        key = variable["key"]
        current_value = get_env_value(key)
        
        result = {
            "key": key,
            "category": variable["category"],
            "required": variable.get("is_required", False),
            "has_value": current_value is not None,
            "valid": True,
            "issues": []
        }
        
        # Check required variables
        if variable.get("is_required", False) and not current_value:
            result["valid"] = False
            result["issues"].append("Required variable is missing")
            errors.append(f"Missing required variable: {key}")
        
        # Validate pattern if value exists
        if current_value and variable.get("validation_pattern"):
            pattern = variable["validation_pattern"]
            if not re.match(pattern, current_value):
                result["valid"] = False
                result["issues"].append(f"Does not match pattern: {pattern}")
                errors.append(f"Invalid format for {key}")
        
        # Check options if value exists
        if current_value and variable.get("options"):
            if current_value not in variable["options"]:
                result["valid"] = False
                result["issues"].append(f"Must be one of: {variable['options']}")
                errors.append(f"Invalid option for {key}")
        
        # Check for default values in production-like settings
        if current_value and variable.get("default_value"):
            if current_value == variable["default_value"] and "YOUR_" in current_value:
                result["issues"].append("Using placeholder value")
                warnings.append(f"Using placeholder value for {key}")
        
        validation_results.append(result)
    
    valid_count = sum(1 for r in validation_results if r["valid"])
    total_count = len(validation_results)
    
    return SettingsResponse(
        success=len(errors) == 0,
        data={
            "validation_results": validation_results,
            "summary": {
                "total_variables": total_count,
                "valid_variables": valid_count,
                "invalid_variables": total_count - valid_count,
                "error_count": len(errors),
                "warning_count": len(warnings)
            },
            "errors": errors,
            "warnings": warnings
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 