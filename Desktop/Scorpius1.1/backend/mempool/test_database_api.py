#!/usr/bin/env python3
"""
Test API Server with Real Database Connection
This script tests if the FastAPI server can connect to PostgreSQL and Redis.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


async def test_database_connections():
    """Test database and cache connections."""
    print("🔌 Testing database connections...")

    # Test PostgreSQL connection
    try:
        import asyncpg

        database_url = os.getenv("DATABASE_URL")
        print(f"📊 Connecting to PostgreSQL: {database_url}")

        conn = await asyncpg.connect(database_url)

        # Test a simple query
        version = await conn.fetchval("SELECT version()")
        print(f"✅ PostgreSQL connected successfully!")
        print(f"   Version: {version.split(',')[0]}")

        # Test table existence
        tables = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """
        )
        print(f"   Tables found: {len(tables)}")

        await conn.close()

    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

    # Test Redis connection
    try:
        import redis.asyncio as redis

        redis_url = os.getenv("REDIS_URL")
        print(f"📦 Connecting to Redis: {redis_url}")

        r = redis.from_url(redis_url)

        # Test ping
        await r.ping()
        print("✅ Redis connected successfully!")

        # Test basic operations
        await r.set("test_key", "test_value", ex=10)
        value = await r.get("test_key")
        print(f"   Test operation: {value.decode() if value else 'None'}")

        await r.close()

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

    return True


async def test_api_app():
    """Test if the FastAPI app can be imported and initialized."""
    print("\n🚀 Testing API application...")

    try:
        # Import the FastAPI app
        from api.main import app

        print("✅ FastAPI app imported successfully!")

        # Check if app has routes
        routes = [route for route in app.routes]
        print(f"   Routes registered: {len(routes)}")

        # List some key routes
        key_routes = []
        for route in routes:
            if hasattr(route, "path"):
                path = route.path
                if any(
                    keyword in path
                    for keyword in ["/health", "/transactions", "/alerts", "/mev"]
                ):
                    key_routes.append(path)

        print(f"   Key endpoints: {key_routes[:5]}...")

        return True

    except Exception as e:
        print(f"❌ FastAPI app failed to load: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧪 Elite Mempool System - Database & API Test")
    print("=" * 50)

    # Test database connections
    db_success = await test_database_connections()

    if not db_success:
        print("\n❌ Database tests failed!")
        return 1

    # Test API app
    api_success = await test_api_app()

    if not api_success:
        print("\n❌ API tests failed!")
        return 1

    print("\n🎉 All tests passed! The system is ready for development.")
    print("\n📋 Next steps:")
    print("   1. Start the API server: uvicorn api.main:app --reload --port 8000")
    print("   2. Test endpoints: curl http://localhost:8000/health")
    print("   3. View API docs: http://localhost:8000/docs")

    return 0


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
