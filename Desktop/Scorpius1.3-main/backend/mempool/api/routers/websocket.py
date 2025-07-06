"""WebSocket router for real-time updates."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..dependencies import verify_websocket_token

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections with authentication and filtering."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_subscriptions: Dict[str, Dict[str, any]] = {}
        self.connection_count = 0

    async def connect(self, websocket: WebSocket, client_id: str, user_info: dict):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_subscriptions[client_id] = {
            "user_info": user_info,
            "filters": {},
            "subscribed_events": ["all"],
            "connected_at": datetime.utcnow(),
        }
        self.connection_count += 1

        # Send welcome message
        await self.send_personal_message(
            json.dumps(
                {
                    "type": "connection",
                    "status": "connected",
                    "client_id": client_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            client_id,
        )

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_subscriptions[client_id]
            self.connection_count -= 1

    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception:
                self.disconnect(client_id)

    async def broadcast_to_filtered(self, message: dict, event_type: str = "all"):
        """Broadcast a message to clients with matching filters."""
        if not self.active_connections:
            return

        disconnected_clients = []
        message_str = json.dumps(message)

        for client_id, websocket in self.active_connections.items():
            try:
                subscription = self.connection_subscriptions.get(client_id, {})
                subscribed_events = subscription.get("subscribed_events", ["all"])

                # Check if client is subscribed to this event type
                if "all" in subscribed_events or event_type in subscribed_events:
                    # Apply filters if any
                    if self._message_matches_filters(
                        message, subscription.get("filters", {})
                    ):
                        await websocket.send_text(message_str)

            except Exception:
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def _message_matches_filters(self, message: dict, filters: dict) -> bool:
        """Check if message matches client filters."""
        if not filters:
            return True

        # Apply chain_id filter
        if "chain_id" in filters and message.get("chain_id") != filters["chain_id"]:
            return False

        # Apply severity filter for alerts
        if "min_severity" in filters and message.get("type") == "alert":
            severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            message_severity = severity_levels.get(message.get("severity", "low"), 1)
            min_severity = severity_levels.get(filters["min_severity"], 1)
            if message_severity < min_severity:
                return False

        # Apply value filter for transactions
        if "min_value" in filters and message.get("type") == "transaction":
            try:
                message_value = float(message.get("value", 0))
                min_value = float(filters["min_value"])
                if message_value < min_value:
                    return False
            except (ValueError, TypeError):
                pass

        return True

    async def update_client_subscription(self, client_id: str, subscription_data: dict):
        """Update client subscription preferences."""
        if client_id in self.connection_subscriptions:
            current_sub = self.connection_subscriptions[client_id]
            current_sub.update(subscription_data)

            # Send confirmation
            await self.send_personal_message(
                json.dumps(
                    {
                        "type": "subscription_updated",
                        "subscription": subscription_data,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                client_id,
            )

    def get_connection_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_connections": self.connection_count,
            "active_connections": len(self.active_connections),
            "connections_by_event": self._get_connections_by_event(),
        }

    def _get_connections_by_event(self) -> dict:
        """Get connection count by subscribed event type."""
        event_counts = {}
        for sub in self.connection_subscriptions.values():
            for event in sub.get("subscribed_events", []):
                event_counts[event] = event_counts.get(event, 0) + 1
        return event_counts


# Global connection manager
connection_manager = ConnectionManager()


class SubscriptionUpdate(BaseModel):
    """Model for subscription updates."""

    event_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, client_id: str, token: Optional[str] = None
):
    """Real-time WebSocket endpoint for live updates."""
    try:
        # Verify authentication
        user_info = (
            await verify_websocket_token(token) if token else {"user_id": "anonymous"}
        )

        await connection_manager.connect(websocket, client_id, user_info)

        while True:
            # Receive messages from client
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_client_message(client_id, message)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await connection_manager.send_personal_message(
                    json.dumps(
                        {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
                    ),
                    client_id,
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        connection_manager.disconnect(client_id)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_client_message(client_id: str, message: dict):
    """Handle incoming messages from WebSocket clients."""
    message_type = message.get("type")

    if message_type == "subscribe":
        # Update subscription preferences
        subscription_data = {
            "subscribed_events": message.get("events", ["all"]),
            "filters": message.get("filters", {}),
        }
        await connection_manager.update_client_subscription(
            client_id, subscription_data
        )

    elif message_type == "unsubscribe":
        # Remove specific event subscriptions
        events_to_remove = message.get("events", [])
        if client_id in connection_manager.connection_subscriptions:
            current_events = connection_manager.connection_subscriptions[client_id].get(
                "subscribed_events", []
            )
            updated_events = [e for e in current_events if e not in events_to_remove]
            await connection_manager.update_client_subscription(
                client_id, {"subscribed_events": updated_events}
            )

    elif message_type == "pong":
        # Respond to ping
        await connection_manager.send_personal_message(
            json.dumps(
                {"type": "pong_ack", "timestamp": datetime.utcnow().isoformat()}
            ),
            client_id,
        )


# Background task functions for broadcasting events
async def broadcast_transaction_event(transaction_data: dict):
    """Broadcast new transaction event."""
    message = {
        "type": "transaction",
        "data": transaction_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast_to_filtered(message, "transaction")


async def broadcast_alert_event(alert_data: dict):
    """Broadcast new alert event."""
    message = {
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast_to_filtered(message, "alert")


async def broadcast_mev_opportunity(mev_data: dict):
    """Broadcast MEV opportunity event."""
    message = {
        "type": "mev_opportunity",
        "data": mev_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast_to_filtered(message, "mev")


async def broadcast_network_stats(stats_data: dict):
    """Broadcast network statistics update."""
    message = {
        "type": "network_stats",
        "data": stats_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast_to_filtered(message, "network_stats")


async def broadcast_gas_price_update(gas_data: dict):
    """Broadcast gas price update."""
    message = {
        "type": "gas_update",
        "data": gas_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast_to_filtered(message, "gas_prices")


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return connection_manager.get_connection_stats()


# Export the connection manager for use in other modules
__all__ = [
    "router",
    "connection_manager",
    "broadcast_transaction_event",
    "broadcast_alert_event",
    "broadcast_mev_opportunity",
    "broadcast_network_stats",
    "broadcast_gas_price_update",
]
