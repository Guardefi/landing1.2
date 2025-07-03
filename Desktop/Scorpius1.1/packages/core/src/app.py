#!/usr/bin/env python3
"""
SCORPIUS BACKEND - MAIN APPLICATION
Entry point for the Scorpius Security Platform backend.
"""


# Import database initialization

# Import route blueprints
try:
    except ImportError:
    auth_bp = None

try:
    except ImportError:
    dashboard_bp = None

try:
    except ImportError:
    scanner_bp = None

try:
    except ImportError:
    mev_bp = None

try:
    except ImportError:
    mempool_bp = None

try:
    except ImportError:
    settings_bp = None

try:
    except ImportError:
    time_machine_bp = None

try:
    except ImportError:
    monitoring_bp = None

try:
    except ImportError:
    reports_bp = None

try:
    except ImportError:
    system_bp = None

try:
    except ImportError:
    files_bp = None


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration from environment
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "VITE_JWT_SECRET", "development-secret-key-change-in-production"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    # Initialize database
    init_database()

    # Enable CORS for frontend
    CORS(
        app,
        origins=[
            "http://localhost:8083",  # Your frontend port
            "http://localhost:8080",  # Alternative frontend port
            "http://localhost:3000",  # Development port
        ],
import logging
import os
from datetime import timedelta

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import init_database
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.files_routes import files_bp
from routes.mempool_routes import mempool_bp
from routes.mev_routes import mev_bp
from routes.monitoring_routes import monitoring_bp
from routes.reports_routes import reports_bp
from routes.scanner_routes import scanner_bp
from routes.settings_routes import settings_bp
from routes.system_routes import system_bp
from routes.time_machine_routes import time_machine_bp

    )

    # Initialize JWT
    JWTManager(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )  # Register blueprints (only if successfully imported)
    if auth_bp:
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
    if dashboard_bp:
        app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    if scanner_bp:
        app.register_blueprint(scanner_bp, url_prefix="/api/scanner")
    if mev_bp:
        app.register_blueprint(mev_bp, url_prefix="/api/mev")
    if mempool_bp:
        app.register_blueprint(mempool_bp, url_prefix="/api/mempool")
    if settings_bp:
        app.register_blueprint(settings_bp, url_prefix="/api/settings")
    if time_machine_bp:
        app.register_blueprint(time_machine_bp, url_prefix="/api/time-machine")
    if monitoring_bp:
        app.register_blueprint(monitoring_bp, url_prefix="/api/monitoring")
    if reports_bp:
        app.register_blueprint(reports_bp, url_prefix="/api/reports")
    if system_bp:
        app.register_blueprint(system_bp)  # No prefix for /health endpoint
    if files_bp:
        app.register_blueprint(files_bp, url_prefix="/api/files")

    return app


if __name__ == "__main__":
    app = create_app()

    print("🚀 Starting Scorpius Backend API Server...")
    print("=" * 60)
    print("📋 Available endpoint modules:")
    print("   Authentication: /api/auth/*")
    print("   Dashboard: /api/dashboard/*")
    print("   Scanner: /api/scanner/*")
    print("   MEV Operations: /api/mev/*")
    print("   Mempool: /api/mempool/*")
    print("   Settings: /api/settings/*")
    print("   Time Machine: /api/time-machine/*")
    print("   Monitoring: /api/monitoring/*")
    print("   Reports: /api/reports/*")
    print("   System Health: /health")
    print("")
    print("=" * 60)
    print("🌐 Frontend URL: http://localhost:8083")
    print("🔗 Backend URL: http://localhost:8001")
    print("")
    print("🔑 Test Login Credentials:")
    print("   Username: demo    | Password: demo")
    print("   Username: admin   | Password: admin123")
    print("   Username: user    | Password: user123")
    print("")

    # Run the Flask development server
    app.run(host="0.0.0.0", port=8001, debug=True, threaded=True)
