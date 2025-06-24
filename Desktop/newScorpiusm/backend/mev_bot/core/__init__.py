"""
Scorpius Enterprise MEV Bot - Core Module
High-performance, modular MEV framework for institutional trading
"""

from .config import Config
from .engine import MEVEngine
from .strategy import AbstractStrategy, StrategyResult
from .types import BundleRequest, MEVOpportunity, TransactionData

__version__ = "1.0.0"
__author__ = "Scorpius Team"


__all__ = [
    "MEVEngine",
    "AbstractStrategy",
    "StrategyResult",
    "MEVOpportunity",
    "BundleRequest",
    "TransactionData",
    "Config",
]
