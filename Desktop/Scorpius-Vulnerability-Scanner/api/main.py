"""
FastAPI application for Scorpius Vulnerability Scanner
Enterprise-grade REST API with authentication, monitoring, and async support
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from core.engine import ScanEngine
from core.enhanced_plugin_manager import EnhancedPluginManager
from core.models import Target, ScanConfig, ScanType
from exploitation.simulation_engine import SimulationType
from api.plugins.plugin_routes import router as plugin_router
from api.plugins.marketplace import router as marketplace_router
from api.results import router as results_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scorpius.api")

# Initialize FastAPI application
app = FastAPI(
    title="Scorpius Vulnerability Scanner API",
    description="Enterprise-grade smart contract vulnerability scanner with simulation capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(plugin_router, prefix="/api/v1", tags=["plugins"])
app.include_router(marketplace_router, prefix="/api/v1", tags=["marketplace"])
app.include_router(results_router, prefix="/api/v1", tags=["results"])

# Security
security = HTTPBearer()

# Global instances
scan_engine: Optional[ScanEngine] = None
plugin_manager: Optional[EnhancedPluginManager] = None

# Pydantic models for API
class ScanRequest(BaseModel):
    target_type: str = Field(..., description="Type of target (file, source_code, contract_address)")
    target_identifier: str = Field(..., description="Target identifier (path, code, address)")
    scan_type: str = Field(default="full", description="Type of scan (static, dynamic, full, quick)")
    plugins: Optional[List[str]] = Field(default=None, description="Specific plugins to use")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Additional configuration")

class SimulationRequest(BaseModel):
    vulnerability_id: str = Field(..., description="ID of vulnerability to simulate")
    simulation_type: str = Field(default="poc", description="Type of simulation")
    target_identifier: str = Field(..., description="Target identifier")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Simulation configuration")

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    scan_id: str
    status: str
    progress: float
    findings_count: int
    current_plugin: Optional[str]
    start_time: str
    estimated_completion: Optional[str]

class PluginInfo(BaseModel):
    name: str
    version: str
    description: str
    capabilities: Dict[str, Any]
    status: str

# Dependency injection
async def get_scan_engine() -> ScanEngine:
    global scan_engine
    if scan_engine is None:
        scan_engine = ScanEngine()
    return scan_engine

async def get_plugin_manager() -> EnhancedPluginManager:
    global plugin_manager
    if plugin_manager is None:
        plugin_manager = EnhancedPluginManager()
        # Initialize common plugins
        await plugin_manager.initialize_plugins(["slither", "mythril", "mythx"])
    return plugin_manager

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token (placeholder implementation)"""
    if credentials.credentials == "scorpius-api-token":
        return credentials.credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/scan", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token),
    engine: ScanEngine = Depends(get_scan_engine)
):
    """Start a new vulnerability scan"""
    try:
        # Create target object
        target = Target(
            type=request.target_type,
            identifier=request.target_identifier,
            path=request.target_identifier if request.target_type == "file" else None,
            content=request.target_identifier if request.target_type == "source_code" else None
        )
        
        # Create scan configuration
        scan_config = ScanConfig()
        if request.config:
            scan_config.custom_options.update(request.config)
        if request.plugins:
            scan_config.custom_options["plugins"] = request.plugins
        
        # Map scan type
        scan_type_mapping = {
            "static": ScanType.STATIC,
            "dynamic": ScanType.DYNAMIC,
            "full": ScanType.FULL,
            "quick": ScanType.QUICK
        }
        scan_type = scan_type_mapping.get(request.scan_type, ScanType.FULL)
        
        # Start scan
        scan_id = await engine.start_scan(target, scan_type, scan_config)
        
        return ScanResponse(
            scan_id=scan_id,
            status="started",
            message=f"Scan {scan_id} started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scan: {str(e)}"
        )

@app.get("/api/v1/scan/{scan_id}/status", response_model=StatusResponse)
async def get_scan_status(
    scan_id: str,
    token: str = Depends(verify_token),
    engine: ScanEngine = Depends(get_scan_engine)
):
    """Get status of a scan"""
    try:
        scan_result = engine.get_scan_status(scan_id)
        
        if not scan_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
        
        return StatusResponse(
            scan_id=scan_id,
            status=scan_result.status.value,
            progress=scan_result.progress,
            findings_count=len(scan_result.findings),
            current_plugin=scan_result.current_plugin,
            start_time=scan_result.start_time,
            estimated_completion=scan_result.estimated_completion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan status: {str(e)}"
        )

