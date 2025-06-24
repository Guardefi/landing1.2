"""
Database models and persistence layer for Scorpius Bridge
"""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, Numeric, String, Text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config.settings import settings
from ..core.types import (
    BridgeTransfer,
    ChainType,
    SecurityLevel,
    TransferStatus,
    ValidatorNode,
)

logger = logging.getLogger(__name__)

# Create base class for database models
Base = declarative_base()


class BridgeTransferDB(Base):
    """Database model for bridge transfers."""

    __tablename__ = "bridge_transfers"

    # Primary fields
    id = Column(String(64), primary_key=True)
    from_chain = Column(SQLEnum(ChainType), nullable=False)
    to_chain = Column(SQLEnum(ChainType), nullable=False)
    asset = Column(String(20), nullable=False)
    amount = Column(Numeric(precision=28, scale=18), nullable=False)
    sender_address = Column(String(42), nullable=False)
    receiver_address = Column(String(42), nullable=False)
    bridge_type = Column(String(20), nullable=False)
    status = Column(SQLEnum(TransferStatus), nullable=False)

    # Transaction hashes
    source_tx_hash = Column(String(66), nullable=True)
    dest_tx_hash = Column(String(66), nullable=True)
    lock_tx_hash = Column(String(66), nullable=True)
    mint_tx_hash = Column(String(66), nullable=True)

    # Security and validation
    security_level = Column(SQLEnum(SecurityLevel), default=SecurityLevel.STANDARD)
    required_confirmations = Column(Integer, default=12)
    current_confirmations = Column(Integer, default=0)
    validator_signatures = Column(JSON, default=list)

    # Financial information
    bridge_fee = Column(Numeric(precision=28, scale=18), default=Decimal("0"))
    gas_cost = Column(Numeric(precision=28, scale=18), default=Decimal("0"))
    exchange_rate = Column(Numeric(precision=28, scale=18), default=Decimal("1"))

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    initiated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Retry and error handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_retry_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # User tracking
    user_id = Column(String(64), nullable=True)
    session_id = Column(String(64), nullable=True)
    # Metadata (renamed to avoid SQLAlchemy conflict)
    transfer_metadata = Column(JSON, default=dict)

    # Indexes for performance
    __table_args__ = ({"mysql_engine": "InnoDB"},)

    @classmethod
    def from_transfer(cls, transfer: BridgeTransfer) -> "BridgeTransferDB":
        """Create database model from domain object."""
        return cls(
            id=transfer.id,
            from_chain=transfer.from_chain,
            to_chain=transfer.to_chain,
            asset=transfer.asset,
            amount=transfer.amount,
            sender_address=transfer.sender_address,
            receiver_address=transfer.receiver_address,
            bridge_type=transfer.bridge_type.value,
            status=transfer.status,
            source_tx_hash=transfer.source_tx_hash,
            dest_tx_hash=transfer.dest_tx_hash,
            lock_tx_hash=transfer.lock_tx_hash,
            mint_tx_hash=transfer.mint_tx_hash,
            security_level=transfer.security_level,
            required_confirmations=transfer.required_confirmations,
            current_confirmations=transfer.current_confirmations,
            validator_signatures=transfer.validator_signatures,
            bridge_fee=transfer.bridge_fee,
            gas_cost=transfer.gas_cost,
            exchange_rate=transfer.exchange_rate,
            timestamp=transfer.timestamp,
            initiated_at=transfer.initiated_at,
            completed_at=transfer.completed_at,
            expires_at=transfer.expires_at,
            retry_count=transfer.retry_count,
            max_retries=transfer.max_retries,
            last_retry_at=transfer.last_retry_at,
            error_message=transfer.error_message,
            user_id=transfer.user_id,
            session_id=transfer.session_id,
            metadata=transfer.metadata,
        )

    def to_transfer(self) -> BridgeTransfer:
        """Convert database model to domain object."""
        from .types import BridgeType  # Avoid circular import

        return BridgeTransfer(
            id=self.id,
            from_chain=self.from_chain,
            to_chain=self.to_chain,
            asset=self.asset,
            amount=self.amount,
            sender_address=self.sender_address,
            receiver_address=self.receiver_address,
            bridge_type=BridgeType(self.bridge_type),
            status=self.status,
            timestamp=self.timestamp,
            source_tx_hash=self.source_tx_hash,
            dest_tx_hash=self.dest_tx_hash,
            lock_tx_hash=self.lock_tx_hash,
            mint_tx_hash=self.mint_tx_hash,
            security_level=self.security_level,
            required_confirmations=self.required_confirmations,
            current_confirmations=self.current_confirmations,
            validator_signatures=self.validator_signatures or [],
            bridge_fee=self.bridge_fee,
            gas_cost=self.gas_cost,
            exchange_rate=self.exchange_rate,
            initiated_at=self.initiated_at,
            completed_at=self.completed_at,
            expires_at=self.expires_at,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            last_retry_at=self.last_retry_at,
            error_message=self.error_message,
            user_id=self.user_id,
            session_id=self.session_id,
            metadata=self.transfer_metadata or {},
        )


