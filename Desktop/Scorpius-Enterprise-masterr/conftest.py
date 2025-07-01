# conftest.py - Global pytest configuration
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Add all necessary paths to sys.path for imports to work
paths_to_add = [
    str(PROJECT_ROOT),  # Root directory
    str(PROJECT_ROOT / "backend"),  # Backend modules
    str(PROJECT_ROOT / "packages"),  # Packages directory
    str(PROJECT_ROOT / "packages" / "core"),  # Core package
    str(PROJECT_ROOT / "services"),  # Services
    str(PROJECT_ROOT / "monitoring"),  # Monitoring
    str(PROJECT_ROOT / "reporting"),  # Reporting
    str(PROJECT_ROOT / "tests"),  # Tests directory
    str(PROJECT_ROOT / "frontend"),  # Frontend (if needed)
    str(PROJECT_ROOT / "tests"),  # Tests directory
    str(PROJECT_ROOT / "tests" / "unit"),  # Unit tests
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set environment variables for testing
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("PYTEST_CURRENT_TEST", "true")

# Create __init__.py files in test directories if they don't exist
test_directories = [
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "tests" / "unit",
    PROJECT_ROOT / "tests" / "unit" / "bytecode",
    PROJECT_ROOT / "tests" / "api",
    PROJECT_ROOT / "packages" / "core" / "tests",
]

for test_dir in test_directories:
    if test_dir.exists():
        init_file = test_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Test package\n")


# Mock commonly problematic imports
class MockModule:
    def __getattr__(self, name):
        return Mock()


# Mock web3 and other blockchain dependencies
sys.modules.setdefault("web3", MockModule())
sys.modules.setdefault("eth_account", MockModule())
sys.modules.setdefault("eth_keys", MockModule())
sys.modules.setdefault("eth_utils", MockModule())

# Mock fastapi test client issues
try:
    from fastapi.testclient import TestClient
    from starlette.testclient import TestClient as StarletteTestClient
except ImportError:
    pass


# Global fixtures for common mocks
@pytest.fixture
def mock_logger():
    """Provide a mock logger for tests"""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.exception = Mock()
    return logger


@pytest.fixture
def mock_config():
    """Provide a mock configuration for tests"""
    config = Mock()
    config.get = Mock(return_value="test_value")
    config.database_url = "sqlite:///:memory:"
    config.redis_url = "redis://localhost:6379/0"
    config.log_level = "DEBUG"
    return config


@pytest.fixture
def mock_similarity_engine():
    """Mock similarity engine for bytecode tests"""

    class MockResult:
        similarity_score = 0.85
        confidence = 0.9
        processing_time = 0.01

    engine = AsyncMock()
    engine.compare_bytecodes.return_value = MockResult()
    engine.cleanup = AsyncMock()
    return engine


@pytest.fixture
def mock_bytecode_normalizer():
    """Mock bytecode normalizer for tests"""
    normalizer = AsyncMock()
    normalizer.normalize = AsyncMock(
        side_effect=lambda x: x.replace("0x", "").lower() if x else ""
    )
    return normalizer


@pytest.fixture
def mock_test_client():
    """Mock test client for API tests"""

    class MockResponse:
        status_code = 200

        def json(self):
            return {"status": "ok"}

    client = Mock()
    client.get = Mock(return_value=MockResponse())
    client.post = Mock(return_value=MockResponse())
    client.put = Mock(return_value=MockResponse())
    client.delete = Mock(return_value=MockResponse())
    return client


# Common mock classes that tests can import
class MockModule:
    """Generic mock module that responds to any attribute access"""

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


# Make common mocks available globally
globals().update(
    {
        "MockModule": MockModule,
        "Mock": Mock,
        "AsyncMock": AsyncMock,
        "patch": patch,
    }
)
