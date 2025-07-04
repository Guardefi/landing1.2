"""
Core config module for API Gateway
Re-exports config from the main core package
"""

import sys
from pathlib import Path

# Add packages/core to the Python path
packages_core_path = Path("/app/packages/core")  # Use absolute container path
core_config_path = packages_core_path / "core"
sys.path.insert(0, str(packages_core_path))
sys.path.insert(0, str(core_config_path))

# Import and re-export from the actual core package config using importlib
import importlib.util
spec = importlib.util.spec_from_file_location("core_config", core_config_path / "config.py")
core_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_config_module)

# Re-export the config classes and functions
Config = core_config_module.Config
get_config = core_config_module.get_config
set_config = core_config_module.set_config
DatabaseConfig = core_config_module.DatabaseConfig
RedisConfig = core_config_module.RedisConfig
SecurityConfig = core_config_module.SecurityConfig
LoggingConfig = core_config_module.LoggingConfig

__all__ = [
    'Config',
    'get_config',
    'set_config',
    'DatabaseConfig',
    'RedisConfig',
    'SecurityConfig',
    'LoggingConfig'
] 