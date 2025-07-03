"""Event broadcasting system for real-time updates."""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from .connection_manager import connection_manager

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of events that can be broadcast."""

    # Bridge transaction events
    BRIDGE_TRANSACTION_INITIATED = "bridge_transaction_initiated"
    BRIDGE_TRANSACTION_CONFIRMED = "bridge_transaction_confirmed"
    BRIDGE_TRANSACTION_COMPLETED = "bridge_transaction_completed"
    BRIDGE_TRANSACTION_FAILED = "bridge_transaction_failed"

    # Validator events
    VALIDATOR_STATUS_CHANGED = "validator_status_changed"
    VALIDATOR_JOINED = "validator_joined"
    VALIDATOR_LEFT = "validator_left"

    # Liquidity pool events
    LIQUIDITY_ADDED = "liquidity_added"
    LIQUIDITY_REMOVED = "liquidity_removed"
    POOL_CREATED = "pool_created"
    POOL_STATUS_CHANGED = "pool_status_changed"

    # Network events
    NETWORK_STATUS_CHANGED = "network_status_changed"
    CHAIN_STATUS_CHANGED = "chain_status_changed"

    # System events
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_MODE = "maintenance_mode"


class BridgeEvent(BaseModel):
    """Standard event structure for broadcasting."""

    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source_chain: Optional[str] = None
    target_chain: Optional[str] = None
    transaction_id: Optional[str] = None
    user_id: Optional[str] = None
    severity: str = "info"  # info, warning, error, critical


class EventBroadcaster:
    """Handles event broadcasting to WebSocket clients."""

    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.is_running = False
        self.background_task = None

    async def start(self):
        """Start the event broadcasting background task."""
        if not self.is_running:
            self.is_running = True
            self.background_task = asyncio.create_task(self._process_events())
            logger.info("Event broadcaster started")

    async def stop(self):
        """Stop the event broadcasting background task."""
        self.is_running = False
        if self.background_task:
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
        logger.info("Event broadcaster stopped")

    async def _process_events(self):
        """Background task to process events from the queue."""
        while self.is_running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._broadcast_event(event)
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _broadcast_event(self, event: BridgeEvent):
        """Broadcast an event to appropriate subscribers."""
        message = {
            "type": "event",
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "source_chain": event.source_chain,
            "target_chain": event.target_chain,
            "transaction_id": event.transaction_id,
            "user_id": event.user_id,
            "severity": event.severity,
        }

        # Broadcast to general events topic
        await connection_manager.broadcast_to_topic(message, "events")

        # Broadcast to specific event type topic
        await connection_manager.broadcast_to_topic(
            message, f"events:{event.event_type}"
        )

        # Broadcast to chain-specific topics if applicable
        if event.source_chain:
            await connection_manager.broadcast_to_topic(
                message, f"chain:{event.source_chain}"
            )

        if event.target_chain:
            await connection_manager.broadcast_to_topic(
                message, f"chain:{event.target_chain}"
            )

        # Broadcast to user-specific topic if applicable
        if event.user_id:
            await connection_manager.broadcast_to_topic(
                message, f"user:{event.user_id}"
            )

        # Broadcast to transaction-specific topic if applicable
        if event.transaction_id:
            await connection_manager.broadcast_to_topic(
                message, f"transaction:{event.transaction_id}"
            )

    async def emit_event(self, event: BridgeEvent):
        """Emit an event for broadcasting."""
        await self.event_queue.put(event)
        logger.debug(f"Event queued: {event.event_type}")

    async def emit_bridge_transaction_event(
        self,
        event_type: EventType,
        transaction_id: str,
        source_chain: str,
        target_chain: str,
        amount: str,
        token: str,
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Emit a bridge transaction event."""
        data = {"amount": amount, "token": token, **(additional_data or {})}

        event = BridgeEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            source_chain=source_chain,
            target_chain=target_chain,
            transaction_id=transaction_id,
            user_id=user_id,
        )

        await self.emit_event(event)

    async def emit_validator_event(
        self,
        event_type: EventType,
        validator_id: str,
        status: str,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Emit a validator event."""
        data = {
            "validator_id": validator_id,
            "status": status,
            **(additional_data or {}),
        }

        event = BridgeEvent(
            event_type=event_type, timestamp=datetime.utcnow(), data=data
        )

        await self.emit_event(event)

    async def emit_liquidity_event(
        self,
        event_type: EventType,
        pool_id: str,
        token_a: str,
        token_b: str,
        amount_a: Optional[str] = None,
        amount_b: Optional[str] = None,
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Emit a liquidity pool event."""
        data = {
            "pool_id": pool_id,
            "token_a": token_a,
            "token_b": token_b,
            **({"amount_a": amount_a} if amount_a else {}),
            **({"amount_b": amount_b} if amount_b else {}),
            **(additional_data or {}),
        }

        event = BridgeEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            user_id=user_id,
        )

        await self.emit_event(event)

    async def emit_system_alert(
        self,
        message: str,
        severity: str = "info",
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Emit a system alert event."""
        data = {"message": message, **(additional_data or {})}

        event = BridgeEvent(
            event_type=EventType.SYSTEM_ALERT,
            timestamp=datetime.utcnow(),
            data=data,
            severity=severity,
        )

        await self.emit_event(event)


# Global event broadcaster instance
event_broadcaster = EventBroadcaster()