class ValidatorNodeDB(Base):
    """Database model for validator nodes."""

    __tablename__ = "validator_nodes"

    id = Column(String(64), primary_key=True)
    address = Column(String(42), nullable=False, unique=True)
    public_key = Column(Text, nullable=False)
    stake_amount = Column(Numeric(precision=28, scale=18), nullable=False)
    reputation_score = Column(Numeric(precision=5, scale=2), default=Decimal("100"))
    active = Column(Boolean, default=True)

    # Timestamps
    last_seen = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_validation_at = Column(DateTime, nullable=True)

    # Performance metrics
    validated_transfers = Column(BigInteger, default=0)
    slashing_events = Column(Integer, default=0)
    response_time_avg = Column(Numeric(precision=10, scale=3), default=Decimal("0"))
    uptime_percentage = Column(Numeric(precision=5, scale=2), default=Decimal("100"))
    validation_accuracy = Column(Numeric(precision=5, scale=2), default=Decimal("100"))

    # Financial tracking
    total_rewards_earned = Column(Numeric(precision=28, scale=18), default=Decimal("0"))
    total_slashed = Column(Numeric(precision=28, scale=18), default=Decimal("0"))

    @classmethod
    def from_validator(cls, validator: ValidatorNode) -> "ValidatorNodeDB":
        """Create database model from domain object."""
        return cls(
            id=validator.id,
            address=validator.address,
            public_key=validator.public_key,
            stake_amount=validator.stake_amount,
            reputation_score=Decimal(str(validator.reputation_score)),
            active=validator.active,
            last_seen=validator.last_seen,
            joined_at=validator.joined_at,
            last_validation_at=validator.last_validation_at,
            validated_transfers=validator.validated_transfers,
            slashing_events=validator.slashing_events,
            response_time_avg=Decimal(str(validator.response_time_avg)),
            uptime_percentage=Decimal(str(validator.uptime_percentage)),
            validation_accuracy=Decimal(str(validator.validation_accuracy)),
            total_rewards_earned=validator.total_rewards_earned,
            total_slashed=validator.total_slashed,
        )

    def to_validator(self) -> ValidatorNode:
        """Convert database model to domain object."""
        return ValidatorNode(
            id=self.id,
            address=self.address,
            public_key=self.public_key,
            stake_amount=self.stake_amount,
            reputation_score=float(self.reputation_score),
            active=self.active,
            last_seen=self.last_seen,
            joined_at=self.joined_at,
            last_validation_at=self.last_validation_at,
            validated_transfers=self.validated_transfers,
            slashing_events=self.slashing_events,
            response_time_avg=float(self.response_time_avg),
            uptime_percentage=float(self.uptime_percentage),
            validation_accuracy=float(self.validation_accuracy),
            total_rewards_earned=self.total_rewards_earned,
            total_slashed=self.total_slashed,
        )


