"""
VM Adapter Interface and Implementations
Provides pluggable backends for Anvil, Hardhat, Geth execution environments.
"""

import asyncio
import json
import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp

from .models import FrameType, Patch, PatchType, TimelineEvent, VMBackend

logger = logging.getLogger(__name__)


class BaseVMAdapter(ABC):
    """Abstract base class for VM adapters."""

    @abstractmethod
    async def start(self) -> None:
        """Start the VM process/connection."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the VM process/connection."""
        pass

    @abstractmethod
    async def load_block(self, block_number: int) -> None:
        """Load blockchain state at specific block."""
        pass

    @abstractmethod
    async def execute_tx(self, tx_hash: str) -> None:
        """Execute a specific transaction."""
        pass

    @abstractmethod
    async def execute_block(self) -> None:
        """Execute all transactions in current block."""
        pass

    @abstractmethod
    async def apply_patch(self, patch: Patch) -> None:
        """Apply a state patch."""
        pass

    @abstractmethod
    async def get_state(self) -> Dict[str, Any]:
        """Get current VM state."""
        pass

    @abstractmethod
    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load VM state."""
        pass

    @abstractmethod
    async def get_timeline_events(self) -> AsyncIterator[TimelineEvent]:
        """Stream timeline events."""
        pass

    @abstractmethod
    async def trace_transaction(self, tx_hash: str) -> List[Dict[str, Any]]:
        """Get detailed transaction trace."""
        pass


class AnvilAdapter(BaseVMAdapter):
    """Anvil VM adapter implementation using JSON-RPC."""

    def __init__(
        self,
        rpc_url: str = "http://localhost:8545",
        fork_url: Optional[str] = None,
        block_number: Optional[int] = None,
    ):
        self.rpc_url = rpc_url
        self.fork_url = fork_url
        self.fork_block = block_number
        self.process = None
        self.current_block = 0
        self.session = None
        self.trace_enabled = True

    async def start(self) -> None:
        """Start Anvil process."""
        cmd = ["anvil", "--host", "0.0.0.0", "--port", "8545"]

        if self.fork_url:
            cmd.extend(["--fork-url", self.fork_url])

        if self.fork_block:
            cmd.extend(["--fork-block-number", str(self.fork_block)])

        if self.trace_enabled:
            cmd.append("--tracing")

        logger.info(f"Starting Anvil with command: {' '.join(cmd)}")

        self.process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for startup
        await asyncio.sleep(3)

        # Create HTTP session
        self.session = aiohttp.ClientSession()

        # Test connection
        try:
            await self._rpc_call("eth_blockNumber")
            logger.info("Anvil started successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Anvil: {e}")
            raise

    async def stop(self) -> None:
        """Stop Anvil process."""
        if self.session:
            await self.session.close()

        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            logger.info("Anvil stopped")

    async def _rpc_call(self, method: str, params: List[Any] = None) -> Any:
        """Make JSON-RPC call to Anvil."""
        if not self.session:
            raise RuntimeError("Anvil not started")

        payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}

        async with self.session.post(self.rpc_url, json=payload) as response:
            result = await response.json()

            if "error" in result:
                raise RuntimeError(f"RPC error: {result['error']}")

            return result.get("result")

    async def load_block(self, block_number: int) -> None:
        """Load blockchain state at specific block."""
        self.current_block = block_number

        # Reset Anvil to specific block
        await self._rpc_call(
            "anvil_reset",
            [{"forking": {"jsonRpcUrl": self.fork_url, "blockNumber": block_number}}],
        )

        logger.info(f"Loaded block {block_number}")

    async def execute_tx(self, tx_hash: str) -> None:
        """Execute a specific transaction."""
        # Get transaction details
        tx = await self._rpc_call("eth_getTransactionByHash", [tx_hash])
        if not tx:
            raise ValueError(f"Transaction {tx_hash} not found")

        # Send transaction
        result = await self._rpc_call("eth_sendTransaction", [tx])
        logger.info(f"Executed transaction {tx_hash}, result: {result}")

    async def execute_block(self) -> None:
        """Execute all transactions in current block."""
        # Mine a new block
        await self._rpc_call("evm_mine")
        self.current_block += 1
        logger.info(f"Executed block, now at {self.current_block}")

    async def apply_patch(self, patch: Patch) -> None:
        """Apply a state patch."""
        if patch.patch_type == PatchType.STORAGE:
            await self._rpc_call(
                "anvil_setStorageAt", [patch.target_address, patch.key, patch.value]
            )
            logger.info(
                f"Applied storage patch: {patch.target_address}[{patch.key}] = {patch.value}"
            )

        elif patch.patch_type == PatchType.BALANCE:
            await self._rpc_call(
                "anvil_setBalance", [patch.target_address, patch.value]
            )
            logger.info(
                f"Applied balance patch: {patch.target_address} = {patch.value}"
            )

        elif patch.patch_type == PatchType.CODE:
            await self._rpc_call("anvil_setCode", [patch.target_address, patch.value])
            logger.info(f"Applied code patch: {patch.target_address}")

        elif patch.patch_type == PatchType.NONCE:
            await self._rpc_call("anvil_setNonce", [patch.target_address, patch.value])
            logger.info(f"Applied nonce patch: {patch.target_address} = {patch.value}")

    async def get_state(self) -> Dict[str, Any]:
        """Get current VM state."""
        block_number = await self._rpc_call("eth_blockNumber")

        return {
            "block_number": int(block_number, 16),
            "timestamp": await self._rpc_call("eth_blockTimestamp") or 0,
            "accounts": {},  # Would need to enumerate known accounts
            "storage": {},  # Would need to enumerate storage slots
            "vm_type": "anvil",
        }

    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load VM state."""
        if "block_number" in state:
            await self.load_block(state["block_number"])

        # Apply account states, storage, etc.
        # This would be more complex in a real implementation
        logger.info(f"Loaded state for block {state.get('block_number', 'unknown')}")

    async def get_timeline_events(self) -> AsyncIterator[TimelineEvent]:
        """Stream timeline events."""
        # Mock implementation - in reality would parse traces
        block_number = await self._rpc_call("eth_blockNumber")
        current_block = int(block_number, 16)

        for i in range(5):  # Mock 5 events
            yield TimelineEvent(
                frame_id=f"anvil_frame_{i}",
                frame_type=FrameType.OPCODE,
                block_number=current_block,
                tx_index=0,
                opcode="SSTORE" if i % 2 == 0 else "SLOAD",
                gas_used=2100 + i * 100,
                address="0x" + "0" * 40,
                metadata={"vm": "anvil", "mock": True},
            )
            await asyncio.sleep(0.1)

    async def trace_transaction(self, tx_hash: str) -> List[Dict[str, Any]]:
        """Get detailed transaction trace."""
        trace = await self._rpc_call(
            "debug_traceTransaction",
            [tx_hash, {"tracer": "callTracer", "tracerConfig": {"withLog": True}}],
        )
        return [trace] if trace else []


