"""
MevGuardian Integrated Bot - Main entry point for the dual-mode MEV system.

This module integrates the existing MEV bot attack capabilities with the new
Guardian defense system, providing seamless mode switching and unified operation.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from core.engine import MevEngine
from execution.execution_engine import ExecutionEngine
from mev_guardian.api import app
from mev_guardian.config import MevGuardianConfig
from mev_guardian.guardian_engine import GuardianEngine
from mev_guardian.types import ThreatType

# Import existing MEV components
from packages.core.mempool_scanner import MempoolScanner


class MevGuardianBot:
    """
    Integrated MEV Guardian Bot supporting both attack and defense modes.

    This class orchestrates the entire MevGuardian system, managing both
    the traditional MEV bot functionality (attack mode) and the new
    Guardian protection capabilities (defense mode).
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MevGuardian bot.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = MevGuardianConfig.load(config_path)
        self.logger = logging.getLogger(__name__)

        # Core components
        self.guardian_engine: Optional[GuardianEngine] = None
        self.mev_engine: Optional[MevEngine] = None
        self.mempool_scanner: Optional[MempoolScanner] = None
        self.execution_engine: Optional[ExecutionEngine] = None

        # State tracking
        self.is_running = False
        self.current_mode = self.config.mode
        self.metrics = {
            "threats_detected": 0,
            "attacks_executed": 0,
            "profits_usd": 0.0,
            "gas_saved": 0.0,
        }

    async def initialize(self) -> None:
        """Initialize all bot components."""
        try:
            self.logger.info(
                f"Initializing MevGuardian in {
                    self.current_mode} mode"
            )

            # Initialize Guardian engine (always available)
            self.guardian_engine = GuardianEngine(self.config)
            await self.guardian_engine.initialize()

            # Initialize attack components if needed
            if self.current_mode == "attack" or self.config.enable_dual_mode:
                await self._initialize_attack_components()

            # Setup event handlers
            self._setup_event_handlers()

            self.logger.info("MevGuardian initialization complete")

        except Exception as e:
            self.logger.error(f"Failed to initialize MevGuardian: {e}")
            raise

    async def _initialize_attack_components(self) -> None:
        """Initialize MEV attack components."""
        try:
            # Initialize mempool scanner
            self.mempool_scanner = MempoolScanner(
                rpc_url=self.config.rpc_url, chain_id=self.config.chain_id
            )

            # Initialize execution engine
            self.execution_engine = ExecutionEngine(
                private_key=self.config.private_key,
                rpc_url=self.config.rpc_url)

            # Initialize MEV engine with strategies
            self.mev_engine = MevEngine(
                config=self.config,
                mempool_scanner=self.mempool_scanner,
                execution_engine=self.execution_engine,
            )

            self.logger.info("Attack components initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize attack components: {e}")
            raise

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for cross-component communication."""
        if self.guardian_engine:
            # Forward Guardian threats to WebSocket clients
            self.guardian_engine.on_threat_detected = self._handle_threat_detected

        if self.mempool_scanner:
            # Forward mempool data to Guardian for analysis
            self.mempool_scanner.on_transaction = self._handle_mempool_transaction

    async def _handle_threat_detected(self, threat: Dict[str, Any]) -> None:
        """Handle threats detected by Guardian engine."""
        self.metrics["threats_detected"] += 1

        # Log threat
        self.logger.warning(f"Threat detected: {threat}")

        # If in attack mode, potentially exploit the threat
        if self.current_mode == "attack" and self.mev_engine:
            await self._evaluate_threat_for_exploitation(threat)

    async def _handle_mempool_transaction(
            self, tx_data: Dict[str, Any]) -> None:
        """Handle new mempool transactions."""
        # Forward to Guardian for threat analysis
        if self.guardian_engine:
            await self.guardian_engine.analyze_transaction(tx_data)

        # Process for MEV opportunities if in attack mode
        if self.current_mode == "attack" and self.mev_engine:
            await self.mev_engine.process_transaction(tx_data)

    async def _evaluate_threat_for_exploitation(
            self, threat: Dict[str, Any]) -> None:
        """Evaluate if a detected threat can be exploited for profit."""
        try:
            threat_type = threat.get("type")

            if threat_type == ThreatType.ARBITRAGE.value:
                # Execute arbitrage opportunity
                await self._execute_arbitrage(threat)
            elif threat_type == ThreatType.SANDWICH.value:
                # Execute sandwich attack
                await self._execute_sandwich(threat)
            elif threat_type == ThreatType.FRONT_RUNNING.value:
                # Execute front-running
                await self._execute_front_run(threat)

        except Exception as e:
            self.logger.error(f"Failed to exploit threat: {e}")

    async def _execute_arbitrage(self, threat: Dict[str, Any]) -> None:
        """Execute arbitrage based on detected opportunity."""
        if not self.execution_engine:
            return

        # Implementation would integrate with existing arbitrage strategy
        self.logger.info(f"Executing arbitrage: {threat}")
        # TODO: Integrate with strategies/two_hop_arbitrage.py

    async def _execute_sandwich(self, threat: Dict[str, Any]) -> None:
        """Execute sandwich attack based on detected opportunity."""
        if not self.execution_engine:
            return

        # Implementation would integrate with existing sandwich strategy
        self.logger.info(f"Executing sandwich: {threat}")
        # TODO: Integrate with strategies/sandwich.py

    async def _execute_front_run(self, threat: Dict[str, Any]) -> None:
        """Execute front-running based on detected opportunity."""
        if not self.execution_engine:
            return

        # Implementation would integrate with front-running logic
        self.logger.info(f"Executing front-run: {threat}")

    async def switch_mode(self, new_mode: str) -> bool:
        """
        Switch between attack and defense modes.

        Args:
            new_mode: "attack" or "guardian"

        Returns:
            True if switch was successful
        """
        try:
            if new_mode == self.current_mode:
                return True

            self.logger.info(
                f"Switching from {
                    self.current_mode} to {new_mode} mode"
            )

            if new_mode == "attack":
                if not self.mev_engine:
                    await self._initialize_attack_components()
                # Resume attack operations
                if self.mev_engine:
                    await self.mev_engine.start()
            elif new_mode == "guardian":
                # Pause attack operations
                if self.mev_engine:
                    await self.mev_engine.stop()

            self.current_mode = new_mode
            self.config.mode = new_mode

            self.logger.info(f"Successfully switched to {new_mode} mode")
            return True

        except Exception as e:
            self.logger.error(f"Failed to switch mode: {e}")
            return False

    async def start(self) -> None:
        """Start the MevGuardian bot."""
        try:
            if self.is_running:
                self.logger.warning("Bot is already running")
                return

            await self.initialize()

            # Start Guardian engine
            if self.guardian_engine:
                await self.guardian_engine.start()

            # Start attack components if in attack mode
            if self.current_mode == "attack" and self.mev_engine:
                await self.mev_engine.start()

            # Start mempool scanner
            if self.mempool_scanner:
                await self.mempool_scanner.start()

            self.is_running = True
            self.logger.info("MevGuardian bot started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start MevGuardian bot: {e}")
            raise

    async def stop(self) -> None:
        """Stop the MevGuardian bot."""
        try:
            if not self.is_running:
                return

            self.logger.info("Stopping MevGuardian bot")

            # Stop all components
            if self.mempool_scanner:
                await self.mempool_scanner.stop()

            if self.mev_engine:
                await self.mev_engine.stop()

            if self.guardian_engine:
                await self.guardian_engine.stop()

            self.is_running = False
            self.logger.info("MevGuardian bot stopped")

        except Exception as e:
            self.logger.error(f"Error stopping MevGuardian bot: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current bot status and metrics."""
        return {
            "running": self.is_running,
            "mode": self.current_mode,
            "metrics": self.metrics,
            "components": {
                "guardian_engine": self.guardian_engine is not None,
                "mev_engine": self.mev_engine is not None,
                "mempool_scanner": self.mempool_scanner is not None,
                "execution_engine": self.execution_engine is not None,
            },
        }


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan manager for MevGuardian bot."""
    # Startup
    bot = MevGuardianBot()
    await bot.start()
    app.state.bot = bot

    yield

    # Shutdown
    await bot.stop()


# Update the FastAPI app to use the lifespan manager
app.router.lifespan_context = lifespan


async def main():
    """Main entry point for running MevGuardian bot."""
    import uvicorn

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    try:
        # Create and start bot
        bot = MevGuardianBot()

        # Start bot in background
        bot_task = asyncio.create_task(bot.start())

        # Start API server
        config = uvicorn.Config(
            app="mev_guardian_bot:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
        server = uvicorn.Server(config)

        logger.info("Starting MevGuardian system...")

        # Run both bot and API server
        await asyncio.gather(bot_task, server.serve())

    except KeyboardInterrupt:
        logger.info("Shutting down MevGuardian...")
    except Exception as e:
        logger.error(f"MevGuardian error: {e}")
        raise
    finally:
        if "bot" in locals():
            await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
