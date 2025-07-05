"""
Enterprise WebSocket Manager for Real-time Bytecode Analysis
Handles real-time connections for security platform integration
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection"""

    connection_id: str
    client_ip: str
    connected_at: datetime
    user_id: Optional[str] = None
    subscription_types: Set[str] = None
    last_activity: datetime = None

    def __post_init__(self):
        if self.subscription_types is None:
            self.subscription_types = set()
        if self.last_activity is None:
            self.last_activity = self.connected_at


@dataclass
class AnalysisEvent:
    """Real-time analysis event"""

    event_type: str  # 'similarity_analysis', 'threat_detected', 'batch_complete'
    timestamp: datetime
    data: Dict[str, Any]
    severity: str = "info"  # 'info', 'warning', 'critical'
    source: str = "engine"


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Active connections by connection_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection metadata
        self.connection_info: Dict[str, ConnectionInfo] = {}
        # Subscriptions: event_type -> set of connection_ids
        self.subscriptions: Dict[str, Set[str]] = {}
        # Rate limiting
        self.rate_limits: Dict[str, int] = {}

    async def connect(
        self, websocket: WebSocket, client_ip: str, user_id: str = None
    ) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()

        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket

        conn_info = ConnectionInfo(
            connection_id=connection_id,
            client_ip=client_ip,
            connected_at=datetime.utcnow(),
            user_id=user_id,
        )
        self.connection_info[connection_id] = conn_info

        # Send welcome message
        await self.send_to_connection(
            connection_id,
            {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to SCORPIUS Bytecode Analysis Engine",
            },
        )

        logger.info(
            f"WebSocket connection established: {connection_id} from {client_ip}"
        )
        return connection_id

    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id in self.active_connections:
            # Remove from all subscriptions
            for event_type, subscriber_ids in self.subscriptions.items():
                subscriber_ids.discard(connection_id)

            # Clean up connection data
            del self.active_connections[connection_id]
            del self.connection_info[connection_id]
            self.rate_limits.pop(connection_id, None)

            logger.info(f"WebSocket connection closed: {connection_id}")

    async def subscribe(self, connection_id: str, event_types: List[str]):
        """Subscribe connection to specific event types"""
        if connection_id not in self.active_connections:
            return False

        for event_type in event_types:
            if event_type not in self.subscriptions:
                self.subscriptions[event_type] = set()
            self.subscriptions[event_type].add(connection_id)

            # Update connection info
            if connection_id in self.connection_info:
                self.connection_info[connection_id].subscription_types.add(event_type)

        await self.send_to_connection(
            connection_id,
            {
                "type": "subscription_confirmed",
                "event_types": event_types,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"Connection {connection_id} subscribed to: {event_types}")
        return True

    async def unsubscribe(self, connection_id: str, event_types: List[str]):
        """Unsubscribe connection from specific event types"""
        for event_type in event_types:
            if event_type in self.subscriptions:
                self.subscriptions[event_type].discard(connection_id)

            # Update connection info
            if connection_id in self.connection_info:
                self.connection_info[connection_id].subscription_types.discard(
                    event_type
                )

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message, default=str))

                # Update last activity
                if connection_id in self.connection_info:
                    self.connection_info[
                        connection_id
                    ].last_activity = datetime.utcnow()

                return True
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)
                return False
        return False

    async def broadcast_event(self, event: AnalysisEvent):
        """Broadcast event to all subscribed connections"""
        if event.event_type not in self.subscriptions:
            return

        message = {
            "type": "analysis_event",
            "event": asdict(event),
            "timestamp": datetime.utcnow().isoformat(),
        }

        subscriber_ids = self.subscriptions[event.event_type].copy()

        # Send to all subscribers
        disconnected_ids = []
        for connection_id in subscriber_ids:
            success = await self.send_to_connection(connection_id, message)
            if not success:
                disconnected_ids.append(connection_id)

        # Clean up disconnected connections
        for connection_id in disconnected_ids:
            await self.disconnect(connection_id)

        logger.debug(
            f"Broadcasted {event.event_type} to {len(subscriber_ids)} connections"
        )

    async def send_analysis_result(
        self, result: Dict[str, Any], analysis_type: str = "similarity"
    ):
        """Send analysis result as real-time event"""
        event = AnalysisEvent(
            event_type=f"{analysis_type}_analysis",
            timestamp=datetime.utcnow(),
            data=result,
            severity="warning" if result.get("similarity_score", 0) > 0.9 else "info",
        )
        await self.broadcast_event(event)

    async def send_threat_alert(self, threat_data: Dict[str, Any]):
        """Send high-priority threat alert"""
        event = AnalysisEvent(
            event_type="threat_detected",
            timestamp=datetime.utcnow(),
            data=threat_data,
            severity="critical",
        )
        await self.broadcast_event(event)

    async def send_system_status(self, status_data: Dict[str, Any]):
        """Send system status update"""
        event = AnalysisEvent(
            event_type="system_status",
            timestamp=datetime.utcnow(),
            data=status_data,
            severity="info",
        )
        await self.broadcast_event(event)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        now = datetime.utcnow()

        return {
            "total_connections": len(self.active_connections),
            "connections_by_subscription": {
                event_type: len(subscriber_ids)
                for event_type, subscriber_ids in self.subscriptions.items()
            },
            "connection_details": [
                {
                    "connection_id": conn_info.connection_id,
                    "client_ip": conn_info.client_ip,
                    "user_id": conn_info.user_id,
                    "connected_duration": str(now - conn_info.connected_at),
                    "subscriptions": list(conn_info.subscription_types),
                    "last_activity": conn_info.last_activity.isoformat(),
                }
                for conn_info in self.connection_info.values()
            ],
        }

    async def cleanup_stale_connections(self, max_idle_minutes: int = 30):
        """Clean up connections that have been idle too long"""
        now = datetime.utcnow()
        stale_connections = []

        for connection_id, conn_info in self.connection_info.items():
            idle_time = now - conn_info.last_activity
            if idle_time.total_seconds() > max_idle_minutes * 60:
                stale_connections.append(connection_id)

        for connection_id in stale_connections:
            await self.disconnect(connection_id)

        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale connections")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


