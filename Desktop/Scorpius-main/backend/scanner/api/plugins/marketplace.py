"""
Plugin Marketplace API for Scorpius Enterprise
Allows users to discover, install, and manage third-party security plugins
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

import docker

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])

# Docker client - Initialize lazily to avoid startup issues
docker_client = None


def get_docker_client():
    global docker_client
    if docker_client is None:
        try:
            docker_client = docker.from_env()
        except Exception as e:
            print(f"Warning: Docker not available: {e}")
            docker_client = False
    return docker_client if docker_client is not False else None


# Marketplace models
class PluginManifest(BaseModel):
    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = []
    capabilities: List[str] = []
    docker_image: str
    memory_limit: str = "512m"
    cpu_limit: str = "1"
    environment_variables: Dict[str, str] = {}
    input_format: str = "solidity"
    output_format: str = "json"
    supported_blockchains: List[str] = ["ethereum"]


class MarketplacePlugin(BaseModel):
    id: str
    manifest: PluginManifest
    download_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    created_at: datetime
    updated_at: datetime
    status: str = "available"  # available, deprecated, removed
    verified: bool = False


class PluginInstallRequest(BaseModel):
    plugin_id: str
    docker_image: Optional[str] = None
    version: Optional[str] = "latest"
    config: Dict[str, Any] = {}


class PluginUploadRequest(BaseModel):
    manifest: PluginManifest
    dockerfile_content: Optional[str] = None
    docker_image_url: Optional[str] = None


# In-memory marketplace storage (in production, use proper database)
marketplace_plugins: Dict[str, MarketplacePlugin] = {}
installed_plugins: Dict[str, Dict] = {}

# Built-in plugins registry
BUILTIN_PLUGINS = [
    {
        "id": "slither-official",
        "manifest": PluginManifest(
            name="Slither",
            version="0.10.0",
            description="Static analysis framework for Solidity smart contracts",
            author="Trail of Bits",
            license="AGPL-3.0",
            homepage="https://github.com/crytic/slither",
            repository="https://github.com/crytic/slither",
            tags=["static-analysis", "solidity", "official"],
            capabilities=["static_analysis", "vulnerability_detection"],
            docker_image="scorpius/slither:latest",
            memory_limit="512m",
            input_format="solidity",
            output_format="json",
            supported_blockchains=["ethereum", "polygon", "bsc"],
        ),
        "verified": True,
        "rating": 4.8,
        "download_count": 15000,
    },
    {
        "id": "mythril-official",
        "manifest": PluginManifest(
            name="Mythril",
            version="0.24.3",
            description="Security analysis tool for Ethereum smart contracts",
            author="ConsenSys",
            license="MIT",
            homepage="https://mythril-classic.readthedocs.io",
            repository="https://github.com/ConsenSys/mythril",
            tags=["symbolic-execution", "ethereum", "official"],
            capabilities=["symbolic_execution", "vulnerability_detection"],
            docker_image="scorpius/mythril:latest",
            memory_limit="1g",
            input_format="solidity",
            output_format="json",
            supported_blockchains=["ethereum"],
        ),
        "verified": True,
        "rating": 4.6,
        "download_count": 12000,
    },
]

# Initialize built-in plugins
for plugin_data in BUILTIN_PLUGINS:
    plugin = MarketplacePlugin(
        id=plugin_data["id"],
        manifest=plugin_data["manifest"],
        download_count=plugin_data.get("download_count", 0),
        rating=plugin_data.get("rating", 0.0),
        reviews_count=plugin_data.get("reviews_count", 0),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        verified=plugin_data.get("verified", False),
    )
    marketplace_plugins[plugin_data["id"]] = plugin


@router.get("/plugins", response_model=List[MarketplacePlugin])
async def list_marketplace_plugins(
    category: Optional[str] = None,
    search: Optional[str] = None,
    verified_only: bool = False,
    limit: int = 50,
):
    """List available plugins in the marketplace"""
    plugins = list(marketplace_plugins.values())

    # Apply filters
    if verified_only:
        plugins = [p for p in plugins if p.verified]

    if category:
        plugins = [
            p
            for p in plugins
            if category.lower() in [tag.lower() for tag in p.manifest.tags]
        ]

    if search:
        search_lower = search.lower()
        plugins = [
            p
            for p in plugins
            if search_lower in p.manifest.name.lower()
            or search_lower in p.manifest.description.lower()
            or any(search_lower in tag.lower() for tag in p.manifest.tags)
        ]

    # Sort by rating and download count
    plugins.sort(key=lambda x: (x.rating, x.download_count), reverse=True)

    return plugins[:limit]


@router.get("/plugins/{plugin_id}", response_model=MarketplacePlugin)
async def get_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin"""
    if plugin_id not in marketplace_plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return marketplace_plugins[plugin_id]


