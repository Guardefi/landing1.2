"""WebSocket connection manager for real-time communication."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectionInfo(BaseModel):
    """Information about a WebSocket connection."""

    client_id: str
    connected_at: datetime
    subscriptions: Set[str] = set()
    metadata: Dict[str, Any] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard integration."""

    def __init__(self):
        # Active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection info: client_id -> ConnectionInfo
        self.connection_info: Dict[str, ConnectionInfo] = {}

        # Topic subscriptions: topic -> set of client_ids
        self.topic_subscriptions: Dict[str, Set[str]] = {}

        # Connection groups: group_name -> set of client_ids
        self.connection_groups: Dict[str, Set[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()

            self.active_connections[client_id] = websocket
            self.connection_info[client_id] = ConnectionInfo(
                client_id=client_id,
                connected_at=datetime.utcnow(),
                metadata=metadata or {},
            )

            logger.info(f"Client {client_id} connected")

            # Send welcome message
            await self.send_personal_message(
                {
                    "type": "connection",
                    "status": "connected",
                    "client_id": client_id,
                    "server_time": datetime.utcnow().isoformat(),
                },
                client_id,
            )

            return True

        except Exception as e:
            logger.error(f"Failed to connect client {client_id}: {e}")
            return False

    async def disconnect(self, client_id: str):
        """Disconnect a client and clean up resources."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if client_id in self.connection_info:
            # Remove from topic subscriptions
            for topic in self.connection_info[client_id].subscriptions:
                if topic in self.topic_subscriptions:
                    self.topic_subscriptions[topic].discard(client_id)
                    if not self.topic_subscriptions[topic]:
                        del self.topic_subscriptions[topic]

            del self.connection_info[client_id]

        # Remove from groups
        for group_clients in self.connection_groups.values():
            group_clients.discard(client_id)

        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(
        self, message: Dict[str, Any], client_id: str
    ) -> bool:
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, default=str))
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                await self.disconnect(client_id)
                return False
        return False

    async def broadcast_to_topic(self, message: Dict[str, Any], topic: str):
        """Broadcast a message to all clients subscribed to a topic."""
        if topic in self.topic_subscriptions:
            disconnected_clients = []

            for client_id in self.topic_subscriptions[topic].copy():
                success = await self.send_personal_message(message, client_id)
                if not success:
                    disconnected_clients.append(client_id)

            # Clean up disconnected clients
            for client_id in disconnected_clients:
                await self.disconnect(client_id)

    async def broadcast_to_group(self, message: Dict[str, Any], group_name: str):
        """Broadcast a message to all clients in a group."""
        if group_name in self.connection_groups:
            disconnected_clients = []

            for client_id in self.connection_groups[group_name].copy():
                success = await self.send_personal_message(message, client_id)
                if not success:
                    disconnected_clients.append(client_id)

            # Clean up disconnected clients
            for client_id in disconnected_clients:
                await self.disconnect(client_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        disconnected_clients = []

        for client_id in list(self.active_connections.keys()):
            success = await self.send_personal_message(message, client_id)
            if not success:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def subscribe_to_topic(self, client_id: str, topic: str):
        """Subscribe a client to a topic."""
        if client_id in self.connection_info:
            self.connection_info[client_id].subscriptions.add(topic)

            if topic not in self.topic_subscriptions:
                self.topic_subscriptions[topic] = set()
            self.topic_subscriptions[topic].add(client_id)

            logger.info(f"Client {client_id} subscribed to topic {topic}")

            # Send confirmation
            await self.send_personal_message(
                {"type": "subscription", "action": "subscribed", "topic": topic},
                client_id,
            )

    async def unsubscribe_from_topic(self, client_id: str, topic: str):
        """Unsubscribe a client from a topic."""
        if client_id in self.connection_info:
            self.connection_info[client_id].subscriptions.discard(topic)

            if topic in self.topic_subscriptions:
                self.topic_subscriptions[topic].discard(client_id)
                if not self.topic_subscriptions[topic]:
                    del self.topic_subscriptions[topic]

            logger.info(f"Client {client_id} unsubscribed from topic {topic}")

            # Send confirmation
            await self.send_personal_message(
                {"type": "subscription", "action": "unsubscribed", "topic": topic},
                client_id,
            )

    async def add_to_group(self, client_id: str, group_name: str):
        """Add a client to a group."""
        if group_name not in self.connection_groups:
            self.connection_groups[group_name] = set()
        self.connection_groups[group_name].add(client_id)

        logger.info(f"Client {client_id} added to group {group_name}")

    async def remove_from_group(self, client_id: str, group_name: str):
        """Remove a client from a group."""
        if group_name in self.connection_groups:
            self.connection_groups[group_name].discard(client_id)
            if not self.connection_groups[group_name]:
                del self.connection_groups[group_name]

        logger.info(f"Client {client_id} removed from group {group_name}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        return {
            "total_connections": len(self.active_connections),
            "total_topics": len(self.topic_subscriptions),
            "total_groups": len(self.connection_groups),
            "connections_by_topic": {
                topic: len(clients)
                for topic, clients in self.topic_subscriptions.items()
            },
            "connections_by_group": {
                group: len(clients) for group, clients in self.connection_groups.items()
            },
        }

    def get_client_info(self, client_id: str) -> Optional[ConnectionInfo]:
        """Get information about a specific client."""
        return self.connection_info.get(client_id)


# Global connection manager instance
connection_manager = ConnectionManager()
