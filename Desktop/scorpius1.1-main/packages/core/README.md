# Scorpius Enterprise Platform - Core

The core orchestrator and shared components for the Scorpius Enterprise Platform.

## Overview

This package provides:

- **Orchestrator**: Central coordination and service management
- **Configuration**: Unified configuration management across services
- **Types**: Shared type definitions and interfaces
- **Utilities**: Common utility functions and helpers

## Installation

```bash
pip install -e packages/core
```

## Usage

```python
from core import get_orchestrator, get_config
from core.types import ServiceInfo

# Get the orchestrator instance
orchestrator = get_orchestrator()

# Get configuration
config = get_config()

# Create service info
service_info = ServiceInfo(
    name="my-service",
    host="localhost",
    port=8000,
    health_endpoint="/health"
)
```

## Development

The core package is designed to be the foundation for all Scorpius services, providing:

- Consistent configuration management
- Service discovery and health monitoring
- Shared data types and interfaces
- Common utilities and helpers

## Components

- `orchestrator_new.py`: Main orchestrator implementation
- `config.py`: Configuration management
- `types.py`: Type definitions
- `exceptions.py`: Custom exceptions
- `utils.py`: Utility functions
