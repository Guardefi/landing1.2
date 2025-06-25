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


class MEVStrategy(Base):
    __tablename__ = "mev_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="paused")
    total_profit = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
    average_gas_cost = Column(Integer, default=0)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_executed = Column(DateTime, nullable=True)


class MEVOpportunity(Base):
    __tablename__ = "mev_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_type = Column(String(50), nullable=False)
    estimated_profit = Column(Float, nullable=False)
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
    status = Column(String(20), default="pending")
    detected_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)
    block_number = Column(Integer, nullable=True)
    mev_probability = Column(Float, default=0.0)
    threat_level = Column(String(10), default="low")


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
