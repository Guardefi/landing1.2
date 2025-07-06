"""Plugin Manager for Scorpius Vulnerability Scanner

This module provides functionality to dynamically load, register, and manage
vulnerability scanning plugins. It supports hot-loading of plugins and maintains
a registry of available plugins and their capabilities.
"""

import importlib
import inspect
import logging
import os
import pkgutil
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set, Type

from core.models import ScanConfig, ScanType, Target, VulnerabilityFinding

logger = logging.getLogger("scorpius.plugin_manager")


class ScannerPlugin(ABC):
    """Base class for all vulnerability scanner plugins"""

    # Plugin metadata
    NAME: str = "base_plugin"  # Unique name for this plugin
    DESCRIPTION: str = "Base plugin class"  # Description of what this plugin does
    VERSION: str = "0.1.0"  # Version of this plugin
    AUTHOR: str = "Scorpius Team"  # Author(s) of this plugin
    SUPPORTED_SCAN_TYPES: List[ScanType] = []  # Scan types this plugin supports
    DEPENDENCIES: List[str] = []  # External dependencies required by this plugin

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass

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
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up any resources used by the plugin"""
        pass

    def supports_scan_type(self, scan_type: ScanType) -> bool:
        """Check if this plugin supports a specific scan type

        Args:
            scan_type: Scan type to check for support

        Returns:
            bool: True if supported, False otherwise
        """
        # Special case: FULL scan type is supported by all plugins
        if scan_type == ScanType.FULL:
            return True

        return scan_type in self.SUPPORTED_SCAN_TYPES

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about this plugin

        Returns:
            Dict[str, Any]: Dictionary containing plugin metadata
        """
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "author": self.AUTHOR,
            "supported_scan_types": [st.value for st in self.SUPPORTED_SCAN_TYPES],
            "dependencies": self.DEPENDENCIES,
        }


