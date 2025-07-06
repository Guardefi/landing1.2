"""WebSocket handlers for different types of real-time data."""

import json
import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError

from .connection_manager import connection_manager
from .events import event_broadcaster

logger = logging.getLogger(__name__)


class WebSocketMessage(BaseModel):
    """Standard WebSocket message structure."""

    type: str
    data: Dict[str, Any] = {}


class SubscriptionRequest(BaseModel):
    """Request to subscribe to a topic."""

    topic: str
    filters: Optional[Dict[str, Any]] = None


class UnsubscriptionRequest(BaseModel):
    """Request to unsubscribe from a topic."""

    topic: str


class BridgeWebSocketHandler:
    """Main WebSocket handler for the bridge system."""

    def __init__(self):
        self.supported_topics = {
            "events",  # All events
            "events:bridge_transaction",  # Bridge transaction events
            "events:validator",  # Validator events
            "events:liquidity",  # Liquidity pool events
            "events:system",  # System events
            "stats",  # Real-time statistics
            "network_status",  # Network status updates
            "chain_status",  # Individual chain status
            "validator_status",  # Validator status
            "liquidity_pools",  # Liquidity pool data
            "transaction_history",  # Transaction history updates
        }

    async def handle_connection(
        self,
        websocket: WebSocket,
        client_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Handle a new WebSocket connection."""
        if not client_id:
            client_id = str(uuid.uuid4())

        metadata = {"user_id": user_id} if user_id else {}

        # Connect to the connection manager
        connected = await connection_manager.connect(websocket, client_id, metadata)
        if not connected:
            return

        try:
            # Message handling loop
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                await self._handle_message(client_id, data)

        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected normally")
        except Exception as e:
            logger.error(f"Error handling WebSocket for client {client_id}: {e}")
        finally:
            await connection_manager.disconnect(client_id)

    async def _handle_message(self, client_id: str, message_data: str):
        """Handle incoming WebSocket message."""
        try:
            # Parse message
            raw_message = json.loads(message_data)
            message = WebSocketMessage(**raw_message)

            # Route message based on type
            if message.type == "subscribe":
                await self._handle_subscription(client_id, message.data)
            elif message.type == "unsubscribe":
                await self._handle_unsubscription(client_id, message.data)
            elif message.type == "ping":
                await self._handle_ping(client_id)
            elif message.type == "get_stats":
                await self._handle_get_stats(client_id)
            elif message.type == "get_status":
                await self._handle_get_status(client_id, message.data)
            else:
                await self._handle_unknown_message(client_id, message.type)

        except json.JSONDecodeError:
            await self._send_error(client_id, "Invalid JSON format")
        except ValidationError as e:
            await self._send_error(client_id, f"Message validation failed: {e}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_error(client_id, "Internal server error")

    async def _handle_subscription(self, client_id: str, data: Dict[str, Any]):
        """Handle subscription request."""
        try:
            request = SubscriptionRequest(**data)

            if request.topic not in self.supported_topics and not any(
                request.topic.startswith(f"{topic}:") for topic in self.supported_topics
            ):
                await self._send_error(
                    client_id, f"Topic '{request.topic}' not supported"
                )
                return

            await connection_manager.subscribe_to_topic(client_id, request.topic)

            # Send current data for certain topics
            if request.topic == "stats":
                await self._send_current_stats(client_id)
            elif request.topic == "network_status":
                await self._send_network_status(client_id)
            elif request.topic.startswith("chain_status:"):
                chain_id = request.topic.split(":", 1)[1]
                await self._send_chain_status(client_id, chain_id)

        except ValidationError as e:
            await self._send_error(client_id, f"Invalid subscription request: {e}")

    async def _handle_unsubscription(self, client_id: str, data: Dict[str, Any]):
        """Handle unsubscription request."""
        try:
            request = UnsubscriptionRequest(**data)
            await connection_manager.unsubscribe_from_topic(client_id, request.topic)

        except ValidationError as e:
            await self._send_error(client_id, f"Invalid unsubscription request: {e}")

    async def _handle_ping(self, client_id: str):
        """Handle ping message."""
        await connection_manager.send_personal_message(
            {"type": "pong", "timestamp": self._get_current_timestamp()}, client_id
        )

    async def _handle_get_stats(self, client_id: str):
        """Handle request for current statistics."""
        await self._send_current_stats(client_id)

    async def _handle_get_status(self, client_id: str, data: Dict[str, Any]):
        """Handle status request."""
        status_type = data.get("status_type", "network")

        if status_type == "network":
            await self._send_network_status(client_id)
        elif status_type == "chain":
            chain_id = data.get("chain_id")
            if chain_id:
                await self._send_chain_status(client_id, chain_id)
            else:
                await self._send_error(client_id, "chain_id required for chain status")
        else:
            await self._send_error(client_id, f"Unknown status type: {status_type}")

    async def _handle_unknown_message(self, client_id: str, message_type: str):
        """Handle unknown message type."""
        await self._send_error(client_id, f"Unknown message type: {message_type}")

    async def _send_error(self, client_id: str, error_message: str):
        """Send error message to client."""
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "message": error_message,
                "timestamp": self._get_current_timestamp(),
            },
            client_id,
        )

    async def _send_current_stats(self, client_id: str):
        """Send current system statistics."""
        # This would integrate with your actual stats collection
        stats = {
            "total_transactions": 0,  # Replace with actual data
            "active_validators": 0,  # Replace with actual data
            "total_liquidity": "0",  # Replace with actual data
            "network_health": "healthy",
            "timestamp": self._get_current_timestamp(),
        }

        await connection_manager.send_personal_message(
            {"type": "stats", "data": stats}, client_id
        )

    async def _send_network_status(self, client_id: str):
        """Send current network status."""
        # This would integrate with your actual network monitoring
        status = {
            "status": "operational",
            "supported_chains": ["ethereum", "polygon", "bsc"],
            "chain_status": {
                "ethereum": "operational",
                "polygon": "operational",
                "bsc": "operational",
            },
            "timestamp": self._get_current_timestamp(),
        }

        await connection_manager.send_personal_message(
            {"type": "network_status", "data": status}, client_id
        )

    async def _send_chain_status(self, client_id: str, chain_id: str):
        """Send status for a specific chain."""
        # This would integrate with your actual chain monitoring
        status = {
            "chain_id": chain_id,
            "status": "operational",
            "block_height": 0,  # Replace with actual data
            "gas_price": "0",  # Replace with actual data
            "last_update": self._get_current_timestamp(),
        }

        await connection_manager.send_personal_message(
            {"type": "chain_status", "data": status}, client_id
        )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()


# Global handler instance
bridge_websocket_handler = BridgeWebSocketHandler()
