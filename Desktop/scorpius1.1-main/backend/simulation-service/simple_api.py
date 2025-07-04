#!/usr/bin/env python3
"""
Simple Simulation API Server
Provides basic simulation endpoints for the Scorpius platform
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulation_service")

# Initialize FastAPI application
app = FastAPI(
    title="Scorpius Simulation Service",
    description="Advanced blockchain vulnerability simulation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SimulationRequest(BaseModel):
    contractAddress: str
    attackType: str
    options: Optional[Dict[str, Any]] = {}

class SimulationResponse(BaseModel):
    scan_id: str
    status: str
    message: str

class SimulationResult(BaseModel):
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
    executionTime: float
    simulation_results: Dict[str, Any]
    exploit_simulations: List[Dict[str, Any]]
    attack_vectors: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    timestamp: str

# In-memory storage for simulations
simulations: Dict[str, Dict[str, Any]] = {}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="simulation",
        timestamp=datetime.now().isoformat()
    )

@app.get("/capabilities")
async def get_capabilities():
    """Get simulation service capabilities"""
    return {
        "name": "simulation",
        "version": "1.0.0",
        "description": "Advanced blockchain vulnerability simulation service",
        "supported_attacks": [
            "flash_loan", 
            "reentrancy", 
            "integer_overflow", 
            "oracle_manipulation"
        ],
        "features": [
            "exploit-simulation",
            "attack-vector-analysis", 
            "risk-assessment",
            "vulnerability-testing",
            "sandbox-execution"
        ]
    }

@app.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """Start a new simulation"""
    try:
        scan_id = str(uuid.uuid4())
        
        # Store simulation metadata
        simulations[scan_id] = {
            "scan_id": scan_id,
            "status": "running",
            "contractAddress": request.contractAddress,
            "attackType": request.attackType,
            "options": request.options,
            "start_time": datetime.now().isoformat(),
            "progress": 0
        }
        
        # Start simulation in background
        asyncio.create_task(run_simulation_background(scan_id))
        
        return SimulationResponse(
            scan_id=scan_id,
            status="started",
            message=f"Simulation {scan_id} started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")

@app.get("/status/{scan_id}")
async def get_simulation_status(scan_id: str):
    """Get simulation status"""
    if scan_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = simulations[scan_id]
    return {
        "scan_id": scan_id,
        "status": sim["status"],
        "progress": sim.get("progress", 0),
        "message": f"Simulation {sim['status']}"
    }

@app.get("/results/{scan_id}", response_model=SimulationResult)
async def get_simulation_results(scan_id: str):
    """Get simulation results"""
    if scan_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    sim = simulations[scan_id]
    
    if sim["status"] != "completed":
        raise HTTPException(status_code=400, detail="Simulation not completed yet")
    
    return sim["results"]

@app.get("/history")
async def get_simulation_history(limit: int = 10):
    """Get simulation history"""
    history = list(simulations.values())
    history.sort(key=lambda x: x["start_time"], reverse=True)
    return {"simulations": history[:limit]}

async def run_simulation_background(scan_id: str):
    """Run simulation in background"""
    try:
        sim = simulations[scan_id]
        
        # Simulate processing steps
        steps = ["initializing", "analyzing", "exploiting", "validating", "reporting"]
        
        for i, step in enumerate(steps):
            await asyncio.sleep(1)  # Simulate work
            sim["progress"] = int((i + 1) / len(steps) * 100)
            sim["current_step"] = step
            
        # Generate mock results
        vulnerability_found = True  # For demo purposes
        attack_type = sim["attackType"]
        
        results = SimulationResult(
            attackType=attack_type,
            contractAddress=sim["contractAddress"],
            status="success" if vulnerability_found else "failed",
            vulnerabilityFound=vulnerability_found,
            exploitableValue=50000.0 if vulnerability_found else 0.0,
            gasUsed=350000,
            transactions=[
                {
                    "type": "setup",
                    "hash": f"0x{uuid.uuid4().hex[:64]}",
                    "success": True,
                    "value": "0",
                    "gasUsed": 50000
                },
                {
                    "type": "exploit",
                    "hash": f"0x{uuid.uuid4().hex[:64]}",
                    "success": vulnerability_found,
                    "value": "5.0" if vulnerability_found else "0",
                    "gasUsed": 300000
                }
            ],
            timeline=[
                {
                    "step": "Contract Analysis",
                    "description": f"Analyzed contract for {attack_type} vulnerabilities",
                    "timestamp": datetime.now(),
                    "status": "success"
                },
                {
                    "step": "Exploit Execution", 
                    "description": "Executed attack simulation",
                    "timestamp": datetime.now(),
                    "status": "success" if vulnerability_found else "failed"
                }
            ],
            mitigation=[
                "Implement proper access controls",
                "Add reentrancy guards",
                "Use SafeMath for arithmetic operations",
                "Validate all external calls"
            ],
            riskScore=85 if vulnerability_found else 20,
            executionTime=5.2,
            simulation_results={
                "sandbox_environment": "isolated",
                "network_forked": "mainnet",
                "block_number": 18000000,
                "simulation_successful": vulnerability_found
            },
            exploit_simulations=[
                {
                    "attack_vector": attack_type,
                    "success": vulnerability_found,
                    "impact": "high" if vulnerability_found else "none",
                    "details": "Simulation completed successfully"
                }
            ],
            attack_vectors=[
                {
                    "vector": attack_type,
                    "feasibility": "high" if vulnerability_found else "low",
                    "complexity": "medium",
                    "impact": "critical" if vulnerability_found else "none"
                }
            ]
        )
        
        sim["status"] = "completed"
        sim["results"] = results
        sim["completion_time"] = datetime.now().isoformat()
        
        logger.info(f"Simulation {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Simulation {scan_id} failed: {e}")
        sim["status"] = "failed"
        sim["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 