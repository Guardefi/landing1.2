"""
Anvil VM Adapter Plugin for Time Machine
Provides interface for Anvil (Foundry) local development chain
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from ..core.execution_vm import BaseVMAdapter
from ..core.models import EventType, TimelineEvent


class AnvilAdapter(BaseVMAdapter):
    """Anvil VM adapter for local Foundry chain manipulation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.anvil_process: Optional[subprocess.Popen] = None
        self.rpc_url = config.get("rpc_url", "http://localhost:8545")
        self.chain_id = config.get("chain_id", 31337)
        self.fork_url = config.get("fork_url")
        self.block_time = config.get("block_time", 0)  # Auto-mining by default
        self.accounts = config.get("accounts", 10)
        self.balance = config.get("balance", 10000)
        self.gas_limit = config.get("gas_limit", 30000000)
        self.gas_price = config.get("gas_price", 20000000000)

    async def initialize(self) -> None:
        """Start Anvil process and wait for initialization"""
        if self.anvil_process and self.anvil_process.poll() is None:
            return  # Already running

        cmd = ["anvil"]

        # Add configuration options
        cmd.extend(["--host", "0.0.0.0"])
        cmd.extend(["--port", str(self._extract_port(self.rpc_url))])
        cmd.extend(["--chain-id", str(self.chain_id)])
        cmd.extend(["--accounts", str(self.accounts)])
        cmd.extend(["--balance", str(self.balance)])
        cmd.extend(["--gas-limit", str(self.gas_limit)])
        cmd.extend(["--gas-price", str(self.gas_price)])

        if self.fork_url:
            cmd.extend(["--fork-url", self.fork_url])

        if self.block_time > 0:
            cmd.extend(["--block-time", str(self.block_time)])
        else:
            cmd.append("--no-mining")  # Manual mining mode

        # Start the process
        self.anvil_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Wait for Anvil to be ready
        await self._wait_for_ready()

    async def cleanup(self) -> None:
        """Stop Anvil process"""
        if self.anvil_process:
            self.anvil_process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process_end()), timeout=5.0
                )
            except asyncio.TimeoutError:
                self.anvil_process.kill()
            self.anvil_process = None

    async def load_block_range(self, start_block: int, end_block: int) -> List[Dict]:
        """Load blocks from Anvil"""
        blocks = []

        for block_num in range(start_block, end_block + 1):
            block_data = await self._rpc_call(
                "eth_getBlockByNumber", [hex(block_num), True]
            )
            if block_data:
                blocks.append(block_data)

        return blocks

    async def load_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Load transaction details from Anvil"""
        return await self._rpc_call("eth_getTransactionByHash", [tx_hash])

    async def get_state_at_block(self, block_number: int) -> Dict:
        """Get state at specific block"""
        # Use Anvil's snapshot functionality
        snapshot_id = await self._rpc_call("evm_snapshot", [])

        # Revert to the target block
        await self._rpc_call("anvil_mine", [block_number])

        # Get current state
        state = await self._get_full_state()

        # Restore snapshot
        await self._rpc_call("evm_revert", [snapshot_id])

        return state

    async def apply_state_patch(self, patch_data: Dict) -> bool:
        """Apply state patch using Anvil's state manipulation"""
        try:
            operations = patch_data.get("operations", [])

            for op in operations:
                if op["op_type"] == "set":
                    await self._apply_state_override(op)
                elif op["op_type"] == "balance":
                    await self._set_balance(op)
                elif op["op_type"] == "storage":
                    await self._set_storage(op)
                elif op["op_type"] == "code":
                    await self._set_code(op)

            return True
        except Exception as e:
            self.logger.error(f"Failed to apply patch: {e}")
            return False

    async def create_snapshot(self) -> str:
        """Create Anvil snapshot"""
        snapshot_id = await self._rpc_call("evm_snapshot", [])
        return str(snapshot_id)

    async def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore Anvil snapshot"""
        try:
            result = await self._rpc_call("evm_revert", [int(snapshot_id)])
            return bool(result)
        except Exception:
            return False

    async def execute_transaction(self, tx_data: Dict) -> Dict:
        """Execute transaction on Anvil"""
        # Send transaction
        tx_hash = await self._rpc_call("eth_sendTransaction", [tx_data])

        # Mine a block to include the transaction
        await self._rpc_call("evm_mine", [])

        # Get transaction receipt
        receipt = await self._rpc_call("eth_getTransactionReceipt", [tx_hash])

        return {
            "hash": tx_hash,
            "receipt": receipt,
            "block_number": int(receipt["blockNumber"], 16) if receipt else None,
        }

    async def trace_transaction(self, tx_hash: str) -> Dict:
        """Trace transaction execution"""
        return await self._rpc_call(
            "debug_traceTransaction",
            [tx_hash, {"tracer": "callTracer", "tracerConfig": {"withLog": True}}],
        )

    async def stream_events(
        self, start_block: int, end_block: Optional[int] = None
    ) -> AsyncIterator[TimelineEvent]:
        """Stream events from Anvil"""
        current_block = start_block

        while end_block is None or current_block <= end_block:
            # Get latest block
            latest = await self._rpc_call("eth_blockNumber", [])
            latest_num = int(latest, 16)

            if current_block <= latest_num:
                # Process blocks
                for block_num in range(
                    current_block, min(latest_num + 1, (end_block or latest_num) + 1)
                ):
                    block_data = await self._rpc_call(
                        "eth_getBlockByNumber", [hex(block_num), True]
                    )

                    if block_data:
                        # Emit block event
                        yield TimelineEvent(
                            event_type=EventType.BLOCK_PROCESSED,
                            description=f"Block {block_num} processed",
                            metadata={
                                "block_number": block_num,
                                "tx_count": len(block_data.get("transactions", [])),
                                "gas_used": int(block_data.get("gasUsed", "0x0"), 16),
                                "timestamp": int(
                                    block_data.get("timestamp", "0x0"), 16
                                ),
                            },
                        )

                        # Emit transaction events
                        for tx in block_data.get("transactions", []):
                            yield TimelineEvent(
                                event_type=EventType.TRANSACTION_EXECUTED,
                                description=f"Transaction {tx['hash']} executed",
                                metadata={
                                    "tx_hash": tx["hash"],
                                    "block_number": block_num,
                                    "from": tx.get("from"),
                                    "to": tx.get("to"),
                                    "value": tx.get("value", "0x0"),
                                    "gas": int(tx.get("gas", "0x0"), 16),
                                    "gas_price": int(tx.get("gasPrice", "0x0"), 16),
                                },
                            )

                current_block = latest_num + 1

            if end_block is not None and current_block > end_block:
                break

            # Wait before checking for new blocks
            await asyncio.sleep(1.0)

    async def get_gas_estimates(self, transactions: List[Dict]) -> List[Dict]:
        """Get gas estimates for transactions"""
        estimates = []

        for tx in transactions:
            try:
                gas_estimate = await self._rpc_call("eth_estimateGas", [tx])
                estimates.append(
                    {
                        "tx": tx,
                        "gas_estimate": int(gas_estimate, 16),
                        "gas_price": int(tx.get("gasPrice", "0x0"), 16)
                        or await self._get_gas_price(),
                    }
                )
            except Exception as e:
                estimates.append({"tx": tx, "error": str(e)})

        return estimates

    # Private helper methods
    async def _wait_for_ready(self) -> None:
        """Wait for Anvil to be ready to accept connections"""
        for _ in range(30):  # 30 second timeout
            try:
                result = await self._rpc_call("eth_blockNumber", [])
                if result:
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)
        raise RuntimeError("Anvil failed to start within timeout")

    async def _wait_for_process_end(self) -> None:
        """Wait for Anvil process to end"""
        if self.anvil_process:
            self.anvil_process.wait()

    def _extract_port(self, url: str) -> int:
        """Extract port from RPC URL"""
        if ":" in url:
            return int(url.split(":")[-1])
        return 8545

    async def _rpc_call(self, method: str, params: List) -> Any:
        """Make RPC call to Anvil"""
        import aiohttp

        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.rpc_url, json=payload) as response:
                data = await response.json()
                if "error" in data:
                    raise Exception(f"RPC error: {data['error']}")
                return data.get("result")

    async def _get_full_state(self) -> Dict:
        """Get full blockchain state"""
        # This is a simplified version - in practice you'd need to
        # enumerate all accounts and their storage
        block_number = await self._rpc_call("eth_blockNumber", [])

        return {
            "block_number": int(block_number, 16),
            "accounts": {},  # Would need to be populated
            "storage": {},  # Would need to be populated
            "timestamp": None,  # Would need to be populated
        }

    async def _apply_state_override(self, op: Dict) -> None:
        """Apply state override operation"""
        # Anvil doesn't have direct state override, so we'd use
        # available methods like anvil_setBalance, anvil_setCode, etc.
        pass

    async def _set_balance(self, op: Dict) -> None:
        """Set account balance"""
        await self._rpc_call(
            "anvil_setBalance", [op["target_address"], hex(int(op["value"]))]
        )

    async def _set_storage(self, op: Dict) -> None:
        """Set storage slot"""
        await self._rpc_call(
            "anvil_setStorageAt", [op["target_address"], op["storage_key"], op["value"]]
        )

    async def _set_code(self, op: Dict) -> None:
        """Set account code"""
        await self._rpc_call("anvil_setCode", [op["target_address"], op["code"]])

    async def _get_gas_price(self) -> int:
        """Get current gas price"""
        gas_price = await self._rpc_call("eth_gasPrice", [])
        return int(gas_price, 16)
