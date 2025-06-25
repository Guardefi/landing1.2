"""
FastAPI routes for Blockchain Forensics
Advanced blockchain analysis, compliance monitoring, and investigation tools
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

# Import blockchain forensics modules
try:
    from ..ai_blockchain_forensics import (
        BlockchainForensics,
        ComplianceMonitor,
        ForensicsAnalyzer,
        TransactionGraph,
    )
except ImportError:
    # Fallback stubs if not available
    class BlockchainForensics:
        def __init__(self):
            pass

        async def analyze_address(self, address, chain="ethereum"):
            return {"address": address, "risk_score": 0.1, "analysis": "stub-analysis"}

        async def trace_funds(self, tx_hash, depth=3):
            return {"trace_id": "stub-trace", "hops": [], "total_amount": 0}

        async def compliance_check(self, address):
            return {"compliant": True, "flags": [], "score": 0.9}

    class ForensicsAnalyzer:
        def __init__(self):
            pass

        async def analyze_transaction_pattern(self, addresses):
            return {"pattern": "normal", "confidence": 0.8}

    class ComplianceMonitor:
        def __init__(self):
            pass

        async def check_sanctions(self, address):
            return {"sanctioned": False, "lists": []}

    class TransactionGraph:
        def __init__(self):
            pass

        async def build_graph(self, root_address, depth=2):
            return {"nodes": [], "edges": [], "metadata": {}}


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/forensics", tags=["Blockchain Forensics"])

# Initialize forensics components
forensics = BlockchainForensics()
analyzer = ForensicsAnalyzer()
compliance = ComplianceMonitor()
tx_graph = TransactionGraph()


# Request/Response models
class AddressAnalysisRequest(BaseModel):
    address: str
    chain: str = "ethereum"
    include_compliance: bool = True
    analysis_depth: int = 3


class AddressAnalysisResponse(BaseModel):
    address: str
    chain: str
    risk_score: float
    compliance_status: str
    flags: list[str]
    analysis: dict[str, Any]
    timestamp: datetime


class FundsTraceRequest(BaseModel):
    transaction_hash: str
    chain: str = "ethereum"
    max_depth: int = 5
    min_amount: float = 0.01


class FundsTraceResponse(BaseModel):
    trace_id: str
    transaction_hash: str
    total_hops: int
    total_amount: float
    trace_path: list[dict[str, Any]]
    risk_assessment: dict[str, Any]
    timestamp: datetime


class ComplianceCheckRequest(BaseModel):
    addresses: list[str]
    chain: str = "ethereum"
    check_sanctions: bool = True
    check_aml: bool = True


class ComplianceCheckResponse(BaseModel):
    results: list[dict[str, Any]]
    overall_risk: float
    flags: list[str]
    timestamp: datetime


class TransactionGraphRequest(BaseModel):
    root_address: str
    depth: int = 2
    max_nodes: int = 100
    min_amount: float = 0.1
    chain: str = "ethereum"


class TransactionGraphResponse(BaseModel):
    graph_id: str
    root_address: str
    total_nodes: int
    total_edges: int
    graph_data: dict[str, Any]
    risk_clusters: list[dict[str, Any]]
    timestamp: datetime


# Endpoints
@router.post("/address/analyze", response_model=AddressAnalysisResponse)
async def analyze_address(request: AddressAnalysisRequest):
    """Perform comprehensive address analysis."""
    try:
        # Run address analysis
        analysis = await forensics.analyze_address(
            address=request.address, chain=request.chain, depth=request.analysis_depth
        )

        # Check compliance if requested
        compliance_result = {"status": "unknown", "flags": []}
        if request.include_compliance:
            compliance_result = await compliance.check_sanctions(request.address)

        return AddressAnalysisResponse(
            address=request.address,
            chain=request.chain,
            risk_score=analysis.get("risk_score", 0.0),
            compliance_status=compliance_result.get("status", "unknown"),
            flags=analysis.get("flags", []) + compliance_result.get("flags", []),
            analysis=analysis,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to analyze address: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") from e


@router.post("/funds/trace", response_model=FundsTraceResponse)
async def trace_funds(request: FundsTraceRequest, background_tasks: BackgroundTasks):
    """Trace the flow of funds from a transaction."""
    try:
        # Start funds tracing
        trace_result = await forensics.trace_funds(
            tx_hash=request.transaction_hash,
            depth=request.max_depth,
            min_amount=request.min_amount,
        )

        # Generate risk assessment
        risk_assessment = await analyzer.analyze_transaction_pattern(
            [hop["address"] for hop in trace_result.get("hops", [])]
        )

        return FundsTraceResponse(
            trace_id=trace_result.get(
                "trace_id", f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ),
            transaction_hash=request.transaction_hash,
            total_hops=len(trace_result.get("hops", [])),
            total_amount=trace_result.get("total_amount", 0.0),
            trace_path=trace_result.get("hops", []),
            risk_assessment=risk_assessment,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to trace funds: {e}")
        raise HTTPException(
            status_code=500, detail=f"Funds tracing failed: {str(e)}"
        ) from e


@router.post("/compliance/check", response_model=ComplianceCheckResponse)
async def compliance_check(request: ComplianceCheckRequest):
    """Perform compliance checks on multiple addresses."""
    try:
        results = []
        all_flags = []
        total_risk = 0.0

        for address in request.addresses:
            # Basic compliance check
            result = await forensics.compliance_check(address)

            # Sanctions check if requested
            if request.check_sanctions:
                sanctions = await compliance.check_sanctions(address)
                result["sanctions"] = sanctions
                if sanctions.get("sanctioned", False):
                    all_flags.extend(sanctions.get("lists", []))

            results.append(
                {
                    "address": address,
                    "compliant": result.get("compliant", True),
                    "risk_score": result.get("score", 0.0),
                    "flags": result.get("flags", []),
                    "details": result,
                }
            )

            total_risk += result.get("score", 0.0)

        average_risk = total_risk / len(request.addresses) if request.addresses else 0.0

        return ComplianceCheckResponse(
            results=results,
            overall_risk=average_risk,
            flags=list(set(all_flags)),  # Remove duplicates
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed compliance check: {e}")
        raise HTTPException(
            status_code=500, detail=f"Compliance check failed: {str(e)}"
        ) from e


@router.post("/graph/build", response_model=TransactionGraphResponse)
async def build_transaction_graph(request: TransactionGraphRequest):
    """Build a transaction graph for visualization and analysis."""
    try:
        # Build transaction graph
        graph = await tx_graph.build_graph(
            root_address=request.root_address,
            depth=request.depth,
            max_nodes=request.max_nodes,
            min_amount=request.min_amount,
        )

        # Analyze for risk clusters
        risk_clusters = await analyzer.identify_risk_clusters(graph)

        return TransactionGraphResponse(
            graph_id=f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            root_address=request.root_address,
            total_nodes=len(graph.get("nodes", [])),
            total_edges=len(graph.get("edges", [])),
            graph_data=graph,
            risk_clusters=risk_clusters,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to build transaction graph: {e}")
        raise HTTPException(
            status_code=500, detail=f"Graph building failed: {str(e)}"
        ) from e


@router.get("/reports/activity")
async def get_forensics_activity():
    """Get recent forensics activity and statistics."""
    try:
        # Get activity statistics
        stats = await forensics.get_activity_stats()

        return {
            "total_analyses": stats.get("total_analyses", 0),
            "high_risk_addresses": stats.get("high_risk_addresses", 0),
            "compliance_violations": stats.get("compliance_violations", 0),
            "active_traces": stats.get("active_traces", 0),
            "recent_activity": stats.get("recent_activity", []),
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to get activity stats: {e}")
        return {
            "error": "Failed to fetch activity statistics",
            "timestamp": datetime.now(),
        }


@router.get("/watchlist")
async def get_watchlist():
    """Get addresses on the monitoring watchlist."""
    try:
        watchlist = await forensics.get_watchlist()

        return {
            "addresses": watchlist.get("addresses", []),
            "total": len(watchlist.get("addresses", [])),
            "last_updated": watchlist.get("last_updated", datetime.now()),
            "auto_monitor": watchlist.get("auto_monitor", True),
        }
    except Exception as e:
        logger.error(f"Failed to get watchlist: {e}")
        return {
            "addresses": [],
            "total": 0,
            "error": "Failed to fetch watchlist",
            "timestamp": datetime.now(),
        }


@router.post("/watchlist/add")
async def add_to_watchlist(request: dict[str, Any]):
    """Add addresses to the monitoring watchlist."""
    try:
        addresses = request.get("addresses", [])
        reason = request.get("reason", "Manual addition")

        result = await forensics.add_to_watchlist(addresses, reason)

        return {
            "added": result.get("added", []),
            "already_monitored": result.get("already_monitored", []),
            "reason": reason,
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Failed to add to watchlist: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to add to watchlist: {str(e)}"
        ) from e


@router.get("/chains/supported")
async def get_supported_chains():
    """Get list of supported blockchain networks."""
    return {
        "chains": [
            {
                "id": "ethereum",
                "name": "Ethereum",
                "native_token": "ETH",
                "explorer": "https://etherscan.io",
                "forensics_enabled": True,
            },
            {
                "id": "bitcoin",
                "name": "Bitcoin",
                "native_token": "BTC",
                "explorer": "https://blockchair.com/bitcoin",
                "forensics_enabled": True,
            },
            {
                "id": "polygon",
                "name": "Polygon",
                "native_token": "MATIC",
                "explorer": "https://polygonscan.com",
                "forensics_enabled": True,
            },
            {
                "id": "bsc",
                "name": "Binance Smart Chain",
                "native_token": "BNB",
                "explorer": "https://bscscan.com",
                "forensics_enabled": True,
            },
        ],
        "default": "ethereum",
        "total_supported": 4,
    }


@router.get("/status")
async def get_forensics_status():
    """Get blockchain forensics system status."""
    try:
        status = await forensics.get_system_status()

        return {
            "status": "operational",
            "active_analyses": status.get("active_analyses", 0),
            "queue_length": status.get("queue_length", 0),
            "data_sources": status.get("data_sources", []),
            "last_sync": status.get("last_sync", datetime.now()),
            "health": status.get("health", "healthy"),
        }
    except Exception as e:
        logger.error(f"Failed to get forensics status: {e}")
        return {"status": "degraded", "error": str(e), "timestamp": datetime.now()}
