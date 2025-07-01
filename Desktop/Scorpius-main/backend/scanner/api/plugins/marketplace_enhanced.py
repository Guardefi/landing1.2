"""
Enhanced Plugin Marketplace API with Advanced Features
Enterprise-grade plugin ecosystem for custom security tools
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

import docker

# Configure logging
logger = logging.getLogger("scorpius.marketplace")

# Create router
router = APIRouter()

# Security
security = HTTPBearer()

# Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.warning(f"Docker client initialization failed: {e}")
    docker_client = None


# Enhanced models
class PluginMetadata(BaseModel):
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    email: Optional[str] = Field(None, description="Author email")
    website: Optional[str] = Field(None, description="Author/company website")
    license: str = Field("MIT", description="Plugin license")
    homepage: Optional[str] = Field(None, description="Plugin homepage")
    repository: Optional[str] = Field(
        None, description="Source code repository")
    documentation: Optional[str] = Field(None, description="Documentation URL")
    changelog: Optional[str] = Field(None, description="Changelog URL")


class PluginCapabilities(BaseModel):
    scan_types: List[str] = Field(..., description="Supported scan types")
    vulnerability_types: List[str] = Field(
        ..., description="Vulnerability types detected"
    )
    supported_languages: List[str] = Field(
        ..., description="Supported programming languages"
    )
    supported_blockchains: List[str] = Field(
        default_factory=lambda: ["ethereum"],
        description="Supported blockchains")
    output_formats: List[str] = Field(
        default_factory=lambda: ["json"], description="Output formats"
    )
    api_version: str = Field("1.0", description="API version compatibility")
    requires_internet: bool = Field(
        False, description="Requires internet access")
    requires_gpu: bool = Field(False, description="Requires GPU acceleration")


class PluginConfiguration(BaseModel):
    docker_image: str = Field(..., description="Docker image name")
    cpu_limit: str = Field("1", description="CPU limit")
    memory_limit: str = Field("512m", description="Memory limit")
    timeout: int = Field(300, description="Execution timeout in seconds")
    environment_variables: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    port: Optional[int] = Field(
        None, description="API port (if plugin has REST API)")
    health_endpoint: Optional[str] = Field(
        None, description="Health check endpoint")
    volumes: List[str] = Field(
        default_factory=list, description="Required volume mounts"
    )
    networks: List[str] = Field(
        default_factory=list,
        description="Required networks")


class PluginUploadRequest(BaseModel):
    metadata: PluginMetadata
    capabilities: PluginCapabilities
    configuration: PluginConfiguration
    category: str = Field(..., description="Plugin category")
    tags: List[str] = Field(default_factory=list, description="Plugin tags")
    price: float = Field(0.0, description="Plugin price (0 for free)")
    release_notes: Optional[str] = Field(None, description="Release notes")


class MarketplacePlugin(BaseModel):
    id: str
    metadata: PluginMetadata
    capabilities: PluginCapabilities
    configuration: PluginConfiguration
    category: str
    tags: List[str]
    price: float

    # Marketplace metrics
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    popularity_score: float = 0.0

    # Status and verification
    status: str = "pending"  # pending, approved, rejected, deprecated
    verified: bool = False
    security_scanned: bool = False

    # Timestamps
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None

    # Additional metadata
    file_size: Optional[int] = None
    image_size: Optional[int] = None
    release_notes: Optional[str] = None


class PluginReview(BaseModel):
    id: str
    plugin_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: str = Field(..., max_length=200, description="Review title")
    content: str = Field(..., max_length=2000, description="Review content")
    verified_purchase: bool = False
    helpful_count: int = 0
    created_at: datetime


class PluginInstallRequest(BaseModel):
    plugin_id: str
    version: Optional[str] = "latest"
    configuration_override: Optional[Dict[str, Any]] = {}


class PluginSearchFilter(BaseModel):
    category: Optional[str] = None
    tags: List[str] = []
    supported_language: Optional[str] = None
    supported_blockchain: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    verified_only: bool = False
    sort_by: str = "popularity"  # popularity, rating, downloads, newest, name


# Storage (replace with proper database in production)
marketplace_plugins: Dict[str, MarketplacePlugin] = {}
plugin_reviews: Dict[str, List[PluginReview]] = {}
installed_plugins: Dict[str, Dict] = {}
user_favorites: Dict[str, List[str]] = {}


# Initialize with built-in plugins
def initialize_builtin_plugins():
    """Initialize marketplace with official plugins"""
    builtin_plugins = [
        {
            "id": "slither-official",
            "metadata": PluginMetadata(
                name="Slither",
                version="0.10.0",
                description="Static analysis framework for Solidity smart contracts",
                author="Trail of Bits",
                website="https://www.trailofbits.com/",
                license="AGPL-3.0",
                homepage="https://github.com/crytic/slither",
                repository="https://github.com/crytic/slither",
                documentation="https://github.com/crytic/slither/wiki",
            ),
            "capabilities": PluginCapabilities(
                scan_types=["static"],
                vulnerability_types=[
                    "reentrancy",
                    "arithmetic",
                    "uninitialized-state",
                    "locked-ether",
                ],
                supported_languages=["solidity"],
                supported_blockchains=["ethereum", "polygon", "bsc", "avalanche"],
                output_formats=["json", "sarif"],
            ),
            "configuration": PluginConfiguration(
                docker_image="scorpius/slither:latest",
                port=8081,
                health_endpoint="/health",
            ),
            "category": "static-analysis",
            "tags": ["static-analysis", "solidity", "official", "trail-of-bits"],
            "verified": True,
            "security_scanned": True,
            "status": "approved",
            "rating": 4.8,
            "download_count": 15000,
        },
        {
            "id": "mythril-official",
            "metadata": PluginMetadata(
                name="Mythril",
                version="0.24.3",
                description="Security analysis tool for Ethereum smart contracts using symbolic execution",
                author="ConsenSys",
                website="https://consensys.net/",
                license="MIT",
                homepage="https://mythril-classic.readthedocs.io",
                repository="https://github.com/ConsenSys/mythril",
            ),
            "capabilities": PluginCapabilities(
                scan_types=["symbolic", "dynamic"],
                vulnerability_types=[
                    "integer-overflow",
                    "reentrancy",
                    "unchecked-retval",
                    "weak-randomness",
                ],
                supported_languages=["solidity", "bytecode"],
                supported_blockchains=["ethereum"],
                output_formats=["json", "markdown"],
            ),
            "configuration": PluginConfiguration(
                docker_image="scorpius/mythril:latest",
                port=8082,
                health_endpoint="/health",
                memory_limit="1g",
            ),
            "category": "symbolic-execution",
            "tags": ["symbolic-execution", "ethereum", "official", "consensys"],
            "verified": True,
            "security_scanned": True,
            "status": "approved",
            "rating": 4.6,
            "download_count": 12000,
        },
    ]

    for plugin_data in builtin_plugins:
        plugin = MarketplacePlugin(
            id=plugin_data["id"],
            metadata=plugin_data["metadata"],
            capabilities=plugin_data["capabilities"],
            configuration=plugin_data["configuration"],
            category=plugin_data["category"],
            tags=plugin_data["tags"],
            verified=plugin_data.get("verified", False),
            security_scanned=plugin_data.get("security_scanned", False),
            status=plugin_data.get("status", "approved"),
            rating=plugin_data.get("rating", 0.0),
            download_count=plugin_data.get("download_count", 0),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        marketplace_plugins[plugin.id] = plugin


# Initialize on module load
initialize_builtin_plugins()


@router.get("/plugins")
async def search_plugins(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    language: Optional[str] = Query(None, description="Supported language"),
    blockchain: Optional[str] = Query(None, description="Supported blockchain"),
    min_rating: Optional[float] = Query(None, description="Minimum rating"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    verified_only: bool = Query(False, description="Only verified plugins"),
    sort_by: str = Query("popularity", description="Sort criteria"),
    limit: int = Query(20, description="Maximum results"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """Search and filter plugins in the marketplace"""
    try:
        plugins = list(marketplace_plugins.values())

        # Apply filters
        if category:
            plugins = [p for p in plugins if p.category == category]

        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            plugins = [
                p for p in plugins if any(
                    tag in p.tags for tag in tag_list)]

        if language:
            plugins = [
                p for p in plugins if language in p.capabilities.supported_languages]

        if blockchain:
            plugins = [
                p for p in plugins if blockchain in p.capabilities.supported_blockchains]

        if min_rating:
            plugins = [p for p in plugins if p.rating >= min_rating]

        if max_price is not None:
            plugins = [p for p in plugins if p.price <= max_price]

        if verified_only:
            plugins = [p for p in plugins if p.verified]

        # Only show approved plugins
        plugins = [p for p in plugins if p.status == "approved"]

        # Sort plugins
        if sort_by == "popularity":
            plugins.sort(key=lambda x: x.popularity_score, reverse=True)
        elif sort_by == "rating":
            plugins.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "downloads":
            plugins.sort(key=lambda x: x.download_count, reverse=True)
        elif sort_by == "newest":
            plugins.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "name":
            plugins.sort(key=lambda x: x.metadata.name)

        # Apply pagination
        total_count = len(plugins)
        plugins = plugins[offset: offset + limit]

        return {
            "plugins": plugins,
            "total_count": total_count,
            "page_size": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error(f"Error searching plugins: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to search plugins: {str(e)}"
        )


@router.get("/plugins/{plugin_id}")
async def get_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin"""
    try:
        if plugin_id not in marketplace_plugins:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin {plugin_id} not found")

        plugin = marketplace_plugins[plugin_id]
        reviews = plugin_reviews.get(plugin_id, [])

        return {
            "plugin": plugin,
            "reviews": reviews[:10],  # Show latest 10 reviews
            "total_reviews": len(reviews),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin details: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get plugin details: {str(e)}"
        )


