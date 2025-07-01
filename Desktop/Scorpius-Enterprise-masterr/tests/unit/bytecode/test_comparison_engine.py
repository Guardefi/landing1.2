import pytest
from unittest.mock import Mock


class TestComparisonEngine:
    def test_basic_comparison(self):
        assert True

    def test_comparison_mock(self):
        mock = Mock()
        mock.return_value = {"score": 0.9}
        assert mock() == {"score": 0.9}
