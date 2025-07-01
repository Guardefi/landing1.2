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


# Mock db object for compatibility with Flask-SQLAlchemy style code
class MockDB:
    Column = Column
    Integer = Integer
    String = String
    Text = Text
    Boolean = Boolean
    Float = Float
    DateTime = DateTime
    ForeignKey = ForeignKey
    relationship = relationship

    def backref(self, name, **kwargs):
        return name

    @property
    def session(self):
        return SessionLocal()


db = MockDB()


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

    id = Column(Integer, primary_key=True, index=True)
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
    preferences = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def get_permissions(self):
        return json.loads(self.permissions) if self.permissions else []

    def set_permissions(self, permissions_list):
        self.permissions = json.dumps(permissions_list)

    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else {}

    def set_preferences(self, preferences_dict):
        self.preferences = json.dumps(preferences_dict)


class MEVStrategy(db.Model):
    __tablename__ = "mev_strategies"

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="inactive")
    configuration = db.Column(db.Text)  # JSON string
    total_profit = db.Column(db.Float, default=0.0)
    total_executions = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    average_gas_cost = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_executed = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("mev_strategies", lazy=True))

    def get_configuration(self):
        return json.loads(self.configuration) if self.configuration else {}

    def set_configuration(self, config_dict):
        self.configuration = json.dumps(config_dict)


class ContractScan(db.Model):
    __tablename__ = "contract_scans"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contract_address = db.Column(db.String(42), nullable=False)
    scan_type = db.Column(db.String(20), default="full")
    status = db.Column(db.String(20), default="pending")
    security_score = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    vulnerabilities_count = db.Column(db.Integer, default=0)
    is_honeypot = db.Column(db.Boolean, default=False)
    honeypot_confidence = db.Column(db.Float, default=0.0)
    scan_results = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", backref=db.backref("contract_scans", lazy=True))

    def get_scan_results(self):
        return json.loads(self.scan_results) if self.scan_results else {}

    def set_scan_results(self, results_dict):
        self.scan_results = json.dumps(results_dict)


class ThreatAlert(db.Model):
    __tablename__ = "threat_alerts"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="active")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.Text)  # JSON string
    contract_address = db.Column(db.String(42))
    transaction_hash = db.Column(db.String(66))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    acknowledged_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    acknowledged_at = db.Column(db.DateTime)

    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}

    def set_metadata(self, metadata_dict):
        self.metadata = json.dumps(metadata_dict)


class MEVOpportunity(db.Model):
    __tablename__ = "mev_opportunities"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    estimated_profit = db.Column(db.Float, nullable=False)
    estimated_gas = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    time_window = db.Column(db.Integer, nullable=False)  # seconds
    protocols = db.Column(db.Text)  # JSON array
    status = db.Column(db.String(20), default="active")
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    executed_at = db.Column(db.DateTime)
    actual_profit = db.Column(db.Float)

    def get_protocols(self):
        return json.loads(self.protocols) if self.protocols else []

    def set_protocols(self, protocols_list):
        self.protocols = json.dumps(protocols_list)


class SystemMetric(db.Model):
    __tablename__ = "system_metrics"

    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    metadata = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}

    def set_metadata(self, metadata_dict):
        self.metadata = json.dumps(metadata_dict)


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref=db.backref("sessions", lazy=True))


class MempoolTransaction(db.Model):
    __tablename__ = "mempool_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42))
    value = db.Column(db.Float, default=0.0)
    gas_price = db.Column(db.Float, nullable=False)
    gas_limit = db.Column(db.Integer, nullable=False)
    mev_probability = db.Column(db.Float, default=0.0)
    threat_level = db.Column(db.String(20), default="low")
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")


def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

import json
import os
from datetime import datetime

from sqlalchemy import (  # Create default admin user if it doesn't exist
    User,
    User.query.filter_by,
    .first,
    :,
    =,
    admin_user,
    declarative_base,
    from,
    generate_password_hash,
    if,
    import,
    not,
    relationship,
    sessionmaker,
    sqlalchemy.ext.declarative,
    sqlalchemy.orm,
    username="admin",
    werkzeug.security,
)

                username="admin",
                email="admin@scorpius.io",
                password_hash=generate_password_hash("admin123"),
                role="admin",
            )
            admin_user.set_permissions(["scan:execute", "mev:manage", "system:admin"])
            admin_user.set_preferences(
                {
                    "theme": "dark",
                    "notifications": {
                        "email": True,
                        "push": True,
                        "criticalThreats": True,
                        "mevOpportunities": True,
                        "systemAlerts": True,
                    },
                    "dashboard": {
                        "refreshInterval": 30000,
                        "defaultCharts": ["threats", "performance"],
                        "layout": "expanded",
                    },
                }
            )
            db.session.add(admin_user)

            # Create demo user
            demo_user = User(
                username="demo",
                email="demo@scorpius.io",
                password_hash=generate_password_hash("demo"),
                role="admin",
            )
            demo_user.set_permissions(["scan:execute", "mev:manage", "system:admin"])
            demo_user.set_preferences(
                {
                    "theme": "dark",
                    "notifications": {
                        "email": True,
                        "push": True,
                        "criticalThreats": True,
                        "mevOpportunities": True,
                        "systemAlerts": True,
                    },
                    "dashboard": {
                        "refreshInterval": 30000,
                        "defaultCharts": ["threats", "performance"],
                        "layout": "expanded",
                    },
                }
            )
            db.session.add(demo_user)

            # Create regular user
            regular_user = User(
                username="user",
                email="user@scorpius.io",
                password_hash=generate_password_hash("user123"),
                role="user",
            )
            regular_user.set_permissions(["scan:view"])
            regular_user.set_preferences(
                {
                    "theme": "light",
                    "notifications": {
                        "email": True,
                        "push": False,
                        "criticalThreats": True,
                        "mevOpportunities": False,
                        "systemAlerts": False,
                    },
                    "dashboard": {
                        "refreshInterval": 60000,
                        "defaultCharts": ["threats"],
                        "layout": "compact",
                    },
                }
            )
            db.session.add(regular_user)

            db.session.commit()
            print("✅ Database initialized with default users")
