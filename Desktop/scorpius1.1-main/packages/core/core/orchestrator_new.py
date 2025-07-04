#!/usr/bin/env python3
"""
Scorpius Core Orchestrator
Central service management and plugin coordination system.
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import structlog
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("orchestrator")

# Metrics
SERVICE_HEALTH_GAUGE = Gauge('service_health_status', 'Service health status', ['service_name'])
PLUGIN_LOAD_COUNTER = Counter('plugin_loads_total', 'Total plugin loads', ['plugin_name', 'status'])
MESSAGE_PROCESSING_HISTOGRAM = Histogram('message_processing_seconds', 'Message processing time', ['message_type'])


class ServiceStatus(Enum):
    """Service status enumeration."""
    UNKNOWN = "unknown"
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


class MessageType(Enum):
    """Inter-service message types."""
    HEALTH_CHECK = "health_check"
    SERVICE_REGISTRATION = "service_registration"
    EVENT_NOTIFICATION = "event_notification"
    COMMAND = "command"
    RESPONSE = "response"


@dataclass
class ServiceInfo:
    """Service registration information."""
    name: str
    version: str
    endpoint: str
    health_endpoint: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Inter-service message structure."""
    id: str
    type: MessageType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class Plugin(ABC):
    """Abstract base class for orchestrator plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger = structlog.get_logger(f"plugin.{name}")
    
    @abstractmethod
    async def initialize(self, orchestrator: 'CoreOrchestrator') -> bool:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the plugin gracefully."""
        pass
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return plugin capabilities."""
        pass


class CoreOrchestrator:
    """
    Core orchestrator responsible for service lifecycle management,
    inter-service communication, and plugin coordination.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.services: Dict[str, ServiceInfo] = {}
        self.plugins: Dict[str, Plugin] = {}
        self.message_handlers: Dict[MessageType, List[Plugin]] = {}
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.running = False
        self.health_check_interval = 30
        self.heartbeat_timeout = 60
        self.logger = logger.bind(component="orchestrator")
        self._start_time = time.time()
        
        # Initialize metrics
        for plugin_type in MessageType:
            MESSAGE_PROCESSING_HISTOGRAM.labels(message_type=plugin_type.value)
    
    async def start(self):
        """Start the orchestrator."""
        self.logger.info("Starting Core Orchestrator")
        
        # Connect to Redis
        self.redis = redis.from_url(self.redis_url)
        await self.redis.ping()
        
        # Initialize plugins
        await self._initialize_plugins()
        
        # Start background tasks
        self.running = True
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._message_processor())
        
        self.logger.info("Core Orchestrator started successfully")
    
    async def stop(self):
        """Stop the orchestrator gracefully."""
        self.logger.info("Stopping Core Orchestrator")
        self.running = False
        
        # Shutdown plugins
        for plugin in self.plugins.values():
            try:
                await plugin.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin.name}: {e}")
        
        # Close Redis connection
        if self.redis:
            await self.redis.close()
        
        self.logger.info("Core Orchestrator stopped")
    
    async def register_service(self, service_info: ServiceInfo):
        """Register a new service."""
        self.logger.info(f"Registering service: {service_info.name}")
        
        service_info.status = ServiceStatus.STARTING
        service_info.last_heartbeat = datetime.utcnow()
        
        self.services[service_info.name] = service_info
        SERVICE_HEALTH_GAUGE.labels(service_name=service_info.name).set(1)
        
        # Notify plugins
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.SERVICE_REGISTRATION,
            source="orchestrator",
            payload={"service_info": service_info.__dict__}
        )
        await self._broadcast_message(message)
        
        self.logger.info(f"Service registered: {service_info.name}")
    
    async def unregister_service(self, service_name: str):
        """Unregister a service."""
        if service_name in self.services:
            self.logger.info(f"Unregistering service: {service_name}")
            del self.services[service_name]
            SERVICE_HEALTH_GAUGE.labels(service_name=service_name).set(0)
    
    async def register_plugin(self, plugin: Plugin):
        """Register a plugin."""
        self.logger.info(f"Registering plugin: {plugin.name}")
        
        try:
            success = await plugin.initialize(self)
            if success:
                self.plugins[plugin.name] = plugin
                
                # Register message handlers
                for msg_type in MessageType:
                    if msg_type not in self.message_handlers:
                        self.message_handlers[msg_type] = []
                
                PLUGIN_LOAD_COUNTER.labels(plugin_name=plugin.name, status="success").inc()
                self.logger.info(f"Plugin registered successfully: {plugin.name}")
            else:
                PLUGIN_LOAD_COUNTER.labels(plugin_name=plugin.name, status="failed").inc()
                self.logger.error(f"Plugin initialization failed: {plugin.name}")
        
        except Exception as e:
            PLUGIN_LOAD_COUNTER.labels(plugin_name=plugin.name, status="error").inc()
            self.logger.error(f"Error registering plugin {plugin.name}: {e}")
    
    async def send_message(self, message: Message):
        """Send a message to a specific service or broadcast."""
        if self.redis:
            channel = f"scorpius.{message.target}" if message.target else "scorpius.broadcast"
            await self.redis.publish(channel, json.dumps(message.__dict__, default=str))
    
    async def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Get the status of a specific service."""
        service = self.services.get(service_name)
        return service.status if service else None
    
    async def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get information about all registered services."""
        return self.services.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Get orchestrator health status."""
        healthy_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        total_services = len(self.services)
        
        return {
            "status": "healthy" if self.running else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "unhealthy": total_services - healthy_services
            },
            "plugins": list(self.plugins.keys()),
            "uptime": time.time() - self._start_time
        }
    
    async def _initialize_plugins(self):
        """Initialize all plugins."""
        # This would typically load plugins from a configuration file
        # For now, we'll just log that plugin initialization is ready
        self.logger.info("Plugin system initialized")
    
    async def _health_monitor(self):
        """Background task to monitor service health."""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for service_name, service in self.services.items():
                    if service.last_heartbeat:
                        time_since_heartbeat = (current_time - service.last_heartbeat).total_seconds()
                        
                        if time_since_heartbeat > self.heartbeat_timeout:
                            if service.status != ServiceStatus.UNHEALTHY:
                                service.status = ServiceStatus.UNHEALTHY
                                SERVICE_HEALTH_GAUGE.labels(service_name=service_name).set(0)
                                self.logger.warning(f"Service {service_name} marked as unhealthy")
                
                await asyncio.sleep(self.health_check_interval)
            
            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(5)
    
    async def _message_processor(self):
        """Background task to process inter-service messages."""
        if not self.redis:
            return
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("scorpius.*")
        
        while self.running:
            try:
                message = await pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    await self._handle_message(message)
            
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _handle_message(self, raw_message):
        """Handle incoming messages."""
        try:
            data = json.loads(raw_message['data'])
            message = Message(**data)
            
            with MESSAGE_PROCESSING_HISTOGRAM.labels(message_type=message.type.value).time():
                # Process message through registered handlers
                handlers = self.message_handlers.get(message.type, [])
                for handler in handlers:
                    try:
                        response = await handler.handle_message(message)
                        if response:
                            await self.send_message(response)
                    except Exception as e:
                        self.logger.error(f"Error in message handler {handler.name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def _broadcast_message(self, message: Message):
        """Broadcast a message to all services."""
        message.target = None
        await self.send_message(message)


# Global orchestrator instance
orchestrator = CoreOrchestrator()


async def get_orchestrator() -> CoreOrchestrator:
    """Dependency injection for FastAPI."""
    return orchestrator
