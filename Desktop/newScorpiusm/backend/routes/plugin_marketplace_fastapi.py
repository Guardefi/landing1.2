"""
FastAPI routes for Plugin Marketplace
Manages plugins, extensions, and marketplace operations
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

# Import plugin marketplace modules
try:
    from ..plugin_marketplace import (
        PluginCategory,
        PluginMarketplace,
        PluginSandbox,
        PluginStatus,
    )
except ImportError:
    # Fallback stubs if not available
    class PluginMarketplace:
        def __init__(self):
            self.plugins = {}

        async def install_plugin(self, plugin_id, version=None):
            return {"status": "installed", "plugin_id": plugin_id}

        async def list_plugins(self, category=None, status=None):
            return {"plugins": [], "total": 0}

        async def get_plugin_info(self, plugin_id):
            return {"id": plugin_id, "status": "active", "version": "1.0.0"}

        async def enable_plugin(self, plugin_id):
            return {"status": "enabled"}

        async def disable_plugin(self, plugin_id):
            return {"status": "disabled"}

        async def uninstall_plugin(self, plugin_id):
            return {"status": "uninstalled"}

    class PluginStatus:
        ACTIVE = "active"
        INACTIVE = "inactive"
        ERROR = "error"
        LOADING = "loading"

    class PluginCategory:
        SECURITY = "security"
        MONITORING = "monitoring"
        ANALYTICS = "analytics"
        AUTOMATION = "automation"

    class PluginSandbox:
        def __init__(self):
            pass

        async def execute_plugin(self, plugin_id, function_name, args):
            return {"result": "stub-execution", "status": "success"}


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/plugins", tags=["Plugin Marketplace"])

# Initialize plugin marketplace
marketplace = PluginMarketplace()
sandbox = PluginSandbox()


# Request/Response models
class PluginInstallRequest(BaseModel):
    plugin_id: str
    version: str | None = None
    auto_enable: bool = True
    config: dict[str, Any] | None = None


class PluginInstallResponse(BaseModel):
    plugin_id: str
    status: str
    version: str
    installed_at: datetime


class PluginListRequest(BaseModel):
    category: str | None = None
    status: str | None = None
    search_term: str | None = None
    limit: int = 50
    offset: int = 0


class PluginInfo(BaseModel):
    id: str
    name: str
    version: str
    description: str
    category: str
    status: str
    author: str
    created_at: datetime
    updated_at: datetime
    permissions: list[str]
    dependencies: list[str]


class PluginListResponse(BaseModel):
    plugins: list[PluginInfo]
    total: int
    has_more: bool


class PluginExecutionRequest(BaseModel):
    plugin_id: str
    function_name: str
    arguments: dict[str, Any] | None = None
    timeout: int = 30


class PluginExecutionResponse(BaseModel):
    result: Any
    execution_time: float
    status: str
    timestamp: datetime


# Endpoints
@router.get("/marketplace", response_model=PluginListResponse)
async def list_marketplace_plugins(
    category: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List available plugins in the marketplace."""
    try:
        result = await marketplace.list_marketplace_plugins(
            category=category, search_term=search, limit=limit, offset=offset
        )

        plugins = [
            PluginInfo(
                id=p["id"],
                name=p["name"],
                version=p["version"],
                description=p["description"],
                category=p["category"],
                status="available",
                author=p["author"],
                created_at=datetime.fromisoformat(p["created_at"]),
                updated_at=datetime.fromisoformat(p["updated_at"]),
                permissions=p.get("permissions", []),
                dependencies=p.get("dependencies", []),
            )
            for p in result["plugins"]
        ]

        return PluginListResponse(
            plugins=plugins,
            total=result["total"],
            has_more=result["total"] > (offset + limit),
        )
    except Exception as e:
        logger.error(f"Failed to list marketplace plugins: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch plugins: {str(e)}"
        )


@router.get("/installed", response_model=PluginListResponse)
async def list_installed_plugins(
    category: str | None = None, status: str | None = None
):
    """List installed plugins."""
    try:
        result = await marketplace.list_plugins(category=category, status=status)

        plugins = [
            PluginInfo(
                id=p["id"],
                name=p["name"],
                version=p["version"],
                description=p["description"],
                category=p["category"],
                status=p["status"],
                author=p["author"],
                created_at=datetime.fromisoformat(p["created_at"]),
                updated_at=datetime.fromisoformat(p["updated_at"]),
                permissions=p.get("permissions", []),
                dependencies=p.get("dependencies", []),
            )
            for p in result["plugins"]
        ]

        return PluginListResponse(
            plugins=plugins, total=result["total"], has_more=False
        )
    except Exception as e:
        logger.error(f"Failed to list installed plugins: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch installed plugins: {str(e)}"
        )


