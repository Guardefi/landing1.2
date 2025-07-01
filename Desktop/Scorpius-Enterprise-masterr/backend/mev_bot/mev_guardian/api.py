"""
MevGuardian FastAPI Application
Enterprise-grade API server with WebSocket support for React dashboard
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, List, Optional

import redis.asyncio as redis
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Security,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Import existing MEV components
from mev_api_server import UltimateMEVBot
from mev_guardian.config import OperatingMode, load_config
from mev_guardian.guardian_engine import GuardianEngine
from mev_guardian.types import ThreatType
from mev_strategies import StrategyType as MEVStrategyType
from pydantic import BaseModel, Field


# Pydantic Models for API
class SystemStatus(BaseModel):
    """System status response"""

    status: str
    mode: str
    uptime_seconds: float
    version: str
    timestamp: str


class GuardianStatus(BaseModel):
    """Guardian system status"""

    is_active: bool
    active_detectors: int
    threats_detected_total: int
    threats_detected_last_hour: int
    simulations_executed_total: int
    honeypots_identified_total: int
    active_simulations: int


class AttackStatus(BaseModel):
    """Attack system status"""

    is_active: bool
    active_strategies: List[str]
    opportunities_found_total: int
    opportunities_found_last_hour: int
    successful_executions: int
    failed_executions: int
    total_profit_eth: float


class ThreatResponse(BaseModel):
    """Threat detection response"""

    id: str
    threat_type: str
    severity: str
    confidence: float
    title: str
    description: str
    detected_at: str
    chain_id: int
    affected_protocols: List[str]
    potential_loss_usd: Optional[float]


class SimulationRequest(BaseModel):
    """Attack simulation request"""

    attack_type: str = Field(..., description="Type of attack to simulate")
    target_protocol: str = Field(..., description="Target protocol")
    chain_id: int = Field(default=1, description="Chain ID")
    fork_block: Optional[int] = Field(None, description="Block number to fork from")
    parameters: Dict = Field(default_factory=dict, description="Attack parameters")


class SimulationResponse(BaseModel):
    """Attack simulation response"""

    id: str
    status: str
    attack_type: str
    target_protocol: str
    success: Optional[bool]
    profit_extracted: Optional[float]
    gas_cost: Optional[float]
    duration_seconds: Optional[float]
    created_at: str
    error_message: Optional[str]


class HoneypotResponse(BaseModel):
    """Honeypot detection response"""

    id: str
    contract_address: str
    chain_id: int
    honeypot_type: str
    confidence: float
    risk_score: float
    detected_at: str
    estimated_victims: int
    total_funds_trapped: Optional[float]


class OpportunityResponse(BaseModel):
    """MEV opportunity response"""

    id: str
    strategy_type: str
    chain_id: int
    estimated_profit: float
    confidence_score: float
    discovered_at: str
    executed: bool
    net_profit: float


class StrategyToggleRequest(BaseModel):
    """Strategy enable/disable request"""

    strategy_type: str
    enabled: bool


class MetricsResponse(BaseModel):
    """System metrics response"""

    guardian_metrics: Dict
    attack_metrics: Dict
    system_metrics: Dict
    timestamp: str


# Global instances
config = None
guardian_engine: Optional[GuardianEngine] = None
mev_bot: Optional[UltimateMEVBot] = None
redis_client: Optional[redis.Redis] = None
websocket_connections: List[WebSocket] = []

# Security
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    """Verify API token"""
    if not config.security.api_key_required:
        return True

    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    # In production, verify JWT token
    # For now, simple token check
    expected_token = "mev-guardian-api-key"  # Should be from config
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global config, guardian_engine, mev_bot, redis_client

    # Startup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MevGuardianAPI")

    try:
        # Load configuration
        config = load_config()
        logger.info(f"🚀 Starting MevGuardian API in {config.mode.value} mode")

        # Initialize Redis
        redis_client = redis.from_url(config.redis.url)
        await redis_client.ping()
        logger.info("✅ Redis connected")

        # Initialize Guardian Engine (always available)
        guardian_engine = GuardianEngine(config)

        # Initialize MEV Bot (if attack mode enabled)
        if config.mode in [OperatingMode.ATTACK, OperatingMode.HYBRID]:
            mev_bot = UltimateMEVBot()
            logger.info("✅ MEV Bot initialized")

        # Start Guardian Engine
        if config.mode in [OperatingMode.GUARDIAN, OperatingMode.HYBRID]:
            await guardian_engine.start()
            logger.info("✅ Guardian Engine started")

        # Start MEV Bot
        if mev_bot and config.mode in [OperatingMode.ATTACK, OperatingMode.HYBRID]:
            await mev_bot.start_bot()
            logger.info("✅ MEV Bot started")

        # Start WebSocket broadcast task
        asyncio.create_task(websocket_broadcast_loop())

        logger.info("🎯 MevGuardian API ready!")

        yield

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    finally:
        # Shutdown
        logger.info("🛑 Shutting down MevGuardian API...")

        if guardian_engine:
            await guardian_engine.stop()

        if mev_bot:
            await mev_bot.stop_bot()

        if redis_client:
            await redis_client.close()

        logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="MevGuardian Enterprise API",
    description="Advanced MEV security platform with both offensive and defensive capabilities",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health and System Endpoints
@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/system/status", response_model=SystemStatus)
async def get_system_status(authenticated: bool = Depends(verify_token)):
    """Get overall system status"""
    uptime = 0
    if guardian_engine and guardian_engine.start_time:
        uptime = (
            datetime.now(timezone.utc) - guardian_engine.start_time
        ).total_seconds()

    return SystemStatus(
        status="running",
        mode=config.mode.value,
        uptime_seconds=uptime,
        version=config.version,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/v1/system/metrics", response_model=MetricsResponse)
async def get_system_metrics(authenticated: bool = Depends(verify_token)):
    """Get comprehensive system metrics"""

    guardian_metrics = {}
    attack_metrics = {}

    if guardian_engine:
        guardian_status = guardian_engine.get_status()
        guardian_metrics = guardian_status.get("metrics", {})

    if mev_bot:
        mev_status = mev_bot.get_bot_status()
        attack_metrics = {
            "total_profit": mev_status.total_profit,
            "total_opportunities": mev_status.total_opportunities,
            "active_strategies": mev_status.active_strategies,
            "uptime_seconds": mev_status.uptime_seconds,
        }

    return MetricsResponse(
        guardian_metrics=guardian_metrics,
        attack_metrics=attack_metrics,
        system_metrics={
            "websocket_connections": len(websocket_connections),
            "redis_connected": redis_client is not None,
            "mode": config.mode.value,
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/v1/system/mode")
async def switch_mode(mode: str, authenticated: bool = Depends(verify_token)):
    """Switch system operating mode"""
    try:
        OperatingMode(mode)

        # This would require restart in production
        # For now, just return the current mode

        return {
            "success": False,
            "message": "Mode switching requires system restart",
            "current_mode": config.mode.value,
            "requested_mode": mode,
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")


# Guardian Mode Endpoints
@app.get("/api/v1/guardian/status", response_model=GuardianStatus)
async def get_guardian_status(authenticated: bool = Depends(verify_token)):
    """Get Guardian system status"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    status = guardian_engine.get_status()

    return GuardianStatus(
        is_active=guardian_engine.is_running,
        active_detectors=status["active_detectors"],
        threats_detected_total=status["threats_detected"],
        threats_detected_last_hour=status["metrics"]["threats_detected_last_hour"],
        simulations_executed_total=status["metrics"]["simulations_executed_total"],
        honeypots_identified_total=status["metrics"]["honeypots_identified_total"],
        active_simulations=status["active_simulations"],
    )


