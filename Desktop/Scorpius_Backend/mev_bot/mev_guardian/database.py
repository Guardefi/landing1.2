"""
Database manager for MevGuardian system.

Provides database operations for threats, simulations, metrics, and other data.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

import asyncpg
from contextlib import asynccontextmanager

from mev_guardian.types import Threat, SimulationResult, HoneypotResult, ForensicAnalysis


class DatabaseManager:
    """
    Manages all database operations for the MevGuardian system.
    
    Handles connections, transactions, and CRUD operations for threats,
    simulations, honeypot scans, forensic analyses, and metrics.
    """
    
    def __init__(self, database_url: str):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            self.logger.info("Database connection pool initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool."""
        if not self.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    # Threat operations
    async def save_threat(self, threat: Threat) -> UUID:
        """Save a threat to the database."""
        async with self.get_connection() as conn:
            threat_id = uuid4()
            await conn.execute(
                """
                INSERT INTO threats (
                    id, threat_type, severity, description, 
                    transaction_hash, block_number, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                threat_id,
                threat.type.value,
                threat.severity.value,
                threat.description,
                threat.transaction_hash,
                threat.block_number,
                threat.metadata
            )
            return threat_id
    
    async def get_threats(
        self, 
        limit: int = 100, 
        offset: int = 0,
        threat_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get threats from database with optional filtering."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM threats 
                WHERE ($3::text IS NULL OR threat_type = $3)
                AND ($4::text IS NULL OR severity = $4)
                ORDER BY detected_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset, threat_type, severity)
            return [dict(row) for row in rows]
    
    async def update_threat_status(self, threat_id: UUID, status: str) -> bool:
        """Update threat status."""
        async with self.get_connection() as conn:
            result = await conn.execute(
                "UPDATE threats SET status = $1, updated_at = NOW() WHERE id = $2",
                status, threat_id
            )
            return result.split()[1] == "1"
    
    # Simulation operations
    async def save_simulation(self, simulation: SimulationResult) -> UUID:
        """Save simulation result to database."""
        async with self.get_connection() as conn:
            sim_id = uuid4()
            await conn.execute(
                """
                INSERT INTO simulations (
                    id, simulation_type, status, profit_usd, gas_used,
                    success_probability, execution_time_ms, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                sim_id,
                simulation.simulation_type,
                simulation.status,
                simulation.profit_usd,
                simulation.gas_used,
                simulation.success_probability,
                simulation.execution_time_ms,
                simulation.metadata
            )
            return sim_id
    
    async def get_simulations(
        self, 
        limit: int = 100, 
        offset: int = 0,
        simulation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get simulations from database."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM simulations 
                WHERE ($3::text IS NULL OR simulation_type = $3)
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset, simulation_type)
            return [dict(row) for row in rows]
    
    # Honeypot operations
    async def save_honeypot_scan(self, honeypot: HoneypotResult) -> UUID:
        """Save honeypot scan result."""
        async with self.get_connection() as conn:
            scan_id = uuid4()
            await conn.execute(
                """
                INSERT INTO honeypot_scans (
                    id, contract_address, is_honeypot, risk_level,
                    reasons, confidence_score, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                scan_id,
                honeypot.contract_address,
                honeypot.is_honeypot,
                honeypot.risk_level,
                honeypot.reasons,
                honeypot.confidence_score,
                honeypot.metadata
            )
            return scan_id
    
    async def get_honeypot_scans(
        self, 
        limit: int = 100, 
        offset: int = 0,
        contract_address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get honeypot scans from database."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM honeypot_scans 
                WHERE ($3::text IS NULL OR contract_address = $3)
                ORDER BY scanned_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset, contract_address)
            return [dict(row) for row in rows]
    
    # Forensic operations
    async def save_forensic_analysis(self, analysis: ForensicAnalysis) -> UUID:
        """Save forensic analysis."""
        async with self.get_connection() as conn:
            analysis_id = uuid4()
            await conn.execute(
                """
                INSERT INTO forensic_analyses (
                    id, incident_id, analysis_type, findings,
                    severity, recommendations, evidence_links, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                analysis_id,
                analysis.incident_id,
                analysis.analysis_type,
                analysis.findings,
                analysis.severity,
                analysis.recommendations,
                analysis.evidence_links,
                analysis.metadata
            )
            return analysis_id
    
    async def get_forensic_analyses(
        self, 
        limit: int = 100, 
        offset: int = 0,
        incident_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get forensic analyses from database."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM forensic_analyses 
                WHERE ($3::text IS NULL OR incident_id = $3)
                ORDER BY analyzed_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset, incident_id)
            return [dict(row) for row in rows]
    
    # Metrics operations
    async def save_metric(self, metric_type: str, value: float, metadata: Optional[Dict] = None) -> None:
        """Save a metric value."""
        async with self.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO metrics (metric_type, value, metadata)
                VALUES ($1, $2, $3)
                """,
                metric_type, value, metadata or {}
            )
    
    async def get_metrics(
        self, 
        metric_type: str,
        limit: int = 100,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get metrics for a specific type within time range."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM metrics 
                WHERE metric_type = $1 
                AND timestamp >= NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC 
                LIMIT $2
            """ % hours
            rows = await conn.fetch(query, metric_type, limit)
            return [dict(row) for row in rows]
    
    # Operations log
    async def log_operation(
        self, 
        operation_type: str, 
        mode: str, 
        status: str,
        details: Optional[Dict] = None,
        profit_usd: Optional[float] = None,
        gas_used: Optional[int] = None
    ) -> UUID:
        """Log a bot operation."""
        async with self.get_connection() as conn:
            op_id = uuid4()
            await conn.execute(
                """
                INSERT INTO operations_log (
                    id, operation_type, mode, status, details, profit_usd, gas_used
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                op_id, operation_type, mode, status, details or {}, profit_usd, gas_used
            )
            return op_id
    
    async def get_operations_log(
        self, 
        limit: int = 100, 
        offset: int = 0,
        mode: Optional[str] = None,
        operation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get operations log with optional filtering."""
        async with self.get_connection() as conn:
            query = """
                SELECT * FROM operations_log 
                WHERE ($3::text IS NULL OR mode = $3)
                AND ($4::text IS NULL OR operation_type = $4)
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset, mode, operation_type)
            return [dict(row) for row in rows]
    
    # Analytics and aggregations
    async def get_threat_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get threat statistics for the specified time period."""
        async with self.get_connection() as conn:
            query = """
                SELECT 
                    threat_type,
                    severity,
                    COUNT(*) as count,
                    COUNT(*) FILTER (WHERE status = 'active') as active_count
                FROM threats 
                WHERE detected_at >= NOW() - INTERVAL '%s hours'
                GROUP BY threat_type, severity
                ORDER BY count DESC
            """ % hours
            
            rows = await conn.fetch(query)
            return {
                "period_hours": hours,
                "statistics": [dict(row) for row in rows],
                "total_threats": sum(row["count"] for row in rows)
            }
    
    async def get_profit_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get profit statistics from operations log."""
        async with self.get_connection() as conn:
            query = """
                SELECT 
                    mode,
                    operation_type,
                    COUNT(*) as operations_count,
                    SUM(profit_usd) as total_profit,
                    AVG(profit_usd) as avg_profit,
                    SUM(gas_used) as total_gas
                FROM operations_log 
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                AND profit_usd IS NOT NULL
                GROUP BY mode, operation_type
                ORDER BY total_profit DESC
            """ % hours
            
            rows = await conn.fetch(query)
            return {
                "period_hours": hours,
                "statistics": [dict(row) for row in rows]
            }


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        from mev_guardian.config import MevGuardianConfig
        config = MevGuardianConfig.load()
        _db_manager = DatabaseManager(config.database_url)
        await _db_manager.initialize()
    return _db_manager


async def close_database_manager() -> None:
    """Close the global database manager."""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None
