"""
Core types module for API Gateway
Re-exports types from the main core package
"""

import sys
from pathlib import Path

# Add packages/core to the Python path
packages_core_path = Path("/app/packages/core")  # Use absolute container path
core_types_path = packages_core_path / "core"
sys.path.insert(0, str(packages_core_path))
sys.path.insert(0, str(core_types_path))

# Import and re-export from the actual core package types module
import importlib.util
spec = importlib.util.spec_from_file_location("core_types", core_types_path / "types.py")
core_types_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_types_module)

# Re-export the types
ServiceInfo = core_types_module.ServiceInfo
ServiceStatus = core_types_module.ServiceStatus
HealthCheckResult = core_types_module.HealthCheckResult
EventType = core_types_module.EventType
EventMessage = core_types_module.EventMessage
ServiceMetrics = core_types_module.ServiceMetrics

__all__ = [
    'ServiceInfo',
    'ServiceStatus', 
    'HealthCheckResult',
    'EventType',
    'EventMessage',
    'ServiceMetrics'
] 