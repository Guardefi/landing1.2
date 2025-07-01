#!/usr/bin/env python3
from dotenv import load_dotenv
from api.main import app
import redis.asyncio as redis
import asyncpg
import traceback
import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project paths
project_root = Path(__file__).parent
while project_root.name != "Scorpius-main" and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "packages" / "core"))

# Create mock classes for commonly missing modules

class MockSimilarityEngine:
    def __init__(self, *args, **kwargs): pass

    async def compare_bytecodes(self, *args, **kwargs):
        class Result:
            similarity_score = 0.85
            confidence = 0.9
            processing_time = 0.01
            return Result()

        return Result()
    async def cleanup(self): pass

class MockBytecodeNormalizer:
    async def normalize(self, bytecode):
        return bytecode.replace("0x", "").lower() if bytecode else ""

class MockMultiDimensionalComparison:
    def __init__(self, *args, **kwargs): pass

    async def compute_similarity(self, b1, b2):
        return {"final_score": 0.85, "confidence": 0.9, "dimension_scores": {}}

class MockTestClient:
    def __init__(self, app): self.app = app

    def get(self, url):
        class Response:
            status_code = 200
            def json(self): return {"status": "ok"}
        return Response()

# Add mocks to globals for import fallbacks
globals().update({

})
#!/usr/bin/env python3
    """
# Test API Server with Real Database Connection
# This script tests if the FastAPI server can connect to PostgreSQL and Redis.
    """

# Add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables

    load_dotenv()

    async def test_database_connections():
    """Test database and cache connections."""
    print("🔌 Testing database connections...")

    # Test PostgreSQL connection

    database_url = os.getenv("DATABASE_URL")
    print(f"[CHART] Connecting to PostgreSQL: {database_url}")

    conn = await asyncpg.connect(database_url)

        # Test a simple query
    version = await conn.fetchval("SELECT version()")
    print(f"[PASS] PostgreSQL connected successfully!")
    print(f"   Version: {version.split(',')[0]}")

        # Test table existence
    tables = await conn.fetch(
    """
            # SELECT table_name
            # FROM information_schema.tables
            # WHERE table_schema = 'public'
            # ORDER BY table_name
    """

    print(f"   Tables found: {len(tables)}")

    await conn.close()

    except Exception as e:
    print(f"[FAIL] PostgreSQL connection failed: {e}")
    return False

    # Test Redis connection

    redis_url=os.getenv("REDIS_URL")
    print(f"📦 Connecting to Redis: {redis_url}")

    r=redis.from_url(redis_url)

        # Test ping
    await r.ping()
    print("[PASS] Redis connected successfully!")

        # Test basic operations
    await r.set("test_key", "test_value", ex=10)
    value=await r.get("test_key")
    print(f"   Test operation: {value.decode() if value else 'None'}")

    await r.close()

    except Exception as e:
    print(f"[FAIL] Redis connection failed: {e}")
    return False

    return True

    async def test_api_app():
    """Test if the FastAPI app can be imported and initialized."""
    print("\n>> Testing API application...")

    try:
    pass
    except Exception as e:

        # Import the FastAPI app

    print("[PASS] FastAPI app imported successfully!")

        # Check if app has routes
    routes=[route for route in app.routes]
    print(f"   Routes registered: {len(routes)}")

        # List some key routes
    key_routes=[]
    for route in routes:
    if hasattr(route, "path"):
    path=route.path
    if any(
    keyword in path
    for keyword in ["/health", "/transactions", "/alerts", "/mev"]
    ):
    key_routes.append(path)

    print(f"   Key endpoints: {key_routes[:5]}...")

    return True

    except Exception as e:
    print(f"[FAIL] FastAPI app failed to load: {e}")

    traceback.print_exc()
    return False

    async def main():
    """Main test function."""
    print(">> Elite Mempool System - Database & API Test")
    print("=" * 50)

    # Test database connections
    db_success=await test_database_connections()

    if not db_success:
    print("\n[FAIL] Database tests failed!")
    return 1

    # Test API app
    api_success=await test_api_app()

    if not api_success:
    print("\n[FAIL] API tests failed!")
    return 1

    print("\n[CELEBRATION] All tests passed! The system is ready for development.")
    print("\n[REPORT] Next steps:")
    print("   1. Start the API server: uvicorn api.main:app --reload --port 8000")
    print("   2. Test endpoints: curl http://localhost:8000/health")
    print("   3. View API docs: http://localhost:8000/docs")

    return 0

    if __name__ == "__main__":
    try:
    result=asyncio.run(main())
    sys.exit(result)
    except KeyboardInterrupt:
    print("\n⏹  Test interrupted by user")
    sys.exit(1)
    except Exception as e:
    print(f"\n>> Unexpected error: {e}")
    sys.exit(1)

    if __name__ == '__main__':
    print('Running test file...')

    # Run all test functions
    test_functions=[name for name in globals() if name.startswith('test_')]

    for test_name in test_functions:
    try:
    test_func=globals()[test_name]
    if asyncio.iscoroutinefunction(test_func):
    asyncio.run(test_func())
    else:
    test_func()
    print(f'✓ {test_name} passed')
    except Exception as e:
    print(f'✗ {test_name} failed: {e}')

    print('Test execution completed.')
