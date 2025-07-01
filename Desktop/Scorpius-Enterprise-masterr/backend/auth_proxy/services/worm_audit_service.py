"""
WORM (Write-Once-Read-Many) Audit Service
Provides immutable audit trail using QLDB and Postgres with cryptographic verification
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

import asyncpg
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pydantic import BaseModel

try:
    from pyqldb.driver.qldb_driver import QldbDriver

    QLDB_AVAILABLE = True
except ImportError:
    QLDB_AVAILABLE = False

logger = logging.getLogger(__name__)


class AuditEvent(BaseModel):
    """Audit event model"""

    event_id: str
    timestamp: datetime
    event_type: str
    user_id: str
    org_id: str
    resource_type: str
    resource_id: str
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = {}
    success: bool = True
    risk_score: Optional[int] = None


class AuditProof(BaseModel):
    """Cryptographic proof for audit event"""

    event_id: str
    content_hash: str
    signature: str
    qldb_document_id: Optional[str] = None
    postgres_block_hash: str
    chain_position: int
    verified: bool = False


class WORMAuditService:
    """WORM Audit Service with dual storage (QLDB + Postgres)"""

    def __init__(
        self,
        postgres_url: str,
        qldb_ledger_name: Optional[str] = None,
        aws_region: str = "us-east-1",
    ):
        self.postgres_url = postgres_url
        self.qldb_ledger_name = qldb_ledger_name
        self.aws_region = aws_region
        self.pool: Optional[asyncpg.Pool] = None
        self.qldb_driver: Optional[QldbDriver] = None
        self.signing_key = self._generate_signing_key()
        self.public_key = self.signing_key.public_key()

    def _generate_signing_key(self) -> rsa.RSAPrivateKey:
        """Generate RSA key for signing audit events"""
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    async def initialize(self):
        """Initialize database connections"""
        # Initialize Postgres connection pool
        self.pool = await asyncpg.create_pool(
            self.postgres_url, min_size=2, max_size=10
        )

        # Initialize QLDB driver if available
        if QLDB_AVAILABLE and self.qldb_ledger_name:
            try:
                self.qldb_driver = QldbDriver(
                    ledger_name=self.qldb_ledger_name, region_name=self.aws_region
                )
                logger.info(
                    f"QLDB driver initialized for ledger: {
                        self.qldb_ledger_name}"
                )
            except Exception as e:
                logger.warning(f"QLDB initialization failed: {e}")
                self.qldb_driver = None

        # Create audit tables
        await self._create_audit_tables()

    async def _create_audit_tables(self):
        """Create immutable audit tables in Postgres"""
        async with self.pool.acquire() as conn:
            # Main audit events table with WORM constraints
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id UUID PRIMARY KEY,
                    block_number BIGSERIAL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    event_type VARCHAR(100) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    org_id VARCHAR(255) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    resource_id VARCHAR(255) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    ip_address INET,
                    user_agent TEXT,
                    details JSONB DEFAULT '{}',
                    success BOOLEAN DEFAULT TRUE,
                    risk_score INTEGER,
                    content_hash VARCHAR(64) NOT NULL,
                    signature TEXT NOT NULL,
                    qldb_document_id VARCHAR(255),
                    previous_block_hash VARCHAR(64),
                    block_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                -- Prevent updates and deletes (WORM enforcement)
                CREATE OR REPLACE RULE audit_events_no_update AS
                    ON UPDATE TO audit_events DO INSTEAD NOTHING;

                CREATE OR REPLACE RULE audit_events_no_delete AS
                    ON DELETE TO audit_events DO INSTEAD NOTHING;

                -- Indexes for efficient querying
                CREATE INDEX IF NOT EXISTS idx_audit_events_org_timestamp
                    ON audit_events(org_id, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_events_user_timestamp
                    ON audit_events(user_id, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_events_type_timestamp
                    ON audit_events(event_type, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_events_resource
                    ON audit_events(resource_type, resource_id);
                CREATE INDEX IF NOT EXISTS idx_audit_events_block_number
                    ON audit_events(block_number);
            """
            )

            # Audit chain metadata table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_chain_metadata (
                    id SERIAL PRIMARY KEY,
                    last_block_number BIGINT NOT NULL DEFAULT 0,
                    last_block_hash VARCHAR(64),
                    total_events BIGINT NOT NULL DEFAULT 0,
                    chain_integrity_verified BOOLEAN DEFAULT TRUE,
                    last_verification_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                -- Insert initial metadata if not exists
                INSERT INTO audit_chain_metadata (id, last_block_number, last_block_hash, total_events)
                VALUES (1, 0, 'genesis', 0)
                ON CONFLICT (id) DO NOTHING;
            """
            )

    async def log_audit_event(self, event: AuditEvent) -> AuditProof:
        """Log audit event with WORM guarantees"""
        if not event.event_id:
            event.event_id = str(uuid4())

        if not event.timestamp:
            event.timestamp = datetime.now(timezone.utc)

        # Generate content hash
        content = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "user_id": event.user_id,
            "org_id": event.org_id,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "details": event.details,
            "success": event.success,
        }

        content_json = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        # Sign the content
        signature = self._sign_content(content_json)

        # Store in both QLDB and Postgres
        qldb_document_id = None
        if self.qldb_driver:
            qldb_document_id = await self._store_in_qldb(event, content_hash, signature)

        # Store in Postgres with blockchain-like chaining
        postgres_result = await self._store_in_postgres(
            event, content_hash, signature, qldb_document_id
        )

        return AuditProof(
            event_id=event.event_id,
            content_hash=content_hash,
            signature=signature,
            qldb_document_id=qldb_document_id,
            postgres_block_hash=postgres_result["block_hash"],
            chain_position=postgres_result["block_number"],
            verified=True,
        )

    def _sign_content(self, content: str) -> str:
        """Sign content with RSA private key"""
        signature = self.signing_key.sign(
            content.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return signature.hex()

    async def _store_in_qldb(
        self, event: AuditEvent, content_hash: str, signature: str
    ) -> Optional[str]:
        """Store audit event in QLDB for immutable ledger"""
        try:
            qldb_document = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "user_id": event.user_id,
                "org_id": event.org_id,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "action": event.action,
                "ip_address": str(event.ip_address) if event.ip_address else None,
                "user_agent": event.user_agent,
                "details": event.details,
                "success": event.success,
                "risk_score": event.risk_score,
                "content_hash": content_hash,
                "signature": signature,
                "service": "scorpius-audit",
            }

            def store_transaction(transaction_executor):
                cursor = transaction_executor.execute_statement(
                    "INSERT INTO AuditEvents ?", qldb_document
                )
                result = list(cursor)
                return result[0]["documentId"] if result else None

            document_id = self.qldb_driver.execute_lambda(store_transaction)
            logger.info(f"Stored audit event in QLDB: {event.event_id}")
            return str(document_id)

        except Exception as e:
            logger.error(f"Failed to store in QLDB: {e}")
            return None

    async def _store_in_postgres(
        self,
        event: AuditEvent,
        content_hash: str,
        signature: str,
        qldb_document_id: Optional[str],
    ) -> Dict[str, Any]:
        """Store audit event in Postgres with blockchain-like chaining"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Get previous block info
                previous_block = await conn.fetchrow(
                    """
                    SELECT last_block_number, last_block_hash
                    FROM audit_chain_metadata WHERE id = 1
                """
                )

                previous_block_number = previous_block["last_block_number"]
                previous_block_hash = previous_block["last_block_hash"]
                new_block_number = previous_block_number + 1

                # Calculate new block hash (includes previous hash for
                # chaining)
                block_content = f"{content_hash}:{signature}:{previous_block_hash}:{new_block_number}"
                block_hash = hashlib.sha256(block_content.encode()).hexdigest()

                # Insert audit event
                await conn.execute(
                    """
                    INSERT INTO audit_events (
                        event_id, timestamp, event_type, user_id, org_id,
                        resource_type, resource_id, action, ip_address, user_agent,
                        details, success, risk_score, content_hash, signature,
                        qldb_document_id, previous_block_hash, block_hash, block_number
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                """,
                    event.event_id,
                    event.timestamp,
                    event.event_type,
                    event.user_id,
                    event.org_id,
                    event.resource_type,
                    event.resource_id,
                    event.action,
                    event.ip_address,
                    event.user_agent,
                    json.dumps(event.details),
                    event.success,
                    event.risk_score,
                    content_hash,
                    signature,
                    qldb_document_id,
                    previous_block_hash,
                    block_hash,
                    new_block_number,
                )

                # Update chain metadata
                await conn.execute(
                    """
                    UPDATE audit_chain_metadata
                    SET last_block_number = $1, last_block_hash = $2,
                        total_events = total_events + 1, updated_at = NOW()
                    WHERE id = 1
                """,
                    new_block_number,
                    block_hash,
                )

                logger.info(
                    f"Stored audit event in Postgres: {
                        event.event_id} (block #{new_block_number})"
                )
                return {
                    "block_number": new_block_number,
                    "block_hash": block_hash,
                    "previous_block_hash": previous_block_hash,
                }

    async def verify_audit_chain(
        self, start_block: int = 1, end_block: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verify the integrity of the audit chain"""
        async with self.pool.acquire() as conn:
            # Get chain metadata
            metadata = await conn.fetchrow(
                "SELECT * FROM audit_chain_metadata WHERE id = 1"
            )

            if not end_block:
                end_block = metadata["last_block_number"]

            # Verify chain integrity
            verification_results = {
                "verified": True,
                "total_blocks": end_block - start_block + 1,
                "verified_blocks": 0,
                "broken_chains": [],
                "invalid_signatures": [],
                "missing_blocks": [],
            }

            # Check each block in sequence
            for block_num in range(start_block, end_block + 1):
                block_record = await conn.fetchrow(
                    """
                    SELECT * FROM audit_events WHERE block_number = $1
                """,
                    block_num,
                )

                if not block_record:
                    verification_results["missing_blocks"].append(block_num)
                    verification_results["verified"] = False
                    continue

                # Verify signature
                content = {
                    "event_id": str(block_record["event_id"]),
                    "timestamp": block_record["timestamp"].isoformat(),
                    "event_type": block_record["event_type"],
                    "user_id": block_record["user_id"],
                    "org_id": block_record["org_id"],
                    "resource_type": block_record["resource_type"],
                    "resource_id": block_record["resource_id"],
                    "action": block_record["action"],
                    "details": block_record["details"],
                    "success": block_record["success"],
                }

                content_json = json.dumps(content, sort_keys=True)
                if not self._verify_signature(content_json, block_record["signature"]):
                    verification_results["invalid_signatures"].append(block_num)
                    verification_results["verified"] = False
                    continue

                # Verify chain linkage
                if block_num > 1:
                    expected_block_content = f"{
                        block_record['content_hash']}:{
                        block_record['signature']}:{
                        block_record['previous_block_hash']}:{block_num}"
                    expected_block_hash = hashlib.sha256(
                        expected_block_content.encode()
                    ).hexdigest()

                    if expected_block_hash != block_record["block_hash"]:
                        verification_results["broken_chains"].append(block_num)
                        verification_results["verified"] = False
                        continue

                verification_results["verified_blocks"] += 1

            # Update metadata
            await conn.execute(
                """
                UPDATE audit_chain_metadata
                SET chain_integrity_verified = $1, last_verification_at = NOW()
                WHERE id = 1
            """,
                verification_results["verified"],
            )

            return verification_results

    def _verify_signature(self, content: str, signature_hex: str) -> bool:
        """Verify RSA signature"""
        try:
            signature = bytes.fromhex(signature_hex)
            self.public_key.verify(
                signature,
                content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    async def get_audit_events(
        self,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Query audit events with filtering"""
        query_parts = ["SELECT * FROM audit_events WHERE 1=1"]
        params = []
        param_count = 0

        if org_id:
            param_count += 1
            query_parts.append(f"AND org_id = ${param_count}")
            params.append(org_id)

        if user_id:
            param_count += 1
            query_parts.append(f"AND user_id = ${param_count}")
            params.append(user_id)

        if event_type:
            param_count += 1
            query_parts.append(f"AND event_type = ${param_count}")
            params.append(event_type)

        if resource_type:
            param_count += 1
            query_parts.append(f"AND resource_type = ${param_count}")
            params.append(resource_type)

        if start_time:
            param_count += 1
            query_parts.append(f"AND timestamp >= ${param_count}")
            params.append(start_time)

        if end_time:
            param_count += 1
            query_parts.append(f"AND timestamp <= ${param_count}")
            params.append(end_time)

        query_parts.append("ORDER BY timestamp DESC")

        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(limit)

        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(offset)

        query = " ".join(query_parts)

        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            return [dict(record) for record in records]

    async def get_audit_proof(self, event_id: str) -> Optional[AuditProof]:
        """Get cryptographic proof for specific audit event"""
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT * FROM audit_events WHERE event_id = $1
            """,
                event_id,
            )

            if not record:
                return None

            # Verify the record's integrity
            content = {
                "event_id": str(record["event_id"]),
                "timestamp": record["timestamp"].isoformat(),
                "event_type": record["event_type"],
                "user_id": record["user_id"],
                "org_id": record["org_id"],
                "resource_type": record["resource_type"],
                "resource_id": record["resource_id"],
                "action": record["action"],
                "details": record["details"],
                "success": record["success"],
            }

            content_json = json.dumps(content, sort_keys=True)
            signature_valid = self._verify_signature(content_json, record["signature"])

            return AuditProof(
                event_id=event_id,
                content_hash=record["content_hash"],
                signature=record["signature"],
                qldb_document_id=record["qldb_document_id"],
                postgres_block_hash=record["block_hash"],
                chain_position=record["block_number"],
                verified=signature_valid,
            )

    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.qldb_driver:
            self.qldb_driver.close()