@router.post("/plugins/{plugin_id}/install")
async def install_plugin(plugin_id: str, request: PluginInstallRequest):
    """Install a plugin from the marketplace"""
    if plugin_id not in marketplace_plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin = marketplace_plugins[plugin_id]

    try:
        # Pull Docker image
        docker_image = request.docker_image or plugin.manifest.docker_image

        client = get_docker_client()
        if not client:
            raise HTTPException(
                status_code=503,
                detail="Docker service not available")

        print(f"Pulling Docker image: {docker_image}")
        client.images.pull(docker_image)

        # Create plugin configuration
        plugin_config = {
            "id": plugin_id,
            "name": plugin.manifest.name,
            "version": request.version or plugin.manifest.version,
            "image": docker_image,
            "memory_limit": plugin.manifest.memory_limit,
            "cpu_limit": plugin.manifest.cpu_limit,
            "environment": plugin.manifest.environment_variables,
            "capabilities": plugin.manifest.capabilities,
            "installed_at": datetime.now(),
            "config": request.config,
        }

        # Store installation info
        installed_plugins[plugin_id] = plugin_config

        # Update download count
        marketplace_plugins[plugin_id].download_count += 1

        return {
            "status": "success",
            "message": f"Plugin {plugin.manifest.name} installed successfully",
            "plugin_id": plugin_id,
            "image": docker_image,
        }

    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=400, detail="Docker image not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Installation failed: {
                str(e)}",
        )


@router.delete("/plugins/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    """Uninstall a plugin"""
    if plugin_id not in installed_plugins:
        raise HTTPException(status_code=404, detail="Plugin not installed")

    try:
        plugin_config = installed_plugins[plugin_id]

        client = get_docker_client()
        if not client:
            raise HTTPException(
                status_code=503,
                detail="Docker service not available")

        # Stop any running containers for this plugin
        containers = client.containers.list(
            filters={"ancestor": plugin_config["image"]}
        )
        for container in containers:
            container.stop()
            container.remove()

        # Remove plugin configuration
        del installed_plugins[plugin_id]

        return {
            "status": "success",
            "message": f"Plugin {
                plugin_config['name']} uninstalled successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Uninstallation failed: {
                str(e)}",
        )


@router.get("/installed", response_model=List[Dict])
async def list_installed_plugins():
    """List all installed plugins"""
    return list(installed_plugins.values())


@router.post("/plugins/upload")
async def upload_plugin(
        manifest_file: UploadFile = File(...),
        dockerfile: Optional[UploadFile] = File(None)):
    """Upload a new plugin to the marketplace"""
    try:
        # Read and parse manifest
        manifest_content = await manifest_file.read()
        manifest_data = json.loads(manifest_content.decode())
        manifest = PluginManifest(**manifest_data)

        # Generate plugin ID
        plugin_id = f"{manifest.name.lower().replace(' ',
                                                     '-')}-{manifest.author.lower().replace(' ',
                                                                                            '-')}"

        # Handle Dockerfile if provided
        if dockerfile:
            (await dockerfile.read()).decode()

        # Create marketplace entry
        plugin = MarketplacePlugin(
            id=plugin_id,
            manifest=manifest,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            verified=False,  # New plugins need verification
        )

        marketplace_plugins[plugin_id] = plugin

        return {
            "status": "success",
            "message": "Plugin uploaded successfully and pending verification",
            "plugin_id": plugin_id,
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid manifest JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/categories")
async def get_plugin_categories():
    """Get all available plugin categories"""
    categories = set()
    for plugin in marketplace_plugins.values():
        categories.update(plugin.manifest.tags)

    return sorted(list(categories))


@router.post("/plugins/{plugin_id}/rate")
async def rate_plugin(plugin_id: str, rating: float = Field(..., ge=1, le=5)):
    """Rate a plugin (1-5 stars)"""
    if plugin_id not in marketplace_plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin = marketplace_plugins[plugin_id]

    # Simple rating calculation (in production, store individual ratings)
    current_total = plugin.rating * plugin.reviews_count
    new_total = current_total + rating
    plugin.reviews_count += 1
    plugin.rating = new_total / plugin.reviews_count

    return {
        "status": "success",
        "message": "Rating submitted successfully",
        "new_rating": plugin.rating,
        "total_reviews": plugin.reviews_count,
    }


@router.get("/plugins/{plugin_id}/manifest")
async def get_plugin_manifest(plugin_id: str):
    """Get the raw manifest for a plugin"""
    if plugin_id not in marketplace_plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return marketplace_plugins[plugin_id].manifest


@router.post("/plugins/{plugin_id}/build")
async def build_plugin_image(plugin_id: str):
    """Build Docker image for a plugin with custom Dockerfile"""
    if plugin_id not in marketplace_plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    # This would handle building custom Docker images
    # For now, return a placeholder response
    return {
        "status": "started",
        "message": "Docker image build started",
        "build_id": f"build-{plugin_id}-{int(datetime.now().timestamp())}",
    }
