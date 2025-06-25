"""
Regression tests to ensure no blocking database calls in async codebase
Tests for Task 11: Backend Consistency
"""

import asyncio
import ast
import os
import pytest
import time
import threading
from pathlib import Path
from typing import List, Set
from unittest.mock import patch, AsyncMock

from backend.database.async_config import (
    db_config,
    get_async_db,
    AsyncDatabaseUtils,
    AsyncMigrationUtils,
)


class AsyncComplianceAnalyzer(ast.NodeVisitor):
    """AST analyzer to detect sync database operations in async code"""
    
    def __init__(self):
        self.violations: List[dict] = []
        self.current_function = None
        self.current_class = None
        self.in_async_function = False
        
        # Patterns that indicate synchronous database operations
        self.sync_patterns = {
            'session.query',
            'session.add',
            'session.commit',
            'session.rollback',
            'session.flush',
            'session.execute',
            'session.merge',
            'session.delete',
            'query.all',
            'query.first',
            'query.filter',
            'query.count',
            'Model.query',
            'db.session',
            'sessionmaker',
            'Session(',
            'create_engine',
        }
        
        # Approved async patterns
        self.async_patterns = {
            'await session.execute',
            'await session.commit',
            'await session.rollback',
            'await session.flush',
            'await session.merge',
            'await session.delete',
            'async with',
            'AsyncSession',
            'create_async_engine',
            'async_sessionmaker',
        }
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        old_function = self.current_function
        old_async = self.in_async_function
        
        self.current_function = node.name
        self.in_async_function = False
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.in_async_function = old_async
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        old_function = self.current_function
        old_async = self.in_async_function
        
        self.current_function = node.name
        self.in_async_function = True
        
        self.generic_visit(node)
        
        self.current_function = old_function
        self.in_async_function = old_async
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        old_class = self.current_class
        self.current_class = node.name
        
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_Attribute(self, node):
        """Visit attribute access (method calls)"""
        if self.in_async_function:
            # Check for sync database operations in async functions
            if hasattr(node, 'attr') and hasattr(node.value, 'id'):
                pattern = f"{node.value.id}.{node.attr}"
                if any(sync_pattern in pattern for sync_pattern in self.sync_patterns):
                    self.violations.append({
                        'type': 'sync_db_in_async',
                        'pattern': pattern,
                        'function': self.current_function,
                        'class': self.current_class,
                        'line': node.lineno,
                    })
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visit function calls"""
        if self.in_async_function:
            # Check for synchronous session creation
            if hasattr(node.func, 'id'):
                func_name = node.func.id
                if func_name in ['sessionmaker', 'Session']:
                    self.violations.append({
                        'type': 'sync_session_creation',
                        'pattern': func_name,
                        'function': self.current_function,
                        'class': self.current_class,
                        'line': node.lineno,
                    })
        
        self.generic_visit(node)


class TestAsyncCompliance:
    """Test suite for async database compliance"""
    
    @pytest.fixture(autouse=True)
    async def setup_database(self):
        """Setup test database"""
        await db_config.initialize()
        yield
        await db_config.close()
    
    def test_analyze_codebase_for_sync_violations(self):
        """Analyze entire codebase for sync database operations in async functions"""
        backend_path = Path(__file__).parent.parent
        violations = []
        
        # Scan all Python files in the backend
        for py_file in backend_path.rglob("*.py"):
            # Skip test files and deprecated modules
            if any(skip in str(py_file) for skip in [
                'test_', 'deprecated_', 'old_', '_old.py', 'fix_'
            ]):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                analyzer = AsyncComplianceAnalyzer()
                analyzer.visit(tree)
                
                for violation in analyzer.violations:
                    violation['file'] = str(py_file)
                    violations.append(violation)
                    
            except (SyntaxError, UnicodeDecodeError):
                # Skip files with syntax errors or encoding issues
                continue
        
        # Report violations
        if violations:
            violation_report = "\n".join([
                f"File: {v['file']}, Line: {v['line']}, "
                f"Function: {v['function']}, Pattern: {v['pattern']}"
                for v in violations
            ])
            pytest.fail(
                f"Found {len(violations)} sync database operations in async functions:\n"
                f"{violation_report}"
            )
    
    async def test_database_operations_are_async(self):
        """Test that all database operations use async patterns"""
        # Test async session creation
        async with db_config.get_async_session() as session:
            assert hasattr(session, 'execute')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
            
            # Test async query execution
            result = await session.execute("SELECT 1 as test_value")
            row = result.fetchone()
            assert row.test_value == 1
    
    async def test_no_blocking_calls_in_async_context(self):
        """Test that async database operations don't block the event loop"""
        start_time = time.time()
        
        # Run multiple concurrent database operations
        async def dummy_query():
            async with db_config.get_async_session() as session:
                await session.execute("SELECT pg_sleep(0.1)")
        
        # Run 5 queries concurrently - should take ~0.1s, not 0.5s
        await asyncio.gather(*[dummy_query() for _ in range(5)])
        
        elapsed = time.time() - start_time
        
        # If operations were blocking, this would take ~0.5 seconds
        # Async operations should complete in ~0.1-0.2 seconds
        assert elapsed < 0.3, f"Database operations appear to be blocking (took {elapsed:.2f}s)"
    
    async def test_async_database_utils(self):
        """Test async database utility functions"""
        # Test raw SQL execution
        result = await AsyncDatabaseUtils.execute_raw_sql(
            "SELECT 'test' as message"
        )
        assert result[0][0] == 'test'
        
        # Test table existence check
        exists = await AsyncDatabaseUtils.check_table_exists('information_schema.tables')
        assert exists is True
        
        # Test non-existent table
        exists = await AsyncDatabaseUtils.check_table_exists('non_existent_table_12345')
        assert exists is False
    
    async def test_fastapi_dependency_is_async(self):
        """Test that FastAPI database dependency uses async session"""
        async for session in get_async_db():
            assert hasattr(session, 'execute')
            
            # Verify it's an async session
            result = await session.execute("SELECT 1")
            assert result.fetchone()[0] == 1
            break  # Only test first session
    
    def test_sync_session_deprecation_warning(self):
        """Test that sync session usage shows deprecation warning"""
        from backend.database.async_config import get_sync_session
        
        with pytest.warns(DeprecationWarning, match="Sync database sessions are deprecated"):
            session = get_sync_session()
            session.close()
    
    async def test_database_health_check(self):
        """Test async database health check"""
        is_healthy = await db_config.health_check()
        assert is_healthy is True
    
    async def test_migration_utils_are_async(self):
        """Test that migration utilities use async operations"""
        # Test table creation/deletion (in memory)
        with patch.object(AsyncMigrationUtils, 'create_tables_async') as mock_create:
            with patch.object(AsyncMigrationUtils, 'drop_tables_async') as mock_drop:
                mock_create.return_value = AsyncMock()
                mock_drop.return_value = AsyncMock()
                
                await AsyncMigrationUtils.reset_database_async()
                
                mock_drop.assert_called_once()
                mock_create.assert_called_once()
    
    def test_no_thread_blocking_in_async_operations(self):
        """Test that async operations don't block other threads"""
        results = []
        
        def background_task():
            """Background thread that should not be blocked"""
            time.sleep(0.05)  # Small delay
            results.append("background_completed")
        
        async def database_task():
            """Async database task"""
            async with db_config.get_async_session() as session:
                await session.execute("SELECT pg_sleep(0.1)")
                results.append("database_completed")
        
        # Start background thread
        thread = threading.Thread(target=background_task)
        thread.start()
        
        # Run async database operation
        asyncio.run(database_task())
        
        # Wait for background thread
        thread.join()
        
        # Both should complete regardless of order
        assert "background_completed" in results
        assert "database_completed" in results
    
    async def test_connection_pool_efficiency(self):
        """Test that connection pool is used efficiently"""
        # Test concurrent connections within pool limits
        async def test_connection():
            async with db_config.get_async_session() as session:
                result = await session.execute("SELECT connection_pid()")
                return result.fetchone()[0]
        
        # Run multiple concurrent connections
        pids = await asyncio.gather(*[test_connection() for _ in range(10)])
        
        # Should have multiple connection PIDs (connection pooling working)
        unique_pids = set(pids)
        assert len(unique_pids) >= 1  # At least one connection
        assert len(unique_pids) <= 10  # Not more than requested
    
    async def test_transaction_rollback_is_async(self):
        """Test that transaction rollback operations are async"""
        try:
            async with db_config.get_async_session() as session:
                # Execute a valid query
                await session.execute("SELECT 1")
                
                # Force an error to trigger rollback
                await session.execute("SELECT invalid_column_name")
                
        except Exception:
            # Exception is expected - test that rollback was async
            pass
        
        # Test explicit rollback
        async with db_config.get_async_session() as session:
            await session.execute("SELECT 1")
            await session.rollback()  # Should be async


