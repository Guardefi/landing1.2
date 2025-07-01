# Test configuration for usage_metering tests
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_config():
    config = Mock()
    config.get = Mock(return_value="test_value")
    return config