"""
Async Database Configuration for Scorpius Backend
Replaces sync SQLModel usage with async engine patterns
"""

import os
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import asyncpg

# Base for SQLAlchemy models
Base = declarative_base()
metadata = MetaData()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://scorpius:dev_password@localhost:5432/scorpius_dev')
ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Test database configuration
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://scorpius:test@localhost:5432/scorpius_test')
ASYNC_TEST_DATABASE_URL = TEST_DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self, database_url: str, async_database_url: str, echo: bool = False):
        self.database_url = database_url
        self.async_database_url = async_database_url
        self.echo = echo
        
        # Async engine for all database operations
        self.async_engine: Optional[AsyncEngine] = None
        self.async_session_factory: Optional[async_sessionmaker] = None
        
        # Sync engine only for migrations and administrative tasks
        self.sync_engine = None
        
    async def initialize(self) -> None:
        """Initialize async database connections"""
        
        # Create async engine with optimized settings
        self.async_engine = create_async_engine(
            self.async_database_url,
            echo=self.echo,
            pool_size=20,              # Number of persistent connections
            max_overflow=30,           # Additional connections on demand
            pool_pre_ping=True,        # Validate connections before use
            pool_recycle=3600,         # Recycle connections after 1 hour
            connect_args={
                "server_settings": {
                    "application_name": "scorpius_backend",
                    "jit": "off",      # Disable JIT for faster startup
                }
            }
        )
        
        # Create async session factory
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,    # Keep objects accessible after commit
            autoflush=True,
            autocommit=False,
        )
    
    async def close(self) -> None:
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with proper cleanup"""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False

# Global database configuration instances
db_config = DatabaseConfig(
    database_url=DATABASE_URL,
    async_database_url=ASYNC_DATABASE_URL,
    echo=os.getenv('DEBUG', 'false').lower() == 'true'
)

test_db_config = DatabaseConfig(
    database_url=TEST_DATABASE_URL,
    async_database_url=ASYNC_TEST_DATABASE_URL,
    echo=True
)

# Dependency for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions"""
    async with db_config.get_async_session() as session:
        yield session

# Legacy sync session for migration compatibility (DEPRECATED)
def get_sync_session():
    """
    DEPRECATED: Sync session for legacy code only
    Use get_async_session() for all new code
    """
    import warnings
    warnings.warn(
        "Sync database sessions are deprecated. Use async sessions instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    if not db_config.sync_engine:
        db_config.sync_engine = create_engine(DATABASE_URL, echo=db_config.echo)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_config.sync_engine)
    return SessionLocal()

# Async database operations utilities
class AsyncDatabaseUtils:
    """Utility functions for async database operations"""
    
    @staticmethod
    async def execute_raw_sql(query: str, params: dict = None) -> list:
        """Execute raw SQL query asynchronously"""
        async with db_config.get_async_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    @staticmethod
    async def check_table_exists(table_name: str) -> bool:
        """Check if table exists in database"""
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
        );
        """
        result = await AsyncDatabaseUtils.execute_raw_sql(
            query, 
            {"table_name": table_name}
        )
        return result[0][0] if result else False
    
    @staticmethod
    async def get_table_info(table_name: str) -> dict:
        """Get table structure information"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :table_name
        ORDER BY ordinal_position;
        """
        result = await AsyncDatabaseUtils.execute_raw_sql(
            query,
            {"table_name": table_name}
        )
        return [
            {
                "column": row[0],
                "type": row[1], 
                "nullable": row[2] == 'YES',
                "default": row[3]
            }
            for row in result
        ]

# Migration utilities
class AsyncMigrationUtils:
    """Utilities for database migrations with async support"""
    
    @staticmethod
    async def create_tables_async():
        """Create all tables using async engine"""
        async with db_config.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def drop_tables_async():
        """Drop all tables using async engine"""
        async with db_config.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @staticmethod
    async def reset_database_async():
        """Reset database (drop and recreate all tables)"""
        await AsyncMigrationUtils.drop_tables_async()
        await AsyncMigrationUtils.create_tables_async()

# Context manager for database lifecycle
@asynccontextmanager
async def database_lifespan():
    """Context manager for database initialization and cleanup"""
    try:
        await db_config.initialize()
        yield db_config
    finally:
        await db_config.close()

# FastAPI lifespan event handler
async def init_database():
    """Initialize database for FastAPI application"""
    await db_config.initialize()

async def close_database():
    """Close database connections for FastAPI application"""
    await db_config.close()
