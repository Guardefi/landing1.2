"""
Enterprise FastAPI with WebSocket Support
Real-time bytecode analysis for security platforms
"""

from fastapi import FastAPI, HTTPException, Depends, Security, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import time
import logging
import yaml
import json
from pathlib import Path
from datetime import datetime
import uuid

from core.similarity_engine import SimilarityEngine
from utils.metrics import PerformanceMonitor
from api.websocket_manager import websocket_manager, realtime_queue

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Global engine instance
engine: Optional[SimilarityEngine] = None
monitor = PerformanceMonitor()

# Load configuration
config_path = Path("configs/engine_config.yaml")
if config_path.exists():
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
else:
    config = {}

api_config = config.get('api', {})

# Create FastAPI app
app = FastAPI(
    title="SCORPIUS Enterprise Bytecode Security Platform",
    description="Real-time bytecode similarity detection and threat analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
if api_config.get('enable_cors', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.get('cors_origins', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Enhanced Request/Response models
class RealtimeBytecodeAnalysisRequest(BaseModel):
    bytecode1: str = Field(..., description="First bytecode to analyze")
    bytecode2: str = Field(..., description="Second bytecode to analyze")
    analysis_type: str = Field("similarity", description="Type of analysis (similarity, threat_detection)")
    priority: str = Field("normal", description="Priority level (low, normal, high, critical)")
    callback_url: Optional[str] = Field(None, description="Webhook URL for results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class BatchAnalysisRequest(BaseModel):
    analyses: List[RealtimeBytecodeAnalysisRequest] = Field(..., description="Batch of analysis requests")
    batch_id: Optional[str] = Field(None, description="Custom batch identifier")

class ThreatDetectionRequest(BaseModel):
    bytecode: str = Field(..., description="Bytecode to analyze for threats")
    contract_address: Optional[str] = Field(None, description="Contract address if known")
    network: Optional[str] = Field("ethereum", description="Blockchain network")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

class LiveMonitoringRequest(BaseModel):
    contract_addresses: List[str] = Field(..., description="Contract addresses to monitor")
    analysis_types: List[str] = Field(["similarity", "threat_detection"], description="Types of analysis to perform")
    monitoring_duration: int = Field(3600, description="Monitoring duration in seconds")

class WebSocketSubscriptionRequest(BaseModel):
    event_types: List[str] = Field(..., description="Event types to subscribe to")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Event filters")

# Enhanced Response models
class RealtimeAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis identifier")
    status: str = Field(..., description="Analysis status")
    queued_at: datetime = Field(..., description="When the analysis was queued")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

class BatchAnalysisResponse(BaseModel):
    batch_id: str = Field(..., description="Batch identifier")
    total_analyses: int = Field(..., description="Total number of analyses in batch")
    queued_analyses: int = Field(..., description="Number of successfully queued analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    estimated_completion: datetime = Field(..., description="Estimated batch completion time")

class ThreatAnalysisResponse(BaseModel):
    threat_score: float = Field(..., description="Threat score between 0 and 1")
    threat_level: str = Field(..., description="Threat level (low, medium, high, critical)")
    indicators: List[Dict[str, Any]] = Field(..., description="Threat indicators found")
    recommendations: List[str] = Field(..., description="Security recommendations")
    confidence: float = Field(..., description="Confidence in the analysis")

class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="Overall system status")
    components: Dict[str, str] = Field(..., description="Component statuses")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    active_connections: int = Field(..., description="Number of active WebSocket connections")
    queue_size: int = Field(..., description="Current analysis queue size")

# Authentication dependency
async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not api_config.get('enable_auth', False):
        return None
    
    if credentials is None:
        raise HTTPException(status_code=401, detail="API key required")
    
    expected_key = api_config.get('api_key', 'your-secret-api-key')
    if credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return credentials.credentials

# Startup event
@app.on_event("startup")
async def startup_event():
    global engine
    logger.info("Starting SCORPIUS Enterprise Security Platform...")
    
    try:
        # Initialize the similarity engine
        engine_config = config.get('similarity_engine', {})
        engine = SimilarityEngine(engine_config)
        
        # Start real-time analysis queue processing
        asyncio.create_task(realtime_queue.start_processing(engine))
        
        # Start periodic cleanup task
        asyncio.create_task(periodic_cleanup())
        
        logger.info("Enterprise security platform initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize platform: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global engine
    logger.info("Shutting down SCORPIUS Enterprise Security Platform...")
    
    realtime_queue.stop_processing()
    
    if engine:
        await engine.cleanup()
    
    logger.info("Shutdown complete")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_ip: str = None):
    """WebSocket endpoint for real-time bytecode analysis updates"""
    connection_id = await websocket_manager.connect(websocket, client_ip or "unknown")
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "subscribe":
                event_types = message.get("event_types", [])
                await websocket_manager.subscribe(connection_id, event_types)
                
            elif message_type == "unsubscribe":
                event_types = message.get("event_types", [])
                await websocket_manager.unsubscribe(connection_id, event_types)
                
            elif message_type == "realtime_analysis":
                # Queue real-time analysis
                await realtime_queue.add_analysis_request({
                    "type": "similarity_analysis",
                    "bytecode1": message.get("bytecode1"),
                    "bytecode2": message.get("bytecode2"),
                    "bytecode1_hash": message.get("bytecode1_hash"),
                    "bytecode2_hash": message.get("bytecode2_hash"),
                    "connection_id": connection_id
                })
                
            elif message_type == "threat_analysis":
                # Queue threat analysis
                await realtime_queue.add_analysis_request({
                    "type": "threat_detection",
                    "bytecode": message.get("bytecode"),
                    "bytecode_hash": message.get("bytecode_hash"),
                    "indicators": message.get("indicators", []),
                    "connection_id": connection_id
                })
                
            elif message_type == "ping":
                # Heartbeat
                await websocket_manager.send_to_connection(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for connection {connection_id}: {e}")
        await websocket_manager.disconnect(connection_id)

# Real-time analysis endpoint
@app.post("/api/v2/analyze/realtime", response_model=RealtimeAnalysisResponse)
async def queue_realtime_analysis(
    request: RealtimeBytecodeAnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Queue bytecode analysis for real-time processing"""
    if not engine:
        raise HTTPException(status_code=503, detail="Analysis engine not available")
    
    analysis_id = str(uuid.uuid4())
    queued_at = datetime.utcnow()
    
    try:
        # Add to real-time queue
        await realtime_queue.add_analysis_request({
            "id": analysis_id,
            "type": request.analysis_type,
            "bytecode1": request.bytecode1,
            "bytecode2": request.bytecode2,
            "priority": request.priority,
            "callback_url": request.callback_url,
            "metadata": request.metadata
        })
        
        # Estimate completion time based on queue size and priority
        estimated_completion = queued_at
        
        return RealtimeAnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            queued_at=queued_at,
            estimated_completion=estimated_completion
        )
        
    except Exception as e:
        logger.error(f"Error queuing real-time analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch analysis endpoint
@app.post("/api/v2/analyze/batch", response_model=BatchAnalysisResponse)
async def queue_batch_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Queue multiple bytecode analyses for batch processing"""
    if not engine:
        raise HTTPException(status_code=503, detail="Analysis engine not available")
    
    batch_id = request.batch_id or str(uuid.uuid4())
    queued_count = 0
    failed_count = 0
    
    try:
        for analysis in request.analyses:
            try:
                await realtime_queue.add_analysis_request({
                    "id": str(uuid.uuid4()),
                    "batch_id": batch_id,
                    "type": analysis.analysis_type,
                    "bytecode1": analysis.bytecode1,
                    "bytecode2": analysis.bytecode2,
                    "priority": analysis.priority,
                    "callback_url": analysis.callback_url,
                    "metadata": analysis.metadata
                })
                queued_count += 1
            except Exception as e:
                logger.error(f"Failed to queue analysis: {e}")
                failed_count += 1
        
        estimated_completion = datetime.utcnow()  # Calculate based on queue size
        
        return BatchAnalysisResponse(
            batch_id=batch_id,
            total_analyses=len(request.analyses),
            queued_analyses=queued_count,
            failed_analyses=failed_count,
            estimated_completion=estimated_completion
        )
        
    except Exception as e:
        logger.error(f"Error processing batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Threat detection endpoint
@app.post("/api/v2/analyze/threats", response_model=ThreatAnalysisResponse)
async def analyze_threats(
    request: ThreatDetectionRequest,
    api_key: str = Depends(get_api_key)
):
    """Analyze bytecode for security threats"""
    if not engine:
        raise HTTPException(status_code=503, detail="Analysis engine not available")
    
    try:
        # Perform threat analysis
        threat_score = await analyze_threat_level(request.bytecode, request.context)
        
        # Determine threat level
        if threat_score >= 0.9:
            threat_level = "critical"
        elif threat_score >= 0.7:
            threat_level = "high"
        elif threat_score >= 0.4:
            threat_level = "medium"
        else:
            threat_level = "low"
        
        # Get threat indicators
        indicators = await get_threat_indicators(request.bytecode)
        
        # Generate recommendations
        recommendations = await generate_security_recommendations(threat_score, indicators)
        
        response = ThreatAnalysisResponse(
            threat_score=threat_score,
            threat_level=threat_level,
            indicators=indicators,
            recommendations=recommendations,
            confidence=0.85  # Mock confidence score
        )
        
        # Send real-time alert if high threat
        if threat_score > 0.7:
            await websocket_manager.send_threat_alert({
                "contract_address": request.contract_address,
                "threat_score": threat_score,
                "threat_level": threat_level,
                "network": request.network
            })
        
        return response
        
    except Exception as e:
        logger.error(f"Error in threat analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Live monitoring endpoint
@app.post("/api/v2/monitor/start")
async def start_live_monitoring(
    request: LiveMonitoringRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Start live monitoring of contract addresses"""
    monitoring_id = str(uuid.uuid4())
    
    # Start monitoring task
    background_tasks.add_task(
        monitor_contracts,
        monitoring_id,
        request.contract_addresses,
        request.analysis_types,
        request.monitoring_duration
    )
    
    return {
        "monitoring_id": monitoring_id,
        "status": "started",
        "contracts": request.contract_addresses,
        "duration": request.monitoring_duration
    }

# System health endpoint
@app.get("/api/v2/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        # Check engine status
        engine_status = "healthy" if engine else "unhealthy"
        
        # Get performance metrics
        performance_metrics = monitor.get_performance_summary()
        
        # Get WebSocket stats
        ws_stats = websocket_manager.get_connection_stats()
        
        components = {
            "similarity_engine": engine_status,
            "websocket_manager": "healthy",
            "realtime_queue": "healthy" if realtime_queue.processing else "stopped",
            "api_server": "healthy"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in components.values()) else "degraded"
        
        return SystemHealthResponse(
            status=overall_status,
            components=components,
            performance_metrics=performance_metrics,
            active_connections=ws_stats["total_connections"],
            queue_size=realtime_queue.queue.qsize() if realtime_queue.queue else 0
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stream analysis results
@app.get("/api/v2/stream/results")
async def stream_analysis_results(api_key: str = Depends(get_api_key)):
    """Stream analysis results as Server-Sent Events"""
    async def event_generator():
        while True:
            # This would connect to your result stream
            # For now, send periodic status updates
            yield f"data: {json.dumps({'type': 'status', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            await asyncio.sleep(5)
    
    return StreamingResponse(event_generator(), media_type="text/plain")

# WebSocket connection stats
@app.get("/api/v2/websocket/stats")
async def get_websocket_stats(api_key: str = Depends(get_api_key)):
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_stats()

# Utility functions
async def analyze_threat_level(bytecode: str, context: Dict[str, Any]) -> float:
    """Analyze threat level of bytecode"""
    threat_score = 0.0
    
    # Check for dangerous patterns
    dangerous_patterns = [
        ("selfdestruct", 0.4),
        ("delegatecall", 0.3),
        ("suicide", 0.4),
        ("create2", 0.2),
        ("call", 0.1)
    ]
    
    bytecode_lower = bytecode.lower()
    for pattern, weight in dangerous_patterns:
        if pattern in bytecode_lower:
            threat_score += weight
    
    return min(threat_score, 1.0)

async def get_threat_indicators(bytecode: str) -> List[Dict[str, Any]]:
    """Get list of threat indicators found in bytecode"""
    indicators = []
    
    patterns = {
        "selfdestruct": "Contract can self-destruct",
        "delegatecall": "Uses dangerous delegatecall",
        "suicide": "Contains suicide opcode",
        "create2": "Can create contracts with predictable addresses"
    }
    
    bytecode_lower = bytecode.lower()
    for pattern, description in patterns.items():
        if pattern in bytecode_lower:
            indicators.append({
                "type": "opcode_pattern",
                "pattern": pattern,
                "description": description,
                "severity": "high" if pattern in ["selfdestruct", "suicide"] else "medium"
            })
    
    return indicators

async def generate_security_recommendations(threat_score: float, indicators: List[Dict[str, Any]]) -> List[str]:
    """Generate security recommendations based on analysis"""
    recommendations = []
    
    if threat_score > 0.7:
        recommendations.append("🚨 HIGH RISK: This contract contains multiple dangerous patterns")
        recommendations.append("🔍 Perform detailed manual code review")
        recommendations.append("⚠️ Consider contract audit before deployment")
    
    for indicator in indicators:
        if indicator["pattern"] == "selfdestruct":
            recommendations.append("💣 Contract can self-destruct - verify proper access controls")
        elif indicator["pattern"] == "delegatecall":
            recommendations.append("🔄 Delegatecall detected - ensure target contract is trusted")
    
    if not recommendations:
        recommendations.append("✅ No immediate security concerns identified")
    
    return recommendations

async def monitor_contracts(monitoring_id: str, addresses: List[str], analysis_types: List[str], duration: int):
    """Background task to monitor contracts"""
    logger.info(f"Started monitoring {len(addresses)} contracts for {duration} seconds")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        # Mock monitoring - in real implementation, this would:
        # 1. Fetch latest transactions for each address
        # 2. Analyze new bytecode
        # 3. Send alerts via WebSocket
        
        await asyncio.sleep(10)  # Check every 10 seconds
        
        # Send status update
        await websocket_manager.send_system_status({
            "monitoring_id": monitoring_id,
            "status": "active",
            "contracts_monitored": len(addresses),
            "elapsed_time": int(time.time() - start_time)
        })
    
    logger.info(f"Monitoring session {monitoring_id} completed")

async def periodic_cleanup():
    """Periodic cleanup task"""
    while True:
        try:
            # Clean up stale WebSocket connections
            await websocket_manager.cleanup_stale_connections()
            
            # Other cleanup tasks...
            
            await asyncio.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

# Main function to run the server
def main():
    """Run the enterprise API server"""
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 8000)
    workers = api_config.get('workers', 1)
    
    logger.info(f"Starting SCORPIUS Enterprise Security Platform on {host}:{port}")
    
    uvicorn.run(
        "api.enterprise_main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        access_log=True,
        ws_ping_interval=20,
        ws_ping_timeout=10
    )

if __name__ == "__main__":
    main()
