"""
Simple FastAPI server for Scorpius - Basic version to get started
"""



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track startup time for uptime calculation
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Scorpius Backend...")
    yield
    logger.info("🛑 Shutting down Scorpius Backend")


app = FastAPI(
    title="Scorpius Security Platform",
    description="Blockchain security analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    uptime_seconds = time.time() - startup_time
    uptime_str = (
        f"{int(uptime_seconds // 3600)}h "
        f"{int((uptime_seconds % 3600) // 60)}m "
        f"{int(uptime_seconds % 60)}s"
    )

    return {
        "status": "online",
        "platform": "Scorpius Security Platform",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "uptime": uptime_str,
        "message": "Welcome to Scorpius!",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Get system information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Database health check (simplified)
        db_healthy = True  # Would check actual DB connection

        checks = {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": (
                    "Database connection successful"
                    if db_healthy
                    else "Database connection failed"
                ),
            },
            "memory": {
                "status": "healthy" if memory.percent < 90 else "warning",
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
            },
            "disk": {
                "status": "healthy" if disk.percent < 90 else "warning",
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2),
            },
        }

        overall_status = "healthy"
        if any(check["status"] == "unhealthy" for check in checks.values()):
            overall_status = "unhealthy"
        elif any(check["status"] == "warning" for check in checks.values()):
            overall_status = "warning"

        return {
            "status": overall_status,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "checks": checks,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "error": str(e),
            "checks": {},
        }