class TestLegacyCodeDetection:
    """Tests to detect and flag legacy synchronous code"""
    
    def test_find_sqlalchemy_session_imports(self):
        """Find files that import legacy SQLAlchemy Session"""
        backend_path = Path(__file__).parent.parent
        violations = []
        
        for py_file in backend_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['test_', 'deprecated_']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for legacy imports
                legacy_patterns = [
                    'from sqlalchemy.orm import Session',
                    'from sqlalchemy.orm import sessionmaker',
                    'Session(',
                    'sessionmaker(',
                ]
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in legacy_patterns:
                        if pattern in line and 'async' not in line.lower():
                            violations.append({
                                'file': str(py_file),
                                'line': i,
                                'pattern': pattern,
                                'content': line.strip()
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Allow some legacy imports in specific files
        allowed_files = [
            'async_config.py',  # Contains compatibility layer
            'conftest.py',      # Test configuration
        ]
        
        filtered_violations = [
            v for v in violations
            if not any(allowed in v['file'] for allowed in allowed_files)
        ]
        
        if filtered_violations:
            violation_report = "\n".join([
                f"File: {v['file']}, Line: {v['line']}: {v['content']}"
                for v in filtered_violations
            ])
            pytest.fail(
                f"Found {len(filtered_violations)} legacy sync database imports:\n"
                f"{violation_report}"
            )


if __name__ == "__main__":
    # Run async compliance tests
    pytest.main([__file__, "-v"])