@app.get("/api/v1/guardian/threats", response_model=List[ThreatResponse])
async def get_threats(
    hours: int = 24,
    severity: Optional[str] = None,
    threat_type: Optional[str] = None,
    authenticated: bool = Depends(verify_token),
):
    """Get recent threat detections"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    threats = guardian_engine.get_recent_threats(hours)

    # Apply filters
    if severity:
        threats = [t for t in threats if t.severity.value == severity]

    if threat_type:
        threats = [t for t in threats if t.threat_type.value == threat_type]

    return [
        ThreatResponse(
            id=threat.id,
            threat_type=threat.threat_type.value,
            severity=threat.severity.value,
            confidence=threat.confidence,
            title=threat.title,
            description=threat.description,
            detected_at=threat.detected_at.isoformat(),
            chain_id=threat.chain_id,
            affected_protocols=threat.affected_protocols,
            potential_loss_usd=threat.potential_loss_usd,
        )
        for threat in threats
    ]


@app.post("/api/v1/guardian/simulate", response_model=SimulationResponse)
async def create_simulation(
    request: SimulationRequest, authenticated: bool = Depends(verify_token)
):
    """Create and run attack simulation"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    try:
        # Validate attack type
        ThreatType(request.attack_type)

        simulation_config = {
            "attack_type": request.attack_type,
            "target_protocol": request.target_protocol,
            "chain_id": request.chain_id,
            "fork_block": request.fork_block,
            "parameters": request.parameters,
        }

        simulation = await guardian_engine.simulate_attack(simulation_config)

        return SimulationResponse(
            id=simulation.id,
            status=simulation.status.value,
            attack_type=simulation.simulation_type.value,
            target_protocol=simulation.target_protocol,
            success=simulation.success,
            profit_extracted=simulation.profit_extracted,
            gas_cost=simulation.gas_cost,
            duration_seconds=simulation.duration_seconds,
            created_at=simulation.created_at.isoformat(),
            error_message=simulation.error_message,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attack type: {
                request.attack_type}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {
                str(e)}",
        )


