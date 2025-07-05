"""WebSocket API for real-time dashboard integration."""

from .connection_manager import ConnectionManager
from .events import EventBroadcaster
from .handlers import BridgeWebSocketHandler

__all__ = ["ConnectionManager", "EventBroadcaster", "BridgeWebSocketHandler"]
