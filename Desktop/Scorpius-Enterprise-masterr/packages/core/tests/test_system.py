import pytest
from unittest.mock import Mock


class TestSystem:
    def test_basic_system(self):
        assert True

    def test_system_mock(self):
        mock = Mock()
        mock.return_value = "system_test"
        assert mock() == "system_test"
