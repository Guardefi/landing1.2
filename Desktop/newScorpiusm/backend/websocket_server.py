#!/usr/bin/env python3
"""
ScorpiusX WebSocket Server
Real-time communication hub for live data, graphs, schedule updates, and chat
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types"""

    # Chat system
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    USER_LIST = "user_list"
    TYPING = "typing"

    # Live data updates
    LIVE_DATA = "live_data"
    GRAPH_UPDATE = "graph_update"
    METRICS_UPDATE = "metrics_update"

    # Schedule updates
    SCHEDULE_UPDATE = "schedule_update"
    TASK_STATUS = "task_status"

    # Scanner updates
    SCAN_PROGRESS = "scan_progress"
    SCAN_RESULT = "scan_result"
    VULNERABILITY_ALERT = "vulnerability_alert"

    # MEV updates
    MEV_OPPORTUNITY = "mev_opportunity"
    MEV_EXECUTION = "mev_execution"

    # System updates
    SYSTEM_STATUS = "system_status"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class ChatMessage:
    """Chat message data structure"""

    id: str
    username: str
    avatar: str
    message: str
    timestamp: datetime
    type: str = "message"
    reactions: list[dict] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "username": self.username,
            "avatar": self.avatar,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "reactions": self.reactions or [],
        }


@dataclass
class ConnectedUser:
    """Connected user data structure"""

    id: str
    username: str
    avatar: str
    status: str
    role: str
    websocket: websockets.WebSocketServerProtocol
    last_seen: datetime


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting"""

    def __init__(self):
        self.connections: dict[str, ConnectedUser] = {}
        self.chat_messages: list[ChatMessage] = []
        self.init_database()
        self.load_chat_history()

    def init_database(self):
        """Initialize SQLite database for persistent chat storage"""
        self.conn = sqlite3.connect("scorpius_chat.db", check_same_thread=False)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                avatar TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                reactions TEXT
            )
        """
        )
        self.conn.commit()

    def load_chat_history(self):
        """Load recent chat messages from database"""
        cursor = self.conn.execute(
            """
            SELECT id, username, avatar, message, timestamp, type, reactions
            FROM chat_messages
            ORDER BY timestamp DESC
            LIMIT 50
        """
        )

        for row in cursor.fetchall():
            reactions = json.loads(row[6]) if row[6] else []
            message = ChatMessage(
                id=row[0],
                username=row[1],
                avatar=row[2],
                message=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                type=row[5],
                reactions=reactions,
            )
            self.chat_messages.append(message)

        # Reverse to get chronological order
        self.chat_messages.reverse()

    def save_message(self, message: ChatMessage):
        """Save chat message to database"""
        self.conn.execute(
            """
            INSERT INTO chat_messages (id, username, avatar, message, timestamp, type, reactions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message.id,
                message.username,
                message.avatar,
                message.message,
                message.timestamp.isoformat(),
                message.type,
                json.dumps(message.reactions or []),
            ),
        )
        self.conn.commit()

    async def register(
        self, websocket: websockets.WebSocketServerProtocol, user_data: dict[str, str]
    ):
        """Register a new WebSocket connection"""
        user_id = str(uuid.uuid4())
        user = ConnectedUser(
            id=user_id,
            username=user_data.get("username", f"User_{user_id[:8]}"),
            avatar=user_data.get("avatar", "👤"),
            status="online",
            role=user_data.get("role", "User"),
            websocket=websocket,
            last_seen=datetime.now(),
        )

        self.connections[user_id] = user
        logger.info(f"User {user.username} connected")

        # Send chat history to new user
        await self.send_chat_history(websocket)

        # Notify all users of new connection
        await self.broadcast_user_list()
        await self.broadcast_message(
            {
                "type": MessageType.USER_JOIN.value,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "avatar": user.avatar,
                    "status": user.status,
                    "role": user.role,
                },
            }
        )

        return user_id

    async def unregister(self, user_id: str):
        """Unregister a WebSocket connection"""
        if user_id in self.connections:
            user = self.connections[user_id]
            del self.connections[user_id]
            logger.info(f"User {user.username} disconnected")

            # Notify remaining users
            await self.broadcast_message(
                {
                    "type": MessageType.USER_LEAVE.value,
                    "user": {"id": user.id, "username": user.username},
                }
            )
            await self.broadcast_user_list()

    async def send_chat_history(self, websocket: websockets.WebSocketServerProtocol):
        """Send chat history to a specific user"""
        messages_data = [
            msg.to_dict() for msg in self.chat_messages[-50:]
        ]  # Last 50 messages
        await websocket.send(
            json.dumps(
                {"type": MessageType.CHAT_HISTORY.value, "messages": messages_data}
            )
        )

    async def broadcast_user_list(self):
        """Broadcast current user list to all connections"""
        users_data = []
        for user in self.connections.values():
            users_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "avatar": user.avatar,
                    "status": user.status,
                    "role": user.role,
                }
            )

        await self.broadcast_message(
            {"type": MessageType.USER_LIST.value, "users": users_data}
        )

    async def handle_chat_message(self, user_id: str, data: dict[str, Any]):
        """Handle incoming chat message"""
        user = self.connections.get(user_id)
        if not user:
            return

        message = ChatMessage(
            id=str(uuid.uuid4()),
            username=user.username,
            avatar=user.avatar,
            message=data.get("message", ""),
            timestamp=datetime.now(),
            type=data.get("type", "message"),
        )

        # Save to database and memory
        self.save_message(message)
        self.chat_messages.append(message)

        # Keep only last 100 messages in memory
        if len(self.chat_messages) > 100:
            self.chat_messages.pop(0)

        # Broadcast to all users
        await self.broadcast_message(
            {"type": MessageType.CHAT_MESSAGE.value, "message": message.to_dict()}
        )

    async def broadcast_message(self, message: dict[str, Any]):
        """Broadcast message to all connected users"""
        if not self.connections:
            return

        disconnected = []
        for user_id, user in self.connections.items():
            try:
                await user.websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(user_id)
            except Exception as e:
                logger.error(f"Error sending message to {user.username}: {e}")
                disconnected.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected:
            await self.unregister(user_id)

    async def broadcast_live_data(self, data_type: str, data: dict[str, Any]):
        """Broadcast live data updates (graphs, metrics, etc.)"""
        await self.broadcast_message(
            {
                "type": MessageType.LIVE_DATA.value,
                "dataType": data_type,
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def broadcast_scan_update(
        self, scan_id: str, progress: int, status: str, results: dict = None
    ):
        """Broadcast scan progress updates"""
        await self.broadcast_message(
            {
                "type": MessageType.SCAN_PROGRESS.value,
                "scanId": scan_id,
                "progress": progress,
                "status": status,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def broadcast_mev_opportunity(self, opportunity: dict[str, Any]):
        """Broadcast MEV opportunity updates"""
        await self.broadcast_message(
            {
                "type": MessageType.MEV_OPPORTUNITY.value,
                "opportunity": opportunity,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def broadcast_schedule_update(
        self, task_id: str, status: str, data: dict[str, Any]
    ):
        """Broadcast schedule/task updates"""
        await self.broadcast_message(
            {
                "type": MessageType.SCHEDULE_UPDATE.value,
                "taskId": task_id,
                "status": status,
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
        )


# Global WebSocket manager instance
manager = WebSocketManager()


async def websocket_handler(websocket: websockets.WebSocketServerProtocol, path: str):
    """Handle WebSocket connections"""
    user_id = None
    try:
        # Wait for initial authentication message
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)

        if auth_data.get("type") != "auth":
            await websocket.send(
                json.dumps(
                    {
                        "type": MessageType.ERROR.value,
                        "message": "Authentication required",
                    }
                )
            )
            return

        # Register user
        user_id = await manager.register(websocket, auth_data.get("user", {}))

        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get("type")

                if message_type == MessageType.CHAT_MESSAGE.value:
                    await manager.handle_chat_message(user_id, data)
                elif message_type == MessageType.TYPING.value:
                    # Broadcast typing indicator
                    user = manager.connections.get(user_id)
                    if user:
                        await manager.broadcast_message(
                            {
                                "type": MessageType.TYPING.value,
                                "username": user.username,
                                "isTyping": data.get("isTyping", False),
                            }
                        )
                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except json.JSONDecodeError:
                logger.error("Invalid JSON message received")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            await manager.unregister(user_id)


async def start_websocket_server():
    """Start the WebSocket server"""
    server = await serve(
        websocket_handler,
        "0.0.0.0",  # Change from localhost to 0.0.0.0 to allow external connections
        8081,
        ping_interval=30,
        ping_timeout=10,
    )

    logger.info("🌐 ScorpiusX WebSocket Server started on ws://0.0.0.0:8081")

    # Start background tasks for live data simulation
    asyncio.create_task(live_data_simulator())

    await server.wait_closed()


async def live_data_simulator():
    """Provide real-time system data instead of simulated data"""

    while True:
        try:
            # Reduce update frequency to 10 seconds to improve performance
            await asyncio.sleep(10)

            # Only broadcast if clients are connected
            if not manager.connections:
                continue

            # Get real system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
import asyncio
import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import psutil
import websockets
from websockets.server import serve

            disk = psutil.disk_usage("/")

            # Real metrics data
            metrics_data = {
                "systemHealth": 100
                - max(cpu_percent, memory.percent) // 2,  # Health based on CPU/Memory
                "cpuUsage": cpu_percent,
                "memoryUsage": memory.percent,
                "diskUsage": disk.percent,
                "diskFree": round(disk.free / (1024**3), 2),  # GB free
            }

            # Add real network stats if available
            try:
                net_io = psutil.net_io_counters()
                metrics_data["networkSent"] = net_io.bytes_sent
                metrics_data["networkRecv"] = net_io.bytes_recv
            except:
                pass

            await manager.broadcast_live_data("metrics", metrics_data)

            # Send system load graph data only every 30 seconds
            if time.time() % 30 < 10:  # First 10 seconds of each 30-second period
                # Get load information
                load_avg = (
                    psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
                )

                graph_data = {
                    "timestamp": time.time(),
                    "cpuLoad": cpu_percent,
                    "memoryLoad": memory.percent,
                    "load1min": load_avg[0],
                    "load5min": load_avg[1],
                    "load15min": load_avg[2],
                }

                await manager.broadcast_live_data("graphs", graph_data)

        except Exception as e:
            logger.error(f"Error in system metrics collector: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    print("🦂 Starting ScorpiusX WebSocket Server...")
    asyncio.run(start_websocket_server())
