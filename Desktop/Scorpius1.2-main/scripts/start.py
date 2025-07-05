#!/usr/bin/env python3
"""
Scorpius Platform Startup Script
Orchestrates the initialization and startup of all services in the correct order.
"""

import asyncio
import logging
import os
import sys
import signal
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml

# Add packages to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from core.orchestrator import ServiceOrchestrator
from core.filesystem import FileSystemUtils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scorpius-startup.log')
    ]
)
logger = logging.getLogger("scorpius-startup")

class PlatformManager:
    """Main platform manager for orchestrating startup and shutdown."""
    
    def __init__(self, config_file: str = "config/platform.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.orchestrator = ServiceOrchestrator()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
    def _load_config(self) -> dict:
        """Load platform configuration."""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Default configuration for the platform."""
        return {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "services": {
                "core": {
                    "enabled": True,
                    "startup_delay": 0,
                    "health_check_path": "/health"
                },
                "api-gateway": {
                    "enabled": True,
                    "startup_delay": 2,
                    "port": 8000,
                    "health_check_path": "/health"
                },
                "scanner": {
                    "enabled": True,
                    "startup_delay": 5,
                    "port": 8001,
                    "health_check_path": "/health"
                },
                "bridge": {
                    "enabled": True,
                    "startup_delay": 5,
                    "port": 8002,
                    "health_check_path": "/health"
                },
                "mempool": {
                    "enabled": True,
                    "startup_delay": 5,
                    "port": 8003,
                    "health_check_path": "/health"
                },
                "mev": {
                    "enabled": True,
                    "startup_delay": 7,
                    "port": 8004,
                    "health_check_path": "/health"
                },
                "honeypot": {
                    "enabled": True,
                    "startup_delay": 7,
                    "port": 8005,
                    "health_check_path": "/health"
                }
            },
            "infrastructure": {
                "postgres": {
                    "enabled": True,
                    "port": 5432
                },
                "redis": {
                    "enabled": True,
                    "port": 6379
                },
                "prometheus": {
                    "enabled": True,
                    "port": 9090
                }
            }
        }
    
    async def start_infrastructure(self):
        """Start infrastructure services (database, cache, monitoring)."""
        logger.info("Starting infrastructure services...")
        
        infra_config = self.config.get("infrastructure", {})
        
        if infra_config.get("postgres", {}).get("enabled", True):
            await self._start_postgres()
        
        if infra_config.get("redis", {}).get("enabled", True):
            await self._start_redis()
        
        if infra_config.get("prometheus", {}).get("enabled", True):
            await self._start_prometheus()
        
        # Wait for infrastructure to be ready
        await asyncio.sleep(3)
        logger.info("Infrastructure services started")
    
    async def _start_postgres(self):
        """Start PostgreSQL if not running."""
        try:
            # Check if PostgreSQL is already running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            if "postgres" not in result.stdout:
                logger.info("Starting PostgreSQL container...")
                subprocess.run([
                    "docker", "run", "-d", "--name", "postgres",
                    "-e", "POSTGRES_DB=scorpius",
                    "-e", "POSTGRES_USER=scorpius",
                    "-e", "POSTGRES_PASSWORD=scorpius123",
                    "-p", "5432:5432",
                    "postgres:15"
                ], check=True)
            else:
                logger.info("PostgreSQL already running")
        except Exception as e:
            logger.error(f"Failed to start PostgreSQL: {e}")
    
    async def _start_redis(self):
        """Start Redis if not running."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=redis", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            if "redis" not in result.stdout:
                logger.info("Starting Redis container...")
                subprocess.run([
                    "docker", "run", "-d", "--name", "redis",
                    "-p", "6379:6379",
                    "redis:7-alpine"
                ], check=True)
            else:
                logger.info("Redis already running")
        except Exception as e:
            logger.error(f"Failed to start Redis: {e}")
    
    async def _start_prometheus(self):
        """Start Prometheus if configured."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=prometheus", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            if "prometheus" not in result.stdout:
                logger.info("Starting Prometheus container...")
                subprocess.run([
                    "docker", "run", "-d", "--name", "prometheus",
                    "-p", "9090:9090",
                    "prom/prometheus:latest"
                ], check=True)
            else:
                logger.info("Prometheus already running")
        except Exception as e:
            logger.error(f"Failed to start Prometheus: {e}")
    
    async def start_services(self):
        """Start all enabled services in order."""
        logger.info("Starting application services...")
        
        # Start core orchestrator
        await self.orchestrator.start()
        
        services_config = self.config.get("services", {})
        startup_order = sorted(
            services_config.items(),
            key=lambda x: x[1].get("startup_delay", 0)
        )
        
        for service_name, service_config in startup_order:
            if service_config.get("enabled", True):
                await self._start_service(service_name, service_config)
                
                # Wait for startup delay
                delay = service_config.get("startup_delay", 0)
                if delay > 0:
                    logger.info(f"Waiting {delay}s before starting next service...")
                    await asyncio.sleep(delay)
        
        logger.info("All services started")
    
    async def _start_service(self, service_name: str, config: dict):
        """Start a specific service."""
        logger.info(f"Starting service: {service_name}")
        
        try:
            # Register service with orchestrator
            await self.orchestrator.register_service(
                name=service_name,
                port=config.get("port", 8000),
                health_check_path=config.get("health_check_path", "/health"),
                dependencies=config.get("dependencies", [])
            )
            
            # Start the service process
            service_dir = self._get_service_directory(service_name)
            if service_dir and service_dir.exists():
                await self._start_service_process(service_name, service_dir)
            else:
                logger.warning(f"Service directory not found for {service_name}")
                
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
    
    def _get_service_directory(self, service_name: str) -> Optional[Path]:
        """Get the directory for a service."""
        project_root = Path(__file__).parent.parent
        
        # Check different possible locations
        possible_paths = [
            project_root / "services" / service_name,
            project_root / "backend" / service_name,
            project_root / "packages" / service_name
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    async def _start_service_process(self, service_name: str, service_dir: Path):
        """Start the actual service process."""
        # Look for main entry point
        main_files = ["main.py", "app.py", "server.py"]
        entry_point = None
        
        for main_file in main_files:
            if (service_dir / main_file).exists():
                entry_point = service_dir / main_file
                break
        
        if not entry_point:
            logger.warning(f"No entry point found for service {service_name}")
            return
        
        # Start the service
        env = os.environ.copy()
        env.update({
            "SERVICE_NAME": service_name,
            "PYTHONPATH": str(Path(__file__).parent.parent / "packages")
        })
        
        process = subprocess.Popen(
            [sys.executable, str(entry_point)],
            cwd=str(service_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[service_name] = process
        logger.info(f"Service {service_name} started with PID {process.pid}")
    
    async def health_check(self):
        """Perform health check on all running services."""
        logger.info("Performing health check...")
        health_status = await self.orchestrator.get_health_status()
        
        for service_name, status in health_status.service_statuses.items():
            if status.healthy:
                logger.info(f"✓ {service_name}: Healthy")
            else:
                logger.warning(f"✗ {service_name}: {status.error}")
        
        return health_status.overall_health == "healthy"
    
    async def stop(self):
        """Stop all services gracefully."""
        logger.info("Stopping all services...")
        self.running = False
        
        # Stop application services
        for service_name, process in self.processes.items():
            logger.info(f"Stopping service: {service_name}")
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing service: {service_name}")
                process.kill()
        
        # Stop orchestrator
        await self.orchestrator.stop()
        
        logger.info("All services stopped")
    
    async def run(self):
        """Main run loop."""
        try:
            self.running = True
            
            # Start infrastructure
            await self.start_infrastructure()
            
            # Start services
            await self.start_services()
            
            # Initial health check
            await asyncio.sleep(5)
            is_healthy = await self.health_check()
            
            if not is_healthy:
                logger.warning("Some services are not healthy, but continuing...")
            
            logger.info("Platform is running. Press Ctrl+C to stop.")
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Platform error: {e}")
        finally:
            await self.stop()

def setup_signal_handlers(platform_manager):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        platform_manager.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scorpius Platform Manager")
    parser.add_argument("--config", default="config/platform.yaml", 
                       help="Configuration file path")
    parser.add_argument("--environment", default="development",
                       help="Environment (development, staging, production)")
    parser.add_argument("--health-check", action="store_true",
                       help="Perform health check and exit")
    
    args = parser.parse_args()
    
    # Set environment
    os.environ["ENVIRONMENT"] = args.environment
    
    # Create platform manager
    platform_manager = PlatformManager(args.config)
    
    if args.health_check:
        # Just perform health check
        is_healthy = await platform_manager.health_check()
        sys.exit(0 if is_healthy else 1)
    
    # Setup signal handlers
    setup_signal_handlers(platform_manager)
    
    # Run the platform
    await platform_manager.run()

if __name__ == "__main__":
    asyncio.run(main())
