"""
Simulation Service Backend API
Provides Python FastAPI wrapper for the simulation sandbox
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Simulation Service Router
router = APIRouter(prefix="/api/simulation", tags=["simulation"])

# Models for the simulation API
class SimulationRequest(BaseModel):
    contractAddress: str = Field(..., description="Target contract address")
    attackType: str = Field(..., description="Type of attack to simulate")
    options: Dict[str, Any] = Field(default_factory=dict, description="Advanced simulation options")

class SimulationStatus(BaseModel):
    simulation_id: str
    status: str
    progress: int
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class SimulationResult(BaseModel):
    simulation_id: str
    attackType: str
    contractAddress: str
    status: str
    vulnerabilityFound: bool
    exploitableValue: float
    gasUsed: int
    transactions: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    mitigation: List[str]
    riskScore: int
    executionTime: int

# In-memory storage for simulation state (in production, use Redis or database)
simulation_sessions: Dict[str, Dict[str, Any]] = {}

class SimulationService:
    def __init__(self):
        self.node_service_url = "http://localhost:3002"  # Node.js simulation service
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout for simulations
    
    async def start_simulation(self, request: SimulationRequest) -> str:
        """Start a new simulation and return simulation ID"""
        simulation_id = str(uuid.uuid4())
        
        # Create simulation session
        session = {
            "id": simulation_id,
            "status": "pending",
            "progress": 0,
            "start_time": datetime.now(),
            "request": request.dict(),
            "result": None,
            "error": None
        }
        
        simulation_sessions[simulation_id] = session
        
        try:
            # Call the Node.js simulation service
            response = await self.client.post(
                f"{self.node_service_url}/api/v1/simulations",
                json={
                    "type": self._map_attack_type(request.attackType),
                    "target": {
                        "contractAddress": request.contractAddress,
                        "contractCode": await self._get_contract_code(request.contractAddress)
                    },
                    "exploitParams": self._get_exploit_params(request.attackType, request.options),
                    "config": {
                        "timeout": request.options.get("timeout", 300000),
                        "gasLimit": int(request.options.get("gasLimit", 1000000)),
                        "fork": request.options.get("fork", True),
                        "verbose": request.options.get("verbose", False)
                    }
                },
                headers={"Authorization": "Bearer scorpius-api-token"}
            )
            
            if response.status_code == 200:
                node_result = response.json()
                session["node_simulation_id"] = node_result.get("simulationId")
                session["status"] = "running"
                simulation_sessions[simulation_id] = session
                
                # Start background task to monitor progress
                asyncio.create_task(self._monitor_simulation(simulation_id))
                
            else:
                session["status"] = "failed"
                session["error"] = f"Failed to start simulation: {response.status_code}"
                simulation_sessions[simulation_id] = session
                
        except Exception as e:
            session["status"] = "failed" 
            session["error"] = str(e)
            simulation_sessions[simulation_id] = session
            logger.error(f"Failed to start simulation {simulation_id}: {e}")
        
        return simulation_id
    
    async def get_simulation_status(self, simulation_id: str) -> Optional[SimulationStatus]:
        """Get the current status of a simulation"""
        session = simulation_sessions.get(simulation_id)
        if not session:
            return None
            
        return SimulationStatus(
            simulation_id=simulation_id,
            status=session["status"],
            progress=session["progress"],
            start_time=session["start_time"],
            end_time=session.get("end_time"),
            error=session.get("error")
        )
    
    async def get_simulation_result(self, simulation_id: str) -> Optional[SimulationResult]:
        """Get the result of a completed simulation"""
        session = simulation_sessions.get(simulation_id)
        if not session or session["status"] != "completed":
            return None
            
        return SimulationResult(**session["result"])
    
    async def abort_simulation(self, simulation_id: str) -> bool:
        """Abort a running simulation"""
        session = simulation_sessions.get(simulation_id)
        if not session:
            return False
            
        if session["status"] == "running" and "node_simulation_id" in session:
            try:
                # Call Node.js service to abort
                response = await self.client.post(
                    f"{self.node_service_url}/api/v1/simulations/{session['node_simulation_id']}/abort",
                    headers={"Authorization": "Bearer scorpius-api-token"}
                )
                
                session["status"] = "aborted"
                session["end_time"] = datetime.now()
                simulation_sessions[simulation_id] = session
                
                return response.status_code == 200
                
            except Exception as e:
                logger.error(f"Failed to abort simulation {simulation_id}: {e}")
                return False
        
        return False
    
    async def _monitor_simulation(self, simulation_id: str):
        """Background task to monitor simulation progress"""
        session = simulation_sessions.get(simulation_id)
        if not session or "node_simulation_id" not in session:
            return
            
        node_simulation_id = session["node_simulation_id"]
        
        try:
            while session["status"] == "running":
                # Check status from Node.js service
                response = await self.client.get(
                    f"{self.node_service_url}/api/v1/simulations/{node_simulation_id}/status",
                    headers={"Authorization": "Bearer scorpius-api-token"}
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    
                    session["progress"] = status_data.get("progress", 0)
                    session["status"] = status_data.get("status", "running")
                    
                    if session["status"] in ["completed", "failed", "timeout", "aborted"]:
                        session["end_time"] = datetime.now()
                        
                        if session["status"] == "completed":
                            # Get final result
                            result_response = await self.client.get(
                                f"{self.node_service_url}/api/v1/simulations/{node_simulation_id}/result",
                                headers={"Authorization": "Bearer scorpius-api-token"}
                            )
                            
                            if result_response.status_code == 200:
                                result_data = result_response.json()
                                session["result"] = self._format_simulation_result(
                                    simulation_id, 
                                    session["request"],
                                    result_data
                                )
                        
                        simulation_sessions[simulation_id] = session
                        break
                else:
                    session["status"] = "failed"
                    session["error"] = f"Failed to get status: {response.status_code}"
                    session["end_time"] = datetime.now()
                    simulation_sessions[simulation_id] = session
                    break
                
                simulation_sessions[simulation_id] = session
                await asyncio.sleep(2)  # Check every 2 seconds
                
        except Exception as e:
            session["status"] = "failed"
            session["error"] = str(e)
            session["end_time"] = datetime.now()
            simulation_sessions[simulation_id] = session
            logger.error(f"Error monitoring simulation {simulation_id}: {e}")
    
    def _map_attack_type(self, attack_type: str) -> str:
        """Map frontend attack types to Node.js simulation types"""
        mapping = {
            "flash_loan": "FULL_EXPLOIT",
            "reentrancy": "FULL_EXPLOIT", 
            "integer_overflow": "PROOF_OF_CONCEPT",
            "oracle_manipulation": "FULL_EXPLOIT"
        }
        return mapping.get(attack_type, "PROOF_OF_CONCEPT")
    
    def _get_exploit_params(self, attack_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get exploit-specific parameters"""
        base_params = {
            "gasPrice": int(options.get("gasPrice", 20)) * 10**9,  # Convert Gwei to Wei
            "gasLimit": int(options.get("gasLimit", 1000000)),
        }
        
        if attack_type == "flash_loan":
            base_params.update({
                "loanAmount": "1000000000000000000000",  # 1000 ETH
                "targetPair": "WETH/USDC"
            })
        elif attack_type == "reentrancy":
            base_params.update({
                "recursionDepth": 10,
                "withdrawAmount": "1000000000000000000"  # 1 ETH
            })
        
        return base_params
    
    async def _get_contract_code(self, contract_address: str) -> str:
        """Get contract bytecode from address"""
        try:
            # This would normally call an Ethereum RPC endpoint
            # For now, return a placeholder
            return "0x608060405234801561001057600080fd5b50..."
        except Exception as e:
            logger.error(f"Failed to get contract code for {contract_address}: {e}")
            return ""
    
    def _format_simulation_result(self, simulation_id: str, request: Dict[str, Any], node_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format Node.js simulation result for frontend"""
        return {
            "simulation_id": simulation_id,
            "attackType": request["attackType"],
            "contractAddress": request["contractAddress"],
            "status": "success" if node_result.get("result") == "SUCCESS" else "failed",
            "vulnerabilityFound": node_result.get("vulnerabilityFound", False),
            "exploitableValue": node_result.get("exploitableValue", 0),
            "gasUsed": node_result.get("gasUsed", 0),
            "transactions": node_result.get("transactions", []),
            "timeline": node_result.get("timeline", []),
            "mitigation": node_result.get("mitigation", []),
            "riskScore": node_result.get("riskScore", 0),
            "executionTime": node_result.get("executionTime", 0)
        }

# Global service instance
simulation_service = SimulationService()

# API Routes
@router.post("/run", response_model=Dict[str, str])
async def run_simulation(
    request: SimulationRequest,
    credentials: HTTPAuthorizationCredentials = security
):
    """Start a new simulation"""
    try:
        simulation_id = await simulation_service.start_simulation(request)
        return {
            "simulation_id": simulation_id,
            "status": "started",
            "message": "Simulation started successfully"
        }
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start simulation: {str(e)}"
        )

@router.get("/{simulation_id}/status", response_model=SimulationStatus)
async def get_simulation_status(
    simulation_id: str,
    credentials: HTTPAuthorizationCredentials = security
):
    """Get simulation status"""
    status_info = await simulation_service.get_simulation_status(simulation_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    return status_info

@router.get("/{simulation_id}/result", response_model=SimulationResult)
async def get_simulation_result(
    simulation_id: str,
    credentials: HTTPAuthorizationCredentials = security
):
    """Get simulation result"""
    result = await simulation_service.get_simulation_result(simulation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation result not found or simulation not completed"
        )
    return result

@router.post("/{simulation_id}/abort")
async def abort_simulation(
    simulation_id: str,
    credentials: HTTPAuthorizationCredentials = security
):
    """Abort a running simulation"""
    success = await simulation_service.abort_simulation(simulation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to abort simulation or simulation not found"
        )
    return {"message": "Simulation aborted successfully"}

@router.get("/history")
async def get_simulation_history(
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = security
):
    """Get simulation history"""
    # Get recent simulations
    recent_simulations = []
    for session_id, session in list(simulation_sessions.items())[-limit:]:
        recent_simulations.append({
            "simulation_id": session_id,
            "status": session["status"],
            "start_time": session["start_time"],
            "end_time": session.get("end_time"),
            "attack_type": session["request"]["attackType"],
            "contract_address": session["request"]["contractAddress"]
        })
    
    return {"simulations": recent_simulations}
