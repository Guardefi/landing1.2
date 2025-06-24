"""
Master FastAPI entrypoint for Scorpius X.
Aggregates routers from every module into one unified API.
Run with:  uvicorn main:app --host 0.0.0.0 --port 8000
"""

from bytecode_analyzer.bytecode_api_server import router as bytecode_router
from config_routes import router as config_router
from dashboard_routes import router as dashboard_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from honeypot_detector.honeypot_api_server import router as honeypot_router
from mempool_monitor.mempool_api_server import router as mempool_router
from mev_bot.mev_router import router as mev_router
from reporting.reporting_api_server import router as reporting_router
from settings.settings_api_server import router as settings_router
from system_health import router as system_router
from time_machine.time_machine_api_server import router as timemachine_router
from vulnerability_scanner.scanner_api_server import router as scanner_router

# --- New routers provided in this bundle ---

# --- Core module routers (already exist in your codebase) ---

# -------------------------------------------------------------

app = FastAPI(
    title="Scorpius X • Unified API",
    version="1.0.0",
)

# Allow everything in dev; lock down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
for r in [
    scanner_router,
    mempool_router,
    honeypot_router,
    bytecode_router,
    mev_router,
    reporting_router,
    timemachine_router,
    config_router,
    dashboard_router,
    system_router,
    settings_router,
]:
    app.include_router(r, prefix="/api")
