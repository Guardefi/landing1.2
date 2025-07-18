"""
Enhanced Mempool Monitor with fully asynchronous processing.
This module provides real-time monitoring of the mempool using AsyncWeb3,
enabling high-throughput transaction analysis with minimal latency.
"""

import asyncio
import logging
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from web3 import AsyncWeb3, Web3
from web3.exceptions import TransactionNotFound
from web3.providers import AsyncBaseProvider, WebSocketProvider
from web3.types import HexStr, TxData, TxReceipt

from models.mempool_event import MempoolEvent, MempoolEventSeverity, MempoolEventType
from .session_manager import SessionManager
from .utils import async_retry, ether_to_wei

logger = logging.getLogger(__name__)


@dataclass
class RawMempoolTransaction:
    """Raw mempool transaction with metadata and analysis flags."""

    tx_hash: str
    tx_data: dict[str, Any]
    network_id: int
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    analyzed: bool = False
    confirmed: bool = False
    estimated_profit: float = 0.0
    simulation_results: dict[str, Any] = field(default_factory=dict)

    def update_seen(self) -> None:
        """Update the last seen timestamp."""
        self.last_seen = time.time()

    def mark_analyzed(self) -> None:
        """Mark the transaction as analyzed."""
        self.analyzed = True

    def mark_confirmed(self) -> None:
        """Mark the transaction as confirmed."""
        self.confirmed = True

    def set_estimated_profit(self, profit: float) -> None:
        """Set the estimated profit for this transaction."""
        self.estimated_profit = profit

    def age(self) -> float:
        """Calculate the age of the transaction in seconds."""
        return time.time() - self.first_seen

    def __repr__(self) -> str:
        return f"RawMempoolTx({self.tx_hash[:10]}..., age={self.age():.1f}s)"

    def to_mempool_event(self) -> MempoolEvent:
        """Convert to standardized MempoolEvent."""
        tx_data_dict = dict(self.tx_data)
        to_address = tx_data_dict.get("to")
        from_address = tx_data_dict.get("from")
        gas_price = int(tx_data_dict.get("gasPrice", 0))
        value = int(tx_data_dict.get("value", 0))
        input_data = str(tx_data_dict.get("input", "0x"))

        severity = MempoolEventSeverity.INFO
        if value > ether_to_wei(10.0):
            severity = MempoolEventSeverity.HIGH
        elif value > ether_to_wei(1.0):
            severity = MempoolEventSeverity.MEDIUM

        event_type = MempoolEventType.TRANSACTION
        if not to_address and input_data != "0x":
            event_type = MempoolEventType.CONTRACT_DEPLOYMENT

        return MempoolEvent(
            tx_hash=self.tx_hash,
            from_address=str(from_address) if from_address else "",
            contract_address=str(to_address) if to_address else None,
            gas_price=gas_price,
            value=value,
            timestamp=self.first_seen,
            network_id=self.network_id,
            input_data=input_data,
            severity=severity,
            event_type=event_type,
            raw_tx_data=tx_data_dict,
            first_seen=self.first_seen,
            last_seen=self.last_seen,
        )


