"""Docker sandbox implementation for Scorpius Vulnerability Scanner

This module provides Docker-based sandboxing capabilities for safely executing
potentially dangerous code during vulnerability analysis, exploit testing, or
dynamic analysis of smart contracts.
"""

import asyncio
import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("scorpius.sandbox.docker")


class DockerSandbox:
    """Docker-based sandbox for secure execution of code and tools"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Docker sandbox

        Args:
            config: Configuration options for the sandbox
        """
        self.config = config or {}
        self.active_containers = {}

        # Default settings
        self.default_timeout = self.config.get("default_timeout", 300)  # 5 minutes
        self.max_memory = self.config.get("max_memory", "1g")
        self.network_mode = self.config.get("network_mode", "none")
        self.default_image = self.config.get("default_image", "ethereum/solc:stable")

        # Security settings
        self.read_only = self.config.get("read_only", True)
        self.no_new_privileges = self.config.get("no_new_privileges", True)
        self.seccomp_profile = self.config.get(
            "seccomp_profile", "/etc/docker/seccomp.json"
        )

        logger.info("Docker sandbox initialized")

    async def check_docker_available(self) -> bool:
        """Check if Docker is available on the system

        Returns:
            bool: True if Docker is available, False otherwise
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info("Docker is available")
                return True
            else:
                logger.error(
                    f"Docker is not available: {
                        stderr.decode() if stderr else 'Unknown error'}"
                )
                return False
        except Exception as e:
            logger.error(f"Failed to check Docker availability: {e}")
            return False

    async def pull_image(self, image: str) -> bool:
        """Pull a Docker image

        Args:
            image: Docker image to pull

        Returns:
            bool: True if image was pulled successfully, False otherwise
        """
        try:
            logger.info(f"Pulling Docker image: {image}")
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "pull",
                image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info(f"Docker image pulled: {image}")
                return True
            else:
                logger.error(
                    f"Failed to pull Docker image {image}: {
                        stderr.decode() if stderr else 'Unknown error'}"
                )
                return False

        except Exception as e:
            logger.error(f"Error pulling Docker image {image}: {e}")
            return False

    async def run_container(
        self,
        image: str = None,
        command: List[str] = None,
        volumes: Dict[str, str] = None,
        env: Dict[str, str] = None,
        timeout: int = None,
        capture_output: bool = True,
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """Run a command in a Docker container

        Args:
            image: Docker image to use
            command: Command to run in the container
            volumes: Dictionary of volume mappings (host_path: container_path)
            env: Dictionary of environment variables
            timeout: Timeout in seconds
            capture_output: Whether to capture and return output

        Returns:
            Tuple containing:
                - Success flag (bool)
                - Container ID (str)
                - stdout (str or None if capture_output is False)
                - stderr (str or None if capture_output is False)
        """
        if not image:
            image = self.default_image

        if not command:
            command = ["echo", "Container started"]

        if timeout is None:
            timeout = self.default_timeout

        # Create a unique container name
        container_name = f"scorpius-{uuid.uuid4().hex[:8]}"

        try:
            # Ensure the image is available
            if not await self._check_image_exists(image):
                if not await self.pull_image(image):
                    return False, "", "Failed to pull image", None

            # Build the base docker command
            docker_cmd = ["docker", "run"]

            # Add container name
            docker_cmd.extend(["--name", container_name])

            # Add security options
            if self.read_only:
                docker_cmd.append("--read-only")

            if self.no_new_privileges:
                docker_cmd.append("--security-opt=no-new-privileges:true")

            if self.seccomp_profile and os.path.exists(self.seccomp_profile):
                docker_cmd.extend(["--security-opt", f"seccomp={self.seccomp_profile}"])

            # Set resource limits
            docker_cmd.extend(["--memory", self.max_memory])
            docker_cmd.extend(["--network", self.network_mode])
            docker_cmd.extend(["--memory-swap", self.max_memory])  # Disable swap
            docker_cmd.extend(["--cpus", "1"])  # Limit to 1 CPU

            # Add volumes
            if volumes:
                for host_path, container_path in volumes.items():
                    # Ensure the host path exists
                    if not os.path.exists(host_path):
                        logger.warning(
                            f"Host path {host_path} does not exist, skipping volume mount"
                        )
                        continue
                    docker_cmd.extend(["--volume", f"{host_path}:{container_path}"])

            # Add environment variables
            if env:
                for key, value in env.items():
                    docker_cmd.extend(["--env", f"{key}={value}"])

            # Run in detached mode if we're not capturing output
            if not capture_output:
                docker_cmd.append("-d")

            # Add cleanup flag
            docker_cmd.append("--rm")

            # Add timeout
            docker_cmd.extend(["--stop-timeout", str(timeout)])

            # Add the image
            docker_cmd.append(image)

            # Add the command
            docker_cmd.extend(command)

            logger.debug(f"Running Docker command: {' '.join(docker_cmd)}")

            # Run the container
            if capture_output:
                # Run synchronously and capture output
                proc = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                stdout_str = stdout.decode() if stdout else ""
                stderr_str = stderr.decode() if stderr else ""

                success = proc.returncode == 0
                if not success:
                    logger.error(
                        f"Container {container_name} exited with non-zero code: {proc.returncode}"
                    )
                    logger.error(f"stderr: {stderr_str}")

                return success, container_name, stdout_str, stderr_str
            else:
                # Run async without capturing output
                proc = await asyncio.create_subprocess_exec(*docker_cmd)
                self.active_containers[container_name] = proc
                return True, container_name, None, None

        except Exception as e:
            logger.error(f"Error running Docker container: {e}")
            return False, "", None, str(e)

    async def _check_image_exists(self, image: str) -> bool:
        """Check if a Docker image exists locally

        Args:
            image: Docker image to check

        Returns:
            bool: True if the image exists locally, False otherwise
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "image",
                "inspect",
                image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def stop_container(self, container_id: str) -> bool:
        """Stop a running container

        Args:
            container_id: ID of the container to stop

        Returns:
            bool: True if container was stopped successfully, False otherwise
        """
        try:
            logger.info(f"Stopping container: {container_id}")
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "stop",
                container_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info(f"Container stopped: {container_id}")
                if container_id in self.active_containers:
                    del self.active_containers[container_id]
                return True
            else:
                logger.error(
                    f"Failed to stop container {container_id}: {
                        stderr.decode() if stderr else 'Unknown error'}"
                )
                return False

        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            return False

    async def execute_in_container(
        self, container_id: str, command: List[str]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Execute a command in a running container

        Args:
            container_id: ID of the container
            command: Command to execute

        Returns:
            Tuple containing:
                - Success flag (bool)
                - stdout (str or None)
                - stderr (str or None)
        """
        try:
            docker_cmd = ["docker", "exec", container_id]
            docker_cmd.extend(command)

            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""

            success = proc.returncode == 0
            if not success:
                logger.error(
                    f"Command execution in container {container_id} failed: {stderr_str}"
                )

            return success, stdout_str, stderr_str

        except Exception as e:
            logger.error(f"Error executing command in container {container_id}: {e}")
            return False, None, str(e)

    async def copy_file_to_container(
        self, container_id: str, local_path: str, container_path: str
    ) -> bool:
        """Copy a file from the host to a container

        Args:
            container_id: ID of the container
            local_path: Path on the host
            container_path: Path in the container

        Returns:
            bool: True if copy was successful, False otherwise
        """
        try:
            # Ensure the local file exists
            if not os.path.exists(local_path):
                logger.error(f"Local file {local_path} does not exist")
                return False

            proc = await asyncio.create_subprocess_exec(
                "docker",
                "cp",
                local_path,
                f"{container_id}:{container_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.debug(
                    f"File copied to container: {local_path} -> {container_id}:{container_path}"
                )
                return True
            else:
                logger.error(
                    f"Failed to copy file to container: {
                        stderr.decode() if stderr else 'Unknown error'}"
                )
                return False

        except Exception as e:
            logger.error(f"Error copying file to container: {e}")
            return False

    async def copy_file_from_container(
        self, container_id: str, container_path: str, local_path: str
    ) -> bool:
        """Copy a file from a container to the host

        Args:
            container_id: ID of the container
            container_path: Path in the container
            local_path: Path on the host

        Returns:
            bool: True if copy was successful, False otherwise
        """
        try:
            # Ensure the directory exists
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)

            proc = await asyncio.create_subprocess_exec(
                "docker",
                "cp",
                f"{container_id}:{container_path}",
                local_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.debug(
                    f"File copied from container: {container_id}:{container_path} -> {local_path}"
                )
                return True
            else:
                logger.error(
                    f"Failed to copy file from container: {
                        stderr.decode() if stderr else 'Unknown error'}"
                )
                return False

        except Exception as e:
            logger.error(f"Error copying file from container: {e}")
            return False

    async def cleanup(self):
        """Clean up all running containers"""
        logger.info("Cleaning up Docker sandbox resources...")

        for container_id, proc in list(self.active_containers.items()):
            await self.stop_container(container_id)

        self.active_containers.clear()
        logger.info("Docker sandbox cleanup complete")


# Legacy function for backward compatibility
async def run_container(image, command=None, volumes=None, env=None, timeout=300):
    """Legacy function for backward compatibility

    Args:
        image: Docker image to use
        command: Command to run in the container
        volumes: Dictionary of volume mappings (host_path: container_path)
        env: Dictionary of environment variables
        timeout: Timeout in seconds

    Returns:
        Tuple containing success flag, container ID, stdout, and stderr
    """
    sandbox = DockerSandbox()
    return await sandbox.run_container(
        image=image, command=command, volumes=volumes, env=env, timeout=timeout
    )
