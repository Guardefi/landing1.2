"""
WebSocket Connection Manager for Scorpius Enterprise Platform
Handles real-time communication with React dashboard clients.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_subscriptions: Dict[WebSocket, Set[str]] = {}
        self.connection_groups: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group: Optional[str] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_subscriptions[websocket] = set()

        if group:
            if group not in self.connection_groups:
                self.connection_groups[group] = []
            self.connection_groups[group].append(websocket)

        logger.info(f"New WebSocket connection established. Group: {group}")
        logger.info(f"Total active connections: {len(self.active_connections)}")

        # Send welcome message
        await self.send_personal_message(
            websocket,
            {
                "type": "connection_established",
                "connection_id": id(websocket),
                "group": group,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if websocket in self.client_subscriptions:
            del self.client_subscriptions[websocket]

        # Remove from all groups
        for group_name, connections in self.connection_groups.items():
            if websocket in connections:
                connections.remove(websocket)

        logger.info(
            f"WebSocket connection closed. Active connections: {len(self.active_connections)}"
        )

    async def send_personal_message(
        self, websocket: WebSocket, message: Dict[str, Any]
    ):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")

    async def broadcast(self, message: Dict[str, Any], group: Optional[str] = None):
        """Broadcast a message to all connected clients or a specific group."""
        message_json = json.dumps(message)

        if group and group in self.connection_groups:
            # Broadcast to specific group
            connections = self.connection_groups[group].copy()
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Failed to broadcast to group {group}: {e}")
                    self.disconnect(connection)
        else:
            # Broadcast to all connections
            disconnected = []
            for connection in self.active_connections.copy():
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Failed to broadcast message: {e}")
                    disconnected.append(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

    async def subscribe_client(self, websocket: WebSocket, events: List[str]):
        """Subscribe a client to specific event types."""
        if websocket in self.client_subscriptions:
            self.client_subscriptions[websocket].update(events)
            await self.send_personal_message(
                websocket,
                {
                    "type": "subscription_updated",
                    "subscribed_events": list(self.client_subscriptions[websocket]),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    async def unsubscribe_client(self, websocket: WebSocket, events: List[str]):
        """Unsubscribe a client from specific event types."""
        if websocket in self.client_subscriptions:
            for event in events:
                self.client_subscriptions[websocket].discard(event)
            await self.send_personal_message(
                websocket,
                {
                    "type": "subscription_updated",
                    "subscribed_events": list(self.client_subscriptions[websocket]),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    async def broadcast_to_subscribers(self, event_type: str, message: Dict[str, Any]):
        """Broadcast a message only to clients subscribed to a specific event type."""
        message["event_type"] = event_type
        message_json = json.dumps(message)

        disconnected = []
        for connection, subscriptions in self.client_subscriptions.items():
            if event_type in subscriptions:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Failed to send subscribed message: {e}")
                    disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections."""
        return {
            "total_connections": len(self.active_connections),
            "groups": {
                group: len(connections)
                for group, connections in self.connection_groups.items()
            },
            "subscriptions": {
                id(ws): list(subs) for ws, subs in self.client_subscriptions.items()
            },
        }