@router.post("/plugins")
async def upload_plugin(
    upload_request: PluginUploadRequest,
    dockerfile: Optional[UploadFile] = File(None),
    token: str = Depends(security),
):
    """Upload a new plugin to the marketplace"""
    try:
        # Generate unique plugin ID
        plugin_id = f"{upload_request.metadata.name.lower().replace(' ',
                                                                    '-')}-{str(uuid.uuid4())[:8]}"

        # Validate plugin metadata
        if plugin_id in marketplace_plugins:
            raise HTTPException(
                status_code=400, detail="Plugin with this name already exists"
            )

        # Security validation
        if not upload_request.configuration.docker_image:
            raise HTTPException(
                status_code=400,
                detail="Docker image is required")

        # Create plugin entry
        plugin = MarketplacePlugin(
            id=plugin_id,
            metadata=upload_request.metadata,
            capabilities=upload_request.capabilities,
            configuration=upload_request.configuration,
            category=upload_request.category,
            tags=upload_request.tags,
            price=upload_request.price,
            status="pending",  # Requires approval
            created_at=datetime.now(),
            updated_at=datetime.now(),
            release_notes=upload_request.release_notes,
        )

        # Store plugin
        marketplace_plugins[plugin_id] = plugin

        logger.info(f"Plugin {plugin_id} uploaded by user, pending approval")

        return {
            "plugin_id": plugin_id,
            "status": "uploaded",
            "message": "Plugin uploaded successfully and is pending approval",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to upload plugin: {str(e)}"
        )


