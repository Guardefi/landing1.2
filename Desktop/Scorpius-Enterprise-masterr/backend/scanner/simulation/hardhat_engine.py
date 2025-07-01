"""
Hardhat-based Simulation Engine for Scorpius Vulnerability Scanner

This module provides blockchain simulation capabilities using Hardhat Network
for testing and validating vulnerability exploits in a controlled environment.
Hardhat is cross-platform and works excellently on Windows.
"""

import asyncio
import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

logger = None
try:
    from utils import setup_logging

    logger = setup_logging(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class HardhatConfig:
    """Configuration for Hardhat simulation environment"""

    port: int = 8545
    host: str = "127.0.0.1"
    network_id: int = 31337
    gas_limit: int = 12000000
    gas_price: int = 20000000000
    accounts_count: int = 20
    accounts_balance: str = "10000"  # ETH
    mnemonic: str = "test test test test test test test test test test test junk"
    fork_url: Optional[str] = None
    fork_block: Optional[int] = None


@dataclass
class SimulationResult:
    """Result of a blockchain simulation"""

    success: bool
    transaction_hash: Optional[str] = None
    gas_used: Optional[int] = None
    block_number: Optional[int] = None
    logs: List[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

    def __post_init__(self):
        if self.logs is None:
            self.logs = []


class HardhatSimulationEngine:
    """
    Hardhat-based blockchain simulation engine for vulnerability testing
    """

    def __init__(self, config: Optional[HardhatConfig] = None):
        self.config = config or HardhatConfig()
        self.process = None
        self.temp_dir = None
        self.is_running = False
        self.rpc_url = f"http://{self.config.host}:{self.config.port}"

    async def setup_hardhat_project(self) -> Path:
        """Set up a temporary Hardhat project"""
        # Create temporary directory for Hardhat project
        self.temp_dir = Path(tempfile.mkdtemp(prefix="scorpius_hardhat_"))

        # Create package.json
        package_json = {
            "name": "scorpius-simulation",
            "version": "1.0.0",
            "description": "Hardhat simulation environment for Scorpius",
            "scripts": {"node": "hardhat node", "test": "hardhat test"},
            "devDependencies": {
                "@nomicfoundation/hardhat-toolbox": "^4.0.0",
                "hardhat": "^2.19.0",
            },
        }

        with open(self.temp_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create hardhat.config.js
        hardhat_config = f"""
require("@nomicfoundation/hardhat-toolbox");

module.exports = {{
  networks: {{
    hardhat: {{
      chainId: {self.config.network_id},
      gas: {self.config.gas_limit},
      gasPrice: {self.config.gas_price},
      accounts: {{
        mnemonic: "{self.config.mnemonic}",
        count: {self.config.accounts_count},
        accountsBalance: "{self.config.accounts_balance}000000000000000000" // in wei
      }},
      mining: {{
        auto: true,
        interval: 0
      }},
      {f'forking: {{ url: "{self.config.fork_url}", blockNumber: {self.config.fork_block} }}' if self.config.fork_url else '// No forking configured'}
    }}
  }},
  solidity: {{
    version: "0.8.19",
    settings: {{
      optimizer: {{
        enabled: true,
        runs: 200
      }}
    }}
  }}
}};
"""

        with open(self.temp_dir / "hardhat.config.js", "w") as f:
            f.write(hardhat_config)

        # Create contracts directory
        (self.temp_dir / "contracts").mkdir(exist_ok=True)

        # Create scripts directory
        (self.temp_dir / "scripts").mkdir(exist_ok=True)

        # Create test directory
        (self.temp_dir / "test").mkdir(exist_ok=True)

        return self.temp_dir

    async def install_dependencies(self) -> bool:
        """Install npm dependencies for Hardhat"""
        try:
            logger.info("Installing Hardhat dependencies...")

            # Check if npm is available
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, cwd=self.temp_dir
            )

            if result.returncode != 0:
                logger.error("npm is not installed or not in PATH")
                return False

            # Install dependencies
            result = subprocess.run(
                ["npm", "install"],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode == 0:
                logger.info("Hardhat dependencies installed successfully")
                return True
            else:
                logger.error(
                    f"Failed to install dependencies: {
                        result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            logger.error("Dependency installation timed out")
            return False
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return False

    async def start(self) -> bool:
        """Start the Hardhat Network node"""
        if self.is_running:
            logger.warning("Hardhat node is already running")
            return True

        try:
            # Set up project
            await self.setup_hardhat_project()

            # Install dependencies
            if not await self.install_dependencies():
                return False

            # Start Hardhat node
            logger.info(f"Starting Hardhat node on {self.rpc_url}")

            cmd = [
                "npx",
                "hardhat",
                "node",
                "--hostname",
                self.config.host,
                "--port",
                str(self.config.port),
            ]

            self.process = subprocess.Popen(
                cmd,
                cwd=self.temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for node to start
            await self._wait_for_node_ready()

            self.is_running = True
            logger.info("Hardhat node started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start Hardhat node: {e}")
            await self.stop()
            return False

    async def _wait_for_node_ready(self, timeout: int = 30) -> bool:
        """Wait for Hardhat node to be ready to accept connections"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.rpc_url,
                        json={
                            "jsonrpc": "2.0",
                            "method": "eth_chainId",
                            "params": [],
                            "id": 1,
                        },
                    ) as response:
                        if response.status == 200:
                            return True
            except BaseException:
                pass

            await asyncio.sleep(1)

        raise TimeoutError("Hardhat node failed to start within timeout")

    async def stop(self):
        """Stop the Hardhat Network node and clean up"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping Hardhat process: {e}")
            finally:
                self.process = None

        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

        self.is_running = False
        logger.info("Hardhat node stopped")

    async def deploy_contract(
        self, contract_code: str, constructor_args: List[Any] = None
    ) -> Optional[str]:
        """Deploy a contract to the Hardhat network"""
        if not self.is_running:
            logger.error("Hardhat node is not running")
            return None

        try:
            # Create contract file
            contract_name = "TestContract"
            contract_file = self.temp_dir / "contracts" / f"{contract_name}.sol"

            with open(contract_file, "w") as f:
                f.write(contract_code)

            # Create deployment script
            deploy_script = f"""
const {{ ethers }} = require("hardhat");

async function main() {{
    const ContractFactory = await ethers.getContractFactory("{contract_name}");
    const contract = await ContractFactory.deploy({', '.join(map(str, constructor_args or []))});
    await contract.waitForDeployment();

    console.log("Contract deployed to:", await contract.getAddress());
    return await contract.getAddress();
}}

main()
    .then((address) => {{
        process.stdout.write(address);
        process.exit(0);
    }})
    .catch((error) => {{
        console.error(error);
        process.exit(1);
    }});
"""

            script_file = self.temp_dir / "scripts" / "deploy.js"
            with open(script_file, "w") as f:
                f.write(deploy_script)

            # Run deployment
            result = subprocess.run(
                ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "hardhat"],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                contract_address = result.stdout.strip()
                logger.info(f"Contract deployed at: {contract_address}")
                return contract_address
            else:
                logger.error(f"Contract deployment failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error deploying contract: {e}")
            return None

    async def call_contract(
        self, contract_address: str, function_data: str, value: int = 0
    ) -> SimulationResult:
        """Call a contract function"""
        if not self.is_running:
            return SimulationResult(success=False, error="Hardhat node is not running")

        try:
            start_time = time.time()

            # Make RPC call
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_sendTransaction",
                    "params": [
                        {
                            "to": contract_address,
                            "data": function_data,
                            "value": hex(value) if value > 0 else "0x0",
                            "gas": hex(self.config.gas_limit),
                        }
                    ],
                    "id": 1,
                }

                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()

                        if "result" in data:
                            tx_hash = data["result"]

                            # Get transaction receipt
                            receipt = await self._get_transaction_receipt(tx_hash)

                            return SimulationResult(
                                success=True,
                                transaction_hash=tx_hash,
                                gas_used=receipt.get("gasUsed"),
                                block_number=receipt.get("blockNumber"),
                                logs=receipt.get("logs", []),
                                execution_time=time.time() - start_time,
                            )
                        else:
                            return SimulationResult(
                                success=False,
                                error=data.get("error", {}).get(
                                    "message", "Unknown error"
                                ),
                                execution_time=time.time() - start_time,
                            )
                    else:
                        return SimulationResult(
                            success=False,
                            error=f"HTTP {response.status}",
                            execution_time=time.time() - start_time,
                        )

        except Exception as e:
            return SimulationResult(
                success=False,
                error=str(e),
                execution_time=(
                    time.time() - start_time if "start_time" in locals() else None
                ),
            )

    async def _get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash],
                    "id": 1,
                }

                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {})

        except Exception as e:
            logger.error(f"Error getting transaction receipt: {e}")

        return {}

    async def simulate_reentrancy_attack(
        self, target_contract: str, vulnerable_function: str
    ) -> Dict[str, Any]:
        """Simulate a reentrancy attack scenario"""
        if not self.is_running:
            return {"success": False, "error": "Hardhat node is not running"}

        try:
            # Create attacker contract
            attacker_contract = f"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITarget {{
    function {vulnerable_function}() external;
    function withdraw() external;
}}

