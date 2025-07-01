import pytest
from unittest.mock import Mock


class TestRpcDecorator:
    def test_basic_decorator(self):
        assert True

    def test_mock_decorator(self):
        mock = Mock()
        mock.return_value = "test"
        assert mock() == "test"