class PluginManager:
    """Manager for vulnerability scanner plugins"""

    def __init__(self, plugin_dirs: List[str] = None):
        """Initialize the plugin manager

        Args:
            plugin_dirs: List of directories containing plugins
        """
        self.plugins: Dict[str, ScannerPlugin] = {}  # name -> plugin instance
        self.plugin_classes: Dict[str, Type[ScannerPlugin]] = {}  # name -> plugin class
        self.plugin_dirs = plugin_dirs or ["plugins", "scanners"]

        # Keep track of loaded modules to avoid duplicates
        self.loaded_modules = set()

        logger.info(f"Plugin Manager initialized with directories: {self.plugin_dirs}")

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directories

        Returns:
            List[str]: List of discovered plugin module paths
        """
        discovered_plugins = []

        # Add plugin directories to path if not already there
        for plugin_dir in self.plugin_dirs:
            if os.path.isdir(plugin_dir) and plugin_dir not in sys.path:
                sys.path.append(os.path.abspath(plugin_dir))

        # Walk through each plugin directory
        for plugin_dir in self.plugin_dirs:
            if not os.path.isdir(plugin_dir):
                logger.warning(f"Plugin directory {plugin_dir} not found")
                continue

            for _, name, ispkg in pkgutil.iter_modules([plugin_dir]):
                module_path = f"{plugin_dir}.{name}"

                if module_path not in self.loaded_modules:
                    discovered_plugins.append(module_path)

            # Also look for nested modules
            for root, dirs, files in os.walk(plugin_dir):
                for dir_name in dirs:
                    # Convert directory path to module path
                    rel_path = os.path.relpath(
                        os.path.join(root, dir_name), start=os.path.dirname(plugin_dir)
                    )
                    module_path = rel_path.replace(os.sep, ".")

                    if (
                        module_path not in self.loaded_modules
                        and "__pycache__" not in module_path
                    ):
                        for _, name, ispkg in pkgutil.iter_modules(
                            [os.path.join(root, dir_name)]
                        ):
                            full_module_path = f"{module_path}.{name}"
                            discovered_plugins.append(full_module_path)

        return discovered_plugins

    def register_plugin(self, plugin_module_path: str) -> bool:
        """Register a plugin from its module path

        Args:
            plugin_module_path: Module path to the plugin

        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            # Import the module
            module = importlib.import_module(plugin_module_path)
            self.loaded_modules.add(plugin_module_path)

            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ScannerPlugin)
                    and obj != ScannerPlugin
                ):
                    plugin_classes.append(obj)

            if not plugin_classes:
                logger.warning(
                    f"No plugin classes found in module {plugin_module_path}"
                )
                return False

            # Register each plugin class found
            for plugin_class in plugin_classes:
                plugin_name = plugin_class.NAME

                if plugin_name in self.plugin_classes:
                    logger.warning(
                        f"Plugin {plugin_name} already registered, will be overwritten"
                    )

                # Store the class for later instantiation
                self.plugin_classes[plugin_name] = plugin_class

                try:
                    # Create an instance of the plugin
                    plugin_instance = plugin_class()
                    self.plugins[plugin_name] = plugin_instance
                    logger.info(
                        f"Successfully registered plugin {plugin_name} from {plugin_module_path}"
                    )
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin {plugin_name}: {e}")
                    continue

            return True

        except ImportError as e:
            logger.error(f"Failed to import plugin module {plugin_module_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error registering plugin from {plugin_module_path}: {e}")
            return False

    async def initialize_plugins(self) -> Dict[str, bool]:
        """Initialize all registered plugins

        Returns:
            Dict[str, bool]: Dictionary mapping plugin names to initialization status
        """
        results = {}

        for name, plugin in self.plugins.items():
            try:
                success = await plugin.initialize()
                results[name] = success

                if success:
                    logger.info(f"Successfully initialized plugin {name}")
                else:
                    logger.warning(f"Plugin {name} initialization returned False")

            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")
                results[name] = False

        return results

    def get_plugins(self) -> Dict[str, ScannerPlugin]:
        """Get all registered plugins

        Returns:
            Dict[str, ScannerPlugin]: Dictionary mapping plugin names to instances
        """
        return self.plugins

    def get_plugin(self, name: str) -> Optional[ScannerPlugin]:
        """Get a specific plugin by name

        Args:
            name: Name of the plugin to get

        Returns:
            Optional[ScannerPlugin]: Plugin instance if found, None otherwise
        """
        return self.plugins.get(name)

    def get_plugins_by_scan_type(self, scan_type: ScanType) -> Dict[str, ScannerPlugin]:
        """Get all plugins that support a specific scan type

        Args:
            scan_type: Scan type to filter by

        Returns:
            Dict[str, ScannerPlugin]: Dictionary mapping plugin names to instances
        """
        return {
            name: plugin
            for name, plugin in self.plugins.items()
            if plugin.supports_scan_type(scan_type)
        }

    async def cleanup_plugins(self) -> None:
        """Clean up all registered plugins"""
        for name, plugin in self.plugins.items():
            try:
                await plugin.cleanup()
                logger.info(f"Cleaned up plugin {name}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin {name}: {e}")

    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin

        Args:
            name: Name of the plugin to unregister

        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        if name not in self.plugins:
            logger.warning(f"Plugin {name} not found, cannot unregister")
            return False

        del self.plugins[name]
        if name in self.plugin_classes:
            del self.plugin_classes[name]

        logger.info(f"Unregistered plugin {name}")
        return True

    def reload_plugin(self, name: str) -> bool:
        """Reload a plugin

        Args:
            name: Name of the plugin to reload

        Returns:
            bool: True if reload was successful, False otherwise
        """
        if name not in self.plugin_classes:
            logger.warning(f"Plugin class {name} not found, cannot reload")
            return False

        # Get the plugin class
        plugin_class = self.plugin_classes[name]

        try:
            # Create a new instance of the plugin
            plugin_instance = plugin_class()
            self.plugins[name] = plugin_instance
            logger.info(f"Successfully reloaded plugin {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload plugin {name}: {e}")
            return False

    def get_plugin_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all plugins

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping plugin names to metadata
        """
        return {name: plugin.get_metadata() for name, plugin in self.plugins.items()}