contract ReentrancyAttacker {{
    ITarget public target;
    uint256 public attackCount = 0;
    uint256 public maxAttacks = 3;

    constructor(address _target) {{
        target = ITarget(_target);
    }}

    function attack() external {{
        target.{vulnerable_function}();
    }}

    receive() external payable {{
        if (attackCount < maxAttacks) {{
            attackCount++;
            target.withdraw();
        }}
    }}
}}
"""

            # Deploy attacker contract
            attacker_address = await self.deploy_contract(
                attacker_contract, [target_contract]
            )

            if not attacker_address:
                return {"success": False, "error": "Failed to deploy attacker contract"}

            # Execute attack
            # This would need proper function encoding based on the target
            # function
            result = await self.call_contract(
                attacker_address, "0x9e5faafc"
            )  # attack() function selector

            return {
                "success": result.success,
                "attacker_address": attacker_address,
                "attack_result": result.__dict__,
                "simulation_type": "reentrancy",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def simulate_flash_loan_attack(
        self, target_contract: str, loan_amount: int
    ) -> Dict[str, Any]:
        """Simulate a flash loan attack scenario"""
        if not self.is_running:
            return {"success": False, "error": "Hardhat node is not running"}

        try:
            # Create flash loan attacker contract
            attacker_contract = f"""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {{
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}}

