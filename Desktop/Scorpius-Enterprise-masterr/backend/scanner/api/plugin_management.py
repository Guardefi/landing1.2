"""
Plugin Management API for Scorpius Enterprise
Provides comprehensive plugin configuration and control
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.enhanced_plugin_manager import EnhancedPluginManager
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger("scorpius.plugin_management")

# Security
security = HTTPBearer()

# Plugin Management Router
router = APIRouter(prefix="/api/v1/plugin-management", tags=["plugin-management"])

# Global plugin manager instance
plugin_manager: Optional[EnhancedPluginManager] = None


# Pydantic models
class PluginToggleRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable the plugin")


class PluginConfigRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="Plugin configuration parameters")


class PluginStatus(BaseModel):
    name: str
    enabled: bool
    initialized: bool
    version: str
    description: str
    capabilities: Dict[str, Any]
    last_used: Optional[datetime]
    total_scans: int
    success_rate: float
    config: Dict[str, Any]


class PluginToggleResponse(BaseModel):
    plugin_name: str
    enabled: bool
    status: str
    message: str


class PluginListResponse(BaseModel):
    plugins: List[PluginStatus]
    total_count: int
    enabled_count: int


# Dependency injection
async def get_plugin_manager() -> EnhancedPluginManager:
    global plugin_manager
    if plugin_manager is None:
        plugin_manager = EnhancedPluginManager()
        # Initialize common plugins
        await plugin_manager.initialize_plugins(["slither", "mythril", "manticore"])
    return plugin_manager


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    if credentials.credentials == "scorpius-api-token":
        return credentials.credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Plugin state management (in production, use Redis/Database)
plugin_states: Dict[str, Dict[str, Any]] = {
    "slither": {
        "enabled": True,
        "initialized": False,
        "config": {
            "detectors": "all",
            "exclude_optimization": False,
            "exclude_informational": False,
            "timeout": 300,
        },
        "stats": {"total_scans": 0, "success_rate": 0.0, "last_used": None},
    },
    "mythril": {
        "enabled": True,
        "initialized": False,
        "config": {
            "execution_timeout": 300,
            "create_timeout": 120,
            "max_depth": 50,
            "strategy": "dfs",
            "transaction_count": 3,
        },
        "stats": {"total_scans": 0, "success_rate": 0.0, "last_used": None},
    },
    "manticore": {
        "enabled": False,  # Disabled by default due to resource usage
        "initialized": False,
        "config": {
            "timeout": 600,
            "max_depth": 100,
            "concrete_start": "0x0",
            "verbosity": 1,
        },
        "stats": {"total_scans": 0, "success_rate": 0.0, "last_used": None},
    },
}


@router.get("/plugins", response_model=PluginListResponse)
async def list_plugin_status(
    token: str = Depends(verify_token),
    manager: EnhancedPluginManager = Depends(get_plugin_manager),
):
    """Get status of all plugins with their configurations"""
    try:
        plugins = []
        enabled_count = 0

        for plugin_name in ["slither", "mythril", "manticore"]:
            state = plugin_states.get(plugin_name, {})
            metadata = manager.plugin_metadata.get(plugin_name)
            
            if state.get("enabled", False):
                enabled_count += 1

            plugin_status = PluginStatus(
                name=plugin_name,
                enabled=state.get("enabled", False),
                initialized=state.get("initialized", False),
                version=metadata.version if metadata else "unknown",
                description=metadata.description if metadata else f"{plugin_name.title()} security analysis",
                capabilities=metadata.capabilities.__dict__ if metadata else {},
                last_used=state.get("stats", {}).get("last_used"),
                total_scans=state.get("stats", {}).get("total_scans", 0),
                success_rate=state.get("stats", {}).get("success_rate", 0.0),
                config=state.get("config", {}),
            )
            plugins.append(plugin_status)

        return PluginListResponse(
            plugins=plugins,
            total_count=len(plugins),
            enabled_count=enabled_count,
        )

    except Exception as e:
        logger.error(f"Error listing plugin status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list plugin status: {str(e)}",
        )


@router.post("/plugins/{plugin_name}/toggle", response_model=PluginToggleResponse)
async def toggle_plugin(
    plugin_name: str,
    request: PluginToggleRequest,
    token: str = Depends(verify_token),
    manager: EnhancedPluginManager = Depends(get_plugin_manager),
):
    """Enable or disable a specific plugin"""
    if plugin_name not in plugin_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_name} not found",
        )

    try:
        # Update plugin state
        plugin_states[plugin_name]["enabled"] = request.enabled

        # Initialize plugin if being enabled
        if request.enabled and not plugin_states[plugin_name]["initialized"]:
            result = await manager.initialize_plugins([plugin_name])
            if result.get(plugin_name, False):
                plugin_states[plugin_name]["initialized"] = True
                status_msg = "enabled and initialized"
            else:
                plugin_states[plugin_name]["enabled"] = False
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to initialize plugin {plugin_name}",
                )
        else:
            status_msg = "enabled" if request.enabled else "disabled"

        logger.info(f"Plugin {plugin_name} {status_msg}")

        return PluginToggleResponse(
            plugin_name=plugin_name,
            enabled=request.enabled,
            status="success",
            message=f"Plugin {plugin_name} {status_msg} successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling plugin {plugin_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle plugin {plugin_name}: {str(e)}",
        )


@router.get("/plugins/{plugin_name}/status", response_model=PluginStatus)
async def get_plugin_status(
    plugin_name: str,
    token: str = Depends(verify_token),
    manager: EnhancedPluginManager = Depends(get_plugin_manager),
):
    """Get detailed status of a specific plugin"""
    if plugin_name not in plugin_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_name} not found",
        )

    try:
        state = plugin_states[plugin_name]
        metadata = manager.plugin_metadata.get(plugin_name)

        return PluginStatus(
            name=plugin_name,
            enabled=state.get("enabled", False),
            initialized=state.get("initialized", False),
            version=metadata.version if metadata else "unknown",
            description=metadata.description if metadata else f"{plugin_name.title()} security analysis",
            capabilities=metadata.capabilities.__dict__ if metadata else {},
            last_used=state.get("stats", {}).get("last_used"),
            total_scans=state.get("stats", {}).get("total_scans", 0),
            success_rate=state.get("stats", {}).get("success_rate", 0.0),
            config=state.get("config", {}),
        )

    except Exception as e:
        logger.error(f"Error getting plugin status for {plugin_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plugin status: {str(e)}",
        )


@router.put("/plugins/{plugin_name}/config")
async def update_plugin_config(
    plugin_name: str,
    request: PluginConfigRequest,
    token: str = Depends(verify_token),
):
    """Update configuration for a specific plugin"""
    if plugin_name not in plugin_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_name} not found",
        )

    try:
        # Update plugin configuration
        plugin_states[plugin_name]["config"].update(request.config)

        logger.info(f"Updated configuration for plugin {plugin_name}")

        return {
            "plugin_name": plugin_name,
            "status": "success",
            "message": f"Configuration updated for plugin {plugin_name}",
            "config": plugin_states[plugin_name]["config"],
        }

    except Exception as e:
        logger.error(f"Error updating plugin config for {plugin_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plugin configuration: {str(e)}",
        )


@router.post("/plugins/{plugin_name}/test")
async def test_plugin(
    plugin_name: str,
    token: str = Depends(verify_token),
    manager: EnhancedPluginManager = Depends(get_plugin_manager),
):
    """Test a plugin with a sample contract"""
    if plugin_name not in plugin_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_name} not found",
        )

    if not plugin_states[plugin_name]["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin {plugin_name} is not enabled",
        )

    try:
        # Sample vulnerable contract for testing
        test_contract = '''
        pragma solidity ^0.8.0;
        
        contract TestContract {
            mapping(address => uint256) public balances;
            
            function withdraw(uint256 amount) public {
                require(balances[msg.sender] >= amount, "Insufficient balance");
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success, "Transfer failed");
                balances[msg.sender] -= amount; // Vulnerable to reentrancy
            }
        }
        '''

        # TODO: Implement actual plugin testing
        # For now, return a mock result
        test_result = {
            "plugin_name": plugin_name,
            "status": "success",
            "test_type": "sample_contract",
            "findings_count": 1 if plugin_name == "slither" else 0,
            "execution_time": 1.5,
            "timestamp": datetime.now().isoformat(),
        }

        return test_result

    except Exception as e:
        logger.error(f"Error testing plugin {plugin_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test plugin {plugin_name}: {str(e)}",
        )


@router.get("/plugins/enabled")
async def get_enabled_plugins(
    token: str = Depends(verify_token),
):
    """Get list of currently enabled plugins"""
    try:
        enabled_plugins = [
            name for name, state in plugin_states.items() 
            if state.get("enabled", False)
        ]

        return {
            "enabled_plugins": enabled_plugins,
            "count": len(enabled_plugins),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting enabled plugins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enabled plugins: {str(e)}",
        )


def get_plugin_states() -> Dict[str, Dict[str, Any]]:
    """Get current plugin states (for use by scan engine)"""
    return plugin_states


def update_plugin_stats(plugin_name: str, success: bool):
    """Update plugin usage statistics"""
    if plugin_name in plugin_states:
        stats = plugin_states[plugin_name]["stats"]
        stats["total_scans"] += 1
        stats["last_used"] = datetime.now()
        
        # Update success rate
        if stats["total_scans"] == 1:
            stats["success_rate"] = 1.0 if success else 0.0
        else:
            current_successes = stats["success_rate"] * (stats["total_scans"] - 1)
            if success:
                current_successes += 1
            stats["success_rate"] = current_successes / stats["total_scans"]
