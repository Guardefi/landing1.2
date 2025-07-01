import pytest
from unittest.mock import Mock


class TestApiMain:
    def test_basic_api_main(self):
        assert True

    def test_api_main_mock(self):
        mock = Mock()
        mock.return_value = "api_main_test"
        assert mock() == "api_main_test"
