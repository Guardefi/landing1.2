"""Base scanner plugin implementation for Scorpius Vulnerability Scanner

This module provides the base implementation for scanner plugins to
be used with the Scorpius Vulnerability Scanner. All scanner plugins
should inherit from this class and implement the required methods.
"""

import logging
from abc import abstractmethod
from typing import List

from core.models import ScanConfig, ScanType, Target, VulnerabilityFinding

# Import from core plugin manager to avoid circular imports
from core.plugin_manager import ScannerPlugin

logger = logging.getLogger("scorpius.scanners.base")


class BaseScannerPlugin(ScannerPlugin):
    """Base class for all scanner plugins

    This class extends the ScannerPlugin abstract base class to provide
    common functionality for all scanner plugins. Each specific scanner
    plugin should inherit from this class.
    """

    NAME = "base_scanner"
    DESCRIPTION = "Base scanner plugin that other scanner plugins should inherit from"
    VERSION = "0.1.0"
    AUTHOR = "Scorpius Team"
    SUPPORTED_SCAN_TYPES = [ScanType.STATIC, ScanType.DYNAMIC]
    DEPENDENCIES = []

    def __init__(self):
        """Initialize the scanner plugin"""
        self.initialized = False
        self.config = {}
        logger.debug(f"Created {self.NAME} scanner plugin")

    async def initialize(self) -> bool:
        """Initialize the plugin with default implementation

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            logger.debug(f"Plugin {self.NAME} already initialized")
            return True

        logger.info(f"Initializing {self.NAME} scanner plugin")

        # Check if dependencies are available
        missing_deps = await self._check_dependencies()
        if missing_deps:
            logger.error(
                f"Cannot initialize {
                    self.NAME}: missing dependencies: {missing_deps}"
            )
            return False

        self.initialized = True
        logger.info(f"Plugin {self.NAME} initialized successfully")
        return True

    async def _check_dependencies(self) -> List[str]:
        """Check if all dependencies are available

        Returns:
            List[str]: List of missing dependencies
        """
        missing = []
        for dep in self.DEPENDENCIES:
            if not await self._check_dependency(dep):
                missing.append(dep)
        return missing

    async def _check_dependency(self, dependency: str) -> bool:
        """Check if a specific dependency is available

        Args:
            dependency: The dependency to check

        Returns:
            bool: True if dependency is available, False otherwise
        """
        # Basic implementation - override for actual dependency checks
        return True

    @abstractmethod
    async def scan(
        self, target: Target, config: ScanConfig
    ) -> List[VulnerabilityFinding]:
        """Perform a vulnerability scan on the target

        Args:
            target: Target to scan
            config: Configuration for the scan

        Returns:
            List[VulnerabilityFinding]: List of vulnerability findings
        """
        raise NotImplementedError("Scan method must be implemented by subclasses")

    async def cleanup(self) -> None:
        """Clean up any resources used by the plugin"""
        if not self.initialized:
            return

        logger.info(f"Cleaning up resources for plugin {self.NAME}")
        self.initialized = False