class DatabaseManager:
    """Manages database operations for the bridge network."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None

    async def initialize(self):
        """Initialize database connections."""
        try:
            # Create async engine for main operations
            self.async_engine = create_async_engine(
                self.database_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

            # Create async session factory
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine, class_=AsyncSession, expire_on_commit=False
            )

            # Create sync engine for migrations
            sync_url = self.database_url.replace("+asyncpg", "").replace(
                "+aiomysql", ""
            )
            self.engine = create_engine(sync_url)

            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            logger.info("Database connections initialized")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e from e

    async def create_tables(self):
        """Create database tables."""
        try:
            # Use async engine to create tables
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise e from e

    async def get_session(self) -> AsyncSession:
        """Get an async database session."""
        if not self.AsyncSessionLocal:
            await self.initialize()

        return self.AsyncSessionLocal()

    async def save_transfer(self, transfer: BridgeTransfer) -> bool:
        """Save or update a bridge transfer."""
        try:
            async with await self.get_session() as session:
                # Check if transfer exists
                existing = await session.get(BridgeTransferDB, transfer.id)

                if existing:
                    # Update existing transfer
                    for key, value in BridgeTransferDB.from_transfer(
                        transfer
                    ).__dict__.items():
                        if not key.startswith("_"):
                            setattr(existing, key, value)
                else:
                    # Create new transfer
                    db_transfer = BridgeTransferDB.from_transfer(transfer)
                    session.add(db_transfer)

                await session.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to save transfer {transfer.id}: {e}")
            return False

    async def get_transfer(self, transfer_id: str) -> BridgeTransfer | None:
        """Get a bridge transfer by ID."""
        try:
            async with await self.get_session() as session:
                db_transfer = await session.get(BridgeTransferDB, transfer_id)
                return db_transfer.to_transfer() if db_transfer else None

        except Exception as e:
            logger.error(f"Failed to get transfer {transfer_id}: {e}")
            return None

    async def save_validator(self, validator: ValidatorNode) -> bool:
        """Save or update a validator node."""
        try:
            async with await self.get_session() as session:
                # Check if validator exists
                existing = await session.get(ValidatorNodeDB, validator.id)

                if existing:
                    # Update existing validator
                    for key, value in ValidatorNodeDB.from_validator(
                        validator
                    ).__dict__.items():
                        if not key.startswith("_"):
                            setattr(existing, key, value)
                else:
                    # Create new validator
                    db_validator = ValidatorNodeDB.from_validator(validator)
                    session.add(db_validator)

                await session.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to save validator {validator.id}: {e}")
            return False

    async def get_validator(self, validator_id: str) -> ValidatorNode | None:
        """Get a validator node by ID."""
        try:
            async with await self.get_session() as session:
                db_validator = await session.get(ValidatorNodeDB, validator_id)
                return db_validator.to_validator() if db_validator else None

        except Exception as e:
            logger.error(f"Failed to get validator {validator_id}: {e}")
            return None

    async def get_active_validators(self) -> list[ValidatorNode]:
        """Get all active validator nodes."""
        try:
            async with await self.get_session() as session:
                from sqlalchemy import select

                result = await session.execute(
                    select(ValidatorNodeDB).where(ValidatorNodeDB.active == True)
                )
                db_validators = result.scalars().all()

                return [v.to_validator() for v in db_validators]

        except Exception as e:
            logger.error(f"Failed to get active validators: {e}")
            return []

    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()

        logger.info("Database connections closed")


# Global database manager instance
_db_manager: DatabaseManager | None = None


async def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
        await _db_manager.create_tables()

    return _db_manager


async def close_database():
    """Close the global database manager."""
    global _db_manager

    if _db_manager:
        await _db_manager.close()
        _db_manager = None