@app.get("/api/v1/guardian/simulations", response_model=List[SimulationResponse])
async def get_simulations(authenticated: bool = Depends(verify_token)):
    """Get all active and recent simulations"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    simulations = list(guardian_engine.active_simulations.values())

    return [
        SimulationResponse(
            id=sim.id,
            status=sim.status.value,
            attack_type=sim.simulation_type.value,
            target_protocol=sim.target_protocol,
            success=sim.success,
            profit_extracted=sim.profit_extracted,
            gas_cost=sim.gas_cost,
            duration_seconds=sim.duration_seconds,
            created_at=sim.created_at.isoformat(),
            error_message=sim.error_message,
        )
        for sim in simulations
    ]


@app.get(
    "/api/v1/guardian/simulations/{simulation_id}", response_model=SimulationResponse
)
async def get_simulation(
    simulation_id: str, authenticated: bool = Depends(verify_token)
):
    """Get specific simulation details"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    simulation = guardian_engine.active_simulations.get(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return SimulationResponse(
        id=simulation.id,
        status=simulation.status.value,
        attack_type=simulation.simulation_type.value,
        target_protocol=simulation.target_protocol,
        success=simulation.success,
        profit_extracted=simulation.profit_extracted,
        gas_cost=simulation.gas_cost,
        duration_seconds=simulation.duration_seconds,
        created_at=simulation.created_at.isoformat(),
        error_message=simulation.error_message,
    )


@app.get("/api/v1/guardian/honeypots", response_model=List[HoneypotResponse])
async def get_honeypots(authenticated: bool = Depends(verify_token)):
    """Get detected honeypot contracts"""
    if not guardian_engine:
        raise HTTPException(status_code=503, detail="Guardian engine not available")

    honeypots = guardian_engine.identified_honeypots

    return [
        HoneypotResponse(
            id=honeypot.id,
            contract_address=honeypot.contract_address,
            chain_id=honeypot.chain_id,
            honeypot_type=honeypot.honeypot_type,
            confidence=honeypot.confidence,
            risk_score=honeypot.risk_score,
            detected_at=honeypot.detected_at.isoformat(),
            estimated_victims=honeypot.estimated_victims,
            total_funds_trapped=honeypot.total_funds_trapped,
        )
        for honeypot in honeypots
    ]


# Attack Mode Endpoints
@app.get("/api/v1/mev/status", response_model=AttackStatus)
async def get_mev_status(authenticated: bool = Depends(verify_token)):
    """Get MEV bot status"""
    if not mev_bot:
        raise HTTPException(status_code=503, detail="MEV bot not available")

    status = mev_bot.get_bot_status()

    return AttackStatus(
        is_active=mev_bot.is_running,
        active_strategies=status.active_strategies,
        opportunities_found_total=status.total_opportunities,
        opportunities_found_last_hour=0,  # Would need to implement
        successful_executions=0,  # Would need to implement
        failed_executions=0,  # Would need to implement
        total_profit_eth=status.total_profit,
    )


