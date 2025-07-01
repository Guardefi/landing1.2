import pytest
from unittest.mock import Mock, AsyncMock


class TestSimple:
    def test_basic_functionality(self):
        assert True

    def test_with_mock(self):
        mock_obj = Mock()
        mock_obj.return_value = "test_value"
        result = mock_obj()
        assert result == "test_value"
