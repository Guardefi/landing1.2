#!/usr/bin/env python3
"""
Debug API Routes
Check what routes are registered in the FastAPI app.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.main import app

    print("🔍 Registered routes in FastAPI app:")
    print("=" * 50)

    for route in app.routes:
        methods = getattr(route, "methods", {"GET"})
        print(f"  {route.path} - Methods: {list(methods)}")

    print(f"\nTotal routes: {len(app.routes)}")

    # Check router registration
    print("\n🔍 Checking router includes:")

    # Try to access each router
    from api.routers import (
        alerts_router,
        analytics_router,
        mev_router,
        rules_router,
        transactions_router,
        websocket_router,
    )

    routers = [
        ("transactions", transactions_router),
        ("alerts", alerts_router),
        ("rules", rules_router),
        ("mev", mev_router),
        ("analytics", analytics_router),
        ("websocket", websocket_router),
    ]

    for name, router in routers:
        route_count = len(router.routes) if hasattr(router, "routes") else 0
        print(f"  {name}_router: {route_count} routes")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
