"""
Database Models and Configuration
SQLAlchemy models for the Scorpius platform
"""


    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///scorpius.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = "users"
import os
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    =,
    declarative_base,
    from,
    id,
    import,
    index=True,
    primary_key=True,
    relationship,
    sessionmaker,
    sqlalchemy.ext.declarative,
    sqlalchemy.orm,
)

    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    mev_strategies = relationship("MEVStrategy", back_populates="user")
    mev_opportunities = relationship("MEVOpportunity", back_populates="user")
    mempool_transactions = relationship("MempoolTransaction", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    contract_scans = relationship("ContractScan", back_populates="user")
    system_metrics = relationship("SystemMetric", back_populates="user")
    sessions = relationship("Session", back_populates="user")


class MEVStrategy(Base):
    __tablename__ = "mev_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    strategy_type = Column(
        String(50), nullable=False
    )  # arbitrage, sandwich, liquidation
    description = Column(Text)
    status = Column(String(20), default="paused")  # active, paused, stopped
    total_profit = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
    average_gas_cost = Column(Integer, default=0)
    config = Column(JSON)  # Strategy configuration
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_executed = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="mev_strategies")


class MEVOpportunity(Base):
    __tablename__ = "mev_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_type = Column(
        String(50), nullable=False
    )  # arbitrage, sandwich, liquidation
    estimated_profit = Column(Float, nullable=False)
    estimated_gas = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    time_window = Column(Integer, nullable=False)  # seconds
    protocols = Column(JSON)  # List of protocols involved
    status = Column(
        String(20), default="detected"
    )  # detected, executing, completed, failed, expired
    detected_at = Column(DateTime, default=datetime.now)
    executed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    actual_profit = Column(Float, nullable=True)
    gas_used = Column(Integer, nullable=True)
    transaction_hash = Column(String(66), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON)  # Additional opportunity data

    # Relationships
    user = relationship("User", back_populates="mev_opportunities")


class MempoolTransaction(Base):
    __tablename__ = "mempool_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_hash = Column(String(66), nullable=False, index=True)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=True)
    value = Column(Float, default=0.0)
    gas_price = Column(Float, nullable=False)
    gas_limit = Column(Integer, nullable=False)
    nonce = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    detected_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)
    block_number = Column(Integer, nullable=True)
    mev_probability = Column(Float, default=0.0)
    threat_level = Column(String(10), default="low")  # low, medium, high

    # Relationships
    user = relationship("User", back_populates="mempool_transactions")


class ContractScan(Base):
    __tablename__ = "contract_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_address = Column(String(42), nullable=False, index=True)
    scan_type = Column(String(50), nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    vulnerabilities_found = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    scan_results = Column(JSON)  # Detailed scan results
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="contract_scans")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="active")  # active, dismissed, resolved
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)  # Additional alert data

    # Relationships
    user = relationship("User", back_populates="alerts")


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)
    metadata = Column(JSON)  # Additional metric data

    # Relationships
    user = relationship("User", back_populates="system_metrics")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
