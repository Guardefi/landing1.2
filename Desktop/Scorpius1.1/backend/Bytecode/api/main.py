"""
Enterprise REST API + WebSocket for Bytecode Similarity Engine
Real-time bytecode analysis for security platforms
"""

import asyncio
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import aiohttp
import redis
import uvicorn
import yaml
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Security,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.similarity_engine import SimilarityEngine
from utils.metrics import PerformanceMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Global engine instance
engine: Optional[SimilarityEngine] = None
monitor = PerformanceMonitor()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket in self.active_connections:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        if not self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.add(connection)

        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# Load configuration
config_path = Path("configs/engine_config.yaml")
if config_path.exists():
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
else:
    config = {}

api_config = config.get("api", {})


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SCORPIUS Bytecode Similarity Engine API")

    # Initialize engine
    global engine
    try:
        engine = SimilarityEngine()
        await engine.initialize()
        logger.info("Similarity engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize similarity engine: {e}")
        engine = None

    # Start background tasks
    metrics_task = asyncio.create_task(broadcast_system_metrics())

    yield

    # Shutdown
    logger.info("Shutting down SCORPIUS API")
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="SCORPIUS Bytecode Similarity Engine",
    description="Enterprise-grade bytecode similarity detection API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
if api_config.get("enable_cors", True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.get("cors_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


# Request/Response models
class BytecodeComparisonRequest(BaseModel):
    bytecode1: str = Field(..., description="First bytecode to compare (hex string)")
    bytecode2: str = Field(..., description="Second bytecode to compare (hex string)")
    threshold: Optional[float] = Field(
        0.7, ge=0.0, le=1.0, description="Similarity threshold"
    )
    use_neural_network: Optional[bool] = Field(
        True, description="Use neural network for comparison"
    )


class BytecodeComparisonResponse(BaseModel):
    similarity_score: float = Field(..., description="Similarity score between 0 and 1")
    confidence: float = Field(..., description="Confidence in the similarity score")
    is_similar: bool = Field(
        ..., description="Whether bytecodes are considered similar"
    )
    dimension_scores: Dict[str, float] = Field(
        ..., description="Scores for each dimension"
    )
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    processing_time: float = Field(..., description="Processing time in seconds")


class SimilaritySearchRequest(BaseModel):
    query_bytecode: str = Field(..., description="Query bytecode (hex string)")
    top_k: Optional[int] = Field(
        10, ge=1, le=100, description="Number of results to return"
    )
    min_similarity: Optional[float] = Field(
        0.7, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )


class SimilaritySearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="List of similar bytecodes")
    total_results: int = Field(..., description="Total number of results found")
    processing_time: float = Field(..., description="Processing time in seconds")


class IndexingRequest(BaseModel):
    bytecode: str = Field(..., description="Bytecode to index (hex string)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Associated metadata"
    )


class IndexingResponse(BaseModel):
    bytecode_hash: str = Field(..., description="Hash of the indexed bytecode")
    success: bool = Field(..., description="Whether indexing was successful")
    processing_time: float = Field(..., description="Processing time in seconds")


class BatchIndexingRequest(BaseModel):
    bytecodes: List[Dict[str, Any]] = Field(
        ..., description="List of bytecodes with metadata to index"
    )


class BatchIndexingResponse(BaseModel):
    indexed_count: int = Field(
        ..., description="Number of successfully indexed bytecodes"
    )
    bytecode_hashes: List[str] = Field(..., description="List of bytecode hashes")
    failed_count: int = Field(..., description="Number of failed indexing operations")
    processing_time: float = Field(..., description="Processing time in seconds")


class EngineStatsResponse(BaseModel):
    total_indexed_bytecodes: int = Field(
        ..., description="Total number of indexed bytecodes"
    )
    cache_size: int = Field(..., description="Current cache size")
    device: str = Field(..., description="Device being used for computation")
    model_loaded: bool = Field(
        ..., description="Whether neural network model is loaded"
    )
    metrics: Dict[str, Any] = Field(..., description="Engine performance metrics")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


# Authentication dependency
async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not api_config.get("enable_auth", False):
        return None

    if credentials is None:
        raise HTTPException(status_code=401, detail="API key required")

    # In production, validate the API key against a database
    expected_key = api_config.get("api_key", "your-secret-api-key")
    if credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return credentials.credentials


# Startup event
@app.on_event("startup")
async def startup_event():
    global engine
    logger.info("Starting SCORPIUS Bytecode Similarity Engine API...")

    try:
        # Initialize the similarity engine
        engine_config = config.get("similarity_engine", {})
        engine = SimilarityEngine(engine_config)
        logger.info("Similarity engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize similarity engine: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    global engine
    logger.info("Shutting down SCORPIUS Bytecode Similarity Engine API...")

    if engine:
        await engine.cleanup()

    logger.info("Shutdown complete")


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if engine else "unhealthy",
        timestamp=time.time(),
        version="1.0.0",
    )


# Compare bytecodes endpoint
@app.post("/api/v1/compare", response_model=BytecodeComparisonResponse)
async def compare_bytecodes(
    request: BytecodeComparisonRequest, api_key: str = Depends(get_api_key)
):
    """Compare two bytecodes for similarity"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    monitor.start_measurement()

    try:
        # Validate input
        if not request.bytecode1 or not request.bytecode2:
            raise HTTPException(
                status_code=400, detail="Both bytecodes must be provided"
            )

        # Perform comparison
        result = await engine.compare_bytecodes(
            request.bytecode1, request.bytecode2, request.use_neural_network
        )

        # Determine if similar based on threshold
        is_similar = result.similarity_score >= request.threshold

        response = BytecodeComparisonResponse(
            similarity_score=result.similarity_score,
            confidence=result.confidence,
            is_similar=is_similar,
            dimension_scores=result.dimension_scores,
            metadata=result.metadata,
            processing_time=result.processing_time,
        )

        monitor.end_measurement(
            "compare_bytecodes",
            {"similarity_score": result.similarity_score, "is_similar": is_similar},
        )

        return response

    except Exception as e:
        monitor.end_measurement("compare_bytecodes_error")
        logger.error(f"Error comparing bytecodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Search for similar bytecodes endpoint
@app.post("/api/v1/search", response_model=SimilaritySearchResponse)
async def search_similar_bytecodes(
    request: SimilaritySearchRequest, api_key: str = Depends(get_api_key)
):
    """Search for similar bytecodes in the index"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    start_time = time.time()

    try:
        # Validate input
        if not request.query_bytecode:
            raise HTTPException(
                status_code=400, detail="Query bytecode must be provided"
            )

        # Perform search
        results = await engine.find_similar_bytecode(
            request.query_bytecode, request.top_k, request.min_similarity
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "bytecode_hash": result.bytecode_hash,
                    "similarity_score": result.similarity_score,
                    "confidence": result.confidence,
                    "metadata": result.metadata,
                }
            )

        processing_time = time.time() - start_time

        response = SimilaritySearchResponse(
            results=formatted_results,
            total_results=len(formatted_results),
            processing_time=processing_time,
        )

        return response

    except Exception as e:
        logger.error(f"Error searching for similar bytecodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Index bytecode endpoint
@app.post("/api/v1/index", response_model=IndexingResponse)
async def index_bytecode(request: IndexingRequest, api_key: str = Depends(get_api_key)):
    """Index a bytecode for similarity search"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    start_time = time.time()

    try:
        # Validate input
        if not request.bytecode:
            raise HTTPException(status_code=400, detail="Bytecode must be provided")

        # Index the bytecode
        bytecode_hash = await engine.index_bytecode(request.bytecode, request.metadata)

        processing_time = time.time() - start_time

        response = IndexingResponse(
            bytecode_hash=bytecode_hash, success=True, processing_time=processing_time
        )

        return response

    except Exception as e:
        logger.error(f"Error indexing bytecode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch index bytecodes endpoint
@app.post("/api/v1/batch-index", response_model=BatchIndexingResponse)
async def batch_index_bytecodes(
    request: BatchIndexingRequest, api_key: str = Depends(get_api_key)
):
    """Index multiple bytecodes for similarity search"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    start_time = time.time()

    try:
        # Validate input
        if not request.bytecodes:
            raise HTTPException(
                status_code=400, detail="Bytecodes list must be provided"
            )

        # Prepare data for batch indexing
        bytecode_pairs = []
        for item in request.bytecodes:
            if "bytecode" not in item:
                continue
            metadata = {k: v for k, v in item.items() if k != "bytecode"}
            bytecode_pairs.append((item["bytecode"], metadata))

        # Perform batch indexing
        bytecode_hashes = await engine.batch_index_bytecodes(bytecode_pairs)

        processing_time = time.time() - start_time

        response = BatchIndexingResponse(
            indexed_count=len(bytecode_hashes),
            bytecode_hashes=bytecode_hashes,
            failed_count=len(request.bytecodes) - len(bytecode_hashes),
            processing_time=processing_time,
        )

        return response

    except Exception as e:
        logger.error(f"Error batch indexing bytecodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Engine statistics endpoint
@app.get("/api/v1/stats", response_model=EngineStatsResponse)
async def get_engine_stats(api_key: str = Depends(get_api_key)):
    """Get engine statistics and performance metrics"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    try:
        stats = engine.get_engine_stats()

        response = EngineStatsResponse(
            total_indexed_bytecodes=stats["total_indexed_bytecodes"],
            cache_size=stats["cache_size"],
            device=stats["device"],
            model_loaded=stats["model_loaded"],
            metrics=stats["metrics"],
        )

        return response

    except Exception as e:
        logger.error(f"Error getting engine stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Clear cache endpoint
@app.post("/api/v1/clear-cache")
async def clear_cache(api_key: str = Depends(get_api_key)):
    """Clear the comparison cache"""
    if not engine:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    try:
        engine.clear_cache()
        return {"message": "Cache cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring and updates"""
    await manager.connect(websocket)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            json.dumps(
                {
                    "type": "connection_established",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Connected to SCORPIUS real-time feed",
                }
            ),
            websocket,
        )

        # Send initial stats
        if engine:
            stats = engine.get_engine_stats()
            await manager.send_personal_message(
                json.dumps(
                    {
                        "type": "stats_update",
                        "data": stats,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                websocket,
            )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                # Parse and handle client messages
                try:
                    message = json.loads(data)
                    message_type = message.get("type", "unknown")

                    if message_type == "ping":
                        await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "pong",
                                    "timestamp": datetime.now().isoformat(),
                                }
                            ),
                            websocket,
                        )
                    elif message_type == "subscribe":
                        # Handle subscription requests
                        await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "subscription_confirmed",
                                    "subscription": message.get("subscription", "all"),
                                    "timestamp": datetime.now().isoformat(),
                                }
                            ),
                            websocket,
                        )

                except json.JSONDecodeError:
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": datetime.now().isoformat(),
                            }
                        ),
                        websocket,
                    )

            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal_message(
                    json.dumps(
                        {"type": "heartbeat", "timestamp": datetime.now().isoformat()}
                    ),
                    websocket,
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


# Background task to broadcast system metrics
async def broadcast_system_metrics():
    """Background task to broadcast system metrics to all connected clients"""
    while True:
        try:
            if manager.active_connections and engine:
                stats = engine.get_engine_stats()
                await manager.broadcast(
                    {
                        "type": "system_metrics",
                        "data": {
                            "timestamp": datetime.now().isoformat(),
                            "cpu_usage": 45.2,  # Mock data - replace with actual system monitoring
                            "memory_usage": 62.8,
                            "active_connections": len(manager.active_connections),
                            "requests_per_minute": stats.get("requests_per_minute", 0),
                            "response_time": stats.get("avg_response_time", 0),
                        },
                    }
                )

            await asyncio.sleep(5)  # Send metrics every 5 seconds

        except Exception as e:
            logger.error(f"Error broadcasting metrics: {e}")
            await asyncio.sleep(10)  # Wait longer on error


# Main function to run the server
def main():
    """Run the API server"""
    host = api_config.get("host", "0.0.0.0")
    port = api_config.get("port", 8000)
    workers = api_config.get("workers", 1)

    logger.info(f"Starting server on {host}:{port} with {workers} workers")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        access_log=True,
    )


if __name__ == "__main__":
    main()
