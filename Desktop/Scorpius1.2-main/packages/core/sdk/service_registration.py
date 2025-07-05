"""
Service Registration SDK for Scorpius Services
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

import httpx
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class ServiceRoute:
    """Service route configuration"""
    path: str
    method: str
    description: Optional[str] = None


@dataclass 
class ServiceRegistrationConfig:
    """Service registration configuration"""
    name: str
    version: str = "1.0.0"
    url: str = ""
    health_path: str = "/health"
    routes: List[ServiceRoute] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistrationClient:
    """Client for registering services with the orchestrator"""
    
    def __init__(self, 
                 gateway_url: str = "http://localhost:8000",
                 redis_url: str = "redis://localhost:6379"):
        self.gateway_url = gateway_url
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.http_client = httpx.AsyncClient()
    
    async def __aenter__(self):
        self.redis_client = redis.from_url(self.redis_url)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis_client:
            await self.redis_client.close()
        await self.http_client.aclose()
    
    async def register(self, config: ServiceRegistrationConfig) -> bool:
        """Register service with the orchestrator"""
        try:
            # Convert routes to dict format
            routes_dict = [
                {
                    "path": route.path,
                    "method": route.method,
                    "description": route.description
                }
                for route in config.routes
            ]
            
            # Prepare registration payload
            payload = {
                "name": config.name,
                "version": config.version,
                "endpoint": config.url,
                "health_endpoint": f"{config.url}{config.health_path}",
                "capabilities": config.capabilities,
                "dependencies": config.dependencies,
                "routes": routes_dict,
                "metadata": config.metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Register via HTTP API
            response = await self.http_client.post(
                f"{self.gateway_url}/services/register",
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered service: {config.name}")
                
                # Also publish to Redis for orchestrator
                if self.redis_client:
                    await self.redis_client.publish(
                        "scorpius.service_registration",
                        json.dumps(payload)
                    )
                
                return True
            else:
                logger.error(f"Failed to register service: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering service {config.name}: {e}")
            return False
    
    async def unregister(self, service_name: str) -> bool:
        """Unregister service from the orchestrator"""
        try:
            response = await self.http_client.delete(
                f"{self.gateway_url}/services/{service_name}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully unregistered service: {service_name}")
                
                # Also publish to Redis
                if self.redis_client:
                    await self.redis_client.publish(
                        "scorpius.service_unregistration",
                        json.dumps({"service_name": service_name})
                    )
                
                return True
            else:
                logger.error(f"Failed to unregister service: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering service {service_name}: {e}")
            return False
    
    async def heartbeat(self, service_name: str) -> bool:
        """Send heartbeat for service"""
        try:
            response = await self.http_client.post(
                f"{self.gateway_url}/services/{service_name}/heartbeat",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending heartbeat for {service_name}: {e}")
            return False


# Convenience functions
async def register_service(config: ServiceRegistrationConfig, 
                          gateway_url: str = "http://localhost:8000",
                          redis_url: str = "redis://localhost:6379") -> bool:
    """Register a service with the orchestrator"""
    async with ServiceRegistrationClient(gateway_url, redis_url) as client:
        return await client.register(config)


async def unregister_service(service_name: str,
                           gateway_url: str = "http://localhost:8000", 
                           redis_url: str = "redis://localhost:6379") -> bool:
    """Unregister a service from the orchestrator"""
    async with ServiceRegistrationClient(gateway_url, redis_url) as client:
        return await client.unregister(service_name)


# Background heartbeat task
async def start_heartbeat_task(service_name: str,
                              interval: int = 30,
                              gateway_url: str = "http://localhost:8000",
                              redis_url: str = "redis://localhost:6379"):
    """Start background heartbeat task"""
    client = ServiceRegistrationClient(gateway_url, redis_url)
    
    async def heartbeat_loop():
        while True:
            try:
                await client.heartbeat(service_name)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Heartbeat error for {service_name}: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds on error
    
    asyncio.create_task(heartbeat_loop())
