#!/usr/bin/env python3
"""
Service Registration Script
--------------------------
Registers all microservices with the orchestrator for centralized management.
"""

import asyncio
import logging
from core import get_orchestrator
from core.types import ServiceInfo

logger = logging.getLogger(__name__)


async def register_services():
    """Register all platform services with the orchestrator"""
    orchestrator = get_orchestrator()
    
    # Service definitions
    services = [
        {
            "name": "api-gateway",
            "module_path": "services.api_gateway.main",
            "entry_point": "app",
            "dependencies": ["redis", "postgresql"],
            "metadata": {
                "host": "api-gateway",
                "port": 8000,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "bridge",
            "module_path": "services.bridge.main",
            "entry_point": "app",
            "dependencies": ["postgresql", "redis"],
            "metadata": {
                "host": "bridge-service",
                "port": 8001,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "mempool",
            "module_path": "services.mempool.main",
            "entry_point": "app",
            "dependencies": ["redis"],
            "metadata": {
                "host": "mempool-service",
                "port": 8002,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "honeypot",
            "module_path": "services.honeypot.main",
            "entry_point": "app",
            "dependencies": ["postgresql"],
            "metadata": {
                "host": "honeypot-service",
                "port": 8003,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "scanner",
            "module_path": "services.scanner.main",
            "entry_point": "app",
            "dependencies": ["postgresql", "redis"],
            "metadata": {
                "host": "scanner-service",
                "port": 8004,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "mev",
            "module_path": "services.mev.main",
            "entry_point": "app",
            "dependencies": ["redis"],
            "metadata": {
                "host": "mev-service",
                "port": 8005,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "bytecode",
            "module_path": "services.bytecode.main",
            "entry_point": "app",
            "dependencies": ["postgresql"],
            "metadata": {
                "host": "bytecode-service",
                "port": 8006,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "quantum",
            "module_path": "services.quantum.main",
            "entry_point": "app",
            "dependencies": ["redis"],
            "metadata": {
                "host": "quantum-service",
                "port": 8007,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "timemachine",
            "module_path": "services.timemachine.main",
            "entry_point": "app",
            "dependencies": ["postgresql"],
            "metadata": {
                "host": "timemachine-service",
                "port": 8008,
                "health_endpoint": "/health"
            }
        },
        {
            "name": "reporting",
            "module_path": "services.reporting.main",
            "entry_point": "app",
            "dependencies": ["postgresql", "redis"],
            "metadata": {
                "host": "reporting-service",
                "port": 8009,
                "health_endpoint": "/health"
            }
        }
    ]
    
    # Register each service
    for service_def in services:
        service_info = ServiceInfo(
            name=service_def["name"],
            module_path=service_def["module_path"],
            entry_point=service_def["entry_point"],
            dependencies=service_def["dependencies"],
            metadata=service_def["metadata"]
        )
        
        orchestrator.register_service(
            name=service_def["name"],
            module_path=service_def["module_path"],
            entry_point=service_def["entry_point"],
            dependencies=service_def["dependencies"],
            metadata=service_def["metadata"]
        )
        
        logger.info(f"Registered service: {service_def['name']}")
    
    logger.info(f"Successfully registered {len(services)} services")
    return orchestrator


if __name__ == "__main__":
    asyncio.run(register_services())
