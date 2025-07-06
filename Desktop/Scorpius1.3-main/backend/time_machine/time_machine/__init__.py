"""
Time Machine: Enterprise Blockchain Forensic Analysis Platform
"""

__version__ = "0.1.0"
__author__ = "Scorpius Team"

from .core.controller import TimeMachineEngine
from .core.models import (
    AnalysisPlugin,
    Branch,
    Diff,
    ForensicSession,
    FrameType,
    Patch,
    ReplayJob,
    StateManipulation,
    TimelineEvent,
    VMBackend,
)

__all__ = [
    "TimeMachineEngine",
    "ReplayJob",
    "Branch",
    "TimelineEvent",
    "Patch",
    "Diff",
    "ForensicSession",
    "StateManipulation",
    "AnalysisPlugin",
    "VMBackend",
    "FrameType",
]
