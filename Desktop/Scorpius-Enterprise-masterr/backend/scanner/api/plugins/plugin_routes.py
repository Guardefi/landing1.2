"""
Plugin API Routes for Scorpius Enterprise
Provides REST APIs for all security analysis plugins
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.models import Target
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sandbox.docker_plugin_manager import DockerPluginManager

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])

# Plugin Manager instance
plugin_manager = DockerPluginManager()


# Pydantic models for API
class ScanRequest(BaseModel):
    target: str
    source_code: Optional[str] = None
    contract_address: Optional[str] = None
    blockchain: str = "ethereum"
    plugins: List[str] = ["slither", "mythril", "manticore", "mythx"]
    config: Dict[str, Any] = {}


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str
    started_at: datetime


class ScanResult(BaseModel):
    scan_id: str
    plugin: str
    status: str
    findings: List[Dict[str, Any]]
    execution_time: float
    error: Optional[str] = None
    completed_at: datetime


class PluginInfo(BaseModel):
    name: str
    version: str
    description: str
    capabilities: List[str]
    status: str
    image: str
    memory_limit: str


class PluginStatus(BaseModel):
    available: bool
    running: bool
    last_used: Optional[datetime]
    total_scans: int
    success_rate: float


# In-memory storage for scan results (in production, use Redis/Database)
scan_results: Dict[str, Dict] = {}
active_scans: Dict[str, Dict] = {}


@router.get("/", response_model=List[PluginInfo])
async def list_plugins():
    """List all available security analysis plugins"""
    try:
        plugins = await plugin_manager.list_available_plugins()
        plugin_info = []

        for plugin_name, details in plugins.items():
            plugin_info.append(
                PluginInfo(
                    name=plugin_name,
                    version=details.get("version", "latest"),
                    description=details.get(
                        "description", f"{plugin_name.title()} security analysis"
                    ),
                    capabilities=details.get("capabilities", ["static_analysis"]),
                    status="available" if details.get("available") else "unavailable",
                    image=details.get("image", f"scorpius/{plugin_name}:latest"),
                    memory_limit=details.get("memory_limit", "512m"),
                )
            )

        return plugin_info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list plugins: {
                str(e)}",
        )


@router.get("/{plugin_name}/status", response_model=PluginStatus)
async def get_plugin_status(plugin_name: str):
    """Get status information for a specific plugin"""
    try:
        status = await plugin_manager.get_plugin_status(plugin_name)
        return PluginStatus(
            available=status.get("available", False),
            running=status.get("running", False),
            last_used=status.get("last_used"),
            total_scans=status.get("total_scans", 0),
            success_rate=status.get("success_rate", 0.0),
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not found")


@router.post("/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a security analysis scan using specified plugins"""
    scan_id = str(uuid.uuid4())

    # Validate plugins
    available_plugins = await plugin_manager.list_available_plugins()
    invalid_plugins = [p for p in request.plugins if p not in available_plugins]
    if invalid_plugins:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plugins: {
                ', '.join(invalid_plugins)}",
        )

    # Create target object
    target = Target(
        identifier=request.target, target_type="contract", blockchain=request.blockchain
    )

    # Store scan info
    scan_info = {
        "scan_id": scan_id,
        "target": request.target,
        "plugins": request.plugins,
        "status": "started",
        "started_at": datetime.now(),
        "results": {},
    }
    active_scans[scan_id] = scan_info

    # Start background scan
    background_tasks.add_task(
        execute_scan,
        scan_id,
        target,
        request.source_code,
        request.plugins,
        request.config,
    )

    return ScanResponse(
        scan_id=scan_id,
        status="started",
        message=f"Scan started with plugins: {', '.join(request.plugins)}",
        started_at=scan_info["started_at"],
    )