class HardhatAdapter(BaseVMAdapter):
    """Hardhat VM adapter implementation."""

    def __init__(
        self, rpc_url: str = "http://localhost:8545", network: str = "hardhat"
    ):
        self.rpc_url = rpc_url
        self.network = network
        self.process = None
        self.session = None
        self.current_block = 0

    async def start(self) -> None:
        """Start Hardhat node."""
        cmd = ["npx", "hardhat", "node", "--port", "8545"]

        logger.info(f"Starting Hardhat with command: {' '.join(cmd)}")

        self.process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await asyncio.sleep(5)  # Hardhat takes longer to start
        self.session = aiohttp.ClientSession()

        logger.info("Hardhat started successfully")

    async def stop(self) -> None:
        """Stop Hardhat node."""
        if self.session:
            await self.session.close()

        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            logger.info("Hardhat stopped")

    async def load_block(self, block_number: int) -> None:
        """Load blockchain state at specific block."""
        # Hardhat implementation would be different
        self.current_block = block_number
        logger.info(f"Loaded block {block_number} (Hardhat)")

    async def execute_tx(self, tx_hash: str) -> None:
        """Execute a specific transaction."""
        logger.info(f"Executed transaction {tx_hash} (Hardhat)")

    async def execute_block(self) -> None:
        """Execute all transactions in current block."""
        self.current_block += 1
        logger.info(f"Executed block, now at {self.current_block} (Hardhat)")

    async def apply_patch(self, patch: Patch) -> None:
        """Apply a state patch."""
        logger.info(f"Applied {patch.patch_type} patch (Hardhat)")

    async def get_state(self) -> Dict[str, Any]:
        """Get current VM state."""
        return {
            "block_number": self.current_block,
            "vm_type": "hardhat",
        }

    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load VM state."""
        if "block_number" in state:
            self.current_block = state["block_number"]
        logger.info(f"Loaded state (Hardhat)")

    async def get_timeline_events(self) -> AsyncIterator[TimelineEvent]:
        """Stream timeline events."""
        # Mock implementation
        for i in range(3):
            yield TimelineEvent(
                frame_id=f"hardhat_frame_{i}",
                frame_type=FrameType.CALL,
                block_number=self.current_block,
                tx_index=0,
                metadata={"vm": "hardhat", "mock": True},
            )
            await asyncio.sleep(0.1)

    async def trace_transaction(self, tx_hash: str) -> List[Dict[str, Any]]:
        """Get detailed transaction trace."""
        return [{"vm": "hardhat", "tx_hash": tx_hash, "mock": True}]


class GethAdapter(BaseVMAdapter):
    """Geth VM adapter implementation."""

    def __init__(
        self, rpc_url: str = "http://localhost:8545", datadir: Optional[str] = None
    ):
        self.rpc_url = rpc_url
        self.datadir = datadir
        self.process = None
        self.session = None
        self.current_block = 0

    async def start(self) -> None:
        """Start Geth node."""
        cmd = [
            "geth",
            "--dev",
            "--http",
            "--http.port",
            "8545",
            "--http.api",
            "eth,net,web3,debug,personal,admin",
            "--ws",
            "--ws.port",
            "8546",
        ]

        if self.datadir:
            cmd.extend(["--datadir", self.datadir])

        logger.info(f"Starting Geth with command: {' '.join(cmd)}")

        self.process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await asyncio.sleep(10)  # Geth takes longest to start
        self.session = aiohttp.ClientSession()

        logger.info("Geth started successfully")

    async def stop(self) -> None:
        """Stop Geth node."""
        if self.session:
            await self.session.close()

        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=15.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            logger.info("Geth stopped")

    async def load_block(self, block_number: int) -> None:
        """Load blockchain state at specific block."""
        self.current_block = block_number
        logger.info(f"Loaded block {block_number} (Geth)")

    async def execute_tx(self, tx_hash: str) -> None:
        """Execute a specific transaction."""
        logger.info(f"Executed transaction {tx_hash} (Geth)")

    async def execute_block(self) -> None:
        """Execute all transactions in current block."""
        self.current_block += 1
        logger.info(f"Executed block, now at {self.current_block} (Geth)")

    async def apply_patch(self, patch: Patch) -> None:
        """Apply a state patch."""
        logger.info(f"Applied {patch.patch_type} patch (Geth)")

    async def get_state(self) -> Dict[str, Any]:
        """Get current VM state."""
        return {
            "block_number": self.current_block,
            "vm_type": "geth",
        }

    async def load_state(self, state: Dict[str, Any]) -> None:
        """Load VM state."""
        if "block_number" in state:
            self.current_block = state["block_number"]
        logger.info(f"Loaded state (Geth)")

    async def get_timeline_events(self) -> AsyncIterator[TimelineEvent]:
        """Stream timeline events."""
        # Mock implementation
        for i in range(4):
            yield TimelineEvent(
                frame_id=f"geth_frame_{i}",
                frame_type=FrameType.LOG,
                block_number=self.current_block,
                tx_index=0,
                metadata={"vm": "geth", "mock": True},
            )
            await asyncio.sleep(0.1)

    async def trace_transaction(self, tx_hash: str) -> List[Dict[str, Any]]:
        """Get detailed transaction trace."""
        return [{"vm": "geth", "tx_hash": tx_hash, "mock": True}]


def get_vm(backend: VMBackend, **kwargs) -> BaseVMAdapter:
    """
    Factory function to get VM adapter.

    Args:
        backend: VM backend type
        **kwargs: Additional arguments for the adapter

    Returns:
        BaseVMAdapter: The appropriate VM adapter instance
    """
    if backend == VMBackend.ANVIL:
        return AnvilAdapter(**kwargs)
    elif backend == VMBackend.HARDHAT:
        return HardhatAdapter(**kwargs)
    elif backend == VMBackend.GETH:
        return GethAdapter(**kwargs)
    else:
        raise ValueError(f"Unknown VM backend: {backend}")


async def detect_vm(rpc_url: str = "http://localhost:8545") -> Optional[VMBackend]:
    """
    Detect which VM is running at the given RPC URL.

    Args:
        rpc_url: RPC endpoint URL

    Returns:
        VMBackend: Detected VM type or None if detection fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Try web3_clientVersion to identify the client
            payload = {
                "jsonrpc": "2.0",
                "method": "web3_clientVersion",
                "params": [],
                "id": 1,
            }

            async with session.post(rpc_url, json=payload) as response:
                result = await response.json()
                client_version = result.get("result", "").lower()

                if "anvil" in client_version:
                    return VMBackend.ANVIL
                elif "hardhat" in client_version:
                    return VMBackend.HARDHAT
                elif "geth" in client_version:
                    return VMBackend.GETH

    except Exception as e:
        logger.error(f"Failed to detect VM: {e}")

    return None