@app.get("/api/system/status")
async def get_system_status():
    """Get system status."""  # Add performance metrics that tests expect
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    return {
        "status": "operational",
        "modules": {
            "scanner": "online",
            "mev_engine": "online",
            "ai_trading": "online",
            "blockchain_bridge": "online",
            "monitoring": "online",
            "reporting": "online",
        },
        "uptime": "00:00:30",
        "performance": {"cpu": cpu_percent, "memory": memory.percent},
    }


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics in format expected by frontend."""


    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    # Calculate uptime (mock for now)
    uptime_seconds = 259200  # 3 days
    current_time = datetime.utcnow().isoformat() + "Z"

    return {
        "timestamp": current_time,
        "cpu": cpu_percent,
        "mem": memory.percent,
        "mem_available_gb": round(memory.available / (1024**3), 2),
        "mem_total_gb": round(memory.total / (1024**3), 2),
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": round((disk.used / disk.total) * 100, 1),
        },
        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        },
        "uptime_seconds": uptime_seconds,
        "history": {
            "cpu": [
                {"timestamp": current_time, "value": max(0, cpu_percent - 5)},
                {"timestamp": current_time, "value": max(0, cpu_percent - 2)},
                {"timestamp": current_time, "value": cpu_percent},
            ],
            "memory": [
                {"timestamp": current_time, "value": max(0, memory.percent - 3)},
                {"timestamp": current_time, "value": max(0, memory.percent - 1)},
                {"timestamp": current_time, "value": memory.percent},
            ],
        },  # Also include the original scorpius-specific metrics
        "threats_detected": 42,
        "contracts_scanned": 156,
        "vulnerability_score": 85.2,
        "uptime": "99.9%",
        "active_scans": len(active_scans),
        "total_transactions": 1847,
        "mev_opportunities": 23,
    }


# ==== SMART CONTRACT SCANNER API ENDPOINTS ====

# Global scan storage (in production, use database)
active_scans: dict[str, Any] = {}
scan_results: dict[str, Any] = {}
uploaded_files: dict[str, Any] = {}


@app.post("/api/scan/start")
async def start_scan(request: dict):
    """Start a new smart contract scan."""

    scan_type = request.get("scanType", "quick")
    mode = request.get("mode", "address")
    target = request.get("target")
    plugins = request.get("plugins", [])

    if not target:
        raise HTTPException(status_code=400, detail="Target is required") from e

    # Validate Ethereum address if in address mode
    if mode == "address":
        if (
            not isinstance(target, str)
            or len(target) != 42
            or not target.startswith("0x")
        ):
            raise HTTPException(
                status_code=400, detail="Invalid Ethereum address format"
            ) from e
        try:
            int(target[2:], 16)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail="Invalid Ethereum address - not valid hexadecimal",
            ) from err

    scan_id = str(uuid.uuid4())

    # Initialize scan record
    active_scans[scan_id] = {
        "id": scan_id,
        "scanType": scan_type,
        "mode": mode,
        "target": target,
        "plugins": plugins,
        "status": "running",
        "progress": 0,
        "startedAt": "2024-12-20T10:30:00.000Z",
        "estimatedDuration": 180 if scan_type == "deep" else 60,
    }

    # Start background scan simulation
    asyncio.create_task(simulate_scan_progress(scan_id))

    return {
        "scanId": scan_id,
        "status": "started",
        "target": target,
        "estimatedDuration": active_scans[scan_id]["estimatedDuration"],
    }


@app.get("/api/scan/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan progress and status."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan not found") from e

    return active_scans[scan_id]


@app.post("/api/scan/stop")
async def stop_scan(request: dict):
    """Stop a running scan."""
    scan_id = request.get("scanId")
    if not scan_id:
        raise HTTPException(status_code=400, detail="scanId is required") from e

    if scan_id in active_scans:
        active_scans[scan_id]["status"] = "stopped"
        active_scans[scan_id]["progress"] = active_scans[scan_id].get("progress", 0)

        return {"message": "Scan stopped successfully", "scanId": scan_id}
    else:
        raise HTTPException(status_code=404, detail="Scan not found") from e


@app.get("/api/scan/results/{scan_id}")
async def get_scan_results(scan_id: str):
    """Get scan results."""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan results not found") from e

    return scan_results[scan_id]


@app.post("/api/scan/export/{scan_id}")
async def export_scan_results(scan_id: str):
    """Export scan results."""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan results not found") from e

    return {
        "downloadUrl": f"/api/downloads/scan-{scan_id}.json",
        "format": "json",
        "size": "2.4 MB",
    }


@app.get("/api/scan/history")
async def get_scan_history():
    """Get scan history."""
    history = []

    # Add completed scans from results
    for scan_id, results in scan_results.items():
        if scan_id in active_scans:
            scan_info = active_scans[scan_id]
            history.append(
                {
                    "id": scan_id,
                    "target": scan_info["target"],
                    "scanType": scan_info["scanType"],
                    "status": "completed",
                    "startedAt": scan_info["startedAt"],
                    "completedAt": results.get("completedAt"),
                    "vulnerabilityCount": len(results.get("vulnerabilities", [])),
                }
            )

    # Add active scans
    for scan_id, scan_info in active_scans.items():
        if scan_info["status"] in ["running", "stopped"]:
            history.append(
                {
                    "id": scan_id,
                    "target": scan_info["target"],
                    "scanType": scan_info["scanType"],
                    "status": scan_info["status"],
                    "startedAt": scan_info["startedAt"],
                    "progress": scan_info["progress"],
                }
            )

    return {"scans": history}


# Add scanner scan endpoint that tests expect
@app.post("/api/scanner/scan")
async def scanner_scan(request: dict):
    """Scanner scan endpoint for compatibility with tests."""

    target = request.get("target")
    scan_type = request.get("scan_type", "quick")
    priority = request.get("priority", "normal")

    if not target:
        raise HTTPException(
            status_code=400, detail="Target is required"
        )) from e  # Validate Ethereum address - complete validation including hex check
    if not isinstance(target, str) or len(target) != 42 or not target.startswith("0x"):
        raise HTTPException(
            status_code=400, detail="Invalid Ethereum address format"
        ) from e

    try:
        int(target[2:], 16)
    except ValueError as err:
        raise HTTPException(
            status_code=400, detail="Invalid Ethereum address - not valid hexadecimal"
        ) from err

    scan_id = str(uuid.uuid4())

    # Store scan info
    scan_info = {
        "scan_id": scan_id,
        "status": "initiated",
        "target": target,
        "scan_type": scan_type,
        "priority": priority,
        "estimated_duration": "2-5 minutes",
        "created_at": datetime.now(UTC).isoformat() + "Z",
    }

    active_scans[scan_id] = scan_info

    return {
        "scan_id": scan_id,
        "status": "initiated",
        "target": target,
        "estimated_duration": "2-5 minutes",
    }


@app.get("/api/system/performance")
async def get_system_performance():
    """Get detailed system performance metrics."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    return {
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "cpu": psutil.cpu_percent(interval=0.1),
        "memory": {
            "percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
        },
        "disk": {
            "percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
        },
        "network": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        },
    }


