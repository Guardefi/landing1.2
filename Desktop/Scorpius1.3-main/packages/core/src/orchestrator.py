"""
Core Orchestrator Module
-----------------------
Provides centralized orchestration for all services and plugins in the Scorpius platform.
Handles service discovery, communication, and lifecycle management.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Type, Callable
import importlib
import inspect
import os
import sys
from datetime import datetime

import redis.asyncio as redis

from .types import ServiceInfo, EventMessage, EventType, ServiceStatus, HealthCheckResult
from .exceptions import ServiceError, DependencyError, HealthCheckError
from .config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("core.orchestrator")


class CoreOrchestrator:
    """
    Core orchestrator for the Scorpius platform.
    Handles service discovery, initialization, and communication.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.plugins: Dict[str, Any] = {}
        self._event_bus = asyncio.Queue()
        self._running = False
        self._redis_client: Optional[redis.Redis] = None
        self._config = get_config()
        logger.info("Core orchestrator initialized")
    
    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection for service registry"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self._config.redis.url,
                    decode_responses=True,
                    socket_timeout=self._config.redis.socket_timeout
                )
                await self._redis_client.ping()
                logger.info("Connected to Redis for service registry")
            except Exception as e:
                logger.warning(f"Could not connect to Redis for service registry: {e}")
                # Fall back to in-memory storage
                self._redis_client = None
        return self._redis_client
    
    def register_service(self, 
                        name: str, 
                        module_path: str, 
                        entry_point: str, 
                        dependencies: List[str] = None,
                        health_check: Callable = None,
                        metadata: dict = None) -> None:
        """
        Register a service with the orchestrator
        """
        if name in self.services:
            logger.warning(f"Service {name} already registered, updating registration")
        
        service_info = ServiceInfo(
            name=name,
            module_path=module_path,
            entry_point=entry_point,
            dependencies=dependencies or [],
            health_check=health_check,
            metadata=metadata or {}
        )
        
        # Store in memory
        self.services[name] = service_info
        
        # Store in Redis for persistence and sharing across processes
        asyncio.create_task(self._store_service_in_redis(name, service_info))
        
        logger.info(f"Service {name} registered")
    
    async def _store_service_in_redis(self, name: str, service_info: ServiceInfo):
        """Store service information in Redis for persistence"""
        try:
            redis_client = await self._get_redis()
            if redis_client:
                service_data = {
                    "name": service_info.name,
                    "module_path": service_info.module_path,
                    "entry_point": service_info.entry_point,
                    "dependencies": service_info.dependencies,
                    "metadata": service_info.metadata,
                    "status": service_info.status.value,
                    "registered_at": datetime.now().isoformat()
                }
                await redis_client.hset(
                    "scorpius:services", 
                    name, 
                    json.dumps(service_data)
                )
                logger.debug(f"Service {name} stored in Redis")
        except Exception as e:
            logger.warning(f"Failed to store service {name} in Redis: {e}")
    
    def register_plugin(self, name: str, plugin_instance: Any) -> None:
        """
        Register a plugin with the orchestrator
        """
        if name in self.plugins:
            logger.warning(f"Plugin {name} already registered, replacing")
        
        self.plugins[name] = plugin_instance
        logger.info(f"Plugin {name} registered")
    
    async def start_service(self, name: str) -> bool:
        """
        Start a registered service
        """
        if name not in self.services:
            logger.error(f"Cannot start unknown service: {name}")
            return False
        
        service = self.services[name]
        
        # Check dependencies
        for dep in service.dependencies:
            if dep not in self.services or self.services[dep].status != "running":
                logger.error(f"Cannot start {name}, dependency {dep} not running")
                return False
        
        # Update status
        service.status = "starting"
        
        try:
            # Import module
            module = importlib.import_module(service.module_path)
            
            # Get entry point
            if hasattr(module, service.entry_point):
                entry_fn = getattr(module, service.entry_point)
                
                # If it's async, await it
                if inspect.iscoroutinefunction(entry_fn):
                    service.instance = await entry_fn()
                else:
                    service.instance = entry_fn()
                
                service.status = "running"
                logger.info(f"Service {name} started successfully")
                return True
            else:
                logger.error(f"Entry point {service.entry_point} not found in {service.module_path}")
                service.status = "error"
                return False
                
        except Exception as e:
            logger.exception(f"Failed to start service {name}: {str(e)}")
            service.status = "error"
            return False
    
    async def stop_service(self, name: str) -> bool:
        """
        Stop a running service
        """
        if name not in self.services:
            logger.error(f"Cannot stop unknown service: {name}")
            return False
        
        service = self.services[name]
        
        if service.status != "running":
            logger.warning(f"Service {name} is not running (status: {service.status})")
            return True
        
        try:
            # If instance has a stop method, call it
            if hasattr(service.instance, "stop"):
                stop_fn = getattr(service.instance, "stop")
                
                # If it's async, await it
                if inspect.iscoroutinefunction(stop_fn):
                    await stop_fn()
                else:
                    stop_fn()
            
            service.status = "stopped"
            service.instance = None
            logger.info(f"Service {name} stopped")
            return True
            
        except Exception as e:
            logger.exception(f"Error stopping service {name}: {str(e)}")
            service.status = "error"
            return False
    
    async def check_health(self, service_name: str = None) -> Dict[str, str]:
        """
        Check health of services
        """
        health_status = {}
        services_to_check = [service_name] if service_name else self.services.keys()
        
        for name in services_to_check:
            if name not in self.services:
                health_status[name] = "unknown"
                continue
                
            service = self.services[name]
            
            if service.status != "running":
                health_status[name] = service.status
                continue
            
            if service.health_check and service.instance:
                try:
                    if inspect.iscoroutinefunction(service.health_check):
                        health_ok = await service.health_check(service.instance)
                    else:
                        health_ok = service.health_check(service.instance)
                    
                    health_status[name] = "healthy" if health_ok else "unhealthy"
                except Exception as e:
                    logger.exception(f"Health check failed for {name}: {str(e)}")
                    health_status[name] = "error"
            else:
                health_status[name] = "running"  # No health check defined, assume running
                
        return health_status
    
    async def start_all_services(self) -> bool:
        """
        Start all registered services in dependency order
        """
        self._running = True
        logger.info("Starting all services...")
        
        # Build dependency graph and start in order
        remaining = set(self.services.keys())
        started = set()
        
        while remaining and self._running:
            progress = False
            
            for name in list(remaining):
                service = self.services[name]
                
                # Check if dependencies are met
                if all(dep in started for dep in service.dependencies):
                    logger.info(f"Starting service: {name}")
                    success = await self.start_service(name)
                    
                    if success:
                        started.add(name)
                        remaining.remove(name)
                        progress = True
                    else:
                        logger.error(f"Failed to start {name}, will not retry")
                        remaining.remove(name)
                        progress = True
            
            # If we made no progress, we have a dependency cycle
            if not progress:
                logger.error("Dependency cycle detected, cannot start remaining services")
                logger.error(f"Remaining services: {remaining}")
                return False
                
            # Small delay to avoid CPU spinning
            await asyncio.sleep(0.1)
        
        logger.info(f"Started {len(started)} services")
        return True
    
    async def stop_all_services(self) -> None:
        """
        Stop all running services in reverse dependency order
        """
        self._running = False
        logger.info("Stopping all services...")
        
        # Build reverse dependency graph
        depends_on = {name: [] for name in self.services}
        
        for name, service in self.services.items():
            for dep in service.dependencies:
                depends_on[dep].append(name)
        
        # Stop in reverse dependency order
        running = [name for name, svc in self.services.items() if svc.status == "running"]
        stopped = set()
        
        while running:
            for name in list(running):
                # Check if all dependent services are stopped
                if all(dep in stopped for dep in depends_on[name]):
                    logger.info(f"Stopping service: {name}")
                    await self.stop_service(name)
                    running.remove(name)
                    stopped.add(name)
            
            # Small delay to avoid CPU spinning
            await asyncio.sleep(0.1)
            
        logger.info("All services stopped")
    
    async def publish_event(self, event_type: str, payload: Any) -> None:
        """
        Publish an event to the event bus
        """
        await self._event_bus.put({"type": event_type, "payload": payload})
        logger.debug(f"Published event: {event_type}")
    
    async def event_loop(self) -> None:
        """
        Main event loop for processing events
        """
        logger.info("Event loop started")
        
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_bus.get(), timeout=1.0)
                logger.debug(f"Processing event: {event['type']}")
                
                # Process event - for now just log it
                # In the future, implement proper event routing
                
                self._event_bus.task_done()
            except asyncio.TimeoutError:
                # No events, continue
                pass
            except Exception as e:
                logger.exception(f"Error in event loop: {str(e)}")
        
        logger.info("Event loop stopped")
    
    async def run(self) -> None:
        """
        Main run method to start the orchestrator
        """
        self._running = True
        event_task = asyncio.create_task(self.event_loop())
        
        try:
            await self.start_all_services()
            
            # Keep running until stopped
            while self._running:
                await asyncio.sleep(1)
                
        finally:
            self._running = False
            await self.stop_all_services()
            await event_task
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """Get service information by name"""
        return self.services.get(name)
    
    def get_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services in API gateway format"""
        # Try to sync from Redis synchronously using asyncio.run
        # This is a temporary solution - ideally we'd make this method async
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                asyncio.create_task(self._sync_services_from_redis())
            else:
                # If not in async context, run synchronously
                asyncio.run(self._sync_services_from_redis())
        except Exception as e:
            logger.warning(f"Could not sync services from Redis: {e}")
        
        result = {}
        for name, service_info in self.services.items():
            # Convert ServiceInfo to API gateway format
            result[name] = {
                "host": service_info.metadata.get("host", f"{name}-service"),
                "port": service_info.metadata.get("port", 8000),
                "health": service_info.metadata.get("health_endpoint", "/health"),
                "status": service_info.status.value,
                "dependencies": service_info.dependencies
            }
        return result
    
    async def _sync_services_from_redis(self):
        """Sync services from Redis to in-memory storage"""
        try:
            redis_client = await self._get_redis()
            if redis_client:
                services_data = await redis_client.hgetall("scorpius:services")
                for name, service_json in services_data.items():
                    # Load service from Redis (update even if exists)
                    try:
                        service_data = json.loads(service_json)
                        service_info = ServiceInfo(
                            name=service_data["name"],
                            module_path=service_data["module_path"],
                            entry_point=service_data["entry_point"],
                            dependencies=service_data.get("dependencies", []),
                            health_check=None,  # Can't serialize functions
                            metadata=service_data.get("metadata", {})
                        )
                        service_info.status = ServiceStatus(service_data.get("status", "registered"))
                        self.services[name] = service_info
                        logger.debug(f"Loaded/updated service {name} from Redis")
                    except Exception as e:
                        logger.warning(f"Failed to load service {name} from Redis: {e}")
        except Exception as e:
            logger.warning(f"Failed to sync services from Redis: {e}")

# Singleton instance
_instance = None

def get_orchestrator() -> CoreOrchestrator:
    """
    Get the singleton orchestrator instance
    """
    global _instance
    if _instance is None:
        _instance = CoreOrchestrator()
    return _instance
