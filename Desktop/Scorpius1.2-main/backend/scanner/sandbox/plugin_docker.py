"""
Enhanced Docker Plugin Manager for Scorpius Vulnerability Scanner

This module provides enterprise-grade Docker-based plugin execution with
specialized containers for different types of security analysis tools.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from sandbox.docker import DockerSandbox

logger = logging.getLogger("scorpius.sandbox.plugin_docker")


class DockerPluginManager:
    """Manager for Docker-based plugin execution"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Docker plugin manager

        Args:
            config: Configuration for Docker plugin management
        """
        self.config = config or {}
        self.docker_sandbox = DockerSandbox(self.config.get("docker", {}))
        self.plugin_containers = {}
        self.image_registry = self._load_image_registry()

        # Plugin-specific configurations
        self.plugin_configs = {
            "slither": {
                "image": "scorpius/slither:latest",
                "build_context": "docker/slither",
                "timeout": 300,
                "memory": "1g",
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
            "mythril": {
                "image": "scorpius/mythril:latest",
                "build_context": "docker/mythril",
                "timeout": 600,
                "memory": "2g",
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
            "manticore": {
                "image": "scorpius/manticore:latest",
                "build_context": "docker/manticore",
                "timeout": 900,
                "memory": "4g",
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
            "mythx": {
                "image": "scorpius/mythx:latest",
                "build_context": "docker/mythx",
                "timeout": 1200,
                "memory": "1g",
                "environment": {"MYTHX_API_KEY": "${MYTHX_API_KEY}"},
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
            "oyente": {
                "image": "scorpius/oyente:latest",
                "build_context": "docker/oyente",
                "timeout": 300,
                "memory": "1g",
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
            "securify": {
                "image": "scorpius/securify:latest",
                "build_context": "docker/securify",
                "timeout": 600,
                "memory": "2g",
                "volumes": {
                    "/contracts": "/workspace/contracts",
                    "/reports": "/workspace/reports",
                },
            },
        }

        logger.info("Docker Plugin Manager initialized")

    def _load_image_registry(self) -> Dict[str, str]:
        """Load Docker image registry configuration"""
        return {
            "slither": "scorpius/slither:latest",
            "mythril": "scorpius/mythril:latest",
            "manticore": "scorpius/manticore:latest",
            "mythx": "scorpius/mythx:latest",
            "oyente": "scorpius/oyente:latest",
            "securify": "scorpius/securify:latest",
            "ethereum-sim": "scorpius/ethereum-sim:latest",
            "defi-sim": "scorpius/defi-sim:latest",
        }

    async def build_plugin_images(self, plugins: List[str] = None) -> Dict[str, bool]:
        """
        Build Docker images for specified plugins

        Args:
            plugins: List of plugin names to build images for. If None, builds all.

        Returns:
            Dict mapping plugin names to build success status
        """
        if plugins is None:
            plugins = list(self.plugin_configs.keys())

        results = {}

        for plugin in plugins:
            if plugin not in self.plugin_configs:
                logger.warning(f"Unknown plugin: {plugin}")
                results[plugin] = False
                continue

            config = self.plugin_configs[plugin]
            build_context = Path(config["build_context"])

            if not build_context.exists():
                logger.error(f"Build context not found for {plugin}: {build_context}")
                results[plugin] = False
                continue

            success = await self._build_image(
                plugin, config["image"], str(build_context)
            )
            results[plugin] = success

        return results

    async def _build_image(
        self, plugin_name: str, image_tag: str, build_context: str
    ) -> bool:
        """
        Build a Docker image for a plugin

        Args:
            plugin_name: Name of the plugin
            image_tag: Docker image tag
            build_context: Path to build context

        Returns:
            True if build was successful, False otherwise
        """
        try:
            logger.info(f"Building Docker image for {plugin_name}: {image_tag}")

            # Prepare build command
            build_cmd = [
                "docker",
                "build",
                "-t",
                image_tag,
                "--label",
                f"scorpius.plugin={plugin_name}",
                "--label",
                f"scorpius.version={self._get_version()}",
                build_context,
            ]

            # Execute build
            proc = await asyncio.create_subprocess_exec(
                *build_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info(f"Successfully built image for {plugin_name}")
                return True
            else:
                logger.error(
                    f"Failed to build image for {plugin_name}: {stderr.decode()}"
                )
                return False

        except Exception as e:
            logger.error(f"Error building image for {plugin_name}: {e}")
            return False

    async def create_plugin_container(
        self, plugin_name: str, options: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Create a container for a specific plugin

        Args:
            plugin_name: Name of the plugin
            options: Additional options for container creation

        Returns:
            Container ID if successful, None otherwise
        """
        if plugin_name not in self.plugin_configs:
            logger.error(f"Unknown plugin: {plugin_name}")
            return None

        config = self.plugin_configs[plugin_name].copy()

        # Override config with provided options
        if options:
            config.update(options)

        # Ensure image exists
        image = config["image"]
        if not await self._ensure_image_available(image):
            logger.error(f"Image not available for {plugin_name}: {image}")
            return None

        try:
            # Prepare container creation options
            container_options = {
                "image": image,
                "command": config.get("command", ["tail", "-f", "/dev/null"]),
                "volumes": config.get("volumes", {}),
                "environment": config.get("environment", {}),
                "memory": config.get("memory", "1g"),
                "timeout": config.get("timeout", 300),
                "network_mode": config.get("network_mode", "none"),
                "read_only": config.get("read_only", False),
            }

            # Create container using docker sandbox
            container_id = await self.docker_sandbox.create_container(
                **container_options
            )

            if container_id:
                self.plugin_containers[plugin_name] = container_id
                logger.info(f"Created container for {plugin_name}: {container_id}")
                return container_id
            else:
                logger.error(f"Failed to create container for {plugin_name}")
                return None

        except Exception as e:
            logger.error(f"Error creating container for {plugin_name}: {e}")
            return None

    async def execute_plugin(
        self,
        plugin_name: str,
        target_file: str,
        output_dir: str,
        additional_args: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a plugin in its dedicated container

        Args:
            plugin_name: Name of the plugin to execute
            target_file: Path to target file to analyze
            output_dir: Directory to store output
            additional_args: Additional arguments for the plugin

        Returns:
            Execution result with output, success status, and artifacts
        """
        if plugin_name not in self.plugin_containers:
            # Create container if it doesn't exist
            container_id = await self.create_plugin_container(plugin_name)
            if not container_id:
                return {
                    "success": False,
                    "error": f"Failed to create container for {plugin_name}",
                    "stdout": "",
                    "stderr": "",
                }

        container_id = self.plugin_containers[plugin_name]

        try:
            # Copy target file to container
            await self._copy_file_to_container(
                container_id, target_file, "/workspace/contracts/"
            )

            # Prepare execution command based on plugin type
            exec_cmd = self._get_plugin_command(
                plugin_name, os.path.basename(target_file), additional_args or []
            )

            # Execute plugin
            result = await self.docker_sandbox.execute_in_container(
                container_id,
                exec_cmd,
                timeout=self.plugin_configs[plugin_name]["timeout"],
            )

            # Copy results back
            await self._copy_results_from_container(
                container_id, output_dir, plugin_name
            )

            return result

        except Exception as e:
            logger.error(f"Error executing {plugin_name}: {e}")
            return {"success": False, "error": str(e), "stdout": "", "stderr": ""}

    def _get_plugin_command(
        self, plugin_name: str, target_file: str, additional_args: List[str]
    ) -> List[str]:
        """
        Get execution command for a specific plugin

        Args:
            plugin_name: Name of the plugin
            target_file: Target file to analyze
            additional_args: Additional arguments

        Returns:
            Command as list of strings
        """
        commands = {
            "slither": [
                "slither",
                f"/workspace/contracts/{target_file}",
                "--json",
                "/workspace/reports/slither_output.json",
                "--print",
                "all",
            ]
            + additional_args,
            "mythril": [
                "myth",
                "analyze",
                f"/workspace/contracts/{target_file}",
                "--execution-timeout",
                "300",
                "--output",
                "json",
                "--outfile",
                "/workspace/reports/mythril_output.json",
            ]
            + additional_args,
            "manticore": [
                "manticore",
                f"/workspace/contracts/{target_file}",
                "--workspace",
                "/workspace/reports/manticore",
                "--timeout",
                "600",
            ]
            + additional_args,
            "mythx": [
                "mythx",
                "analyze",
                f"/workspace/contracts/{target_file}",
                "--format",
                "json",
                "--output",
                "/workspace/reports/mythx_output.json",
            ]
            + additional_args,
            "oyente": [
                "python",
                "/oyente/oyente.py",
                "-s",
                f"/workspace/contracts/{target_file}",
                "-j",
            ]
            + additional_args,
            "securify": [
                "java",
                "-Xmx1024m",
                "-jar",
                "/securify/securify.jar",
                "-fs",
                f"/workspace/contracts/{target_file}",
                "-o",
                "/workspace/reports/",
            ]
            + additional_args,
        }

        return commands.get(plugin_name, ["echo", f"Unknown plugin: {plugin_name}"])

    async def _ensure_image_available(self, image: str) -> bool:
        """Ensure Docker image is available (pull if necessary)"""
        try:
            # Check if image exists locally
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "images",
                "-q",
                image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()

            if stdout.strip():
                return True  # Image exists locally

            # Pull image if not found locally
            logger.info(f"Pulling Docker image: {image}")
            return await self.docker_sandbox.pull_image(image)

        except Exception as e:
            logger.error(f"Error checking image availability: {e}")
            return False

    async def _copy_file_to_container(
        self, container_id: str, src_path: str, dest_dir: str
    ) -> bool:
        """Copy file from host to container"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "cp",
                src_path,
                f"{container_id}:{dest_dir}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode == 0:
                return True
            else:
                logger.error(f"Failed to copy file to container: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error copying file to container: {e}")
            return False

    async def _copy_results_from_container(
        self, container_id: str, output_dir: str, plugin_name: str
    ) -> bool:
        """Copy results from container to host"""
        try:
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Copy entire reports directory
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "cp",
                f"{container_id}:/workspace/reports/",
                f"{output_dir}/{plugin_name}_results/",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode == 0:
                return True
            else:
                logger.warning(
                    f"Failed to copy results from container: {stderr.decode()}"
                )
                return False

        except Exception as e:
            logger.error(f"Error copying results from container: {e}")
            return False

    async def cleanup_plugin_container(self, plugin_name: str) -> bool:
        """
        Clean up container for a specific plugin

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if cleanup was successful, False otherwise
        """
        if plugin_name not in self.plugin_containers:
            return True  # Already cleaned up

        container_id = self.plugin_containers[plugin_name]

        try:
            # Stop and remove container
            await asyncio.create_subprocess_exec(
                "docker",
                "stop",
                container_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            await asyncio.create_subprocess_exec(
                "docker",
                "rm",
                container_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            del self.plugin_containers[plugin_name]
            logger.info(f"Cleaned up container for {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error cleaning up container for {plugin_name}: {e}")
            return False

    async def cleanup_all_containers(self) -> None:
        """Clean up all plugin containers"""
        for plugin_name in list(self.plugin_containers.keys()):
            await self.cleanup_plugin_container(plugin_name)

    def _get_version(self) -> str:
        """Get Scorpius version"""
        return "1.0.0"  # This should be read from a version file

    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get status of a plugin container

        Args:
            plugin_name: Name of the plugin

        Returns:
            Status information
        """
        if plugin_name not in self.plugin_containers:
            return {"status": "not_created", "container_id": None}

        container_id = self.plugin_containers[plugin_name]

        # This would typically check actual container status
        return {
            "status": "running",
            "container_id": container_id,
            "config": self.plugin_configs.get(plugin_name, {}),
        }

    def list_available_plugins(self) -> List[str]:
        """Get list of available plugins"""
        return list(self.plugin_configs.keys())