@router.post("/install", response_model=PluginInstallResponse)
async def install_plugin(
    request: PluginInstallRequest, background_tasks: BackgroundTasks
):
    """Install a plugin from the marketplace."""
    try:
        # Start installation in background
        background_tasks.add_task(
            _install_plugin_task,
            request.plugin_id,
            request.version,
            request.auto_enable,
            request.config,
        )

        return PluginInstallResponse(
            plugin_id=request.plugin_id,
            status="installing",
            version=request.version or "latest",
            installed_at=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to start plugin installation: {e}")
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")


@router.post("/upload")
async def upload_plugin(file: UploadFile = File(...)):
    """Upload a custom plugin package."""
    try:
        # Save uploaded file
        content = await file.read()

        # Install from uploaded package
        result = await marketplace.install_from_package(content, file.filename)

        return {
            "plugin_id": result["plugin_id"],
            "status": "uploaded",
            "filename": file.filename,
            "size": len(content),
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to upload plugin: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{plugin_id}")
async def get_plugin_info(plugin_id: str):
    """Get detailed information about a plugin."""
    try:
        info = await marketplace.get_plugin_info(plugin_id)
        if not info:
            raise HTTPException(status_code=404, detail="Plugin not found") from e

        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plugin info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch plugin info: {str(e)}"
        )


@router.post("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """Enable a plugin."""
    try:
        result = await marketplace.enable_plugin(plugin_id)
        return {
            "plugin_id": plugin_id,
            "status": "enabled",
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to enable plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to enable plugin: {str(e)}"
        )


@router.post("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """Disable a plugin."""
    try:
        result = await marketplace.disable_plugin(plugin_id)
        return {
            "plugin_id": plugin_id,
            "status": "disabled",
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to disable plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to disable plugin: {str(e)}"
        )


@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    """Uninstall a plugin."""
    try:
        result = await marketplace.uninstall_plugin(plugin_id)
        return {
            "plugin_id": plugin_id,
            "status": "uninstalled",
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to uninstall plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to uninstall plugin: {str(e)}"
        )


@router.post("/{plugin_id}/execute", response_model=PluginExecutionResponse)
async def execute_plugin_function(plugin_id: str, request: PluginExecutionRequest):
    """Execute a function in a plugin sandbox."""
    try:
        start_time = datetime.now()

        result = await sandbox.execute_plugin(
            plugin_id=plugin_id,
            function_name=request.function_name,
            arguments=request.arguments or {},
            timeout=request.timeout,
        )

        execution_time = (datetime.now() - start_time).total_seconds()

        return PluginExecutionResponse(
            result=result["result"],
            execution_time=execution_time,
            status=result["status"],
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to execute plugin function: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/categories/list")
async def list_plugin_categories():
    """List available plugin categories."""
    return {
        "categories": [
            {
                "id": "security",
                "name": "Security",
                "description": "Security-focused plugins",
            },
            {
                "id": "monitoring",
                "name": "Monitoring",
                "description": "System monitoring plugins",
            },
            {
                "id": "analytics",
                "name": "Analytics",
                "description": "Data analysis plugins",
            },
            {
                "id": "automation",
                "name": "Automation",
                "description": "Workflow automation plugins",
            },
            {
                "id": "integration",
                "name": "Integration",
                "description": "Third-party integrations",
            },
            {
                "id": "visualization",
                "name": "Visualization",
                "description": "Data visualization plugins",
            },
            {"id": "utilities", "name": "Utilities", "description": "Utility plugins"},
            {"id": "custom", "name": "Custom", "description": "Custom plugins"},
        ]
    }


@router.get("/sandbox/status")
async def get_sandbox_status():
    """Get plugin sandbox status."""
    try:
        status = await sandbox.get_status()
        return {
            "active_plugins": status.get("active_plugins", 0),
            "sandboxed_executions": status.get("total_executions", 0),
            "security_violations": status.get("security_violations", 0),
            "sandbox_health": status.get("health", "healthy"),
            "last_check": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to get sandbox status: {e}")
        return {"status": "error", "error": str(e), "last_check": datetime.now()}


# Background task for plugin installation
async def _install_plugin_task(
    plugin_id: str,
    version: str | None,
    auto_enable: bool,
    config: dict[str, Any] | None,
):
    """Background task to install a plugin."""
    try:
        result = await marketplace.install_plugin(
            plugin_id=plugin_id, version=version, auto_enable=auto_enable, config=config
        )
        logger.info(f"Plugin {plugin_id} installed successfully: {result}")
    except Exception as e:
        logger.error(f"Failed to install plugin {plugin_id}: {e}")
