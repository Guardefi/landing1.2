"""
Enhanced Plugin Integration for Scorpius Vulnerability Scanner

This module provides enterprise-grade plugin integration with Docker support,
advanced configuration management, and simulation capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models import ScanConfig, Target, VulnerabilityFinding
from exploitation.simulation_engine import ExploitSimulationEngine, SimulationType
from sandbox.plugin_docker import DockerPluginManager

logger = logging.getLogger("scorpius.core.enhanced_plugin_manager")


@dataclass
class PluginCapabilities:
    """Describes the capabilities of a plugin"""

    static_analysis: bool = False
    dynamic_analysis: bool = False
    symbolic_execution: bool = False
    exploit_generation: bool = False
    simulation_support: bool = False
    supported_languages: List[str] = None
    vulnerability_categories: List[str] = None
    confidence_levels: List[str] = None

    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["solidity"]
        if self.vulnerability_categories is None:
            self.vulnerability_categories = []
        if self.confidence_levels is None:
            self.confidence_levels = ["low", "medium", "high"]


@dataclass
class PluginMetadata:
    """Metadata for a plugin"""

    name: str
    version: str
    author: str
    description: str
    docker_image: str
    capabilities: PluginCapabilities
    config_schema: Dict[str, Any] = None
    dependencies: List[str] = None
    resource_requirements: Dict[str, str] = None

    def __post_init__(self):
        if self.config_schema is None:
            self.config_schema = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.resource_requirements is None:
            self.resource_requirements = {"memory": "1g", "cpu": "1"}


class EnhancedPluginManager:
    """Enhanced plugin manager with Docker integration and simulation support"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the enhanced plugin manager

        Args:
            config: Configuration for the plugin manager
        """
        self.config = config or {}
        self.docker_manager = DockerPluginManager(self.config.get("docker", {}))
        self.simulation_engine = None  # Will be initialized when needed

        self.plugins = {}
        self.plugin_metadata = {}
        self.execution_history = {}

        # Load plugin registry
        self._load_plugin_registry()

        logger.info("Enhanced Plugin Manager initialized")

    def _load_plugin_registry(self) -> None:
        """Load plugin registry with metadata"""

        # Define plugin metadata
        plugin_registry = {
            "slither": PluginMetadata(
                name="slither",
                version="0.9.3",
                author="Crytic",
                description="Static analysis framework for Solidity",
                docker_image="scorpius/slither:latest",
                capabilities=PluginCapabilities(
                    static_analysis=True,
                    supported_languages=["solidity"],
                    vulnerability_categories=[
                        "reentrancy",
                        "integer_overflow",
                        "access_control",
                        "unchecked_calls",
                        "timestamp_dependence",
                    ],
                ),
                dependencies=["solc"],
                resource_requirements={"memory": "1g", "cpu": "1"},
            ),
            "mythril": PluginMetadata(
                name="mythril",
                version="0.23.15",
                author="ConsenSys",
                description="Security analysis tool for Ethereum smart contracts",
                docker_image="scorpius/mythril:latest",
                capabilities=PluginCapabilities(
                    static_analysis=True,
                    symbolic_execution=True,
                    exploit_generation=True,
                    supported_languages=["solidity"],
                    vulnerability_categories=[
                        "reentrancy",
                        "integer_overflow",
                        "unchecked_calls",
                        "delegatecall",
                        "state_access_after_external_call",
                    ],
                ),
                dependencies=["solc", "z3"],
                resource_requirements={"memory": "2g", "cpu": "2"},
            ),
            "manticore": PluginMetadata(
                name="manticore",
                version="0.3.7",
                author="Trail of Bits",
                description="Symbolic execution tool for analysis of smart contracts",
                docker_image="scorpius/manticore:latest",
                capabilities=PluginCapabilities(
                    dynamic_analysis=True,
                    symbolic_execution=True,
                    simulation_support=True,
                    supported_languages=["solidity", "bytecode"],
                    vulnerability_categories=[
                        "reentrancy",
                        "integer_overflow",
                        "assertion_failure",
                        "unhandled_exception",
                        "external_call_failure",
                    ],
                ),
                dependencies=["solc", "z3"],
                resource_requirements={"memory": "4g", "cpu": "2"},
            ),
            "mythx": PluginMetadata(
                name="mythx",
                version="1.6.0",
                author="ConsenSys",
                description="Professional security analysis service",
                docker_image="scorpius/mythx:latest",
                capabilities=PluginCapabilities(
                    static_analysis=True,
                    dynamic_analysis=True,
                    supported_languages=["solidity"],
                    vulnerability_categories=[
                        "reentrancy",
                        "integer_overflow",
                        "access_control",
                        "unchecked_calls",
                        "front_running",
                        "timestamp_dependence",
                    ],
                ),
                dependencies=["mythx_api_key"],
                resource_requirements={"memory": "1g", "cpu": "1"},
            ),
        }

        self.plugin_metadata = plugin_registry
        logger.info(f"Loaded {len(plugin_registry)} plugins into registry")

    async def initialize_plugins(
        self, plugin_names: List[str] = None
    ) -> Dict[str, bool]:
        """
        Initialize specified plugins or all available plugins

        Args:
            plugin_names: List of plugin names to initialize. If None, initializes all.

        Returns:
            Dict mapping plugin names to initialization success status
        """
        if plugin_names is None:
            plugin_names = list(self.plugin_metadata.keys())

        results = {}

        # First, build Docker images for the plugins
        build_results = await self.docker_manager.build_plugin_images(plugin_names)

        for plugin_name in plugin_names:
            if plugin_name not in self.plugin_metadata:
                logger.warning(f"Unknown plugin: {plugin_name}")
                results[plugin_name] = False
                continue

            # Check if Docker image was built successfully
            if not build_results.get(plugin_name, False):
                logger.error(f"Failed to build Docker image for {plugin_name}")
                results[plugin_name] = False
                continue

            # Create container for the plugin
            container_id = await self.docker_manager.create_plugin_container(
                plugin_name
            )

            if container_id:
                self.plugins[plugin_name] = {
                    "container_id": container_id,
                    "metadata": self.plugin_metadata[plugin_name],
                    "status": "ready",
                }
                results[plugin_name] = True
                logger.info(f"Successfully initialized plugin: {plugin_name}")
            else:
                results[plugin_name] = False
                logger.error(f"Failed to initialize plugin: {plugin_name}")

        return results

    async def execute_plugin(
        self, plugin_name: str, target: Target, config: ScanConfig
    ) -> Dict[str, Any]:
        """
        Execute a plugin against a target

        Args:
            plugin_name: Name of the plugin to execute
            target: Target to analyze
            config: Scan configuration

        Returns:
            Execution results
        """
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} is not initialized")

        logger.info(
            f"Executing plugin {plugin_name} on target {
                target.identifier}"
        )

        try:
            # Prepare target file
            target_file = await self._prepare_target_file(target)

            # Create output directory
            output_dir = (
                Path(self.config.get("output_directory", "results")) / plugin_name
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            # Execute plugin in Docker container
            result = await self.docker_manager.execute_plugin(
                plugin_name,
                target_file,
                str(output_dir),
                config.custom_options.get("additional_args", []),
            )

            # Parse results
            findings = await self._parse_plugin_results(
                plugin_name, result, str(output_dir)
            )

            # Store execution history
            execution_id = (
                f"{plugin_name}_{target.identifier}_{len(self.execution_history)}"
            )
            self.execution_history[execution_id] = {
                "plugin": plugin_name,
                "target": target.identifier,
                "timestamp": asyncio.get_event_loop().time(),
                "success": result["success"],
                "findings_count": len(findings),
                "execution_time": result.get("execution_time", 0),
            }

            return {
                "success": result["success"],
                "findings": findings,
                "raw_output": result,
                "execution_id": execution_id,
            }

        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {e}")
            return {"success": False, "error": str(e), "findings": []}

    async def run_simulation(
        self,
        plugin_name: str,
        vulnerability: VulnerabilityFinding,
        target: Target,
        simulation_type: SimulationType = None,
    ) -> str:
        """
        Run exploit simulation for a vulnerability found by a plugin

        Args:
            plugin_name: Name of the plugin that found the vulnerability
            vulnerability: Vulnerability to simulate
            target: Target system
            simulation_type: Type of simulation to run

        Returns:
            Simulation ID for tracking
        """
        if not self.simulation_engine:
            # Initialize simulation engine with sandbox manager
            from sandbox.manager import SandboxManager

            sandbox_manager = SandboxManager(self.config.get("sandbox", {}))
            self.simulation_engine = ExploitSimulationEngine(
                sandbox_manager, self.config.get("simulation", {})
            )

        # Check if plugin supports simulation
        plugin_metadata = self.plugin_metadata.get(plugin_name)
        if not plugin_metadata or not plugin_metadata.capabilities.simulation_support:
            logger.warning(f"Plugin {plugin_name} does not support simulation")

        # Default simulation type based on vulnerability category
        if simulation_type is None:
            simulation_type = self._get_default_simulation_type(vulnerability.category)

        return await self.simulation_engine.simulate_exploit(
            vulnerability, simulation_type, target
        )

    def _get_default_simulation_type(
        self, vulnerability_category: str
    ) -> SimulationType:
        """Get default simulation type for a vulnerability category"""
        simulation_map = {
            "reentrancy": SimulationType.PROOF_OF_CONCEPT,
            "integer_overflow": SimulationType.PROOF_OF_CONCEPT,
            "access_control": SimulationType.IMPACT_ASSESSMENT,
            "front_running": SimulationType.ATTACK_CHAIN,
            "flash_loan": SimulationType.FULL_EXPLOIT,
        }

        return simulation_map.get(
            vulnerability_category.lower(), SimulationType.PROOF_OF_CONCEPT
        )

    async def _prepare_target_file(self, target: Target) -> str:
        """
        Prepare target file for analysis

        Args:
            target: Target to prepare

        Returns:
            Path to prepared target file
        """
        if target.type == "file":
            return target.path
        elif target.type == "source_code":
            # Save source code to temporary file
            temp_dir = Path("/tmp/scorpius_targets")
            temp_dir.mkdir(exist_ok=True)

            target_file = temp_dir / f"{target.identifier}.sol"
            with open(target_file, "w") as f:
                f.write(target.content)

            return str(target_file)
        elif target.type == "contract_address":
            # For deployed contracts, we might need to fetch source code
            # This is a placeholder - implementation would depend on how
            # source code is obtained (Etherscan API, etc.)
            raise NotImplementedError("Contract address analysis not yet implemented")
        else:
            raise ValueError(f"Unsupported target type: {target.type}")

    async def _parse_plugin_results(
        self, plugin_name: str, execution_result: Dict[str, Any], output_dir: str
    ) -> List[VulnerabilityFinding]:
        """
        Parse plugin execution results into vulnerability findings

        Args:
            plugin_name: Name of the plugin
            execution_result: Raw execution result
            output_dir: Directory containing output files

        Returns:
            List of vulnerability findings
        """
        findings = []

        try:
            # Look for plugin-specific output files
            output_files = list(Path(output_dir).glob("**/*.json"))

            for output_file in output_files:
                with open(output_file, "r") as f:
                    data = json.load(f)

                # Parse based on plugin type
                if plugin_name == "slither":
                    findings.extend(self._parse_slither_results(data))
                elif plugin_name == "mythril":
                    findings.extend(self._parse_mythril_results(data))
                elif plugin_name == "manticore":
                    findings.extend(self._parse_manticore_results(data))
                elif plugin_name == "mythx":
                    findings.extend(self._parse_mythx_results(data))

        except Exception as e:
            logger.error(f"Error parsing results for {plugin_name}: {e}")

        return findings

    def _parse_slither_results(
        self, data: Dict[str, Any]
    ) -> List[VulnerabilityFinding]:
        """Parse Slither results into vulnerability findings"""
        findings = []

        for detector_result in data.get("results", {}).get("detectors", []):
            finding = VulnerabilityFinding(
                id=f"slither_{len(findings)}",
                category=detector_result.get("check", "unknown"),
                title=detector_result.get("check", "Slither Detection"),
                description=detector_result.get("description", ""),
                severity=self._map_slither_impact(detector_result.get("impact", "Low")),
                confidence=self._map_slither_confidence(
                    detector_result.get("confidence", "Low")
                ),
                location=self._extract_slither_location(detector_result),
                plugin="slither",
                raw_data=detector_result,
            )
            findings.append(finding)

        return findings

    def _parse_mythril_results(
        self, data: Dict[str, Any]
    ) -> List[VulnerabilityFinding]:
        """Parse Mythril results into vulnerability findings"""
        findings = []

        for issue in data.get("issues", []):
            finding = VulnerabilityFinding(
                id=f"mythril_{len(findings)}",
                category=issue.get("swc-id", "unknown"),
                title=issue.get("title", "Mythril Detection"),
                description=issue.get("description", ""),
                severity=self._map_mythril_severity(issue.get("severity", "Low")),
                confidence=0.8,  # Mythril generally has high confidence
                location={
                    "line": issue.get("lineno", 0),
                    "filename": issue.get("filename", "unknown"),
                },
                plugin="mythril",
                raw_data=issue,
            )
            findings.append(finding)

        return findings

    def _parse_manticore_results(
        self, data: Dict[str, Any]
    ) -> List[VulnerabilityFinding]:
        """Parse Manticore results into vulnerability findings"""
        findings = []

        # Manticore output format varies, this is a basic implementation
        for result in data.get("results", []):
            finding = VulnerabilityFinding(
                id=f"manticore_{len(findings)}",
                category=result.get("type", "unknown"),
                title=f"Manticore: {result.get('type', 'Detection')}",
                description=result.get("description", ""),
                severity="medium",  # Default severity
                confidence=0.7,
                location=result.get("location", {}),
                plugin="manticore",
                raw_data=result,
            )
            findings.append(finding)

        return findings

    def _parse_mythx_results(self, data: Dict[str, Any]) -> List[VulnerabilityFinding]:
        """Parse MythX results into vulnerability findings"""
        findings = []

        for issue in data.get("issues", []):
            finding = VulnerabilityFinding(
                id=f"mythx_{len(findings)}",
                category=issue.get("swcID", "unknown"),
                title=issue.get("swcTitle", "MythX Detection"),
                description=issue.get("description", ""),
                severity=self._map_mythx_severity(issue.get("severity", "Low")),
                confidence=0.9,  # MythX generally has high confidence
                location={
                    "line": issue.get("sourceMap", {}).get("line", 0),
                    "filename": issue.get("sourceMap", {}).get("filename", "unknown"),
                },
                plugin="mythx",
                raw_data=issue,
            )
            findings.append(finding)

        return findings

    def _map_slither_impact(self, impact: str) -> str:
        """Map Slither impact levels to our severity levels"""
        mapping = {
            "High": "high",
            "Medium": "medium",
            "Low": "low",
            "Informational": "info",
            "Optimization": "info",
        }
        return mapping.get(impact, "low")

    def _map_slither_confidence(self, confidence: str) -> float:
        """Map Slither confidence levels to numeric values"""
        mapping = {"High": 0.9, "Medium": 0.7, "Low": 0.4}
        return mapping.get(confidence, 0.5)

    def _map_mythril_severity(self, severity: str) -> str:
        """Map Mythril severity levels to our severity levels"""
        mapping = {"High": "high", "Medium": "medium", "Low": "low"}
        return mapping.get(severity, "low")

    def _map_mythx_severity(self, severity: str) -> str:
        """Map MythX severity levels to our severity levels"""
        mapping = {"High": "high", "Medium": "medium", "Low": "low"}
        return mapping.get(severity, "low")

    def _extract_slither_location(
        self, detector_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract location information from Slither results"""
        elements = detector_result.get("elements", [])
        if elements:
            first_element = elements[0]
            return {
                "line": first_element.get("source_mapping", {}).get("lines", [0])[0],
                "filename": first_element.get("source_mapping", {}).get(
                    "filename_absolute", "unknown"
                ),
            }
        return {}

    async def cleanup(self) -> None:
        """Clean up all plugin resources"""
        await self.docker_manager.cleanup_all_containers()
        logger.info("All plugin resources cleaned up")

    def get_plugin_capabilities(self, plugin_name: str) -> Optional[PluginCapabilities]:
        """Get capabilities of a specific plugin"""
        metadata = self.plugin_metadata.get(plugin_name)
        return metadata.capabilities if metadata else None

    def list_plugins(self) -> List[str]:
        """Get list of available plugins"""
        return list(self.plugin_metadata.keys())

    def get_execution_history(self) -> Dict[str, Any]:
        """Get plugin execution history"""
        return self.execution_history.copy()