class EnhancedMempoolMonitor:
    """
    Enhanced mempool monitor with comprehensive transaction tracking and filtering.
    """

    def __init__(
        self,
        chain_id: int,
        rpc_urls: list[str],
        session_manager: SessionManager | None = None,
        max_stored_txs: int = 10000,
        poll_interval: float = 0.1,
        cleanup_interval: float = 60.0,
        reconnect_delay: float = 5.0,
        request_timeout: float = 10.0,
    ):
        """
        Initialize the enhanced mempool monitor.

        Args:
            chain_id: Blockchain chain ID
            rpc_urls: List of RPC URLs to use
            session_manager: HTTP session manager
            max_stored_txs: Maximum transactions to store in memory
            poll_interval: Polling interval in seconds
            cleanup_interval: Cleanup interval in seconds
            reconnect_delay: Delay before reconnecting in seconds
            request_timeout: Request timeout in seconds
        """
        self.chain_id = chain_id
        self.rpc_urls = rpc_urls
        self.session_manager = session_manager or SessionManager(
            timeout_seconds=request_timeout
        )
        self.max_stored_txs = max_stored_txs
        self.poll_interval = poll_interval
        self.cleanup_interval = cleanup_interval
        self.reconnect_delay = reconnect_delay
        self.request_timeout_for_provider = request_timeout

        self._web3_instances: list[AsyncWeb3] = []
        self._active_web3: AsyncWeb3 | None = None
        self._pending_filter_id: HexStr | None = None
        self._is_running = False
        self._shutting_down = False
        self._main_task: asyncio.Task | None = None

        self._pending_txs: dict[str, RawMempoolTransaction] = {}
        self._confirmed_txs: dict[str, RawMempoolTransaction] = {}
        self._seen_tx_hashes: set[str] = set()

        self._callbacks: list[Callable[[MempoolEvent], None]] = []
        self._async_callbacks: list[Callable[[MempoolEvent], Coroutine]] = []

        self._filter_addresses: set[str] = set()
        self._filter_method_sigs: set[str] = set()
        self._min_value_wei: int = 0

        self._stats = {
            "txs_fetched_from_filter": 0,
            "txs_data_retrieved": 0,
            "txs_processed_for_callbacks": 0,
            "txs_filtered_out": 0,
            "reconnects": 0,
            "rpc_errors": 0,
            "last_filter_poll_success": 0.0,
        }

        self._tx_cache: dict[str, TxData] = {}
        self._receipt_cache: dict[str, TxReceipt] = {}

        self._initialize_web3_instances()
        logger.info(
            f"EnhancedMempoolMonitor initialized for chain {chain_id} with {len(self._web3_instances)} RPC endpoints."
        )

    def _make_request_with_session_manager(self, url: str, session_key: str):
        """Create a request function for HTTP providers."""

        async def request_func(method: str, params: list[Any]) -> Any:
            if not self.session_manager:
                raise RuntimeError("SessionManager not available for HTTP request.") from None
            try:
                session = await self.session_manager.get_session(session_key)
                payload = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": int(time.time() * 1000),
                }
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if "error" in data:
                        raise ValueError(f"RPC error: {data['error']}") from None
                    return data["result"]
            except Exception as e:
                logger.error(f"RPC request error to {url} with method {method}: {e}")
                raise e from e

        return request_func

    def _initialize_web3_instances(self) -> None:
        """Initialize Web3 instances for all provided RPC URLs."""
        self._web3_instances = []
        for url in self.rpc_urls:
            try:
                if url.startswith("ws"):
                    provider = WebSocketProvider(
                        url, request_timeout=self.request_timeout_for_provider
                    )
                else:  # HTTP
                    session_key = f"mempool_monitor_{self.chain_id}_{url[:30].replace('/', '_').replace(':', '_')}"
                    provider = AsyncBaseProvider(
                        request_func=self._make_request_with_session_manager(
                            url, session_key
                        )
                    )
                w3 = AsyncWeb3(provider)
                # Manually set endpoint_uri on provider for logging/reference if not auto-set by Web3.py
                if not hasattr(w3.provider, "endpoint_uri"):
                    w3.provider.endpoint_uri = url
                self._web3_instances.append(w3)
                logger.info(f"Added Web3 instance for {url}")
            except Exception as e:
                logger.error(f"Failed to initialize Web3 for {url}: {e}", exc_info=True)

        if not self._web3_instances:
            raise ConnectionError("No valid Web3 providers could be initialized.")

    async def start(self) -> None:
        """Start the mempool monitor."""
        if self._is_running:
            logger.warning("Monitor already running.")
            return
        self._shutting_down = False
        self._is_running = True
        self._main_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Started monitor for chain {self.chain_id}.")

    async def stop(self) -> None:
        """Stop the mempool monitor."""
        if not self._is_running:
            logger.warning("Monitor not running.")
            return
        logger.info("Stopping monitor...")
        self._shutting_down = True
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                logger.info("Main task cancelled.")
            except Exception as e:
                logger.error(f"Error during main task stop: {e}")

        if self._pending_filter_id and self._active_web3:
            try:
                filter_id_hex = (
                    HexStr(self._pending_filter_id)
                    if not self._pending_filter_id.startswith("0x")
                    else self._pending_filter_id
                )
                await self._active_web3.eth.uninstall_filter(filter_id_hex)
                logger.info(f"Uninstalled filter: {self._pending_filter_id}")
            except Exception as e:
                logger.error(f"Error uninstalling filter: {e}")

        if self.session_manager:
            await self.session_manager.close_all()
        self._is_running = False
        logger.info("Monitor stopped.")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        next_cleanup_time = time.monotonic() + self.cleanup_interval
        while not self._shutting_down:
            try:
                if not self._active_web3 or not await self._active_web3.is_connected():
                    await self._select_working_web3()
                    if not self._active_web3:
                        await asyncio.sleep(self.reconnect_delay)
                        continue

                if not self._pending_filter_id:
                    try:
                        self._pending_filter_id = (
                            await self._active_web3.eth.new_pending_transaction_filter()
                        )
                        logger.info(
                            f"New filter: {self._pending_filter_id} on {getattr(self._active_web3.provider, 'endpoint_uri', 'Unknown')}"
                        )
                    except Exception as e:
                        logger.error(f"Filter creation failed: {e}. Resetting.")
                        self._stats["rpc_errors"] += 1
                        self._active_web3 = None
                        self._pending_filter_id = None
                        await asyncio.sleep(self.reconnect_delay)
                        continue

                pending_tx_hashes_raw = await self._active_web3.eth.get_filter_changes(
                    self._pending_filter_id
                )
                pending_tx_hashes = [tx_hash.hex() for tx_hash in pending_tx_hashes_raw]

                if pending_tx_hashes:
                    self._stats["txs_fetched_from_filter"] += len(pending_tx_hashes)
                    await self._process_pending_transaction_hashes(pending_tx_hashes)

                self._stats["last_filter_poll_success"] = time.monotonic()

                if time.monotonic() >= next_cleanup_time:
                    await self._cleanup_old_data()
                    next_cleanup_time = time.monotonic() + self.cleanup_interval

                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                logger.info("Loop cancelled.")
                break
            except Exception as e:
                logger.error(f"Loop error: {e}", exc_info=True)
                self._stats["rpc_errors"] += 1
                self._active_web3 = None
                self._pending_filter_id = None
                await asyncio.sleep(self.reconnect_delay)

    @async_retry(retries=3, delay=2.0, backoff=2)
    async def _select_working_web3(self) -> None:
        """Select a working Web3 instance from available providers."""
        logger.info("Selecting working Web3 instance...")
        for w3 in self._web3_instances:
            uri = getattr(w3.provider, "endpoint_uri", "Unknown URI")
            try:
                if not await w3.is_connected():
                    logger.warning(
                        f"Provider {uri} not connected. Attempting reconnect (if WS)..."
                    )
                    if isinstance(w3.provider, WebSocketProvider):
                        try:
                            await w3.provider.connect()
                        except Exception as connect_e:
                            logger.warning(f"Reconnect failed for {uri}: {connect_e}")
                            continue
                    if not await w3.is_connected():
                        logger.warning(f"Still not connected to {uri}")
                        continue

                fetched_chain_id = await w3.eth.chain_id
                if fetched_chain_id == self.chain_id:
                    self._active_web3 = w3
                    logger.info(f"Selected Web3: {uri}")
                    self._stats["reconnects"] += 1
                    return
                else:
                    logger.warning(
                        f"Chain ID mismatch for {uri}: exp {self.chain_id}, got {fetched_chain_id}"
                    )
            except Exception as e:
                logger.warning(f"Web3 check failed for {uri}: {e}")

        logger.error("No working Web3 instance found after retries.")
        self._active_web3 = None
        raise ConnectionError("Failed to connect to any RPC provider.")

    async def _process_pending_transaction_hashes(self, tx_hashes: list[str]) -> None:
        """Process a batch of transaction hashes."""
        new_unique_hashes = [h for h in tx_hashes if h not in self._seen_tx_hashes]
        tasks = []
        for tx_hash in new_unique_hashes:
            self._seen_tx_hashes.add(tx_hash)
            tasks.append(self._fetch_and_process_tx_event(tx_hash))
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    logger.error(f"Error in task: {res}", exc_info=res)

    async def _fetch_and_process_tx_event(self, tx_hash: str) -> None:
        """Fetch transaction data and process through callbacks."""
        try:
            tx_data_web3 = await self._get_transaction_data(tx_hash)
            if not tx_data_web3:
                return
            self._stats["txs_data_retrieved"] += 1

            tx_data_dict = dict(tx_data_web3)

            if not self._passes_filters(tx_data_dict):
                self._stats["txs_filtered_out"] += 1
                return

            raw_tx_obj = RawMempoolTransaction(tx_hash, tx_data_dict, self.chain_id)
            self._pending_txs[tx_hash] = raw_tx_obj

            mempool_event = raw_tx_obj.to_mempool_event()

            self._stats["txs_processed_for_callbacks"] += 1

            for callback in self._callbacks:
                try:
                    callback(mempool_event)
                except Exception as e:
                    logger.error(
                        f"Sync callback error for {tx_hash}: {e}", exc_info=True
                    )

            async_tasks = [cb(mempool_event) for cb in self._async_callbacks]
            await asyncio.gather(*async_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error processing {tx_hash}: {e}", exc_info=True)

    @async_retry(retries=2, delay=0.5)
    async def _get_transaction_data(self, tx_hash: str) -> TxData | None:
        """Get transaction data with caching."""
        if tx_hash in self._tx_cache:
            return self._tx_cache[tx_hash]
        if not self._active_web3:
            logger.warning("No active Web3.")
            return None
        try:
            tx_data = await self._active_web3.eth.get_transaction(tx_hash)
            if tx_data:
                self._tx_cache[tx_hash] = tx_data
            # Simple cache eviction
            if len(self._tx_cache) > self.max_stored_txs * 2:
                self._tx_cache.pop(next(iter(self._tx_cache)))
            return tx_data
        except TransactionNotFound:
            logger.debug(f"Tx {tx_hash} not found by provider.")
            return None
        except TimeoutError:
            logger.warning(f"Timeout fetching {tx_hash}")
            self._stats["rpc_errors"] += 1
            return None
        except Exception as e:
            logger.warning(f"Error fetching {tx_hash}: {e}")
            self._stats["rpc_errors"] += 1
            return None

    async def _get_transaction_receipt(self, tx_hash: str) -> TxReceipt | None:
        """Get transaction receipt with caching."""
        if tx_hash in self._receipt_cache:
            return self._receipt_cache[tx_hash]
        if not self._active_web3:
            return None
        try:
            receipt = await self._active_web3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                self._receipt_cache[tx_hash] = receipt
            if len(self._receipt_cache) > self.max_stored_txs:
                self._receipt_cache.pop(next(iter(self._receipt_cache)))
            return receipt
        except Exception as e:
            logger.debug(f"Error fetching receipt {tx_hash}: {e}")
            return None

    def _passes_filters(self, tx_data_dict: dict[str, Any]) -> bool:
        """Check if transaction passes all configured filters."""
        if (
            self._min_value_wei > 0
            and int(tx_data_dict.get("value", 0)) < self._min_value_wei
        ):
            return False
        to_lower = (
            str(tx_data_dict.get("to", "")).lower() if tx_data_dict.get("to") else ""
        )
        from_lower = (
            str(tx_data_dict.get("from", "")).lower()
            if tx_data_dict.get("from")
            else ""
        )
        if self._filter_addresses and not (
            to_lower in self._filter_addresses or from_lower in self._filter_addresses
        ):
            return False
        if self._filter_method_sigs:
            input_data = str(tx_data_dict.get("input", "0x"))
            if len(input_data) >= 10:
                if input_data[:10].lower() not in self._filter_method_sigs:
                    return False
            else:
                return False
        return True

    async def _cleanup_old_data(self) -> None:
        """Clean up old transaction data to prevent memory leaks."""
        logger.debug(
            f"Running cleanup. Pending TXs: {len(self._pending_txs)}, Seen Hashes: {len(self._seen_tx_hashes)}"
        )
        current_mono_time = time.monotonic()
        max_age = self.cleanup_interval * 5

        # Pending TXs
        txs_to_remove_pending = [
            h
            for h, tx in self._pending_txs.items()
            if (current_mono_time - tx.first_seen) > max_age
        ]
        for h in txs_to_remove_pending:
            del self._pending_txs[h]
            logger.debug(f"Aged out pending: {h[:10]}")

        # Confirmed TXs
        if len(self._confirmed_txs) > self.max_stored_txs:
            num_to_del = len(self._confirmed_txs) - self.max_stored_txs
            sorted_conf = sorted(
                self._confirmed_txs.items(), key=lambda item: item[1].last_seen
            )
            for i in range(num_to_del):
                del self._confirmed_txs[sorted_conf[i][0]]
            logger.debug(f"Pruned {num_to_del} oldest confirmed TXs.")

        # Seen Hashes
        if len(self._seen_tx_hashes) > self.max_stored_txs * 10:
            logger.info(f"Pruning _seen_tx_hashes from {len(self._seen_tx_hashes)}.")
            current_known_hashes = set(self._pending_txs.keys()) | set(
                self._confirmed_txs.keys()
            )
            if len(current_known_hashes) < len(self._seen_tx_hashes) * 0.8:
                self._seen_tx_hashes = current_known_hashes
                logger.info(
                    f"_seen_tx_hashes reset to current known TXs: {len(self._seen_tx_hashes)}."
                )

        logger.debug(
            f"Cleanup done. Pending: {len(self._pending_txs)}, Confirmed: {len(self._confirmed_txs)}, Seen: {len(self._seen_tx_hashes)}"
        )

    # Public interface methods
    def add_callback(self, callback: Callable[[MempoolEvent], None]) -> None:
        """Add a synchronous callback for mempool events."""
        self._callbacks.append(callback)

    def add_async_callback(self, callback: Callable[[MempoolEvent], Coroutine]) -> None:
        """Add an asynchronous callback for mempool events."""
        self._async_callbacks.append(callback)

    def set_filter_addresses(self, addresses: list[str]) -> None:
        """Set address filter for transactions."""
        self._filter_addresses = {a.lower() for a in addresses if Web3.is_address(a)}
        logger.info(f"Filters: Addresses set ({len(self._filter_addresses)}).")

    def set_filter_method_signatures(self, method_sigs: list[str]) -> None:
        """Set method signature filter for transactions."""
        self._filter_method_sigs = {
            s.lower() for s in method_sigs if s.startswith("0x") and len(s) == 10
        }
        logger.info(f"Filters: Method sigs set ({len(self._filter_method_sigs)}).")

    def set_min_value(self, min_value_eth: float) -> None:
        """Set minimum value filter for transactions."""
        self._min_value_wei = ether_to_wei(min_value_eth)
        logger.info(f"Filters: Min value set ({min_value_eth} ETH).")

    def get_stats(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        s = self._stats.copy()
        s.update(
            {
                "pending_txs_count": len(self._pending_txs),
                "confirmed_txs_count": len(self._confirmed_txs),
                "seen_tx_hashes_count": len(self._seen_tx_hashes),
                "tx_cache_size": len(self._tx_cache),
                "receipt_cache_size": len(self._receipt_cache),
                "active_provider": (
                    getattr(self._active_web3.provider, "endpoint_uri", "None")
                    if self._active_web3
                    else "None"
                ),
                "is_running": self._is_running,
            }
        )
        return s