class RealtimeAnalysisQueue:
    """Queue for handling real-time analysis requests"""

    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processing = False

    async def add_analysis_request(self, request_data: Dict[str, Any]):
        """Add analysis request to queue"""
        await self.queue.put(
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow(),
                "data": request_data,
            }
        )

    async def start_processing(self, similarity_engine):
        """Start processing queued requests"""
        if self.processing:
            return

        self.processing = True
        logger.info("Started real-time analysis queue processing")

        try:
            while self.processing:
                try:
                    # Wait for request with timeout
                    request = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                    # Process the request
                    await self._process_request(request, similarity_engine)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing analysis request: {e}")
        finally:
            self.processing = False
            logger.info("Stopped real-time analysis queue processing")

    async def _process_request(self, request: Dict[str, Any], similarity_engine):
        """Process individual analysis request"""
        try:
            request_data = request["data"]

            if request_data.get("type") == "similarity_analysis":
                # Perform similarity analysis
                result = await similarity_engine.compare_bytecodes(
                    request_data["bytecode1"], request_data["bytecode2"]
                )

                # Send result via WebSocket
                await websocket_manager.send_analysis_result(
                    {
                        "request_id": request["id"],
                        "similarity_score": result.similarity_score,
                        "confidence": result.confidence,
                        "dimension_scores": result.dimension_scores,
                        "processing_time": result.processing_time,
                        "bytecode1_hash": request_data.get("bytecode1_hash"),
                        "bytecode2_hash": request_data.get("bytecode2_hash"),
                    }
                )

            elif request_data.get("type") == "threat_detection":
                # Perform threat detection analysis
                # This would integrate with your threat detection logic
                threat_score = await self._analyze_threat_level(
                    request_data, similarity_engine
                )

                if threat_score > 0.8:  # High threat threshold
                    await websocket_manager.send_threat_alert(
                        {
                            "request_id": request["id"],
                            "threat_score": threat_score,
                            "bytecode_hash": request_data.get("bytecode_hash"),
                            "threat_indicators": request_data.get("indicators", []),
                            "severity": "high" if threat_score > 0.9 else "medium",
                        }
                    )

        except Exception as e:
            logger.error(f"Error processing request {request['id']}: {e}")

    async def _analyze_threat_level(
        self, request_data: Dict[str, Any], similarity_engine
    ) -> float:
        """Analyze threat level of bytecode"""
        # This is where you'd implement your threat detection logic
        # For now, return a dummy score based on certain patterns

        bytecode = request_data.get("bytecode", "")
        threat_score = 0.0

        # Example threat indicators
        threat_patterns = [
            "selfdestruct",  # Contract can self-destruct
            "delegatecall",  # Dangerous delegatecall
            "suicide",  # Old self-destruct
        ]

        for pattern in threat_patterns:
            if pattern in bytecode.lower():
                threat_score += 0.3

        return min(threat_score, 1.0)

    def stop_processing(self):
        """Stop processing queue"""
        self.processing = False


# Global analysis queue
realtime_queue = RealtimeAnalysisQueue()
