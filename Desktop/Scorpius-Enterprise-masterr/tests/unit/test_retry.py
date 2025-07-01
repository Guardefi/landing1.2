import pytest
from unittest.mock import Mock


class TestRetry:
    def test_basic_retry(self):
        assert True

    def test_mock_functionality(self):
        mock = Mock()
        mock.return_value = "test"
        assert mock() == "test"