@router.post("/plugins/{plugin_id}/install")
async def install_plugin(
    plugin_id: str,
    install_request: PluginInstallRequest,
    token: str = Depends(security),
):
    """Install a plugin from the marketplace"""
    try:
        if plugin_id not in marketplace_plugins:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin {plugin_id} not found")

        plugin = marketplace_plugins[plugin_id]

        if plugin.status != "approved":
            raise HTTPException(
                status_code=400,
                detail="Plugin is not approved for installation")

        # Check if already installed
        if plugin_id in installed_plugins:
            return {
                "plugin_id": plugin_id,
                "status": "already_installed",
                "message": "Plugin is already installed",
            }

        # Install plugin (pull Docker image)
        if docker_client:
            try:
                docker_image = plugin.configuration.docker_image
                logger.info(f"Pulling Docker image: {docker_image}")

                # This would pull the image in production
                # docker_client.images.pull(docker_image)

                # Store installation record
                installed_plugins[plugin_id] = {
                    "plugin": plugin,
                    "installed_at": datetime.now(),
                    "version": install_request.version,
                    "configuration": install_request.configuration_override,
                }

                # Update download count
                plugin.download_count += 1

                logger.info(f"Plugin {plugin_id} installed successfully")

                return {
                    "plugin_id": plugin_id,
                    "status": "installed",
                    "message": "Plugin installed successfully",
                }

            except Exception as docker_error:
                logger.error(f"Docker error installing plugin: {docker_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to install plugin: {str(docker_error)}",
                )
        else:
            raise HTTPException(status_code=500, detail="Docker not available")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to install plugin: {str(e)}"
        )


