"""Unit tests for the Enhanced Mempool Monitor."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from core.enhanced_mempool_monitor import EnhancedMempoolMonitor, RawMempoolTransaction
from core.session_manager import SessionManager
from models.mempool_event import MempoolEvent, MempoolEventSeverity, MempoolEventType


class TestRawMempoolTransaction:
    """Test RawMempoolTransaction class."""

    def test_creation(self):
        """Test creating a RawMempoolTransaction."""
        tx = RawMempoolTransaction(
            tx_hash="0x123",
            tx_data={"from": "0xabc", "to": "0xdef", "value": 1000},
            network_id=1,
        )
        assert tx.tx_hash == "0x123"
        assert tx.network_id == 1
        assert not tx.analyzed
        assert not tx.confirmed

    def test_update_seen(self):
        """Test updating last seen timestamp."""
        tx = RawMempoolTransaction(tx_hash="0x123", tx_data={}, network_id=1)
        original_time = tx.last_seen
        time.sleep(0.01)
        tx.update_seen()
        assert tx.last_seen > original_time

    def test_mark_analyzed(self):
        """Test marking transaction as analyzed."""
        tx = RawMempoolTransaction(tx_hash="0x123", tx_data={}, network_id=1)
        assert not tx.analyzed
        tx.mark_analyzed()
        assert tx.analyzed

    def test_age_calculation(self):
        """Test age calculation."""
        tx = RawMempoolTransaction(tx_hash="0x123", tx_data={}, network_id=1)
        time.sleep(0.01)
        age = tx.age()
        assert age > 0

    def test_to_mempool_event(self):
        """Test conversion to MempoolEvent."""
        tx_data = {
            "from": "0xfrom_address",
            "to": "0xto_address",
            "value": "1000000000000000000",  # 1 ETH
            "gasPrice": "20000000000",
            "input": "0x",
        }
        tx = RawMempoolTransaction(tx_hash="0x123", tx_data=tx_data, network_id=1)

        event = tx.to_mempool_event()
        assert isinstance(event, MempoolEvent)
        assert event.tx_hash == "0x123"
        assert event.from_address == "0xfrom_address"
        assert event.contract_address == "0xto_address"
        assert event.value == 1000000000000000000
        assert event.event_type == MempoolEventType.TRANSACTION


@pytest.mark.asyncio
class TestEnhancedMempoolMonitor:
    """Test EnhancedMempoolMonitor class."""

    async def test_initialization(self, session_manager):
        """Test monitor initialization."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )
        assert monitor.chain_id == 1
        assert monitor.rpc_urls == ["http://localhost:8545"]
        assert monitor.session_manager == session_manager
        assert not monitor.is_running

    async def test_start_stop(self, session_manager):
        """Test starting and stopping the monitor."""
        with patch.object(EnhancedMempoolMonitor, "_monitor_loop"):
            monitor = EnhancedMempoolMonitor(
                chain_id=1,
                rpc_urls=["http://localhost:8545"],
                session_manager=session_manager,
            )

            await monitor.start()
            assert monitor.is_running

            await monitor.stop()
            assert not monitor.is_running

    async def test_add_transaction(self, session_manager):
        """Test adding a transaction."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
            max_stored_txs=5,
        )

        tx_data = {"hash": "0x123", "from": "0xabc", "to": "0xdef", "value": "1000"}

        monitor.add_transaction("0x123", tx_data)
        assert len(monitor.transactions) == 1
        assert "0x123" in monitor.transactions

    async def test_max_transactions_limit(self, session_manager):
        """Test that monitor respects max transactions limit."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
            max_stored_txs=2,
        )

        # Add transactions beyond limit
        for i in range(5):
            tx_data = {"hash": f"0x{i}", "from": "0xabc", "value": "1000"}
            monitor.add_transaction(f"0x{i}", tx_data)

        # Should only keep the most recent transactions
        assert len(monitor.transactions) <= 2

    async def test_get_transaction(self, session_manager):
        """Test getting a transaction."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )

        tx_data = {"hash": "0x123", "from": "0xabc", "value": "1000"}
        monitor.add_transaction("0x123", tx_data)

        tx = monitor.get_transaction("0x123")
        assert tx is not None
        assert tx.tx_hash == "0x123"

    async def test_get_transactions_by_filter(self, session_manager):
        """Test filtering transactions."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )

        # Add various transactions
        high_value_tx = {
            "hash": "0x1",
            "from": "0xabc",
            "value": "2000000000000000000",
        }  # 2 ETH
        low_value_tx = {
            "hash": "0x2",
            "from": "0xdef",
            "value": "100000000000000000",
        }  # 0.1 ETH

        monitor.add_transaction("0x1", high_value_tx)
        monitor.add_transaction("0x2", low_value_tx)

        # Filter by minimum value
        high_value_txs = monitor.get_transactions_by_filter(
            min_value_wei=1000000000000000000  # 1 ETH
        )
        assert len(high_value_txs) == 1
        assert high_value_txs[0].tx_hash == "0x1"

    async def test_cleanup_old_transactions(self, session_manager):
        """Test cleanup of old transactions."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )

        # Add old transaction
        old_tx = RawMempoolTransaction(
            tx_hash="0x1", tx_data={"value": "1000"}, network_id=1
        )
        old_tx.first_seen = time.time() - 1000  # Very old
        monitor.transactions["0x1"] = old_tx

        # Add recent transaction
        recent_tx_data = {"hash": "0x2", "value": "1000"}
        monitor.add_transaction("0x2", recent_tx_data)

        monitor._cleanup_old_transactions(max_age_seconds=100)

        # Old transaction should be removed
        assert "0x1" not in monitor.transactions
        assert "0x2" in monitor.transactions

    async def test_statistics(self, session_manager):
        """Test getting statistics."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )

        # Add some transactions
        for i in range(3):
            tx_data = {"hash": f"0x{i}", "value": "1000"}
            monitor.add_transaction(f"0x{i}", tx_data)

        stats = monitor.get_statistics()
        assert stats["total_transactions"] == 3
        assert stats["chain_id"] == 1
        assert "uptime_seconds" in stats

    @patch("core.enhanced_mempool_monitor.AsyncWeb3")
    async def test_web3_initialization(self, mock_web3, session_manager):
        """Test Web3 instance initialization."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545", "wss://localhost:8546"],
            session_manager=session_manager,
        )

        monitor._initialize_web3_instances()
        assert len(monitor._web3_instances) == 2

    async def test_event_callback(self, session_manager):
        """Test event callback functionality."""
        monitor = EnhancedMempoolMonitor(
            chain_id=1,
            rpc_urls=["http://localhost:8545"],
            session_manager=session_manager,
        )

        events_received = []

        def callback(event):
            events_received.append(event)

        monitor.add_event_callback(callback)

        # Add a transaction to trigger event
        tx_data = {"hash": "0x123", "from": "0xabc", "value": "1000"}
        monitor.add_transaction("0x123", tx_data)

        # Event should be triggered
        assert len(events_received) > 0
        assert isinstance(events_received[0], MempoolEvent)
