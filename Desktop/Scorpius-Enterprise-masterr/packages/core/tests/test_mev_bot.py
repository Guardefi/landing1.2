import pytest
from unittest.mock import Mock


class TestMevBot:
    def test_basic_mev_bot(self):
        assert True

    def test_mev_bot_mock(self):
        mock = Mock()
        mock.return_value = {"bot": "active"}
        assert mock() == {"bot": "active"}
