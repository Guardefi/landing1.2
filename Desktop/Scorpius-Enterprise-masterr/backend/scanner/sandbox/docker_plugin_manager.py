"""
Docker-based Plugin Manager for Scorpius Vulnerability Scanner

This module manages containerized security analysis plugins, ensuring
clean isolation and no dependency conflicts between tools.
"""

import json
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import docker
from core.models import Target, VulnerabilityFinding, VulnerabilityLevel

logger = logging.getLogger(__name__)


@dataclass
class ContainerPlugin:
    """Configuration for a containerized plugin"""

    name: str
    image: str
    command: str
    input_volume: str = "/workspace/input"
    output_volume: str = "/workspace/output"
    environment: Dict[str, str] = None
    timeout: int = 300  # 5 minutes default
    memory_limit: str = "1g"

    def __post_init__(self):
        if self.environment is None:
            self.environment = {}


class DockerPluginManager:
    """
    Manages containerized vulnerability scanning plugins
    """

    def __init__(self, docker_socket: str = None):
        """Initialize Docker plugin manager"""
        try:
            self.client = (
                docker.from_env()
                if not docker_socket
                else docker.DockerClient(base_url=docker_socket)
            )
            self.plugins = self._initialize_plugins()
            logger.info(
                f"Docker plugin manager initialized with {len(self.plugins)} plugins"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
            self.plugins = {}

    def _initialize_plugins(self) -> Dict[str, ContainerPlugin]:
        """Initialize available containerized plugins"""
        return {
            "slither": ContainerPlugin(
                name="slither",
                image="scorpius/slither:latest",
                command="slither /workspace/input/contract.sol --json /workspace/output/results.json",
                timeout=180,
                memory_limit="512m",
            ),
            "mythril": ContainerPlugin(
                name="mythril",
                image="scorpius/mythril:latest",
                command="myth analyze /workspace/input/contract.sol --output-json /workspace/output/results.json",
                timeout=300,
                memory_limit="1g",
            ),
            "manticore": ContainerPlugin(
                name="manticore",
                image="scorpius/manticore:latest",
                command="python3 /app/manticore_runner.py /workspace/input/contract.sol /workspace/output/results.json",
                timeout=600,
                memory_limit="2g",
            ),
            "mythx": ContainerPlugin(
                name="mythx",
                image="scorpius/mythx:latest",
                command="python3 /app/mythx_runner.py /workspace/input/contract.sol /workspace/output/results.json",
                environment={"MYTHX_API_KEY": os.getenv("MYTHX_API_KEY", "")},
                timeout=300,
                memory_limit="512m",
            ),
            "securify": ContainerPlugin(
                name="securify",
                image="scorpius/securify:latest",
                command="java -jar /app/securify.jar /workspace/input/contract.sol --output /workspace/output/results.json",
                timeout=240,
                memory_limit="1g",
            ),
        }

    async def scan_with_plugin(
        self, plugin_name: str, target: Target, source_code: str, **kwargs
    ) -> List[VulnerabilityFinding]:
        """
        Run vulnerability scan using a containerized plugin
        """
        if not self.client:
            logger.error("Docker client not available")
            return []

        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} not found")
            return []

        plugin = self.plugins[plugin_name]

        try:
            # Create temporary directories for input/output
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_dir = temp_path / "input"
                output_dir = temp_path / "output"
                input_dir.mkdir()
                output_dir.mkdir()

                # Write contract source code
                contract_file = input_dir / "contract.sol"
                with open(contract_file, "w") as f:
                    f.write(source_code)

                # Run containerized analysis
                results = await self._run_container(
                    plugin, input_dir, output_dir, target
                )

                # Parse results
                return self._parse_plugin_results(plugin_name, results, target)

        except Exception as e:
            logger.error(f"Error running plugin {plugin_name}: {e}")
            return []

    async def _run_container(
        self, plugin: ContainerPlugin, input_dir: Path, output_dir: Path, target: Target
    ) -> Dict[str, Any]:
        """Run analysis in Docker container"""

        try:
            # Prepare volumes
            volumes = {
                str(input_dir): {"bind": plugin.input_volume, "mode": "ro"},
                str(output_dir): {"bind": plugin.output_volume, "mode": "rw"},
            }

            # Check if image exists, build if necessary
            if not self._image_exists(plugin.image):
                logger.info(f"Building image {plugin.image}...")
                await self._build_plugin_image(plugin)

            # Run container
            logger.info(f"Running {plugin.name} analysis...")

            container = self.client.containers.run(
                image=plugin.image,
                command=plugin.command,
                volumes=volumes,
                environment=plugin.environment,
                mem_limit=plugin.memory_limit,
                detach=True,
                remove=True,
                working_dir="/workspace",
            )

            # Wait for completion with timeout
            result = container.wait(timeout=plugin.timeout)

            # Get container logs
            logs = container.logs().decode("utf-8")

            # Read results file
            results_file = output_dir / "results.json"
            if results_file.exists():
                with open(results_file) as f:
                    return json.load(f)
            else:
                logger.warning(f"No results file found for {plugin.name}")
                return {"logs": logs, "exit_code": result["StatusCode"]}

        except Exception as e:
            logger.error(f"Container execution failed: {e}")
            return {"error": str(e)}

    def _image_exists(self, image_name: str) -> bool:
        """Check if Docker image exists locally"""
        try:
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False
        except Exception as e:
            logger.error(f"Error checking image {image_name}: {e}")
            return False

    async def _build_plugin_image(self, plugin: ContainerPlugin):
        """Build Docker image for plugin"""
        dockerfile_path = Path(__file__).parent.parent / "docker" / plugin.name

        if not dockerfile_path.exists():
            logger.error(f"Dockerfile not found for {plugin.name}")
            return False

        try:
            logger.info(f"Building Docker image {plugin.image}...")

            # Build image
            image, logs = self.client.images.build(
                path=str(dockerfile_path), tag=plugin.image, rm=True, timeout=600
            )

            logger.info(f"Successfully built {plugin.image}")
            return True

        except Exception as e:
            logger.error(f"Failed to build image {plugin.image}: {e}")
            return False

    def _parse_plugin_results(
        self, plugin_name: str, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse plugin results into VulnerabilityFinding objects"""

        findings = []

        try:
            if "error" in results:
                logger.error(
                    f"{plugin_name} analysis failed: {
                        results['error']}"
                )
                return []

            # Handle different plugin output formats
            if plugin_name == "slither":
                findings.extend(self._parse_slither_results(results, target))
            elif plugin_name == "mythril":
                findings.extend(self._parse_mythril_results(results, target))
            elif plugin_name == "manticore":
                findings.extend(self._parse_manticore_results(results, target))
            elif plugin_name == "mythx":
                findings.extend(self._parse_mythx_results(results, target))
            elif plugin_name == "securify":
                findings.extend(self._parse_securify_results(results, target))
            else:
                logger.warning(f"Unknown plugin format: {plugin_name}")

        except Exception as e:
            logger.error(f"Error parsing {plugin_name} results: {e}")

        return findings

    def _parse_slither_results(
        self, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse Slither analysis results"""
        findings = []

        detectors = results.get("results", {}).get("detectors", [])

        for detector in detectors:
            # Map Slither impact to our severity levels
            impact_map = {
                "Critical": VulnerabilityLevel.CRITICAL,
                "High": VulnerabilityLevel.HIGH,
                "Medium": VulnerabilityLevel.MEDIUM,
                "Low": VulnerabilityLevel.LOW,
                "Informational": VulnerabilityLevel.INFO,
            }

            severity = impact_map.get(
                detector.get("impact", "Medium"), VulnerabilityLevel.MEDIUM
            )

            finding = VulnerabilityFinding(
                vulnerability_type=f"slither_{
                    detector.get(
                        'check', 'unknown')}",
                title=detector.get("description", "Slither Detection"),
                description=detector.get("markdown", ""),
                severity=severity,
                confidence=0.8,  # Slither is generally reliable
                location=f"Line {detector.get('first_markdown_element', '')}",
                source="slither",
                metadata={
                    "detector": detector.get("check"),
                    "impact": detector.get("impact"),
                    "confidence": detector.get("confidence"),
                    "elements": detector.get("elements", []),
                },
            )

            findings.append(finding)

        return findings

    def _parse_mythril_results(
        self, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse Mythril analysis results"""
        findings = []

        issues = results.get("issues", [])

        for issue in issues:
            severity_map = {
                "High": VulnerabilityLevel.HIGH,
                "Medium": VulnerabilityLevel.MEDIUM,
                "Low": VulnerabilityLevel.LOW,
            }

            severity = severity_map.get(
                issue.get("severity", "Medium"), VulnerabilityLevel.MEDIUM
            )

            finding = VulnerabilityFinding(
                vulnerability_type=f"mythril_{issue.get('swc-id', 'unknown')}",
                title=issue.get("title", "Mythril Detection"),
                description=issue.get("description", ""),
                severity=severity,
                confidence=0.7,
                location=f"PC: {issue.get('address', 'unknown')}",
                source="mythril",
                metadata={
                    "swc_id": issue.get("swc-id"),
                    "bytecode_address": issue.get("address"),
                    "function": issue.get("function"),
                    "type": issue.get("type"),
                },
            )

            findings.append(finding)

        return findings

    def _parse_manticore_results(
        self, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse Manticore analysis results"""
        findings = []

        vulnerabilities = results.get("vulnerabilities", [])

        for vuln in vulnerabilities:
            finding = VulnerabilityFinding(
                vulnerability_type=f"manticore_{vuln.get('type', 'unknown')}",
                title=vuln.get("name", "Manticore Detection"),
                description=vuln.get("description", ""),
                severity=VulnerabilityLevel.MEDIUM,  # Default to medium
                confidence=0.9,  # Manticore symbolic execution is very reliable
                location=vuln.get("location", "unknown"),
                source="manticore",
                metadata={
                    "type": vuln.get("type"),
                    "state_count": vuln.get("state_count"),
                    "execution_path": vuln.get("path"),
                },
            )

            findings.append(finding)

        return findings

    def _parse_mythx_results(
        self, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse MythX analysis results"""
        findings = []

        issues = results.get("issues", [])

        for issue in issues:
            severity_map = {
                "Critical": VulnerabilityLevel.CRITICAL,
                "High": VulnerabilityLevel.HIGH,
                "Medium": VulnerabilityLevel.MEDIUM,
                "Low": VulnerabilityLevel.LOW,
                "None": VulnerabilityLevel.INFO,
            }

            severity = severity_map.get(
                issue.get("severity", "Medium"), VulnerabilityLevel.MEDIUM
            )

            finding = VulnerabilityFinding(
                vulnerability_type=f"mythx_{issue.get('swcID', 'unknown')}",
                title=issue.get("title", "MythX Detection"),
                description=issue.get("description", ""),
                severity=severity,
                confidence=0.85,  # MythX combines multiple tools
                location=f"Line {
                    issue.get(
                        'sourceLocation',
                        {}).get(
                        'line',
                        'unknown')}",
                source="mythx",
                metadata={
                    "swc_id": issue.get("swcID"),
                    "swc_title": issue.get("swcTitle"),
                    "location": issue.get("sourceLocation"),
                },
            )

            findings.append(finding)

        return findings

    def _parse_securify_results(
        self, results: Dict[str, Any], target: Target
    ) -> List[VulnerabilityFinding]:
        """Parse Securify analysis results"""
        findings = []

        violations = results.get("violations", [])

        for violation in violations:
            finding = VulnerabilityFinding(
                vulnerability_type=f"securify_{
                    violation.get(
                        'type',
                        'unknown')}",
                title=violation.get("name", "Securify Detection"),
                description=violation.get("description", ""),
                severity=VulnerabilityLevel.MEDIUM,
                confidence=0.75,
                location=violation.get("location", "unknown"),
                source="securify",
                metadata={
                    "type": violation.get("type"),
                    "pattern": violation.get("pattern"),
                },
            )

            findings.append(finding)

        return findings

    async def scan_with_all_plugins(
        self,
        target: Target,
        source_code: str,
        selected_plugins: Optional[List[str]] = None,
    ) -> Dict[str, List[VulnerabilityFinding]]:
        """
        Run vulnerability scans with multiple containerized plugins
        """
        if not self.client:
            logger.error("Docker client not available")
            return {}

        plugins_to_run = selected_plugins or list(self.plugins.keys())
        results = {}

        # Run plugins in parallel
        tasks = []
        for plugin_name in plugins_to_run:
            if plugin_name in self.plugins:
                task = self.scan_with_plugin(plugin_name, target, source_code)
                tasks.append((plugin_name, task))

        # Wait for all tasks to complete
        for plugin_name, task in tasks:
            try:
                findings = await task
                results[plugin_name] = findings
                logger.info(
                    f"{plugin_name}: Found {
                        len(findings)} vulnerabilities"
                )
            except Exception as e:
                logger.error(f"Plugin {plugin_name} failed: {e}")
                results[plugin_name] = []

        return results

    def get_available_plugins(self) -> List[str]:
        """Get list of available containerized plugins"""
        return list(self.plugins.keys())

    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all plugins (image availability, etc.)"""
        status = {}

        for plugin_name, plugin in self.plugins.items():
            status[plugin_name] = {
                "image": plugin.image,
                "image_exists": self._image_exists(plugin.image),
                "timeout": plugin.timeout,
                "memory_limit": plugin.memory_limit,
            }

        return status

    async def build_all_images(self):
        """Build all plugin Docker images"""
        for plugin_name, plugin in self.plugins.items():
            if not self._image_exists(plugin.image):
                logger.info(f"Building {plugin_name} image...")
                await self._build_plugin_image(plugin)
            else:
                logger.info(f"{plugin_name} image already exists")

    def cleanup(self):
        """Cleanup Docker resources"""
        if self.client:
            try:
                # Clean up any stopped containers
                containers = self.client.containers.list(
                    all=True, filters={"label": "scorpius.plugin"}
                )
                for container in containers:
                    if container.status != "running":
                        container.remove()

                logger.info("Docker cleanup completed")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
