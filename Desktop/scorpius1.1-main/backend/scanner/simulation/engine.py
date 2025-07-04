"""
Advanced Blockchain Simulation Engine
Manages Anvil/Foundry-based blockchain simulation for vulnerability testing
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("scorpius.simulation.engine")


@dataclass
class SimulationConfig:
    """Configuration for blockchain simulation"""

    anvil_path: str = "anvil"
    forge_path: str = "forge"
    default_gas_limit: int = 30000000
    block_time: int = 1
    port: int = 8545
    fork_url: Optional[str] = None
    fork_block_number: Optional[int] = None
    accounts_count: int = 10
    balance: str = "10000"  # ETH


@dataclass
class SimulationResult:
    """Result of a simulation run"""

    success: bool
    stdout: str
    stderr: str
    gas_used: int = 0
    block_number: int = 0
    transaction_hash: Optional[str] = None
    events: List[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0


class AdvancedSimulationEngine:
    """Advanced blockchain simulation engine using Anvil/Foundry"""

    def __init__(self, config: SimulationConfig = None):
        """Initialize the simulation engine"""
        self.config = config or SimulationConfig()
        self.anvil_process: Optional[subprocess.Popen] = None
        self.temp_dir: Optional[str] = None
        self.is_running = False
        self.local_rpc_url = f"http://localhost:{self.config.port}"

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def start(self) -> None:
        """Start the Anvil blockchain simulation"""
        if self.is_running:
            logger.warning("Simulation engine is already running")
            return

        self.temp_dir = tempfile.mkdtemp(prefix="scorpius_sim_")
        logger.info(f"Starting simulation in {self.temp_dir}")

        # Build Anvil command
        cmd = [
            self.config.anvil_path,
            "--port",
            str(self.config.port),
            "--gas-limit",
            str(self.config.default_gas_limit),
            "--accounts",
            str(self.config.accounts_count),
            "--balance",
            self.config.balance,
            "--block-time",
            str(self.config.block_time),
            "--silent",
        ]

        # Add fork configuration if specified
        if self.config.fork_url:
            cmd.extend(["--fork-url", self.config.fork_url])
            if self.config.fork_block_number:
                cmd.extend(["--fork-block-number", str(self.config.fork_block_number)])

        try:
            logger.info(f"Starting Anvil with command: {' '.join(cmd)}")
            self.anvil_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.temp_dir,
                env=os.environ.copy(),
            )

            # Wait for Anvil to start
            await self._wait_for_anvil_startup()
            self.is_running = True
            logger.info(f"Anvil started successfully on port {self.config.port}")

        except Exception as e:
            logger.error(f"Failed to start Anvil: {e}")
            await self.cleanup()
            raise

    async def _wait_for_anvil_startup(self, timeout: int = 30) -> None:
        """Wait for Anvil to start and be ready to accept connections"""
        import aiohttp

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.local_rpc_url,
                        json={
                            "jsonrpc": "2.0",
                            "method": "eth_chainId",
                            "params": [],
                            "id": 1,
                        },
                        timeout=aiohttp.ClientTimeout(total=2),
                    ) as response:
                        if response.status == 200:
                            return
            except Exception:
                pass

            await asyncio.sleep(0.5)

        raise RuntimeError(f"Anvil failed to start within {timeout} seconds")

    async def cleanup(self) -> None:
        """Clean up simulation resources"""
        if self.anvil_process:
            logger.info("Terminating Anvil process")
            self.anvil_process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process_termination()),
                    timeout=10,
                )
            except asyncio.TimeoutError:
                logger.warning("Anvil process did not terminate gracefully, killing")
                self.anvil_process.kill()

            self.anvil_process = None

        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")

        self.is_running = False

    async def _wait_for_process_termination(self) -> None:
        """Wait for the Anvil process to terminate"""
        if self.anvil_process:
            while self.anvil_process.poll() is None:
                await asyncio.sleep(0.1)

    async def run_forge_test(
        self,
        test_contract: str,
        test_name: Optional[str] = None,
        additional_contracts: Optional[Dict[str, str]] = None,
    ) -> SimulationResult:
        """
        Run a Forge test against the simulation

        Args:
            test_contract: Solidity test contract code
            test_name: Specific test function name to run
            additional_contracts: Additional contract files needed

        Returns:
            SimulationResult with test execution details
        """
        if not self.is_running:
            raise RuntimeError("Simulation engine is not running")

        start_time = time.time()

        try:
            # Create forge project structure
            project_dir = await self._create_forge_project(
                test_contract, additional_contracts
            )

            # Run forge test
            cmd = [
                self.config.forge_path,
                "test",
                "--rpc-url",
                self.local_rpc_url,
                "-vvv",  # Verbose output
            ]

            if test_name:
                cmd.extend(["--match-test", test_name])

            logger.info(f"Running forge test: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )

            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            return SimulationResult(
                success=process.returncode == 0,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
                execution_time=execution_time,
            )

        except Exception as e:
            logger.error(f"Forge test execution failed: {e}")
            return SimulationResult(
                success=False,
                stdout="",
                stderr=str(e),
                error_message=f"Test execution failed: {e}",
                execution_time=time.time() - start_time,
            )

    async def _create_forge_project(
        self, test_contract: str, additional_contracts: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a temporary Forge project with the test contracts"""
        project_dir = os.path.join(self.temp_dir, "forge_project")
        os.makedirs(project_dir, exist_ok=True)

        # Create foundry.toml
        foundry_config = """
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
test = "test"
cache_path = "cache"
"""
        with open(os.path.join(project_dir, "foundry.toml"), "w") as f:
            f.write(foundry_config)

        # Create directory structure
        for dir_name in ["src", "test", "lib"]:
            os.makedirs(os.path.join(project_dir, dir_name), exist_ok=True)

        # Write test contract
        test_dir = os.path.join(project_dir, "test")
        with open(os.path.join(test_dir, "VulnerabilityTest.sol"), "w") as f:
            f.write(test_contract)

        # Write additional contracts
        if additional_contracts:
            src_dir = os.path.join(project_dir, "src")
            for filename, content in additional_contracts.items():
                with open(os.path.join(src_dir, filename), "w") as f:
                    f.write(content)

        return project_dir

    async def deploy_contract(
        self, contract_code: str, constructor_args: Optional[List[Any]] = None
    ) -> SimulationResult:
        """
        Deploy a contract to the simulation blockchain

        Args:
            contract_code: Solidity contract code
            constructor_args: Constructor arguments

        Returns:
            SimulationResult with deployment details
        """
        if not self.is_running:
            raise RuntimeError("Simulation engine is not running")

        start_time = time.time()

        try:
            # Create deployment script
            deployment_script = self._create_deployment_script(
                contract_code, constructor_args
            )

            # Create temporary project
            project_dir = await self._create_forge_project(
                "", {"Target.sol": contract_code}
            )

            # Write deployment script
            script_dir = os.path.join(project_dir, "script")
            os.makedirs(script_dir, exist_ok=True)
            with open(os.path.join(script_dir, "Deploy.s.sol"), "w") as f:
                f.write(deployment_script)

            # Run deployment
            cmd = [
                self.config.forge_path,
                "script",
                "script/Deploy.s.sol",
                "--rpc-url",
                self.local_rpc_url,
                "--broadcast",
                "--private-key",
                "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",  # Anvil default key
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            return SimulationResult(
                success=process.returncode == 0,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
                execution_time=execution_time,
            )

        except Exception as e:
            logger.error(f"Contract deployment failed: {e}")
            return SimulationResult(
                success=False,
                stdout="",
                stderr=str(e),
                error_message=f"Deployment failed: {e}",
                execution_time=time.time() - start_time,
            )

    def _create_deployment_script(
        self, contract_code: str, constructor_args: Optional[List[Any]] = None
    ) -> str:
        """Create a Forge deployment script"""
        script = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/Target.sol";

contract DeployScript is Script {{
    function run() public {{
        vm.startBroadcast();
        
        Target target = new Target({', '.join(map(str, constructor_args or []))});
        
        vm.stopBroadcast();
        
        console.log("Contract deployed at:", address(target));
    }}
}}
"""
        return script

    async def simulate_transaction(
        self,
        to_address: str,
        data: str,
        value: int = 0,
        from_address: Optional[str] = None,
    ) -> SimulationResult:
        """
        Simulate a transaction on the blockchain

        Args:
            to_address: Target contract address
            data: Transaction data
            value: ETH value to send
            from_address: Sender address (uses default if None)

        Returns:
            SimulationResult with transaction details
        """
        if not self.is_running:
            raise RuntimeError("Simulation engine is not running")

        import aiohttp

        # Default sender address (first Anvil account)
        if not from_address:
            from_address = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"

        # Prepare transaction
        transaction = {
            "jsonrpc": "2.0",
            "method": "eth_sendTransaction",
            "params": [
                {
                    "from": from_address,
                    "to": to_address,
                    "data": data,
                    "value": hex(value) if value > 0 else "0x0",
                }
            ],
            "id": 1,
        }

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.local_rpc_url, json=transaction
                ) as response:
                    result = await response.json()
                    execution_time = time.time() - start_time

                    if "result" in result:
                        return SimulationResult(
                            success=True,
                            stdout=f"Transaction hash: {result['result']}",
                            stderr="",
                            transaction_hash=result["result"],
                            execution_time=execution_time,
                        )
                    else:
                        return SimulationResult(
                            success=False,
                            stdout="",
                            stderr=result.get("error", {}).get(
                                "message", "Unknown error"
                            ),
                            execution_time=execution_time,
                        )

        except Exception as e:
            logger.error(f"Transaction simulation failed: {e}")
            return SimulationResult(
                success=False,
                stdout="",
                stderr=str(e),
                error_message=f"Transaction failed: {e}",
                execution_time=time.time() - start_time,
            )

    async def get_blockchain_state(self) -> Dict[str, Any]:
        """Get current blockchain state information"""
        if not self.is_running:
            raise RuntimeError("Simulation engine is not running")

        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                # Get chain ID
                chain_id_resp = await session.post(
                    self.local_rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_chainId",
                        "params": [],
                        "id": 1,
                    },
                )
                chain_id = await chain_id_resp.json()

                # Get block number
                block_number_resp = await session.post(
                    self.local_rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 2,
                    },
                )
                block_number = await block_number_resp.json()

                # Get gas price
                gas_price_resp = await session.post(
                    self.local_rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_gasPrice",
                        "params": [],
                        "id": 3,
                    },
                )
                gas_price = await gas_price_resp.json()

                return {
                    "chain_id": chain_id.get("result"),
                    "block_number": int(block_number.get("result", "0x0"), 16),
                    "gas_price": int(gas_price.get("result", "0x0"), 16),
                    "rpc_url": self.local_rpc_url,
                    "is_fork": bool(self.config.fork_url),
                }

        except Exception as e:
            logger.error(f"Failed to get blockchain state: {e}")
            return {"error": str(e)}