interface IFlashLoanProvider {{
    function flashLoan(uint256 amount) external;
}}

contract FlashLoanAttacker {{
    address public target;
    IERC20 public token;

    constructor(address _target, address _token) {{
        target = _target;
        token = IERC20(_token);
    }}

    function executeAttack() external {{
        // Simulate flash loan attack logic
        uint256 amount = {loan_amount};
        // This would contain the actual attack logic
    }}
}}
"""

            # Deploy attacker contract
            attacker_address = await self.deploy_contract(
                attacker_contract, [target_contract, "0x0"]
            )

            if not attacker_address:
                return {
                    "success": False,
                    "error": "Failed to deploy flash loan attacker",
                }

            # Execute attack
            result = await self.call_contract(
                attacker_address, "0x3fb2d32d"
            )  # executeAttack() selector

            return {
                "success": result.success,
                "attacker_address": attacker_address,
                "attack_result": result.__dict__,
                "simulation_type": "flash_loan",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_account_info(self, account_index: int = 0) -> Dict[str, Any]:
        """Get information about a Hardhat account"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get accounts
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_accounts",
                    "params": [],
                    "id": 1,
                }

                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        accounts = data.get("result", [])

                        if account_index < len(accounts):
                            account = accounts[account_index]

                            # Get balance
                            balance_payload = {
                                "jsonrpc": "2.0",
                                "method": "eth_getBalance",
                                "params": [account, "latest"],
                                "id": 2,
                            }

                            async with session.post(
                                self.rpc_url, json=balance_payload
                            ) as balance_response:
                                balance_data = await balance_response.json()
                                balance = balance_data.get("result", "0x0")

                                return {
                                    "address": account,
                                    "balance": int(balance, 16),
                                    "balance_eth": int(balance, 16) / 10**18,
                                }

        except Exception as e:
            logger.error(f"Error getting account info: {e}")

        return {}

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.is_running:
            try:
                asyncio.create_task(self.stop())
            except BaseException:
                pass