@router.get("/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Get the current status of a scan"""
    if scan_id not in active_scans and scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan_id in active_scans:
        return {
            "scan_id": scan_id,
            "status": active_scans[scan_id]["status"],
            "progress": active_scans[scan_id].get("progress", {}),
            "started_at": active_scans[scan_id]["started_at"],
        }
    else:
        return {
            "scan_id": scan_id,
            "status": "completed",
            "completed_at": scan_results[scan_id]["completed_at"],
            "total_findings": sum(
                len(r.get("findings", []))
                for r in scan_results[scan_id]["results"].values()
            ),
        }


@router.get("/scan/{scan_id}/results", response_model=List[ScanResult])
async def get_scan_results(scan_id: str):
    """Get the results of a completed scan"""
    if scan_id not in scan_results:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan still in progress")
        else:
            raise HTTPException(status_code=404, detail="Scan not found")

    results = []
    for plugin_name, result_data in scan_results[scan_id]["results"].items():
        results.append(
            ScanResult(
                scan_id=scan_id,
                plugin=plugin_name,
                status=result_data.get("status", "unknown"),
                findings=result_data.get("findings", []),
                execution_time=result_data.get("execution_time", 0.0),
                error=result_data.get("error"),
                completed_at=result_data.get("completed_at", datetime.now()),
            )
        )

    return results


@router.get("/scan/{scan_id}/results/{plugin_name}")
async def get_plugin_scan_result(scan_id: str, plugin_name: str):
    """Get the result of a specific plugin from a scan"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")

    if plugin_name not in scan_results[scan_id]["results"]:
        raise HTTPException(
            status_code=404, detail=f"No results for plugin {plugin_name}"
        )

    return scan_results[scan_id]["results"][plugin_name]


@router.post("/{plugin_name}/analyze")
async def analyze_with_plugin(
    plugin_name: str,
    target: str,
    source_code: Optional[str] = None,
    config: Dict[str, Any] = {},
):
    """Run analysis with a single plugin immediately"""
    try:
        # Create target object
        target_obj = Target(
            identifier=target, target_type="contract", blockchain="ethereum"
        )

        # Run single plugin analysis
        result = await plugin_manager.run_plugin(
            plugin_name=plugin_name,
            target=target_obj,
            source_code=source_code,
            config=config,
        )

        return {
            "plugin": plugin_name,
            "target": target,
            "status": "completed",
            "findings": result.get("findings", []),
            "execution_time": result.get("execution_time", 0.0),
            "completed_at": datetime.now(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin {plugin_name} analysis failed: {
                str(e)}",
        )


async def execute_scan(
    scan_id: str,
    target: Target,
    source_code: Optional[str],
    plugins: List[str],
    config: Dict[str, Any],
):
    """Execute scan in background"""
    try:
        # Update status
        active_scans[scan_id]["status"] = "running"
        active_scans[scan_id]["progress"] = {p: "pending" for p in plugins}

        # Run plugins in parallel
        tasks = []
        for plugin_name in plugins:
            task = asyncio.create_task(
                run_single_plugin(scan_id, plugin_name, target, source_code, config)
            )
            tasks.append(task)

        # Wait for all plugins to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Move to completed results
        scan_results[scan_id] = {
            "scan_id": scan_id,
            "completed_at": datetime.now(),
            "results": active_scans[scan_id]["results"],
        }

        # Remove from active scans
        del active_scans[scan_id]

    except Exception as e:
        # Handle scan failure
        active_scans[scan_id]["status"] = "failed"
        active_scans[scan_id]["error"] = str(e)


async def run_single_plugin(
    scan_id: str,
    plugin_name: str,
    target: Target,
    source_code: Optional[str],
    config: Dict[str, Any],
):
    """Run a single plugin and store results"""
    try:
        active_scans[scan_id]["progress"][plugin_name] = "running"

        start_time = datetime.now()
        result = await plugin_manager.run_plugin(
            plugin_name=plugin_name,
            target=target,
            source_code=source_code,
            config=config,
        )
        end_time = datetime.now()

        # Store result
        active_scans[scan_id]["results"][plugin_name] = {
            "status": "completed",
            "findings": result.get("findings", []),
            "execution_time": (end_time - start_time).total_seconds(),
            "completed_at": end_time,
        }

        active_scans[scan_id]["progress"][plugin_name] = "completed"

    except Exception as e:
        # Store error
        active_scans[scan_id]["results"][plugin_name] = {
            "status": "failed",
            "findings": [],
            "execution_time": 0.0,
            "error": str(e),
            "completed_at": datetime.now(),
        }

        active_scans[scan_id]["progress"][plugin_name] = "failed"
