import pytest
from unittest.mock import Mock


class TestApi:
    def test_basic_api(self):
        assert True

    def test_api_mock(self):
        mock = Mock()
        mock.return_value = {"status": "ok"}
        assert mock() == {"status": "ok"}
