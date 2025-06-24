"""
Storage module for Scorpius Bridge
"""

from .database import DatabaseManager, get_database_manager

__all__ = ["DatabaseManager", "get_database_manager"]
