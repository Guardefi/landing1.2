"""
Main detector component that orchestrates all analysis engines
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.metrics import HONEYPOT_DETECTED, track_analysis_metrics
from blockchain.contract_fetcher import ContractFetcher
from core.analyzers.bytecode_analyzer import BytecodeAnalyzer
from core.analyzers.transaction_analyzer import TransactionAnalyzer
from core.engines.ml_engine import MLEngine
from core.engines.static_engine import StaticEngine
from core.engines.symbolic_engine import SymbolicEngine
from database.cache_service import cache_service
from database.mongodb_client import MongoDBClient
from database.repositories.analysis_repository import AnalysisRepository
from database.repositories.contract_repository import ContractRepository
from models.data_models import AnalysisResponse, RiskLevel

# Configure logger
logger = logging.getLogger("core.detector")


class HoneypotDetector:
    """
    Main honeypot detection coordinator

    This class orchestrates the various analysis engines and
    analyzers to produce a comprehensive honeypot analysis.
    """

    def __init__(self):
        """Initialize detector with all required components"""
        self.static_engine = None
        self.symbolic_engine = None
        self.ml_engine = None
        self.bytecode_analyzer = None
        self.transaction_analyzer = None
        self.contract_fetcher = None
        self.analysis_repo = None
        self.contract_repo = None
        self.initialized = False

    async def initialize(self):
        """Initialize all engines and components"""
        if self.initialized:
            return

        try:
            logger.info("Initializing honeypot detector components...")

            # Initialize engines
            self.static_engine = StaticEngine()
            await self.static_engine.load_patterns()

            self.symbolic_engine = SymbolicEngine()
            await self.symbolic_engine.initialize()

            self.ml_engine = MLEngine()
            await self.ml_engine.load_models()

            # Initialize analyzers
            self.bytecode_analyzer = BytecodeAnalyzer()
            await self.bytecode_analyzer.load_patterns()

            self.transaction_analyzer = TransactionAnalyzer()

            # Initialize data providers and repositories
            self.contract_fetcher = ContractFetcher()

            mongodb_client = MongoDBClient()
            await mongodb_client.connect()

            self.analysis_repo = AnalysisRepository()
            self.contract_repo = ContractRepository(mongodb_client)

            self.initialized = True
            logger.info("Honeypot detector initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing honeypot detector: {e}", exc_info=True)
            raise

    @track_analysis_metrics
    async def analyze_contract(
        self, address: str, chain_id: int = 1, deep_analysis: bool = False
    ) -> AnalysisResponse:
        """
        Analyze a smart contract for honeypot patterns

        Args:
            address: Contract address to analyze
            chain_id: Blockchain network ID
            deep_analysis: Whether to perform deep analysis (including symbolic execution)

        Returns:
            Comprehensive analysis response
        """
        if not self.initialized:
            await self.initialize()

        start_time = time.time()
        address = address.lower()

        logger.info(f"Starting analysis for contract {address} on chain {chain_id}")

        # Check cache first
        cached_result = await cache_service.get_cached_analysis(address, chain_id)
        if cached_result:
            logger.info(f"Using cached analysis for {address}")
            # Convert to proper response object
            return AnalysisResponse(**cached_result)

        # Fetch contract data
        try:
            contract_data = await self.contract_fetcher.fetch_contract(
                address, chain_id
            )

            if not contract_data or not contract_data.get("bytecode"):
                raise ValueError(f"Contract not found or has no bytecode: {address}")

            # Fetch token data if it's a token
            is_token = await self.contract_fetcher.is_token_contract(contract_data)
            if is_token:
                token_data = await self.contract_fetcher.fetch_token_metadata(
                    address, chain_id
                )
                contract_data.update({"token_data": token_data})
                contract_data["is_token"] = True

            # Fetch transactions
            transactions = await self.contract_fetcher.fetch_transactions(
                address, chain_id
            )
            contract_data["transactions"] = transactions

            # Save contract to database
            contract_data["chain_id"] = chain_id
            await self.contract_repo.save_contract(contract_data)

        except Exception as e:
            logger.error(f"Error fetching contract data: {e}", exc_info=True)
            raise ValueError(f"Failed to fetch contract data: {str(e)}")

        # Run analysis engines in parallel
        try:
            # Run preliminary bytecode analysis
            bytecode_analysis = await self.bytecode_analyzer.analyze_bytecode(
                contract_data.get("bytecode", "")
            )
            contract_data["bytecode_metrics"] = bytecode_analysis.get(
                "bytecode_metrics", {}
            )

            analysis_tasks = [
                self.static_engine.analyze(contract_data),
                self.ml_engine.predict(contract_data),
                self.transaction_analyzer.analyze_transactions(
                    contract_data.get("transactions", [])
                ),
            ]

            # Only run symbolic execution for deep analysis requests
            if deep_analysis:
                analysis_tasks.append(self.symbolic_engine.analyze(contract_data))

            # Run all analyses in parallel
            analysis_results = await asyncio.gather(*analysis_tasks)

            # Combine results
            static_result = analysis_results[0]
            ml_result = analysis_results[1]
            transaction_result = analysis_results[2]

            if deep_analysis:
                symbolic_result = analysis_results[3]
            else:
                symbolic_result = {
                    "confidence": 0,
                    "techniques": [],
                    "message": "Symbolic analysis not performed",
                }

            # Combine detected techniques
            all_techniques = (
                static_result.get("techniques", [])
                + transaction_result.get("detected_techniques", [])
                + bytecode_analysis.get("detected_techniques", [])
            )

            if deep_analysis and symbolic_result:
                all_techniques.extend(symbolic_result.get("techniques", []))

            # Remove duplicates
            detected_techniques = list(set(all_techniques))

            # Calculate confidence
            confidence_values = [
                static_result.get("confidence", 0),
                ml_result.get("confidence", 0),
                transaction_result.get("confidence", 0),
                bytecode_analysis.get("confidence", 0),
            ]

            if deep_analysis:
                confidence_values.append(symbolic_result.get("confidence", 0))

            # Remove zero values and calculate weighted average
            valid_values = [v for v in confidence_values if v > 0]
            if valid_values:
                confidence = sum(valid_values) / len(valid_values)
            else:
                confidence = 0

            # Determine honeypot status and risk level
            is_honeypot = confidence >= 0.5
            risk_level = self._calculate_risk_level(
                confidence, len(detected_techniques)
            )

            # Create aggregated result
            result = AnalysisResponse(
                is_honeypot=is_honeypot,
                confidence=confidence,
                risk_level=risk_level,
                detected_techniques=detected_techniques,
                analysis_duration=time.time() - start_time,
                analysis_timestamp=datetime.utcnow(),
                source_available=bool(contract_data.get("source_code")),
                engine_results={
                    "static": static_result,
                    "ml": ml_result,
                    "transaction": transaction_result,
                    "bytecode": bytecode_analysis,
                    "symbolic": symbolic_result
                    if deep_analysis
                    else {"performed": False},
                },
                contract_metadata={
                    "name": contract_data.get("contract_name", "Unknown"),
                    "compiler": contract_data.get("compiler_version", "Unknown"),
                    "is_token": contract_data.get("is_token", False),
                    "token_data": contract_data.get("token_data", {}),
                },
                transaction_history={
                    "transaction_count": len(contract_data.get("transactions", [])),
                    "first_seen": contract_data.get("created_at")
                    if "created_at" in contract_data
                    else None,
                    "unique_senders": len(
                        set(
                            tx.get("from")
                            for tx in contract_data.get("transactions", [])
                        )
                    ),
                },
            )

            # Track honeypot detection in metrics
            if is_honeypot:
                HONEYPOT_DETECTED.labels(
                    chain_id=chain_id, risk_level=risk_level.value
                ).inc()

            # Save result to database and cache
            await self.analysis_repo.save_analysis(address, result)
            await cache_service.cache_analysis(address, chain_id, result.dict())

            logger.info(
                f"Analysis completed for {address}: honeypot={is_honeypot}, confidence={confidence:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"Error analyzing contract {address}: {e}", exc_info=True)
            raise

    def _calculate_risk_level(
        self, confidence: float, technique_count: int
    ) -> RiskLevel:
        """
        Calculate risk level based on confidence score and detected techniques

        Args:
            confidence: Confidence score (0.0 - 1.0)
            technique_count: Number of distinct honeypot techniques detected

        Returns:
            Risk level enumeration
        """
        if confidence >= 0.8 or (confidence >= 0.7 and technique_count >= 3):
            return RiskLevel.HIGH
        elif confidence >= 0.5 or (confidence >= 0.4 and technique_count >= 2):
            return RiskLevel.MEDIUM
        elif confidence >= 0.3 or technique_count >= 1:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    async def get_analysis_history(
        self, address: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get analysis history for a contract

        Args:
            address: Contract address
            limit: Maximum number of history entries

        Returns:
            List of historical analysis results
        """
        if not self.initialized:
            await self.initialize()

        return await self.analysis_repo.get_analysis_history(address, limit)