@app.get("/api/v1/scan/{scan_id}/results")
async def get_scan_results(
    scan_id: str,
    token: str = Depends(verify_token),
    engine: ScanEngine = Depends(get_scan_engine)
):
    """Get results of a completed scan"""
    try:
        scan_result = engine.get_scan_status(scan_id)
        
        if not scan_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )
        
        return {
            "scan_id": scan_id,
            "status": scan_result.status.value,
            "target": scan_result.target.__dict__,
            "scan_type": scan_result.scan_type.value,
            "start_time": scan_result.start_time,
            "end_time": scan_result.end_time,
            "duration": scan_result.duration,
            "findings": [finding.__dict__ for finding in scan_result.findings],
            "summary": {
                "total_findings": len(scan_result.findings),
                "high_severity": len([f for f in scan_result.findings if f.severity == "high"]),
                "medium_severity": len([f for f in scan_result.findings if f.severity == "medium"]),
                "low_severity": len([f for f in scan_result.findings if f.severity == "low"]),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan results: {str(e)}"
        )

@app.post("/api/v1/simulation", response_model=SimulationResponse)
async def start_simulation(
    request: SimulationRequest,
    token: str = Depends(verify_token),
    plugin_manager: EnhancedPluginManager = Depends(get_plugin_manager)
):
    """Start a new exploit simulation"""
    try:
        # This is a simplified implementation
        # In practice, you'd need to look up the vulnerability from the database
        from core.models import VulnerabilityFinding
        
        # Create a mock vulnerability (replace with actual lookup)
        vulnerability = VulnerabilityFinding(
            id=request.vulnerability_id,
            category="reentrancy",
            title="Mock Vulnerability",
            description="Mock vulnerability for simulation",
            severity="high",
            confidence=0.9,
            location={"line": 42, "filename": "contract.sol"},
            plugin="mock"
        )
        
        # Create target
        target = Target(
            type="source_code",
            identifier=request.target_identifier
        )
        
        # Map simulation type
        simulation_type_mapping = {
            "poc": SimulationType.PROOF_OF_CONCEPT,
            "full_exploit": SimulationType.FULL_EXPLOIT,
            "impact_assessment": SimulationType.IMPACT_ASSESSMENT,
            "attack_chain": SimulationType.ATTACK_CHAIN,
            "mitigation_test": SimulationType.MITIGATION_TEST
        }
        simulation_type = simulation_type_mapping.get(
            request.simulation_type, 
            SimulationType.PROOF_OF_CONCEPT
        )
        
        # Start simulation
        simulation_id = await plugin_manager.run_simulation(
            "mock_plugin", vulnerability, target, simulation_type
        )
        
        return SimulationResponse(
            simulation_id=simulation_id,
            status="started",
            message=f"Simulation {simulation_id} started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start simulation: {str(e)}"
        )

@app.get("/api/v1/plugins", response_model=List[PluginInfo])
async def list_plugins(
    token: str = Depends(verify_token),
    plugin_manager: EnhancedPluginManager = Depends(get_plugin_manager)
):
    """List available plugins"""
    try:
        plugins = []
        for plugin_name in plugin_manager.list_plugins():
            metadata = plugin_manager.plugin_metadata.get(plugin_name)
            if metadata:
                plugins.append(PluginInfo(
                    name=metadata.name,
                    version=metadata.version,
                    description=metadata.description,
                    capabilities=metadata.capabilities.__dict__,
                    status="available"
                ))
        
        return plugins
        
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list plugins: {str(e)}"
        )

@app.post("/api/v1/plugins/{plugin_name}/initialize")
async def initialize_plugin(
    plugin_name: str,
    token: str = Depends(verify_token),
    plugin_manager: EnhancedPluginManager = Depends(get_plugin_manager)
):
    """Initialize a specific plugin"""
    try:
        result = await plugin_manager.initialize_plugins([plugin_name])
        
        if result.get(plugin_name, False):
            return {"status": "success", "message": f"Plugin {plugin_name} initialized"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize plugin {plugin_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing plugin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize plugin: {str(e)}"
        )

@app.get("/api/v1/metrics")
async def get_metrics(token: str = Depends(verify_token)):
    """Get system metrics"""
    try:
        # Placeholder metrics - implement with actual monitoring
        return {
            "scans": {
                "total": 0,
                "active": 0,
                "completed": 0,
                "failed": 0
            },
            "simulations": {
                "total": 0,
                "active": 0,
                "completed": 0
            },
            "plugins": {
                "available": len(plugin_manager.list_plugins()) if plugin_manager else 0,
                "initialized": len(plugin_manager.plugins) if plugin_manager else 0
            },
            "system": {
                "uptime": "0h 0m",
                "memory_usage": "0%",
                "cpu_usage": "0%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Scorpius API server...")
    
    # Initialize scan engine
    global scan_engine
    scan_engine = ScanEngine()
    
    # Initialize plugin manager
    global plugin_manager
    plugin_manager = EnhancedPluginManager()
    
    logger.info("Scorpius API server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Scorpius API server...")
    
    if plugin_manager:
        await plugin_manager.cleanup()
    
    logger.info("Scorpius API server shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
