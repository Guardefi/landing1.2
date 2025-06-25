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
    finally:
        pass


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
    full_name = Column(String(200), nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)

    # Add relationships to User class
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
    strategy_type = Column(String(50), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="paused")
    # Add missing fields referenced in FastAPI routes
    profit_target = Column(Float, nullable=True)
    current_profit = Column(Float, default=0.0)
    trades_executed = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    risk_level = Column(String(20), default="medium")
    parameters = Column(JSON)
    # Legacy fields (keep for compatibility)
    total_profit = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
    average_gas_cost = Column(Integer, default=0)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_executed = Column(DateTime, nullable=True)

    # Add relationships to other models
    user = relationship("User", back_populates="mev_strategies")


class MEVOpportunity(Base):
    __tablename__ = "mev_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("mev_strategies.id"), nullable=True)
    opportunity_type = Column(String(50), nullable=False)
    estimated_profit = Column(Float, nullable=False)
    block_number = Column(Integer, nullable=True)
    gas_cost = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    # Legacy fields
    estimated_gas = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    time_window = Column(Integer, nullable=False)
    protocols = Column(JSON)
    status = Column(String(20), default="detected")
    detected_at = Column(DateTime, default=datetime.now)
    executed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    actual_profit = Column(Float, nullable=True)
    gas_used = Column(Integer, nullable=True)
    transaction_hash = Column(String(66), nullable=True)
    error_message = Column(Text, nullable=True)
    data = Column(JSON)

    # Add relationships to other models
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
    # Add missing fields for mempool transactions
    transaction_type = Column(String(50), default="unknown")
    mev_potential = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    # Legacy fields
    status = Column(String(20), default="pending")
    detected_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)
    block_number = Column(Integer, nullable=True)
    mev_probability = Column(Float, default=0.0)
    threat_level = Column(String(10), default="low")

    # Add relationships to other models
    user = relationship("User", back_populates="mempool_transactions")


class ContractScan(Base):
    __tablename__ = "contract_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_address = Column(String(42), nullable=False, index=True)
    scan_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    vulnerabilities_found = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    scan_results = Column(JSON)
    error_message = Column(Text, nullable=True)

    # Add relationships to other models
    user = relationship("User", back_populates="contract_scans")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime, nullable=True)
    data = Column(JSON)

    # Add relationships to other models
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
    data = Column(JSON)

    # Add relationships to other models
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

    # Add relationships to other models
    user = relationship("User", back_populates="sessions")
