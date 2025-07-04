"""
Core Scanning Engine for Scorpius Vulnerability Scanner
Orchestrates the scanning process and coordinates all scan operations
"""
import asyncio
import concurrent.futures
import importlib
import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from core.models import (
    ScanConfig,
    ScanResult,
    ScanStatus,
    ScanType,
    Target,
    VulnerabilityFinding,
    VulnerabilityLevel,
)
from core.plugin_manager import PluginManager
from sandbox import SandboxManager, SandboxType
from utils.logging_utils import setup_logger

from reporting import ReportFormat, generate_report

logger = logging.getLogger("scorpius.engine")


class ScanEngine:
    """Core engine that orchestrates all scanning operations"""

    def __init__(self, config_path: str = None):
        """
        Initialize the scan engine with configuration

        Args:
            config_path: Path to configuration file
        """
        self.plugin_manager = PluginManager()
        self.active_scans = {}  # Track active scan jobs
        self.scan_history = {}  # Track completed scans
        self.config = self._load_config(config_path)

        # Initialize sandbox manager for secure execution
        self.sandbox_manager = SandboxManager(self.config.get("sandbox", {}))

        # Load default plugins
        self._load_default_plugins()

        logger.info("Scorpius Scan Engine initialized successfully")

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "max_concurrent_scans": 5,
            "default_timeout": 300,  # 5 minutes
            "plugin_directory": "plugins",
            "report_directory": "reports",
            "sandbox_enabled": True,
            "logging": {"level": "INFO", "file": "logs/scorpius.log"},
        }

        if not config_path:
            logger.info("Using default configuration")
            return default_config

        try:
            with open(config_path, "r") as config_file:
                loaded_config = json.load(config_file)
                # Merge with defaults
                for key, value in loaded_config.items():
                    default_config[key] = value
                logger.info(f"Configuration loaded from {config_path}")
                return default_config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config

    def _load_default_plugins(self):
        """Load the default scanning plugins"""
        default_plugins = [
            "scanners.static.slither_plugin",
            "scanners.dynamic.mythril_plugin",
            "scanners.dynamic.manticore_plugin",
        ]

        for plugin_module in default_plugins:
            try:
                self.plugin_manager.register_plugin(plugin_module)
                logger.info(f"Loaded default plugin: {plugin_module}")
            except ImportError as e:
                logger.warning(f"Could not load plugin {plugin_module}: {e}")

    async def start_scan(
        self, target: Target, scan_type: ScanType, config: Optional[ScanConfig] = None
    ) -> str:
        """
        Start a new vulnerability scan

        Args:
            target: Target to scan (contract address, source code, etc.)
            scan_type: Type of scan to perform
            config: Additional scan configuration

        Returns:
            Scan ID for tracking
        """
        scan_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Create scan result object to track progress
        scan_result = ScanResult(
            id=scan_id,
            target=target,
            scan_type=scan_type,
            status=ScanStatus.PENDING,
            start_time=timestamp,
            config=config or ScanConfig(),
            findings=[],
        )

        self.active_scans[scan_id] = scan_result

        # Start the scan in the background
        asyncio.create_task(self._execute_scan(scan_id, scan_result))

        logger.info(f"Scan {scan_id} started for target {target.identifier}")
        return scan_id

    async def _execute_scan(self, scan_id: str, scan_result: ScanResult) -> None:
        """
        Execute a scan with the appropriate plugins

        Args:
            scan_id: ID of the scan to execute
            scan_result: Scan result object to update
        """
        try:
            logger.info(f"Executing scan {scan_id}")
            scan_result.status = ScanStatus.RUNNING
            scan_result.progress = 0
            start_time = time.time()

            # Check sandbox availability if enabled
            if self.config.get("sandbox_enabled", True):
                sandbox_available = await self.sandbox_manager.check_availability()
                if not any(sandbox_available.values()):
                    logger.warning(
                        "No sandbox environments available, continuing without sandbox"
                    )
                    scan_result.warnings = ["No sandbox environments available"]

            # Determine which plugins to use based on scan type
            plugins_to_run = self._select_plugins(
                scan_result.scan_type, scan_result.config
            )

            if not plugins_to_run:
                scan_result.status = ScanStatus.FAILED
                scan_result.end_time = datetime.now().isoformat()
                scan_result.error = "No suitable plugins found for this scan type"
                logger.error(f"Scan {scan_id} failed: No suitable plugins")
                return

            total_plugins = len(plugins_to_run)
            complete_plugins = 0
            all_findings = []

            # Initialize all plugins before scanning
            for plugin_name, plugin in plugins_to_run.items():
                try:
                    logger.info(f"Initializing plugin {plugin_name}")
                    await plugin.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
                    plugins_to_run.pop(plugin_name)  # Remove plugin from execution

            # Create sandboxes for dynamic plugins if enabled
            sandboxes = {}
            if self.config.get("sandbox_enabled", True):
                for plugin_name, plugin in plugins_to_run.items():
                    # Check if plugin needs a sandbox (currently all dynamic plugins use sandbox)
                    if (
                        ScanType.DYNAMIC in plugin.SUPPORTED_SCAN_TYPES
                        or scan_result.scan_type == ScanType.DYNAMIC
                    ):
                        try:
                            sandbox_id = await self.create_sandbox_for_plugin(
                                plugin_name, plugin
                            )
                            if sandbox_id:
                                sandboxes[plugin_name] = sandbox_id
                                logger.info(
                                    f"Created sandbox {sandbox_id} for plugin {plugin_name}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Failed to create sandbox for plugin {plugin_name}: {e}"
                            )

            # Sequential scanning for now - could be made parallel if plugins support it
            for plugin_name, plugin in plugins_to_run.items():
                try:
                    logger.info(f"Running plugin {plugin_name} for scan {scan_id}")
                    scan_result.current_plugin = plugin_name

                    # Pass sandbox ID to plugin if available through config
                    custom_config = (
                        scan_result.config.copy()
                        if scan_result.config
                        else ScanConfig()
                    )
                    if plugin_name in sandboxes:
                        custom_config.custom_options["sandbox_id"] = sandboxes[
                            plugin_name
                        ]

                    # Run the scan
                    plugin_findings = await plugin.scan(
                        scan_result.target, custom_config
                    )

                    # Filter findings
                    enriched_findings = self._enrich_findings(
                        plugin_findings, plugin_name
                    )
                    all_findings.extend(enriched_findings)

                    complete_plugins += 1
                    scan_result.progress = int((complete_plugins / total_plugins) * 100)

                    logger.info(
                        f"Plugin {plugin_name} completed with {len(plugin_findings)} findings"
                    )
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} failed: {e}")

            # Cleanup sandboxes
            if sandboxes:
                await self.cleanup_sandboxes(sandboxes)

            # Cleanup plugins
            for plugin_name, plugin in plugins_to_run.items():
                try:
                    await plugin.cleanup()
                except Exception as e:
                    logger.error(f"Failed to cleanup plugin {plugin_name}: {e}")

            # Deduplicate and prioritize findings
            scan_result.findings = self._process_findings(all_findings)
            scan_result.status = ScanStatus.COMPLETED
            scan_result.end_time = datetime.now().isoformat()
            scan_result.progress = 100
            scan_result.scan_duration = time.time() - start_time

            # Generate reports if configured
            if scan_result.config and scan_result.config.generate_reports:
                await self.generate_scan_reports(scan_id, scan_result)

            # Move to scan history
            self.scan_history[scan_id] = scan_result
            if scan_id in self.active_scans:
                del self.active_scans[scan_id]

            logger.info(
                f"Scan {scan_id} completed successfully with {len(scan_result.findings)} findings in {scan_result.scan_duration:.2f} seconds"
            )

        except Exception as e:
            logger.error(f"Scan {scan_id} failed with error: {e}")
            scan_result.status = ScanStatus.FAILED
            scan_result.end_time = datetime.now().isoformat()
            scan_result.error = str(e)

            # Try to cleanup any sandboxes on error
            if "sandboxes" in locals() and sandboxes:
                await self.cleanup_sandboxes(sandboxes)

    def _select_plugins(
        self, scan_type: ScanType, config: ScanConfig
    ) -> Dict[str, Any]:
        """Select appropriate plugins based on scan type and configuration"""
        all_plugins = self.plugin_manager.get_plugins()
        selected_plugins = {}

        # Filter plugins by scan type
        for plugin_name, plugin in all_plugins.items():
            if plugin.supports_scan_type(scan_type):
                # Check if plugin is enabled in config
                if config.enabled_plugins and plugin_name not in config.enabled_plugins:
                    continue

                # Check if plugin is explicitly disabled
                if config.disabled_plugins and plugin_name in config.disabled_plugins:
                    continue

                selected_plugins[plugin_name] = plugin

        return selected_plugins

    def _enrich_findings(
        self, findings: List[VulnerabilityFinding], plugin_name: str
    ) -> List[VulnerabilityFinding]:
        """Add metadata to findings from a plugin"""
        for finding in findings:
            finding.source = plugin_name
            finding.timestamp = datetime.now().isoformat()

            # Add any other metadata or context we want

        return findings

    def _process_findings(
        self, findings: List[VulnerabilityFinding]
    ) -> List[VulnerabilityFinding]:
        """Process and deduplicate findings"""
        # Use a simple set to track seen findings (in a real implementation, this would be more sophisticated)
        unique_findings = []
        seen = set()

        for finding in findings:
            # Create a simple key based on vulnerability type and location
            key = f"{finding.vulnerability_type}:{finding.location}"

            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)

        # Sort by severity
        return sorted(unique_findings, key=lambda f: f.severity.value, reverse=True)

    async def get_scan_status(self, scan_id: str) -> Optional[ScanResult]:
        """Get the status of a scan by ID"""
        # First check active scans
        if scan_id in self.active_scans:
            return self.active_scans[scan_id]

        # Then check scan history
        if scan_id in self.scan_history:
            return self.scan_history[scan_id]

        return None

    async def cancel_scan(self, scan_id: str) -> bool:
        """Cancel an in-progress scan"""
        if scan_id not in self.active_scans:
            return False

        scan_result = self.active_scans[scan_id]
        scan_result.status = ScanStatus.CANCELLED
        scan_result.end_time = datetime.now().isoformat()

        # Move to scan history
        self.scan_history[scan_id] = scan_result
        del self.active_scans[scan_id]

        logger.info(f"Scan {scan_id} cancelled")
        return True

    async def batch_scan(
        self,
        targets: List[Target],
        scan_type: ScanType,
        config: Optional[ScanConfig] = None,
    ) -> List[str]:
        """
        Start multiple scans in batch mode

        Args:
            targets: List of targets to scan
            scan_type: Type of scan to perform
            config: Additional scan configuration

        Returns:
            List of scan IDs
        """
        scan_ids = []

        for target in targets:
            scan_id = await self.start_scan(target, scan_type, config)
            scan_ids.append(scan_id)

        return scan_ids

    async def schedule_scan(
        self,
        target: Target,
        scan_type: ScanType,
        schedule: Dict[str, Any],
        config: Optional[ScanConfig] = None,
    ) -> str:
        """
        Schedule a scan to run at a specified time

        Args:
            target: Target to scan
            scan_type: Type of scan to perform
            schedule: Schedule information (cron expression, interval, etc.)
            config: Additional scan configuration

        Returns:
            Schedule ID
        """
        # This would integrate with an external scheduler in a real implementation
        # For now, just return a placeholder
        schedule_id = str(uuid.uuid4())
        logger.info(f"Scan scheduled for {target.identifier} with ID {schedule_id}")
        return schedule_id

    async def create_sandbox_for_plugin(
        self, plugin_name: str, plugin: Any
    ) -> Optional[str]:
        """
        Create an appropriate sandbox environment for a plugin

        Args:
            plugin_name: Name of the plugin
            plugin: The plugin instance

        Returns:
            Optional[str]: Sandbox ID if created, None otherwise
        """
        try:
            sandbox_options = {}

            # Configure based on plugin type
            if "slither" in plugin_name.lower():
                # Slither needs solc compiler
                sandbox_options["image"] = "trailofbits/eth-security-toolbox"
                sandbox_options["command"] = [
                    "tail",
                    "-f",
                    "/dev/null",
                ]  # Keep container running
            elif "mythril" in plugin_name.lower():
                # Mythril needs specific environment
                sandbox_options["image"] = "mythril/myth"
                sandbox_options["command"] = ["tail", "-f", "/dev/null"]
            elif "manticore" in plugin_name.lower():
                # Manticore needs Python and solc
                sandbox_options["image"] = "trailofbits/manticore"
                sandbox_options["command"] = ["tail", "-f", "/dev/null"]
            else:
                # Default for other plugins
                sandbox_options["image"] = "ethereum/solc:stable"
                sandbox_options["command"] = ["tail", "-f", "/dev/null"]

            # Create the sandbox
            sandbox_id = await self.sandbox_manager.create_sandbox(
                sandbox_type=SandboxType.DOCKER, options=sandbox_options
            )

            return sandbox_id
        except Exception as e:
            logger.error(f"Failed to create sandbox for plugin {plugin_name}: {e}")
            return None

    async def cleanup_sandboxes(self, sandboxes: Dict[str, str]) -> None:
        """
        Clean up sandboxes after scan completion or failure

        Args:
            sandboxes: Dictionary mapping plugin names to sandbox IDs
        """
        for plugin_name, sandbox_id in sandboxes.items():
            try:
                await self.sandbox_manager.destroy_sandbox(sandbox_id)
                logger.info(f"Cleaned up sandbox {sandbox_id} for plugin {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to clean up sandbox {sandbox_id}: {e}")

    async def generate_scan_reports(
        self, scan_id: str, scan_result: ScanResult
    ) -> List[str]:
        """
        Generate reports for a completed scan

        Args:
            scan_id: ID of the scan
            scan_result: Scan result with findings

        Returns:
            List[str]: Paths to generated reports
        """
        if not scan_result.findings:
            logger.info(f"No findings to report for scan {scan_id}")
            return []

        # Prepare report data
        report_data = {
            "scanner_version": "1.0.0",  # Would come from version tracking in production
            "scan_duration": getattr(scan_result, "scan_duration", 0),
            "plugins_used": [scan_result.current_plugin]
            if scan_result.current_plugin
            else [],
            "target": scan_result.target.to_dict(),
            "status": scan_result.status.value,
            "findings": [finding.to_dict() for finding in scan_result.findings],
        }

        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(
            os.getcwd(), self.config.get("report_directory", "reports")
        )
        os.makedirs(reports_dir, exist_ok=True)

        # Generate different report formats
        report_files = []
        base_filename = f"{reports_dir}/scan-{scan_id[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Generate JSON report (always generated)
        json_path = generate_report(report_data, f"{base_filename}", ReportFormat.JSON)
        report_files.append(json_path)

        # Generate HTML report if requested
        if (
            scan_result.config.report_formats
            and ReportFormat.HTML.value in scan_result.config.report_formats
        ):
            html_path = generate_report(
                report_data, f"{base_filename}", ReportFormat.HTML
            )
            report_files.append(html_path)

        # Generate Markdown report if requested
        if (
            scan_result.config.report_formats
            and ReportFormat.MARKDOWN.value in scan_result.config.report_formats
        ):
            md_path = generate_report(
                report_data, f"{base_filename}", ReportFormat.MARKDOWN
            )
            report_files.append(md_path)

        logger.info(f"Generated {len(report_files)} reports for scan {scan_id}")
        return report_files