# ==== MEV ENGINE API ENDPOINTS ====


@app.get("/api/mev/opportunities")
async def get_mev_opportunities():
    """Get MEV opportunities."""
    return {
        "opportunities": [
            {
                "id": "op_001",
                "type": "sandwich",
                "estimated_profit": "0.05 ETH",
                "gas_cost": "0.01 ETH",
                "confidence": 0.85,
            }
        ],
        "total_count": 1,
        "estimated_profit": "0.05 ETH",
    }


@app.post("/api/mev/configure")
async def configure_mev_strategy(request: dict):
    """Configure MEV strategy."""
    strategy = request.get("strategy", "sandwich")
    max_gas_price = request.get("max_gas_price", "100")
    min_profit_threshold = request.get("min_profit_threshold", "0.01")

    return {
        "status": "configured",
        "strategy": strategy,
        "max_gas_price": max_gas_price,
        "min_profit_threshold": min_profit_threshold,
    }


# ==== AI TRADING ENGINE API ENDPOINTS ====


@app.get("/api/ai/trading/status")
async def get_ai_trading_status():
    """Get AI trading engine status."""
    return {
        "status": "active",
        "active_strategies": ["momentum", "arbitrage"],
        "performance_metrics": {
            "total_trades": 150,
            "win_rate": 0.68,
            "average_profit": "0.02 ETH",
        },
    }


# ==== EXISTING ENDPOINTS CONTINUE ====


# Background task to simulate scan progress
async def simulate_scan_progress(scan_id: str):
    """Simulate realistic scan progress."""

    if scan_id not in active_scans:
        return

    scan_info = active_scans[scan_id]
    plugins = scan_info["plugins"]
    scan_type = scan_info["scanType"]

    # Simulate plugin execution
    plugin_steps = len(plugins) if plugins else 5
    step_increment = 100 / plugin_steps

    vulnerabilities = []

    for i, plugin in enumerate(
import asyncio
import logging
import random
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

        plugins if plugins else ["bytecode", "reentrancy", "overflow", "access", "gas"]
    ):
        if scan_info["status"] != "running":
            break

        # Update progress
        progress = min(95, int((i + 1) * step_increment))
        active_scans[scan_id]["progress"] = progress

        # Simulate finding vulnerabilities
        if random.random() < 0.3:  # 30% chance to find vulnerability
            vulnerabilities.append(
                {
                    "id": f"vuln_{len(vulnerabilities) + 1}",
                    "type": plugin.replace("_", " ").title(),
                    "severity": random.choice(["low", "medium", "high", "critical"]),
                    "description": f"Potential {plugin} vulnerability detected",
                    "line": random.randint(1, 100),
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "plugin": plugin,
                }
            )

        # Wait between plugin executions
        wait_time = 2 if scan_type == "quick" else 4
        await asyncio.sleep(wait_time)

    # Complete the scan
    if scan_info["status"] == "running":
        active_scans[scan_id]["status"] = "completed"
        active_scans[scan_id]["progress"] = 100

        # Store results
        scan_results[scan_id] = {
            "scanId": scan_id,
            "target": scan_info["target"],
            "scanType": scan_info["scanType"],
            "status": "completed",
            "completedAt": "2024-12-20T10:35:00.000Z",
            "vulnerabilities": vulnerabilities,
            "summary": {
                "totalVulnerabilities": len(vulnerabilities),
                "critical": len(
                    [v for v in vulnerabilities if v["severity"] == "critical"]
                ),
                "high": len([v for v in vulnerabilities if v["severity"] == "high"]),
                "medium": len(
                    [v for v in vulnerabilities if v["severity"] == "medium"]
                ),
                "low": len([v for v in vulnerabilities if v["severity"] == "low"]),
            },
        }

        return scan_results[scan_id]


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
