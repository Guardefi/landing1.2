"""WebSocket router for real-time dashboard integration."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket
from fastapi.responses import HTMLResponse

# from ..http.dependencies import get_current_user_optional  # TODO: Implement optional auth
from ..websocket.connection_manager import connection_manager
from ..websocket.handlers import bridge_websocket_handler

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
):
    """Main WebSocket endpoint for real-time communication."""

    # Optional authentication via token
    user_id = None
    if token:
        try:
            # Here you would validate the token and get user_id
            # For now, we'll use the token as user_id for demo
            user_id = token
        except Exception as e:
            logger.warning(f"Invalid token provided: {e}")

    await bridge_websocket_handler.handle_connection(
        websocket=websocket, client_id=client_id, user_id=user_id
    )


@router.websocket("/ws/bridge")
async def bridge_websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
):
    """WebSocket endpoint specifically for bridge transaction updates."""

    user_id = None
    if token:
        try:
            user_id = token
        except Exception as e:
            logger.warning(f"Invalid token provided: {e}")

    await bridge_websocket_handler.handle_connection(
        websocket=websocket, client_id=client_id, user_id=user_id
    )


@router.websocket("/ws/validator")
async def validator_websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    token: Optional[str] = Query(None),
):
    """WebSocket endpoint for validator status updates."""

    user_id = None
    if token:
        try:
            user_id = token
        except Exception as e:
            logger.warning(f"Invalid token provided: {e}")

    await bridge_websocket_handler.handle_connection(
        websocket=websocket, client_id=client_id, user_id=user_id
    )


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get current WebSocket connection statistics."""
    return connection_manager.get_connection_stats()


@router.get("/ws/test")
async def websocket_test_page():
    """Test page for WebSocket connection (development only)."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scorpius Bridge WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin: 10px 0; background: #f9f9f9; }
            .controls { margin: 10px 0; }
            input, button, select { margin: 5px; padding: 5px; }
            .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .received { background: #e8f5e8; }
            .sent { background: #e8e8f5; }
            .error { background: #f5e8e8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Scorpius Bridge WebSocket Test</h1>
            
            <div class="controls">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
                <span>Status: <span id="status">Disconnected</span></span>
            </div>
            
            <div class="controls">
                <h3>Quick Actions:</h3>
                <button onclick="subscribeToEvents()">Subscribe to Events</button>
                <button onclick="subscribeToStats()">Subscribe to Stats</button>
                <button onclick="ping()">Ping</button>
                <button onclick="getStats()">Get Stats</button>
            </div>
            
            <div class="controls">
                <h3>Custom Message:</h3>
                <input type="text" id="messageType" placeholder="Message type" value="subscribe">
                <input type="text" id="messageData" placeholder="Message data (JSON)" value='{"topic": "events"}'>
                <button onclick="sendCustomMessage()">Send</button>
            </div>
            
            <div id="messages" class="messages"></div>
        </div>

        <script>
            let ws = null;
            
            function connect() {
                if (ws) {
                    ws.close();
                }
                
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/api/ws?client_id=test-client`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {
                    document.getElementById('status').textContent = 'Connected';
                    addMessage('Connected to WebSocket', 'received');
                };
                
                ws.onmessage = function(event) {
                    addMessage('Received: ' + event.data, 'received');
                };
                
                ws.onclose = function() {
                    document.getElementById('status').textContent = 'Disconnected';
                    addMessage('WebSocket connection closed', 'error');
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket error: ' + error, 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendMessage(type, data) {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    addMessage('WebSocket not connected', 'error');
                    return;
                }
                
                const message = { type: type, data: data || {} };
                const messageStr = JSON.stringify(message);
                ws.send(messageStr);
                addMessage('Sent: ' + messageStr, 'sent');
            }
            
            function subscribeToEvents() {
                sendMessage('subscribe', { topic: 'events' });
            }
            
            function subscribeToStats() {
                sendMessage('subscribe', { topic: 'stats' });
            }
            
            function ping() {
                sendMessage('ping');
            }
            
            function getStats() {
                sendMessage('get_stats');
            }
            
            function sendCustomMessage() {
                const type = document.getElementById('messageType').value;
                const dataStr = document.getElementById('messageData').value;
                
                try {
                    const data = dataStr ? JSON.parse(dataStr) : {};
                    sendMessage(type, data);
                } catch (e) {
                    addMessage('Invalid JSON data: ' + e.message, 'error');
                }
            }
            
            function addMessage(message, type) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type;
                messageDiv.textContent = new Date().toLocaleTimeString() + ' - ' + message;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // Auto-connect on page load
            window.onload = function() {
                connect();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
