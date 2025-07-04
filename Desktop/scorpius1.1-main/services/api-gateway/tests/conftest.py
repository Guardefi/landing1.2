import asyncio
import os

import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Set required env vars before importing the gateway
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, os.path.join(repo_root, "services", "api-gateway"))

import enhanced_gateway as gateway

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
def client(event_loop):
    engine = create_async_engine(os.environ["DATABASE_URL"])
    gateway.db_engine = engine
    gateway.session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def setup():
        async with engine.begin() as conn:
            await conn.run_sync(gateway.metadata.create_all)
            hashed = gateway.pwd_context.hash("password123")
            await conn.execute(
                gateway.users_table.insert().values(
                    id="user123",
                    email="user@example.com",
                    username="user",
                    password_hash=hashed,
                    roles="user",
                )
            )
    event_loop.run_until_complete(setup())

    with TestClient(gateway.app) as c:
        yield c

    event_loop.run_until_complete(engine.dispose())