@router.delete("/plugins/{plugin_id}/install")
async def uninstall_plugin(plugin_id: str, token: str = Depends(security)):
    """Uninstall a plugin"""
    try:
        if plugin_id not in installed_plugins:
            raise HTTPException(
                status_code=404, detail=f"Plugin {plugin_id} is not installed"
            )

        # Remove from installed plugins
        del installed_plugins[plugin_id]

        logger.info(f"Plugin {plugin_id} uninstalled successfully")

        return {
            "plugin_id": plugin_id,
            "status": "uninstalled",
            "message": "Plugin uninstalled successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to uninstall plugin: {str(e)}"
        )


@router.get("/installed")
async def list_installed_plugins(token: str = Depends(security)):
    """List all installed plugins"""
    try:
        return {
            "installed_plugins": list(installed_plugins.values()),
            "count": len(installed_plugins),
        }

    except Exception as e:
        logger.error(f"Error listing installed plugins: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list installed plugins: {
                str(e)}",
        )


@router.post("/plugins/{plugin_id}/reviews")
async def add_review(
    plugin_id: str,
    rating: int = Field(..., ge=1, le=5),
    title: str = Field(..., max_length=200),
    content: str = Field(..., max_length=2000),
    token: str = Depends(security),
):
    """Add a review for a plugin"""
    try:
        if plugin_id not in marketplace_plugins:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin {plugin_id} not found")

        # Create review
        review = PluginReview(
            id=str(uuid.uuid4()),
            plugin_id=plugin_id,
            user_id="current_user",  # Would get from token in production
            rating=rating,
            title=title,
            content=content,
            verified_purchase=plugin_id in installed_plugins,
            created_at=datetime.now(),
        )

        # Store review
        if plugin_id not in plugin_reviews:
            plugin_reviews[plugin_id] = []
        plugin_reviews[plugin_id].append(review)

        # Update plugin rating
        plugin = marketplace_plugins[plugin_id]
        all_reviews = plugin_reviews[plugin_id]
        plugin.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        plugin.review_count = len(all_reviews)

        return {
            "review_id": review.id,
            "status": "added",
            "message": "Review added successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add review: {
                str(e)}",
        )


@router.get("/categories")
async def get_categories():
    """Get all available plugin categories"""
    try:
        categories = {}
        for plugin in marketplace_plugins.values():
            if plugin.status == "approved":
                category = plugin.category
                if category not in categories:
                    categories[category] = {
                        "name": category,
                        "count": 0,
                        "description": f"Plugins for {category}",
                    }
                categories[category]["count"] += 1

        return {
            "categories": list(categories.values()),
            "total_categories": len(categories),
        }

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    try:
        approved_plugins = [
            p for p in marketplace_plugins.values() if p.status == "approved"
        ]

        return {
            "total_plugins": len(approved_plugins),
            "verified_plugins": len([p for p in approved_plugins if p.verified]),
            "total_downloads": sum(p.download_count for p in approved_plugins),
            "average_rating": (
                sum(p.rating for p in approved_plugins) / len(approved_plugins)
                if approved_plugins
                else 0
            ),
            "categories": len(set(p.category for p in approved_plugins)),
            "total_reviews": sum(len(reviews) for reviews in plugin_reviews.values()),
        }

    except Exception as e:
        logger.error(f"Error getting marketplace stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get marketplace stats: {
                str(e)}",
        )


# Admin endpoints (would require admin authentication in production)
@router.post("/admin/plugins/{plugin_id}/approve")
async def approve_plugin(plugin_id: str, token: str = Depends(security)):
    """Approve a pending plugin (admin only)"""
    try:
        if plugin_id not in marketplace_plugins:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin {plugin_id} not found")

        plugin = marketplace_plugins[plugin_id]
        plugin.status = "approved"
        plugin.approved_at = datetime.now()
        plugin.updated_at = datetime.now()

        return {
            "plugin_id": plugin_id,
            "status": "approved",
            "message": "Plugin approved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to approve plugin: {str(e)}"
        )


@router.post("/admin/plugins/{plugin_id}/verify")
async def verify_plugin(plugin_id: str, token: str = Depends(security)):
    """Verify a plugin as officially vetted (admin only)"""
    try:
        if plugin_id not in marketplace_plugins:
            raise HTTPException(
                status_code=404,
                detail=f"Plugin {plugin_id} not found")

        plugin = marketplace_plugins[plugin_id]
        plugin.verified = True
        plugin.security_scanned = True
        plugin.updated_at = datetime.now()

        return {
            "plugin_id": plugin_id,
            "status": "verified",
            "message": "Plugin verified successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying plugin: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to verify plugin: {str(e)}"
        )