@app.get("/api/v1/mev/strategies")
async def get_mev_strategies(authenticated: bool = Depends(verify_token)):
    """Get available MEV strategies"""
    if not mev_bot:
        raise HTTPException(status_code=503, detail="MEV bot not available")

    strategies = []
    for strategy_type, strategy in mev_bot.strategies.items():
        strategies.append(
            {
                "type": strategy_type.value,
                "name": strategy_type.value.replace("_", " ").title(),
                "enabled": strategy.enabled,
                "is_active": strategy.is_active,
                "stats": strategy.stats.to_dict(),
            }
        )

    return strategies


@app.post("/api/v1/mev/strategies/{strategy_type}/toggle")
async def toggle_mev_strategy(
    strategy_type: str,
    request: StrategyToggleRequest,
    authenticated: bool = Depends(verify_token),
):
    """Enable or disable MEV strategy"""
    if not mev_bot:
        raise HTTPException(status_code=503, detail="MEV bot not available")

    try:
        strategy_enum = MEVStrategyType(strategy_type)

        if request.enabled:
            success = await mev_bot.start_strategy(strategy_enum)
        else:
            success = await mev_bot.stop_strategy(strategy_enum)

        return {
            "success": success,
            "strategy_type": strategy_type,
            "enabled": request.enabled,
        }

    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid strategy type: {strategy_type}"
        )


@app.get("/api/v1/mev/opportunities", response_model=List[OpportunityResponse])
async def get_mev_opportunities(authenticated: bool = Depends(verify_token)):
    """Get recent MEV opportunities"""
    if not mev_bot:
        raise HTTPException(status_code=503, detail="MEV bot not available")

    opportunities = mev_bot.recent_opportunities

    return [
        OpportunityResponse(
            id=str(hash(str(opp.to_dict()))),  # Generate ID from hash
            strategy_type=opp.strategy_type.value,
            chain_id=1,  # Default
            estimated_profit=opp.estimated_profit,
            confidence_score=opp.confidence_score,
            discovered_at=datetime.fromtimestamp(
                opp.timestamp, timezone.utc
            ).isoformat(),
            executed=False,  # Would need to track
            net_profit=opp.estimated_profit,  # Simplified
        )
        for opp in opportunities[-50:]  # Last 50 opportunities
    ]


@app.get("/api/v1/mev/executions")
async def get_mev_executions(authenticated: bool = Depends(verify_token)):
    """Get MEV execution history"""
    if not mev_bot:
        raise HTTPException(status_code=503, detail="MEV bot not available")

    return mev_bot.recent_executions


# WebSocket Endpoints
@app.websocket("/ws/guardian/live")
async def guardian_websocket(websocket: WebSocket):
    """WebSocket for real-time Guardian updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


@app.websocket("/ws/mev/live")
async def mev_websocket(websocket: WebSocket):
    """WebSocket for real-time MEV updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


@app.websocket("/ws/system/live")
async def system_websocket(websocket: WebSocket):
    """WebSocket for real-time system updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def websocket_broadcast_loop():
    """Background task to broadcast updates to WebSocket clients"""
    while True:
        try:
            if websocket_connections:
                # Broadcast system status every 5 seconds
                status_data = {
                    "event_type": "system_status",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "active_connections": len(websocket_connections),
                        "mode": config.mode.value if config else "unknown",
                    },
                }

                # Send to all connected clients
                disconnected = []
                for websocket in websocket_connections:
                    try:
                        await websocket.send_json(status_data)
                    except BaseException:
                        disconnected.append(websocket)

                # Remove disconnected clients
                for ws in disconnected:
                    websocket_connections.remove(ws)

            await asyncio.sleep(5)

        except Exception as e:
            logging.error(f"WebSocket broadcast error: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    uvicorn.run(
        "mev_guardian.api:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
