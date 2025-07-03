import asyncio
import logging
import os
import sys
from typing import Any, Dict

from celery import Celery
from celery.signals import worker_init, worker_process_init

# Add project root to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.contract_fetcher import ContractFetcher
from blockchain.web3_client import Web3Client
from core.analyzers.bytecode_analyzer import BytecodeAnalyzer
from core.analyzers.transaction_analyzer import TransactionAnalyzer
from core.engines.ml_engine import MLEngine
from core.engines.static_engine import StaticEngine
from core.engines.symbolic_engine import SymbolicEngine
from database.mongodb_client import MongoDBClient
from models.data_models import AnalysisRequest, RiskLevel

from config.settings import settings

# Configure logger
logger = logging.getLogger("worker")

# Create Celery instance
celery_app = Celery("honeypot_detector")
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)

# Global variables for clients
mongo_client = None
web3_client = None
contract_fetcher = None
ml_engine = None
static_engine = None
symbolic_engine = None
bytecode_analyzer = None
transaction_analyzer = None


@worker_init.connect
def init_worker(**kwargs):
    """Initialize worker process"""
    logger.info("Initializing worker process")


@worker_process_init.connect
async def init_worker_process(**kwargs):
    """Initialize worker process dependencies"""
    global mongo_client, web3_client, contract_fetcher, ml_engine
    global static_engine, symbolic_engine, bytecode_analyzer, transaction_analyzer

    loop = asyncio.get_event_loop()

    # Initialize MongoDB client
    logger.info("Initializing MongoDB client")
    mongo_client = MongoDBClient()
    await mongo_client.initialize()

    # Initialize blockchain client
    logger.info("Initializing Web3 client")
    web3_client = Web3Client()
    await web3_client.initialize()

    # Initialize contract fetcher
    logger.info("Initializing Contract fetcher")
    contract_fetcher = ContractFetcher()
    await contract_fetcher.initialize()

    # Initialize analysis engines
    logger.info("Initializing analysis engines")
    ml_engine = MLEngine()
    await ml_engine.initialize()

    static_engine = StaticEngine()

    symbolic_engine = SymbolicEngine()
    await symbolic_engine.initialize()

    # Initialize analyzers
    bytecode_analyzer = BytecodeAnalyzer()
    transaction_analyzer = TransactionAnalyzer()

    logger.info("Worker initialization complete")


@celery_app.task(name="analyze_contract")
def analyze_contract(
    contract_address: str, chain_id: int = 1, deep_analysis: bool = False
) -> Dict[str, Any]:
    """
    Analyze a contract for honeypot patterns

    Args:
        contract_address: Contract address to analyze
        chain_id: Blockchain network ID (1=Ethereum, 56=BSC)
        deep_analysis: Whether to perform deep analysis with symbolic execution

    Returns:
        Analysis results
    """
    logger.info(f"Starting analysis of contract {contract_address} on chain {chain_id}")

    # Run in event loop
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _analyze_contract_async(contract_address, chain_id, deep_analysis)
    )


async def _analyze_contract_async(
    contract_address: str, chain_id: int, deep_analysis: bool
) -> Dict[str, Any]:
    """Async implementation of contract analysis"""
    try:
        # Fetch contract data
        contract_data = await contract_fetcher.fetch_contract_details(
            contract_address, chain_id
        )

        # Perform static analysis
        static_results = static_engine.analyze(contract_data)

        # Perform ML analysis
        ml_results = await ml_engine.predict(contract_data)

        results = {
            "address": contract_address,
            "chain_id": chain_id,
            "bytecode_available": bool(contract_data.get("bytecode")),
            "source_available": bool(contract_data.get("source_code")),
            "static_analysis": static_results,
            "ml_analysis": ml_results,
            "transaction_analysis": None,
            "symbolic_analysis": None,
        }

        # Analyze transactions if available
        if contract_data.get("transactions"):
            tx_results = transaction_analyzer.analyze_transactions(
                contract_data["transactions"]
            )
            results["transaction_analysis"] = tx_results

        # Perform symbolic execution if deep analysis requested
        if deep_analysis and contract_data.get("bytecode"):
            symbolic_results = await symbolic_engine.analyze(contract_data)
            results["symbolic_analysis"] = symbolic_results

        # Determine overall risk level
        risk_level = _calculate_risk_level(results)
        results["risk_level"] = risk_level

        # Store results in database
        await _store_analysis_results(contract_address, chain_id, results)

        return results

    except Exception as e:
        logger.error(f"Error analyzing contract {contract_address}: {e}", exc_info=True)
        error_result = {
            "address": contract_address,
            "chain_id": chain_id,
            "error": str(e),
            "risk_level": RiskLevel.UNKNOWN.value,
        }
        await _store_analysis_results(contract_address, chain_id, error_result)
        return error_result


def _calculate_risk_level(results: Dict[str, Any]) -> str:
    """Calculate overall risk level based on analysis results"""
    # Get confidence scores from each engine
    static_confidence = results.get("static_analysis", {}).get("confidence", 0)
    ml_confidence = results.get("ml_analysis", {}).get("confidence", 0)

    symbolic_confidence = 0
    if results.get("symbolic_analysis"):
        symbolic_confidence = results.get("symbolic_analysis", {}).get("confidence", 0)

    tx_confidence = 0
    if results.get("transaction_analysis"):
        tx_confidence = results.get("transaction_analysis", {}).get("confidence", 0)

    # Calculate weighted average confidence
    weights = [0.25, 0.35, 0.25, 0.15]  # ML, Symbolic, Static, Transaction
    confidences = [ml_confidence, symbolic_confidence, static_confidence, tx_confidence]

    # If no symbolic analysis was performed, adjust weights
    if symbolic_confidence == 0:
        weights = [0.5, 0, 0.35, 0.15]  # ML, Symbolic, Static, Transaction

    weighted_sum = sum(c * w for c, w in zip(confidences, weights))

    # Determine risk level based on confidence
    if weighted_sum >= 0.8:
        return RiskLevel.CRITICAL.value
    elif weighted_sum >= 0.6:
        return RiskLevel.HIGH.value
    elif weighted_sum >= 0.4:
        return RiskLevel.MEDIUM.value
    elif weighted_sum >= 0.2:
        return RiskLevel.LOW.value
    else:
        return RiskLevel.SAFE.value


async def _store_analysis_results(
    contract_address: str, chain_id: int, results: Dict[str, Any]
):
    """Store analysis results in database"""
    try:
        # Get analysis repository
        analysis_repo = await mongo_client.get_analysis_repository()

        # Save analysis results
        await analysis_repo.save_analysis(
            contract_address=contract_address, chain_id=chain_id, results=results
        )

        # Update statistics
        await analysis_repo.update_statistics(
            chain_id=chain_id,
            risk_level=results.get("risk_level", RiskLevel.UNKNOWN.value),
        )

    except Exception as e:
        logger.error(f"Error storing analysis results: {e}", exc_info=True)


@celery_app.task(name="update_ml_model")
def update_ml_model():
    """Update ML model with recent data"""
    logger.info("Starting ML model update")

    # Run in event loop
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_update_ml_model_async())


async def _update_ml_model_async():
    """Async implementation of model update"""
    try:
        # Retrain model with recent data
        await ml_engine.train()
        return {"status": "success", "message": "ML model updated successfully"}

    except Exception as e:
        logger.error(f"Error updating ML model: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    celery_app.start()
